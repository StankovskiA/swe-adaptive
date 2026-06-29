# Benchmark: istresearch/traptor

## Test Results (Baseline)
- **86 passed**, 0 failed
- Python 3.8 (python:3.8-slim)

## Fix Applied
Used `python -m pytest` instead of `pytest` in CMD to ensure the installed package
(traptor) is on the Python path when running tests.

## Python 3.13 Incompatibility
`pip install -r requirements.txt` fails on Python 3.13 — a Redis or hiredis related Cython
extension fails to compile: `Error compiling Cython file` with `_syserr_cb` return type error.
The C extension has no cp313 pre-built wheel and its Cython-generated code is incompatible
with Python 3.13's C API changes.

## Test Coverage
86 tests pass across: traptor Twitter stream tracking filter maintenance, rule management,
rate limiting, offline rule matching (track/follow/locations modes), and message routing logic.
