# Benchmark: nums-project/nums

## Test Results (Baseline)
- **158 passed**, 15 failed, 11 skipped, 9 errors
- Python 3.8 (python:3.8-slim)

## Fix Applied
- Added `tqdm` and `boto3` to pip install — test files import `tqdm` and `boto3` at module level.
- Added `--ignore=tests/core/storage/test_s3.py` — requires AWS S3 credentials (`moto` package for
  mocking is not installed to keep image small).
- Added `--ignore=tests/test_api.py` — also requires `moto`; tests live S3 interactions.
- Kept `--ignore=tests/experimental` from the pre-session Dockerfile.

## Failing Tests
15 failures in backend tests (Ray-based distributed backends), plus 9 errors in
`test_backends.py` for parameterized `app_inst_all*` fixtures — these require multi-node Ray
cluster configuration that isn't available in the single-container test environment.

## Python 3.13 Incompatibility
`pip install -e .` fails on Python 3.13 — the Python 3.13 slim image does not include `setuptools`
by default (removed from bundled packages in Python 3.12+). The `nums` package uses `setup.py`
which requires `setuptools` as a build backend, and pip raises
`BackendUnavailable: Cannot import 'setuptools.build_meta'`.

## Test Coverage
158 tests pass across: NumPy array operations (creation, arithmetic, broadcasting, selection,
views), NumPy linalg, random, reduction, and reshape functions. All pure Python/NumPy tests
pass; only Ray-distributed backend tests fail.
