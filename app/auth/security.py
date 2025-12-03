# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/18/2025
# Assignment-11: Authentication Security Utilities
# File: app/auth/security.py
# ----------------------------------------------------------
# Description:
# Implements secure password hashing, verification, and JWT
# creation/decoding. Fully aligned with the Module-11 test
# suite. Adds verify_password_hash() wrapper required by
# test_auth_security.py for bcrypt hash validation.
# ----------------------------------------------------------

from datetime import datetime, timedelta
from typing import Optional
import jwt  # Using PyJWT (not python-jose, tests patch this)
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
        - Invalid/empty → ValueError("Password must be a non-empty string")
    """
    if not isinstance(password, str) or not password.strip():
        raise ValueError("Password must be a non-empty string")

    try:
        return pwd_context.hash(password)
    except Exception as e:
        raise RuntimeError("Password hashing failed") from e


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plaintext password against its hashed version.

    Tests expect:
        - Invalid types → return False
    """
    if not isinstance(plain, str) or not isinstance(hashed, str):
        return False

    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False


def verify_password_hash(hashed: str) -> bool:
    """
    Wrapper required exclusively for Module-11 tests.

    Tests expect:
        - Function exists and returns True for valid bcrypt hashes.
        - bcrypt hashes always begin with "$2".
    """
    try:
        return isinstance(hashed, str) and hashed.startswith("$2")
    except Exception:
        return False


# ----------------------------------------------------------
# JWT Token Creation
# ----------------------------------------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a signed JWT access token.

    Tests expect:
        - Any encode failure → RuntimeError("JWT creation failed")
    """
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
    """
    Decode a JWT and return payload.

    Tests expect:
        - Expired or invalid token → RuntimeError("Invalid or expired token")
        - Other unexpected errors → RuntimeError("Token decode failure")
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    except jwt.ExpiredSignatureError:
        raise RuntimeError("Invalid or expired token")

    except jwt.InvalidTokenError:
        raise RuntimeError("Invalid or expired token")

    except Exception as e:
        raise RuntimeError("Token decode failure") from e
