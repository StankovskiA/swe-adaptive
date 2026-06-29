# Benchmark: danielgafni/dagster-polars

## Test Results (Baseline)
- **22 passed**, 53 failed, 5 rerun
- Python 3.10 (python:3.10-slim)

## Fix Applied
- Pinned `dagster<1.8` — in dagster 1.8+, `dagster._annotations.experimental` was renamed
  to `preview`, and `dagster.ExperimentalWarning` was renamed to `PreviewWarning`. The
  source code imports `experimental` at module level and conftest.py references
  `dagster.ExperimentalWarning`, so newer dagster breaks both.
- Installed `.[deltalake]` optional extra — `conftest.py` imports `PolarsDeltaIOManager`
  unconditionally at the top level; without the `deltalake` optional extra installed, this
  import fails and blocks all test collection.
- Added `deepdiff` — required by test files but not installed by the default `pip install -e .`.
- Pinned `pytest<8` — `pytest-cases 3.10.1` calls `pytest.IdMaker.__init__()` with 7 args,
  but pytest 8/9 changed its constructor signature; downgrading to pytest 7.x fixes this.

## Failing Tests
53 failures all trace to `write_deltalake()` receiving an unexpected `engine` keyword
argument: polars 1.x's `write_delta()` passes `engine` to `deltalake`'s `write_deltalake()`,
but `deltalake 1.6.0` does not accept that parameter. Tests affected include all delta lake
write/read tests and all `test_upath_io_managers_lazy.py` parametrized variants using
`PolarsDeltaIOManager`.

## Python 3.13 Incompatibility
`pip install -e .` fails on Python 3.13 — `dagster` (a direct dependency) has a transitive
dependency that fails to build for Python 3.13.

## Test Coverage
22 tests pass across: Parquet IO manager (write/read DataFrame, partitioned write/read,
storage metadata writing and reading), plus rerun-resilient flaky variants of the same tests.
