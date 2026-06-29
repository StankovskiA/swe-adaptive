# Benchmark: NimbleBoxAI/ChainFury

## Test Results (Baseline)
- **14 passed**, 0 failures
- Python 3.10 (python:3.10-slim)

## Fix Applied
- Added `pip install tqdm` before `pip install -e .` — `tqdm` is used by chainfury internals
  but not listed as a dependency in `pyproject.toml`, causing `ModuleNotFoundError` at import time.
- Ignored `tests/test_base_types.py` — module-level code instantiates a `Chain()` with
  edges referencing undefined nodes, raising `ValueError: Cannot have edges with only 1 node`
  at collection time before any test function runs. This is a bug in the test file itself.

## Failing Tests
0 failures. The only excluded file has a collection-time crash from invalid module-level code.

## Python 3.13 Incompatibility
`pip install -e .` fails on Python 3.13: the package's `pyproject.toml` declares
`python = ">=3.9,<3.12"`, so pip refuses to install: `Package 'chainfury' requires a different
Python: 3.13.14 not in '<3.12,>=3.9'`.

## Test Coverage
14 tests pass across: `test_base_chain2.py` (Chain topological sort validation) and
`test_getkv.py` (nested dict key-value extraction with dot notation, wildcards, two-level
keys, return values — 13 parameterised cases).
