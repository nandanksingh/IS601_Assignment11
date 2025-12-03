# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/15/2025
# Assignment-11: User Schemas 
# File: app/schemas/user_schema.py
# ----------------------------------------------------------
# Description:
# Pydantic v2 schemas for:
#   • UserCreate (registration)
#   • UserLogin
#   • UserRead (ORM → API safe)
#   • UserResponse (public user API)
#   • JWT token models
#
# IMPORTANT FIX:
#   first_name / last_name now allow empty string ("")
#   using min_length=0 — required to pass test_user_to_read_schema.
# ----------------------------------------------------------

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from .base import UserBase, PasswordMixin


# ----------------------------------------------------------
# User Registration Schema
# ----------------------------------------------------------
class UserCreate(UserBase, PasswordMixin):
    pass


# ----------------------------------------------------------
# Login Schema
# ----------------------------------------------------------
class UserLogin(PasswordMixin):
    username: str = Field(..., min_length=3, max_length=120)


# ----------------------------------------------------------
# ORM → API Read Schema
# ----------------------------------------------------------
class UserRead(UserBase):
    id: int
    # FIX: allow "" (required by test_user_to_read_schema)
    first_name: str = Field("", min_length=0)
    last_name: str = Field("", min_length=0)

    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ----------------------------------------------------------
# Public API User Response
# ----------------------------------------------------------
class UserResponse(BaseModel):
    id: int
    first_name: str = Field("", min_length=0)
    last_name: str = Field("", min_length=0)
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ----------------------------------------------------------
# JWT Token Model
# ----------------------------------------------------------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional[UserResponse] = None


# ----------------------------------------------------------
# JWT Token Payload
# ----------------------------------------------------------
class TokenData(BaseModel):
    sub: Optional[str] = None
