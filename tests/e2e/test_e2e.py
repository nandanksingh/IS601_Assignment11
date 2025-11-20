# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/17/2025
# Assignment-11: End-to-End (E2E) API & UI Testing
# File: tests/e2e/test_e2e.py
# ----------------------------------------------------------
# Description:
# Full end-to-end test suite using Playwright + HTTP requests.
#
# Covers:
#   • FastAPI server health readiness
#   • Homepage rendering (UI)
#   • Calculator UI → backend arithmetic operations
#   • Error handling (invalid input, missing values, division by zero)
# ----------------------------------------------------------

import os
import time
import pytest
import requests
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


# ----------------------------------------------------------
# Base URL (local or overridden in CI/CD)
# ----------------------------------------------------------
BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000")


# ----------------------------------------------------------
# Helper — Wait Until App Is Ready
# ----------------------------------------------------------
def wait_for_app_ready(url=f"{BASE_URL}/health", timeout=30):
    """
    Waits up to 30 seconds until FastAPI responds with HTTP 200.
    Prevents tests from running before the server is fully started.
    """
    for _ in range(timeout):
        try:
            r = requests.get(url)
            if r.status_code == 200:
                print(" FastAPI server is ready.")
                return
        except requests.exceptions.ConnectionError:
            time.sleep(1)

    pytest.fail(f"FastAPI server did not respond at {url}")


# ----------------------------------------------------------
# Playwright Fixtures
# ----------------------------------------------------------
@pytest.fixture(scope="module")
def browser():
    """Launch headless Chromium once per module."""
    wait_for_app_ready()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    """Fresh browser page for every test."""
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()


# ----------------------------------------------------------
# Homepage & Health Checks
# ----------------------------------------------------------
@pytest.mark.e2e
def test_homepage_loads(page):
    """Verify homepage loads and contains expected title text."""
    page.goto(BASE_URL, wait_until="domcontentloaded")
    title_text = page.text_content("h1") or ""
    assert "FastAPI" in title_text or "Calculator" in title_text


@pytest.mark.e2e
def test_health_endpoint_direct():
    """Confirm /health returns JSON indicating service is OK."""
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    body = r.json()
    assert "status" in body
    assert body["status"].lower() in ["ok", "healthy", "running"]


# ----------------------------------------------------------
# Calculator Functional Tests
# ----------------------------------------------------------
@pytest.mark.e2e
@pytest.mark.parametrize(
    "op, a, b, expected",
    [
        ("Add", "5", "7", "12"),
        ("Subtract", "15", "4", "11"),
        ("Multiply", "6", "3", "18"),
        ("Divide", "20", "5", "4"),
    ],
)
def test_calculator_operations(page, op, a, b, expected):
    """Ensure UI → API calculation flow works for all operations."""
    page.goto(BASE_URL, wait_until="domcontentloaded")
    page.fill("#a", a)
    page.fill("#b", b)
    page.click(f"text={op}")

    try:
        page.wait_for_selector("#result", timeout=7000)
        result_text = page.text_content("#result") or ""
        assert expected in result_text
    except PlaywrightTimeoutError:
        pytest.fail(f"Timeout waiting for result in '{op}' operation")


# ----------------------------------------------------------
# Negative / Error Handling Tests
# ----------------------------------------------------------
@pytest.mark.e2e
def test_divide_by_zero(page):
    """Division by zero should show proper error message."""
    page.goto(BASE_URL)
    page.fill("#a", "10")
    page.fill("#b", "0")
    page.click("text=Divide")

    try:
        page.wait_for_selector("#result", timeout=5000)
        msg = page.text_content("#result") or ""
        assert "divide by zero" in msg.lower() or "error" in msg.lower()
    except PlaywrightTimeoutError:
        pytest.fail("Result element missing after division by zero.")


@pytest.mark.e2e
def test_invalid_input(page):
    """Non-numeric input must trigger validation error."""
    page.goto(BASE_URL)
    page.fill("#a", "abc")
    page.fill("#b", "3")
    page.click("text=Add")

    page.wait_for_selector("#result", timeout=5000)
    msg = page.text_content("#result") or ""
    assert "error" in msg.lower()


@pytest.mark.e2e
def test_missing_input(page):
    """Empty fields must return a validation message."""
    page.goto(BASE_URL)
    page.fill("#a", "")
    page.fill("#b", "")
    page.click("text=Add")

    page.wait_for_selector("#result", timeout=5000)
    msg = page.text_content("#result") or ""
    assert "error" in msg.lower() or "invalid" in msg.lower()
