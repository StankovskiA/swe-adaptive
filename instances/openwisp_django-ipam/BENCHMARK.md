# Benchmark: openwisp/django-ipam

**Repository:** https://github.com/openwisp/django-ipam
**Language:** Python
**Test framework:** pytest + pytest-django

django-ipam is a Django app for IP address management (IPAM). Tests cover subnet models, IP address CRUD, REST API endpoints, admin interface, and CSV import/export commands.

---

## Dockerfile.test — Baseline (Python 3.8)

**Python version:** 3.8
**Result:** 69 passed

### Special setup

- **`pytest-django`**: The test suite uses Django's `TestCase` class; `pytest-django` is required to integrate it with pytest.
- **`DJANGO_SETTINGS_MODULE=settings`**: Django settings are at `tests/settings.py`. Set via `pytest.ini`.
- **`PYTHONPATH=/root/code/tests`**: Makes `tests/settings.py` importable as `settings` by pytest-django.
- **Tests in `django_ipam/tests/`**: The `tests/` directory at the repo root is a Django project skeleton (settings, urls, wsgi), not the actual test files. The real tests are in `django_ipam/tests/`.

### Excluded tests

| Excluded | Reason |
|----------|--------|
| `test_unavailable_ip`, `test_unavailable_request_ip` (test_models.py) | Pre-existing bug: Python 3.8 `ipaddress.IPv4Network('10.0.0.0/32').hosts()` returns `[10.0.0.0]`, but tests expect `None`. The tests assume no IPs exist in a `/32` subnet, contradicting Python's standard library behavior for host routes. |
| `test_unvailable_request_api` (test_api.py) | Same root cause as above (note: typo "unvailable" in original test name). |

### Build and run

```bash
docker build -f Dockerfile.test -t django-ipam-test .
docker run --rm django-ipam-test
# Expected: 69 passed in ~7s
```

---

## Dockerfile.py313 — Failing Target (Python 3.13)

**Python version:** 3.13
**Result:** Build fails during `pip install -e .`

`django_ipam/__init__.py` defines `VERSION = (0, 1, 0, 'alpha')` and a `get_version()` function that produces the string `'0.1 alpha'`. Python 3.13 ships with `setuptools >= 70` which strictly enforces PEP 440 version formatting. The string `'0.1 alpha'` is not PEP 440 compliant (correct format would be `0.1a0` or `0.1.0a0`).

### Build command (expected to fail)

```bash
docker build -f Dockerfile.py313 -t django-ipam-py313 .
# Expected: packaging.version.InvalidVersion: Invalid version: '0.1 alpha'
```

---

## Errors in Dockerfile.py313

```
packaging.version.InvalidVersion: Invalid version: '0.1 alpha'
ERROR: Failed to build 'file:///root/code' when getting requirements to build editable
```

**Root cause:** `django_ipam/get_version()` returns `'0.1 alpha'` (with a space, not PEP 440 format). Python 3.13's bundled setuptools 70+ raises `InvalidVersion` on non-compliant version strings, blocking `pip install -e .`.

**Minimal fix:** Change `VERSION = (0, 1, 0, 'alpha')` and update `get_version()` to produce a PEP 440 compliant string such as `0.1.0a0`.
