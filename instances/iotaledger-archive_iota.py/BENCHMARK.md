# Benchmark: iotaledger-archive/iota.py

## Test Results (Baseline)
- **826 passed**, 4 warnings
- Python 3.10 (python:3.10-slim)
- Runtime: ~72 seconds

## Fix Applied
Added `aiounittest` to pip install in Dockerfile.test — test collection failed with `ModuleNotFoundError: No module named 'aiounittest'` without it.
Also added `"phx-class-registry<5"` to avoid a class-registry version conflict.

## Python 3.13 Incompatibility
`pip install -e .` fails on Python 3.13 due to `pysha3` C extension build failure — `pysha3` has no Python 3.13-compatible wheel and its C code uses deprecated Python APIs removed in 3.13.

## Test Coverage
826 tests across: adapter, api, codecs, commands (core + extended), crypto, multisig subdirectories.
