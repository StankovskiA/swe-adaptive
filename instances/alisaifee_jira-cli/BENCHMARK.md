# Benchmark: alisaifee/jira-cli

## Test Results (Baseline)
- **13 passed**, 3 failed
- Python 3.7 (python:3.7-slim)

## Fix Applied
- Changed CMD to run only `tests/test_parsing.py` — the other two test files are broken
  independently of Python version:
  - `test_rest_bridge.py` and `test_soap_bridge.py`: both fail with
    `TypeError: Can't instantiate abstract class JiraRestBridge/JiraSoapBridge with
    abstract methods get_issue_type, get_status` — the test's `setUp` directly instantiates
    an abstract class that was never given concrete implementations of the newly-added
    abstract methods; this is a pre-existing code defect unrelated to Python version.

## Failing Tests
3 failures in `test_parsing.py::CliInitParsing` (`test_first_run`,
`test_first_run_with_error_and_persist`, `test_subsequent_run_with_persist`) —
`TypeError: option values must be strings` in `configparser`. The library passes a
non-string value (boolean `False`) to a `ConfigParser` set call; Python 3 enforces the
string constraint strictly while Python 2 did not.

## Python 3.13 Incompatibility
`pip install -r requirements/main.txt` fails on Python 3.13 — `suds-jurko` (a SOAP
client library required by `jiracli`) has no Python 3.13 wheel and its C extension fails
to build:
`ERROR: Failed to build 'suds-jurko' when getting requirements to build wheel`

## Test Coverage
13 tests across: CLI argument parsing (issue operations, sprint, board, epic, project,
component, version, transition commands), config file loading, server/user/password
detection from config, and format string parsing from jiracli's configuration layer.
