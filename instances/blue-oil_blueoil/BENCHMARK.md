# Benchmark: blueoil

**Repository:** https://github.com/blue-oil/blueoil
**Language:** Python
**Test framework:** pytest

blueoil is a command-line framework for training and deploying deep learning models on FPGA-based edge devices, with support for Vyper/Solidity smart contracts and TensorFlow-based model quantization.

---

## Dockerfile.test — Baseline (Python 3.8)

**Python version:** 3.8
**Result:** 25 passed

### Excluded tests and reasons

| Excluded | Reason |
|----------|--------|
| `tests/unit/` (entire directory) | `tests/unit/conftest.py` imports `tensorflow` at module level — all unit tests fail to collect without TensorFlow installed |
| `test_tf_io.py` | Directly imports TensorFlow |
| `test_code_generation.py` | Transitively imports TensorFlow via `blueoil/converter/generate_project.py` → `frontend/tensorflow.py` |
| `test_binary.py` | Extends `TestCaseDLKBase` which requires a connected DE10-Nano FPGA board |
| `test_generate_project.py` | Extends `TestCaseDLKBase` — same FPGA hardware requirement |

The 6 remaining converter test files (`test_consistency_check.py`, `test_dynamic_create_op.py`, `test_graph.py`, `test_operators.py`, `test_optimizer.py`, `test_packer.py`) test the pure Python graph/operator model and quantization optimizer — no TF or hardware required.

### Build and run

```bash
docker build -f Dockerfile.test -t blueoil_test .
docker run --rm blueoil_test
# Expected: 25 passed in ~0.2s
```

---

## Dockerfile.py313 — Failing Target (Python 3.13)

**Python version:** 3.13
**Result:** Build fails at install

`matplotlib==3.3.0` (pinned in `install_requires`) uses `configparser.SafeConfigParser`, which was removed in Python 3.12. The wheel build fails immediately on Python 3.13.

### Build command (expected to fail)

```bash
docker build -f Dockerfile.py313 -t blueoil_py313 .
# Expected: AttributeError: module 'configparser' has no attribute 'SafeConfigParser'
```

---

## Errors in Dockerfile.py313

```
AttributeError: module 'configparser' has no attribute 'SafeConfigParser'.
Did you mean: 'RawConfigParser'?
note: This error originates from a subprocess, and is likely not a problem with pip.
ERROR: Failed to build 'matplotlib' when getting requirements to build wheel
```

**Root cause:** `matplotlib==3.3.0` uses the removed `configparser.SafeConfigParser` API during its wheel build. This attribute was removed in Python 3.12 (deprecated since 3.2).

**Minimal fix:** Upgrade `matplotlib` to `>=3.5.0` which removed the `SafeConfigParser` usage.
