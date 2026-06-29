# Benchmark: datafold/sqeleton

## Test Results (Baseline)
- **28 passed**, 17 failed, 1 skipped, 2 errors
- Python 3.8 (python:3.8-slim)

## Fix Applied
- Added `git` to `apt-get install` — `tests/common.py` calls `git rev-parse` at import time.
- Skipped editable install (`pip install -e .`) due to Poetry `pyproject.toml` bug (`documentation = ""`
  must be a valid URI per poetry-core >= 1.3 validation). Used `ENV PYTHONPATH=/root/code` instead and
  installed runtime deps manually: `runtype`, `dsnparse`, `click`, `rich`, `toml`, `pytz`.

## Failing Tests
17 tests fail because they require live database connections (MySQL, PostgreSQL, DuckDB) — the
database connector modules (`mysql`, `psycopg2`, `duckdb`) are not installed in the image since
they are optional extras. 2 errors at setup also hit the same missing `mysql` module.

## Python 3.13 Incompatibility
`pip install "duckdb>=0.7.0,<0.8.0"` fails on Python 3.13 — DuckDB 0.7.x predates Python 3.13
(cp313) wheel support and has no pre-built wheel; building from source fails. The dev-dependency
in `pyproject.toml` pins `duckdb = "^0.7.0"`, so the full dev install is broken on Python 3.13.

## Test Coverage
28 tests pass across core SQL query builder functionality:
- `test_query.py` (15 tests): query building, CTE, JOINs, GROUP BY, subqueries
- `test_sql.py` (9 tests): SQL compilation for strings, integers, table names, SELECT
- `test_utils.py` (5 tests): match_like, match_regexps, number_to_human, cache, passwords
