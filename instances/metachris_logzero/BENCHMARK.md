# Benchmark: logzero

**Repository:** https://github.com/metachris/logzero
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.9)

**Docker image:** `Dockerfile.test`
**Python version:** 3.9
**Result:** 25 passed, 0 failed

All 25 tests pass on Python 3.9.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error 1 — `imp` module removed in Python 3.12+ (deprecated since 3.4)

```
#9 8.307           exec(code, locals())
#9 8.307           ~~~~^^^^^^^^^^^^^^^^
#9 8.307         File "<string>", line 25, in <module>
#9 8.307       ModuleNotFoundError: No module named 'imp'
#9 8.307       [end of output]
#9 8.307   
#9 8.307   note: This error originates from a subprocess, and is likely not a problem with pip.
#9 8.307 ERROR: Failed to build 'pathtools' when getting requirements to build wheel
#9 ERROR: process "/bin/sh -c pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -r requirements_dev.txt  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest" did not complete successfully: exit code: 1
------
 > [5/5] RUN pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -r requirements_dev.txt  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest:
8.307           ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
8.307         File "/tmp/pip-build-env-3we2u882/overlay/lib/python3.13/site-packages/setuptools/build_meta.py", line 317, in run_setup
8.307           exec(code, locals())
8.307           ~~~~^^^^^^^^^^^^^^^^
8.307         File "<string>", line 25, in <module>
8.307       ModuleNotFoundError: No module named 'imp'
8.307       [end of output]
```

**Root cause:** `imp` module removed in Python 3.12+ (deprecated since 3.4)

**Minimal fix:** Upgrade the package that imports `imp` to a newer version using `importlib`.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | `imp` module removed in Python 3.12+ (deprecated since 3.4) | Upgrade the package that imports `imp` to a newer version using `importlib`. |
