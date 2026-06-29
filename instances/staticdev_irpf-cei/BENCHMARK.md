# Benchmark: irpf-cei

**Repository:** https://github.com/staticdev/irpf-cei
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.8)

**Docker image:** `Dockerfile.test`
**Python version:** 3.8
**Result:** 47 passed, 0 failed

All 47 tests pass on Python 3.8.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error 1 — `pkg_resources` unavailable — `setuptools` is no longer bundled in Python 3.13+

```
#9 8.002           exec(code, locals())
#9 8.002           ~~~~^^^^^^^^^^^^^^^^
#9 8.002         File "<string>", line 19, in <module>
#9 8.002       ModuleNotFoundError: No module named 'pkg_resources'
#9 8.002       [end of output]
#9 8.002   
#9 8.002   note: This error originates from a subprocess, and is likely not a problem with pip.
#9 8.002 ERROR: Failed to build 'pandas' when getting requirements to build wheel
#9 ERROR: process "/bin/sh -c pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest pytest-mock pyfakefs xdoctest coverage" did not complete successfully: exit code: 1
------
 > [5/5] RUN pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest pytest-mock pyfakefs xdoctest coverage:
8.002           ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
8.002         File "/tmp/pip-build-env-yejet8oh/overlay/lib/python3.13/site-packages/setuptools/build_meta.py", line 317, in run_setup
8.002           exec(code, locals())
8.002           ~~~~^^^^^^^^^^^^^^^^
8.002         File "<string>", line 19, in <module>
8.002       ModuleNotFoundError: No module named 'pkg_resources'
8.002       [end of output]
```

**Root cause:** `pkg_resources` unavailable — `setuptools` is no longer bundled in Python 3.13+

**Minimal fix:** Add `setuptools` as an explicit dependency, or upgrade the package that uses `pkg_resources`.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | `pkg_resources` unavailable — `setuptools` is no longer bundled in Python 3.13+ | Add `setuptools` as an explicit dependency, or upgrade the package that uses `pkg_resources`. |
