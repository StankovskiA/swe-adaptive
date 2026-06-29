# Benchmark Setup

This benchmark assesses an agent's ability to update a Python project's dependencies
and source code to support a newer Python version.

## Project

[drf-openapi-tester](https://github.com/snok/drf-openapi-tester) is a Django REST
Framework test utility that validates API responses against their OpenAPI schema
documentation. It uses a set of pinned dependencies (`poetry.lock`) that were written
targeting Python 3.7–3.10.

---

## Dockerfile.test — Baseline (Python 3.10)

`Dockerfile.test` establishes the working baseline. It builds and runs the full
test suite on **Python 3.10-slim**, with 177 tests passing and no pre-existing
failures.

### What it does

1. **Include README.md in the build context** — `pyproject.toml` declares
   `readme = "README.md"`, so Poetry refuses to install the project package
   (`drf-openapi-tester`) without it. The COPY step was updated to include
   `README.md` alongside `pyproject.toml` and `poetry.lock`.

2. **Install both optional extras** — `test_project/settings.py` lists both
   `drf_yasg` and `drf_spectacular` in `INSTALLED_APPS`. Poetry must be invoked
   with `--extras "drf-spectacular drf-yasg"` so those packages are installed and
   Django's app registry can load at test time.

### Running

```bash
docker build -f Dockerfile.test -t drf-openapi-tester-test .
docker run --rm drf-openapi-tester-test bash -c "cd /root/code && pytest tests/ -q"
```

### Expected result

```
177 passed in 14.65s
```

---

## Dockerfile.py313 — Failing Target (Python 3.13)

`Dockerfile.py313` attempts a straightforward install of the project on
**Python 3.13** without any workarounds. It is expected to fail at build time.
This is the starting point for the benchmark task.

### Running

```bash
docker build -f Dockerfile.py313 -t drf-openapi-tester-py313 .
```

### Expected result

The build fails during `poetry install --extras "drf-spectacular drf-yasg"`.

---

## Errors in Dockerfile.py313

### Error 1 — `pyyaml==6.0`: no wheel for Python 3.13, PEP 517 build fails

```
• Installing pyyaml (6.0)

  ChefInstallError

  Failed to install setuptools >= 40.8.0.

  CalledProcessError

  Command '['/tmp/tmp.../.venv/bin/python', ...]' returned non-zero exit status 1.

  FileNotFoundError: [Errno 2] No such file or directory:
    '/usr/local/lib/python3.13/site-packages/packaging/tags.py'

Note: This error originates from the build backend, and is likely not a problem
with poetry but with pyyaml (6.0) not supporting PEP 517 builds. You can verify
this by running 'pip wheel --no-cache-dir --use-pep517 "pyyaml (==6.0)"'.
```

**Nature:** PyYAML 6.0 (released 2021) uses Cython-compiled C extensions and ships
pre-built wheels for CPython up to 3.10. No `cp313` wheel was ever added to the
6.0 release. When Poetry falls back to building from source on Python 3.13, it
creates a PEP 517 build-isolation environment and fails during environment setup
because `poetry==1.7.1` uses a code path that expects `packaging/tags.py` as a
standalone file — a layout that changed in newer packaging releases bundled with
Python 3.13. The underlying root cause is that pyyaml 6.0 has no Python 3.13
wheel; 6.0.1 (released 2023) added `cp313` wheel support and fixes this.

**Type:** Build toolchain issue

---

### Error 2 — `django==3.2.18`: imports removed `cgi` stdlib module

```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import django; django.setup()
  File ".../django/urls/base.py", line 8, in <module>
    from .exceptions import NoReverseMatch, Resolver404
  File ".../django/http/__init__.py", line 2, in <module>
    from django.http.request import (...)
  File ".../django/http/request.py", line 1, in <module>
    import cgi
ModuleNotFoundError: No module named 'cgi'
```

*This error is revealed after fixing Error 1 and running the tests.*

**Nature:** Python 3.13 removed the `cgi` module (deprecated since 3.11, removed
per PEP 594). Django 3.2.18 imports `cgi` unconditionally at the top level of
`django/http/request.py`, causing every `django.setup()` call — including the one
pytest-django performs at test collection time — to raise
`ModuleNotFoundError: No module named 'cgi'`. Django removed its `cgi` dependency
in version 4.0 (backported to 4.2). The `pyproject.toml` constraint
`'^3 || ^4'` already permits Django 4.x; only the `poetry.lock` pin needs updating.

**Type:** Dependency incompatibility

---

## Benchmark Task

Given `Dockerfile.py313` as a starting point, update the project so that it builds
and the test suite passes on Python 3.13. The solution requires:

1. **Update `pyyaml`** from `6.0` to `>=6.0.1` in `poetry.lock` (the
   `pyproject.toml` constraint is already `"*"`).
2. **Update `django`** from `3.2.18` to `>=4.0` in `poetry.lock` (the
   `pyproject.toml` constraint `'^3 || ^4'` already permits 4.x; Django 4.2.x is
   the recommended target as the current LTS).
3. **Regenerate `poetry.lock`** to reflect the updated transitive dependency graph
   (cascade updates to `asgiref`, `sqlparse`, and other Django-pinned packages are
   expected).

The fix is purely dependency updates — no changes to `openapi_tester` source code
are required.
