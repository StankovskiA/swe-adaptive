# Benchmark: handprint

**Repository:** https://github.com/caltechlibrary/handprint
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.10)

**Docker image:** `Dockerfile.test`
**Python version:** 3.10
**Result:** 12 passed, 0 failed

All 12 tests pass on Python 3.10.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error 1 — `pkg_resources` unavailable — `setuptools` is no longer bundled in Python 3.13+

```
#9 9.759           exec(code, locals())
#9 9.759           ~~~~^^^^^^^^^^^^^^^^
#9 9.759         File "<string>", line 42, in <module>
#9 9.759       ModuleNotFoundError: No module named 'pkg_resources'
#9 9.759       [end of output]
#9 9.759   
#9 9.759   note: This error originates from a subprocess, and is likely not a problem with pip.
#9 9.759 ERROR: Failed to build 'grpcio' when getting requirements to build wheel
#9 ERROR: process "/bin/sh -c pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest" did not complete successfully: exit code: 1
------
 > [5/5] RUN pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest:
9.759           ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
9.759         File "/tmp/pip-build-env-ot5wi1jw/overlay/lib/python3.13/site-packages/setuptools/build_meta.py", line 317, in run_setup
9.759           exec(code, locals())
9.759           ~~~~^^^^^^^^^^^^^^^^
9.759         File "<string>", line 42, in <module>
9.759       ModuleNotFoundError: No module named 'pkg_resources'
9.759       [end of output]
```

**Root cause:** `pkg_resources` unavailable — `setuptools` is no longer bundled in Python 3.13+

**Minimal fix:** Add `setuptools` as an explicit dependency, or upgrade the package that uses `pkg_resources`.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | `pkg_resources` unavailable — `setuptools` is no longer bundled in Python 3.13+ | Add `setuptools` as an explicit dependency, or upgrade the package that uses `pkg_resources`. |
