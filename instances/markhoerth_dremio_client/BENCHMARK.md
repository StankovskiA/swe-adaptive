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

### Error — unknown

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

**Root cause:** Requires manual investigation.

**Minimal fix:** Investigate the error above.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| ? | Unknown error — see raw output above | Investigate manually |
