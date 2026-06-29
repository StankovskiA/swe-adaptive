# Benchmark: backoff

**Repository:** https://github.com/litl/backoff
**Language:** Python
**Test framework:** pytest

---

## Baseline (Python 3.8)

**Docker image:** `Dockerfile.test`
**Python version:** 3.8
**Result:** 123 passed, 0 failed

All 123 tests pass on Python 3.8.

---

## Python 3.13 (failing)

**Docker image:** `Dockerfile.py313`
**Python version:** 3.13
**Result:** Build/test fails

### Error 1 — `asyncio.get_event_loop()` raises RuntimeError in Python 3.10+ when called outside a running loop

```
#9 1.028 tests/test_backoff_async.py::test_on_predicate_on_regular_function_without_event_loop FAILED [ 86%]
#9 1.060 tests/test_backoff_async.py::test_on_exception_on_regular_function_without_event_loop FAILED [ 86%]
#9 1.077 tests/test_integration.py::test_on_predicate_runtime PASSED              [ 87%]
#9 1.081 tests/test_integration.py::test_on_exception_runtime PASSED              [ 88%]
#9 1.084 tests/test_jitter.py::test_full_jitter PASSED                            [ 89%]
#9 1.086 tests/test_wait_gen.py::test_decay PASSED                                [ 90%]
#9 1.087 tests/test_wait_gen.py::test_decay_init100 PASSED                        [ 91%]
#9 1.087 tests/test_wait_gen.py::test_decay_init100_decay3 PASSED                 [ 91%]
#9 1.088 tests/test_wait_gen.py::test_decay_init100_decay3_min5 PASSED            [ 92%]
#9 1.088 tests/test_wait_gen.py::test_expo PASSED                                 [ 93%]
#9 1.089 tests/test_wait_gen.py::test_expo_base3 PASSED                           [ 94%]
#9 1.089 tests/test_wait_gen.py::test_expo_factor3 PASSED                         [ 95%]
#9 1.090 tests/test_wait_gen.py::test_expo_base3_factor5 PASSED                   [ 95%]
#9 1.090 tests/test_wait_gen.py::test_expo_max_value PASSED                       [ 96%]
#9 1.091 tests/test_wait_gen.py::test_fibo PASSED                                 [ 97%]
```

**Root cause:** `asyncio.get_event_loop()` raises RuntimeError in Python 3.10+ when called outside a running loop

**Minimal fix:** Upgrade the package or configure `asyncio_mode = auto` in pytest settings.

---

## Summary

| # | Error | Minimal fix |
|---|-------|-------------|
| 1 | `asyncio.get_event_loop()` raises RuntimeError in Python 3.10+ when called outside a running loop | Upgrade the package or configure `asyncio_mode = auto` in pytest settings. |
