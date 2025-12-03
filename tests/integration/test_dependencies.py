# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/19/2025
# Assignment-11: Authentication Dependencies (OAuth2 + JWT)
# File: tests/integration/test_dependencies.py
# ----------------------------------------------------------
# Description:
# Integration test suite for authentication dependencies.
#
# Covered components:
#   • JWT creation + verification
#   • Token decoding / invalid token handling
#   • authenticate_user() logic with mock DB
#   • get_current_user() behavior using JWT + DB lookup
#   • get_db() lifecycle validation
# ----------------------------------------------------------

import pytest
from unittest.mock import MagicMock
from jose import jwt
from fastapi import HTTPException, status
from datetime import timedelta

from sqlalchemy.orm import Session
from app.auth import dependencies
from app.auth.security import hash_password, verify_password


# ----------------------------------------------------------
# Fixtures
# ----------------------------------------------------------
@pytest.fixture
def mock_db():
    """Provide a mocked SQLAlchemy DB session."""
    return MagicMock()


@pytest.fixture
def fake_user():
    """Provide a mocked user object for authentication tests."""
    return MagicMock(
        id=1,
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("SecurePass123"),
        is_active=True,
    )


# ----------------------------------------------------------
# Token Utility Tests
# ----------------------------------------------------------
def test_create_access_token_wrapper(fake_user):
    """create_access_token wrapper should embed user ID."""
    token = dependencies.create_access_token({"sub": str(fake_user.id)})
    decoded = jwt.decode(token, dependencies.SECRET_KEY, algorithms=[dependencies.ALGORITHM])
    assert decoded["sub"] == str(fake_user.id)


def test_verify_access_token_wrapper_valid(fake_user):
    """verify_access_token should decode valid token."""
    token = dependencies.create_access_token({"sub": str(fake_user.id)})
    payload = dependencies.verify_access_token(token)
    assert payload["sub"] == str(fake_user.id)


def test_verify_access_token_wrapper_invalid():
    """Invalid token should raise HTTP_401."""
    with pytest.raises(HTTPException) as exc:
        dependencies.verify_access_token("invalid.token.value")
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid" in exc.value.detail.lower()


# ----------------------------------------------------------
# authenticate_user() Tests
# ----------------------------------------------------------
def test_authenticate_user_valid(mock_db, fake_user):
    """Valid credentials should return user."""
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = fake_user
    mock_query.filter.return_value = mock_filter
    mock_db.query.return_value = mock_query

    result = dependencies.authenticate_user(mock_db, fake_user.username, "SecurePass123")
    assert result.username == fake_user.username
    assert verify_password("SecurePass123", result.password_hash)


def test_authenticate_user_with_email(mock_db, fake_user):
    """Email-based login should succeed."""
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = fake_user
    mock_query.filter.return_value = mock_filter
    mock_db.query.return_value = mock_query

    result = dependencies.authenticate_user(mock_db, fake_user.email, "SecurePass123")
    assert result.email == fake_user.email


def test_authenticate_user_invalid_password(mock_db, fake_user):
    """Wrong password should return None."""
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = fake_user
    mock_query.filter.return_value = mock_filter
    mock_db.query.return_value = mock_query

    result = dependencies.authenticate_user(mock_db, fake_user.username, "WrongPass")
    assert result is None


def test_authenticate_user_not_found(mock_db):
    """Missing user should return None."""
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = None
    mock_query.filter.return_value = mock_filter
    mock_db.query.return_value = mock_query

    result = dependencies.authenticate_user(mock_db, "ghost", "password123")
    assert result is None


# ----------------------------------------------------------
# get_current_user() Tests
# ----------------------------------------------------------
def test_get_current_user_valid_token(mock_db, fake_user):
    """Valid token should return user."""
    token = dependencies.create_access_token({"sub": str(fake_user.id)})

    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = fake_user
    mock_query.filter.return_value = mock_filter
    mock_db.query.return_value = mock_query

    result = dependencies.get_current_user(token=token, db=mock_db)
    assert result.username == fake_user.username
    assert result.email == fake_user.email


def test_get_current_user_missing_sub(mock_db):
    """Token missing 'sub' should raise HTTP_401."""
    token = dependencies.create_access_token({})

    with pytest.raises(HTTPException) as exc:
        dependencies.get_current_user(token=token, db=mock_db)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "user id" in exc.value.detail.lower()


def test_get_current_user_user_not_found(mock_db):
    """User lookup failure should raise HTTP_401."""
    token = dependencies.create_access_token({"sub": "999"})

    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = None
    mock_query.filter.return_value = mock_filter
    mock_db.query.return_value = mock_query

    with pytest.raises(HTTPException) as exc:
        dependencies.get_current_user(token=token, db=mock_db)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "not found" in exc.value.detail.lower()


def test_get_current_user_invalid_token(mock_db):
    """Invalid token should raise HTTP_401."""
    with pytest.raises(HTTPException) as exc:
        dependencies.get_current_user(token="invalid.token", db=mock_db)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid" in exc.value.detail.lower()


# ----------------------------------------------------------
# get_db() Lifecycle Test
# ----------------------------------------------------------
def test_get_db_session_lifecycle():
    """Ensure get_db yields and closes session properly."""
    gen = dependencies.get_db()
    db = next(gen)
    assert isinstance(db, Session)

    with pytest.raises(StopIteration):
        next(gen)

    assert getattr(db, "closed", True)