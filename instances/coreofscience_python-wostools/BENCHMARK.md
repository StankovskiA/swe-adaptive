# Benchmark: python-wostools

**Repository:** https://github.com/coreofscience/python-wostools
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.7)

**Docker image:** `Dockerfile.test`
**Python version:** 3.7
**Result:** 26 passed, 0 failed

All 26 tests pass on Python 3.7.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — unknown

```
#9 14.84   error: subprocess-exited-with-error
#9 14.84   
#9 14.84   × Preparing editable metadata (pyproject.toml) did not run successfully.
#9 14.84   │ exit code: 1
#9 14.84   ╰─> [7 lines of output]
#9 14.84       /tmp/pip-build-env-a_d15vs8/overlay/lib/python3.13/site-packages/setuptools/_distutils/dist.py:287: UserWarning: Unknown distribution option: 'test_suite'
#9 14.84         warnings.warn(msg)
#9 14.84       /tmp/pip-build-env-a_d15vs8/overlay/lib/python3.13/site-packages/setuptools/_distutils/dist.py:287: UserWarning: Unknown distribution option: 'tests_require'
#9 14.84         warnings.warn(msg)
#9 14.84       error in wostools setup command: 'install_requires' must be a string or iterable of strings containing valid project/version requirement specifiers; Expected comma (within version specifier), semicolon (after version specifier) or end
#9 14.84           Click>=7.0<8
#9 14.84                ~~~~~^
#9 14.84       [end of output]
#9 14.84   
#9 14.84   note: This error originates from a subprocess, and is likely not a problem with pip.
#9 14.84 error: metadata-generation-failed
#9 14.84 
#9 14.84 × Encountered error while generating package metadata.
#9 14.84 ╰─> from file:///root/code
#9 14.84
```

**Root cause:** Requires manual investigation.

**Minimal fix:** Investigate the error above.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| ? | Unknown error — see raw output above | Investigate manually |
