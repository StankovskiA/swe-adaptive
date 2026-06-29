# Benchmark: SpikeInterface/spikeextractors

## Test Results (Baseline)
- **14 passed**, 31 failed (data-dependent), 1 warning
- Python 3.10 (python:3.10-slim)

## Fix Applied
Added `git` to `apt-get install` in Dockerfile.test — required by the package during install.
Added `--ignore=tests/test_gin_repo.py` to CMD to exclude GIN data download tests.

## Failing Tests
31 tests fail because they require external data files from the GIN (G-Node Infrastructure) neuroscience data repository, which requires network access and authentication to download. These are integration tests, not unit tests.

## Python 3.13 Incompatibility
`pip install -r requirements.txt` fails on Python 3.13 — several C-extension dependencies (neo, nixio, etc.) lack Python 3.13-compatible wheels.

## Test Coverage
14 pure-logic tests pass across: test_numpy_extractors (numpy array-based extractors), test_tools (probe/dat file I/O).
