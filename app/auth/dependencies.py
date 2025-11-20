# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/18/2025
# Assignment-11: Authentication Dependencies
# File: app/auth/dependencies.py
# ----------------------------------------------------------
# Description:
# Test-aligned authentication logic:
#   • DB session dependency
#   • User authentication
#   • JWT create/verify wrappers
#   • get_current_user() for routes
# ----------------------------------------------------------

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.dbase import get_session
from app.models.user_model import User
from app.schemas.user_schema import TokenData
from app.auth.security import (
    hash_password,
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
#SECRET_KEY = settings.JWT_SECRET_KEY
#ALGORITHM = settings.JWT_ALGORITHM
# ----------------------------------------------------------
# JWT Key + Algorithm (tests expect these names)
# ----------------------------------------------------------
SECRET_KEY = getattr(settings, "JWT_SECRET_KEY", settings.SECRET_KEY)
ALGORITHM = getattr(settings, "JWT_ALGORITHM", settings.ALGORITHM)

# ----------------------------------------------------------
# DB Session Dependency
# ----------------------------------------------------------
def get_db():
    db = get_session()
    db.closed = False
    try:
        yield db
    finally:
        db.close()
        db.closed = True


# ----------------------------------------------------------
# Token Creation Wrapper (test_create_access_token_wrapper)
# ----------------------------------------------------------
def create_access_token(data: dict) -> str:
    return jwt_create_token(data)


# ----------------------------------------------------------
# Token Verification Wrapper
# ----------------------------------------------------------
def verify_access_token(token: str) -> dict:
    try:
        return jwt_decode_token(token)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


# ----------------------------------------------------------
# Authenticate User
# ----------------------------------------------------------
def authenticate_user(db: Session, identifier: str, password: str):
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
# Get Current User (multiple test expectations)
# ----------------------------------------------------------
def get_current_user(
    token: str,
    db: Session = Depends(get_db),
):
    # 1. Missing token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    # 2. Decode
    try:
        payload = jwt_decode_token(token)
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    # 3. Missing "sub" field
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing user id in token",   
        )

    # 4. User lookup
    user = db.query(User).filter(User.id == int(sub)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
