# Benchmark: mamba

**Repository:** https://github.com/arjunaskykok/mamba
**Language:** Python
**Test framework:** pytest

mamba is a development framework for writing, testing, and deploying smart contracts written in Vyper and Solidity, with integrated web3.py support.

---

## Dockerfile.test — Baseline (Python 3.9)

**Python version:** 3.9
**Result:** 16 passed, 8 deselected

### Excluded tests and reasons

| Excluded | Reason |
|----------|--------|
| `test/test_compile.py` (entire file) | Requires `vyper` and `solc` compilers to be installed as system binaries |
| `test_pin_manifest` | Calls IPFS `pin_manifest()` — requires a live IPFS node |
| `test_install`, `test_list`, `test_uninstall`, `test_load`, `test_get_abi` | Call GitHub API (`https://api.github.com/...`) to download an EthPM manifest |
| `test_get_contract_object`, `test_get_contract_with_parameters_object` | Require Vyper compiler binary |

### Special setup

- No `setup.py` or `[build-system]` in `pyproject.toml` (Poetry format only) — `pip install -e .` is skipped; the package root is added to `PYTHONPATH` instead.
- `typing_extensions>=4.1` is pinned after `requirements.txt` install because `py-evm==0.4.0a4` pulls in an older version that is incompatible with the vendored `typeguard` in modern setuptools.

### Build and run

```bash
docker build -f Dockerfile.test -t mamba_test .
docker run --rm mamba_test
# Expected: 16 passed, 8 deselected in ~1s
```

---

## Dockerfile.py313 — Failing Target (Python 3.13)

**Python version:** 3.13
**Result:** Build fails at install

`py-evm==0.4.0a4` depends on `blake2b-py<0.2,>=0.1.4`. All versions of `blake2b-py` that satisfy this range (`0.1.2`, `0.1.3`) require Python `<3.11`, so pip cannot find a compatible distribution on Python 3.13.

### Build command (expected to fail)

```bash
docker build -f Dockerfile.py313 -t mamba_py313 .
# Expected: ERROR: No matching distribution found for blake2b-py<0.2,>=0.1.4
```

---

## Errors in Dockerfile.py313

```
ERROR: Ignored the following versions that require a different python version:
  0.3.0 Requires-Python >=3.7,<3.10; 0.3.1 Requires-Python >=3.7,<3.10;
  0.3.2 Requires-Python >=3.7,<3.11; ... 6.0.0b4 Requires-Python >=3.7.2,<3.11
ERROR: Could not find a version that satisfies the requirement blake2b-py<0.2,>=0.1.4
       (from py-evm) (from versions: 0.1.2, 0.1.3, 0.2.2, 0.3.0, 0.3.1, 0.3.2)
ERROR: No matching distribution found for blake2b-py<0.2,>=0.1.4
```

**Root cause:** `py-evm==0.4.0a4` requires `blake2b-py<0.2`, and all versions of `blake2b-py` in that range are capped at Python `<3.11`.

**Minimal fix:** Upgrade `py-evm` to a version that supports Python 3.13 (≥6.0.0), but this requires significant dependency updates across `web3`, `eth-tester`, and the project's own code.
