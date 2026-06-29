#!/usr/bin/env python3
"""
Automated SWE-Adaptive benchmark creator.

For each repo in archived_repos.json (after femueller/python-n26):
  1. Clone the repo
  2. Probe Python 3.13 (install + test via Docker RUN — build fails if tests fail)
  3. If 3.13 fails → establish Python 3.10 baseline
  4. If 3.10 passes  → create Dockerfile.test, Dockerfile.py313, BENCHMARK.md
  5. Move dir to success_benchmark/

Usage:
    python3 auto_benchmark.py [--start-after femueller/python-n26] [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import textwrap
import time
from datetime import datetime
from pathlib import Path

# ── paths ──────────────────────────────────────────────────────────────────────
BASE_DIR         = Path(__file__).parent.resolve()
SUCCESS_DIR      = BASE_DIR / "success_benchmark"     # 3.13 fails + baseline tests pass
VALID_CASES_DIR  = BASE_DIR / "valid_cases"           # 3.13 fails + baseline installs but tests need work
REVIEW_DIR       = BASE_DIR / "skip_passing_review"   # 3.13 already passes — not a benchmark candidate
WORK_DIR         = BASE_DIR / "_benchmark_work"       # scratch space for clones
LOG_PATH         = BASE_DIR / "benchmark_run.log"
PROCESSED_FILE   = BASE_DIR / "processed_repos.json"

# ── Infrastructure failure patterns — why tests fail on ALL Python versions ────
# Used to produce a clear one-line skip reason in the log.
INFRA_SKIP_PATTERNS = [
    (r"redis\.exceptions\.ConnectionError|redis\.exceptions\.ResponseError",
     "tests require a running Redis service"),
    (r"TEST_DATABASE_URLS is not set|DATABASE_URL.*not set|connection refused.*postgres|connection refused.*mysql|sqlalchemy.*could not connect",
     "tests require a running database service (env var or live DB)"),
    (r"consul\.exceptions\.|ConnectionRefusedError.*8500|consul.*connect",
     "tests require a running Consul service"),
    (r"ModuleNotFoundError: No module named 'tensorflow'",
     "tests require tensorflow (too large to install in benchmark)"),
    (r"AssertionError: TEST_DATABASE_URLS",
     "tests require database URL env var"),
    (r"No module named 'adb'|adb.*device.*not found|AndroidError",
     "tests require a connected Android device (ADB)"),
    (r"No module named 'tests'",
     "pytest import error — test module path misconfiguration"),
    (r"FileNotFoundError.*\.(json|yaml|bin|pkl|pt|h5|csv|txt)",
     "tests require data files not bundled in the repo"),
    (r"requests\.exceptions\.ConnectionError|urllib.*ConnectionRefusedError|HTTPSConnectionPool.*Failed to establish",
     "tests make real network/HTTP calls (need external services or API keys)"),
    (r"API_KEY|api_key.*required|BITLY_TOKEN|AUTH_TOKEN.*not set",
     "tests require API keys / credentials"),
    (r"pkgutil.*ImpImporter|pkg_resources.*ImpImporter",
     "old setuptools/pkg_resources incompatible — pkgutil.ImpImporter removed in Python 3.12"),
    (r"collected 0 items|no tests ran",
     "pytest collects 0 tests — test suite requires special config, plugins, or credentials"),
    # pip install / build failures
    (r"ERROR: Could not find a version that satisfies the requirement",
     "pip cannot find a matching package version — dependency incompatible with this Python"),
    (r"ERROR: No matching distribution found for",
     "pip cannot find a distribution — package unavailable for this Python/platform"),
    (r"error: command '.*gcc.*' failed|error: Microsoft Visual C\+\+",
     "C extension build failed — missing compiler or incompatible C headers"),
    (r"error: legacy-install-failure|ERROR: legacy-install-failure",
     "package has no wheel and source build failed"),
]


def categorize_skip_reason(combined_output: str) -> str:
    """Return a human-readable one-liner for why all baseline versions failed."""
    for pattern, reason in INFRA_SKIP_PATTERNS:
        if re.search(pattern, combined_output, re.IGNORECASE):
            return reason
    return "unknown — check log output above for details"


# ── Known Python 3.13 breaking-change patterns ─────────────────────────────────
# Each entry: (regex, human description, minimal fix).
BREAKING_PATTERNS = [
    (
        r"No module named 'cgi'|from cgi import|import cgi\b",
        "`cgi` module removed in Python 3.13 (PEP 594)",
        "Upgrade the dependency that imports `cgi` to a Python 3.13-compatible release.",
    ),
    (
        r"No module named 'pkg_resources'",
        "`pkg_resources` unavailable — `setuptools` is no longer bundled in Python 3.13+",
        "Add `setuptools` as an explicit dependency, or upgrade the package that uses `pkg_resources`.",
    ),
    (
        r"cannot import name 'Annotated' from 'pydantic\.typing'",
        "`pydantic.typing.Annotated` — private pydantic v1 API removed in pydantic v2",
        "Upgrade `inflect` (or the relevant package) to a version that supports pydantic v2.",
    ),
    (
        r"'build_ext' object has no attribute 'cython_sources'",
        "`PyYAML==6.0` has no Python 3.13 wheel; Cython source build is incompatible with modern setuptools",
        "Upgrade `pyyaml` to `>=6.0.1` which ships a Python 3.13-compatible wheel.",
    ),
    (
        r"cannot import name 'url_quote' from 'werkzeug",
        "`werkzeug` 3.x removed `url_quote`, which Flask 2.1.x relied on",
        "Pin `werkzeug<3.0`, or upgrade Flask to a version that supports werkzeug 3.x.",
    ),
    (
        r"No module named 'distutils'",
        "`distutils` removed in Python 3.12+ (deprecated since 3.10)",
        "Upgrade `setuptools` and any package that imports `distutils` directly.",
    ),
    (
        r"No module named 'imp'",
        "`imp` module removed in Python 3.12+ (deprecated since 3.4)",
        "Upgrade the package that imports `imp` to a newer version using `importlib`.",
    ),
    (
        r"No module named 'pipes'",
        "`pipes` module removed in Python 3.13 (PEP 594)",
        "Upgrade the package that imports `pipes`.",
    ),
    (
        r"No module named '(?:aifc|chunk|sunau|telnetlib|uu|xdrlib|nntplib|imghdr|sndhdr|msilib|ossaudiodev|spwd)'",
        "Removed stdlib module (PEP 594) — one of several modules deleted in Python 3.13",
        "Upgrade the dependency that imports the removed module.",
    ),
    (
        r"No module named 'typing_extensions'",
        "`typing_extensions` not installed (required by many packages on older Python)",
        "Add `typing_extensions` as an explicit dependency.",
    ),
    (
        r"collections\.(?:Callable|Mapping|MutableMapping|Sequence|Iterable|Iterator|MutableSequence|Set|MutableSet)\b",
        "Deprecated `collections.X` alias removed in Python 3.10+ — must use `collections.abc.X`",
        "Upgrade the affected dependency to a version that uses `collections.abc.*`.",
    ),
    (
        r"SyntaxError:",
        "Syntax error — code uses Python syntax not valid in 3.13",
        "Review and update the syntax in the affected module.",
    ),
    (
        r"RuntimeError: There is no current event loop",
        "`asyncio.get_event_loop()` raises RuntimeError in Python 3.10+ when called outside a running loop",
        "Upgrade the package or configure `asyncio_mode = auto` in pytest settings.",
    ),
    (
        r"No module named 'collections\.abc'",
        "`collections.abc` import issue",
        "Upgrade the affected dependency.",
    ),
    (
        r"AttributeError: module 'asyncio' has no attribute",
        "asyncio API change in Python 3.10+",
        "Upgrade the affected dependency to a version compatible with Python 3.10+.",
    ),
    (
        r"No module named 'ssl'|ssl\.SSLError|ssl\.PROTOCOL_TLS\b",
        "SSL/TLS API change or missing ssl module",
        "Check ssl configuration and upgrade affected dependencies.",
    ),
]

# ── Logging ────────────────────────────────────────────────────────────────────

def log(msg: str, level: str = "INFO") -> None:
    ts   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level:5s}] {msg}"
    print(line, flush=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def sep(char: str = "─", width: int = 72) -> None:
    log(char * width)


# ── Shell helpers ───────────────────────────────────────────────────────────────

def safe_move(src: Path, dst: Path) -> None:
    """shutil.move with retry for Windows file-locking (OneDrive, Defender)."""
    for attempt in range(3):
        try:
            shutil.move(str(src), str(dst))
            return
        except OSError:
            if attempt < 2:
                time.sleep(2 ** attempt)
    shutil.copytree(str(src), str(dst), dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns(".git"))
    rmtree(src)


def rmtree(path: Path) -> None:
    """shutil.rmtree with read-only handling and retry for OneDrive/Defender file locks."""
    def _handle_readonly(func, fpath, _):
        try:
            os.chmod(fpath, stat.S_IWRITE)
            func(fpath)
        except OSError:
            pass
    for attempt in range(3):
        try:
            if sys.version_info >= (3, 12):
                shutil.rmtree(path, onexc=_handle_readonly)
            else:
                shutil.rmtree(path, onerror=_handle_readonly)
            return
        except OSError:
            if attempt < 2:
                time.sleep(2 ** attempt)


def run(cmd, cwd=None, timeout=300, env=None):
    """Run a command, return (returncode, combined_output_str)."""
    try:
        r = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=env,
        )
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return -1, "TIMEOUT"
    except Exception as exc:
        return -1, str(exc)


# ── Repo config detection ───────────────────────────────────────────────────────

REQ_FILES = [
    "requirements.txt",
    "requirements/base.txt",
    "requirements/main.txt",
    "requirements/common.txt",
]
TEST_REQ_FILES = [
    "requirements-test.txt",
    "requirements_test.txt",
    "test-requirements.txt",
    "requirements-dev.txt",
    "requirements_dev.txt",
    "dev-requirements.txt",
    "requirements/test.txt",
    "requirements/dev.txt",
    "requirements/testing.txt",
    "requirements/tests.txt",
]

# Test-related package keywords — used to filter poetry dev-deps
_TEST_PKG_KEYWORDS = (
    "pytest", "mock", "fake", "factory", "test", "responses",
    "hypothesis", "coverage", "asynctest", "aiohttp",
)

def _parse_pyproject_extras(pyproject_text: str) -> list:
    """
    Return extras names that look like test/dev groups.
    Handles PEP-621 [project.optional-dependencies] sections.
    """
    test_extras = []
    for m in re.finditer(r'\[project\.optional-dependencies\.(\w+)\]', pyproject_text):
        name = m.group(1).lower()
        if name in ("test", "tests", "dev", "testing", "check"):
            test_extras.append(m.group(1))
    return test_extras


def _parse_poetry_dev_deps(pyproject_text: str) -> list:
    """
    Extract package names from [tool.poetry.dev-dependencies] or
    [tool.poetry.group.dev.dependencies] that look test-related.
    """
    deps = []
    section_patterns = [
        r'\[tool\.poetry\.dev-dependencies\](.*?)(?=\n\[|\Z)',
        r'\[tool\.poetry\.group\.dev\.dependencies\](.*?)(?=\n\[|\Z)',
        r'\[tool\.poetry\.group\.test\.dependencies\](.*?)(?=\n\[|\Z)',
    ]
    for pat in section_patterns:
        m = re.search(pat, pyproject_text, re.DOTALL)
        if not m:
            continue
        block = m.group(1)
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("["):
                continue
            pkg_m = re.match(r'^([A-Za-z0-9_\-\.]+)\s*[=<>!]', line)
            if pkg_m:
                pkg = pkg_m.group(1).lower()
                if any(kw in pkg for kw in _TEST_PKG_KEYWORDS):
                    deps.append(pkg_m.group(1))
    return deps


def detect_config(repo_dir: Path, repo_info: dict) -> dict:
    """
    Heuristically determine how to install and test this repo.
    Returns a dict with keys:
      install_lines : list[str]   — pip install commands (full, incl 'pip install ...')
      test_cmd      : str         — pytest invocation
      has_tests     : bool
    """
    cfg = {
        "install_lines": [],
        "test_cmd":      "pytest tests/ -v",
        "has_tests":     False,
    }

    # ── test command ──────────────────────────────────────────────────────
    test_dir = repo_info.get("test_directory") or "tests"
    if (repo_dir / test_dir).exists():
        cfg["has_tests"]  = True
        cfg["test_cmd"]   = f"pytest {test_dir}/ -v"
    elif (repo_dir / "test").exists():
        cfg["has_tests"]  = True
        cfg["test_cmd"]   = "pytest test/ -v"
    else:
        hits = list(repo_dir.glob("**/test_*.py"))[:3]
        if hits:
            cfg["has_tests"] = True

    # honour pytest testpaths from config files
    for cfg_file in ["pytest.ini", "setup.cfg", "pyproject.toml"]:
        path = repo_dir / cfg_file
        if not path.exists():
            continue
        txt = path.read_text(errors="replace")
        m = re.search(r"testpaths\s*[=:]\s*(.+)", txt)
        if m:
            raw = m.group(1).strip()
            # TOML list like ["tests"] or plain "tests tests2"
            paths = re.findall(r'[\w/]+', raw)
            if paths:
                cfg["test_cmd"] = "pytest " + " ".join(paths) + " -v"
                cfg["has_tests"] = True
        break

    # ── install steps ─────────────────────────────────────────────────────
    found_reqs      = [rf for rf in REQ_FILES      if (repo_dir / rf).exists()]
    found_test_reqs = [rf for rf in TEST_REQ_FILES if (repo_dir / rf).exists()]

    if found_reqs or found_test_reqs:
        parts = [f"-r {r}" for r in found_reqs + found_test_reqs]
        cfg["install_lines"].append("pip install --no-cache-dir " + " ".join(parts))

    has_pkg = any(
        (repo_dir / f).exists()
        for f in ("setup.py", "pyproject.toml", "setup.cfg")
    )

    # Try extras from pyproject.toml
    pyproject_path = repo_dir / "pyproject.toml"
    extra_test_deps = []
    if pyproject_path.exists():
        pyproject_text = pyproject_path.read_text(errors="replace")
        # PEP-621 extras
        pep621_extras = _parse_pyproject_extras(pyproject_text)
        if has_pkg and pep621_extras:
            extras_str = ",".join(pep621_extras)
            cfg["install_lines"].append(f"pip install --no-cache-dir -e '.[{extras_str}]'")
            has_pkg = False  # already handled -e install
        # Poetry dev deps
        extra_test_deps = _parse_poetry_dev_deps(pyproject_text)

    if has_pkg:
        cfg["install_lines"].append("pip install --no-cache-dir -e .")

    # Install poetry dev deps that look test-related
    if extra_test_deps:
        cfg["install_lines"].append(
            "pip install --no-cache-dir " + " ".join(extra_test_deps)
        )

    if not cfg["install_lines"]:
        cfg["install_lines"].append("pip install --no-cache-dir pytest")

    # always ensure pytest is available
    if not any("pytest" in l for l in cfg["install_lines"]):
        cfg["install_lines"].append("pip install --no-cache-dir pytest")

    return cfg


# ── Dockerfile generation ───────────────────────────────────────────────────────

def make_dockerfile(python_version: str, cfg: dict, probe: bool = False) -> str:
    """
    Generate Dockerfile content.
    probe=True  → RUN pytest (build fails on test failure = py313 image)
    probe=False → CMD pytest  (run-time = baseline image)
    """
    lines = [
        f"FROM python:{python_version}-slim",
        "WORKDIR /root/code",
        "RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*",
        "COPY . .",
    ]

    # Dockerfile RUN uses /bin/sh so single-quoted shell expansions work.
    install_block = ["pip install --no-cache-dir --upgrade pip"] + cfg["install_lines"]
    joined = " \\\n && ".join(install_block)
    lines.append(f"RUN {joined}")

    if probe:
        lines.append(f"RUN {cfg['test_cmd']}")
    else:
        parts   = cfg["test_cmd"].split()
        cmd_str = json.dumps(parts)
        lines.append(f"CMD {cmd_str}")

    return "\n".join(lines) + "\n"


# ── Docker build / run ──────────────────────────────────────────────────────────

def docker_build(tag: str, dockerfile_content: str, context: Path, timeout: int = 600):
    """Write a temp Dockerfile outside the context dir, build image, remove temp file.
    Returns (returncode, output)."""
    # Write outside the context dir so COPY . . in the Dockerfile doesn't include it
    tmp_df = Path(tempfile.gettempdir()) / f"_Dockerfile_tmp_{context.name}_{os.getpid()}"
    tmp_df.write_text(dockerfile_content, encoding="utf-8")
    try:
        rc, out = run(
            ["docker", "build", "-t", tag, "-f", str(tmp_df), str(context)],
            timeout=timeout,
        )
        return rc, out
    finally:
        tmp_df.unlink(missing_ok=True)


def docker_run(tag: str, timeout: int = 180):
    """Run a Docker container to completion. Returns (returncode, output)."""
    rc, out = run(["docker", "run", "--rm", "--network=none", tag], timeout=timeout)
    return rc, out


def docker_rmi(tag: str) -> None:
    run(["docker", "rmi", "-f", tag], timeout=30)


# ── Error analysis ──────────────────────────────────────────────────────────────

def analyze(output: str) -> list:
    """Return list of (pattern, description, fix) for matching breaking-change patterns."""
    found = []
    for pattern, desc, fix in BREAKING_PATTERNS:
        if re.search(pattern, output, re.IGNORECASE | re.MULTILINE):
            found.append((pattern, desc, fix))
    return found


def extract_error_snippet(output: str, max_lines: int = 20) -> str:
    """Extract the most relevant error lines from Docker build output."""
    lines = output.splitlines()
    relevant = []
    capture  = False
    for line in lines:
        if any(kw in line for kw in ("ERROR:", "Error:", "Traceback", "ImportError",
                                      "ModuleNotFoundError", "AttributeError",
                                      "SyntaxError", "FAILED", "error:")):
            capture = True
        if capture:
            relevant.append(line)
        if len(relevant) >= max_lines:
            break
    return "\n".join(relevant) if relevant else "\n".join(lines[-max_lines:])


def extract_issue_snippet(output: str, pattern: str, context_lines: int = 15) -> str:
    """Extract lines around the first regex match of pattern in output."""
    lines = output.splitlines()
    for i, line in enumerate(lines):
        if re.search(pattern, line, re.IGNORECASE):
            start = max(0, i - 3)
            end   = min(len(lines), i + context_lines)
            return "\n".join(lines[start:end])
    return extract_error_snippet(output, context_lines)


# ── BENCHMARK.md generation ─────────────────────────────────────────────────────

def generate_benchmark_md(
    repo_info:        dict,
    baseline_version: str,
    baseline_passed:  int,
    baseline_total:   int,
    py313_output:     str,
    issues:           list,  # list of (pattern, desc, fix)
    baseline_extra_notes: str = "",
) -> str:
    repo_name = repo_info["full_name"]
    repo_url  = repo_info.get("url", f"https://github.com/{repo_name}")

    issue_rows = "\n".join(
        f"| {i+1} | {desc} | {fix} |"
        for i, (_, desc, fix) in enumerate(issues)
    )
    if not issue_rows:
        issue_rows = "| ? | Unknown error — see raw output above | Investigate manually |"

    issue_sections = ""
    for i, (pattern, desc, fix) in enumerate(issues, 1):
        snippet = extract_issue_snippet(py313_output, pattern)
        issue_sections += f"""
### Error {i} — {desc}

```
{snippet.strip()}
```

**Root cause:** {desc}

**Minimal fix:** {fix}
"""

    if not issues:
        error_snippet = extract_error_snippet(py313_output)
        issue_sections = f"""
### Error — unknown

```
{error_snippet.strip()}
```

**Root cause:** Requires manual investigation.

**Minimal fix:** Investigate the error above.
"""

    baseline_note = f"\n{baseline_extra_notes.strip()}" if baseline_extra_notes.strip() else ""

    return f"""# Benchmark: {repo_name.split("/")[1]}

**Repository:** {repo_url}
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python {baseline_version})

**Docker image:** `Dockerfile.test`
**Python version:** {baseline_version}
**Result:** {baseline_passed} passed, {baseline_total - baseline_passed} failed{baseline_note}

All {baseline_passed} tests pass on Python {baseline_version}.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails
{issue_sections}
---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
{issue_rows}
"""


# ── Main per-repo pipeline ──────────────────────────────────────────────────────

def process_repo(repo_info: dict, dry_run: bool = False) -> str:
    """
    Process one repo.  Returns one of:
      "success"      — 3.13 fails + baseline passes → artifacts created, moved to success_benchmark/
      "valid_case"   — 3.13 fails + baseline installs but tests need work → valid_cases/
      "skip_passing" — 3.13 installs fine → not a benchmark candidate → skip_passing_review/
      "skip_notests" — no tests detected
      "skip_clone"   — clone failed
      "skip_baseline"— install fails on all baseline versions (3.10 → 3.7)
      "skip_error"   — unrecoverable error
      "dry_run"      — stopped after config detection (--dry-run mode)
    """
    repo_name  = repo_info["full_name"]
    short_name = repo_name.replace("/", "_")
    tag_base   = f"swe-bench-{short_name.lower().replace('_', '-')}"

    sep()
    log(f"REPO  : {repo_name}")
    log(f"URL   : {repo_info.get('url', 'n/a')}")
    log(f"Stars : {repo_info.get('stars', '?')}  |  Python-requires: {repo_info.get('python_requires', 'unspecified')}")

    # ── 1. Clone ──────────────────────────────────────────────────────────
    # Skip if already successfully benchmarked
    success_dest = SUCCESS_DIR / short_name
    if success_dest.exists():
        log("Already in success_benchmark — skipping", "INFO")
        return "skip_done"

    repo_dir = WORK_DIR / short_name
    if repo_dir.exists():
        log(f"Removing existing work dir for clean state…")
        rmtree(repo_dir)
    log("Cloning…")
    rc, out = run(
        ["git", "clone", "--depth=1",
         f"https://github.com/{repo_name}.git", str(repo_dir)],
        timeout=120,
    )
    if rc != 0:
        log(f"Clone failed:\n{out[:400]}", "ERROR")
        if repo_dir.exists():
            rmtree(repo_dir)
        return "skip_clone"
    log("Clone OK")

    # ── 2. Detect config ──────────────────────────────────────────────────
    cfg = detect_config(repo_dir, repo_info)
    log(f"Install steps : {cfg['install_lines']}")
    log(f"Test command  : {cfg['test_cmd']}")
    log(f"Has tests     : {cfg['has_tests']}")

    if not cfg["has_tests"]:
        log("No tests detected — skipping", "WARN")
        rmtree(repo_dir)
        return "skip_notests"

    if dry_run:
        log("DRY-RUN — stopping here", "WARN")
        return "dry_run"

    # ── 3. Check Python 3.13 installation ────────────────────────────────
    # Use probe=False (CMD pytest) so we only check installation, not tests.
    # If the install succeeds, 3.13 is already compatible — not a benchmark.
    log("▶ Checking Python 3.13 installation…")
    df313_check = make_dockerfile("3.13", cfg, probe=False)
    tag313      = f"{tag_base}-py313-check"
    rc313, out313 = docker_build(tag313, df313_check, repo_dir, timeout=600)
    docker_rmi(tag313)

    if rc313 == 0:
        log("Python 3.13: installation PASSED — not a valid benchmark candidate", "WARN")
        dest_review = REVIEW_DIR / short_name
        if dest_review.exists():
            rmtree(dest_review)
        safe_move(repo_dir, dest_review)
        log(f"Moved to skip_passing_review/{short_name}")
        return "skip_passing"

    log("Python 3.13: installation FAILED (as expected for a benchmark)")
    issues = analyze(out313)
    for _, desc, fix in issues:
        log(f"  ↳ issue: {desc}")
    if not issues:
        log("  ↳ No known breaking-change pattern matched — unknown install error")

    # ── 4. Baseline: try 3.10 → 3.9 → 3.8 → 3.7 ────────────────────────────
    # Two-tier result:
    #   valid_install_ver / valid_install_df — first version where install passes
    #   baseline_version  / df_baseline      — first version where install + tests pass
    valid_install_ver = None
    valid_install_df  = None
    valid_test_output = ""
    baseline_version  = None
    df_baseline       = None
    n_passed = 0
    n_total  = 0
    all_failure_output = ""

    for try_ver in ("3.10", "3.9", "3.8", "3.7"):
        log(f"▶ Testing baseline on Python {try_ver}…")
        df_try  = make_dockerfile(try_ver, cfg, probe=False)
        tag_try = f"{tag_base}-py{try_ver.replace('.', '')}"
        rc_build, out_build = docker_build(tag_try, df_try, repo_dir, timeout=600)

        if rc_build != 0:
            log(f"Python {try_ver} install FAILED — trying lower version", "WARN")
            log(extract_error_snippet(out_build, max_lines=40), "WARN")
            all_failure_output += out_build
            docker_rmi(tag_try)
            continue

        # Install succeeded — record as valid_case candidate if first
        if valid_install_ver is None:
            valid_install_ver = try_ver
            valid_install_df  = df_try

        log(f"Python {try_ver} install OK — running tests…")
        rc_run, out_run = docker_run(tag_try, timeout=180)
        docker_rmi(tag_try)

        if rc_run != 0:
            if re.search(r"collected 0 items|no tests ran", out_run):
                log(f"Python {try_ver} — 0 tests collected, trying lower version", "WARN")
            else:
                log(f"Python {try_ver} tests FAILED — trying lower version", "WARN")
                log(out_run[-400:], "WARN")
            valid_test_output = out_run  # keep for NOTES.md
            all_failure_output += out_run
            continue

        # Tests passed — full success
        summary_line = ""
        for line in reversed(out_run.splitlines()):
            if re.search(r"\d+ (?:passed|failed|error)", line):
                summary_line = line
                break
        m_passed = re.search(r"(\d+) passed", summary_line or out_run)
        n_passed = int(m_passed.group(1)) if m_passed else 0
        if summary_line:
            all_nums = re.findall(r"(\d+) (?:passed|failed|error)", summary_line)
            n_total  = sum(int(x) for x in all_nums) if all_nums else n_passed
        else:
            n_total = n_passed
        baseline_version = try_ver
        df_baseline      = df_try
        log(f"Python {try_ver} baseline: {n_passed} passed / {n_total} total ✓")
        break

    # ── 5. Route to outcome ───────────────────────────────────────────────
    if baseline_version is not None:
        # Full success — write all artifacts and move to success_benchmark/
        (repo_dir / "Dockerfile.test").write_text(df_baseline, encoding="utf-8")
        log("Wrote Dockerfile.test")
        (repo_dir / "Dockerfile.py313").write_text(make_dockerfile("3.13", cfg, probe=True), encoding="utf-8")
        log("Wrote Dockerfile.py313")
        bm_md = generate_benchmark_md(
            repo_info        = repo_info,
            baseline_version = baseline_version,
            baseline_passed  = n_passed,
            baseline_total   = n_total,
            py313_output     = out313,
            issues           = issues,
        )
        (repo_dir / "BENCHMARK.md").write_text(bm_md, encoding="utf-8")
        log("Wrote BENCHMARK.md")
        dest = SUCCESS_DIR / short_name
        if dest.exists():
            rmtree(dest)
        safe_move(repo_dir, dest)
        log(f"Moved to success_benchmark/{short_name}")
        return "success"

    if valid_install_ver is not None:
        # Install works on some version but tests need manual fixing → valid_cases/
        log(f"Python {valid_install_ver} install OK but tests fail — saving to valid_cases/", "WARN")
        (repo_dir / "Dockerfile.test").write_text(valid_install_df, encoding="utf-8")
        (repo_dir / "Dockerfile.py313").write_text(make_dockerfile("3.13", cfg, probe=True), encoding="utf-8")
        skip_reason = categorize_skip_reason(valid_test_output)
        notes = f"""# Valid Case: {repo_name}

**Python 3.13 installation:** FAILS — this repo is a benchmark candidate.
**Baseline Python {valid_install_ver} installation:** PASSES
**Baseline tests:** FAIL — needs manual Dockerfile pinning to pass

## Why tests fail on {valid_install_ver}

{skip_reason}

```
{extract_error_snippet(valid_test_output).strip()}
```

## Why 3.13 installation fails

```
{extract_error_snippet(out313).strip()}
```
"""
        (repo_dir / "NOTES.md").write_text(notes, encoding="utf-8")
        dest = VALID_CASES_DIR / short_name
        if dest.exists():
            rmtree(dest)
        safe_move(repo_dir, dest)
        log(f"Moved to valid_cases/{short_name}")
        return "valid_case"

    # Nothing installs on any baseline version
    skip_reason = categorize_skip_reason(all_failure_output)
    log(f"SKIP REASON: {skip_reason}", "ERROR")
    log("No installable baseline found on 3.10 → 3.7 — skipping", "ERROR")
    rmtree(repo_dir)
    return "skip_baseline"


# ── Processed-repo tracking ─────────────────────────────────────────────────────

def load_processed_repos() -> dict:
    """Return dict of full_name -> {outcome, processed_at} from processed_repos.json."""
    if not PROCESSED_FILE.exists():
        return {}
    try:
        return json.loads(PROCESSED_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_processed_repo(processed: dict, name: str, outcome: str) -> None:
    """Record a repo as processed and persist to processed_repos.json."""
    processed[name] = {
        "outcome": outcome,
        "processed_at": datetime.now().isoformat(),
    }
    # Merge with whatever is currently on disk (handles mid-run recovery restores).
    try:
        on_disk = json.loads(PROCESSED_FILE.read_text(encoding="utf-8"))
    except Exception:
        on_disk = {}
    on_disk.update(processed)  # in-memory entries win over stale disk entries
    PROCESSED_FILE.write_text(json.dumps(on_disk, indent=2), encoding="utf-8")


# ── Entry point ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-after", default=None,
                        help="Skip all repos up to and including this one (positional, one-time override).")
    parser.add_argument("--only",        default=None,
                        help="Process only this repo (full_name), then stop.")
    parser.add_argument("--dry-run",     action="store_true",
                        help="Clone + detect config only, no Docker builds.")
    parser.add_argument("--repos-file",  default=None,
                        help="Path to JSON repos file (default: archived_repos.json next to script).")
    parser.add_argument("--reprocess",   action="store_true",
                        help="Re-process repos even if already recorded in processed_repos.json.")
    args = parser.parse_args()

    WORK_DIR.mkdir(parents=True, exist_ok=True)
    SUCCESS_DIR.mkdir(parents=True, exist_ok=True)
    VALID_CASES_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)

    repos_file = Path(args.repos_file) if args.repos_file else BASE_DIR / "archived_repos.json"
    data  = json.loads(repos_file.read_text(encoding="utf-8"))
    repos = data["repos"]

    # Load previously processed repos
    processed = load_processed_repos()
    log(f"Loaded {len(processed)} previously processed repos from {PROCESSED_FILE.name}")

    # Apply --start-after positional filter (one-time override)
    start_idx = 0
    if args.start_after:
        found_start = False
        for i, r in enumerate(repos):
            if r["full_name"] == args.start_after:
                start_idx = i + 1
                found_start = True
                break
        if not found_start:
            log(f"WARNING: --start-after '{args.start_after}' not found in repos list — processing all {len(repos)} repos", "WARN")

    todo = repos[start_idx:]

    # Filter out repos already recorded in processed_repos.json
    if not args.reprocess:
        before = len(todo)
        todo = [r for r in todo if r["full_name"] not in processed]
        skipped = before - len(todo)
        if skipped:
            log(f"Skipping {skipped} already-processed repos (use --reprocess to override)")

    log(f"{'=' * 72}")
    log(f"SWE-Adaptive Auto-Benchmark  |  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"Starting after : {args.start_after or '(none)'}")
    log(f"Repos to process: {len(todo)}")
    log(f"{'=' * 72}")

    results = {}
    for repo_info in todo:
        name = repo_info["full_name"]
        if args.only and name != args.only:
            continue
        try:
            outcome = process_repo(repo_info, dry_run=args.dry_run)
        except Exception as exc:
            log(f"Unhandled exception for {name}: {exc}", "ERROR")
            outcome = "skip_error"
        results[name] = outcome
        save_processed_repo(processed, name, outcome)
        if args.only:
            break

    sep("=")
    log("FINAL RESULTS")
    sep("=")
    counts = {}
    for name, outcome in results.items():
        counts[outcome] = counts.get(outcome, 0) + 1
        if outcome == "success":
            icon = "✓"
        elif outcome in ("dry_run", "skip_passing", "valid_case"):
            icon = "~"
        else:
            icon = "✗"
        log(f"  {icon}  {name:<45}  {outcome}")
    sep()
    for outcome, count in sorted(counts.items()):
        log(f"  {outcome}: {count}")
    log(f"Done. Log: {LOG_PATH}")


if __name__ == "__main__":
    main()
