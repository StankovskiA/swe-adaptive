# Benchmark: aomi

**Repository:** https://github.com/Autodesk/aomi
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.8)

**Docker image:** `Dockerfile.test`
**Python version:** 3.8
**Result:** 46 passed, 0 failed

All 46 tests pass on Python 3.8.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error 1 — `pkg_resources` unavailable — `setuptools` is no longer bundled in Python 3.13+

```
#9 2.860           exec(code, locals())
#9 2.860           ~~~~^^^^^^^^^^^^^^^^
#9 2.860         File "<string>", line 5, in <module>
#9 2.860       ModuleNotFoundError: No module named 'pkg_resources'
#9 2.860       [end of output]
#9 2.860   
#9 2.860   note: This error originates from a subprocess, and is likely not a problem with pip.
#9 2.860 ERROR: Failed to build 'file:///root/code' when getting requirements to build editable
#9 ERROR: process "/bin/sh -c pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest" did not complete successfully: exit code: 1
------
 > [5/5] RUN pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest:
2.860           ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
2.860         File "/tmp/pip-build-env-gy6pvmsu/overlay/lib/python3.13/site-packages/setuptools/build_meta.py", line 317, in run_setup
2.860           exec(code, locals())
2.860           ~~~~^^^^^^^^^^^^^^^^
2.860         File "<string>", line 5, in <module>
2.860       ModuleNotFoundError: No module named 'pkg_resources'
2.860       [end of output]
```

**Root cause:** `pkg_resources` unavailable — `setuptools` is no longer bundled in Python 3.13+

**Minimal fix:** Add `setuptools` as an explicit dependency, or upgrade the package that uses `pkg_resources`.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | `pkg_resources` unavailable — `setuptools` is no longer bundled in Python 3.13+ | Add `setuptools` as an explicit dependency, or upgrade the package that uses `pkg_resources`. |
