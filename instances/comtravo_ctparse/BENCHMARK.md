# Benchmark: ctparse

**Repository:** https://github.com/comtravo/ctparse
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.10)

**Docker image:** `Dockerfile.test`
**Python version:** 3.10
**Result:** 479 passed, 0 failed

All 479 tests pass on Python 3.10.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error 1 — `imp` module removed in Python 3.12+ (deprecated since 3.4)

```
#9 9.705           exec(code, locals())
#9 9.705           ~~~~^^^^^^^^^^^^^^^^
#9 9.705         File "<string>", line 25, in <module>
#9 9.705       ModuleNotFoundError: No module named 'imp'
#9 9.705       [end of output]
#9 9.705   
#9 9.705   note: This error originates from a subprocess, and is likely not a problem with pip.
#9 9.706 ERROR: Failed to build 'pathtools' when getting requirements to build wheel
#9 ERROR: process "/bin/sh -c pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -r requirements.txt -r requirements_dev.txt  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest" did not complete successfully: exit code: 1
------
 > [5/5] RUN pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -r requirements.txt -r requirements_dev.txt  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest:
9.705           ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
9.705         File "/tmp/pip-build-env-per8u3qr/overlay/lib/python3.13/site-packages/setuptools/build_meta.py", line 317, in run_setup
9.705           exec(code, locals())
9.705           ~~~~^^^^^^^^^^^^^^^^
9.705         File "<string>", line 25, in <module>
9.705       ModuleNotFoundError: No module named 'imp'
9.705       [end of output]
```

**Root cause:** `imp` module removed in Python 3.12+ (deprecated since 3.4)

**Minimal fix:** Upgrade the package that imports `imp` to a newer version using `importlib`.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | `imp` module removed in Python 3.12+ (deprecated since 3.4) | Upgrade the package that imports `imp` to a newer version using `importlib`. |
