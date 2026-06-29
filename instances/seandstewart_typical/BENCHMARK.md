# Benchmark: typical

**Repository:** https://github.com/seandstewart/typical
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.10)

**Docker image:** `Dockerfile.test`
**Python version:** 3.10
**Result:** 841 passed, 0 failed

All 841 tests pass on Python 3.10.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — `numpy==1.21.4` declares `Requires-Python >=3.7,<3.11`; excluded on Python 3.13

```
#9 9.882 ERROR: Ignored the following versions that require a different python version:
         1.21.4 Requires-Python >=3.7,<3.11
         1.26.0 Requires-Python >=3.9,<3.13
         1.26.1 Requires-Python >=3.9,<3.13
#9 9.882 ERROR: Could not find a version that satisfies the requirement numpy==1.21.4
         (from versions: ..., 1.21.0, 1.21.1, 1.22.0, ..., 2.5.0)
#9 9.882 ERROR: No matching distribution found for numpy==1.21.4
```

**Root cause:** `requirements.txt` pins `numpy==1.21.4`. That exact release declares `Requires-Python >=3.7,<3.11`, which explicitly excludes Python 3.13. pip correctly refuses to install it — note the "Ignored versions that require a different python version" message. The version does exist on PyPI but pip enforces the metadata constraint.

**Minimal fix:** Upgrade `numpy` in `requirements.txt` to `>=2.0.0` (the oldest numpy series with Python 3.13 wheels) and ensure any numpy 1.x API usages are compatible with numpy 2.x.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | `numpy==1.21.4` declares `Requires-Python >=3.7,<3.11`; pip on Python 3.13 correctly skips it → `No matching distribution found` | Upgrade `numpy` to `>=2.0.0` in `requirements.txt` |
