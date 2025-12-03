# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/16/2025
# Assignment-11: Health Endpoint Test
# File: tests/unit/test_health.py
# ----------------------------------------------------------
# Description:
# Minimal test to verify that the /health endpoint works.
# Ensures:
#   • Router is mounted correctly
#   • Endpoint returns the expected JSON
#   • Works with TestClient (no DB or auth required)
# ----------------------------------------------------------

from fastapi.testclient import TestClient
from main import app


def test_health_endpoint():
    """Ensure /health returns a healthy status."""
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
