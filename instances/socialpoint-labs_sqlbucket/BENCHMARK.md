# Benchmark: socialpoint-labs/sqlbucket

## Repository
**GitHub:** https://github.com/socialpoint-labs/sqlbucket  
**Description:** Write your SQL ETL flow and ETL integrity tool. Manages SQL scripts with Jinja2 templating and YAML configuration.

## Baseline
- **Python version:** 3.10
- **Test command:** `pytest tests/ -v`
- **Result:** 57 passed

## Python 3.13 Failure
- **Test command:** `pytest tests/ -v` (run at image build time)
- **Result:** Build fails — cannot install `PyYAML==6.0`

### Error
```
Collecting PyYAML==6.0 (from sqlbucket==0.4.4)
  Downloading PyYAML-6.0.tar.gz (124 kB)
  AttributeError: 'build_ext' object has no attribute 'cython_sources'
ERROR: Failed to build 'PyYAML' when getting requirements to build wheel
```

### Root Cause
`sqlbucket==0.4.4` pins `PyYAML==6.0` in its `dependencies`. `PyYAML 6.0` has no pre-built wheel for Python 3.13 and its source build fails because it uses `build_ext.cython_sources` — an attribute removed from `setuptools` in newer versions that ship with Python 3.13.

## Minimal Fix
In `pyproject.toml`, relax the PyYAML pin to a version that ships Python 3.13 wheels:

```diff
-'PyYAML==6.0',
+'PyYAML>=6.0.1',
```

`PyYAML 6.0.1` and later ship pre-built wheels for Python 3.13.
