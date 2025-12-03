# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/19/2025
# Assignment-11: User SQLAlchemy Model (Final Version)
# File: app/models/user_model.py
# ----------------------------------------------------------
# Description:
# Defines the SQLAlchemy ORM model for User accounts.
# Supports:
#   • Unique username & email
#   • Secure password hashing and verification
#   • Required fields: first_name, last_name, is_active
#   • Timestamp tracking (created_at, updated_at)
#   • Relationship to Calculation model
#   • ORM → Pydantic conversion (safe, complete, test-aligned)
#   • Fully compatible with SQLAlchemy 2.x and Pydantic v2
# ----------------------------------------------------------

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    func,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database.dbase import Base
from app.auth.security import hash_password, verify_password
from app.schemas.user_schema import UserResponse


class User(Base):
    """Represents an authenticated user in the system."""

    __tablename__ = "users"

    # ------------------------------------------------------
    # Core Columns
    # ------------------------------------------------------
    id = Column(Integer, primary_key=True, index=True)

    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)

    # Required fields expected by tests
    first_name = Column(String(50), nullable=False, default="Unknown")
    last_name = Column(String(50), nullable=False, default="Unknown")
    is_active = Column(Boolean, nullable=False, default=True)

    # Secure password storage
    password_hash = Column(String(255), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Unique constraints
    __table_args__ = (
        UniqueConstraint("username", name="uq_user_username"),
        UniqueConstraint("email", name="uq_user_email"),
    )

    # ------------------------------------------------------
    # Relationship: user.calculations
    # ------------------------------------------------------
    calculations = relationship(
        "Calculation",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # ------------------------------------------------------
    # Password Helpers
    # ------------------------------------------------------
    def set_password(self, raw_password: str):
        """Hash and store the user's password."""
        if not raw_password or not isinstance(raw_password, str):
            raise ValueError("Password must be a non-empty string")
        self.password_hash = hash_password(raw_password)

    def verify_password(self, raw_password: str) -> bool:
        """Safely verify password correctness."""
        try:
            return verify_password(raw_password, self.password_hash)
        except Exception:
            return False

    # ------------------------------------------------------
    # ORM → Pydantic Conversion (Test-Aligned)
    # ------------------------------------------------------
    def to_read_schema(self) -> UserResponse:
        """
        Convert ORM → Pydantic UserResponse.
        Tests require ALL fields to be explicitly provided.
        """
        return UserResponse.model_validate({
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        })

    # ------------------------------------------------------
    # Safe Debug Representation
    # ------------------------------------------------------
    def __repr__(self):
        try:
            return (
                f"User(id={self.id}, username='{self.username}', "
                f"email='{self.email}')"
            )
        except Exception:
            return f"User(id={getattr(self, 'id', None)})"
