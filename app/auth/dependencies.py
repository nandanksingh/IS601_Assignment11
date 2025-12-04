# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/18/2025
# Assignment-11: Authentication Dependencies
# File: app/auth/dependencies.py
# ----------------------------------------------------------
# Description:
# Provides reusable authentication utilities:
#   • get_db()  → DB session dependency
#   • JWT wrappers for test suite compatibility
#   • authenticate_user() for login
#   • get_current_user() to enforce protected routes
#
# Notes:
#   - Tests import SECRET_KEY and ALGORITHM directly.
#   - get_current_user() intentionally accepts token as plain
#     string (not OAuth2 scheme) because tests expect it.
# ----------------------------------------------------------

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.config import settings
from app.database.dbase import get_session
from app.models.user_model import User
from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token as jwt_create_token,
    decode_access_token as jwt_decode_token,
)

# ----------------------------------------------------------
# REQUIRED BY TESTS:
# tests import dependencies.SECRET_KEY and dependencies.ALGORITHM
# ----------------------------------------------------------
SECRET_KEY = getattr(settings, "JWT_SECRET_KEY", settings.SECRET_KEY)
ALGORITHM = getattr(settings, "JWT_ALGORITHM", settings.ALGORITHM)


# ----------------------------------------------------------
# DB Session Dependency
# ----------------------------------------------------------
def get_db():
    """
    Provides a SQLAlchemy session for request handling.
    Test suite checks .closed flag, so it is included.
    """
    db = get_session()
    db.closed = False

    try:
        yield db
    finally:
        db.close()
        db.closed = True


# ----------------------------------------------------------
# JWT Token Creation Wrapper (test_create_access_token_wrapper)
# ----------------------------------------------------------
def create_access_token(data: dict) -> str:
    """
    Wrapper around core JWT creation function.
    Tests import THIS wrapper, not the security module directly.
    """
    return jwt_create_token(data)


# ----------------------------------------------------------
# JWT Token Verification Wrapper
# ----------------------------------------------------------
def verify_access_token(token: str) -> dict:
    """
    Validate JWT and return decoded payload.
    Raises HTTP 401 if token is invalid.
    """
    try:
        return jwt_decode_token(token)
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


# ----------------------------------------------------------
# Authenticate User (used by POST /auth/login)
# ----------------------------------------------------------
def authenticate_user(db: Session, identifier: str, password: str):
    """
    Return User if credentials match, else None.

    identifier → username or email
    """

    user = (
        db.query(User)
        .filter(
            or_(
                User.username == identifier,
                User.email == identifier,
            )
        )
        .first()
    )

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


# ----------------------------------------------------------
# Get Current User from Token
# ----------------------------------------------------------
def get_current_user(
    token: str,
    db: Session = Depends(get_db),
):
    """
    Extract user from a plain JWT passed as `token`.
    Tests intentionally DO NOT use OAuth2PasswordBearer.
    """

    # 1. Token missing
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    # 2. Decode JWT
    try:
        payload = jwt_decode_token(token)
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    # 3. Validate "sub" claim
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing user id in token",
        )

    # 4. Lookup user
    user = db.query(User).filter(User.id == int(sub)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
