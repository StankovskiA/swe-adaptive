# Benchmark: awaitwhat

**Repository:** https://github.com/dimaqq/awaitwhat
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.9)

**Docker image:** `Dockerfile.test`
**Python version:** 3.9
**Result:** 4 passed, 0 failed

All 4 tests pass on Python 3.9.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — unknown

```
#9 4.913   error: subprocess-exited-with-error
#9 4.913   
#9 4.913   × Building editable for awaitwhat (pyproject.toml) did not run successfully.
#9 4.913   │ exit code: 1
#9 4.913   ╰─> [44 lines of output]
#9 4.913       /tmp/pip-build-env-ooaureaj/overlay/lib/python3.13/site-packages/setuptools/config/pyprojecttoml.py:72: _ExperimentalConfiguration: `[tool.setuptools.ext-modules]` in `pyproject.toml` is still *experimental* and likely to change in future releases.
#9 4.913         config = read_configuration(filepath, True, ignore_option_errors, dist)
#9 4.913       /tmp/pip-build-env-ooaureaj/overlay/lib/python3.13/site-packages/setuptools/config/_apply_pyprojecttoml.py:82: SetuptoolsDeprecationWarning: `project.license` as a TOML table is deprecated
#9 4.913       !!
#9 4.913       
#9 4.913               ********************************************************************************
#9 4.913               Please use a simple string containing a SPDX expression for `project.license`. You can also use `project.license-files`. (Both options available on setuptools>=77.0.0).
#9 4.913       
#9 4.913               By 2027-Feb-18, you need to update your project and remove deprecated calls
#9 4.913               or your builds will no longer be supported.
#9 4.913       
#9 4.913               See https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#license for details.
#9 4.913               ********************************************************************************
#9 4.913       
#9 4.913       !!
```

**Root cause:** Requires manual investigation.

**Minimal fix:** Investigate the error above.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| ? | Unknown error — see raw output above | Investigate manually |
