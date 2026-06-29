# Benchmark: juniper

**Repository:** https://github.com/eabglobal/juniper
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.8)

**Docker image:** `Dockerfile.test`
**Python version:** 3.8
**Result:** 24 passed, 0 failed

All 24 tests pass on Python 3.8.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — `ipdb` uses `use_2to3` setuptools option removed in Python 3.12+

```
#9 4.739   error: subprocess-exited-with-error
#9 4.739   
#9 4.739   × Getting requirements to build wheel did not run successfully.
#9 4.739   │ exit code: 1
#9 4.739   ╰─> [3 lines of output]
#9 4.739       /tmp/pip-build-env-vr3ytz5h/overlay/lib/python3.13/site-packages/setuptools/_distutils/dist.py:287: UserWarning: Unknown distribution option: 'test_suite'
#9 4.739         warnings.warn(msg)
#9 4.739       error in ipdb setup command: use_2to3 is invalid.
#9 4.739       [end of output]
#9 4.739   
#9 4.739   note: This error originates from a subprocess, and is likely not a problem with pip.
#9 4.740 ERROR: Failed to build 'ipdb' when getting requirements to build wheel
#9 ERROR: process "/bin/sh -c pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -r requirements/dev.txt  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest" did not complete successfully: exit code: 1
------
 > [5/5] RUN pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -r requirements/dev.txt  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest:
4.739   × Getting requirements to build wheel did not run successfully.
4.739   │ exit code: 1
4.739   ╰─> [3 lines of output]
4.739       /tmp/pip-build-env-vr3ytz5h/overlay/lib/python3.13/site-packages/setuptools/_distutils/dist.py:287: UserWarning: Unknown distribution option: 'test_suite'
4.739         warnings.warn(msg)
```

**Root cause:** `requirements/dev.txt` pins an old version of `ipdb` whose `setup.py` declares `use_2to3 = True`. The `use_2to3` option (a Python 2→3 migration helper) was removed from `setuptools` in version 58.3.0. The modern setuptools shipped with Python 3.13 rejects it outright with `error in ipdb setup command: use_2to3 is invalid.`

**Minimal fix:** Upgrade `ipdb` to ≥0.13.9 in `requirements/dev.txt`, which dropped the `use_2to3` flag.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | Old `ipdb` `setup.py` declares `use_2to3 = True` — removed from setuptools ≥58.3.0; Python 3.13 ships modern setuptools → build fails | Upgrade `ipdb` to ≥0.13.9 in `requirements/dev.txt` |
