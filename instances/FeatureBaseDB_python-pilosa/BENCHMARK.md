# Benchmark: python-pilosa

**Repository:** https://github.com/FeatureBaseDB/python-pilosa
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.7)

**Docker image:** `Dockerfile.test`
**Python version:** 3.7
**Result:** 113 passed, 0 failed

All 113 tests pass on Python 3.7.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error 1 — `pkg_resources` unavailable — `setuptools` is no longer bundled in Python 3.13+

```
#9 11.42           ~~~~^^^^^^^^^^^^^^^^
#9 11.42         File "<string>", line 44, in <module>
#9 11.42         File "<string>", line 37, in <module>
#9 11.42       ModuleNotFoundError: No module named 'pkg_resources'
#9 11.42       [end of output]
#9 11.42   
#9 11.42   note: This error originates from a subprocess, and is likely not a problem with pip.
#9 11.42 ERROR: Failed to build 'file:///root/code' when getting requirements to build editable
#9 ERROR: process "/bin/sh -c pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -r requirements/main.txt -r requirements/test.txt  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest" did not complete successfully: exit code: 1
------
 > [5/5] RUN pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -r requirements/main.txt -r requirements/test.txt  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest:
11.42         File "/tmp/pip-build-env-qp3e1l2h/overlay/lib/python3.13/site-packages/setuptools/build_meta.py", line 317, in run_setup
11.42           exec(code, locals())
11.42           ~~~~^^^^^^^^^^^^^^^^
11.42         File "<string>", line 44, in <module>
11.42         File "<string>", line 37, in <module>
11.42       ModuleNotFoundError: No module named 'pkg_resources'
11.42       [end of output]
```

**Root cause:** `pkg_resources` unavailable — `setuptools` is no longer bundled in Python 3.13+

**Minimal fix:** Add `setuptools` as an explicit dependency, or upgrade the package that uses `pkg_resources`.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | `pkg_resources` unavailable — `setuptools` is no longer bundled in Python 3.13+ | Add `setuptools` as an explicit dependency, or upgrade the package that uses `pkg_resources`. |
