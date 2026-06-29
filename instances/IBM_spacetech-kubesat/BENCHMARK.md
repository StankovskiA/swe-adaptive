# Benchmark: IBM/spacetech-kubesat

**Repository:** https://github.com/IBM/spacetech-kubesat
**Language:** Python
**Test framework:** pytest (asyncio)

spacetech-kubesat is a satellite simulation and coordination framework. Tests cover base service, base simulation, NATS messaging, logging, Orekit orbital mechanics, and JSON schema validation.

---

## Dockerfile.test — Baseline (Python 3.8)

**Python version:** 3.8
**Result:** 12 passed

### Excluded tests

| Excluded | Reason |
|----------|--------|
| `test_orekit.py` | Requires the Orekit orbital mechanics library (`orekit`), a Java-based package requiring a JVM; not installable via pip |
| `test_nats_handler.py` (8 tests) | Tests connect to a NATS message broker server; `ErrNoServers` error when no NATS server is running; NATS server binary not available in apt |

### Special setup

- `tests/` and `pytest.ini` were excluded from the Docker build context by `.dockerignore` — removed those exclusions so the test files are copied into the image.

### Build and run

```bash
docker build -f Dockerfile.test -t kubesat-test .
docker run --rm kubesat-test
# Expected: 12 passed in ~1s
```

---

## Dockerfile.py313 — Failing Target (Python 3.13)

**Python version:** 3.13
**Result:** Build fails during `pip install -e .`

`setup.py` pins `numpy==1.19.0` (2020). Building this wheel fails on Python 3.13 because numpy 1.19.0 uses `setup.py` conventions and CPython internals removed in Python 3.13.

### Build command (expected to fail)

```bash
docker build -f Dockerfile.py313 -t kubesat-py313 .
# Expected: error preparing metadata for numpy==1.19.0
```

---

## Errors in Dockerfile.py313

```
× Preparing metadata (pyproject.toml) did not run successfully.
│ exit code: 1
Running from numpy source directory.
```

**Root cause:** `numpy==1.19.0` uses a `setup.py` that embeds Cython code generation and relies on CPython internals changed in Python 3.13. NumPy added Python 3.13 support only in numpy 2.1+.

**Minimal fix:** Remove the `numpy==1.19.0` pin and allow `numpy>=1.20` in `setup.py`.
