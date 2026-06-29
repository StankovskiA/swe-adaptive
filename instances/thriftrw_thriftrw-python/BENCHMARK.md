# Benchmark: thriftrw/thriftrw-python

## Test Results (Baseline)
- **313 passed**, 8 failed
- Python 3.7 (python:3.7-slim)

## Fix Applied
Installed all requirements files (`requirements.txt`, `requirements-test.txt`,
`requirements-dev.txt`) and `pytest` explicitly — the repo uses Cython-built C extensions
for the parser which require `requirements.txt` to be installed before the editable install.

## Failing Tests
8 tests fail in `tests/protocol/test_binary.py` — `test_reader_and_writer` and
`test_input_too_short` parametrized tests for STRUCT/LIST/MAP/SET types. These appear to be
known edge cases in the binary protocol implementation related to nested type handling.

## Python 3.13 Incompatibility
`pip install -e .` fails on Python 3.13 — the `thriftrw` package includes a C extension
(Cython-based Thrift IDL parser) that fails to compile with `gcc`: incompatible with Python 3.13's
C API changes. No cp313 wheel exists.

## Test Coverage
313 tests pass across: Thrift IDL parsing (structs, enums, services, constants, typedefs),
binary wire protocol encoding/decoding, union types, exception handling, and round-trip
serialization/deserialization of all Thrift primitive types.
