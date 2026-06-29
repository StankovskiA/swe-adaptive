# Benchmark: pybotics

**Repository:** https://github.com/engnadeau/pybotics
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.10)

**Docker image:** `Dockerfile.test`
**Python version:** 3.10
**Result:** 36 passed, 0 failed

All 36 tests pass on Python 3.10.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — `python_requires = ">=3.9,<3.13"` explicitly excludes Python 3.13

```
#9 5.044 ERROR: Package 'pybotics' requires a different Python: 3.13.14 not in '<3.13,>=3.9'
#9 ERROR: process "/bin/sh -c pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -e .  && pip install --no-cache-dir coverage hypothesis pytest pytest-cov pytest-randomly pytest-runner" did not complete successfully: exit code: 1
------
 > [5/5] RUN pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -e .  && pip install --no-cache-dir coverage hypothesis pytest pytest-cov pytest-randomly pytest-runner:
3.393   Installing build dependencies: started
4.428   Installing build dependencies: finished with status 'done'
4.429   Checking if build backend supports build_editable: started
4.692   Checking if build backend supports build_editable: finished with status 'done'
4.694   Getting requirements to build editable: started
4.815   Getting requirements to build editable: finished with status 'done'
4.817   Preparing editable metadata (pyproject.toml): started
5.038   Preparing editable metadata (pyproject.toml): finished with status 'done'
5.044 INFO: pip is looking at multiple versions of pybotics to determine which version is compatible with other requirements. This could take a while.
5.044 ERROR: Package 'pybotics' requires a different Python: 3.13.14 not in '<3.13,>=3.9'
------
_Dockerfile_tmp_engnadeau_pybotics:5
--------------------
   4 |     COPY . .
   5 | >>> RUN pip install --no-cache-dir --upgrade pip \
   6 | >>>  && pip install --no-cache-dir -e . \
```

**Root cause:** `pyproject.toml` declares `requires-python = ">=3.9,<3.13"`, explicitly capping support at Python 3.12. pip enforces this constraint and refuses to install the package on Python 3.13.14.

**Minimal fix:** Widen the constraint to `requires-python = ">=3.9"` in `pyproject.toml` and verify that any Python-version-specific code in the library works on 3.13.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | `pyproject.toml` declares `requires-python = ">=3.9,<3.13"` — pip refuses to install on Python 3.13.14 | Widen to `requires-python = ">=3.9"` in `pyproject.toml` |
