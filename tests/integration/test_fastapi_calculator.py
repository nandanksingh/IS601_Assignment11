# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/17/2025
# Assignment-11: Calculator API Integration Tests
# File: tests/integration/test_fastapi_calculator.py
# ----------------------------------------------------------
# Description:
# Integration test suite for FastAPI calculator endpoints.
#
# Covers:
#   • /calc/compute (ADD / SUB / MUL / DIV)
#   • JSON input validation (400/422 cases)
#   • Zero-division error handling
#   • Health check endpoint
# ----------------------------------------------------------

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


# ----------------------------------------------------------
# Arithmetic Endpoint Tests  (Assignment 11 format)
# ----------------------------------------------------------
@pytest.mark.parametrize(
    "payload, expected",
    [
        ({"type": "add", "a": 4, "b": 6}, 10),
        ({"type": "subtract", "a": 15, "b": 5}, 10),
        ({"type": "multiply", "a": 3, "b": 4}, 12),
        ({"type": "divide", "a": 20, "b": 4}, 5.0),
    ],
)
def test_arithmetic_operations(payload, expected):
    """Verify that calculation endpoint performs correct operations."""
    response = client.post("/calc/compute", json=payload)
    assert response.status_code == 200
    assert response.json()["result"] == expected


# ----------------------------------------------------------
# Validation: Invalid JSON
# ----------------------------------------------------------
def test_invalid_json_request():
    """Ensure invalid input types trigger FastAPI validation error."""
    bad_payload = {"type": "add", "a": "text", "b": 5}

    response = client.post("/calc/compute", json=bad_payload)
    assert response.status_code in (400, 422)


# ----------------------------------------------------------
# Validation: Divide-by-zero
# ----------------------------------------------------------
def test_divide_by_zero_error():
    """Ensure division by zero returns validation / computation error."""
    payload = {"type": "divide", "a": 10, "b": 0}
    response = client.post("/calc/compute", json=payload)

    assert response.status_code in (400, 422)
    assert "zero" in response.text.lower() or "error" in response.text.lower()


# ----------------------------------------------------------
# Health Check Endpoint
# ----------------------------------------------------------
def test_health_endpoint_ok():
    """Ensure /health endpoint returns OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "healthy" in response.json()["status"].lower()
