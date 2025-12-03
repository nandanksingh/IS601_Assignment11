# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/15/2025
# Assignment-11: Calculation Router Tests
# File: tests/integration/test_rout_calc.py
# ----------------------------------------------------------

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from app.database import dbase

client = TestClient(app)


# ----------------------------------------------------------
# Helper: reset DB schema before each test
# ----------------------------------------------------------
@pytest.fixture(autouse=True)
def setup_db():
    dbase.init_db()
    from app.models.user_model import User
    from app.models.cal_models import Calculation
    dbase.Base.metadata.drop_all(bind=dbase.engine)
    dbase.Base.metadata.create_all(bind=dbase.engine)

    # Insert test user with id=1 to satisfy FK constraint
    session = dbase.SessionLocal()
    user = User(
        id=1,
        first_name="Test",
        last_name="User",
        username="testuser",
        email="test@example.com",
        is_active=True,
    )
    user.set_password("pass123")
    session.add(user)
    session.commit()
    session.close()

    yield
    dbase.Base.metadata.drop_all(bind=dbase.engine)


# ----------------------------------------------------------
# Success Case
# ----------------------------------------------------------
def test_compute_calculation_success():
    payload = {"type": "add", "a": 5, "b": 3}
    response = client.post("/calc/compute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 8
    assert data["type"] == "add"


# ----------------------------------------------------------
# Invalid Factory Input (schema-level)
# ----------------------------------------------------------
def test_compute_calculation_invalid_type():
    payload = {"type": "foobar", "a": 1, "b": 2}
    response = client.post("/calc/compute", json=payload)
    assert response.status_code == 422  # schema validation error
    assert "detail" in response.json()


# ----------------------------------------------------------
# Database Error Path
# ----------------------------------------------------------
def test_compute_calculation_db_error(monkeypatch):
    payload = {"type": "add", "a": 2, "b": 2}

    def broken_add(self, obj):
        raise Exception("forced DB failure")

    monkeypatch.setattr(Session, "add", broken_add)

    response = client.post("/calc/compute", json=payload)
    assert response.status_code == 500
    assert "Database error" in response.json()["error"]