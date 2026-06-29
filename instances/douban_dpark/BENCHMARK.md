# Benchmark: douban/dpark

**Repository:** https://github.com/douban/dpark
**Language:** Python
**Test framework:** pytest (with flaky plugin)

dpark is a Python clone of Apache Spark, providing distributed data processing via RDDs, DStreams, and shuffle operations.

---

## Dockerfile.test — Baseline (Python 3.7)

**Python version:** 3.7
**Result:** 146 passed

### Special setup

- `flaky` plugin added: used in `test_rdd.py::test_big_object_performance` via `@flaky` decorator; pytest raises `No module named 'flaky'` at collection without it.
- CRLF line endings stripped: source files checked out on Windows retain `\r\n` endings. `open()` uses universal newlines so reads yield `\n`, but dpark's `partialTextFile` reads raw bytes and returns lines with trailing `\r`. The 4 `test_partial_file` variants all fail with CRLF; a `sed -i 's/\r$//'` pass in the Dockerfile fixes all four.

### Build and run

```bash
docker build -f Dockerfile.test -t dpark-test .
docker run --rm dpark-test
# Expected: 146 passed in ~3:45
```

---

## Dockerfile.py313 — Failing Target (Python 3.13)

**Python version:** 3.13
**Result:** Build fails during `pip install -e .`

`dpark` depends on `http-parser`, which imports the `imp` module in its `setup.py`. `imp` was removed in Python 3.12.

### Build command (expected to fail)

```bash
docker build -f Dockerfile.py313 -t dpark-py313 .
# Expected: ModuleNotFoundError: No module named 'imp'
```

---

## Errors in Dockerfile.py313

```
ModuleNotFoundError: No module named 'imp'
```

**Root cause:** `http-parser` (pinned in dpark's requirements) uses `imp.find_module()` in its `setup.py` to locate the C extension. The `imp` module was deprecated in Python 3.4 and removed entirely in Python 3.12+.

**Minimal fix:** Replace `http-parser` with `httptools` or another http parsing library that supports Python 3.12+.
