# Benchmark: tudorelu/pyjuque

## Test Results (Baseline)
- **10 passed**, 1 failed
- Python 3.9 (python:3.9-slim)

## Fix Applied
- No Dockerfile changes needed — repo installs cleanly on Python 3.9. The test suite runs
  as-is with `pip install -r requirements.txt && pip install -e .`.

## Failing Tests
1 failure in `tests/test_BotController.py::TestSqliteDecimal::test_entry_exit_signal` —
`NameError: name 'defineBot' is not defined`. The test calls `defineBot(bot_config)` but
never imports that function; this is a pre-existing bug in the test code unrelated to the
Python version.

## Python 3.13 Incompatibility
`pip install -e .` fails on Python 3.13 — `setup.py` uses `bdist_wheel` and license
classifier syntax that modern setuptools (bundled with Python 3.13) no longer supports;
`self._finalize_license_expression()` raises during wheel build.

## Test Coverage
10 tests across: SQLite decimal type coercion (initial value, bind param, result value),
ORM model creation for Order/Pair/Bot tables, bot instantiation with SQLite, and bot
state queries (getActivePairs, getOpenOrders, getPair).
