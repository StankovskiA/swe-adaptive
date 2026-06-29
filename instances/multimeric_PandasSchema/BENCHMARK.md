# Benchmark: multimeric/PandasSchema

## Repository
**GitHub:** https://github.com/multimeric/PandasSchema  
**Description:** A validation library for Pandas DataFrames, inspired by JSON Schema.

## Baseline
- **Python version:** 3.10
- **Test command:** `pytest test/ -v --deselect=test/test_schema.py::OrderedSchema::test_mixed_columns`
- **Result:** 66 passed, 1 deselected (pre-existing unrelated failure)

## Python 3.13 Failure
- **Test command:** `pytest test/ -v` (run at image build time)
- **Result:** 3 failed (2 new failures on top of the pre-existing one)

### Error
```
FAILED test/test_validation.py::Dtype::test_invalid_items - TypeError: Cannot interpret '<U7' as a data type
FAILED test/test_validation.py::Dtype::test_schema - TypeError: Cannot interpret '<U7' as a data type
```

### Root Cause
`pandas_schema` uses numpy dtype string aliases (e.g. `'unicode'`) in its `DtypeValidation` class. Python 3.13 requires `numpy>=2.0` (no older numpy wheels exist for Python 3.13). NumPy 2.0 removed several dtype string aliases that were deprecated in 1.x, causing `TypeError: Cannot interpret '<U7' as a data type` when validating string/unicode column types.

The relevant code in `pandas_schema/validation.py`:
```python
class DtypeValidation(SeriesValidation):
    def __init__(self, dtype, ...):
        self._dtype = np.dtype(dtype)  # fails with numpy 2.0 for old aliases
```

## Minimal Fix
Update `DtypeValidation` to use the canonical numpy 2.0 dtype names:

```diff
-self._dtype = np.dtype(dtype)
+# Use np.dtype() which accepts the canonical form; map legacy aliases first
+_ALIAS_MAP = {'unicode': np.str_, 'string': np.str_}
+self._dtype = np.dtype(_ALIAS_MAP.get(dtype, dtype))
```

Or, equivalently, upgrade the dtype alias usage in tests and library code to use `np.str_` instead of `'unicode'`.
