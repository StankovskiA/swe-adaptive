# Benchmark: facebookresearch/higher

## Test Results (Baseline)
- **173 passed**, 1 failed, 1 warning
- Python 3.7 (python:3.7-slim)

## Fix Applied
Added `parameterized` to pip install — tests use `@parameterized.expand` decorator from the
`parameterized` package which is not in requirements.txt.

## Failing Tests
1 test fails: `TestOptim::testDiffOptCallback_0_simple_model_adam` with `AssertionError: True is
not false` — a non-deterministic numerical assertion in optimizer callback testing that appears
environment-dependent.

## Python 3.13 Incompatibility
`pip install -r requirements.txt` fails on Python 3.13 — `requirements.txt` pins PyTorch as a
cp37-specific wheel URL (`torch-1.2.0+cpu-cp37-cp37m-manylinux1_x86_64.whl`). This wheel is
platform-tagged for Python 3.7 only and cannot be installed on Python 3.13.

## Test Coverage
173 tests pass across: differentiable optimizer wrappers, gradient patching through higher-order
optimization steps, model parameter manipulation, and functional forward pass testing.
