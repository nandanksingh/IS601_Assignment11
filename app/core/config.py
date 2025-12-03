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
# Pydantic Settings Class (v2)
# ----------------------------------------------------------
class Settings(BaseSettings):
    """
    Main configuration container for:
      • Database URL resolution
      • JWT & security settings
      • Environment mode control (dev / prod / testing)
      • Logging level
    Loaded automatically from:
      • Environment variables
      • .env file in project root
    """

    # ------------------------------------------------------
    # Database Configuration
    # ------------------------------------------------------
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")

    # ------------------------------------------------------
    # JWT + Security Settings
    # ------------------------------------------------------
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super_secret_key_123")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    )

    # ------------------------------------------------------
    # Environment Mode (development / production / testing)
    # ------------------------------------------------------
    ENV: str = os.getenv("ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # ------------------------------------------------------
    # Helper Flags
    # ------------------------------------------------------
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

    # ------------------------------------------------------
    # Pydantic Model Configuration
    # ------------------------------------------------------
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


# ----------------------------------------------------------
# Global Singleton Settings Instance
# ----------------------------------------------------------
settings = Settings()


# ----------------------------------------------------------
# TEST UTILITIES (Required for Module-11 & CI)
# ----------------------------------------------------------
def reload_settings() -> Settings:
    """
    Re-load configuration after environment variables change.

    Example in tests:
        os.environ["ENV"] = "testing"
        cfg = reload_settings()
        assert cfg.is_test
    """
    global settings
    settings = Settings()
    return settings


def get_environment_mode(env: str) -> str:
    """
    Convert an ENV string into a readable description.
    Used in tests to verify proper environment interpretation.
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
