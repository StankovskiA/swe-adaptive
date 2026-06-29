# Benchmark: pymultiMATIC

**Repository:** https://github.com/thomasgermain/pymultiMATIC
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.10)

**Docker image:** `Dockerfile.test`
**Python version:** 3.10
**Result:** 259 passed, 0 failed

All 259 tests pass on Python 3.10.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — unknown

```
#9 11.15   error: subprocess-exited-with-error
#9 11.15   
#9 11.15   × Building wheel for yarl (pyproject.toml) did not run successfully.
#9 11.15   │ exit code: 1
#9 11.15   ╰─> [110 lines of output]
#9 11.15       /tmp/pip-build-env-4vdnw3i5/overlay/lib/python3.13/site-packages/setuptools/dist.py:765: SetuptoolsDeprecationWarning: License classifiers are deprecated.
#9 11.15       !!
#9 11.15       
#9 11.15               ********************************************************************************
#9 11.15               Please consider removing the following classifiers in favor of a SPDX license expression:
#9 11.15       
#9 11.15               License :: OSI Approved :: Apache Software License
#9 11.15       
#9 11.15               See https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#license for details.
#9 11.15               ********************************************************************************
#9 11.15       
#9 11.15       !!
#9 11.15         self._finalize_license_expression()
#9 11.15       **********************
#9 11.15       * Accelerated build *
```

**Root cause:** Requires manual investigation.

**Minimal fix:** Investigate the error above.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| ? | Unknown error — see raw output above | Investigate manually |
