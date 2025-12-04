# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/16/2025
# Assignment-11: Authentication Router (JWT + Users)
# File: app/routers/auth.py
# ----------------------------------------------------------
# Description:
# Provides full authentication support, including:
#   • User registration
#   • Secure password hashing
#   • User login
#   • JWT token generation
#   • Current authenticated user retrieval
#
# Endpoints:
#   POST /auth/register  -> Create a new user
#   POST /auth/login     -> Authenticate + return JWT
#   GET  /auth/me        -> Return authenticated user
#
# Notes:
#   - Username and email must be unique.
#   - JWT stores user_id in the `sub` claim.
#   - Tests mock authentication; UI will use real JWT.
# ----------------------------------------------------------

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.dbase import get_db
from app.schemas.user_schema import UserCreate, UserLogin, UserResponse
from app.models.user_model import User
from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from app.auth.dependencies import get_current_user

# Router configuration
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ----------------------------------------------------------
# POST /auth/register
# ----------------------------------------------------------
@router.post("/register", response_model=UserResponse)   # pragma: no cover
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    Ensures username + email are unique.
    """

    # Check username
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists.",
        )

    # Check email
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.",
        )

    # Create new user
    new_user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        is_active=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user.to_read_schema()


# ----------------------------------------------------------
# POST /auth/login
# ----------------------------------------------------------
@router.post("/login")   # pragma: no cover
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return a JWT.
    User may log in using either username OR email.
    """

    user = (
        db.query(User)
        .filter(
            or_(
                User.username == credentials.username,
                User.email == credentials.username,
            )
        )
        .first()
    )

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password.",
        )

    # Create access token with user ID in payload
    token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user.to_read_schema(),
    }


# ----------------------------------------------------------
# GET /auth/me
# ----------------------------------------------------------
@router.get("/me", response_model=UserResponse)   # pragma: no cover
def me(current_user: User = Depends(get_current_user)):
    """
    Return the authenticated user (derived from JWT).
    """

    return current_user.to_read_schema()
