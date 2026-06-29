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

### Error — `yarl==1.9.2` has no Python 3.13 wheels; Cython C extension fails to build from source

```
#9 11.15   error: subprocess-exited-with-error
#9 11.15   
#9 11.15   x Building wheel for yarl (pyproject.toml) did not run successfully.
#9 11.15   | exit code: 1
#9 11.15   +-> [110 lines of output]
#9 11.15       **********************
#9 11.15       * Accelerated build *
#9 11.15       **********************
#9 11.15       ...
#9 17.52   Building wheel for yarl (pyproject.toml): finished with status 'error'
#9 18.02   ERROR: Failed building wheel for yarl
#9 18.03 x Failed to build installable wheels for some pyproject.toml based projects
```

**Root cause:** `requirements.txt` pins `yarl==1.9.2`. That release ships pre-built wheels only for Python ≤3.12 (`cp38-cp312` manylinux wheels). On Python 3.13, pip downloads the source tarball instead (`yarl-1.9.2.tar.gz`) and tries to build from source. `yarl` uses Cython to generate a C extension (`_quoting.c`) for URL quoting performance. The bundled Cython-generated C code in 1.9.2 is not compatible with the Python 3.13 C API (internal struct layouts and `_Py*` API changes), causing the C extension wheel build to fail.

**Minimal fix:** Upgrade `yarl` to `>=1.11.0` in `requirements.txt`, which ships Python 3.13 pre-built wheels and uses Cython ≥3.0-generated C code compatible with Python 3.13.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | `yarl==1.9.2` has no Python 3.13 wheels; source build of Cython C extension fails against Python 3.13 C API | Upgrade `yarl` to `>=1.11.0` in `requirements.txt` |
