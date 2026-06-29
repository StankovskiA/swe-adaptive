#!/usr/bin/env python3
"""
find_archived_repos.py
=======================
Find archived Python repositories from 2020-2026 that have:
  - Tests (pytest-based)
  - Setup files (pyproject.toml, setup.py, setup.cfg)
  - Preferably Dockerfiles or docker-compose files
  - Python 3.10 target (optional filter)

These are candidates for adaptive maintenance benchmark instances.
Archived repos are frozen in time — they never migrated to Python 3.13
and are less likely to appear as solved examples in model training data.

Usage:
  export GITHUB_TOKEN=your_token
  python find_archived_repos.py
  python find_archived_repos.py --max-repos 5000 --stars-min 20
  python find_archived_repos.py --require-docker --output archived_repos.json

Output:
  archived_repos.json  — machine-readable results (Iterative Incremental Save)
  archived_repos.md    — human-readable summary table (Iterative Incremental Save)

Requirements:
  pip install PyGithub requests tqdm python-dotenv
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import datetime as dt
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

try:
    from github import Github, GithubException
    from tqdm import tqdm
except ImportError:
    print("Missing: pip install PyGithub tqdm python-dotenv")
    sys.exit(1)


# ── Configuration ──────────────────────────────────────────────────────────

# Archived between these dates
ARCHIVED_AFTER  = "2020-01-01"
ARCHIVED_BEFORE = "2026-06-01"

DEFAULT_STARS_MIN  = 50
DEFAULT_STARS_MAX  = 5000
DEFAULT_MAX_REPOS  = 100
MIN_TEST_FILES     = 3

ALLOWED_LICENSES = {
    "mit", "apache-2.0", "bsd-2-clause", "bsd-3-clause",
    "isc", "mpl-2.0", "lgpl-2.1", "lgpl-3.0",
    "gpl-2.0", "gpl-3.0", "agpl-3.0",
}

# 1. Base configuration from your criteria
START_YEAR = 2020
END_YEAR = 2026
END_MONTH = 6  # Up to June 2026

TOPICS = [
    "",  # Broad catch-all for Python repos without specific topic tags
    "topic:api",
    "topic:cli",
    "topic:web",
    "topic:library",
    "topic:machine-learning",
    "topic:data-science",
    "topic:automation",
    "topic:backend",
    "topic:scraping",
]

# 2. Slice popularity into specific, non-overlapping star buckets
# This prevents high-star repos from burying low-star repos in the pagination
STAR_BUCKETS = [
    "stars:20..50",
    "stars:51..150",
    "stars:151..500",
    "stars:501..5000",
]

# 3. Helper function to generate 6-month date ranges
def generate_date_ranges(start_yr, end_yr, end_mo):
    ranges = []
    current_date = dt.date(start_yr, 1, 1)
    final_date = dt.date(end_yr, end_mo, 1)
    
    while current_date < final_date:
        # Calculate 6 months later
        start_str = current_date.strftime("%Y-%m-%d")
        
        # Advance by roughly 6 months (half a year)
        if current_date.month == 1:
            end_date = dt.date(current_date.year, 6, 30)
            current_date = dt.date(current_date.year, 7, 1)
        else:
            end_date = dt.date(current_date.year, 12, 31)
            current_date = dt.date(current_date.year + 1, 1, 1)
            
        # Ensure we don't exceed the overall benchmark ceiling
        if end_date > final_date:
            end_date = final_date
            
        end_str = end_date.strftime("%Y-%m-%d")
        ranges.append(f"pushed:{start_str}..{end_str}")
        
        if end_date == final_date:
            break
            
    return ranges

DATE_RANGES = generate_date_ranges(START_YEAR, END_YEAR, END_MONTH)

# 4. Generate the matrix of stratified queries
SEARCH_QUERIES = []

for date_range in DATE_RANGES:
    for star_bucket in STAR_BUCKETS:
        for topic in TOPICS:
            # Construct query components cleanly, filtering out empty strings
            components = [
                "language:Python",
                "archived:true",
                date_range,
                star_bucket
            ]
            if topic:
                components.append(topic)
                
            query_string = " ".join(components)
            SEARCH_QUERIES.append(query_string)

# Setup file names that indicate the repo is properly packaged
SETUP_FILES = [
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
]

# Docker-related files
DOCKER_FILES = [
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    ".dockerignore",
]


# ── Data model ─────────────────────────────────────────────────────────────

@dataclass
class ArchivedRepo:
    # Identity
    full_name:      str = ""
    url:            str = ""
    description:    str = ""
    stars:          int = 0
    forks:          int = 0
    license:        str = ""
    language:       str = ""
    default_branch: str = ""

    # Timing
    created_at:     str = ""
    pushed_at:      str = ""   # last commit before archiving
    age_days:       int = 0

    # Python version
    python_requires:    str = ""
    python_confirmed:   bool = False

    # Setup files present
    has_pyproject:  bool = False
    has_setup_py:   bool = False
    has_setup_cfg:  bool = False
    has_tox:        bool = False
    has_makefile:   bool = False

    # Docker
    has_dockerfile:        bool = False
    has_docker_compose:    bool = False

    # Tests
    has_tests:          bool = False
    test_directory:     str = ""
    test_file_count:    int = 0
    has_pytest:         bool = False

    # CI
    has_ci:         bool = False
    ci_platform:    str = ""   # github-actions, travis, circleci

    # Quality score (computed)
    quality_score:  int = 0    # higher = better candidate
    quality_notes:  list = field(default_factory=list)

    # Filter
    passed_filters: bool = False
    filter_failures: list = field(default_factory=list)

    def to_dict(self): return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        # Gracefully construct class instances back from file dictionaries
        failures = data.pop("filter_failures", [])
        notes = data.pop("quality_notes", [])
        obj = cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        obj.filter_failures = failures
        obj.quality_notes = notes
        return obj


# ── GitHub client ──────────────────────────────────────────────────────────

def get_client(token: str) -> Github:
    if not token:
        print("ERROR: Set GITHUB_TOKEN environment variable or populate a local .env file.")
        sys.exit(1)
    try:
        from github import Auth
        return Github(auth=Auth.Token(token))
    except ImportError:
        return Github(token)


def check_rate_limit(g: Github, logger: logging.Logger) -> int:
    try:
        limits = g.get_rate_limit()
        core_remaining = limits.core.remaining
        search_remaining = limits.search.remaining
        
        # Check search limit
        if search_remaining < 2:
            reset_timestamp = limits.search.reset.replace(tzinfo=timezone.utc).timestamp()
            sleep_time = max(reset_timestamp - time.time(), 0) + 5
            logger.warning(f"Search rate limit low. Sleeping {int(sleep_time)}s...")
            time.sleep(sleep_time)
            
        # Check core limit
        if core_remaining < 30:
            logger.warning(f"Core rate limit low ({core_remaining}). Sleeping 60s...")
            time.sleep(60)
            
        return min(core_remaining, search_remaining)
    except Exception:
        return 100


# ── Python version helpers ────────────────────────────────────────────────

def _is_capped_at_310(requires: str) -> bool:
    """
    Return True if the requires-python string targets Python 3.10 or below.

    Note: open-ended lower bounds (e.g. >=3.10 with no upper cap) are accepted
    intentionally. Such repositories may still fail on Python 3.13 despite not
    explicitly capping their version specifier — the auto_benchmark.py pipeline
    will detect and filter out any that already pass on Python 3.13.
    """
    r = requires.strip()

    # 1. Exact pin to 3.10
    if re.search(r'==\s*3\.10', r):
        return True

    # 2. Minimum 3.10 with no upper bound or cap at 3.12
    if re.search(r'>=\s*3\.10', r):
        return True

    # 3. Explicit upper cap combined with a minimum version of 3.7, 3.8, or 3.9.
    # We split this into independent lookups so that string order doesn't matter.
    has_upper_cap = bool(re.search(r'<\s*3\.11|<\s*3\.10|<=\s*3\.10', r))
    has_valid_min = bool(re.search(r'>=\s*3\.[789]', r))

    if has_upper_cap and has_valid_min:
        return True

    # 4. Fallback: If it just has an upper cap with no minimum declared (e.g., "<3.11")
    if has_upper_cap:
        return True

    return False


# ── File checks via GitHub API ─────────────────────────────────────────────

def check_files_via_api(repo, logger: logging.Logger) -> dict:
    result = {
        "has_pyproject": False,
        "has_setup_py":  False,
        "has_setup_cfg": False,
        "has_tox":       False,
        "has_makefile":  False,
        "has_dockerfile":     False,
        "has_docker_compose": False,
        "has_ci":        False,
        "ci_platform":   "",
        "python_requires": "",
        "python_confirmed": False,
        "already_migrated": False,
        "has_tests":     False,
        "test_directory": "",
        "test_file_count": 0,
        "has_pytest":    False,
    }

    # Check setup files and extract python version
    for filename in ["pyproject.toml", "setup.py", "setup.cfg", ".python-version"]:
        try:
            f = repo.get_contents(filename)
            content = f.decoded_content.decode("utf-8", errors="ignore")

            if filename == "pyproject.toml":
                result["has_pyproject"] = True
                m = re.search(r'requires-python\s*=\s*["\']([^"\']+)["\']', content)
                if m:
                    raw = m.group(1)
                    result["python_requires"] = raw
                    if re.search(r'3\.(1[2-9]|[2-9]\d)', raw):
                        result["already_migrated"] = True
                        return result
                    if _is_capped_at_310(raw):
                        result["python_confirmed"] = True
                if "tool.pytest" in content or "[pytest]" in content:
                    result["has_pytest"] = True

            elif filename == "setup.py":
                result["has_setup_py"] = True
                m = re.search(r'python_requires\s*=\s*["\']([^"\']+)["\']', content)
                if m:
                    raw = m.group(1)
                    if not result["python_requires"]:
                        result["python_requires"] = raw
                    if re.search(r'3\.(1[2-9]|[2-9]\d)', raw):
                        result["already_migrated"] = True
                        return result
                    if _is_capped_at_310(raw):
                        result["python_confirmed"] = True

            elif filename == "setup.cfg":
                result["has_setup_cfg"] = True
                m = re.search(r'python_requires\s*=\s*([^\n]+)', content)
                if m:
                    raw = m.group(1).strip()
                    if not result["python_requires"]:
                        result["python_requires"] = raw
                    if re.search(r'3\.(1[2-9]|[2-9]\d)', raw):
                        result["already_migrated"] = True
                        return result
                    if _is_capped_at_310(raw):
                        result["python_confirmed"] = True

            elif filename == ".python-version":
                content = content.strip()
                if re.match(r'^3\.10', content):
                    result["python_requires"] = content
                    result["python_confirmed"] = True

            time.sleep(0.05)
        except GithubException:
            continue
        except Exception:
            continue

    try:
        repo.get_contents("tox.ini")
        result["has_tox"] = True
        time.sleep(0.05)
    except GithubException:
        pass

    try:
        repo.get_contents("Makefile")
        result["has_makefile"] = True
        time.sleep(0.05)
    except GithubException:
        pass

    for docker_file in DOCKER_FILES:
        try:
            repo.get_contents(docker_file)
            if "compose" in docker_file.lower():
                result["has_docker_compose"] = True
            else:
                result["has_dockerfile"] = True
            time.sleep(0.05)
        except GithubException:
            continue

    ci_checks = [
        (".github/workflows", "github-actions"),
        (".travis.yml",       "travis"),
        (".circleci",         "circleci"),
        ("Jenkinsfile",       "jenkins"),
    ]
    for ci_path, platform in ci_checks:
        try:
            repo.get_contents(ci_path)
            result["has_ci"] = True
            result["ci_platform"] = platform
            time.sleep(0.05)
            break
        except GithubException:
            continue

    for test_dir in ["tests", "test", "src/tests", "tests/unit", "tests/integration"]:
        try:
            contents = repo.get_contents(test_dir)
            if isinstance(contents, list):
                py_files = [
                    f for f in contents
                    if f.name.endswith(".py")
                    and f.name not in ("__init__.py", "conftest.py")
                ]
                if len(py_files) >= MIN_TEST_FILES:
                    result["has_tests"]       = True
                    result["test_directory"]  = test_dir
                    result["test_file_count"] = len(py_files)
                    break
            time.sleep(0.05)
        except GithubException:
            continue

    if not result["has_pytest"]:
        for req_file in ["requirements-dev.txt", "requirements_dev.txt",
                         "requirements-test.txt", "requirements/dev.txt"]:
            try:
                f = repo.get_contents(req_file)
                content = f.decoded_content.decode("utf-8", errors="ignore")
                if "pytest" in content.lower():
                    result["has_pytest"] = True
                    break
                time.sleep(0.05)
            except GithubException:
                continue

    return result


# ── Quality scoring ────────────────────────────────────────────────────────

def compute_quality_score(r: ArchivedRepo) -> tuple[int, list]:
    score = 0
    notes = []

    if r.has_tests:
        score += 20
        if r.test_file_count >= 10:
            score += 10
            notes.append(f"{r.test_file_count} test files — good coverage")
        elif r.test_file_count >= 5:
            score += 5

    if r.has_pytest:
        score += 10
        notes.append("uses pytest")

    if r.has_pyproject:
        score += 15
        notes.append("has pyproject.toml")
    elif r.has_setup_py or r.has_setup_cfg:
        score += 8

    if r.has_dockerfile:
        score += 15
        notes.append("has Dockerfile — reproducible environment")
    if r.has_docker_compose:
        score += 10
        notes.append("has docker-compose")

    if r.has_ci:
        score += 10
        notes.append(f"has CI ({r.ci_platform})")

    if r.python_confirmed:
        score += 20
        if re.search(r'<\s*3\.1[01]|<=\s*3\.10|==\s*3\.10', r.python_requires):
            score += 10
            notes.append(f"explicitly capped at 3.10 ({r.python_requires})")
        else:
            notes.append(f"targets Python 3.10 ({r.python_requires})")
    elif r.python_requires:
        score += 5
        notes.append(f"declares python_requires: {r.python_requires}")

    if r.stars >= 500:
        score += 10
    elif r.stars >= 200:
        score += 7
    elif r.stars >= 100:
        score += 4

    if r.has_tox:
        score += 5
        notes.append("has tox.ini")
    if r.has_makefile:
        score += 3

    try:
        pushed = datetime.fromisoformat(r.pushed_at.replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - pushed).days
        if age <= 365:
            score += 15
            notes.append("archived very recently (within 1 year)")
        elif age <= 730:
            score += 10
            notes.append("archived recently (1-2 years ago)")
        elif age <= 1095:
            score += 5
    except Exception:
        pass

    return score, notes


# ── Main assessment ────────────────────────────────────────────────────────

def assess_repo(repo, logger: logging.Logger,
                require_docker: bool,
                require_py310: bool) -> ArchivedRepo:
    r = ArchivedRepo()
    r.full_name     = repo.full_name
    r.url           = repo.html_url
    r.description   = (repo.description or "")[:200]
    r.stars         = repo.stargazers_count
    r.forks         = repo.forks_count
    r.language      = repo.language or ""
    r.default_branch = repo.default_branch or "main"
    r.created_at    = str(repo.created_at) if repo.created_at else ""
    r.pushed_at     = str(repo.pushed_at)  if repo.pushed_at  else ""

    try:
        r.license = repo.license.key if repo.license else ""
    except Exception:
        r.license = ""

    if repo.created_at:
        created = repo.created_at.replace(tzinfo=timezone.utc)
        r.age_days = (datetime.now(timezone.utc) - created).days

    if r.license and r.license not in ALLOWED_LICENSES:
        r.filter_failures.append(f"license:{r.license}")
    elif not r.license:
        r.filter_failures.append("no_license")

    if repo.fork:
        r.filter_failures.append("fork")

    if repo.pushed_at:
        pushed = repo.pushed_at.replace(tzinfo=timezone.utc)
        year   = pushed.year
        if year < 2020:
            r.filter_failures.append(f"archived_too_old:{year}")

    if r.filter_failures:
        r.passed_filters = False
        return r

    files = check_files_via_api(repo, logger)

    r.has_pyproject      = files["has_pyproject"]
    r.has_setup_py       = files["has_setup_py"]
    r.has_setup_cfg      = files["has_setup_cfg"]
    r.has_tox            = files["has_tox"]
    r.has_makefile       = files["has_makefile"]
    r.has_dockerfile     = files["has_dockerfile"]
    r.has_docker_compose = files["has_docker_compose"]
    r.has_ci             = files["has_ci"]
    r.ci_platform        = files["ci_platform"]
    r.python_requires    = files["python_requires"]
    r.python_confirmed   = files["python_confirmed"]
    r.has_tests          = files["has_tests"]
    r.test_directory     = files["test_directory"]
    r.test_file_count    = files["test_file_count"]
    r.has_pytest         = files["has_pytest"]

    if files.get("already_migrated"):
        r.filter_failures.append(f"already_supports_312+:{r.python_requires}")
        r.passed_filters = False
        return r

    has_setup = r.has_pyproject or r.has_setup_py or r.has_setup_cfg
    if not has_setup:
        r.filter_failures.append("no_setup_file")

    if not r.has_tests:
        r.filter_failures.append(f"insufficient_tests:{r.test_file_count}")

    if require_docker and not (r.has_dockerfile or r.has_docker_compose):
        r.filter_failures.append("no_docker")

    if require_py310 and not r.python_confirmed:
        r.filter_failures.append("python_310_not_confirmed")

    if r.filter_failures:
        r.passed_filters = False
        return r

    r.quality_score, r.quality_notes = compute_quality_score(r)
    r.passed_filters = True
    return r


# ── Report generation ──────────────────────────────────────────────────────

def generate_markdown_report(records: list[ArchivedRepo]) -> str:
    lines = [
        "# Archived Python Repos — Benchmark Candidates",
        f"",
        f"Found: {len(records)} candidates  ",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}  ",
        f"Archived Bounds: 2020–2026  ",
        f"",
        "---",
        "",
        "## Candidates (sorted by quality score)",
        "",
        "| # | Repo | ★ | py_requires | Tests | Docker | CI | Score | Notes |",
        "|---|------|---|-------------|-------|--------|-----|-------|-------|",
    ]

    for i, r in enumerate(records, 1):
        docker = "🐳" if (r.has_dockerfile or r.has_docker_compose) else "—"
        ci     = "[PASS]" if r.has_ci else "—"
        py_req = r.python_requires[:15] if r.python_requires else "—"
        tests  = f"{r.test_file_count} files" if r.has_tests else "—"
        notes  = ", ".join(r.quality_notes[:2])

        lines.append(
            f"| {i} "
            f"| [{r.full_name}]({r.url}) "
            f"| {r.stars} "
            f"| `{py_req}` "
            f"| {tests} "
            f"| {docker} "
            f"| {ci} "
            f"| **{r.quality_score}** "
            f"| {notes} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Score breakdown",
        "",
        "| Component | Points |",
        "|-----------|--------|",
        "| Has tests (≥3 files) | 20 |",
        "| 10+ test files | +10 |",
        "| Uses pytest | 10 |",
        "| Has pyproject.toml | 15 |",
        "| Has Dockerfile | 15 |",
        "| Has docker-compose | 10 |",
        "| Has CI | 10 |",
        "| Explicitly targets Python 3.10 | 20 |",
        "| Stars ≥500 | 10 |",
        "| Archived within last year | 8 |",
        "",
        "---",
        "",
        "## Next steps",
        "",
        "For each candidate (start from highest score):",
        "",
        "```bash",
        "# Clone the repo",
        "git clone <url>",
        "cd <repo>",
        "",
        "# Try on Python 3.10 first (baseline)",
        "~/.pyenv/versions/3.10.14/bin/python3.10 -m venv .venv310",
        "source .venv310/bin/activate",
        "pip install -e '.[dev]' || pip install -e '.[test]' || pip install -e '.'",
        "pytest tests/ --tb=short -q",
        "",
        "# Then try Python 3.13",
        "~/.pyenv/versions/3.13.1/bin/python3.13 -m venv .venv313",
        "source .venv313/bin/activate",
        "pip install -e '.[dev]' || pip install -e '.[test]' || pip install -e '.'",
        "pytest tests/ --tb=short -q 2>&1 | tee test_313.txt",
        "```",
        "",
        "A repo is a valid benchmark instance if:",
        "- Python 3.10: all tests pass (clean baseline)",
        "- Python 3.13: 5–50 tests fail with runtime errors (not import cascades)",
    ]

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Find archived Python repos from 2020-2026 with tests and setup files"
    )
    parser.add_argument("--max-repos",     type=int, default=DEFAULT_MAX_REPOS,
                        help="Max valid repos to find (default: 100)")
    parser.add_argument("--require-docker", action="store_true",
                        help="Only include repos with Dockerfile or docker-compose")
    parser.add_argument("--require-py310",  action="store_true",
                        help="Only include repos explicitly targeting Python 3.10")
    parser.add_argument("--output",        type=str, default="archived_repos.json")
    parser.add_argument("--verbose",       action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(
                f"archived_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log", encoding="utf-8"),
        ]
    )
    logger = logging.getLogger("find_archived")

    token = os.environ.get("GITHUB_TOKEN", "")
    g     = get_client(token)

    logger.info("=" * 60)
    logger.info("SWE-Adaptive: Finding archived repos (2020-2026)")
    logger.info(f"Target: {args.max_repos} valid repos")
    logger.info(f"Require Docker: {args.require_docker}")
    logger.info(f"Require Python 3.10: {args.require_py310}")
    logger.info("=" * 60)

    # Verification Output
    print(f"Total generated micro-queries: {len(SEARCH_QUERIES)}")
    print("\nFirst 5 sample queries:")
    for q in SEARCH_QUERIES[:5]:
        print(f'  "{q}"')

    seen = set()
    passed_records = []
    
    # ── HYDRATION LAYER: Load existing passed repositories from past runs ────
    out_path = Path(args.output)
    if out_path.exists():
        try:
            existing_data = json.loads(out_path.read_text(encoding="utf-8"))
            if "repos" in existing_data:
                for repo_dict in existing_data["repos"]:
                    record = ArchivedRepo.from_dict(repo_dict)
                    passed_records.append(record)
                    seen.add(record.full_name)
                logger.info(f"Hydrated pipeline: loaded {len(passed_records)} valid repos from {args.output}")
        except Exception as e:
            logger.warning(f"Could not hydrate existing records from json file: {e}. Starting fresh.")

    # ── Load rejected cache ────────────────────────────────────────────────
    rejected_cache_path = out_path.with_name("rejected_cache.json")
    rejected_cache: dict = {}

    if rejected_cache_path.exists():
        try:
            rejected_cache = json.loads(rejected_cache_path.read_text(encoding="utf-8"))
            logger.info(f"Loaded rejected cache: {len(rejected_cache)} repos to skip")
        except Exception:
            rejected_cache = {}

    rejected_count  = 0
    rejection_log   = {}

    def save_rejected_cache():
        rejected_cache_path.write_text(json.dumps(rejected_cache, indent=2), encoding="utf-8")

    # Helper inline function to save passed configurations iteratively to disk
    def save_passed_records_iteratively():
        # 1. Keep the internal dataset correctly ranked by design relevance
        passed_records.sort(key=lambda x: x.quality_score, reverse=True)
        
        # 2. Write out structural machine-readable JSON contents
        out_path.write_text(json.dumps({
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "archived_after": ARCHIVED_AFTER,
                "archived_before": ARCHIVED_BEFORE,
                "total_found": len(passed_records),
                "require_docker": args.require_docker,
                "require_py310": args.require_py310,
                "partial_incremental_save": True
            },
            "repos": [r.to_dict() for r in passed_records]
        }, indent=2, default=str), encoding="utf-8")
        
        # 3. Write out visual human-readable Markdown tracking matrices
        md_path = out_path.with_suffix(".md")
        md_path.write_text(generate_markdown_report(passed_records), encoding="utf-8")

    # Sync initial progress bar state with hydrated data count
    initial_pbar_count = min(len(passed_records), args.max_repos)

    with tqdm(total=args.max_repos, desc="Valid repos found", unit="repo",
              bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]",
              initial=initial_pbar_count) as pbar:

        for query in SEARCH_QUERIES:
            if len(passed_records) >= args.max_repos:
                break

            full_query = query
            logger.info(f"\n  Query: {full_query[:80]}...")

            try:
                check_rate_limit(g, logger)
                results = g.search_repositories(full_query, sort="updated", order="desc")

                checked = 0
                for repo in results:
                    if len(passed_records) >= args.max_repos:
                        break
                    if checked >= args.max_repos * 8:
                        break
                    if repo.full_name in seen:
                        continue
                    if not repo.archived:
                        continue

                    # Skip repos already rejected in a previous run
                    if repo.full_name in rejected_cache:
                        seen.add(repo.full_name)
                        rejected_count += 1
                        continue

                    checked += 1
                    seen.add(repo.full_name)

                    try:
                        check_rate_limit(g, logger)
                        record = assess_repo(
                            repo, logger,
                            args.require_docker,
                            args.require_py310)
                    except Exception as e:
                        logger.warning(f"  Error on {repo.full_name}: {e}")
                        continue

                    if record.passed_filters:
                        passed_records.append(record)
                        pbar.update(1)
                        logger.info(
                            f"  [PASS] {record.full_name} Stars: {record.stars} "
                            f"score={record.quality_score} "
                            f"py={record.python_requires or '?'} "
                            f"tests={record.test_file_count} "
                            f"docker={'yes' if record.has_dockerfile else 'no'}"
                        )
                        # CRITICAL FIX: Save valid candidates immediately to disk
                        save_passed_records_iteratively()
                    else:
                        rejected_count += 1
                        rejected_cache[repo.full_name] = {
                            "reasons":     record.filter_failures,
                            "stars":       record.stars,
                            "pushed_at":   record.pushed_at[:10],
                            "rejected_at": datetime.now().isoformat()[:10],
                        }
                        for reason in record.filter_failures:
                            key = reason.split(":")[0]
                            rejection_log[key] = rejection_log.get(key, 0) + 1
                        save_rejected_cache()

                    time.sleep(0.4)

            except GithubException as e:
                logger.warning(f"  Query failed: {e}")
            except Exception as e:
                logger.warning(f"  Error: {e}")

            save_rejected_cache()
            time.sleep(2)

    # Final execution wrap up saves
    save_rejected_cache()
    save_passed_records_iteratively()

    logger.info(f"\nPassed: {len(passed_records)} | Rejected: {rejected_count}")
    if rejection_log:
        for reason, count in sorted(rejection_log.items(), key=lambda x: -x[1]):
            logger.info(f"  {reason:<35} {count}")

if __name__ == "__main__":
    main()