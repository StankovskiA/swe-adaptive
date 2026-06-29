# Benchmark: openwisp/django-netjsongraph

**Repository:** https://github.com/openwisp/django-netjsongraph
**Language:** Python
**Test framework:** pytest + pytest-django

django-netjsongraph is a Django app for storing and visualizing network topology graphs in NetJSON format. Tests cover topology CRUD, node/link management, snapshot creation, REST API endpoints, admin views, and utility functions.

---

## Dockerfile.test — Baseline (Python 3.7)

**Python version:** 3.7
**Result:** 82 passed

### Special setup

- **`pytest-django`**: The test suite uses Django's `TestCase`; `pytest-django` is required for pytest integration.
- **`DJANGO_SETTINGS_MODULE=settings`**: Django settings are at `tests/settings.py`. Set via `pytest.ini`.
- **`PYTHONPATH=/root/code/tests`**: Makes `tests/settings.py` importable as `settings` by pytest-django.
- **`--ignore=django_netjsongraph/tests/base/`**: The `tests/base/` directory contains abstract mixin classes (`TestTopologyMixin`, `TestNodeMixin`, etc.) intended to be subclassed, not run directly. pytest collects them because they start with `Test`.
- **`-k "not Mixin"`**: Even with `tests/base/` ignored, concrete test files import the mixin classes into their module namespace (e.g., `from .base.test_topology import TestTopologyMixin`), so pytest finds them again. This filter skips all mixin classes.

### Build and run

```bash
docker build -f Dockerfile.test -t django-netjson-test .
docker run --rm django-netjson-test
# Expected: 82 passed in ~3s
```

---

## Dockerfile.py313 — Failing Target (Python 3.13)

**Python version:** 3.13
**Result:** Build fails during `pip install -r requirements.txt`

`requirements.txt` pins `openwisp-utils~=0.5.0` (released 2019). The 0.5.x releases of `openwisp-utils` were published before Python 3.13 existed and have no wheel distribution for Python 3.13. pip cannot find a compatible distribution.

### Build command (expected to fail)

```bash
docker build -f Dockerfile.py313 -t django-netjson-py313 .
# Expected: No matching distribution found for openwisp-utils~=0.5.0
```

---

## Errors in Dockerfile.py313

```
ERROR: Could not find a version that satisfies the requirement openwisp-utils~=0.5.0
  (from versions: 0.1.0a0, 0.1.0, ... 0.5, 0.5.1, 0.6, ...)
ERROR: No matching distribution found for openwisp-utils~=0.5.0
```

**Root cause:** `openwisp-utils` 0.5.x was released in 2019 and has no `cp313` wheel and no source distribution compatible with Python 3.13 (the package's own `python_requires` predates Python 3.13 classifier). Newer versions (0.6+) dropped support for the API surface this project depends on.

**Minimal fix:** Upgrade to a version of `openwisp-utils` that supports Python 3.13 and update any API call sites that changed between 0.5 and the new version.
