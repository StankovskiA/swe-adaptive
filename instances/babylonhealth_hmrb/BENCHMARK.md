# Benchmark: hmrb

**Repository:** https://github.com/babylonhealth/hmrb
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.8)

**Docker image:** `Dockerfile.test`
**Python version:** 3.8
**Result:** 323 passed, 0 failed

All 323 tests pass on Python 3.8.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — unknown

```
#9 7.631   error: subprocess-exited-with-error
#9 7.631   
#9 7.631   × Building editable for hmrb (pyproject.toml) did not run successfully.
#9 7.631   │ exit code: 1
#9 7.631   ╰─> [73 lines of output]
#9 7.631       /tmp/pip-build-env-dcl_sbqi/overlay/lib/python3.13/site-packages/setuptools/dist.py:483: SetuptoolsDeprecationWarning: Cannot find any files for the given pattern.
#9 7.631       !!
#9 7.631       
#9 7.631               ********************************************************************************
#9 7.631               Pattern 'LICENSE.txt' did not match any files.
#9 7.631       
#9 7.631               By 2027-Feb-18, you need to update your project and remove deprecated calls
#9 7.631               or your builds will no longer be supported.
#9 7.631               ********************************************************************************
#9 7.631       
#9 7.631       !!
#9 7.631         for path in sorted(cls._find_pattern(pattern, enforce_match))
#9 7.631       running editable_wheel
#9 7.631       creating /tmp/pip-ephem-wheel-cache-yji43don/wheels/44/45/32/d3e940b1091f8232ad46ed69e6a343cc3d1cdc55bd12aeb96a/tmp9b0id7um/.tmp-_bwjmzj3/hmrb.egg-info
#9 7.631       writing /tmp/pip-ephem-wheel-cache-yji43don/wheels/44/45/32/d3e940b1091f8232ad46ed69e6a343cc3d1cdc55bd12aeb96a/tmp9b0id7um/.tmp-_bwjmzj3/hmrb.egg-info/PKG-INFO
```

**Root cause:** Requires manual investigation.

**Minimal fix:** Investigate the error above.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| ? | Unknown error — see raw output above | Investigate manually |
