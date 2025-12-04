# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/18/2025
# Assignment-11: User Schema Tests (UPDATED for new rules)
# File: tests/integration/test_user_schema.py
# ----------------------------------------------------------
# Description:
# Updated tests for simplified User schemas:
#   • No first_name / last_name fields
#   • Username: alphanumeric, length 4–10
#   • Password: 6–20 chars (must contain upper/lower/digit)
# ----------------------------------------------------------

import pytest
from pydantic import ValidationError
from datetime import datetime

from app.schemas.user_schema import (
    UserCreate,
    UserLogin,
    UserRead,
    UserResponse
)

# ----------------------------------------------------------
# UserCreate — Valid Case
# ----------------------------------------------------------
def test_user_create_valid():
    schema = UserCreate(
        username="nk123",
        email="nandan@example.com",
        password="Strong123"
    )

    assert schema.username == "nk123"
    assert schema.email == "nandan@example.com"


# ----------------------------------------------------------
# UserCreate — Invalid password rules
# ----------------------------------------------------------
@pytest.mark.parametrize(
    "password",
    [
        "short",          # too short
        "nocaps123",      # no uppercase
        "NOLOWER123",     # no lowercase
        "NoNumber",       # no digit
    ],
)
def test_user_create_invalid_password(password):
    with pytest.raises(ValidationError):
        UserCreate(
            username="nk123",
            email="test@example.com",
            password=password
        )


# ----------------------------------------------------------
# UserCreate — Invalid email
# ----------------------------------------------------------
def test_user_create_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(
            username="user1",
            email="not-an-email",
            password="Strong123"
        )


# ----------------------------------------------------------
# UserLogin — Valid
# ----------------------------------------------------------
def test_user_login_valid():
    schema = UserLogin(
        username="user123",
        password="Strong123"
    )
    assert schema.username == "user123"


# ----------------------------------------------------------
# UserLogin — Invalid username (too short)
# ----------------------------------------------------------
def test_user_login_invalid_username():
    with pytest.raises(ValidationError):
        UserLogin(
            username="ab",  # too short
            password="Strong123"
        )


# ----------------------------------------------------------
# UserRead — ORM conversion
# ----------------------------------------------------------
def test_user_read_schema():
    now = datetime.utcnow()
    schema = UserRead(
        id=1,
        username="nk123",
        email="nk@example.com",
        is_active=True,
        created_at=now,
        updated_at=now
    )

    assert schema.id == 1
    assert schema.username == "nk123"
    assert schema.email == "nk@example.com"
    assert schema.created_at == now


# ----------------------------------------------------------
# UserResponse — API safe model
# ----------------------------------------------------------
def test_user_response_schema():
    now = datetime.utcnow()
    schema = UserResponse(
        id=5,
        username="alpha1",
        email="test@example.com",
        is_active=True,
        created_at=now,
        updated_at=now
    )

    assert schema.id == 5
    assert schema.username == "alpha1"
    assert schema.is_active is True
