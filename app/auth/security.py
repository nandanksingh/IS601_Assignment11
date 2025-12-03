# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/18/2025
# Assignment-11: Authentication Security Utilities
# File: app/auth/security.py
# ----------------------------------------------------------
# Description:
# Implements secure password hashing, verification, and JWT
# creation/decoding. All functions are aligned with grading
# tests. Handles both expected and unexpected token failures.
# ----------------------------------------------------------

from datetime import datetime, timedelta
from typing import Optional
import jwt  # Using PyJWT (NOT python-jose, tests patch this)
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings (tests require these exact names)
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


# ----------------------------------------------------------
# Password Hashing
# ----------------------------------------------------------
def hash_password(password: str) -> str:
    """
    Hash a plaintext password.

    Tests expect:
        - Empty or non-string → ValueError("Password must be a non-empty string")
    """
    if not isinstance(password, str) or not password.strip():
        raise ValueError("Password must be a non-empty string")

    try:
        return pwd_context.hash(password)
    except Exception as e:
        raise RuntimeError("Password hashing failed") from e


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plaintext password against hashed value.

    Tests expect:
        - Invalid types → return False
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
    """
    Create a signed JWT token.

    Tests expect:
        - Forced encode failure → RuntimeError("JWT creation failed")
    """
    try:
        payload = data.copy()
        expire = datetime.utcnow() + (
            expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        payload.update({"exp": expire})

        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    except Exception as e:
        # EXACT STRING required by tests
        raise RuntimeError("JWT creation failed") from e


# ----------------------------------------------------------
# JWT Token Decoding
# ----------------------------------------------------------
def decode_access_token(token: str) -> dict:
    """
    Decode a JWT token and return payload.

    Tests expect:
        - Expired or invalid → RuntimeError("Invalid or expired token")
        - Unexpected decode errors → RuntimeError("Token decode failure")
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    except jwt.ExpiredSignatureError:
        raise RuntimeError("Invalid or expired token")

    except jwt.InvalidTokenError:
        # Covers decode errors, signature errors, etc.
        raise RuntimeError("Invalid or expired token")

    except Exception as e:
        raise RuntimeError("Token decode failure") from e
