# Benchmark: COALAIP/pycoalaip

## Test Results (Baseline)
- **152 passed**, 224 failed, 52 skipped, 1 error
- Python 3.8 (python:3.8-slim)

## Fix Applied
- Pinned `attrs>=16.2.0,<19.2.0` — pytest 3.4.2 uses `attr.ib(convert=...)` which was removed in
  attrs 19.2.0 (renamed to `converter`). Must pin old attrs to allow pytest to initialize.
- Pinned `pytest==3.4.2` — the test suite uses the deprecated `mark.skip(tuple)` syntax inside
  `@pytest.mark.parametrize`, which was removed in pytest 3.5. Newer pytest raises
  `TypeError: object of type 'MarkDecorator' has no len()` during collection.
- Replaced `requirements_dev.txt` install with direct `pytest pytest-cov pytest-mock` install to
  avoid `pip==9.0.1` in requirements_dev.txt (which requires Python 2-era pip).

## Failing Tests
224 tests fail due to `attr.exceptions.FrozenInstanceError` in `coalaip/utils.py:30`. The
`PostInitImmutable` mixin checks `isinstance(current_value, attr.Attribute)` to allow post-init
assignment; with attrs 17.x, class-level attribute access no longer returns `attr.Attribute`
instances for uninitialized fields, causing premature `FrozenInstanceError` when the test suite
uses `pytest-mock` to patch object attributes.

## Python 3.13 Incompatibility
`pip install -r requirements_dev.txt` fails on Python 3.13 — the pinned `pip==9.0.1` in
requirements_dev.txt imports the `cgi` module which was removed from Python's standard library in
Python 3.13.

## Test Coverage
152 tests pass across: COALA IP registration/transfer workflows, plugin interface validation,
data format conversion (JSON/JSONLD), and entity model tests that don't involve post-init mutation.
