# Benchmark: rhasspy/gruut-ipa

## Test Results (Baseline)
- **28 passed**
- Python 3.10 (python:3.10-slim)
- Runtime: ~0.2 seconds

## Fix Applied
Added `numpy` to pip install in Dockerfile.test — `gruut_ipa.distances` imports numpy at module level but it was not declared as a dependency.

## Python 3.13 Incompatibility
`pip install -r requirements_dev.txt` fails on Python 3.13 due to `typed-ast` dependency — `typed-ast` has no Python 3.13 wheel (its functionality was merged into the stdlib `ast` module).

## Test Coverage
28 tests across: test_accent, test_distances, test_features, test_phone, test_phonemes, test_pronunciation.
