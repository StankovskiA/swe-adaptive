# Benchmark: 0xSpaceShard/starknet-devnet-deprecated

## Test Results (Baseline)
- **121 passed**, 10 failed
- Python 3.9 (python:3.9-slim)
- Tests run: `test/rpc/` only (RPC API tests)

## Fix Applied
- Created a minimal `poetry` shim at `/usr/local/bin/poetry` that strips the `run` subcommand:
  `if [ "$1" = "run" ]; then shift; fi; exec "$@"` — the test utilities start starknet-devnet
  via `poetry run starknet-devnet`, so the shim lets that work without Poetry being installed.
- Pre-compiled Cairo contracts at build time with `starknet-compile-deprecated`:
  contracts in `test/contracts/cairo/*.cairo` are compiled to JSON artifacts in
  `test/artifacts/contracts/cairo/` — these artifacts are required by the test fixtures.
- Added `--timeout=60` via `pytest-timeout` to prevent individual tests from hanging
  indefinitely (some integration tests spawn a starknet-devnet process per test and wait
  for network responses).
- Focused the test run on `test/rpc/` which tests the JSON-RPC API surface. The remaining
  integration tests in `test/` take 60+ minutes total to run.

## Failing Tests
10 failures — all `declare_v2` / Sierra-related tests:
- `test_add_declare_transaction_v2`, `test_declare_transaction_v2_already_declared`,
  `test_get_transaction_by_hash_declare_v2`, `test_simulate_transaction_declare_v2[*]` —
  Cairo v2 (Sierra) contract declaration requires a Sierra-to-CASM compiler which is not
  bundled in the deprecated devnet; the devnet only supports Cairo v1 (deprecated class hash).

## Python 3.13 Incompatibility
`pip install -e .` fails on Python 3.13 — the package metadata explicitly declares
`python_requires = "<3.10,>=3.9"`, and pip enforces this constraint: Python 3.13 is not in
the supported range `<3.10`. This is an intentional constraint since the package is deprecated
and was specifically built for Python 3.9.

## Test Coverage
121 tests pass across: JSON-RPC block queries (get_block_with_tx_hashes, get_block_transaction_count,
get_block_number), contract calls (call, call_raises), class queries (get_class, get_class_at),
fee estimation, miscellaneous RPC endpoints, schema validation, storage queries, transaction
simulation (invoke, declare_v1, deploy_account), and transaction lifecycle
(get/add invoke, declare, deploy, deploy_account transactions).
