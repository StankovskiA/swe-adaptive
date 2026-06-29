# Benchmark: natelandau/obsidian-metadata

**Repository:** https://github.com/natelandau/obsidian-metadata  
**Baseline Python:** 3.10  
**Failing Python:** 3.13  
**Tests passing on baseline:** 484

## What this benchmark tests

`obsidian-metadata` is a CLI tool for managing Obsidian vault metadata. It pins `regex<2024.0.0,>=2023.8.8` as a core dependency. The `regex` package is a C extension providing advanced regular expression support beyond the standard `re` module.

## Why Python 3.13 fails

`regex==2023.12.25` (the latest version in the `<2024.0.0,>=2023.8.8` range) has no pre-built wheel for Python 3.13 and its C extension source build fails:

```
Building wheel for regex (pyproject.toml): finished with status 'error'
× Building wheel for regex (pyproject.toml) did not run successfully.
```

Installation fails before the package can be installed.

## Why Python 3.10 passes

On Python 3.10, `regex==2023.12.25` installs from a pre-built wheel. 484 tests pass across metadata parsing, manipulation, and file I/O tests. (`tests/cli_test.py` is excluded due to a `typer`/`click` version incompatibility in `test_version` that is unrelated to the Python version being tested.)

## Minimal fix for Python 3.13

Upgrade `regex` in `pyproject.toml`:

```toml
# Change:
regex = ">=2023.8.8,<2024.0.0"
# To:
regex = ">=2024.0.0"
```

`regex 2024.x` ships pre-built wheels for Python 3.13.
