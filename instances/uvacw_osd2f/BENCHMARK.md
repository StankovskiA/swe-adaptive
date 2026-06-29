# Benchmark: osd2f

**Repository:** https://github.com/uvacw/osd2f
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.9)

**Docker image:** `Dockerfile.test`
**Python version:** 3.9
**Result:** 55 passed, 0 failed

All 55 tests pass on Python 3.9.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — unknown

```
#9 47.48   error: subprocess-exited-with-error
#9 47.48   
#9 47.48   × Building wheel for asyncpg (pyproject.toml) did not run successfully.
#9 47.48   │ exit code: 1
#9 47.48   ╰─> [262 lines of output]
#9 47.48       /tmp/pip-build-env-p7gv2dx9/overlay/lib/python3.13/site-packages/setuptools/config/_apply_pyprojecttoml.py:82: SetuptoolsDeprecationWarning: `project.license` as a TOML table is deprecated
#9 47.48       !!
#9 47.48       
#9 47.48               ********************************************************************************
#9 47.48               Please use a simple string containing a SPDX expression for `project.license`. You can also use `project.license-files`. (Both options available on setuptools>=77.0.0).
#9 47.48       
#9 47.48               By 2027-Feb-18, you need to update your project and remove deprecated calls
#9 47.48               or your builds will no longer be supported.
#9 47.48       
#9 47.48               See https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#license for details.
#9 47.48               ********************************************************************************
#9 47.48       
#9 47.48       !!
#9 47.48         corresp(dist, value, root_dir)
#9 47.48       /tmp/pip-build-env-p7gv2dx9/overlay/lib/python3.13/site-packages/setuptools/config/_apply_pyprojecttoml.py:61: SetuptoolsDeprecationWarning: License classifiers are deprecated.
```

**Root cause:** Requires manual investigation.

**Minimal fix:** Investigate the error above.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| ? | Unknown error — see raw output above | Investigate manually |
