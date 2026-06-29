# Benchmark Instances

This directory contains the 132 verified benchmark instances.

Each instance is a subdirectory named `owner__reponame/` containing:
- `Dockerfile.test` — baseline (passes on historical Python version)
- `Dockerfile.py313` — failing target (fails on Python 3.13, uses RUN not CMD)
- `BENCHMARK.md` — project description, root cause analysis, benchmark task

## Instance Format

```json
{
  "instance_id": "owner__reponame",
  "repo_url": "https://github.com/owner/reponame",
  "base_commit": "<sha>",
  "breaking_change_type": "no_wheel",
  "py313_error_output": "...",
  "reproduction_recipe": {
    "install_cmd": "pip install -e '.[dev]'",
    "test_cmd": "pytest tests/ -q"
  }
}
```

Instance data will be populated upon public release.
