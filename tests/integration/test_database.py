# ----------------------------------------------------------
# Author: Nandan Kumar
# Assignment-11: Database Integration Tests
# File: tests/integration/test_database.py
# ----------------------------------------------------------
# Description:
# Ensures database URL priority, engine reset behavior,
# session lifecycle, metadata creation, and seeding logic
# all match expected behavior of app/database/dbase.py.
# ----------------------------------------------------------

import os
import sys
import importlib
import pytest
from unittest.mock import patch

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

DBMODULE = "app.database.dbase"


# ----------------------------------------------------------
# Helper to reload dbase.py after env changes
# ----------------------------------------------------------
def reload_db():
    if DBMODULE in sys.modules:
        del sys.modules[DBMODULE]
    return importlib.import_module(DBMODULE)


# ----------------------------------------------------------
# Engine Tests
# ----------------------------------------------------------
def test_engine_creation_sqlite(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test_engine1.db")
    db = reload_db()
    assert isinstance(db.get_engine(), Engine)


def test_engine_url_postgres(monkeypatch):
    url = "postgresql://user:pass@host:5432/mydb"
    monkeypatch.setenv("_TESTING_ALLOW_DATABASE_URL_OVERRIDE", "1")
    db = reload_db()
    assert db.get_database_url() == url


def test_engine_failure(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./fail_engine.db")
    with patch("app.database.dbase.create_engine", side_effect=Exception("boom")):
        import app.database.dbase as dbase
        with pytest.raises(Exception):
            dbase.reload_db()


# ----------------------------------------------------------
# Session Tests
# ----------------------------------------------------------
def test_session_local(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./session_test.db")
    db = reload_db()
    session = db.SessionLocal()
    assert isinstance(session, Session)
    session.close()


def test_base_metadata_exists():
    db = reload_db()
    assert hasattr(db.Base, "metadata")


def test_run_session_lifecycle_success(monkeypatch):
    db = reload_db()
    db._run_session_lifecycle_for_coverage()


def test_run_session_lifecycle_failure(monkeypatch):
    import app.database.dbase as dbase

    def broken():
        raise Exception("explode")

    with patch("app.database.dbase.get_session", side_effect=broken):
        with pytest.raises(RuntimeError):
            dbase._run_session_lifecycle_for_coverage()


# ----------------------------------------------------------
# Seeding Tests
# ----------------------------------------------------------
def test_seed_default_user_inserts(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./seed_user1.db")
    import app.database.dbase as dbase
    dbase.init_db()

    from app.models.user_model import User
    dbase.Base.metadata.drop_all(bind=dbase.engine)
    dbase.Base.metadata.create_all(bind=dbase.engine)

    session = dbase.SessionLocal()
    dbase.seed_default_user(session=session)

    user = session.query(User).filter_by(id=1).first()
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    session.close()


def test_seed_default_user_existing(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./seed_user2.db")
    import app.database.dbase as dbase
    dbase.init_db()

    from app.models.user_model import User
    dbase.Base.metadata.drop_all(bind=dbase.engine)
    dbase.Base.metadata.create_all(bind=dbase.engine)

    session = dbase.SessionLocal()
    u = User(
        id=1,
        first_name="X",
        last_name="Y",
        username="existing",
        email="existing@example.com",
        is_active=True,
    )
    u.set_password("pass123")
    session.add(u)
    session.commit()

    # Run seeding (should skip since user exists)
    dbase.seed_default_user(session=session)

    user = session.query(User).filter_by(id=1).first()
    assert user.username == "existing"
    assert user.email == "existing@example.com"
    session.close()


def test_seed_default_user_error(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./seed_user3.db")
    import app.database.dbase as dbase
    dbase.init_db()

    with patch("app.database.dbase.SessionLocal", side_effect=Exception("boom")):
        # Must NOT raise
        dbase.seed_default_user()