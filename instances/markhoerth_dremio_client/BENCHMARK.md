# Benchmark: dremio_client

**Repository:** https://github.com/markhoerth/dremio_client
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.8)

**Docker image:** `Dockerfile.test`
**Python version:** 3.8
**Result:** 12 passed, 0 failed

All 12 tests pass on Python 3.8.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — pip's vendored `pkg_resources` uses `pkgutil.ImpImporter` removed in Python 3.12+

```
#9 22.33 Traceback (most recent call last):
#9 22.33   File "/usr/local/bin/pip", line 3, in <module>
#9 22.33     from pip._internal.cli.main import main
#9 22.33   File "/usr/local/lib/python3.13/site-packages/pip/_internal/cli/main.py", line 9, in <module>
#9 22.33     from pip._internal.cli.autocompletion import autocomplete
#9 22.33   File "/usr/local/lib/python3.13/site-packages/pip/_internal/cli/autocompletion.py", line 10, in <module>
#9 22.33     from pip._internal.cli.main_parser import create_main_parser
#9 22.33   File "/usr/local/lib/python3.13/site-packages/pip/_internal/cli/main_parser.py", line 8, in <module>
#9 22.33     from pip._internal.cli import cmdoptions
#9 22.33   File "/usr/local/lib/python3.13/site-packages/pip/_internal/cli/cmdoptions.py", line 23, in <module>
#9 22.33     from pip._internal.cli.parser import ConfigOptionParser
#9 22.33   File "/usr/local/lib/python3.13/site-packages/pip/_internal/cli/parser.py", line 12, in <module>
#9 22.33     from pip._internal.configuration import Configuration, ConfigurationError
#9 22.33   File "/usr/local/lib/python3.13/site-packages/pip/_internal/configuration.py", line 21, in <module>
#9 22.33     from pip._internal.exceptions import (
#9 22.33     ...<2 lines>...
#9 22.33     )
#9 22.33   File "/usr/local/lib/python3.13/site-packages/pip/_internal/exceptions.py", line 7, in <module>
#9 22.33     from pip._vendor.pkg_resources import Distribution
#9 22.33   File "/usr/local/lib/python3.13/site-packages/pip/_vendor/pkg_resources/__init__.py", line 2164, in <module>
```

**Root cause:** The bundled pip in `python:3.13-slim` vendors an old `pkg_resources` (`pip._vendor.pkg_resources`) that accesses `pkgutil.ImpImporter` unconditionally at module-level. Python 3.12 removed `pkgutil.ImpImporter` (legacy import system shim). The crash happens inside pip itself before any package install begins: `from pip._vendor.pkg_resources import Distribution` → `AttributeError: module 'pkgutil' has no attribute 'ImpImporter'`.

**Minimal fix:** Use `python -m ensurepip --upgrade` or bootstrap pip with `curl https://bootstrap.pypa.io/get-pip.py | python` before calling pip, or pin the base image to a tag that ships pip ≥23.1 which vendored a fixed `pkg_resources`.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | pip's vendored `pkg_resources` accesses `pkgutil.ImpImporter` removed in Python 3.12+ → pip itself crashes on startup → `AttributeError: module 'pkgutil' has no attribute 'ImpImporter'` | Bootstrap pip via `python -m ensurepip --upgrade` or use a base image with pip ≥23.1 |
