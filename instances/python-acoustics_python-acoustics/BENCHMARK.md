# Benchmark: python-acoustics

**Repository:** https://github.com/python-acoustics/python-acoustics
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.8)

**Docker image:** `Dockerfile.test`
**Python version:** 3.8
**Result:** 381 passed, 0 failed

All 381 tests pass on Python 3.8.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — `scipy.special.sph_harm` removed in SciPy 1.15+

```
#9 1.705 tests/standards/test_iec_61672_1_2013.py:4: in <module>
#9 1.705     from acoustics.standards.iec_61672_1_2013 import *
#9 1.705 acoustics/__init__.py:17: in <module>
#9 1.705     import acoustics.directivity
#9 1.705 acoustics/directivity.py:20: in <module>
#9 1.705     from scipy.special import sph_harm  # pylint: disable=no-name-in-module
#9 1.705     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#9 1.705 E   ImportError: cannot import name 'sph_harm' from 'scipy.special'
```

**Root cause:** `acoustics/directivity.py` imports `scipy.special.sph_harm`, a spherical harmonic function that was deprecated in SciPy 1.12 and removed in SciPy 1.15. On Python 3.13, pip resolves SciPy ≥1.15 (the oldest version with Python 3.13 wheels), which no longer exports `sph_harm`. The import fails at package load time, causing all tests that import from `acoustics` to error during collection.

**Minimal fix:** Replace `from scipy.special import sph_harm` with `from scipy.special import sph_harm_y` and `sph_harm_y` as needed, or compute it via `scipy.special.sph_harm_y` (SciPy 1.15+ replacement API).

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | `acoustics/directivity.py` imports `scipy.special.sph_harm` removed in SciPy ≥1.15; Python 3.13 resolves SciPy ≥1.15 → `ImportError` at package load time | Replace with `scipy.special.sph_harm_y` (SciPy 1.15+ API) |
