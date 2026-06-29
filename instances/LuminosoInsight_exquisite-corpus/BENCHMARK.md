# Benchmark: LuminosoInsight/exquisite-corpus

## Test Results (Baseline)
- **46 passed**, 6 failed
- Python 3.8 (python:3.8-slim)

## Fix Applied
No additional fixes needed beyond standard pip install — the package installs cleanly on Python 3.8.

## Failing Tests
6 tests fail in `test_wordfreq_build.py::test_text_result_same_as_reference` — diff comparisons
of word frequency output files vs. reference files. Platform-specific hash ordering or numeric
precision differences cause slight variations in the computed frequency outputs (specifically
for Chinese text processing with `zh.txt` and `zh-Hans.txt`).

## Python 3.13 Incompatibility
`pip install -e .` fails on Python 3.13 — `snakemake` (a workflow management dependency) uses
`configparser.SafeConfigParser` which was removed in Python 3.13 (it was deprecated in Python 3.2
and removed after a long deprecation period). The `snakemake` package setup script crashes during
installation.

## Test Coverage
46 tests pass across: language detection, tokenization, unicode normalization, text cleaning,
multilingual word frequency list building, and corpus pipeline utilities.
