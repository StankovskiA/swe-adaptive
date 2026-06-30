#!/usr/bin/env python3
"""
parse_trajectories.py
=====================
Reads all run_metadata.json and score.json files under runs/ and produces:
  results/summary.csv     — one row per (model, instance)
  results/summary.md      — human-readable results table
  results/failed_instances.json — instances where scoring infrastructure failed
"""
from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

# ── Config ────────────────────────────────────────────────────────────────────

SCRIPT_DIR     = Path(__file__).parent.resolve()
EVAL_BASE      = SCRIPT_DIR
INSTANCES_JSON = EVAL_BASE / "instances" / "instances.json"
RUNS_DIR       = EVAL_BASE / "runs"
RESULTS_DIR    = EVAL_BASE / "results"

# ── Per-model pricing (USD per 1M tokens) ────────────────────────────────────

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


def _parse_trajectory_tokens(traj_path: Path, model: str) -> dict:
    """
    Sum token usage from messages[i]['extra']['response']['usage'].
    Used to retroactively fix run_metadata.json records with missing token data.
    Returns {} on any failure.
    """
    if not traj_path.exists():
        return {}
    try:
        data = json.loads(traj_path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}

    messages = data.get("messages") or data.get("history") or []

    input_tokens      = 0
    output_tokens     = 0
    cache_hit_tokens  = 0
    cache_miss_tokens = 0

    for msg in messages:
        if not isinstance(msg, dict):
            continue
        try:
            usage = msg["extra"]["response"]["usage"]
        except (KeyError, TypeError):
            continue
        if not isinstance(usage, dict):
            continue
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
        cache_hit_tokens  += hit
        cache_miss_tokens += miss

    # Resolve sanitized dir name (deepseek__deepseek-v4-flash) to canonical
    canonical = model.replace("__", "/")
    pricing = _MODEL_PRICING.get(canonical) or _MODEL_PRICING.get(model)
    cost = None
    if pricing and (input_tokens or output_tokens):
        if cache_hit_tokens or cache_miss_tokens:
            cost = (
                cache_hit_tokens  * pricing["cache_hit_per_m"]  / 1_000_000 +
                cache_miss_tokens * pricing["cache_miss_per_m"] / 1_000_000 +
                output_tokens     * pricing["output_per_m"]     / 1_000_000
            )
        else:
            cost = (
                input_tokens  * pricing["cache_miss_per_m"] / 1_000_000 +
                output_tokens * pricing["output_per_m"]     / 1_000_000
            )

    iterations = sum(
        1 for m in messages
        if isinstance(m, dict) and m.get("role") in ("assistant", "model")
    )
    return {
        "iterations":   iterations or None,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd":     cost,
    }

CSV_FIELDS = [
    "model", "instance_id", "folder", "breaking_change_type", "complexity",
    "resolved", "scoring_error", "timed_out",
    "iterations", "input_tokens", "output_tokens", "cost_usd",
    "wall_time_seconds", "patch_empty", "patch_lines_added", "patch_lines_removed",
    "patch_files_changed", "error",
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _load_instance_metadata() -> dict:
    """Returns dict: instance_id → {folder, breaking_change_type, complexity}"""
    if not INSTANCES_JSON.exists():
        return {}
    data = json.loads(INSTANCES_JSON.read_text())
    return {
        i["instance_id"]: {
            "folder":               i.get("folder", ""),
            "breaking_change_type": i.get("breaking_change_type", ""),
            "complexity":           i.get("complexity", ""),
        }
        for i in data.get("instances", [])
    }


def _collect_runs() -> list[dict]:
    """Walk runs/ and collect one record per (model, instance) run."""
    instance_meta = _load_instance_metadata()
    records = []

    if not RUNS_DIR.exists():
        return records

    for model_dir in sorted(RUNS_DIR.iterdir()):
        if not model_dir.is_dir():
            continue
        model_name = model_dir.name  # sanitized, e.g. gemini__gemini-2-0-flash

        for instance_dir in sorted(model_dir.iterdir()):
            if not instance_dir.is_dir() or "__50step" in instance_dir.name:
                continue

            instance_id = instance_dir.name
            meta_path  = instance_dir / "run_metadata.json"
            score_path = instance_dir / "score.json"

            rec = {
                "model":              model_name,
                "instance_id":        instance_id,
                "folder":             "",
                "breaking_change_type": "",
                "complexity":         "",
                "resolved":           False,
                "scoring_error":      False,
                "timed_out":          False,
                "iterations":         None,
                "input_tokens":       None,
                "output_tokens":      None,
                "cost_usd":           None,
                "wall_time_seconds":  None,
                "patch_empty":        None,
                "patch_lines_added":  None,
                "patch_lines_removed": None,
                "patch_files_changed": "",
                "error":              None,
            }

            # Merge instance metadata
            if instance_id in instance_meta:
                rec.update(instance_meta[instance_id])

            # Merge run_metadata.json
            if meta_path.exists():
                try:
                    meta = json.loads(meta_path.read_text())
                    rec["timed_out"]         = meta.get("timed_out", False)
                    rec["iterations"]        = meta.get("iterations")
                    rec["input_tokens"]      = meta.get("input_tokens_total")
                    rec["output_tokens"]     = meta.get("output_tokens_total")
                    rec["cost_usd"]          = meta.get("cost_usd")
                    rec["wall_time_seconds"] = meta.get("wall_time_seconds")
                    if meta.get("error") and not rec["error"]:
                        rec["error"] = str(meta["error"])[:300]
                except Exception as exc:
                    rec["error"] = f"run_metadata parse error: {exc}"

            # Re-parse trajectory.json for accurate per-message token counts.
            # This supersedes run_metadata values when the metadata was written
            # by an older version of the parser that returned zeros.
            traj_path = instance_dir / "trajectory.json"
            traj = _parse_trajectory_tokens(traj_path, model_name)
            if traj.get("input_tokens") or traj.get("output_tokens"):
                rec["input_tokens"]  = traj["input_tokens"]
                rec["output_tokens"] = traj["output_tokens"]
                if traj.get("cost_usd") is not None:
                    rec["cost_usd"] = traj["cost_usd"]
                if traj.get("iterations") is not None and rec["iterations"] is None:
                    rec["iterations"] = traj["iterations"]

            # Merge score.json
            if score_path.exists():
                try:
                    score = json.loads(score_path.read_text())
                    rec["resolved"]           = score.get("resolved", False)
                    rec["scoring_error"]      = score.get("scoring_error", False)
                    rec["patch_empty"]        = score.get("patch_empty")
                    rec["patch_lines_added"]  = score.get("patch_lines_added")
                    rec["patch_lines_removed"] = score.get("patch_lines_removed")
                    files = score.get("patch_files_changed", [])
                    rec["patch_files_changed"] = "; ".join(files) if isinstance(files, list) else str(files)
                    if score.get("error") and not rec["error"]:
                        rec["error"] = str(score["error"])[:300]
                except Exception as exc:
                    rec["error"] = f"score.json parse error: {exc}"
            else:
                rec["error"] = (rec.get("error") or "") + " score.json missing"

            records.append(rec)

    return records


def _write_csv(records: list[dict], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)
    print(f"Wrote {path} ({len(records)} rows)")


def _write_summary_md(records: list[dict], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)

    # Group by model
    models = sorted({r["model"] for r in records})
    instance_ids = sorted({r["instance_id"] for r in records})

    # Build lookup: (model, instance_id) → record
    lookup = {(r["model"], r["instance_id"]): r for r in records}

    lines = [
        "# SWE-Adaptive Evaluation Results",
        "",
        f"Generated: {_now()}",
        "",
        "---",
        "",
        "## Overall resolution rate",
        "",
        "| Model | Resolved | Total | Rate | Scoring Errors | Timeouts |",
        "|-------|----------|-------|------|----------------|----------|",
    ]

    for model in models:
        model_recs = [r for r in records if r["model"] == model]
        total    = len(model_recs)
        resolved = sum(1 for r in model_recs if r["resolved"])
        s_errors = sum(1 for r in model_recs if r["scoring_error"])
        timeouts = sum(1 for r in model_recs if r["timed_out"])
        rate = f"{resolved/total*100:.1f}%" if total else "—"
        lines.append(f"| `{model}` | {resolved} | {total} | {rate} | {s_errors} | {timeouts} |")

    # By breaking change type
    change_types = sorted({r["breaking_change_type"] for r in records if r["breaking_change_type"]})
    if change_types:
        lines += [
            "",
            "---",
            "",
            "## By breaking change type",
            "",
        ]
        header = "| Type | " + " | ".join(f"`{m}`" for m in models) + " |"
        sep    = "|------|" + "|".join("---" for _ in models) + "|"
        lines += [header, sep]
        for ct in change_types:
            row = f"| {ct} |"
            for model in models:
                ct_recs = [r for r in records if r["model"] == model and r["breaking_change_type"] == ct]
                if not ct_recs:
                    row += " — |"
                else:
                    res = sum(1 for r in ct_recs if r["resolved"])
                    row += f" {res}/{len(ct_recs)} |"
            lines.append(row)

    # By complexity
    complexities = sorted({r["complexity"] for r in records if r["complexity"]})
    if complexities:
        lines += [
            "",
            "---",
            "",
            "## By complexity",
            "",
        ]
        header = "| Complexity | " + " | ".join(f"`{m}`" for m in models) + " |"
        sep    = "|------------|" + "|".join("---" for _ in models) + "|"
        lines += [header, sep]
        for c in complexities:
            row = f"| {c} |"
            for model in models:
                c_recs = [r for r in records if r["model"] == model and r["complexity"] == c]
                if not c_recs:
                    row += " — |"
                else:
                    res = sum(1 for r in c_recs if r["resolved"])
                    row += f" {res}/{len(c_recs)} |"
            lines.append(row)

    # Per-instance results
    lines += [
        "",
        "---",
        "",
        "## Per-instance results",
        "",
    ]
    header = "| Instance | Type |" + "".join(f" {m} |" for m in models)
    sep    = "|----------|------|" + "".join("------|" for _ in models)
    lines += [header, sep]

    for iid in instance_ids:
        # Get metadata from any record
        recs = [r for r in records if r["instance_id"] == iid]
        ct     = recs[0]["breaking_change_type"] if recs else ""
        row = f"| `{iid}` | {ct} |"
        for model in models:
            r = lookup.get((model, iid))
            if r is None:
                row += " — |"
            elif r.get("scoring_error"):
                row += " ⚠ |"
            elif r.get("timed_out"):
                row += " ⏱ |"
            elif r["resolved"]:
                row += " ✅ |"
            else:
                empty = " (empty patch)" if r.get("patch_empty") else ""
                row += f" ❌{empty} |"
        lines.append(row)

    lines += [
        "",
        "---",
        "",
        "## Token and cost summary",
        "",
        "| Model | Total input tokens | Total output tokens | Total cost (USD) | Avg time (s) |",
        "|-------|--------------------|---------------------|------------------|--------------|",
    ]
    for model in models:
        model_recs = [r for r in records if r["model"] == model]
        in_tok  = sum(r["input_tokens"]  or 0 for r in model_recs)
        out_tok = sum(r["output_tokens"] or 0 for r in model_recs)
        cost    = sum(r["cost_usd"]      or 0 for r in model_recs)
        times   = [r["wall_time_seconds"] for r in model_recs if r["wall_time_seconds"]]
        avg_t   = f"{sum(times)/len(times):.0f}" if times else "—"
        lines.append(
            f"| `{model}` | {in_tok:,} | {out_tok:,} | ${cost:.4f} | {avg_t} |"
        )

    # Mean cost on the 13 instances run by all models
    all_model_instance_sets = [
        {r["instance_id"] for r in records if r["model"] == m} for m in models
    ]
    common_instances = set.intersection(*all_model_instance_sets) if all_model_instance_sets else set()
    if len(models) > 1 and common_instances:
        lines += [
            "",
            "---",
            "",
            f"## Mean cost on shared instances (n={len(common_instances)})",
            "",
            "| Model | Mean cost/instance (USD) | Mean input tokens | Mean output tokens |",
            "|-------|--------------------------|-------------------|--------------------|",
        ]
        for model in models:
            common_recs = [r for r in records if r["model"] == model and r["instance_id"] in common_instances]
            n = len(common_recs)
            if n == 0:
                lines.append(f"| `{model}` | — | — | — |")
                continue
            mean_cost   = sum(r["cost_usd"]     or 0 for r in common_recs) / n
            mean_in     = sum(r["input_tokens"]  or 0 for r in common_recs) / n
            mean_out    = sum(r["output_tokens"] or 0 for r in common_recs) / n
            lines.append(
                f"| `{model}` | ${mean_cost:.4f} | {mean_in:,.0f} | {mean_out:,.0f} |"
            )

    lines += [
        "",
        "---",
        "",
        "> ✅ resolved  ❌ not resolved  ⚠ scoring error  ⏱ timed out  — not run",
    ]

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {path}")


def _write_failed_instances(records: list[dict], path: Path):
    failed = [
        r for r in records
        if r["scoring_error"] or (not r["resolved"] and r.get("error"))
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(failed, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {path} ({len(failed)} entries)")


def main():
    print("Collecting run data...")
    records = _collect_runs()

    if not records:
        print("No run data found. Run run_eval.py first.")
        sys.exit(0)

    print(f"Found {len(records)} (model, instance) records across "
          f"{len({r['model'] for r in records})} model(s)")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    _write_csv(records,             RESULTS_DIR / "summary.csv")
    _write_summary_md(records,      RESULTS_DIR / "summary.md")
    _write_failed_instances(records, RESULTS_DIR / "failed_instances.json")

    print(f"\nResults written to {RESULTS_DIR}/")


if __name__ == "__main__":
    main()
