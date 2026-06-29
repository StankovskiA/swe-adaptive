# Benchmark: pygrocy

**Repository:** https://github.com/SebRut/pygrocy
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.10)

**Docker image:** `Dockerfile.test`
**Python version:** 3.10
**Result:** 125 passed, 0 failed

All 125 tests pass on Python 3.10.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error — `StrEnum.__str__` behavior changed in Python 3.12+ causing VCR cassette URL mismatch

```
#9 1.228 test/test_meal_plan_sections.py::TestMealPlanSections::test_get_sections_valid FAILED [ 55%]
#9 1.306 test/test_meal_plan_sections.py::TestMealPlanSections::test_get_sections_filters_valid FAILED [ 57%]
#9 1.360 test/test_meal_plan_sections.py::TestMealPlanSections::test_get_sections_filters_invalid FAILED [ 58%]
...
pygrocy/grocy_api_client.py:795: in get_generic_objects_for_type
    return self._do_get_request(f"objects/{entity_type}", query_filters)
...
raise CannotOverwriteExistingCassetteException(
    cassette=self.cassette,
    failed_request=self._vcr_request,
)
```

**Root cause:** `EntityType` is a `StrEnum` subclass. `pygrocy` builds API URLs like `f"objects/{entity_type}"`. In Python 3.11 (when `StrEnum` was introduced), `str(StrEnum.MEMBER)` returned the full `ClassName.member_name` string. Python 3.12 changed `StrEnum.__str__` to return just the member's value (the plain string), because `StrEnum` inherits from `str`. This means the URL path constructed from `entity_type` differs between Python 3.10 and 3.13, so requests no longer match the pre-recorded VCR cassettes, triggering `CannotOverwriteExistingCassetteException` (cassette is write-protected).

**Minimal fix:** Update the URL-building code to explicitly call `.value` (`f"objects/{entity_type.value}"`) so behavior is consistent across Python versions.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | `StrEnum.__str__` changed in Python 3.12+: now returns the member value directly instead of `ClassName.member_name` → URL path differs → VCR cassette mismatch → `CannotOverwriteExistingCassetteException` | Use `entity_type.value` explicitly in URL construction |
