# Benchmark: dcos-deploy

**Repository:** https://github.com/MaibornWolff/dcos-deploy
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.8)

**Docker image:** `Dockerfile.test`
**Python version:** 3.8
**Result:** 49 passed, 0 failed

All 49 tests pass on Python 3.8.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — `pystache` uses `use_2to3` setuptools option removed in Python 3.12+

```
#9 15.85   error: subprocess-exited-with-error
#9 15.85   
#9 15.85   x Getting requirements to build wheel did not run successfully.
#9 15.85   | exit code: 1
#9 15.85   +-> [3 lines of output]
#9 15.85       pystache: using: version '82.0.1' of setuptools
#9 15.85       Warning: 'classifiers' should be a list, got type 'tuple'
#9 15.85       error in pystache setup command: use_2to3 is invalid.
#9 15.85   note: This error originates from a subprocess, and is likely not a problem with pip.
#9 15.85 ERROR: Failed to build 'pystache' when getting requirements to build wheel
```

**Root cause:** `requirements-dev.txt` includes `pystache`, a Mustache template library whose `setup.py` declares `use_2to3 = True` — a Python 2→3 source translation flag that was removed from `setuptools` in version 58.3.0. The modern setuptools bundled with Python 3.13 (v82.0.1) rejects it with `error in pystache setup command: use_2to3 is invalid.`

**Minimal fix:** Replace `pystache` with a maintained fork (e.g., `pystache2`, `chevron`, or `mustache`) in `requirements-dev.txt`.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | `pystache` `setup.py` declares `use_2to3 = True` — removed from setuptools ≥58.3.0; Python 3.13 ships setuptools 82.x → build fails | Replace `pystache` with a maintained Mustache library in `requirements-dev.txt` |
