#!/usr/bin/env python3
"""
analyze_runs.py
===============
Comprehensive analysis of all completed evaluation runs.

Usage:
  python analyze_runs.py
  python analyze_runs.py --model deepseek/deepseek-v4-flash
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import yaml

# ── Config ────────────────────────────────────────────────────────────────────

SCRIPT_DIR       = Path(__file__).parent.resolve()
MINI_CONFIG_PATH = SCRIPT_DIR / "mini_config.yaml"

EVAL_BASE      = SCRIPT_DIR
INSTANCES_JSON = EVAL_BASE / "instances" / "instances.json"
RUNS_DIR       = EVAL_BASE / "runs"
RESULTS_DIR    = EVAL_BASE / "results"

_STEP_LIMIT = 50
try:
    with open(MINI_CONFIG_PATH) as _f:
        _mc = yaml.safe_load(_f)
        _STEP_LIMIT = (_mc.get("agent") or {}).get("step_limit", 50)
except Exception:
    pass

_MODEL_PRICING = {
    "deepseek/deepseek-v4-flash": {
        "cache_hit_per_m":  0.0028,
        "cache_miss_per_m": 0.14,
        "output_per_m":     0.28,
    },
    "deepseek/deepseek-v4-pro": {
        "cache_hit_per_m":  0.003625,
        "cache_miss_per_m": 0.435,
        "output_per_m":     0.87,
    },
    "gemini/gemini-3.5-flash": {
        "cache_hit_per_m":  0.0375,   # cached input (75% off standard)
        "cache_miss_per_m": 0.15,     # non-cached input
        "output_per_m":     9.00,
    },
}

_SHORT_MODEL = {
    "deepseek__deepseek-v4-flash": "deepseek-v4-flash",
    "deepseek__deepseek-v4-pro":   "deepseek-v4-pro",
    "gemini__gemini-3.5-flash":    "gemini-3.5-flash",
}

def _short(model: str) -> str:
    return _SHORT_MODEL.get(model, model)


# ── File classification ───────────────────────────────────────────────────────

_DEP_FILES = {
    "requirements.txt", "requirements-dev.txt", "requirements_dev.txt",
    "requirements-test.txt", "requirements_test.txt",
    "pyproject.toml", "setup.py", "setup.cfg",
    "Pipfile", "Pipfile.lock", "poetry.lock",
    "constraints.txt", "tox.ini", "hatch.toml",
    "Dockerfile.py313",
}


def _is_dep_file(path: str) -> bool:
    name = Path(path).name
    return name in _DEP_FILES or bool(re.match(r"requirements.*\.txt$", name))


def _is_test_file(path: str) -> bool:
    parts = Path(path).parts
    name  = Path(path).name
    return (
        "tests" in parts or "test" in parts
        or name.startswith("test_")
        or name.endswith("_test.py")
    )


def _is_source_file(path: str) -> bool:
    return (
        path.endswith(".py")
        and not _is_dep_file(path)
        and not _is_test_file(path)
    )


# ── Loaders ───────────────────────────────────────────────────────────────────

def _load_instances() -> dict:
    if not INSTANCES_JSON.exists():
        return {}
    data = json.loads(INSTANCES_JSON.read_text())
    return {i["instance_id"]: i for i in data.get("instances", [])}


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}


# ── Diff analysis ─────────────────────────────────────────────────────────────

def _analyze_diff(diff_path: Path) -> dict:
    if not diff_path.exists():
        return {
            "diff_available":      False,
            "test_files_modified": False,
            "test_files":          [],
            "dep_only":            False,
            "source_changed":      False,
            "dockerfile_in_diff":  False,
            "changed_files":       [],
        }

    text = diff_path.read_text(encoding="utf-8", errors="replace")
    changed_files = [
        line[6:] for line in text.splitlines() if line.startswith("+++ b/")
    ]

    test_files   = [f for f in changed_files if _is_test_file(f)]
    source_files = [f for f in changed_files if _is_source_file(f)]
    dockerfile   = any("Dockerfile.py313" in f for f in changed_files)
    dep_only     = bool(changed_files) and not test_files and not source_files

    return {
        "diff_available":      bool(text.strip()),
        "test_files_modified": bool(test_files),
        "test_files":          test_files,
        "dep_only":            dep_only,
        "source_changed":      bool(source_files),
        "dockerfile_in_diff":  dockerfile,
        "changed_files":       changed_files,
    }


# ── Docker build log analysis ─────────────────────────────────────────────────

_FAILURE_PATTERNS = [
    ("wheel_unavailable",         r"no matching distribution|could not find a version that satisfies"),
    ("c_extension_build_failure", r"\bgcc\b|\bg\+\+\b|compilation failed|error: command .* failed|cc1\b|ld returned"),
    ("import_error",              r"ModuleNotFoundError|ImportError|cannot import name"),
    ("test_failure",              r"\bFAILED\b|AssertionError|test session starts|\bpytest\b"),
    ("install_error",             r"pip.*install.*failed|error.*install|Could not install"),
    ("timeout",                   r"\btimeout\b|timed out"),
]


def _categorize_failure(docker_log_path: Path):
    if not docker_log_path.exists():
        return "no_log", ""

    text       = docker_log_path.read_text(encoding="utf-8", errors="replace")
    last_lines = "\n".join(text.splitlines()[-30:])

    for category, pattern in _FAILURE_PATTERNS:
        if re.search(pattern, last_lines, re.IGNORECASE):
            for line in reversed(last_lines.splitlines()):
                if re.search(pattern, line, re.IGNORECASE):
                    return category, line.strip()[:200]

    for line in reversed(last_lines.splitlines()):
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return "unknown", stripped[:200]

    return "unknown", ""


# ── Trajectory analysis ───────────────────────────────────────────────────────

def _analyze_trajectory(traj_path: Path, model: str) -> dict:
    empty = {
        "traj_available":   False,
        "api_calls":        0,
        "submitted":        False,
        "exit_status":      None,
        "cache_hit_tokens": 0,
        "cache_miss_tokens": 0,
        "input_tokens":     0,
        "output_tokens":    0,
        "cost_usd":         None,
        "steps_used":       0,
        "step_limit_hit":   False,
    }
    if not traj_path.exists():
        return empty

    try:
        data = json.loads(traj_path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return empty

    messages = data.get("messages") or data.get("history") or []
    info     = data.get("info") or {}

    exit_status = (
        info.get("exit_status")
        or info.get("exit_reason")
        or data.get("exit_status")
    )
    submitted = bool(exit_status and "submitted" in str(exit_status).lower())

    api_calls = input_tokens = output_tokens = cache_hit = cache_miss = 0

    for msg in messages:
        if not isinstance(msg, dict):
            continue
        try:
            usage = msg["extra"]["response"]["usage"]
        except (KeyError, TypeError):
            continue
        if not isinstance(usage, dict):
            continue
        api_calls    += 1
        input_tokens  += usage.get("prompt_tokens", 0) or 0
        output_tokens += usage.get("completion_tokens", 0) or 0
        hit  = usage.get("prompt_cache_hit_tokens", 0) or 0
        miss = usage.get("prompt_cache_miss_tokens", 0) or 0
        if not hit and not miss:
            cached = (
                usage.get("cache_read_input_tokens", 0)
                or (usage.get("prompt_tokens_details") or {}).get("cached_tokens", 0)
                or 0
            )
            hit  = cached
            miss = max(0, (usage.get("prompt_tokens", 0) or 0) - cached)
        cache_hit  += hit
        cache_miss += miss

    canonical = model.replace("__", "/")
    pricing   = _MODEL_PRICING.get(canonical) or _MODEL_PRICING.get(model)
    cost = None
    if pricing and (input_tokens or output_tokens):
        if cache_hit or cache_miss:
            cost = (
                cache_hit  * pricing["cache_hit_per_m"]  / 1_000_000 +
                cache_miss * pricing["cache_miss_per_m"] / 1_000_000 +
                output_tokens * pricing["output_per_m"]  / 1_000_000
            )
        else:
            cost = (
                input_tokens  * pricing["cache_miss_per_m"] / 1_000_000 +
                output_tokens * pricing["output_per_m"]     / 1_000_000
            )

    steps_used = sum(
        1 for m in messages
        if isinstance(m, dict) and m.get("role") in ("assistant", "model")
    )

    return {
        "traj_available":    True,
        "api_calls":         api_calls,
        "submitted":         submitted,
        "exit_status":       str(exit_status) if exit_status else None,
        "cache_hit_tokens":  cache_hit,
        "cache_miss_tokens": cache_miss,
        "input_tokens":      input_tokens,
        "output_tokens":     output_tokens,
        "cost_usd":          cost,
        "steps_used":        steps_used,
        "step_limit_hit":    steps_used >= _STEP_LIMIT,
    }


# ── Per-run record builder ────────────────────────────────────────────────────

def _build_record(
    model_name: str,
    instance_id: str,
    instance_dir: Path,
    instance_meta: dict,
) -> dict:
    score    = _load_json(instance_dir / "score.json")
    metadata = _load_json(instance_dir / "run_metadata.json")
    diff     = _analyze_diff(instance_dir / "agent_patch.diff")
    traj     = _analyze_trajectory(instance_dir / "trajectory.json", model_name)

    resolved         = score.get("resolved", False)
    dockerfile_gen   = score.get("dockerfile_generated")

    if not resolved and dockerfile_gen is False:
        failure_cat, final_error = "no_dockerfile", "Agent did not generate Dockerfile.py313"
    elif not resolved:
        failure_cat, final_error = _categorize_failure(instance_dir / "docker_build.log")
    else:
        failure_cat, final_error = None, None

    # Prefer trajectory-derived token counts (per-message sums are more accurate)
    input_tokens  = traj["input_tokens"]  or metadata.get("input_tokens_total") or 0
    output_tokens = traj["output_tokens"] or metadata.get("output_tokens_total") or 0
    cost_usd      = traj["cost_usd"] if traj["cost_usd"] is not None else metadata.get("cost_usd")
    iterations    = traj["steps_used"] or metadata.get("iterations")

    inst = instance_meta.get(instance_id, {})

    return {
        # Identity
        "model":                model_name,
        "instance_id":          instance_id,
        "folder":               inst.get("folder", ""),
        "breaking_change_type": inst.get("breaking_change_type", ""),
        "complexity":           inst.get("complexity", ""),
        # Resolution
        "resolved":             resolved,
        "dockerfile_generated": dockerfile_gen,
        "docker_exit_code":     score.get("docker_exit_code"),
        # Patch stats
        "patch_lines_added":    score.get("patch_lines_added", 0),
        "patch_lines_removed":  score.get("patch_lines_removed", 0),
        "patch_files_changed":  score.get("patch_files_changed", []),
        # Execution
        "iterations":           iterations,
        "wall_time_seconds":    metadata.get("wall_time_seconds"),
        "input_tokens":         input_tokens,
        "output_tokens":        output_tokens,
        "cost_usd":             cost_usd,
        "timed_out":            metadata.get("timed_out", False),
        # Diff analysis
        "diff_available":       diff["diff_available"],
        "test_files_modified":  diff["test_files_modified"],
        "test_files":           diff["test_files"],
        "dep_only":             diff["dep_only"],
        "source_changed":       diff["source_changed"],
        "dockerfile_in_diff":   diff["dockerfile_in_diff"],
        "changed_files":        diff["changed_files"],
        # Failure
        "failure_category":     failure_cat,
        "final_error":          final_error,
        # Trajectory
        "api_calls":            traj["api_calls"],
        "submitted":            traj["submitted"],
        "exit_status":          traj["exit_status"],
        "cache_hit_tokens":     traj["cache_hit_tokens"],
        "cache_miss_tokens":    traj["cache_miss_tokens"],
        "step_limit_hit":       traj["step_limit_hit"],
        "steps_used":           traj["steps_used"],
    }


# ── Record collection ─────────────────────────────────────────────────────────

def collect_records(model_filter=None):
    instance_meta = _load_instances()
    records = []
    pending = 0

    if not RUNS_DIR.exists():
        return records, pending

    for model_dir in sorted(RUNS_DIR.iterdir()):
        if not model_dir.is_dir():
            continue
        model_name = model_dir.name
        if model_filter:
            canonical = model_name.replace("__", "/")
            if model_filter not in (model_name, canonical):
                continue

        for instance_dir in sorted(model_dir.iterdir()):
            if not instance_dir.is_dir() or "__50step" in instance_dir.name:
                continue
            instance_id = instance_dir.name

            if not (instance_dir / "score.json").exists():
                pending += 1
                continue

            records.append(
                _build_record(model_name, instance_id, instance_dir, instance_meta)
            )

    return records, pending


# ── Markdown helpers ──────────────────────────────────────────────────────────

def _pct(n, d):
    return f"{n/d*100:.1f}%" if d else "—"


def _avg(values):
    vals = [v for v in values if v is not None]
    return sum(vals) / len(vals) if vals else None


def _fmt(val, spec=".1f", prefix="", suffix=""):
    return f"{prefix}{val:{spec}}{suffix}" if val is not None else "—"


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


# ── Markdown report ───────────────────────────────────────────────────────────

def build_markdown(records, pending, all_records=None):
    L = []

    def h(text):
        L.extend(["", f"## {text}", ""])

    def rule():
        L.extend(["", "---"])

    L += [
        "# SWE-Adaptive Evaluation — Analysis Report",
        "",
        f"Generated: {_now()}",
    ]
    if pending:
        L.append(f"> ⚠ **{pending} instance(s) still pending** — excluded from analysis.")

    models = sorted({r["model"] for r in records})

    # ── Overall Summary ───────────────────────────────────────────────────────
    rule(); h("Overall Summary")
    L.append(
        "| Model | Resolved | Total | Rate | "
        "Avg Steps | Avg Tokens | Avg Cost | Avg Time (s) |"
    )
    L.append(
        "|-------|----------|-------|------|"
        "-----------|------------|----------|--------------|"
    )
    for model in models:
        recs  = [r for r in records if r["model"] == model]
        total = len(recs)
        res   = sum(1 for r in recs if r["resolved"])
        L.append(
            f"| `{model}` | {res} | {total} | {_pct(res, total)} | "
            f"{_fmt(_avg([r['iterations'] for r in recs]))} | "
            f"{_fmt(_avg([(r['input_tokens'] or 0)+(r['output_tokens'] or 0) for r in recs]), '.0f')} | "
            f"{_fmt(_avg([r['cost_usd'] for r in recs]), '.4f', '$')} | "
            f"{_fmt(_avg([r['wall_time_seconds'] for r in recs]), '.0f')} |"
        )

    # ── By Breaking Change Type ───────────────────────────────────────────────
    rule(); h("Resolution by Breaking Change Type")
    L.append("| Breaking Change Type | Resolved | Total | Rate |")
    L.append("|----------------------|----------|-------|------|")
    for t in sorted({r["breaking_change_type"] for r in records if r["breaking_change_type"]}):
        recs = [r for r in records if r["breaking_change_type"] == t]
        res  = sum(1 for r in recs if r["resolved"])
        L.append(f"| {t} | {res} | {len(recs)} | {_pct(res, len(recs))} |")

    # ── By Folder ─────────────────────────────────────────────────────────────
    rule(); h("Resolution by Folder")
    L.append("| Folder | Resolved | Total | Rate |")
    L.append("|--------|----------|-------|------|")
    for f in sorted({r["folder"] for r in records if r["folder"]}):
        recs = [r for r in records if r["folder"] == f]
        res  = sum(1 for r in recs if r["resolved"])
        L.append(f"| {f} | {res} | {len(recs)} | {_pct(res, len(recs))} |")

    # ── Failure Analysis ──────────────────────────────────────────────────────
    rule(); h("Failure Analysis (unresolved instances)")
    failed = [r for r in records if not r["resolved"]]

    if failed:
        L.append("| Model | Instance | Failure Category | Steps | Hit Limit | Final Error |")
        L.append("|-------|----------|-----------------|-------|-----------|-------------|")
        for r in sorted(failed, key=lambda x: (x["failure_category"] or "", x["model"], x["instance_id"])):
            err = (r["final_error"] or "")[:100].replace("|", "\\|")
            L.append(
                f"| {_short(r['model'])} | `{r['instance_id']}` | {r['failure_category'] or '—'} | "
                f"{r['steps_used'] or '?'} | {'✓' if r['step_limit_hit'] else ''} | {err} |"
            )

        L.append("")
        L.append("**Failure category counts:**")
        L.append("")
        L.append("| Category | Count |")
        L.append("|----------|-------|")
        for cat, cnt in Counter(r["failure_category"] for r in failed if r["failure_category"]).most_common():
            L.append(f"| {cat} | {cnt} |")
    else:
        L.append("All instances resolved.")

    # ── Test file modifications ───────────────────────────────────────────────
    rule(); h("Test File Modifications")
    test_recs = [r for r in records if r["test_files_modified"]]
    if test_recs:
        for r in sorted(test_recs, key=lambda x: (x["instance_id"], x["model"])):
            mark = "✅" if r["resolved"] else "❌"
            L.append(f"- {mark} {_short(r['model'])} / `{r['instance_id']}` — {', '.join(r['test_files'])}")
    else:
        L.append("No agents modified test files.")

    # ── Dependency-only fixes ─────────────────────────────────────────────────
    rule(); h("Dependency-only Fixes")
    L.append(
        "Instances resolved by changing only dependency/config files "
        "(no Python source changes required):"
    )
    L.append("")
    dep_resolved = [r for r in records if r["resolved"] and r["dep_only"]]
    if dep_resolved:
        for r in sorted(dep_resolved, key=lambda x: (x["instance_id"], x["model"])):
            files = ", ".join(r["changed_files"])
            L.append(f"- {_short(r['model'])} / `{r['instance_id']}` — {files}")
    else:
        L.append("None yet.")

    # ── Agent Behaviour Patterns ──────────────────────────────────────────────
    rule(); h("Agent Behaviour Patterns")
    total     = len(records)
    submitted = sum(1 for r in records if r["submitted"])
    lim_hit   = sum(1 for r in records if r["step_limit_hit"])
    timed_out = sum(1 for r in records if r["timed_out"])
    no_patch  = sum(1 for r in records if not r["diff_available"])
    no_df     = sum(1 for r in records if r["dockerfile_generated"] is False)

    avg_steps_res   = _avg([r["steps_used"] for r in records if r["resolved"]])
    avg_steps_unres = _avg([r["steps_used"] for r in records if not r["resolved"]])

    total_hit  = sum(r["cache_hit_tokens"]  for r in records)
    total_miss = sum(r["cache_miss_tokens"] for r in records)
    total_cache = total_hit + total_miss
    cache_pct  = f"{total_hit/total_cache*100:.1f}%" if total_cache else "—"

    L += [
        f"- **Agent signalled completion (vs. cut off by step/time limit)**: {submitted}/{total}",
        f"- **Hit step limit ({_STEP_LIMIT} steps)**: {lim_hit}/{total}",
        f"- **Timed out**: {timed_out}/{total}",
        f"- **Empty patch (no file changes)**: {no_patch}/{total}",
        f"- **No Dockerfile generated**: {no_df}/{total}",
        f"- **Avg steps — resolved**: {_fmt(avg_steps_res)}",
        f"- **Avg steps — unresolved**: {_fmt(avg_steps_unres)}",
        f"- **Cache hit rate** (all runs): {cache_pct}",
        f"  — hit: {total_hit:,} tokens / miss: {total_miss:,} tokens",
    ]

    # ── Gemini subset cross-model comparison ──────────────────────────────────
    ref = all_records if all_records is not None else records
    gemini_models = sorted({r["model"] for r in ref if "gemini" in r["model"].lower()})
    if gemini_models:
        gemini_instance_ids = sorted({
            r["instance_id"] for r in ref if r["model"] in gemini_models
        })
        if gemini_instance_ids:
            all_models_ref = sorted({r["model"] for r in ref})
            lookup = {(r["model"], r["instance_id"]): r for r in ref}

            rule(); h(f"Gemini Subset — Cross-Model Comparison ({len(gemini_instance_ids)} instances)")
            L.append(
                f"Resolution rate of each model restricted to the "
                f"{len(gemini_instance_ids)} instance(s) evaluated by Gemini:"
            )
            L.append("")

            short = {m: m.replace("__", "/", 1).split("/")[-1] for m in all_models_ref}
            header = "| Instance | Type |" + "".join(f" {short[m]} |" for m in all_models_ref)
            sep    = "|----------|------|" + "".join("---|" for _ in all_models_ref)
            L += [header, sep]

            for iid in gemini_instance_ids:
                inst_recs = [r for r in ref if r["instance_id"] == iid]
                bct = inst_recs[0].get("breaking_change_type") or "—" if inst_recs else "—"
                row = f"| `{iid}` | {bct} |"
                for m in all_models_ref:
                    rec = lookup.get((m, iid))
                    if rec is None:
                        row += " — |"
                    elif rec["resolved"]:
                        row += " ✅ |"
                    else:
                        row += " ❌ |"
                L.append(row)

            L.append("")
            rate_row = "| **Resolution rate** | |"
            for m in all_models_ref:
                m_recs = [lookup.get((m, iid)) for iid in gemini_instance_ids]
                m_recs = [r for r in m_recs if r is not None]
                res = sum(1 for r in m_recs if r["resolved"])
                total = len(m_recs)
                rate_row += f" {res}/{total} ({_pct(res, total)}) |" if total else " — |"
            L.append(rate_row)

    # ── Per-instance detail ───────────────────────────────────────────────────
    rule(); h("Per-instance Detail")
    L.append(
        "| Model | Instance | Type | Resolved | Steps | Limit | "
        "Tokens | Cost | Time (s) | Dockerfile | Dep Only | Tests |"
    )
    L.append(
        "|-------|----------|------|----------|-------|-------|"
        "--------|------|---------|------------|----------|-------|"
    )
    for r in sorted(records, key=lambda x: (x["model"], x["instance_id"])):
        tokens = (r["input_tokens"] or 0) + (r["output_tokens"] or 0)
        L.append(
            f"| {_short(r['model'])} | `{r['instance_id']}` | {r['breaking_change_type'] or '—'} | "
            f"{'✅' if r['resolved'] else '❌'} | {r['steps_used'] or '?'} | "
            f"{'✓' if r['step_limit_hit'] else ''} | "
            f"{tokens:,} | {_fmt(r['cost_usd'], '.4f', '$')} | "
            f"{_fmt(r['wall_time_seconds'], '.0f')} | "
            f"{'✓' if r['dockerfile_generated'] else '✗' if r['dockerfile_generated'] is False else '?'} | "
            f"{'✓' if r['dep_only'] else ''} | "
            f"{'✓' if r['test_files_modified'] else ''} |"
        )

    L += ["", "---", "", "> ✅ resolved  ❌ not resolved  ✓ yes  ✗ no  — n/a"]

    return "\n".join(L) + "\n"


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Analyse SWE-Adaptive evaluation runs")
    parser.add_argument("--model", default=None,
                        help="Filter by model, e.g. deepseek/deepseek-v4-flash")
    args = parser.parse_args()

    print("Collecting records...")
    records, pending = collect_records(model_filter=args.model)
    all_records, _   = collect_records()  # unfiltered, for cross-model sections

    if not records:
        print("No completed runs found.")
        if pending:
            print(f"{pending} instance(s) still pending.")
        sys.exit(0)

    print(f"  {len(records)} completed  |  {pending} pending")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    json_path = RESULTS_DIR / "analysis.json"
    json_path.write_text(
        json.dumps(records, indent=2, default=str), encoding="utf-8"
    )

    md_path = RESULTS_DIR / "analysis.md"
    md_path.write_text(build_markdown(records, pending, all_records=all_records), encoding="utf-8")

    # ── Stdout summary ────────────────────────────────────────────────────────
    total    = len(records)
    resolved = sum(1 for r in records if r["resolved"])
    models   = sorted({r["model"] for r in records})

    print()
    print("=" * 60)
    print("SWE-Adaptive Run Analysis")
    print("=" * 60)
    print(f"  Completed : {total}  |  Pending : {pending}")
    print(f"  Resolved  : {resolved}/{total} ({_pct(resolved, total)})")
    print()

    for model in models:
        recs    = [r for r in records if r["model"] == model]
        res     = sum(1 for r in recs if r["resolved"])
        no_df   = sum(1 for r in recs if r["dockerfile_generated"] is False)
        lim     = sum(1 for r in recs if r["step_limit_hit"])
        t_out   = sum(1 for r in recs if r["timed_out"])
        cost    = sum(r["cost_usd"] or 0 for r in recs)
        tokens  = sum((r["input_tokens"] or 0) + (r["output_tokens"] or 0) for r in recs)
        print(f"  {model}")
        print(f"    Resolved:        {res}/{len(recs)} ({_pct(res, len(recs))})")
        print(f"    No Dockerfile:   {no_df}")
        print(f"    Hit step limit:  {lim}")
        print(f"    Timed out:       {t_out}")
        print(f"    Total tokens:    {tokens:,}")
        print(f"    Total cost:      ${cost:.4f}")
        print()

    failed = [r for r in records if not r["resolved"]]
    if failed:
        print("  Failure breakdown:")
        for cat, cnt in Counter(
            r["failure_category"] for r in failed if r["failure_category"]
        ).most_common():
            print(f"    {cat}: {cnt}")
        print()

    print(f"  analysis.json → {json_path}")
    print(f"  analysis.md   → {md_path}")


if __name__ == "__main__":
    main()
