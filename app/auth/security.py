# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/18/2025
# Assignment-11: Authentication Security Utilities
# File: app/auth/security.py
# ----------------------------------------------------------
# Description:
# Implements secure password hashing, verification, and JWT
# creation/decoding. Fully aligned with the Module-11 test
# suite, including verify_password_hash wrapper required by
# test_auth_security.py.
# ----------------------------------------------------------

from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


# ----------------------------------------------------------
# Password Hashing
# ----------------------------------------------------------
def hash_password(password: str) -> str:
    if not isinstance(password, str) or not password.strip():
        raise ValueError("Password must be a non-empty string")

    try:
        return pwd_context.hash(password)
    except Exception as e:
        raise RuntimeError("Password hashing failed") from e


def verify_password(plain: str, hashed: str) -> bool:
    if not isinstance(plain, str) or not isinstance(hashed, str):
        return False

    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False


def verify_password_hash(plain: str, hashed: str) -> bool:
    """
    Wrapper used ONLY for tests.
    Tests pass two parameters:
        verify_password_hash(raw, hashed)
    """
    if not isinstance(plain, str) or not isinstance(hashed, str):
        return False

    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False


# ----------------------------------------------------------
# JWT Token Creation
# ----------------------------------------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    try:
        payload = data.copy()
        expire = datetime.utcnow() + (
            expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        payload.update({"exp": expire})

        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    except Exception as e:
        raise RuntimeError("JWT creation failed") from e


# ----------------------------------------------------------
# JWT Token Decoding
# ----------------------------------------------------------
def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    except jwt.ExpiredSignatureError:
        raise RuntimeError("Invalid or expired token")

    except jwt.InvalidTokenError:
        raise RuntimeError("Invalid or expired token")

    except Exception as e:
        raise RuntimeError("Token decode failure") from e
