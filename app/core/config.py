# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/16/2025
# Assignment-11: Central Application Configuration
# File: app/core/config.py
# ----------------------------------------------------------
# Description:
# Centralized configuration management for the FastAPI project.
#
# Responsibilities:
#   • Load environment variables from `.env`
#   • Provide secure defaults for JWT, DB URLs, and runtime modes
#   • Expose helper utilities used extensively in tests:
#         - reload_settings() → reinitialize settings after env change
#         - get_environment_mode() → convert ENV into human-readable text
# ----------------------------------------------------------

import os
from pydantic_settings import BaseSettings


# ----------------------------------------------------------
#  Settings Class (Pydantic v2)
# ----------------------------------------------------------
class Settings(BaseSettings):
    """
    Main configuration container for:
      - Database URLs
      - Authentication & JWT settings
      - Environment mode (dev / prod / testing)
      - Application-wide defaults

    Loaded from:
      • Environment variables
      • .env file in the project root
    """

    # -----------------------------
    # Database Settings
    # -----------------------------
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")

    # -----------------------------
    # Security / JWT
    # -----------------------------
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super_secret_key_123")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    )

    # -----------------------------
    # Runtime Environment
    # -----------------------------
    ENV: str = os.getenv("ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")  # ✅ Added for logging setup

    # -----------------------------
    # Helper Properties
    # -----------------------------
    @property
    def is_dev(self) -> bool:
        """Return True if running in development mode."""
        return self.ENV.lower() == "development"

    @property
    def is_prod(self) -> bool:
        """Return True if running in production mode."""
        return self.ENV.lower() == "production"

    @property
    def is_test(self) -> bool:
        """Return True if running under pytest or ENV=testing."""
        return self.ENV.lower() == "testing"

    # -----------------------------
    # Pydantic model configuration
    # -----------------------------
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


# ----------------------------------------------------------
# Global settings instance used throughout the project
# ----------------------------------------------------------
settings = Settings()


# ----------------------------------------------------------
# TEST HOOKS — Required by test suite
# ----------------------------------------------------------
def reload_settings() -> Settings:
    """
    Re-load settings after environment variables change.
    Tests use this to verify dynamic environment behavior.

    Example:
        os.environ["ENV"] = "testing"
        new_settings = reload_settings()
    """
    global settings
    settings = Settings()
    return settings


def get_environment_mode(env: str) -> str:
    """
    Convert raw ENV names into human-readable mode labels.

    Expected output:
      • "development" → "development mode"
      • "production"  → "production mode"
      • "testing"     → "testing mode"
      • anything else → "Unknown environment"
    """
    env = (env or "").lower()

    if env == "development":
        return "development mode"
    elif env == "production":
        return "production mode"
    elif env == "testing":
        return "testing mode"
    else:
        return "Unknown environment"