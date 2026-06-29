# Benchmark: target/matrixprofile-ts

## Test Results (Baseline)
- **96 passed**, 0 failed, 2 warnings
- Python 3.8 (python:3.8-slim)

## Fix Applied
- Changed WORKDIR from `/root/code` to `/app` — Python's standard library contains a
  module named `code`; when the working directory is named `code`, pytest tries to import
  tests as `code.tests.*` and fails with
  `ModuleNotFoundError: No module named 'code.tests'; 'code' is not a package`.
  Renaming the WORKDIR to `/app` eliminates the namespace collision.

## Failing Tests
None — all 96 collected tests pass.

## Python 3.13 Incompatibility
`pip install -r requirements.txt` fails on Python 3.13 — `numpy` (the core numerical
dependency) fails metadata generation:
`× Encountered error while generating package metadata.`
`╰─> numpy`
The pinned numpy version in requirements.txt has no Python 3.13 wheel and its C extension
build fails under the newer compiler/build tools in the 3.13 slim image.

## Test Coverage
96 tests across: matrix profile computation (stomp, scrimp, scrimp++), sliding dot
products, MASS distance computation, regime detection (FLUSS/FLOSS), annotation vectors,
and utility functions — covering both self-join and AB-join variants with odd/even query
lengths and edge cases.
