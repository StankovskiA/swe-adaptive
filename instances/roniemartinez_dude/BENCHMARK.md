# Benchmark: roniemartinez/dude

## Test Results (Baseline)
- **32 passed**, 0 failures
- Python 3.10 (python:3.10-slim)

## Fix Applied
- Installed optional extras `[bs4,lxml,parsel]` via `pip install -e ".[bs4,lxml,parsel]"` —
  beautifulsoup4, httpx, lxml, cssselect, and parsel are optional extras in pyproject.toml,
  but their test files fail to import when not installed.
- Ignored browser-dependent tests:
  - `tests/test_playwright_async.py` and `tests/test_playwright_sync.py` — require Playwright
    with a downloaded Chromium/Firefox/WebKit browser binary; `playwright install` is not run.
  - `tests/test_selenium.py` — requires a running ChromeDriver/GeckoDriver and browser.
- Ignored `tests/test_parsel.py` — parsel 1.x requires `cssselect._unicode_safe_getattr`
  which was removed from cssselect in newer versions; `ImportError` during collection prevents
  the tests from running even with the extras installed.

## Failing Tests
0 failures. Ignored tests require browser binaries (Playwright/Selenium) or have a transitive
version incompatibility (parsel vs cssselect).

## Python 3.13 Incompatibility
`pip install -e .` fails on Python 3.13 — `braveblock ^0.5.0` (a required direct dependency
providing ad-blocking) has no Python 3.13 wheel and fails to install with a compiler/C
extension error.

## Test Coverage
32 tests pass across: CSS/XPath/text/regex selector types and string representations, selector
comparison and invalid selector detection, bs4 scraper (BeautifulSoup4 — scraping with
CSS/XPath selectors, pagination, save callbacks, async and generator patterns), lxml scraper
(same functionality via lxml backend), and scraper rule registration.
