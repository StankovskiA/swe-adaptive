# Benchmark: dephell/dephell

**Repository:** https://github.com/dephell/dephell
**Language:** Python
**Test framework:** pytest

dephell is a Python project manager and dependency resolver. It converts between formats (pip, Pipfile, poetry, setup.py, etc.) and resolves dependencies against PyPI.

---

## Dockerfile.test — Baseline (Python 3.10)

**Python version:** 3.10
**Result:** 277 passed, 2 deselected, 2 xfailed, 4 xpassed, 47 failed

### Excluded tests and reasons

| Excluded | Reason |
|----------|--------|
| `test_conda_loads` | Requires `conda` package (not installed — large optional dependency) |
| `test_conda_dumps_new` | Same as above |

### Remaining failures (47 tests)

The 47 remaining failures fall into these categories:

- **Real PyPI network tests with non-PEP440 version strings** (`test_resolving/test_smoke`, `test_warehouse_api`, `test_warehouse_simple`): Tests marked `@pytest.mark.allow_hosts()` make real HTTP calls to PyPI and encounter packages with old version strings (e.g. `pytz (>=2011k)` parenthesis syntax, `0.5.2.5.g5b3e942` pre-release format). These are pre-existing data compatibility issues between old PyPI metadata and the `packaging` library.
- **Various command/converter tests**: Depend on external services or optional deps (`html5lib`, `ruamel.yaml`) not installed.

### Special setup

- `appdirs` installed explicitly: it is an optional `[full]` extra but is lazily imported at module level in `dephell/imports.py`, causing `test_cli.py` to fail at collection time.
- `fissix` installed: optional dep needed for Python 2→3 import transform tests (`test_actions/test_transform.py`, `test_commands/test_vendor_import.py`).
- `git` installed: needed by `tests/test_repositories/test_git_git.py`.
- `packaging>=20,<22` pinned: dephell uses the old `packaging.version.LegacyVersion` / `Requirement.specs` API that was removed in packaging 22.0. Modern packaging raises `InvalidVersion` for non-PEP440 version strings that dephell's specifier logic expected to handle.
- `pip install -e .` downgrades pip to 19.3.1 (declared as `pip<=19.3.1,>=18.0` in `install_requires`). pip 19.3.1 still works on Python 3.10 for package installation.

### Build and run

```bash
docker build -f Dockerfile.test -t dephell_dephell_test .
docker run --rm dephell_dephell_test
# Expected: 277 passed, 2 deselected, 2 xfailed, 4 xpassed in ~7 minutes
```

---

## Dockerfile.py313 — Failing Target (Python 3.13)

**Python version:** 3.13
**Result:** Build fails during install

dephell declares `pip<=19.3.1,>=18.0` as a hard install dependency. When `pip install -e .` runs, it downgrades pip to 19.3.1. Attempting any subsequent `pip` command (here: `pip install pytest`) immediately crashes because pip 19.3.1 imports an internal `urllib3` module (`pip._vendor.urllib3.packages.six.moves`) that was removed in Python 3.13.

### Build command (expected to fail)

```bash
docker build -f Dockerfile.py313 -t dephell_dephell_py313 .
# Expected: ModuleNotFoundError: No module named 'pip._vendor.urllib3.packages.six.moves'
```

---

## Errors in Dockerfile.py313

```
  File "/usr/local/bin/pip", line 3, in <module>
    from pip._internal.main import main
  ...
  File "/usr/local/lib/python3.13/site-packages/pip/_internal/utils/compat.py", line 17, in <module>
    from pip._vendor.urllib3.util import IS_PYOPENSSL
  File "/usr/local/lib/python3.13/site-packages/pip/_vendor/urllib3/exceptions.py", line 2, in <module>
    from .packages.six.moves.http_client import IncompleteRead as httplib_IncompleteRead
ModuleNotFoundError: No module named 'pip._vendor.urllib3.packages.six.moves'
```

**Root cause:** dephell hard-depends on `pip<=19.3.1` (it shells out to pip internals). pip 19.3.1 was released in 2019 and bundles `urllib3` with `six` compatibility shims that were dropped in Python 3.13-era vendored urllib3. After `pip install -e .` downgrades pip to 19.3.1, any subsequent use of the `pip` binary crashes at import time.

**Minimal fix:** Remove the `pip<=19.3.1` hard constraint from `install_requires` and replace internal pip usage with the public `subprocess`/`importlib.metadata` APIs.
