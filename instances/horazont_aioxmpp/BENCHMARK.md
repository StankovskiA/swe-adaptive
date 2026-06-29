# Benchmark: horazont/aioxmpp

## Test Results (Baseline)
- **4549 passed**, 3 failed, 65 skipped
- Python 3.10 (python:3.10-slim)

## Fix Applied
- Added `pip install pytz` before `pip install -e .` — `aioxmpp/xso/types.py` imports
  `pytz` directly but `pytz` is not listed in `install_requires`; it was previously a
  transitive dependency that got pulled in, but is no longer guaranteed on Python 3.10.
- Added `--ignore=tests/test_e2e.py` to the pytest CMD — the end-to-end tests use
  `aioxmpp.e2etest.provisioner.get_connected_client()`, which requires a live XMPP server
  to be configured and reachable; all 118 tests in that file fail at setup.

## Failing Tests
3 failures, all caused by Python 3.10 API changes:
- `test__set_bookmarks_failure` — checks for the error message
  "can only assign an iterable" but Python 3.10 changed it to
  "must assign iterable to extended slice"; the `assertRaisesRegex` pattern no longer matches.
- `test_convert_field_datetime_default_locale` — `tzlocal` on Python 3.10 returns a
  `zoneinfo.ZoneInfo` object instead of a `pytz.timezone`; the code calls
  `tzinfo.normalize(value)` which is a pytz-only method not present on `ZoneInfo`.
- `test_zombofant_net` — newer `pyOpenSSL` removed `X509.get_extension()`; the
  `security_layer.extract_python_dict_from_x509()` function still calls it.

## Python 3.13 Incompatibility
`pip install -e .` fails on Python 3.13 — `lxml~=4.0` (pinned in install_requires) has
no Python 3.13 wheel on PyPI, and building from source requires `libxml2` and `libxslt`
development packages which are not in the slim image:
`Error: Please make sure the libxml2 and libxslt development packages are installed.`

## Test Coverage
4549 tests across the full aioxmpp XMPP library: XSO (XML stream object) model,
types, and query; XML generation; protocol, stream, stanza, RFC 3921/6120 handling;
SASL authentication; security layer; dispatcher, callbacks, tasks; string preparation
(stringprep); XMPP structs, node, nonza, statemachine; tracking, connectors, network;
i18n/localization; service base classes; and all XEP extension modules (adhoc commands,
avatar, blocking, bookmarks, carbons, chatstates, disco, entitycaps, forms, httpupload,
IBB, IBR, IM, MDR, MUC, PEP, ping, presence, private XML, pubsub, roster, RPC, RSM,
SHIM, vcard, version).
