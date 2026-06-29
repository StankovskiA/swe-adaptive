# Benchmark: flask-assistant

**Repository:** https://github.com/treethought/flask-assistant
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.9)

**Docker image:** `Dockerfile.test`
**Python version:** 3.9
**Result:** 17 passed, 0 failed

All 17 tests pass on Python 3.9.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error 1 — `pkg_resources` unavailable — `setuptools` is no longer bundled in Python 3.13+

```
#9 8.194           exec(code, locals())
#9 8.194           ~~~~^^^^^^^^^^^^^^^^
#9 8.194         File "<string>", line 31, in <module>
#9 8.194       ModuleNotFoundError: No module named 'pkg_resources'
#9 8.194       [end of output]
#9 8.194   
#9 8.194   note: This error originates from a subprocess, and is likely not a problem with pip.
#9 8.195 ERROR: Failed to build 'grpcio' when getting requirements to build wheel
#9 ERROR: process "/bin/sh -c pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -r requirements.txt  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest" did not complete successfully: exit code: 1
------
 > [5/5] RUN pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -r requirements.txt  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest:
8.194           ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
8.194         File "/tmp/pip-build-env-7bbdotgu/overlay/lib/python3.13/site-packages/setuptools/build_meta.py", line 317, in run_setup
8.194           exec(code, locals())
8.194           ~~~~^^^^^^^^^^^^^^^^
8.194         File "<string>", line 31, in <module>
8.194       ModuleNotFoundError: No module named 'pkg_resources'
8.194       [end of output]
```

**Root cause:** `pkg_resources` unavailable — `setuptools` is no longer bundled in Python 3.13+

**Minimal fix:** Add `setuptools` as an explicit dependency, or upgrade the package that uses `pkg_resources`.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | `pkg_resources` unavailable — `setuptools` is no longer bundled in Python 3.13+ | Add `setuptools` as an explicit dependency, or upgrade the package that uses `pkg_resources`. |
