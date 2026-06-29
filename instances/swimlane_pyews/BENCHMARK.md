# Benchmark: pyews

**Repository:** https://github.com/swimlane/pyews
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.10)

**Docker image:** `Dockerfile.test`
**Python version:** 3.10
**Result:** 8 passed, 0 failed

All 8 tests pass on Python 3.10.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — `lxml==4.7.1` has no Python 3.13 wheels; source build fails — missing `libxml2-dev`

```
#9 6.007   error: subprocess-exited-with-error
#9 6.007   
#9 6.007   x Getting requirements to build wheel did not run successfully.
#9 6.007   | exit code: 1
#9 6.007   +-> [4 lines of output]
#9 6.007       Building lxml version 4.7.1.
#9 6.007       Building without Cython.
#9 6.007       Error: Please make sure the libxml2 and libxslt development packages are installed.
#9 6.007   note: This error originates from a subprocess, and is likely not a problem with pip.
#9 6.007 ERROR: Failed to build 'lxml' when getting requirements to build wheel
```

**Root cause:** `requirements.txt` pins `lxml==4.7.1`. This release ships pre-built wheels only for Python ≤3.10. On Python 3.13, pip falls back to building from source, which requires the `libxml2` and `libxslt` development headers. These are not installed in `python:3.13-slim`, so the source build fails with `Error: Please make sure the libxml2 and libxslt development packages are installed.`

**Minimal fix:** Upgrade `lxml` to `>=5.0.0` in `requirements.txt`, which ships Python 3.13 pre-built wheels that don't require system libraries.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | `lxml==4.7.1` has no Python 3.13 wheels; pip falls back to source build but `python:3.13-slim` lacks `libxml2-dev`/`libxslt1-dev` → build fails | Upgrade `lxml` to `>=5.0.0` in `requirements.txt` (has Python 3.13 pre-built wheels) |
