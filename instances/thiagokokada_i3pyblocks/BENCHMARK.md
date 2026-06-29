# Benchmark: i3pyblocks

**Repository:** https://github.com/thiagokokada/i3pyblocks
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.9)

**Docker image:** `Dockerfile.test`
**Python version:** 3.9
**Result:** 63 passed, 0 failed

All 63 tests pass on Python 3.9.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error 1 — `pkg_resources` unavailable — `setuptools` is no longer bundled in Python 3.13+

```
#9 7.966           from .version import format_version, meta
#9 7.966         File "/tmp/pip-build-env-un3qmb6n/overlay/lib/python3.13/site-packages/setuptools_scm/version.py", line 11, in <module>
#9 7.966           from pkg_resources import iter_entry_points
#9 7.966       ModuleNotFoundError: No module named 'pkg_resources'
#9 7.966       [end of output]
#9 7.966   
#9 7.966   note: This error originates from a subprocess, and is likely not a problem with pip.
#9 7.967 error: metadata-generation-failed
#9 7.967 
#9 7.967 × Encountered error while generating package metadata.
#9 7.967 ╰─> lazy-object-proxy
#9 7.967 
#9 7.967 note: This is an issue with the package mentioned above, not pip.
#9 7.967 hint: See above for details.
#9 ERROR: process "/bin/sh -c pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -r requirements.txt  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest" did not complete successfully: exit code: 1
------
 > [5/5] RUN pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -r requirements.txt  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest:
7.966       [end of output]
```

**Root cause:** `pkg_resources` unavailable — `setuptools` is no longer bundled in Python 3.13+

**Minimal fix:** Add `setuptools` as an explicit dependency, or upgrade the package that uses `pkg_resources`.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | `pkg_resources` unavailable — `setuptools` is no longer bundled in Python 3.13+ | Add `setuptools` as an explicit dependency, or upgrade the package that uses `pkg_resources`. |
