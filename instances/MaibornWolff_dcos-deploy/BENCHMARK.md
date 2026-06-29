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

### Error — unknown

```
#9 15.85   error: subprocess-exited-with-error
#9 15.85   
#9 15.85   × Getting requirements to build wheel did not run successfully.
#9 15.85   │ exit code: 1
#9 15.85   ╰─> [3 lines of output]
#9 15.85       pystache: using: version '82.0.1' of <module 'setuptools' from '/tmp/pip-build-env-dql4mo6w/overlay/lib/python3.13/site-packages/setuptools/__init__.py'>
#9 15.85       Warning: 'classifiers' should be a list, got type 'tuple'
#9 15.85       error in pystache setup command: use_2to3 is invalid.
#9 15.85       [end of output]
#9 15.85   
#9 15.85   note: This error originates from a subprocess, and is likely not a problem with pip.
#9 15.85 ERROR: Failed to build 'pystache' when getting requirements to build wheel
#9 ERROR: process "/bin/sh -c pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -r requirements-dev.txt  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest" did not complete successfully: exit code: 1
------
 > [5/5] RUN pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -r requirements-dev.txt  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest:
15.85   × Getting requirements to build wheel did not run successfully.
15.85   │ exit code: 1
15.85   ╰─> [3 lines of output]
15.85       pystache: using: version '82.0.1' of <module 'setuptools' from '/tmp/pip-build-env-dql4mo6w/overlay/lib/python3.13/site-packages/setuptools/__init__.py'>
15.85       Warning: 'classifiers' should be a list, got type 'tuple'
```

**Root cause:** Requires manual investigation.

**Minimal fix:** Investigate the error above.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| ? | Unknown error — see raw output above | Investigate manually |
