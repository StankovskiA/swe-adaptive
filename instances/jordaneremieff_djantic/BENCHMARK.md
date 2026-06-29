# Benchmark Setup

This benchmark assesses an agent's ability to update a Python project's dependencies
and source code to support a newer Python version.

## Project

[djantic](https://github.com/jordaneremieff/djantic) is a library that generates
Pydantic models from Django ORM models. It uses a set of pinned dependencies
(`pyproject.toml`) that were written targeting Python 3.7–3.10, Pydantic v1, and
Django 3.x.

---

## Dockerfile.test — Baseline (Python 3.10.20)

`Dockerfile.test` establishes the working baseline. It builds and runs the full
test suite on **Python 3.10.20**, with 32 tests passing and no pre-existing failures.

### What it does

1. **Pin Django to 3.x and Pydantic to v1** — The project's `pyproject.toml`
   declares `Django = "~3"` and `pydantic = "^1.8.2"`. These constraints are
   passed explicitly to pip to ensure reproducible resolution and avoid pip
   upgrading either package beyond the supported range.

2. **Install `psycopg2-binary` instead of `psycopg2`** — The dev dependencies
   list `psycopg2 ^2.9.1`, which requires a system `libpq` build toolchain. Using
   the pre-compiled `psycopg2-binary` wheel avoids this in the Docker environment.
   The tests use an in-memory SQLite database, so the binary variant is sufficient.

### Running

```bash
docker build -f Dockerfile.test -t djantic-test .
docker run --rm djantic-test
```

### Expected result

```
32 passed, 7 warnings in 0.54s
```

The 7 warnings are `DeprecationWarning` from `factory-boy` about a future change
to post-generation save behaviour; they are unrelated to the Python version and do
not affect test outcomes.

---

## Dockerfile.py313 — Failing Target (Python 3.13)

`Dockerfile.py313` attempts a straightforward install of the project on
**Python 3.13** without any workarounds. It is expected to fail at build time.
This is the starting point for the benchmark task.

### Running

```bash
docker build -f Dockerfile.py313 -t djantic-py313 .
```

### Expected result

The build fails during `RUN pytest tests/ -q`.
All packages install successfully; the failure occurs at test-collection time when
pytest-django calls `django.setup()`, which triggers the broken import chain.

---

## Errors in Dockerfile.py313

### Error 1 — `Django==3.2.25`: `cgi` module removed in Python 3.13

```
File "/usr/local/lib/python3.13/site-packages/django/http/request.py", line 1, in <module>
    import cgi
ModuleNotFoundError: No module named 'cgi'
```

**Nature:** Django 3.x uses the `cgi` standard-library module in
`django.http.request`. The `cgi` module was deprecated in Python 3.11
([PEP 594](https://peps.python.org/pep-0594/)) and removed entirely in Python 3.13.
The import fails before any test code runs — it is triggered by `django.setup()`
during pytest startup. Every import path into `django.http` hits this module, so
there is no way to work around it without replacing Django 3.x.

**Type:** Dependency incompatibility

---

## Benchmark Task

Given `Dockerfile.py313` as a starting point, update the project so that it builds
and the test suite passes on Python 3.13. The solution requires:

1. **Upgrade Django** from `~3` to a version that supports Python 3.13 (Django 4.2
   LTS or Django 5.x). Django 4.2 is the minimum release that removed the `cgi`
   dependency and officially supports Python 3.13.

2. **Verify Pydantic v1 compatibility with the upgraded Django** — `pydantic
   ^1.8.2` installs and runs on Python 3.13 without errors, so no Pydantic upgrade
   is strictly required to restore the passing baseline. However, Pydantic v1 is
   end-of-life; agents may choose to upgrade to Pydantic v2, which requires source
   code changes throughout `djantic/main.py` and `djantic/fields.py` to replace the
   v1 model API (`__fields__`, `validator`, `Field(...)` internals) with the v2
   equivalents.

The minimal fix is a dependency-only change (Django version bump). A more complete
fix also migrates the source to Pydantic v2.
