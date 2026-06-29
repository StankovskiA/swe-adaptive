# Benchmark: pipelinewise-tap-postgres

**Repository:** https://github.com/transferwise/pipelinewise-tap-postgres
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.9)

**Docker image:** `Dockerfile.test`
**Python version:** 3.9
**Result:** 112 passed, 0 failed

All 112 tests pass on Python 3.9.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — `python_requires = ">=3.7,<3.10"` explicitly excludes Python 3.13

```
#9 6.040 ERROR: Package 'pipelinewise-tap-postgres' requires a different Python: 3.13.14 not in '<3.10,>=3.7'
#9 ERROR: process "/bin/sh -c pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest" did not complete successfully: exit code: 1
------
 > [5/5] RUN pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest:
6.039 INFO: pip is looking at multiple versions of pipelinewise-tap-postgres to determine which version is compatible with other requirements. This could take a while.
6.040 ERROR: Package 'pipelinewise-tap-postgres' requires a different Python: 3.13.14 not in '<3.10,>=3.7'
```

**Root cause:** `setup.py` (or `setup.cfg`) declares `python_requires=">=3.7,<3.10"`, explicitly capping support at Python 3.9. pip enforces this constraint and refuses to install the package on Python 3.13.14.

**Minimal fix:** Widen the constraint to `python_requires=">=3.7"` in `setup.cfg` and verify that any Python-version-specific code (likely psycopg2 usage or PostgreSQL-specific typing) works on Python 3.13.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | `setup.cfg` declares `python_requires=">=3.7,<3.10"` — pip refuses to install on Python 3.13.14 | Widen to `python_requires=">=3.7"` in `setup.cfg` |
