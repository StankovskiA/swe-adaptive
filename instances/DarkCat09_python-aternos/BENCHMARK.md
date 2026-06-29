# Benchmark: DarkCat09/python-aternos

**Repository:** https://github.com/DarkCat09/python-aternos  
**Baseline Python:** 3.10  
**Failing Python:** 3.13  
**Tests passing on baseline:** 7 passed, 4 skipped

## What this benchmark tests

`python-aternos` is a Python client for the Aternos game server hosting platform. Its `requirements.txt` pins `lxml==4.9.2`, an XML/HTML processing C extension library.

## Why Python 3.13 fails

`lxml==4.9.2` cannot build its wheel on Python 3.13. The `lxml` source build requires `libxml2` and `libxslt` development headers, and the 4.9.x series has C API compatibility issues with Python 3.13:

```
Building lxml version 4.9.2.
Building without Cython.
Error: Please make sure the libxml2 and libxslt development packages are installed.
ERROR: Failed to build 'lxml' when getting requirements to build wheel
```

No pre-built wheel for `lxml==4.9.2` is available for Python 3.13.

## Why Python 3.10 passes

On Python 3.10, `lxml==4.9.2` installs from a pre-built wheel. With `tests/requirements.txt` also installed (`requests-mock`), 7 tests pass using mocked HTTP responses. 4 tests are appropriately skipped (one requires Node.js, three require login credentials).

## Minimal fix for Python 3.13

Upgrade `lxml` in `requirements.txt`:

```
# Change:
lxml==4.9.2
# To:
lxml>=5.0
```

`lxml` 5.0+ ships pre-built wheels for Python 3.13 and resolved its C API compatibility issues.
