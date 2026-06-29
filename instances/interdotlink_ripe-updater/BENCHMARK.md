# Benchmark Setup

This benchmark assesses an agent's ability to update a Python project's dependencies
and source code to support a newer Python version.

## Project

[ripe-updater](https://github.com/interdotlink/ripe-updater) is a Flask web service
that automates RIPE NCC database updates for IPv4/IPv6 prefixes managed by NetBox.
It uses a set of hard-pinned dependencies (`requirements.txt`) that were written
targeting Python 3.9–3.10, Flask 2.x, and early-2022 AWS SDK releases.

---

## Dockerfile.test — Baseline (Python 3.10.20)

`Dockerfile.test` establishes the working baseline. It builds and runs the full
test suite on **Python 3.10.20**, with 12 tests passing and no pre-existing failures.

### What it does

1. **Pin `werkzeug<3.0`** — `requirements.txt` pins `flask==2.1.1` but leaves
   `werkzeug` unpinned. pip resolves werkzeug 3.x, which removed `url_quote` from
   `werkzeug.urls`. Flask 2.1.x requires `werkzeug>=2.0,<3.0`, so the install
   succeeds but the import chain breaks at runtime. Adding `werkzeug<3.0` constrains
   pip to the compatible werkzeug 2.x series. This is a pre-existing transitive
   dependency gap in the project, not a Python version issue.

### Running

```bash
docker build -f Dockerfile.test -t ripe-updater-test .
docker run --rm ripe-updater-test
```

### Expected result

```
12 passed, 1 warning in 0.25s
```

The 1 warning is a `DeprecationWarning` from `pynetbox` noting that `pkg_resources`
is a deprecated API; it does not affect test outcomes on Python 3.10.

---

## Dockerfile.py313 — Failing Target (Python 3.13)

`Dockerfile.py313` applies the werkzeug baseline fix and then attempts to run the
test suite on **Python 3.13** without any further workarounds. It is expected to
fail at build time. This is the starting point for the benchmark task.

### Running

```bash
docker build -f Dockerfile.py313 -t ripe-updater-py313 .
```

### Expected result

The build fails during `RUN pytest tests/ -v` with two collection errors.
8 of the 12 tests (all of `test_functions.py`) are collected successfully but
the session is interrupted before any test runs.

---

## Errors in Dockerfile.py313

### Error 1 — `pynetbox==6.6.2`: `pkg_resources` removed from Python 3.13

```
tests/test_netbox.py:5: in <module>
    from ripeupdater.netbox import ObjectBuilder
ripeupdater/netbox.py:5: in <module>
    import pynetbox
.../pynetbox/__init__.py:1: in <module>
    from pkg_resources import get_distribution, DistributionNotFound
ModuleNotFoundError: No module named 'pkg_resources'
```

**Nature:** `pynetbox==6.6.2` imports `pkg_resources` at the top level to read its
own installed version. `pkg_resources` is provided by `setuptools` and was never
part of the standard library; however, Python 3.12+ installers stopped bundling
`setuptools` by default, leaving `pkg_resources` absent in the `python:3.13-slim`
image. The `DeprecationWarning` raised on Python 3.10 was a sign of this future
breakage — newer versions of `pynetbox` replaced this with `importlib.metadata`.

**Type:** Dependency incompatibility

---

### Error 2 — `boto3==1.21.44` / `botocore==1.24.44`: `cgi` module removed in Python 3.13

```
tests/test_ripe.py:5: in <module>
    from ripeupdater.backup_manager import BackupManager
ripeupdater/backup_manager.py:4: in <module>
    import boto3
.../botocore/utils.py:15: in <module>
    import cgi
ModuleNotFoundError: No module named 'cgi'
```

**Nature:** `botocore 1.24.44` (pulled in by `boto3==1.21.44`) imports the `cgi`
standard-library module in `botocore/utils.py`. The `cgi` module was deprecated
in Python 3.11 ([PEP 594](https://peps.python.org/pep-0594/)) and removed in
Python 3.13. Newer botocore releases replaced this with `email.message` and
`urllib.parse`. Upgrading `boto3` to any release from late 2022 onwards resolves
this.

**Type:** Dependency incompatibility

---

## Benchmark Task

Given `Dockerfile.py313` as a starting point, update the project so that it builds
and the test suite passes on Python 3.13. The solution requires:

1. **Upgrade `pynetbox`** from `==6.6.2` to a version that uses `importlib.metadata`
   instead of `pkg_resources` (7.x or later).

2. **Upgrade `boto3`** from `==1.21.44` to a version whose bundled `botocore` no
   longer uses the removed `cgi` module (any release from late 2022 / botocore
   ≥ 1.27.x).

3. **Verify transitive compatibility** — both upgrades pull in new versions of
   their transitive dependencies (`botocore`, `s3transfer`, `urllib3`); the updated
   versions must remain mutually compatible and compatible with the pinned
   `requests==2.27.1`.

The fix is purely dependency updates; no source code changes to the project itself
are required.
