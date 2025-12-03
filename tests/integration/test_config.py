# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/17/2025
# Assignment-11: Configuration Module Integration Tests
# File: tests/integration/test_config.py
# ----------------------------------------------------------
# Description:
# Integration test suite for the application configuration module.
#
# Covers:
#   • Environment flag logic (is_dev, is_prod, is_test)
#   • reload_settings() ensuring updated environment values reload correctly
#   • get_environment_mode() readable labels for different ENV values
# ----------------------------------------------------------

import os
import pytest
from app.core.config import Settings, reload_settings, get_environment_mode


# ----------------------------------------------------------
# Environment Flag Tests
# ----------------------------------------------------------
def test_environment_flags(monkeypatch):
    """Verify is_dev / is_prod / is_test properties under each ENV mode."""

    # Development
    monkeypatch.setenv("ENV", "development")
    s = Settings()
    assert s.is_dev is True
    assert s.is_prod is False
    assert s.is_test is False

    # Production
    monkeypatch.setenv("ENV", "production")
    s = Settings()
    assert s.is_prod is True
    assert s.is_dev is False
    assert s.is_test is False

    # Testing
    monkeypatch.setenv("ENV", "testing")
    s = Settings()
    assert s.is_test is True
    assert s.is_dev is False
    assert s.is_prod is False


# ----------------------------------------------------------
# reload_settings() Tests
# ----------------------------------------------------------
def test_reload_updates_values(monkeypatch):
    """Ensure reload_settings() rebuilds the global settings instance."""

    monkeypatch.setenv("DATABASE_URL", "sqlite:///./changed.db")
    monkeypatch.setenv("SECRET_KEY", "newkey123")
    monkeypatch.setenv("ENV", "testing")

    updated = reload_settings()

    assert updated.DATABASE_URL == "sqlite:///./changed.db"
    assert updated.SECRET_KEY == "newkey123"
    assert updated.is_test is True


# ----------------------------------------------------------
# get_environment_mode() Tests
# ----------------------------------------------------------
@pytest.mark.parametrize(
    "env_value, expected",
    [
        ("development", "development mode"),
        ("production", "production mode"),
        ("testing", "testing mode"),
        ("something_else", "Unknown environment"),
    ],
)
def test_print_environment_modes(env_value, expected):
    """Validate conversion of ENV string into readable text."""
    assert expected.lower() in get_environment_mode(env_value).lower()
