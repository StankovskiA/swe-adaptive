# Benchmark: icon-project/loopchain

## Test Results (Baseline)
- **230 passed**, 24 skipped, 3 xfailed, 14 xpassed, 63 errors, 6 warnings
- Python 3.7 (python:3.7-slim)

## Fix Applied
- Added `freezegun` to pip install — tests use `freezegun.freeze_time` for time mocking.
- Added `pytest-timeout` and `--timeout=30` to CMD — prevents tests from hanging on I/O.
- Added `--ignore` flags for network-dependent test files:
  - `test_message_queue.py` — requires live RabbitMQ (uses `aio_pika`)
  - `test_rest_client.py` — makes live HTTP requests
  - `test_common_process.py` — spawns system processes
  - `test_common_subprocess.py` — spawns system subprocesses

## Failing Tests
63 errors in `blockchain/transactions/test_transaction_verifier*.py` — these tests fail at setup
due to missing `icon_rc` binary (a Go IISS calculation runtime). These are blockchain-specific
integration tests that require the full ICON runtime stack.

## Python 3.13 Incompatibility
`pip install -r requirements.txt` fails on Python 3.13 — `grpcio==1.32.0` has no cp313 wheel
and fails to build from source. Additionally, `coincurve==13.0.0` (secp256k1 C extension) and
`protobuf==3.13.0` also have no Python 3.13 wheels.

## Test Coverage
230 tests pass across: block creation and verification, blockchain storage, candidate block
management, channel state machines, configuration parsing, cryptography primitives, DoS guard,
key-value store (LevelDB), LRU cache, message encoding/decoding, statemachine transitions,
signature verification, and utility functions.
