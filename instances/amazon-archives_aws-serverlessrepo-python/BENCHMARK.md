# Benchmark: amazon-archives/aws-serverlessrepo-python

## Test Results (Baseline)
- **63 passed**, 0 failed
- Python 3.9 (python:3.9-slim)

## Fix Applied
Added `mock` to pip install in Dockerfile.test — tests import `from unittest.mock import ...` through
the `mock` compatibility shim.

## Python 3.13 Incompatibility
`pip install -e .` fails on Python 3.13 — `pyyaml` (pinned in setup.py requirements) fails to build
because the old Cython-based `_yaml` extension hits `AttributeError: 'build_ext' object has no
attribute 'cython_sources'`. PyYAML 5.x has no cp313 wheel and its Cython-based build is broken
with modern setuptools on Python 3.13.

## Test Coverage
63 tests pass across all unit tests:
- `test_publish.py`: SAR application publish/update/create workflows, template parsing, client mocking
- Full unit test suite passes with zero failures on Python 3.9.
