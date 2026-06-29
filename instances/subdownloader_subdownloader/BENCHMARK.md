# Benchmark: subdownloader

**Repository:** https://github.com/subdownloader/subdownloader
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.7)

**Docker image:** `Dockerfile.test`
**Python version:** 3.7
**Result:** 27 passed, 0 failed

All 27 tests pass on Python 3.7.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — `setup.py` imports `sphinx` at module level; absent from pip build isolation env

```
#9 22.73   error: subprocess-exited-with-error
#9 22.73   
#9 22.73   x Getting requirements to build editable did not run successfully.
#9 22.73   | exit code: 1
#9 22.73   +-> [26 lines of output]
#9 22.73       Traceback (most recent call last):
#9 22.73         File ".../setuptools/build_meta.py", line 333, in get_requires_for_build_wheel
#9 22.73           return self._get_build_requires(config_settings, requirements=[])
#9 22.73       ...
#9 22.73       ModuleNotFoundError: No module named 'sphinx'
#9 22.73   note: This error originates from a subprocess, and is likely not a problem with pip.
#9 22.73 ERROR: Failed to build 'file:///root/code' when getting requirements to build editable
```

**Root cause:** `setup.py` imports `sphinx` at module level (to introspect extensions or build docs metadata). pip (as shipped with Python 3.13) executes `setup.py` in a fully isolated build environment that contains only build-system dependencies. Even though `sphinx` was installed from `requirements_dev.txt` in the previous step, it is invisible inside the isolated subprocess, causing `ModuleNotFoundError: No module named 'sphinx'`. Older pip on Python 3.7 ran `setup.py` in the ambient environment where the prior install was visible.

**Minimal fix:** Add `sphinx` to `build-system.requires` in `setup.cfg`, or move the sphinx import inside the function body so it is only executed at runtime, not during the metadata step.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | `setup.py` imports `sphinx` at module level; pip's build isolation (enforced by modern pip/Python 3.13) hides it → `ModuleNotFoundError: No module named 'sphinx'` | Add `sphinx` to `build-system.requires` in `setup.cfg` or guard the import |
