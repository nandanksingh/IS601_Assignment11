# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/19/2025
# Assignment-11: User Schemas 
# File: app/schemas/user_schema.py
# ----------------------------------------------------------
# Description:
# Pydantic v2 schemas for:
#   • User registration
#   • User login
#   • User read/response formatting
#   • JWT token structures
#
# Fully compatible with Assignment-11 test cases.
# ----------------------------------------------------------

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from .base import UserBase, PasswordMixin


# ----------------------------------------------------------
# User Registration Schema
# Combines:
#   • first_name, last_name, username, email  (UserBase)
#   • password rules                           (PasswordMixin)
# ----------------------------------------------------------
class UserCreate(UserBase, PasswordMixin):
    """Schema for registering a new user."""
    pass


# ----------------------------------------------------------
# User Login Schema
# username here may be username OR email
# ----------------------------------------------------------
class UserLogin(PasswordMixin):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username or email used to sign in"
    )


# ----------------------------------------------------------
# ORM → Pydantic Read Schema
# Includes ID + timestamps
# ----------------------------------------------------------
class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ----------------------------------------------------------
# Minimal API-Safe User Response
# Tests expect:
#   id, username, email, is_active, created_at, updated_at
# ----------------------------------------------------------
class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ----------------------------------------------------------
# JWT Token Response
# ----------------------------------------------------------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional[UserResponse] = None


# ----------------------------------------------------------
# JWT Token Payload
# Tests expect TokenData.sub to be optional
# ----------------------------------------------------------
class TokenData(BaseModel):
    sub: Optional[str] = None
