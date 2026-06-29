# Benchmark: rjagerman/shoelace

**Repository:** https://github.com/rjagerman/shoelace
**Language:** Python
**Test framework:** pytest (with nose.tools assertions)

Shoelace is a learning-to-rank library built on top of Chainer. Tests cover dataset loading, evaluation metrics (NDCG, MAP, Precision), list-wise loss functions (ListMLE, ListNet), log-cumsum-exp computation, and a linear ranking network example.

---

## Dockerfile.test — Baseline (Python 3.8)

**Python version:** 3.8
**Result:** 33 passed

### Special setup

- **`nose`**: All test files import assertion helpers from `nose.tools` (e.g., `assert_almost_equal`, `assert_equal`). The `nose` package must be installed even though pytest is the test runner.

### Build and run

```bash
docker build -f Dockerfile.test -t shoelace-test .
docker run --rm shoelace-test
# Expected: 33 passed in ~1s
```

---

## Dockerfile.py313 — Failing Target (Python 3.13)

**Python version:** 3.13
**Result:** Build fails during `pip install -r requirements.txt` (chainer installation)

`chainer>=2.0.0` was released in 2017 and deprecated in 2019. Its `setup.py` uses `import pkg_resources` (from `setuptools`) without declaring `setuptools` as a build dependency in `pyproject.toml`. Python 3.13's pip no longer automatically injects `setuptools` into the build environment for old-style `setup.py` packages, causing `ModuleNotFoundError: No module named 'pkg_resources'` during wheel metadata generation.

### Build command (expected to fail)

```bash
docker build -f Dockerfile.py313 -t shoelace-py313 .
# Expected: ModuleNotFoundError: No module named 'pkg_resources'
```

---

## Errors in Dockerfile.py313

```
Getting requirements to build wheel did not run successfully.
│ exit code: 1
╰─> [23 lines of output]
    ModuleNotFoundError: No module named 'pkg_resources'

ERROR: Failed to build 'chainer' when getting requirements to build wheel
```

**Root cause:** `chainer` has an old-style `setup.py` that imports `pkg_resources` without declaring `setuptools` as a PEP 517/518 build dependency. Python 3.13's pip (23+) no longer auto-injects `setuptools` into isolated build environments, breaking any package that assumes it is available without declaring it.

**Minimal fix:** Add `setuptools` to the pip install before `chainer`, or pin a `chainer` version that has a `pyproject.toml` declaring its build deps (no such version exists — chainer was abandoned in 2019).
