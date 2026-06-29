# Benchmark: typer-cli

**Repository:** https://github.com/tiangolo/typer-cli
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.9)

**Docker image:** `Dockerfile.test`
**Python version:** 3.9
**Result:** 41 passed, 0 failed

All 41 tests pass on Python 3.9.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error 1 — `distutils` removed in Python 3.12+ (deprecated since 3.10)

```
#9 0.498 INTERNALERROR>     res = hook_impl.function(*args)
#9 0.498 INTERNALERROR>   File "/usr/local/lib/python3.13/site-packages/pytest_sugar.py", line 168, in pytest_configure
#9 0.498 INTERNALERROR>     from distutils.version import LooseVersion
#9 0.498 INTERNALERROR> ModuleNotFoundError: No module named 'distutils'
#9 ERROR: process "/bin/sh -c pytest tests/ -v" did not complete successfully: exit code: 3
------
 > [5/5] RUN pytest tests/ -v:
0.498 INTERNALERROR>   File "/usr/local/lib/python3.13/site-packages/pluggy/_manager.py", line 120, in _hookexec
0.498 INTERNALERROR>     return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
0.498 INTERNALERROR>            ~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
0.498 INTERNALERROR>   File "/usr/local/lib/python3.13/site-packages/pluggy/_callers.py", line 167, in _multicall
0.498 INTERNALERROR>     raise exception
0.498 INTERNALERROR>   File "/usr/local/lib/python3.13/site-packages/pluggy/_callers.py", line 121, in _multicall
0.498 INTERNALERROR>     res = hook_impl.function(*args)
0.498 INTERNALERROR>   File "/usr/local/lib/python3.13/site-packages/pytest_sugar.py", line 168, in pytest_configure
0.498 INTERNALERROR>     from distutils.version import LooseVersion
0.498 INTERNALERROR> ModuleNotFoundError: No module named 'distutils'
------
```

**Root cause:** `distutils` removed in Python 3.12+ (deprecated since 3.10)

**Minimal fix:** Upgrade `setuptools` and any package that imports `distutils` directly.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | `distutils` removed in Python 3.12+ (deprecated since 3.10) | Upgrade `setuptools` and any package that imports `distutils` directly. |
