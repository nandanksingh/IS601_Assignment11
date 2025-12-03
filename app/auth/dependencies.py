# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/15/2025
# Assignment-11: Authentication Dependencies
# File: app/auth/dependencies.py
# ----------------------------------------------------------
# Description:
# Central authentication helpers used across Module-11:
#   • Database session dependency
#   • JWT encode/decode wrappers
#   • User authentication helper
#   • get_current_user() for protected routes
# ----------------------------------------------------------

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.dbase import SessionLocal
from app.models.user_model import User
from app.schemas.user_schema import TokenData
from app.auth.security import (
    verify_password,
    create_access_token as jwt_create_token,
    decode_access_token as jwt_decode_token,
)

# ----------------------------------------------------------
# REQUIRED BY TESTS
# Tests import:
#   dependencies.SECRET_KEY
#   dependencies.ALGORITHM
# ----------------------------------------------------------
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

# OAuth2 Bearer token extractor
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ----------------------------------------------------------
# Database Session Dependency (Final Correct Version)
# ----------------------------------------------------------
def get_db():
    """
    Provides a clean SQLAlchemy session.
    Compatible with FastAPI + Assignment-11 tests.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------------------------------------
# JWT Creation Wrapper
# ----------------------------------------------------------
def create_access_token(data: dict) -> str:
    """Test-visible wrapper."""
    return jwt_create_token(data)


# ----------------------------------------------------------
# JWT Verification Wrapper
# ----------------------------------------------------------
def verify_access_token(token: str) -> dict:
    """Test-visible wrapper with 401 handling."""
    try:
        return jwt_decode_token(token)
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


# ----------------------------------------------------------
# Authenticate User (username or email)
# ----------------------------------------------------------
def authenticate_user(db: Session, identifier: str, password: str):
    """
    Authenticate by username OR email.
    """
    user = (
        db.query(User)
        .filter((User.username == identifier) | (User.email == identifier))
        .first()
    )

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


# ----------------------------------------------------------
# Return Current Authenticated User
# ----------------------------------------------------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Extract user from Bearer token.
    """
    # Decode token
    try:
        payload = jwt_decode_token(token)
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    # Extract user ID (sub)
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing user id in token",
        )

    # Fetch user
    user = db.query(User).filter(User.id == int(sub)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
