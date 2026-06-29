# Benchmark: dschep/lambda-decorators

## Test Results (Baseline)
- **29 passed**, 3 failed
- Python 3.8 (python:3.8-slim)

## Fix Applied
None. The original Dockerfile.test works as-is.

## Failing Tests
3 failures in `tests/test_ssm_parameter_store.py` — these tests call AWS SSM (Systems
Manager Parameter Store) without credentials/region configured; they fail with
`botocore.exceptions.NoRegionError`. All other tests are offline unit tests using mocked
AWS Lambda event/context objects.

## Python 3.13 Incompatibility
`pip install -r requirements.txt` fails on Python 3.13 — the `aws-xray-sdk` or `boto3`
dependency chain has a package that fails to install on Python 3.13.

## Test Coverage
29 tests pass across: async_handler (async Lambda function wrapping), cors_headers
(CORS header injection), dead_letter_exception_handler (DLQ error forwarding), json_http_resp
(HTTP response formatting with status codes/headers), json_schema_validator (request/response
JSON Schema validation), LambdaDecorator subclass chaining, and load_json_body (request body
deserialization).
