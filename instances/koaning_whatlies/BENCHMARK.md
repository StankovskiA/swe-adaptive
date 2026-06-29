# Benchmark: koaning/whatlies

## Test Results (Baseline)
- **118 passed**, 324 warnings
- Python 3.8 (python:3.8-slim)

## Fix Applied
- Added `pandas` and pinned `altair>=4.2.0,<5` before `pip install -e .` — pandas is imported directly
  by `whatlies/embeddingset.py` but was not in `install_requires`; altair 5 reorganized its module
  structure so pin to 4.x matches the codebase's API usage.
- Added `gensim~=3.8.3` before `-e .` to ensure version resolution.
- Ignored test files that require optional heavy dependencies not available in the base image:
  - `test_transformers.py`, `test_lang/test_hftransformers_lang.py` — need `transformers`
  - `test_lang/test_fasttext_lang.py`, `test_sklearn/test_fasttext_sklearn.py` — need `fasttext`
  - `test_lang/test_sent_tfm.py` — needs `sentence-transformers`
  - `test_lang/test_tfhub_lang.py`, `test_lang/test_universal_sentence_encoder.py` — need TensorFlow Hub
  - `test_documentation/` — needs docs build tools
  - `test_plotting/test_matplotlib/test_plot_3d.py`, `test_sklearn/test_simple_pipeline.py` — load
    `en_core_web_sm` at module level; spacy model download fails at build time due to SSL issues
    with raw.githubusercontent.com from inside Docker.
  - `test_plotting/test_dist_sim_plots.py` — fixture requires `FasttextLanguage`

## Python 3.13 Incompatibility
`pip install -e .` fails on Python 3.13 — `gensim~=3.8.3` (a core dependency for word embedding
language backends) fails to build its C extensions on Python 3.13. The `gensim` 3.8.x line
predates Python 3.13 and has no cp313-compatible wheel; its C extension build fails with a
metadata-generation-failed error.

## Test Coverage
118 tests pass across: core Embedding and EmbeddingSet operations, TF-IDF language backend,
CountVector language backend, gensim language backend, bpemb language backend, spaCy language
backend, matplotlib plotting (2D), altair interactive plotting, and scikit-learn transformer
pipeline integration.
