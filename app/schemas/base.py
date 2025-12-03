# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/14/2025
# Assignment-11: Secure User Model (Pydantic Validation)
# File: app/schemas/base.py
# ----------------------------------------------------------
# Description:
# Core Pydantic schemas providing reusable validation logic
# for user creation and authentication.
#
# Defines:
#   • UserBase        → first_name, last_name, username, email
#   • PasswordMixin   → strong password validation (uppercase,
#                       lowercase, digit, minimum length)
#
# Fully compatible with:
#   • Pydantic v2
#   • SQLAlchemy ORM
#   • Assignment-11 test suite
# ----------------------------------------------------------

from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator


# ----------------------------------------------------------
# Base Schema for Shared User Fields
# Tests require:
#   first_name: str
#   last_name: str
#   username : str
#   email    : EmailStr
# ----------------------------------------------------------
class UserBase(BaseModel):
    """
    Shared fields used across user schemas.
    Includes first_name, last_name, username, and email.
    """

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username for the user",
    )

    email: EmailStr = Field(
        ...,
        description="Valid email address of the user",
    )

    model_config = ConfigDict(from_attributes=True)


# ----------------------------------------------------------
# Password Validation Mixin
# Enforces:
#   • Minimum 6 characters
#   • At least one lowercase letter
#   • At least one uppercase letter
#   • At least one digit
# ----------------------------------------------------------
class PasswordMixin(BaseModel):
    """Reusable password validation logic."""

    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="Password must include uppercase, lowercase, and digits.",
    )

    @model_validator(mode="before")
    @classmethod
    def validate_password(cls, values):
        pwd = values.get("password", "")

        if not pwd:
            raise ValueError("Password is required.")
        if len(pwd) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        if not any(c.islower() for c in pwd):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not any(c.isupper() for c in pwd):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in pwd):
            raise ValueError("Password must contain at least one numeric digit.")

        return values
