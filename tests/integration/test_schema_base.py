# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/17/2025
# Assignment-11: Pydantic Schema Validation Tests
# File: tests/integration/test_schema_base.py
# ----------------------------------------------------------
# Description:
# Integration tests for app/schemas/base.py.
#
# Covers:
#   • UserBase field validation (email, lengths, missing fields)
#   • PasswordMixin rules (uppercase, lowercase, digits, length)
#   • UserCreate combined validation (UserBase + PasswordMixin)
#   • UserLogin validation (username + password rules)
# ----------------------------------------------------------

import pytest
from pydantic import ValidationError

from app.schemas.base import (
    UserBase,
    PasswordMixin,
    UserCreate,
    UserLogin,
)


# ----------------------------------------------------------
# UserBase Schema Tests
# ----------------------------------------------------------
def test_user_base_valid():
    """Valid UserBase payload should initialize successfully."""
    data = {
        "first_name": "Nandan",
        "last_name": "Kumar",
        "username": "nandan123",
        "email": "nandan@example.com",
    }
    user = UserBase(**data)

    assert user.first_name == "Nandan"
    assert user.last_name == "Kumar"
    assert user.username == "nandan123"
    assert user.email == "nandan@example.com"


def test_user_base_invalid_email():
    """Invalid email format should trigger ValidationError."""
    invalid_data = {
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser",
        "email": "invalid-email",
    }
    with pytest.raises(ValidationError):
        UserBase(**invalid_data)


def test_user_base_missing_field():
    """Missing required fields must raise ValidationError."""
    with pytest.raises(ValidationError):
        UserBase(first_name="OnlyName")  # Missing last_name, username, email


# ----------------------------------------------------------
# PasswordMixin Schema Tests
# ----------------------------------------------------------
@pytest.mark.parametrize("password", [
    "SecurePass123",
    "AnotherGood1",
])
def test_password_mixin_valid(password):
    """Accept passwords that meet all required strength rules."""
    schema = PasswordMixin(password=password)
    assert schema.password == password


@pytest.mark.parametrize("password, expected_msg", [
    ("short", "at least 6 characters"),
    ("lowercase1", "uppercase"),
    ("UPPERCASE1", "lowercase"),
    ("NoDigitsHere", "digit"),
])
def test_password_mixin_invalid(password, expected_msg):
    """Reject weak passwords missing uppercase, lowercase, or digits."""
    with pytest.raises(ValidationError) as exc:
        PasswordMixin(password=password)
    assert expected_msg.lower() in str(exc.value).lower()


def test_password_mixin_missing_password():
    """Password is required — test both missing and None cases."""
    # Case 1: password key missing
    with pytest.raises(ValidationError) as exc1:
        PasswordMixin()  # type: ignore
    assert "Password is required" in str(exc1.value)

    # Case 2: explicitly None
    with pytest.raises(ValidationError) as exc2:
        PasswordMixin(password=None)  # type: ignore
    assert "Password is required" in str(exc2.value)


# ----------------------------------------------------------
# UserCreate Schema Tests
# ----------------------------------------------------------
def test_user_create_valid():
    """Validate full user creation schema (UserBase + PasswordMixin)."""
    data = {
        "first_name": "Nandan",
        "last_name": "Kumar",
        "username": "nandan123",
        "email": "nandan@example.com",
        "password": "SecurePass123",
    }
    schema = UserCreate(**data)

    assert schema.username == "nandan123"
    assert schema.email == "nandan@example.com"
    assert schema.password == "SecurePass123"


def test_user_create_invalid_password():
    """Weak password should be rejected during user creation."""
    data = {
        "first_name": "Nandan",
        "last_name": "Kumar",
        "username": "nandan123",
        "email": "nandan@example.com",
        "password": "weak",
    }
    with pytest.raises(ValidationError):
        UserCreate(**data)


# ----------------------------------------------------------
# UserLogin Schema Tests
# ----------------------------------------------------------
def test_user_login_valid():
    """Valid username/email and password should pass."""
    data = {"username": "nandan@example.com", "password": "SecurePass123"}
    schema = UserLogin(**data)

    assert schema.username == "nandan@example.com"
    assert schema.password == "SecurePass123"


@pytest.mark.parametrize("username", ["ab", "", None])
def test_user_login_invalid_username(username):
    """Reject usernames that are too short or missing."""
    data = {"username": username, "password": "SecurePass123"}
    with pytest.raises(ValidationError):
        UserLogin(**data)


def test_user_login_invalid_password():
    """Password must still meet minimum rules in login schema."""
    with pytest.raises(ValidationError):
        UserLogin(username="nandan@example.com", password="short")
