# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/16/2025
# Assignment-11: Secure User Model + Calculation Model
# File: app/__init__.py
# ----------------------------------------------------------
# Description:
# Marks the "app" directory as a Python package.
#
# Provides:
#   • BASE_DIR constant for path resolution
#   • Centralized reference point used by submodules
#
# This file ensures consistent import behavior across the
# entire project and supports Docker, pytest, and CI/CD.
# ----------------------------------------------------------

from pathlib import Path

# Root directory of the application package
BASE_DIR = Path(__file__).resolve().parent

__all__ = ["BASE_DIR"]
