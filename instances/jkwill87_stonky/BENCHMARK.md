# Benchmark: jkwill87_stonky

## Build
- Base image: `python:3.10-slim`
- Dockerfile: `Dockerfile.test`
- Build command: `docker build -f Dockerfile.test -t stonky-test .`
- Build result: SUCCESS

## Test Run
- Run command: `docker run --rm stonky-test`
- Test framework: pytest
- Results: **34 passed, 2 failed**
- Summary line: `2 failed, 34 passed, 1 warning in 12.97s`

## Failing Tests
The 2 failing tests are live network tests that make HTTP requests to Yahoo Finance:
- `tests/test_api.py::TestProviders::test_forex` — `aiohttp.client_exceptions.ContentTypeError`: Yahoo Finance API returns HTML instead of JSON
- `tests/test_api.py::TestProviders::test_quote` — same issue

These failures are due to external API changes (Yahoo Finance returning HTML), not code defects.

## Graduation Criteria
- Tests passing: 34 >= 10 (threshold)
- Status: GRADUATED

## Dockerfile.py313 Check
`Dockerfile.py313` uses `RUN pytest tests/ -v` (correct — `RUN` not `CMD`).
