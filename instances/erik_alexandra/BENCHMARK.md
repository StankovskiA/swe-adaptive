# Benchmark: erik/alexandra

**Repository:** https://github.com/erik/alexandra
**Language:** Python
**Test framework:** pytest

alexandra is a Python toolkit for writing Amazon Alexa skills as web services. Tests cover app routing, session handling, request validation, and certificate verification.

---

## Dockerfile.test — Baseline (Python 3.7)

**Python version:** 3.7
**Result:** 17 passed, 1 skipped, 1 deselected

### Excluded tests

| Excluded | Reason |
|----------|--------|
| `test_good_url_expired_cert` | Makes a live HTTPS request to `s3.amazonaws.com` to download an Amazon Alexa cert; the network request fails inside Docker (no outbound S3 access), so the test errors rather than testing the cert-expiry logic |
| `test_request_validation` | Already marked `@pytest.mark.skip` in the repo — the comment in the code says "this test is disabled due to echo-api-cert-4 having expired" |

### Build and run

```bash
docker build -f Dockerfile.test -t alexandra-test .
docker run --rm alexandra-test
# Expected: 17 passed, 1 skipped in ~0.3s
```

---

## Dockerfile.py313 — Failing Target (Python 3.13)

**Python version:** 3.13
**Result:** Build fails during `pip install -r requirements.txt`

`requirements.txt` pins `cffi==1.11.5` (2018). Building this wheel requires compiling a C extension that uses deprecated CPython internals incompatible with Python 3.13.

### Build command (expected to fail)

```bash
docker build -f Dockerfile.py313 -t alexandra-py313 .
# Expected: error: Building wheel for cffi (pyproject.toml) did not run successfully
```

---

## Errors in Dockerfile.py313

```
× Building wheel for cffi (pyproject.toml) did not run successfully.
│ exit code: 1
```

**Root cause:** `requirements.txt` pins `cffi==1.11.5`, released in 2018. The C extension in this version uses CPython internals that were removed or changed in Python 3.13. `cffi` was updated to support Python 3.12+ only in version 1.16+.

**Minimal fix:** Remove the version pin on `cffi` in `requirements.txt` to allow `pip` to install `cffi>=1.16`.
