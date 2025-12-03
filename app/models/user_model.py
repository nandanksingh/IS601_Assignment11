# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/16/2025
# Assignment-11: User SQLAlchemy Model 
# File: app/models/user_model.py
# ----------------------------------------------------------
# Description:
# Defines the User ORM model for authentication, ownership
# of calculations, and serialization into Pydantic schemas.
# Fully aligned with Assignment-11 test requirements:
#   • Supports deterministic id=1 seeding
#   • Converts None → "" for Pydantic (tests expect this)
#   • Secure password hashing + verification
#   • Test-safe __repr__ implementation
# ----------------------------------------------------------

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.database.dbase import Base
from app.schemas.user_schema import UserRead, UserResponse
from app.auth.security import hash_password, verify_password


class User(Base):
    __tablename__ = "users"

    # ------------------------------------------------------
    # Columns
    # ------------------------------------------------------
    id = Column(Integer, primary_key=True, index=True)

    # Nullable names → tests expect empty string fallback
    first_name = Column(String(120), nullable=True)
    last_name = Column(String(120), nullable=True)

    username = Column(String(120), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)

    password_hash = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)

    # Relationship to Calculation model
    calculations = relationship("Calculation", back_populates="user")

    # ------------------------------------------------------
    # Password Handling
    # ------------------------------------------------------
    def set_password(self, raw_password: str):
        """Hash and store a user's password."""
        self.password_hash = hash_password(raw_password)

    def verify_password(self, raw_password: str) -> bool:
        """Validate a raw password using stored hash."""
        return verify_password(raw_password, self.password_hash)

    # ------------------------------------------------------
    # Schema Conversions (must match test expectations)
    # ------------------------------------------------------
    def to_read_schema(self) -> UserRead:
        """
        Convert ORM object → UserRead Pydantic schema.
        Tests require that None becomes "" for names.
        """
        return UserRead.model_validate({
            "id": self.id,
            "first_name": self.first_name or "",
            "last_name": self.last_name or "",
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        })

    def to_response_schema(self) -> UserResponse:
        """
        Convert ORM → API response schema.
        Same None → "" rule applies here.
        """
        return UserResponse.model_validate({
            "id": self.id,
            "first_name": self.first_name or "",
            "last_name": self.last_name or "",
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        })

    # ------------------------------------------------------
    # __repr__
    # ------------------------------------------------------
    def __repr__(self):
        """
        Test-safe repr. Even if fields are missing during
        partial instantiation (e.g., factory tests), repr
        should not raise exceptions.
        """
        try:
            return f"<User id={self.id} username='{self.username}' email='{self.email}'>"
        except Exception:
            return f"<User id={self.id}>"
