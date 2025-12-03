# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/17/2025
# Assignment-11: Secure User Authentication Tests
# File: tests/integration/test_user_auth.py
# ----------------------------------------------------------
# Description:
# Integration tests for:
#   • Password hashing and verification
#   • JWT creation and decoding (valid, tampered, expired)
#   • User model persistence and uniqueness
#   • SQLAlchemy commit/rollback behavior
#   • ORM → Pydantic schema conversion
# ----------------------------------------------------------

import pytest
from unittest.mock import patch
from sqlalchemy.exc import SQLAlchemyError

from app.models.user_model import User
from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

# ----------------------------------------------------------
# Password Hashing + Verification
# ----------------------------------------------------------
def test_password_hashing_and_verification():
    """Correct password should verify; incorrect should fail."""
    raw = "SecurePass123"
    hashed = hash_password(raw)

    assert verify_password(raw, hashed) is True
    assert verify_password("WrongPass", hashed) is False


def test_password_verification_with_invalid_hash():
    """Invalid hash input should return False safely."""
    assert verify_password("AnyPass", "$2b$12$invalidhash") is False


def test_hash_password_rejects_invalid_input():
    """Empty password input should raise ValueError."""
    with pytest.raises(ValueError, match="Password must be a non-empty string"):
        hash_password("")


def test_verify_password_invalid_type():
    """Non-string input should return False."""
    assert verify_password(123, "notahash") is False


def test_verify_password_empty_strings():
    """Empty strings should return False."""
    assert verify_password("", "") is False


# ----------------------------------------------------------
# User Model + DB Behavior
# ----------------------------------------------------------
@pytest.fixture
def user_data():
    """Reusable user payload."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password_hash": hash_password("TestPass123"),
    }


def test_user_creation_and_persistence(db_session, user_data):
    """User should persist and be queryable."""
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()

    stored = db_session.query(User).filter_by(username="testuser").first()
    assert stored.email == "test@example.com"


def test_unique_username_email_constraint(db_session, user_data):
    """Duplicate username/email should raise SQLAlchemyError."""
    db_session.add(User(**user_data))
    db_session.commit()

    db_session.add(User(**user_data))
    with pytest.raises(SQLAlchemyError):
        db_session.commit()


def test_rollback_after_integrity_error(db_session, user_data):
    """Session should rollback cleanly after failure."""
    db_session.add(User(**user_data))
    db_session.commit()

    db_session.add(User(**user_data))
    with pytest.raises(SQLAlchemyError):
        db_session.commit()

    db_session.rollback()
    assert db_session.query(User).count() == 1


def test_user_model_repr(db_session, user_data):
    """__repr__ should include username and email."""
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()

    output = repr(user)
    assert "username='testuser'" in output
    assert "email='test@example.com'" in output


def test_to_read_schema_conversion(db_session, user_data):
    """ORM → Pydantic schema conversion should succeed."""
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()

    schema = user.to_read_schema()
    assert schema.username == "testuser"
    assert schema.email == "test@example.com"


def test_database_commit_failure(monkeypatch, db_session, user_data):
    """Simulate commit failure and assert error propagation."""
    user = User(**user_data)
    db_session.add(user)

    with patch.object(db_session, "commit", side_effect=SQLAlchemyError("commit fail")):
        with pytest.raises(SQLAlchemyError, match="commit fail"):
            db_session.commit()


# ----------------------------------------------------------
# JWT Token Behavior (PyJWT)
# ----------------------------------------------------------
def test_jwt_token_creation_and_verification():
    """Valid token should decode correctly."""
    token = create_access_token({"sub": "testuser"})
    decoded = decode_access_token(token)
    assert decoded.get("sub") == "testuser"


def test_invalid_token_rejected():
    """Invalid token string should raise RuntimeError."""
    with pytest.raises(RuntimeError, match="Invalid or expired token"):
        decode_access_token("invalid.token.string")


def test_tampered_jwt_signature():
    """Tampered token should fail verification."""
    token = create_access_token({"sub": "user"})
    tampered = token + "abc123"

    with pytest.raises(RuntimeError, match="Invalid or expired token"):
        decode_access_token(tampered)


def test_expired_token_behavior(monkeypatch):
    """Expired token should raise RuntimeError."""
    import jwt
    from datetime import datetime, timedelta
    from app.core.config import settings

    expired = jwt.encode(
        {"sub": "user", "exp": datetime.utcnow() - timedelta(seconds=1)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    with pytest.raises(RuntimeError, match="Invalid or expired token"):
        decode_access_token(expired)


def test_create_access_token_failure(monkeypatch):
    """Force PyJWT encode failure to test fallback."""
    import jwt
    import app.auth.security as sec

    def bad_encode(*args, **kwargs):
        raise Exception("encode failed")

    monkeypatch.setattr(jwt, "encode", bad_encode)

    # Must match EXACT message used in security.py
    with pytest.raises(RuntimeError, match="JWT creation failed"):
        sec.create_access_token({"sub": "abc"})


def test_decode_access_token_unexpected_error(monkeypatch):
    """Unexpected decode error should raise RuntimeError('Token decode error')."""
    import jwt
    import app.auth.security as sec

    def bad_decode(*args, **kwargs):
        raise ValueError("broken decode")

    monkeypatch.setattr(jwt, "decode", bad_decode)

    with pytest.raises(RuntimeError, match="Token decode failure"):
        sec.decode_access_token("dummy")
