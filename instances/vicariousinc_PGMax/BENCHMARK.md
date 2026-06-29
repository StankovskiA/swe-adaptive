# Benchmark: vicariousinc/PGMax

## Test Results (Baseline)
- **21 passed**, 1 failed
- Python 3.10 (python:3.10-slim)

## Fix Applied
- No Dockerfile changes needed — the package installs cleanly on Python 3.10 and all but
  one test run offline without any patching.

## Failing Test
`tests/vgroup/test_vgroup.py::test_variable_dict` — `AttributeError: module 'jax.tree_util'
has no attribute 'tree_multimap'`. The `jax.tree_util.tree_multimap` API was removed in
JAX 0.4.1 (deprecated in 0.3.x). The test uses this removed function directly; it is a
pre-existing incompatibility between the test code and current JAX, not a Python version
issue.

## Python 3.13 Incompatibility
`pip install -e .` fails on Python 3.13 with a hard version gate from the package's own
metadata: `Package 'pgmax' requires a different Python: 3.13.14 not in '<3.11,>=3.7'`.
The package explicitly declares `python_requires=">=3.7,<3.11"`.

## Test Coverage
21 tests across: variable group types (VarArray, VarDict, NDVarArray, HeteroVarArray) —
construction, indexing, flattening/unflattening, shape inference, neighbour counting, and
GPU device placement checks.
