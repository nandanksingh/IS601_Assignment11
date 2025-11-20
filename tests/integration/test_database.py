# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/17/2025
# Assignment-10: Database Integration Tests
# File: tests/integration/test_database.py
# ----------------------------------------------------------
# Description:
# Covers:
#   • Engine initialization (success + error paths)
#   • DATABASE_URL resolution
#   • Session lifecycle behavior
#   • init_db() and drop_db() success/failure
#   • PostgreSQL fallback helpers
# ----------------------------------------------------------

import os
import sys
import pytest
import importlib
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

DATABASE_MODULE = "app.database.dbase"


# Helper: Reload module for fresh environment
def reload_database_module():
    if DATABASE_MODULE in sys.modules:
        del sys.modules[DATABASE_MODULE]
    return importlib.import_module(DATABASE_MODULE)


# ----------------------------------------------------------
# Engine and URL Coverage
# ----------------------------------------------------------
def test_get_engine_success(monkeypatch):
    """Ensure a valid SQLAlchemy engine is created."""
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test.db")
    db = reload_database_module()
    engine = db.get_engine()
    assert isinstance(engine, Engine)


def test_get_engine_failure_with_sqlite(monkeypatch):
    """Force create_engine() failure to cover error-handling path."""
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test.db")
    with patch("app.database.dbase.create_engine",
               side_effect=SQLAlchemyError("Simulated failure")):
        import app.database.dbase as dbase
        with pytest.raises(SQLAlchemyError):
            dbase.get_engine()


def test_get_engine_coverage_fallback(monkeypatch):
    """Validate SQLite branch with connect_args."""
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test.db")
    db = reload_database_module()
    engine = db.get_engine()
    assert "sqlite" in str(engine.url)


def test_get_database_url_variants(monkeypatch):
    """DATABASE_URL should return postgres or sqlite strings."""
    monkeypatch.setenv("DATABASE_URL",
                       "postgresql://user:pass@db:5432/test_db")
    import app.database.dbase as dbase
    result = dbase.get_database_url()
    assert "postgresql" in result or "sqlite" in result


# ----------------------------------------------------------
# Session Lifecycle
# ----------------------------------------------------------
def test_session_factory(monkeypatch):
    """Ensure SessionLocal creates usable SQLAlchemy sessions."""
    db = reload_database_module()
    session = db.SessionLocal()
    assert isinstance(session, Session)
    session.close()


def test_base_declaration(monkeypatch):
    """Base metadata must exist."""
    db = reload_database_module()
    assert db.Base is not None


def test_init_drop_db(monkeypatch):
    """init_db() and drop_db() must call metadata methods."""
    db = reload_database_module()
    with patch.object(db.Base.metadata, "create_all") as mock_create, \
            patch.object(db.Base.metadata, "drop_all") as mock_drop:
        db.init_db()
        db.drop_db()
        assert mock_create.called
        assert mock_drop.called


def test_run_session_lifecycle_success(monkeypatch):
    """Force commit path."""
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "dummy")
    import app.database.dbase as dbase
    dbase._run_session_lifecycle_for_coverage()


def test_run_session_lifecycle_failure(monkeypatch):
    """Force failure path."""
    import app.database.dbase as dbase
    with patch("app.database.dbase.get_session",
               side_effect=Exception("session fail")):
        with pytest.raises(RuntimeError):
            dbase._run_session_lifecycle_for_coverage()


# ----------------------------------------------------------
# Fallback Helpers
# ----------------------------------------------------------
import app.database.dbase as db_init


def test_postgres_unavailable_true():
    with patch("socket.create_connection", side_effect=OSError()):
        assert db_init._postgres_unavailable() is True


def test_postgres_unavailable_false():
    mock_conn = MagicMock()
    with patch("socket.create_connection", return_value=mock_conn):
        assert db_init._postgres_unavailable() is False


def test_ensure_sqlite_fallback(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgres://x")
    with patch("app.database.dbase._postgres_unavailable", return_value=True):
        db_init._ensure_sqlite_fallback()
        assert "sqlite" in os.getenv("DATABASE_URL")


def test_trigger_fallback_executes(monkeypatch):
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "dummy")
    monkeypatch.setenv("DATABASE_URL", "postgres://x")
    with patch("app.database.dbase._postgres_unavailable", return_value=True):
        db_init._trigger_fallback_if_test_env()
        assert "sqlite" in os.getenv("DATABASE_URL")


def test_trigger_fallback_error(monkeypatch):
    """Force fallback helper to fail → router should raise RuntimeError."""
    import app.database.dbase as db

    def boom():
        raise Exception("fail")

    monkeypatch.setattr(db, "_ensure_sqlite_fallback", boom)

    with pytest.raises(RuntimeError):
        db._trigger_fallback_if_test_env()

