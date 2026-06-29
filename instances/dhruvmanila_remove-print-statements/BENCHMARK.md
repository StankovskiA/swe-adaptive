# Benchmark: remove-print-statements

**Repository:** https://github.com/dhruvmanila/remove-print-statements
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.10)

**Docker image:** `Dockerfile.test`
**Python version:** 3.10
**Result:** 41 passed, 0 failed

All 41 tests pass on Python 3.10.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — unknown

```
#9 6.159   error: subprocess-exited-with-error
#9 6.159   
#9 6.159   × Building wheel for libcst (pyproject.toml) did not run successfully.
#9 6.159   │ exit code: 1
#9 6.159   ╰─> [423 lines of output]
#9 6.159       /tmp/pip-build-env-cmsjsd2r/overlay/lib/python3.13/site-packages/setuptools/_distutils/dist.py:287: UserWarning: Unknown distribution option: 'test_suite'
#9 6.159         warnings.warn(msg)
#9 6.159       toml section missing PosixPath('pyproject.toml') does not contain any of the tool sections: ['setuptools_scm', 'vcs-versioning']
#9 6.159       toml section missing PosixPath('pyproject.toml') does not contain any of the tool sections: ['setuptools_scm', 'vcs-versioning']
#9 6.159       /tmp/pip-build-env-cmsjsd2r/overlay/lib/python3.13/site-packages/setuptools/config/_apply_pyprojecttoml.py:82: SetuptoolsDeprecationWarning: `project.license` as a TOML table is deprecated
#9 6.159       !!
#9 6.159       
#9 6.159               ********************************************************************************
#9 6.159               Please use a simple string containing a SPDX expression for `project.license`. You can also use `project.license-files`. (Both options available on setuptools>=77.0.0).
#9 6.159       
#9 6.159               By 2027-Feb-18, you need to update your project and remove deprecated calls
#9 6.159               or your builds will no longer be supported.
#9 6.159       
#9 6.159               See https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#license for details.
#9 6.159               ********************************************************************************
```

**Root cause:** Requires manual investigation.

**Minimal fix:** Investigate the error above.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| ? | Unknown error — see raw output above | Investigate manually |
