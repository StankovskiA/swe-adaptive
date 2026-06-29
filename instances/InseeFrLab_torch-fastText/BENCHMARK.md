# Benchmark: InseeFrLab/torch-fastText

## Test Results (Baseline)
- **10 passed**, 0 failures
- Python 3.10 (python:3.10-slim)

## Fix Applied
- Pinned `torch<2.6` — PyTorch 2.6.0 changed `torch.load()` to use `weights_only=True` by
  default (a security change). Lightning checkpoints contain arbitrary Python objects
  (hyperparameters dict, callbacks, etc.), so loading them with `weights_only=True` raises
  `_pickle.UnpicklingError: Weights only load failed`. Installing torch<2.6 keeps the
  old `weights_only=False` default and allows `FastTextModule.load_from_checkpoint()` to
  succeed (called at line 656 in `torchFastText/torchFastText.py` after training finishes).
- Added `|| retry` pattern to NLTK stopwords download — `python -m nltk.downloader stopwords`
  makes a network call that can fail intermittently; added three attempts to handle transient
  network issues during Docker build.

## Failing Tests
0 failures on Python 3.10 with torch<2.6.

## Python 3.13 Incompatibility
On Python 3.13, `torch>=2.6` is the only available version (torch<2.6 has no Python 3.13
wheels). With torch 2.6+, `FastTextModule.load_from_checkpoint()` fails with
`_pickle.UnpicklingError: Weights only load failed` because torch 2.6 flipped the default for
`torch.load(weights_only=...)` from `False` to `True`. The `Dockerfile.py313` build fails at
`RUN pytest tests/ -v` with 1 failure (test_training) and exit code 1.

## Test Coverage
10 tests pass across: model building (all combinations of categorical embeddings, vocabulary
sizes, and feature counts), full training pipeline (train + checkpoint + reload + predict),
prediction with explanations, tokenization (NGramTokenizer subword extraction, tokenize
sentences), fastText dataset handling (dataset creation, batching), and text preprocessing.
