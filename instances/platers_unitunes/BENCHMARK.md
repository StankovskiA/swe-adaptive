# Benchmark: unitunes

**Repository:** https://github.com/platers/unitunes
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.10)

**Docker image:** `Dockerfile.test`
**Python version:** 3.10
**Result:** 11 passed, 0 failed

All 11 tests pass on Python 3.10.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — `dearpygui` 1.x no longer available on PyPI; only 2.x exists

```
#9 5.004 ERROR: Could not find a version that satisfies the requirement dearpygui<2.0.0,>=1.6.2 (from unitunes) (from versions: 2.0.0rc1, 2.0.0, 2.1.0, 2.1.1, 2.2, 2.3, 2.3.1)
#9 5.004 ERROR: No matching distribution found for dearpygui<2.0.0,>=1.6.2
#9 ERROR: process "/bin/sh -c pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest" did not complete successfully: exit code: 1
------
 > [5/5] RUN pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest:
4.144   Checking if build backend supports build_editable: finished with status 'done'
4.146   Getting requirements to build editable: started
4.311   Getting requirements to build editable: finished with status 'done'
4.313   Preparing editable metadata (pyproject.toml): started
4.607   Preparing editable metadata (pyproject.toml): finished with status 'done'
4.760 Collecting appdirs<2.0.0,>=1.4.4 (from unitunes==2.0.1)
4.859   Downloading appdirs-1.4.4-py2.py3-none-any.whl.metadata (9.0 kB)
5.003 INFO: pip is looking at multiple versions of unitunes to determine which version is compatible with other requirements. This could take a while.
5.004 ERROR: Could not find a version that satisfies the requirement dearpygui<2.0.0,>=1.6.2 (from unitunes) (from versions: 2.0.0rc1, 2.0.0, 2.1.0, 2.1.1, 2.2, 2.3, 2.3.1)
5.004 ERROR: No matching distribution found for dearpygui<2.0.0,>=1.6.2
------
_Dockerfile_tmp_platers_unitunes:5
--------------------
   4 |     COPY . .
   5 | >>> RUN pip install --no-cache-dir --upgrade pip \
```

**Root cause:** `unitunes` requires `dearpygui>=1.6.2,<2.0.0`. The `dearpygui` 1.x release series has been removed from PyPI — only versions 2.0.0rc1 and later remain. On Python 3.10 the baseline Docker would have been built when 1.x was still available, but on Python 3.13 pip cannot find any installable version in the `>=1.6.2,<2.0.0` range.

**Minimal fix:** Upgrade the `dearpygui` dependency to `>=2.0.0` and update any API calls that changed between `dearpygui` 1.x and 2.x.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | `dearpygui>=1.6.2,<2.0.0` — all 1.x versions removed from PyPI; only 2.x remains → `No matching distribution found` | Upgrade to `dearpygui>=2.0.0` and adapt to the 2.x API |
