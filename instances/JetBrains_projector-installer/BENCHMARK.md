# Benchmark: projector-installer

**Repository:** https://github.com/JetBrains/projector-installer
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.8)

**Docker image:** `Dockerfile.test`
**Python version:** 3.8
**Result:** 39 passed, 0 failed

All 39 tests pass on Python 3.8.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — `setup.py` imports `netifaces` at module level; absent from pip build isolation env

```
#9 10.19   error: subprocess-exited-with-error
#9 10.19   
#9 10.19   x Getting requirements to build editable did not run successfully.
#9 10.19   | exit code: 1
#9 10.19   +-> [29 lines of output]
#9 10.19       Traceback (most recent call last):
#9 10.19         File "/usr/local/lib/python3.13/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py", line 389, in <module>
#9 10.19           main()
#9 10.19         File ".../setuptools/build_meta.py", line 333, in get_requires_for_build_wheel
#9 10.19           return self._get_build_requires(config_settings, requirements=[])
#9 10.19       ...
#9 10.19       ModuleNotFoundError: No module named 'netifaces'
#9 10.19   note: This error originates from a subprocess, and is likely not a problem with pip.
#9 10.26 ERROR: Failed to build 'file:///root/code' when getting requirements to build editable
```

**Root cause:** `setup.py` imports `netifaces` at module level (to enumerate network interfaces). pip (as shipped with Python 3.13) executes `setup.py` in a fully isolated build environment containing only build-system dependencies (setuptools, wheel). Even though `netifaces` was installed from `requirements.txt` in the previous step, it is invisible inside the isolated subprocess, causing `ModuleNotFoundError: No module named 'netifaces'`. Older pip on Python 3.8 ran `setup.py` in the ambient environment where the prior install was visible.

**Minimal fix:** Add `netifaces` to `build-system.requires` in `setup.cfg` (or, better, remove the top-level `netifaces` import from `setup.py` and replace it with a static string).

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | `setup.py` imports `netifaces` at module level; pip's build isolation (enforced by modern pip/Python 3.13) hides it → `ModuleNotFoundError: No module named 'netifaces'` | Add `netifaces` to `build-system.requires` in `setup.cfg` or remove the import from `setup.py` |
