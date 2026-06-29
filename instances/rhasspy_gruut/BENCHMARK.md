# Benchmark: rhasspy/gruut

## Test Results (Baseline)
- **92 passed**, 0 failed, 1 warning
- Python 3.8 (python:3.8-slim)

## Fix Applied
- Added all 12 missing gruut language data packages to the Dockerfile:
  `gruut_lang_ar`, `gruut_lang_cs`, `gruut_lang_de`, `gruut_lang_es`, `gruut_lang_fa`,
  `gruut_lang_fr`, `gruut_lang_it`, `gruut_lang_nl`, `gruut_lang_pt`, `gruut_lang_ru`,
  `gruut_lang_sv`, `gruut_lang_sw`.
  The baseline `requirements.txt` only installs `gruut_lang_en`; without the other language
  packages, 16 tests in `test_fr.py` (2) and `test_sqlite_phonemizer.py` (14) return empty
  phoneme lists (`None`/`[]`) instead of expected IPA strings.

## Failing Tests
None — all 92 collected tests pass.

## Python 3.13 Incompatibility
`pip install -r requirements.txt` fails on Python 3.13 — `libwapiti` (a CRF tagger C
extension required by `python-crfsuite`, listed in `requirements.txt`) has no Python 3.13
wheel on PyPI and its C extension fails to build:
`Failed to build libwapiti`
`× Failed to build installable wheels for some pyproject.toml based projects`

## Test Coverage
92 tests across: English text processing (numbers, dates, times, abbreviations, punctuation,
spell-out, replacements, SSML tags, word breaks, phonemization), French liaison rules,
G2P (grapheme-to-phoneme) model inference, golden rule phoneme tests, part-of-speech
tagging, SQLite-based phonemizer for 13 languages (ar, cs, de, en, es, fa, fr, it, nl, pt,
ru, sv, sw), SSML document parsing, and multi-language text processor integration tests.
