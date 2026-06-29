# Benchmark: microsoft/AdaMix

## Test Results (Baseline)
- **1542 passed**, 224 failed, 4564 skipped, 39 collection errors
- Python 3.9 (python:3.9-slim)

## Fix Applied
- Pinned `packaging<22` before `pip install -e .` — the transformers
  `dependency_versions_check.py` calls `version.parse()` on version specifier strings like
  `'0.10.1,<0.11'`. `packaging` v22 removed `LegacyVersion`, so non-PEP 440 strings now
  raise `InvalidVersion`. Pinning to v21.x restores the `LegacyVersion` fallback.
- Added `--continue-on-collection-errors` to the pytest CMD — several test files fail at
  collection (e.g., `test_logging.py`, `test_skip_decorators.py`) due to
  `AttributeError: module 'unittest' has no attribute 'mock'` in class-level decorators;
  without this flag, any single collection error causes pytest to abort entirely.

## Failing Tests
224 failures and 39 collection errors, all from tests that require PyTorch, TensorFlow,
or Flax (none of which are installed in the baseline image). The 4564 skipped tests are
those decorated with `@require_torch`, `@require_tf`, etc. Collection errors affect test
files that use `mockenv()` (which calls `unittest.mock` without importing it) or require
live HuggingFace Hub API tokens.

## Python 3.13 Incompatibility
`pip install -e .` fails on Python 3.13 — `tokenizers<0.11,>=0.10.1` (required by
`transformers==4.4.2`) has no Python 3.13 wheel on PyPI. Building from source requires a
Rust toolchain:
`Building wheel for tokenizers (pyproject.toml): finished with status 'error'`

## Test Coverage
1542 tests pass across tokenization (BERT, RoBERTa, GPT-2, XLNet, ALBERT, DistilBERT,
ELECTRA, etc. — slow Python tokenizers without C extensions), HuggingFace argparser,
model output dataclasses, version utility checks, configuration serialization/
deserialization, data collator variants, and model card utilities.
