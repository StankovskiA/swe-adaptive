# Benchmark: dungdm93/sqlalchemy-trino

## Overview

This benchmark validates that the `sqlalchemy-trino` library test suite runs correctly on Python 3.8 and fails to build on Python 3.13.

## Baseline Environment

- **Python version**: 3.8 (python:3.8-slim Docker image)
- **Dockerfile**: `Dockerfile.test`
- **Docker image tag**: `sqltrino-test`

## Problem (Pre-fix)

Tests failed at collection time with:

```
ModuleNotFoundError: No module named 'assertpy'
```

The `assertpy` assertion library was used in tests but not installed in the test environment.

## Fix Applied

Added `pip install --no-cache-dir assertpy` to the `RUN` step in `Dockerfile.test`:

```dockerfile
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt \
 && pip install --no-cache-dir -e . \
 && pip install --no-cache-dir pytest \
 && pip install --no-cache-dir assertpy
```

Tests are run via `CMD ["pytest", "tests/", "-v"]` (not `RUN`) so they execute at container run time, not build time.

## Test Results (Python 3.8)

- **Total tests collected**: 88
- **Tests passed**: 88
- **Tests failed**: 0
- **Test files**: `tests/test_compiler.py`, `tests/test_datatype_parse.py`, `tests/test_datatype_split.py`, `tests/test_dialect.py`

All 88 tests pass successfully.

## Python 3.13 Incompatibility

- **Dockerfile**: `Dockerfile.py313`
- **Docker image tag**: `sqltrino-py313`
- **Result**: Build fails at the `RUN pip install` step

### Failure Reason

The build fails during `pip install -e .` because the newer `setuptools` shipped with Python 3.13 enforces stricter package discovery rules. It detects multiple top-level packages (`sqlalchemy_trino` and `tests`) and aborts with:

```
multiple top-level packages discovered in a flat-layout: ['sqlalchemy_trino', 'tests']
...
ERROR: Failed to build 'file:///root/code' when getting requirements to build editable
```

This is a build-time failure (exit code 1 in the `RUN` layer), not a runtime failure — the image cannot be created at all on Python 3.13.

## Benchmark Verdict

- **Passes threshold**: YES (88 >= 10)
- **Python 3.13 fails at build time**: YES
- **Status**: VALIDATED
