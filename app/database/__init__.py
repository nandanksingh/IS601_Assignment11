# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/19/2025
# Assignment-11: Database Package Initialization
# File: app/database/__init__.py
# ----------------------------------------------------------
# Description:
# Exposes the main database components for easy importing
# throughout the application:
#
#   • Base         — Declarative SQLAlchemy base class
#   • get_engine   — Database engine factory
#   • get_session  — SQLAlchemy session provider
# ----------------------------------------------------------

from .dbase import Base, get_engine, get_session

__all__ = ["Base", "get_engine", "get_session"]
