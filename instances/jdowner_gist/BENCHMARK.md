# Benchmark: jdowner/gist

## Test Results (Baseline)
- **64 passed**, 0 failed
- Python 3.9 (python:3.9-slim)

## Fix Applied
- Added `gnupg` to apt-get — tests for GPG-encrypted gists require the `gnupg` binary.
- Added `responses` to pip install — tests mock the GitHub API with the `responses` library.

## Python 3.13 Incompatibility
`pip install -r requirements-dev.txt` fails on Python 3.13 — `typed-ast` (a static analysis
dependency via mypy/black) fails to build from source: the C extension requires the `code.h`
system header which is missing in the slim image, and more fundamentally, `typed-ast` was
deprecated for Python 3.8+ and has no cp313 wheel.

## Test Coverage
64 tests pass across: GitHub Gist API operations (list, create, content fetch), config file
parsing, personal access token validation, and GPG encryption/decryption integration with gists.
