# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/19/2025
# Assignment-11: User Schemas (FINAL)
# File: app/schemas/user_schema.py
# ----------------------------------------------------------

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
import re


# ----------------------------------------------------------
# PASSWORD VALIDATION
# ----------------------------------------------------------
def validate_password(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("Password must be a string")

    if len(value) < 6 or len(value) > 20:
        raise ValueError("Password length must be 6–20 characters")

    if not re.search(r"[A-Z]", value):
        raise ValueError("Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", value):
        raise ValueError("Password must contain at least one lowercase letter")

    if not re.search(r"\d", value):
        raise ValueError("Password must contain at least one digit")

    return value


# ----------------------------------------------------------
# USERNAME VALIDATION (alphanumeric, 4–10 chars)
# ----------------------------------------------------------
def validate_username(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("Username must be a string")

    if len(value) < 4 or len(value) > 10:
        raise ValueError("Username length must be 4–10 characters")

    if not re.match(r"^[A-Za-z0-9]+$", value):
        raise ValueError("Username must be alphanumeric")

    return value


# ----------------------------------------------------------
# USER CREATE (registration)
# ----------------------------------------------------------
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    # VALIDATORS
    _normalize_username = field_validator("username")(validate_username)
    _normalize_password = field_validator("password")(validate_password)


# ----------------------------------------------------------
# USER LOGIN
# ----------------------------------------------------------
class UserLogin(BaseModel):
    username: str
    password: str

    _normalize_username = field_validator("username")(validate_username)
    _normalize_password = field_validator("password")(validate_password)


# ----------------------------------------------------------
# USER READ (ORM → API)
# ----------------------------------------------------------
class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ----------------------------------------------------------
# USER RESPONSE (API SAFE)
# ----------------------------------------------------------
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ----------------------------------------------------------
# JWT TOKEN MODELS
# ----------------------------------------------------------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional[UserResponse] = None


class TokenData(BaseModel):
    sub: Optional[str] = None
