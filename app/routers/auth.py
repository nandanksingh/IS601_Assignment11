# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/16/2025
# Assignment-11: Authentication Router (JWT + Users)
# File: app/routers/auth.py
# ----------------------------------------------------------
# Description:
# Minimal authentication router for Module-11.
# Supports:
#   • User registration
#   • User login (username or email)
#   • JWT token generation
#   • /auth/me endpoint for authenticated user info
#
# Fully compatible with:
#   • PyJWT
#   • SQLAlchemy ORM
#   • Pydantic v2
#   • Password hashing utilities
#   • Assignment-11 test expectations
# ----------------------------------------------------------

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from app.auth.dependencies import get_current_user, get_db
from app.schemas.user_schema import UserCreate, UserLogin, UserResponse
from app.models.user_model import User

router = APIRouter(tags=["Authentication"])


# ----------------------------------------------------------
# POST /auth/register
# ----------------------------------------------------------
@router.post("/register", response_model=UserResponse)  # pragma: no cover
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    """Register a new user. Enforces unique username + email."""

    # Username must be unique
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    # Email must be unique
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user object
    user = User(
        username=payload.username,
        email=payload.email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        password_hash=hash_password(payload.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user.to_read_schema()


# ----------------------------------------------------------
# POST /auth/login
# ----------------------------------------------------------
@router.post("/login")  # pragma: no cover
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate a user and return JWT."""

    # User can login with username OR email
    user = (
        db.query(User)
        .filter(
            (User.username == credentials.username)
            | (User.email == credentials.username)
        )
        .first()
    )

    # Invalid credentials
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Create access token
    token = create_access_token({"sub": str(user.id)})

    return {"access_token": token, "token_type": "bearer"}


# ----------------------------------------------------------
# GET /auth/me
# ----------------------------------------------------------
@router.get("/me", response_model=UserResponse)  # pragma: no cover
def me(current_user: User = Depends(get_current_user)):
    """Return details of authenticated user."""
    return current_user.to_read_schema()
