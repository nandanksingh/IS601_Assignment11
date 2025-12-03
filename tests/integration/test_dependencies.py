# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/18/2025
# Assignment-11: Authentication Dependencies Tests
# File: tests/integration/test_dependencies.py
# ----------------------------------------------------------
# Description:
# Validates:
#   • create_access_token() wrapper
#   • verify_access_token() wrapper
#   • authenticate_user() DB logic
#   • get_current_user() behavior (valid, invalid, missing sub)
#   • get_db() generator lifecycle
# ----------------------------------------------------------

import pytest
from unittest.mock import MagicMock
import jwt  # PyJWT

from fastapi import HTTPException, status
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
    """Mock user instance used across tests."""
    return MagicMock(
        id=1,
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("SecurePass123"),
        is_active=True,
    )


# ----------------------------------------------------------
# Token Wrapper Tests
# ----------------------------------------------------------
def test_create_access_token_valid(fake_user):
    """Token should embed user ID (sub)."""
    token = dependencies.create_access_token({"sub": str(fake_user.id)})

    decoded = jwt.decode(
        token,
        dependencies.SECRET_KEY,
        algorithms=[dependencies.ALGORITHM],
    )

    assert decoded["sub"] == str(fake_user.id)


def test_verify_access_token_valid(fake_user):
    """verify_access_token should decode a valid token."""
    token = dependencies.create_access_token({"sub": str(fake_user.id)})
    payload = dependencies.verify_access_token(token)

    assert payload["sub"] == str(fake_user.id)


def test_verify_access_token_invalid():
    """Invalid/corrupted token → HTTP 401."""
    with pytest.raises(HTTPException) as exc:
        dependencies.verify_access_token("invalid.token.value")

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid" in exc.value.detail.lower()


# ----------------------------------------------------------
# authenticate_user() Tests
# ----------------------------------------------------------
def test_authenticate_user_valid(mock_db, fake_user):
    """Correct username + password returns user."""
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = fake_user

    mock_query.filter.return_value = mock_filter
    mock_db.query.return_value = mock_query

    result = dependencies.authenticate_user(
        mock_db, fake_user.username, "SecurePass123"
    )

    assert result.username == fake_user.username
    assert verify_password("SecurePass123", result.password_hash)


def test_authenticate_user_email(mock_db, fake_user):
    """Email login also allowed."""
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = fake_user

    mock_query.filter.return_value = mock_filter
    mock_db.query.return_value = mock_query

    assert dependencies.authenticate_user(
        mock_db, fake_user.email, "SecurePass123"
    )


def test_authenticate_user_wrong_password(mock_db, fake_user):
    """Incorrect password → None."""
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = fake_user

    mock_query.filter.return_value = mock_filter
    mock_db.query.return_value = mock_query

    result = dependencies.authenticate_user(
        mock_db, fake_user.username, "WrongPass"
    )

    assert result is None


def test_authenticate_user_not_found(mock_db):
    """No user found → None."""
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = None

    mock_query.filter.return_value = mock_filter
    mock_db.query.return_value = mock_query

    result = dependencies.authenticate_user(mock_db, "ghost", "Password123")
    assert result is None


# ----------------------------------------------------------
# get_current_user() Tests
# ----------------------------------------------------------
def test_get_current_user_valid(fake_user, mock_db):
    """Valid token + user in DB → return user."""
    token = dependencies.create_access_token({"sub": str(fake_user.id)})

    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = fake_user

    mock_query.filter.return_value = mock_filter
    mock_db.query.return_value = mock_query

    user = dependencies.get_current_user(token=token, db=mock_db)

    assert user.username == fake_user.username
    assert user.email == fake_user.email


def test_get_current_user_missing_sub(mock_db):
    """Token missing 'sub' → HTTP 401."""
    token = dependencies.create_access_token({})  # no sub

    with pytest.raises(HTTPException) as exc:
        dependencies.get_current_user(token=token, db=mock_db)

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "user id" in exc.value.detail.lower()


def test_get_current_user_user_not_found(mock_db):
    """Valid token but user not found → HTTP 401."""
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
    """Invalid token → HTTP 401."""
    with pytest.raises(HTTPException) as exc:
        dependencies.get_current_user(token="bad.token", db=mock_db)

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid" in exc.value.detail.lower()


# ----------------------------------------------------------
# get_db() Generator Lifecycle
# ----------------------------------------------------------
def test_get_db_lifecycle():
    """get_db yields one session and closes it on exit."""
    gen = dependencies.get_db()

    db = next(gen)
    assert isinstance(db, Session)

    with pytest.raises(StopIteration):
        next(gen)

    assert getattr(db, "closed", True)
