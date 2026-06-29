# Benchmark: pyews

**Repository:** https://github.com/swimlane/pyews
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.10)

**Docker image:** `Dockerfile.test`
**Python version:** 3.10
**Result:** 8 passed, 0 failed

All 8 tests pass on Python 3.10.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — unknown

```
#9 6.007   error: subprocess-exited-with-error
#9 6.007   
#9 6.007   × Getting requirements to build wheel did not run successfully.
#9 6.007   │ exit code: 1
#9 6.007   ╰─> [4 lines of output]
#9 6.007       <string>:114: SyntaxWarning: invalid escape sequence '\.'
#9 6.007       Building lxml version 4.7.1.
#9 6.007       Building without Cython.
#9 6.007       Error: Please make sure the libxml2 and libxslt development packages are installed.
#9 6.007       [end of output]
#9 6.007   
#9 6.007   note: This error originates from a subprocess, and is likely not a problem with pip.
#9 6.007 ERROR: Failed to build 'lxml' when getting requirements to build wheel
#9 ERROR: process "/bin/sh -c pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -r requirements.txt -r test-requirements.txt  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest" did not complete successfully: exit code: 1
------
 > [5/5] RUN pip install --no-cache-dir --upgrade pip  && pip install --no-cache-dir -r requirements.txt -r test-requirements.txt  && pip install --no-cache-dir -e .  && pip install --no-cache-dir pytest:
6.007   │ exit code: 1
6.007   ╰─> [4 lines of output]
6.007       <string>:114: SyntaxWarning: invalid escape sequence '\.'
6.007       Building lxml version 4.7.1.
```

**Root cause:** Requires manual investigation.

**Minimal fix:** Investigate the error above.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| ? | Unknown error — see raw output above | Investigate manually |
