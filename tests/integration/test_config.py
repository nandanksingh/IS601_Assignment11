# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/17/2025
# Module 11: Configuration Module Integration Tests
# File: tests/unit/test_config.py
# ----------------------------------------------------------
# Description:
# Tests for the application configuration system.
#
# Covers:
#   • Environment flag logic (is_dev, is_prod, is_test)
#   • reload_settings() ensuring updated ENV variables reload correctly
#   • get_environment_mode() readable labels for different ENV values
#
# Ensures config.py behaves correctly in all test environments.
# ----------------------------------------------------------

import pytest
import os
from app.core.config import Settings, reload_settings, get_environment_mode


# ----------------------------------------------------------
# Environment Flag Tests
# ----------------------------------------------------------
def test_environment_flags(monkeypatch):
    """Verify is_dev / is_prod / is_test react correctly to ENV."""

    # Development mode
    monkeypatch.setenv("ENV", "development")
    s = Settings()
    assert s.is_dev is True
    assert s.is_prod is False
    assert s.is_test is False

    # Production mode
    monkeypatch.setenv("ENV", "production")
    s = Settings()
    assert s.is_prod is True
    assert s.is_dev is False
    assert s.is_test is False

    # Testing mode
    monkeypatch.setenv("ENV", "testing")
    s = Settings()
    assert s.is_test is True
    assert s.is_dev is False
    assert s.is_prod is False


# ----------------------------------------------------------
# reload_settings() Tests
# ----------------------------------------------------------
def test_reload_settings(monkeypatch):
    """Ensure global Settings object reloads after environment changes."""

    monkeypatch.setenv("DATABASE_URL", "sqlite:///./changed.db")
    monkeypatch.setenv("SECRET_KEY", "mynewsecret")
    monkeypatch.setenv("ENV", "testing")

    new_settings = reload_settings()

    assert new_settings.DATABASE_URL == "sqlite:///./changed.db"
    assert new_settings.SECRET_KEY == "mynewsecret"
    assert new_settings.is_test is True


# ----------------------------------------------------------
# get_environment_mode() Tests
# ----------------------------------------------------------
@pytest.mark.parametrize(
    "env_value, expected",
    [
        ("development", "development mode"),
        ("production", "production mode"),
        ("testing", "testing mode"),
        ("staging", "Unknown environment"),
    ],
)
def test_environment_mode_output(env_value, expected):
    """Validate mapping of ENV → human-readable label."""
    result = get_environment_mode(env_value)
    assert expected.lower() in result.lower()
