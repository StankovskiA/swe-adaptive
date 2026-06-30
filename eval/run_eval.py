#!/usr/bin/env python3
"""
run_eval.py
===========
Main evaluation script for SWE-Adaptive.

Usage
-----
  python run_eval.py --model gemini/gemini-2.0-flash --all
  python run_eval.py --model gemini/gemini-2.0-flash --instance encode_databases
  python run_eval.py --model gemini/gemini-2.0-flash --folder validated_success_benchmark
  python run_eval.py --model gemini/gemini-2.0-flash --all --resume
  python run_eval.py --model gemini/gemini-2.0-flash --all --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shlex
import shutil
import socket
import subprocess
import sys
import threading
import traceback
from datetime import datetime, timezone
from pathlib import Path

import yaml

from score_instance import score_instance

# ── Config ────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent.resolve()
CONFIG_PATH = SCRIPT_DIR / "config.yaml"

with open(CONFIG_PATH) as _f:
    CONFIG = yaml.safe_load(_f)

EVAL_BASE = Path(CONFIG["eval_base"])
BENCHMARK_BASE = Path(CONFIG["benchmark_base"])
INSTANCES_JSON = EVAL_BASE / "instances" / "instances.json"
PROMPT_TEMPLATE = EVAL_BASE / "prompts" / "task_prompt.txt"
RUNS_DIR = EVAL_BASE / "runs"
TMP_DIR = Path(CONFIG.get("tmp_dir", "/tmp"))
AGENT_CMD = CONFIG.get("agent_command", "mini")
MINI_CUSTOM_CONFIG = EVAL_BASE / "mini_config.yaml"
TIMEOUT_SECONDS = int(CONFIG.get("agent_timeout_seconds", 2700))
API_KEYS_TO_CHECK = CONFIG.get("api_keys_to_check", [])

# ── Load .env and map project-specific key names ──────────────────────────────


def _load_dotenv(dotenv_path: Path) -> None:
    """Parse a .env file and set missing env vars. Values are never logged."""
    if not dotenv_path.exists():
        return
    for raw_line in dotenv_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_dotenv(BENCHMARK_BASE / ".env")

# Map project-specific key names to standard LiteLLM names if the standard
# names are not already set. Values are read from os.environ — never logged.
_GEMINI_KEY_ALIASES = ["SWE_ADAPTIVE_GEMINI_API_KEY"]
if not os.environ.get("GEMINI_API_KEY"):
    for _alias in _GEMINI_KEY_ALIASES:
        if os.environ.get(_alias):
            os.environ["GEMINI_API_KEY"] = os.environ[_alias]
            break


# ── Utilities ─────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _model_dir_name(model: str) -> str:
    """Sanitize model string for use as a directory name."""
    return model.replace("/", "__").replace(":", "_").replace(" ", "_")


def _ts_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load_instances() -> list[dict]:
    if not INSTANCES_JSON.exists():
        print(f"ERROR: instances.json not found at {INSTANCES_JSON}")
        print("Run: python build_instance_index.py")
        sys.exit(1)
    data = json.loads(INSTANCES_JSON.read_text())
    return data["instances"]


def _load_prompt_template() -> str:
    return PROMPT_TEMPLATE.read_text(encoding="utf-8")


def _write_json(path: Path, data: dict, log):
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    log(f"  wrote {path}")


# ── Environment snapshot ──────────────────────────────────────────────────────

def _capture_env_snapshot(model: str, instance_id: str, working_copy: Path) -> dict:
    def _run(cmd):
        try:
            return subprocess.check_output(
                cmd, shell=True, stderr=subprocess.DEVNULL, text=True
            ).strip()
        except Exception:
            return ""

    pyenv_versions = []
    try:
        raw = subprocess.check_output(
            ["pyenv", "versions", "--bare"], stderr=subprocess.DEVNULL, text=True
        )
        pyenv_versions = [v.strip() for v in raw.splitlines() if v.strip()]
    except Exception:
        pass

    git_commit = ""
    try:
        git_commit = subprocess.check_output(
            ["git", "-C", str(working_copy), "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL, text=True,
        ).strip()
    except Exception:
        pass

    keys_present = [k for k in API_KEYS_TO_CHECK if os.environ.get(k)]

    return {
        "timestamp_start":      _now(),
        "hostname":             socket.gethostname(),
        "platform":             platform.platform(),
        "python_version":       sys.version,
        "mini_swe_agent_version": _run(f"{AGENT_CMD} --version"),
        "model":                model,
        "instance_id":          instance_id,
        "git_commit_repo":      git_commit,
        "docker_version":       _run("docker version --format '{{.Server.Version}}'"),
        "pyenv_versions":       pyenv_versions,
        "env_vars_present":     keys_present,
        "agent_command":        AGENT_CMD,
        "timeout_seconds":      TIMEOUT_SECONDS,
    }


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


# ── Trajectory parsing ────────────────────────────────────────────────────────

def _parse_trajectory(traj_path: Path, model: str = "") -> dict:
    """
    Parse mini-swe-agent trajectory JSON.
    Sums token usage from messages[i]['extra']['response']['usage'] fields.
    Never raises — errors go into the 'parse_error' key.
    """
    if not traj_path.exists():
        return {"parse_error": f"trajectory.json not found at {traj_path}"}

    raw = traj_path.read_text(encoding="utf-8", errors="replace")
    if not raw.strip():
        return {"parse_error": "trajectory.json is empty"}

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return {
            "parse_error": f"JSON decode error: {exc}",
            "raw_content_preview": raw[:500],
        }

    messages = data.get("messages") or data.get("history") or []

    input_tokens = 0
    output_tokens = 0
    cache_hit_tokens = 0
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

        input_tokens += usage.get("prompt_tokens", 0) or 0
        output_tokens += usage.get("completion_tokens", 0) or 0

        # DeepSeek: direct hit/miss split
        hit = usage.get("prompt_cache_hit_tokens", 0) or 0
        miss = usage.get("prompt_cache_miss_tokens", 0) or 0
        # Gemini: cache_read_input_tokens (or prompt_tokens_details.cached_tokens)
        if not hit and not miss:
            cached = (
                usage.get("cache_read_input_tokens", 0)
                or (usage.get("prompt_tokens_details") or {}).get("cached_tokens", 0)
                or 0
            )
            hit = cached
            miss = max(0, (usage.get("prompt_tokens", 0) or 0) - cached)
        cache_hit_tokens += hit
        cache_miss_tokens += miss

    # Cost: use model-specific cache-aware pricing when available
    pricing = _MODEL_PRICING.get(model)
    cost = None
    if pricing and (input_tokens or output_tokens):
        if cache_hit_tokens or cache_miss_tokens:
            cost = (
                cache_hit_tokens * pricing["cache_hit_per_m"] / 1_000_000 +
                cache_miss_tokens * pricing["cache_miss_per_m"] / 1_000_000 +
                output_tokens * pricing["output_per_m"] / 1_000_000
            )
        else:
            # No cache breakdown — treat all input as cache-miss
            cost = (
                input_tokens * pricing["cache_miss_per_m"] / 1_000_000 +
                output_tokens * pricing["output_per_m"] / 1_000_000
            )

    iterations = sum(
        1 for m in messages
        if isinstance(m, dict) and m.get("role") in ("assistant", "model")
    )

    return {
        "iterations":          iterations,
        "input_tokens_total":  input_tokens,
        "output_tokens_total": output_tokens,
        "cache_hit_tokens":    cache_hit_tokens,
        "cache_miss_tokens":   cache_miss_tokens,
        "cost_usd":            cost,
        "parse_error":         None,
    }


# ── Fatal agent error detection ───────────────────────────────────────────────

_FATAL_PATTERNS = [
    ("Insufficient Balance",        "API account has insufficient balance"),
    ("invalid_api_key",             "Invalid API key"),
    ("Incorrect API key",           "Invalid API key"),
    ("AuthenticationError",         "Authentication error"),
    ("No API key provided",         "No API key provided"),
    ("Connection refused",          "Connection refused"),
    ("Cannot connect to",           "Cannot connect to host"),
    ("Network is unreachable",      "Network unreachable"),
    ("Aborted.",                    "mini-swe-agent aborted (setup not complete?)"),
    ("Input is not a terminal",     "mini-swe-agent aborted (non-interactive setup)"),
]


def _detect_fatal_agent_error(stderr_text: str):
    """Return (is_fatal, short_summary) for unrecoverable agent failures."""
    for pattern, summary in _FATAL_PATTERNS:
        if pattern in stderr_text:
            return True, summary
    return False, ""


# ── Per-instance runner ───────────────────────────────────────────────────────

def run_instance(instance: dict, model: str, run_dir: Path, dry_run: bool = False):
    instance_id = instance["instance_id"]
    repo_path = Path(instance["repo_path"])

    # Logger for this instance
    log_lines = []

    def log(msg: str):
        line = f"[{_now()}] {msg}"
        print(line)
        log_lines.append(line)

    log(f"{'='*60}")
    log(f"INSTANCE : {instance_id}")
    log(f"MODEL    : {model}")
    log(f"RUN DIR  : {run_dir}")
    log(f"DRY RUN  : {dry_run}")

    run_dir.mkdir(parents=True, exist_ok=True)

    if dry_run:
        log("DRY RUN — skipping execution")
        prompt_text = _load_prompt_template().replace(
            "{py313_error_output}", instance.get(
                "py313_error_output", "(not extracted)")
        )
        (run_dir / "prompt_used.txt").write_text(prompt_text, encoding="utf-8")
        log(
            f"  wrote (dry-run) prompt_used.txt → {run_dir / 'prompt_used.txt'}")
        return

    # ── 1. Working copy ──────────────────────────────────────────────────────
    ts = _ts_compact()
    working_copy = TMP_DIR / f"swe_eval_{instance_id}_{ts}"
    log(f"  copying repo: {repo_path} → {working_copy}")
    shutil.copytree(str(repo_path), str(working_copy), symlinks=True)

    # Strip Dockerfiles so the agent never sees them
    for df_name in ["Dockerfile.test", "Dockerfile.py313"]:
        df = working_copy / df_name
        if df.exists():
            df.unlink()
            log(f"  removed {df_name} from working copy")

    # Delete any pre-existing virtual environments so the agent always starts clean
    for venv_name in [".venv", "venv"]:
        venv_dir = working_copy / venv_name
        if venv_dir.is_dir():
            shutil.rmtree(venv_dir, ignore_errors=True)
            log(f"  removed pre-existing {venv_name}/ from working copy")

    # ── 2. Environment snapshot ──────────────────────────────────────────────
    env_snap = _capture_env_snapshot(model, instance_id, working_copy)
    env_snap_path = run_dir / "env_snapshot.json"
    _write_json(env_snap_path, env_snap, log)

    ts_start = datetime.now(timezone.utc)
    metadata: dict = {
        "instance_id":    instance_id,
        "model":          model,
        "timestamp_start": _now(),
        "timed_out":      False,
        "agent_exit_code": None,
        "error":          None,
    }

    try:
        # ── 3. Prompt ────────────────────────────────────────────────────────
        template = _load_prompt_template()
        prompt_text = template.replace(
            "{py313_error_output}",
            instance.get("py313_error_output",
                         "(py313_error_output not extracted)"),
        )
        prompt_path = run_dir / "prompt_used.txt"
        prompt_path.write_text(prompt_text, encoding="utf-8")
        log(f"  wrote prompt_used.txt ({len(prompt_text)} chars) → {prompt_path}")

        # ── 4. Run mini-swe-agent ────────────────────────────────────────────
        traj_path = run_dir / "trajectory.json"
        stdout_path = run_dir / "stdout.log"
        stderr_path = run_dir / "stderr.log"
        combined_path = run_dir / "combined.log"

        agent_cmd = [
            AGENT_CMD,
            "-c", "mini.yaml",
            "-c", str(MINI_CUSTOM_CONFIG),
            "--model", model,
            "--yolo",
            "--exit-immediately",
            "--output", str(traj_path),
            "--task", prompt_text,
        ]

        env = os.environ.copy()
        env["MSWEA_COST_TRACKING"] = "ignore_errors"

        log(f"  agent command: {shlex.join(agent_cmd)}")
        metadata["agent_command"] = shlex.join(agent_cmd)

        combined_lock = threading.Lock()

        def _stream(pipe, dest_fh, label):
            """Read pipe line-by-line, write to dest_fh and combined.log live."""
            for line in pipe:
                dest_fh.write(line)
                dest_fh.flush()
                with combined_lock:
                    fcomb.write(line)
                    fcomb.flush()

        with open(stdout_path, "w", encoding="utf-8") as fout, \
                open(stderr_path, "w", encoding="utf-8") as ferr, \
                open(combined_path, "w", encoding="utf-8") as fcomb:

            proc = subprocess.Popen(
                agent_cmd,
                cwd=str(working_copy),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
            )

            t_out = threading.Thread(target=_stream, args=(
                proc.stdout, fout, "OUT"), daemon=True)
            t_err = threading.Thread(target=_stream, args=(
                proc.stderr, ferr, "ERR"), daemon=True)
            t_out.start()
            t_err.start()

            try:
                proc.wait(timeout=TIMEOUT_SECONDS)
                agent_exit_code = proc.returncode
            except subprocess.TimeoutExpired:
                proc.kill()
                agent_exit_code = -1
                metadata["timed_out"] = True
                log(f"  TIMEOUT after {TIMEOUT_SECONDS}s — killed agent")

            t_out.join()
            t_err.join()

        metadata["agent_exit_code"] = agent_exit_code
        log(f"  agent exit code: {agent_exit_code}")
        log(f"  stdout → {stdout_path}")
        log(f"  stderr → {stderr_path}")
        log(f"  combined → {combined_path}")

        # ── Fail-fast: detect unrecoverable agent errors ─────────────────────
        skip_scoring = False
        if agent_exit_code != 0 and not metadata.get("timed_out"):
            stderr_text = stderr_path.read_text(
                encoding="utf-8", errors="replace") if stderr_path.exists() else ""
            is_fatal, summary = _detect_fatal_agent_error(stderr_text)
            if is_fatal:
                log(
                    f"  FATAL AGENT ERROR: {summary} — skipping scoring, moving to next instance")
                metadata["error"] = f"Fatal agent error: {summary}"
                skip_scoring = True
                # Write a minimal score.json so parse_trajectories.py doesn't flag it as missing
                _write_json(run_dir / "score.json", {
                    "instance_id":          instance_id,
                    "model":                model,
                    "resolved":             False,
                    "scoring_error":        False,
                    "skipped":              True,
                    "skip_reason":          summary,
                    "dockerfile_generated": False,
                    "agent_dockerfile_path": None,
                    "docker_exit_code":     None,
                    "patch_empty":          True,
                    "patch_lines_added":    0,
                    "patch_lines_removed":  0,
                    "patch_files_changed":  [],
                    "error":                summary,
                    "scored_at":            _now(),
                }, log)

        if not skip_scoring:
            # ── 4.5. Check for agent-generated Dockerfile.py313 ─────────────
            agent_dockerfile = working_copy / "Dockerfile.py313"
            dockerfile_generated = agent_dockerfile.is_file()
            agent_dockerfile_dst = run_dir / "Dockerfile.py313_agent"

            if dockerfile_generated:
                shutil.copy2(str(agent_dockerfile), str(agent_dockerfile_dst))
                log(
                    f"  agent generated Dockerfile.py313 → {agent_dockerfile_dst}")
            else:
                log("  WARNING: agent did NOT generate Dockerfile.py313 — skipping docker build")

            # ── 5. Capture patch ─────────────────────────────────────────────
            diff_path = run_dir / "agent_patch.diff"
            diff_stat_path = run_dir / "agent_patch_stat.txt"
            diff_text = ""

            try:
                # Stage Dockerfile.py313 if the agent created it so that
                # git diff HEAD captures it as a new file in the diff.
                if dockerfile_generated:
                    subprocess.run(
                        ["git", "add", "Dockerfile.py313"],
                        cwd=str(working_copy),
                        stderr=subprocess.DEVNULL,
                        check=False,
                    )

                diff_text = subprocess.check_output(
                    ["git", "diff", "HEAD"],
                    cwd=str(working_copy),
                    stderr=subprocess.DEVNULL,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
                diff_path.write_text(diff_text, encoding="utf-8")
                log(f"  agent_patch.diff: {len(diff_text)} chars → {diff_path}")
                if not diff_text.strip():
                    log("  WARNING: agent patch is EMPTY — agent made no file changes")

                diff_stat = subprocess.check_output(
                    ["git", "diff", "HEAD", "--stat"],
                    cwd=str(working_copy),
                    stderr=subprocess.DEVNULL,
                    text=True,
                    encoding="utf-8",
                )
                diff_stat_path.write_text(diff_stat, encoding="utf-8")
                log(f"  agent_patch_stat.txt → {diff_stat_path}")
            except Exception as exc:
                log(f"  WARNING: could not capture git diff: {exc}")
                diff_path.write_text("", encoding="utf-8")

            # ── 6. Score ─────────────────────────────────────────────────────
            if dockerfile_generated:
                score = score_instance(
                    instance_id=instance_id,
                    model=model,
                    working_copy=working_copy,
                    run_dir=run_dir,
                    log=log,
                    agent_dockerfile_path=agent_dockerfile_dst,
                )
            else:
                _write_json(run_dir / "score.json", {
                    "instance_id":           instance_id,
                    "model":                 model,
                    "resolved":              False,
                    "scoring_error":         False,
                    "dockerfile_generated":  False,
                    "agent_dockerfile_path": None,
                    "docker_exit_code":      None,
                    "docker_build_log_path": None,
                    "patch_empty":           len(diff_text.strip()) == 0,
                    "patch_lines_added":     0,
                    "patch_lines_removed":   0,
                    "patch_files_changed":   [],
                    "error":                 "Agent did not generate Dockerfile.py313",
                    "scored_at":             _now(),
                }, log)
                score = {"resolved": False, "patch_empty": len(
                    diff_text.strip()) == 0}

            # ── 7. Trajectory metrics ─────────────────────────────────────────
            traj_metrics = _parse_trajectory(traj_path, model)

        ts_end = datetime.now(timezone.utc)
        if skip_scoring:
            traj_metrics = {}
            score = {}
        metadata.update({
            "timestamp_end":        ts_end.isoformat(),
            "wall_time_seconds":    int((ts_end - ts_start).total_seconds()),
            "iterations":           traj_metrics.get("iterations"),
            "input_tokens_total":   traj_metrics.get("input_tokens_total"),
            "output_tokens_total":  traj_metrics.get("output_tokens_total"),
            "cost_usd":             traj_metrics.get("cost_usd"),
            "resolved":             score.get("resolved", False),
            "patch_empty":          score.get("patch_empty", True),
            "trajectory_parse_error": traj_metrics.get("parse_error"),
        })

    except Exception as exc:
        tb = traceback.format_exc()
        log(f"  EXCEPTION: {exc}")
        log(tb)
        metadata["error"] = tb
        ts_end = datetime.now(timezone.utc)
        metadata["timestamp_end"] = ts_end.isoformat()
        metadata["wall_time_seconds"] = int(
            (ts_end - ts_start).total_seconds())

    # ── 8. Write run_metadata.json ────────────────────────────────────────────
    _write_json(run_dir / "run_metadata.json", metadata, log)

    # ── 9. Progress log ───────────────────────────────────────────────────────
    progress_path = RUNS_DIR / _model_dir_name(model) / "progress.log"
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    resolved = metadata.get("resolved", False)
    iterations = metadata.get("iterations") or "?"
    inp = metadata.get("input_tokens_total") or 0
    out = metadata.get("output_tokens_total") or 0
    cost = metadata.get("cost_usd")
    wall = metadata.get("wall_time_seconds", 0)
    cost_str = f"${cost:.4f}" if cost is not None else "?"
    tokens_str = f"{(inp or 0) + (out or 0)}"
    line = (
        f"{_now()} | {instance_id} | resolved={resolved} | "
        f"iter={iterations} | tokens={tokens_str} | cost={cost_str} | time={wall}s"
    )
    with open(progress_path, "a", encoding="utf-8") as pf:
        pf.write(line + "\n")
    log(f"  progress.log: {line}")

    # ── 8. Cleanup ────────────────────────────────────────────────────────────
    if working_copy.exists():
        shutil.rmtree(working_copy, ignore_errors=True)
        log(f"  cleaned up working copy: {working_copy}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="SWE-Adaptive evaluation runner")
    parser.add_argument("--model",    required=True,
                        help="Model string, e.g. gemini/gemini-2.0-flash")
    parser.add_argument("--all",      action="store_true",
                        help="Run all instances")
    parser.add_argument("--instance", type=str, action="append", default=None,
                        help="Run a specific instance (may be repeated for multiple)")
    parser.add_argument("--folder",   type=str, default=None,
                        help="Run all instances in one benchmark folder")
    parser.add_argument("--resume",   action="store_true",
                        help="Skip instances that already have a score.json")
    parser.add_argument("--rerun-unresolved", action="store_true",
                        help="Skip resolved instances; archive unresolved run dirs and rerun fresh")
    parser.add_argument("--dry-run",  action="store_true",
                        help="Print what would run without executing anything")
    args = parser.parse_args()

    if not args.all and not args.instance and not args.folder:
        parser.error("Specify --all, --instance, or --folder")

    model = args.model
    model_dir = _model_dir_name(model)
    all_instances = _load_instances()

    # Filter instances
    if args.instance:
        wanted = set(args.instance)
        selected = [i for i in all_instances if i["instance_id"] in wanted]
        missing = wanted - {i["instance_id"] for i in selected}
        if missing:
            print(
                f"ERROR: instance(s) not found in instances.json: {', '.join(sorted(missing))}")
            sys.exit(1)
    elif args.folder:
        selected = [i for i in all_instances if i["folder"] == args.folder]
        if not selected:
            print(f"ERROR: no instances found in folder '{args.folder}'")
            sys.exit(1)
    else:
        selected = all_instances

    # Apply --resume filter (skip everything already scored)
    if args.resume:
        before = len(selected)
        selected = [
            i for i in selected
            if not (RUNS_DIR / model_dir / i["instance_id"] / "score.json").exists()
        ]
        print(
            f"Resume: skipping {before - len(selected)} already-scored instances")

    # Apply --rerun-unresolved filter (skip resolved, archive-then-rerun unresolved)
    if args.rerun_unresolved:
        before = len(selected)
        kept = []
        for inst in selected:
            score_path = RUNS_DIR / model_dir / \
                inst["instance_id"] / "score.json"
            if score_path.exists():
                try:
                    resolved = json.loads(
                        score_path.read_text()).get("resolved", False)
                except Exception:
                    resolved = False
                if resolved:
                    continue  # skip — leave resolved runs completely untouched
            kept.append(inst)
        selected = kept
        print(f"Rerun-unresolved: skipping {before - len(selected)} resolved instances, "
              f"{len(selected)} unresolved/pending will be rerun")

    print(f"\n{'='*60}")
    print(f"SWE-Adaptive Evaluation")
    print(f"  Model              : {model}")
    print(f"  Instances          : {len(selected)}")
    print(f"  Dry run            : {args.dry_run}")
    print(f"  Resume             : {args.resume}")
    print(f"  Rerun-unresolved   : {args.rerun_unresolved}")
    print(f"  Run dir            : {RUNS_DIR / model_dir}")
    print(f"{'='*60}\n")

    resolved_count = 0
    failed_count = 0

    for i, instance in enumerate(selected, 1):
        instance_id = instance["instance_id"]
        run_dir = RUNS_DIR / model_dir / instance_id

        # Archive existing unresolved run dir before overwriting
        if args.rerun_unresolved and run_dir.exists():
            archive_name = f"{instance_id}__prev_{_ts_compact()}"
            archive_dir = RUNS_DIR / model_dir / archive_name
            run_dir.rename(archive_dir)
            print(
                f"\n[{i}/{len(selected)}] {instance_id}  (archived → {archive_name})")
        else:
            print(f"\n[{i}/{len(selected)}] {instance_id}")

        try:
            run_instance(
                instance=instance,
                model=model,
                run_dir=run_dir,
                dry_run=args.dry_run,
            )

            if not args.dry_run:
                score_path = run_dir / "score.json"
                if score_path.exists():
                    score = json.loads(score_path.read_text())
                    if score.get("resolved"):
                        resolved_count += 1
                    else:
                        failed_count += 1

        except Exception as exc:
            tb = traceback.format_exc()
            print(f"  OUTER LOOP EXCEPTION for {instance_id}: {exc}")
            print(tb)
            failed_count += 1
            # Try to write a minimal run_metadata.json so this isn't silently lost
            run_dir.mkdir(parents=True, exist_ok=True)
            meta_path = run_dir / "run_metadata.json"
            if not meta_path.exists():
                meta_path.write_text(json.dumps({
                    "instance_id": instance_id,
                    "model": model,
                    "error": tb,
                    "timestamp_start": _now(),
                }, indent=2), encoding="utf-8")

    if not args.dry_run:
        print(f"\n{'='*60}")
        print(f"Finished {len(selected)} instances")
        print(f"  Resolved : {resolved_count}")
        print(f"  Failed   : {failed_count}")
        print(
            f"  Rate     : {resolved_count/len(selected)*100:.1f}%" if selected else "")
        print(f"{'='*60}")
        print(f"\nNext: python parse_trajectories.py to generate results/summary.csv")


if __name__ == "__main__":
    main()
