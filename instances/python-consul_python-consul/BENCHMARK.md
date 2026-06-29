# Benchmark: python-consul/python-consul

**Repo:** https://github.com/python-consul/python-consul  
**Stars:** 459  
**Baseline Python:** 3.10 (26/26 tests pass in `tests/test_base.py`)  
**Failing Python:** 3.13  

## Why the baseline requires special setup

The repo has `README.md` but `setup.py` reads `README.rst` and `CHANGELOG.rst` — both missing. Fix: create stubs with `touch README.rst CHANGELOG.rst`. Additionally, this legacy `setup.py`-based package requires `setuptools<66` with `--no-build-isolation` to install successfully on Python 3.10.

Note: only `tests/test_base.py` is run. The other test files (`test_std.py`, `test_aio.py`, `test_tornado.py`, `test_twisted.py`) require a running Consul service and are excluded from the benchmark.

## Python 3.13 failure

**Error:**
```
File ".../site-packages/pkg_resources/__init__.py", line 2191, in <module>
    register_finder(pkgutil.ImpImporter, find_on_path)
AttributeError: module 'pkgutil' has no attribute 'ImpImporter'
```

**Root cause:** The package requires `setuptools<66`, which ships an old `pkg_resources` that calls `pkgutil.ImpImporter` at import time. `pkgutil.ImpImporter` was removed in Python 3.12 (PEP 594 cleanup), so the package cannot even be installed on Python 3.13.

**Minimal fix:** Upgrade `setuptools` to >=66 (which removes the `pkg_resources` dependency on `pkgutil.ImpImporter`) AND update `setup.py` to use `packages=find_packages()` instead of the broken `py_modules` approach, so the `consul` package is importable after installation.
