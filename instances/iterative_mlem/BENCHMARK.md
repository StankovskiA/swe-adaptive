# Benchmark Setup

This benchmark assesses an agent's ability to update a Python project's dependencies and source code to support a newer Python version.

## Project

[MLEM](https://github.com/iterative/mlem) is a machine learning model packaging and deployment framework built by Iterative. It saves ML models in a standard YAML-described format and supports deployment to Heroku, SageMaker, Kubernetes, and other platforms. It uses `pydantic<2`, `isort>=5.10`, and a set of loosely-pinned dependencies that were written targeting Python 3.8–3.10.

---

## Dockerfile.test — Baseline (Python 3.8)

`Dockerfile.test` establishes the working baseline. It builds and runs the full test suite on **Python 3.8**, with all optional ML extras installed.

### What it does

1. **Pre-installs CPU-only torch and torchvision** — `setup.py` lists `torch` as an optional extra. Without intervention, pip pulls the GPU build (~2 GB). Installing from the PyTorch CPU wheel index first satisfies the `torch` constraint while keeping the image manageable.

2. **Installs the project with all test extras** — `pip install -e ".[tests]"` installs the project in editable mode with the full test dependency set defined in `setup.py`, which includes numpy, pandas, scikit-learn, dvc, boto3, s3fs, gcsfs, adlfs, pytest, and more.

3. **Installs remaining optional ML extras** — The `[tests]` extra does not include all of mlem's optional framework integrations. The following are installed separately so that all extension modules are importable and their tests can run: `tensorflow`, `h5py` (required by `mlem.contrib.tensorflow` at import time), `catboost`, `sagemaker`, `kubernetes`, `streamlit`, `streamlit_pydantic`, and `onnxruntime`.

4. **Pins packages with breaking API changes** — `setup.py` uses loose lower bounds on several dependencies. Newer versions of those packages introduced breaking changes that are not compatible with this codebase:

   | Package | Pin | Reason |
   |---|---|---|
   | `isort` | `>=5.10,<6` | isort 6 removed `isort.deprecated.finders`, imported unconditionally at module load in `mlem/utils/module.py:21` |
   | `pytest` | `<8` | pytest 8 removed `CallSpec2.funcargs`, relied on by `pytest-lazy-fixture==0.6.3` |
   | `typer` | `>=0.6,<0.9` | typer 0.9 changed the signature of `get_group_from_info()`, called directly in `tests/cli/test_main.py:30` |
   | `prometheus-fastapi-instrumentator` | `<7` | version 7 uses `list[X]` generic syntax (Python 3.9+) which fails on Python 3.8 |
   | `fsspec` | `<2023.6.0` | fsspec 2023.6 added strict `**` glob validation that rejects patterns used in existing tests |
   | `s3fs` + `boto3` + `botocore` | `s3fs<2022.11`, `boto3<1.25`, `botocore<1.28` | s3fs 2022.11 changed `.protocol` from `'s3'` to `('s3','s3a')`, breaking URI assertions in tests; s3fs<2022.11 uses `aiobotocore` which requires older botocore, so boto3/botocore must be pinned to a consistent set |

### Running

```bash
docker build --progress=plain -f Dockerfile.test -t mlem-test . 2>&1 | tee build-test.log
docker run --rm mlem-test 2>&1 | tee run-test.log
```

### Expected result

```
801 passed, 53 deselected, 8 xfailed
```

Zero unexpected failures. The 8 `xfailed` results are tests explicitly marked `@pytest.mark.xfail` in `tests/core/custom_requirements/test_shell_reqs.py` — known failures unrelated to Python version.

---

## Dockerfile.py313 — Failing Target (Python 3.13)

`Dockerfile.py313` attempts a plain `pip install -e "."` on **Python 3.13** with no workarounds, then bakes in a `python -c "import mlem"` check as a `RUN` step. The build fails at that step because `import mlem` triggers the broken import.

### Running

```bash
docker build --progress=plain -f Dockerfile.py313 -t mlem-py313 . 2>&1 | tee build-py313.log
```

### Expected result

The build fails at the `RUN python -c "import mlem"` step:

```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/root/code/mlem/__init__.py", line 9, in <module>
    from . import api
  File "/root/code/mlem/api/__init__.py", line 4, in <module>
    from ..core.metadata import load, load_meta, save
  File "/root/code/mlem/core/metadata.py", line 14, in <module>
    from mlem.core.data_type import DataType
  File "/root/code/mlem/core/data_type.py", line 46, in <module>
    from mlem.utils.module import get_object_requirements
  File "/root/code/mlem/utils/module.py", line 21, in <module>
    from isort.deprecated.finders import FindersManager
ModuleNotFoundError: No module named 'isort.deprecated'
```

---

## Errors in Dockerfile.py313

### Error 1 — `isort.deprecated.finders`: module removed in isort 6

```
ModuleNotFoundError: No module named 'isort.deprecated'
```

**Location:** `mlem/utils/module.py:21`

```python
from isort.deprecated.finders import FindersManager
```

**Nature:** `setup.py` declares `isort>=5.10` with no upper bound. On Python 3.13, pip installs the latest isort (6.x), which removed the entire `isort.deprecated` subpackage. Because this import is at module top level, `import mlem` crashes unconditionally — no test can run at all.

**Type:** Dependency API removal requiring a source code change. The fix is either to pin `isort<6` in `setup.py` or to replace the `FindersManager` usage in `mlem/utils/module.py` with the current isort API.

---

### Error 2 — `typer`: internal API signature change

```
TypeError: get_group_from_info() missing 1 required keyword-only argument: 'suggest_commands'
```

**Location:** `tests/cli/test_main.py:30`

```python
from typer.main import get_command_from_info, get_group, get_group_from_info
...
get_group_from_info(g, pretty_exceptions_short=False, rich_markup_mode="rich")
```

**Nature:** `setup.py` does not pin an upper bound on `typer`. Version 0.9 added a required `suggest_commands` keyword argument to the internal `get_group_from_info()` function. The tests call this internal function directly.

**Type:** Dependency internal API change — requires either pinning `typer<0.9` or updating the test to pass the new argument.

---

### Error 3 — `fsspec`: strict `**` glob validation

```
ValueError: Invalid pattern: '**' can only be an entire path component
```

**Nature:** fsspec 2023.6 introduced strict validation of glob patterns, rejecting `**` when used as part of a path component (e.g. `path/**.mlem`). Existing test patterns and internal mlem code use this form.

**Type:** Dependency behaviour change — requires updating glob patterns in mlem source and tests, or pinning `fsspec<2023.6`.

---

### Error 4 — `s3fs`: `.protocol` changed from string to tuple

```
AssertionError: assert "('s3', 's3a')://some_path" == 's3://some_path'
```

**Nature:** s3fs 2022.11 changed the `AbstractFileSystem.protocol` attribute from the string `'s3'` to the tuple `('s3', 's3a')` to expose the `s3a` alias. Code that builds URIs by string-concatenating `fs.protocol + "://"` now produces `('s3', 's3a')://...` instead.

**Type:** Dependency behaviour change — requires updating URI construction logic to handle both string and tuple protocols, or pinning `s3fs<2022.11`.

---

## Benchmark Task

Given `Dockerfile.py313` as a starting point, update the project so that `import mlem` succeeds and the test suite passes on Python 3.13.

The solution requires:

1. **Fixing the `isort.deprecated` import** in `mlem/utils/module.py` — this is the primary blocker that prevents the project from loading at all. Either replace `FindersManager` with the current isort API or remove the dependency on the deprecated subpackage.

2. **Updating loose dependency bounds** in `setup.py` — add upper bounds or migrate usage for `isort`, `typer`, `fsspec`, and `s3fs` to versions whose APIs are stable and compatible with Python 3.13.

3. **Fixing consuming code** — update any call sites in `mlem/` and `tests/` that rely on the changed APIs (glob patterns, URI construction, typer internals).
