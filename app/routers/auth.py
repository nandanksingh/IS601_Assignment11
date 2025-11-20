# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/16/2025
# Assignment-11: Authentication Router (JWT + Users)
# File: app/routers/auth.py
# ----------------------------------------------------------
# Description:
# Handles user registration, login, password hashing,
# JWT token generation, and authenticated user retrieval.
# ----------------------------------------------------------

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.dbase import get_session
from app.schemas.user_schema import UserCreate, UserLogin, UserResponse
from app.models.user_model import User
from app.auth.security import hash_password, verify_password, create_access_token
from app.auth.dependencies import get_current_user

router = APIRouter()


# ----------------------------------------------------------
# POST /auth/register
# ----------------------------------------------------------
@router.post("/register", response_model=UserResponse)   # pragma: no cover
def register_user(payload: UserCreate, db: Session = Depends(get_session)):
    """Register a new user (username + email must be unique)."""

    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Username already exists")

    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user.to_read_schema()


# ----------------------------------------------------------
# POST /auth/login
# ----------------------------------------------------------
@router.post("/login")   # pragma: no cover
def login(credentials: UserLogin, db: Session = Depends(get_session)):
    """Authenticate user & return JWT."""

    user = (
        db.query(User)
        .filter(
            (User.username == credentials.username)
            | (User.email == credentials.username)
        )
        .first()
    )

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token = create_access_token({"sub": str(user.id)})

    return {"access_token": token, "token_type": "bearer"}


# ----------------------------------------------------------
# GET /auth/me
# ----------------------------------------------------------
@router.get("/me", response_model=UserResponse)   # pragma: no cover
def me(current_user: User = Depends(get_current_user)):
    """Return authenticated user."""
    return current_user.to_read_schema()
