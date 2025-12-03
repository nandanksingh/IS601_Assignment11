# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/18/2025
# Assignment-11: User Schema Tests
# File: tests/integration/test_user_schema.py
# ----------------------------------------------------------
# Description:
# Tests Pydantic user schemas:
#   • UserCreate (registration)
#   • UserLogin
#   • UserRead
#   • UserResponse
#   • Email + password validation rules
#   • ORM → Pydantic validation for read-safe models
# Uses Pydantic v2 ValidationError.
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
        first_name="Nandan",
        last_name="Kumar",
        username="nandan123",
        email="nandan@example.com",
        password="Strong123"
    )

    assert schema.first_name == "Nandan"
    assert schema.last_name == "Kumar"
    assert schema.username == "nandan123"
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
            first_name="Nandan",
            last_name="Kumar",
            username="testuser",
            email="test@example.com",
            password=password
        )


# ----------------------------------------------------------
# UserCreate — Invalid email
# ----------------------------------------------------------
def test_user_create_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(
            first_name="A",
            last_name="B",
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
# UserLogin — Invalid username
# ----------------------------------------------------------
def test_user_login_invalid_username():
    with pytest.raises(ValidationError):
        UserLogin(
            username="ab",  # too short
            password="Strong123"
        )


# ----------------------------------------------------------
# UserRead — ORM conversion (UPDATED)
# ----------------------------------------------------------
def test_user_read_schema():
    now = datetime.utcnow()
    schema = UserRead(
        id=1,
        first_name="Nandan",
        last_name="Kumar",
        username="nk123",
        email="nk@example.com",
        is_active=True,          # ✅ FIX ADDED — REQUIRED FIELD
        created_at=now,
        updated_at=now
    )

    assert schema.id == 1
    assert schema.first_name == "Nandan"
    assert schema.email == "nk@example.com"
    assert schema.created_at == now


# ----------------------------------------------------------
# UserResponse — API safe model
# ----------------------------------------------------------
def test_user_response_schema():
    now = datetime.utcnow()
    schema = UserResponse(
        id=5,
        first_name="A",
        last_name="B",
        username="alpha",
        email="test@example.com",
        is_active=True,
        created_at=now,
        updated_at=now
    )

    assert schema.id == 5
    assert schema.username == "alpha"
    assert schema.is_active is True
