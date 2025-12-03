# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/16/2025
# Assignment-11: Application Core Module
# File: app/core/__init__.py
# ----------------------------------------------------------
# Description:
# Initializes the core module for application-wide settings.
#
# Responsibilities:
#   • Exposes the global `settings` object created in config.py
#   • Provides a clean import path for any module needing
#     environment variables, security constants, JWT settings,
#     database URLs, etc.
#
# This improves consistency across FastAPI routes, database
# layers, authentication utilities, and test configurations.
# ----------------------------------------------------------

from .config import settings

__all__ = ["settings"]
