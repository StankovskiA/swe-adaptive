# Benchmark: keusuanl-sec/Ciphey

## Test Results (Baseline)
- **61 passed**, 2 skipped
- Python 3.9 (python:3.9-slim)

## Fix Applied
None. The original Dockerfile.test works as-is.

## Failing Tests
None. The 2 skipped tests are decorated with `@pytest.mark.skip` in the source.

## Python 3.13 Incompatibility
`pip install -e .` fails on Python 3.13 — `ciphey` requires `cipheycore<0.4.0,>=0.3.2`,
a Rust-based C extension dependency that only has a wheel for version 0.0.1 on PyPI (which
does not satisfy the `>=0.3.2` constraint). No Python 3.13 compatible wheel for
`cipheycore` exists:
`ERROR: No matching distribution found for cipheycore<0.4.0,>=0.3.2`

## Test Coverage
61 tests pass across: advanced cipher decoding (Atbash, Bases 32/58/62/64/65/85/91/92,
Binary, Braille, Caesar shift, Dvorak, Galactic alphabet, Gematria, Hexadecimal, Morse,
MTAP, NATO phonetic, Octal, Pig Latin, Postfix, ROT47, Soundex, Tap Code, URL encoding,
UUencode, Vigenere, XAndY), quadgram scoring with spacing variants, quick-detect modes
(Base32, Base58 Ripple, IP address greppable, visual output), and regex pattern matching
(IP address, domain, Bitcoin address).
