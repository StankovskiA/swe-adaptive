# Benchmark: Protean-Labs/subgrounds

## Status: GRADUATED

## Test Results

- **Python version:** 3.10 (python:3.10-slim)
- **Tests collected:** 161
- **Tests passed:** 161
- **Tests failed:** 0
- **Exit code:** 0

## Fix Applied

**Problem:** `pandas ^1.4.2` (which resolves to 1.5.3) has pre-compiled C extensions that are incompatible with numpy 2.x. When pip resolves dependencies, it installs the latest numpy (2.x) which breaks the pandas C-extension import.

**Error:**
```
ImportError: pandas/_libs/interval.pyx: init pandas._libs.interval
```

**Fix:** Pin numpy and pandas to compatible versions before the package install in `Dockerfile.test` and `Dockerfile.py313`:
```dockerfile
RUN pip install --no-cache-dir "numpy<2" "pandas>=1.4.2,<2"
```

This forces numpy 1.26.4 and pandas 1.5.3, which are binary-compatible.

## Dockerfile Verification

- `Dockerfile.test`: Uses `CMD` to run tests (correct)
- `Dockerfile.py313`: Uses `RUN` to run tests (correct)
