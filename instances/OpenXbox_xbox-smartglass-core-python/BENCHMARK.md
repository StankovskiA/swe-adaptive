# Benchmark: xbox-smartglass-core-python

**Repository:** https://github.com/OpenXbox/xbox-smartglass-core-python
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.7)

**Docker image:** `Dockerfile.test`
**Python version:** 3.7
**Result:** 122 passed, 0 failed

All 122 tests pass on Python 3.7.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error 1 — `imp` module removed in Python 3.12+ (deprecated since 3.4)

```
#9 3.296           from construct.core import *
#9 3.296         File "/tmp/pip-install-iuhlb159/construct_a02e78dbfa2a44ba8e294d6235af3fd1/construct/core.py", line 3, in <module>
#9 3.296           import struct, io, binascii, itertools, collections, pickle, sys, os, tempfile, hashlib, importlib, imp
#9 3.296       ModuleNotFoundError: No module named 'imp'
#9 3.296       [end of output]
#9 3.296   
#9 3.296   note: This error originates from a subprocess, and is likely not a problem with pip.
#9 3.297 ERROR: Failed to build 'construct' when getting requirements to build wheel
#9 ERROR: process "/bin/sh -c pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -r requirements.txt  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest" did not complete successfully: exit code: 1
------
 > [5/5] RUN pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -r requirements.txt  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest:
3.296         File "<string>", line 3, in <module>
3.296         File "/tmp/pip-install-iuhlb159/construct_a02e78dbfa2a44ba8e294d6235af3fd1/construct/__init__.py", line 22, in <module>
3.296           from construct.core import *
3.296         File "/tmp/pip-install-iuhlb159/construct_a02e78dbfa2a44ba8e294d6235af3fd1/construct/core.py", line 3, in <module>
3.296           import struct, io, binascii, itertools, collections, pickle, sys, os, tempfile, hashlib, importlib, imp
3.296       ModuleNotFoundError: No module named 'imp'
3.296       [end of output]
```

**Root cause:** `imp` module removed in Python 3.12+ (deprecated since 3.4)

**Minimal fix:** Upgrade the package that imports `imp` to a newer version using `importlib`.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | `imp` module removed in Python 3.12+ (deprecated since 3.4) | Upgrade the package that imports `imp` to a newer version using `importlib`. |
