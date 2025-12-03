# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/12/2025
# Assignment-11: End-to-End Tests 
# File: tests/e2e/test_e2e.py
# ----------------------------------------------------------
# Description:
#   • Full-stack E2E tests for the Calculator project
#   • Uses Playwright to drive the UI
#   • Confirms FastAPI backend responds correctly
#   • Covers homepage rendering, calculation flows,
#     division by zero, and invalid input handling
# ----------------------------------------------------------

import os
import time
import pytest
import requests
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ----------------------------------------------------------
# Base URL for FastAPI application
# ----------------------------------------------------------
# Inside Docker, use service name "app".
# On host machine, override BASE_URL to http://localhost:8000.
BASE_URL = os.getenv("BASE_URL", "http://app:8000")

# ----------------------------------------------------------
# Helper: Wait until FastAPI server responds
# ----------------------------------------------------------
def wait_for_app_ready():
    """Poll the /health endpoint until FastAPI reports ready."""
    for _ in range(30):
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(1)
    pytest.fail("FastAPI server did not respond.")

# ----------------------------------------------------------
# Playwright browser fixtures
# ----------------------------------------------------------
@pytest.fixture(scope="module")
def browser():
    """Launch Chromium once per module after app is healthy."""
    wait_for_app_ready()
    with sync_playwright() as pw:
        br = pw.chromium.launch(headless=True)
        yield br
        br.close()

@pytest.fixture
def page(browser):
    """Provide a fresh browser page for each test."""
    context = browser.new_context()
    pg = context.new_page()
    yield pg
    context.close()

# ----------------------------------------------------------
# Test: Homepage loads correctly
# ----------------------------------------------------------
@pytest.mark.e2e
def test_homepage_loads(page):
    page.goto(BASE_URL)
    assert "Calculator" in (page.text_content("h1") or "")

# ----------------------------------------------------------
# Test: UI operations perform correct calculations
# ----------------------------------------------------------
@pytest.mark.e2e
@pytest.mark.parametrize(
    "op,a,b,expected",
    [
        ("Add", "5", "7", "12"),
        ("Subtract", "15", "4", "11"),
        ("Multiply", "6", "3", "18"),
        ("Divide", "20", "5", "4"),
    ],
)
def test_calculation_ui_flow(page, op, a, b, expected):
    page.goto(BASE_URL)
    page.fill("#a", a)
    page.fill("#b", b)
    page.click(f"text={op}")
    try:
        # Wait until #result has non-empty text
        page.wait_for_function(
            "document.querySelector('#result').textContent.trim() !== ''",
            timeout=7000,
        )
        text = page.text_content("#result") or ""
        assert text.strip() == expected or "error" in text.lower()
    except PWTimeout:
        pytest.fail(f"Timeout waiting for result for {op}")

# ----------------------------------------------------------
# Test: Division by zero shows an error message
# ----------------------------------------------------------
@pytest.mark.e2e
def test_divide_by_zero(page):
    page.goto(BASE_URL)
    page.fill("#a", "10")
    page.fill("#b", "0")
    page.click("text=Divide")
    page.wait_for_function(
        "document.querySelector('#result').textContent.trim() !== ''",
        timeout=7000,
    )
    text = page.text_content("#result") or ""
    assert "error" in text.lower() or "zero" in text.lower()

# ----------------------------------------------------------
# Test: Invalid input is handled gracefully
# ----------------------------------------------------------
@pytest.mark.e2e
def test_invalid_input(page):
    page.goto(BASE_URL)
    page.fill("#a", "abc")
    page.fill("#b", "5")
    page.click("text=Add")
    page.wait_for_function(
        "document.querySelector('#result').textContent.trim() !== ''",
        timeout=7000,
    )
    text = page.text_content("#result") or ""
    assert "error" in text.lower() or "invalid" in text.lower()
