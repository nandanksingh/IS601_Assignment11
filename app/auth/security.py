# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/17/2025
# Assignment-11: Authentication Security Utilities
# File: app/auth/security.py
# ----------------------------------------------------------
# Description:
# Provides password hashing / verification and JWT creation
# using pyjwt (NOT python-jose). All functions work safely in
# local, docker, and CI/CD environments.
# ----------------------------------------------------------

from datetime import datetime, timedelta
from typing import Optional
import jwt  # pyjwt
from passlib.context import CryptContext

from app.core.config import settings

# bcrypt hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configs
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


# ----------------------------------------------------------
# Password Hashing
# ----------------------------------------------------------
def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.
    Tests require:
        - non-string or empty password -> ValueError
    """
    if not isinstance(password, str) or not password.strip():
        raise ValueError("Password must be a non-empty string")

    try:
        return pwd_context.hash(password)
    except Exception as e:
        # explicit branch for coverage
        raise RuntimeError("Password hashing failed") from e


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plaintext password against a stored bcrypt hash.
    Tests expect False rather than exceptions.
    """
    if not isinstance(plain, str) or not isinstance(hashed, str):
        return False

    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        # explicit branch for coverage
        return False


# ----------------------------------------------------------
# REQUIRED BY TESTS
# ----------------------------------------------------------
def verify_password_hash(raw_password: str, stored_hash: str) -> bool:
    """Compatibility wrapper required by Assignment-11 tests."""
    return verify_password(raw_password, stored_hash)


# ----------------------------------------------------------
# JWT Token Creation
# ----------------------------------------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a signed JWT access token.
    Any failure -> RuntimeError("JWT creation failed")
    """
    try:
        payload = data.copy()
        expire = datetime.utcnow() + (
            expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        payload.update({"exp": expire})

        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    except Exception as e:
        # explicit branch for coverage
        raise RuntimeError("JWT creation failed") from e


# ----------------------------------------------------------
# JWT Token Decoding
# ----------------------------------------------------------
def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT token.
    On error -> RuntimeError("Invalid or expired token")
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    except jwt.ExpiredSignatureError:
        raise RuntimeError("Invalid or expired token")

    except jwt.InvalidTokenError:
        raise RuntimeError("Invalid or expired token")

    except Exception as e:
        # explicit branch for coverage
        raise RuntimeError("Token decode failure") from e