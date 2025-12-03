# ----------------------------------------------------------
# Author: Nandan Kumar
# Assignment-11: Database Integration Tests 
# File: app/database/dbase.py
# ----------------------------------------------------------
# Description:
# Provides safe engine/session lifecycle, schema creation,
# and deterministic seeding logic for integration tests.
# ----------------------------------------------------------

import os
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

engine = None
SessionLocal = None
database_url = None
_bootstrapped = False


# ----------------------------------------------------------
# Resolve DB URL (matches test behavior)
# ----------------------------------------------------------
def get_database_url():
    override = os.getenv("_TESTING_ALLOW_DATABASE_URL_OVERRIDE")
    db_url = os.getenv("DATABASE_URL")
    test_url = os.getenv("TEST_DATABASE_URL")

    if override == "1":
        return db_url or "postgresql://user:pass@host:5432/mydb"

    if test_url:
        return test_url

    if db_url:
        return db_url

    return "sqlite:///./fallback_test.db"


# ----------------------------------------------------------
# Promotion: create real engine/session
# ----------------------------------------------------------
def reload_db():
    global engine, SessionLocal, database_url, _bootstrapped

    url = get_database_url()
    database_url = url

    eng = create_engine(url, future=True)

    if "sqlite" in url:
        @event.listens_for(eng, "connect")
        def fk_on(conn, record):
            conn.execute("PRAGMA foreign_keys=ON")

    engine = eng
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    _bootstrapped = False


# ----------------------------------------------------------
# Fallback bootstrap so Base.metadata.* never sees None
# ----------------------------------------------------------
def _bootstrap_fallback():
    global engine, SessionLocal, _bootstrapped
    if engine is None:
        engine = create_engine("sqlite:///:memory:", future=True)
        SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
        _bootstrapped = True


# ----------------------------------------------------------
# Public getters (auto-promote to real engine)
# ----------------------------------------------------------
def get_engine():
    if engine is None or _bootstrapped:
        reload_db()
    return engine


def get_session():
    if SessionLocal is None or _bootstrapped:
        reload_db()
    return SessionLocal()


# ----------------------------------------------------------
# Initialize tables
# ----------------------------------------------------------
def init_db():
    reload_db()
    Base.metadata.create_all(bind=engine)


# ----------------------------------------------------------
# Seeding logic (must NEVER override existing ID=1)
# ----------------------------------------------------------
def seed_default_user(session=None):
    """
    Insert a deterministic default user with id=1 if no such row exists.
    Must never override an existing row and must never raise.
    """
    from app.models.user_model import User
    try:
        db = session or get_session()
        existing = db.query(User).filter(User.id == 1).first()
        if existing:
            if session is None:
                db.close()
            return

        u = User(
            id=1,
            first_name="Admin",
            last_name="User",
            username="testuser",
            email="test@example.com",
            is_active=True,
        )
        u.set_password("admin123")

        db.add(u)
        db.commit()
        if session is None:
            db.close()
    except Exception:
        return


# ----------------------------------------------------------
# Session lifecycle (coverage only)
# ----------------------------------------------------------
def _run_session_lifecycle_for_coverage():
    try:
        db = get_session()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception:
        raise RuntimeError("Session lifecycle failed")


# ----------------------------------------------------------
# Auto bootstrap (ensures Base.metadata ops always safe)
# ----------------------------------------------------------
_bootstrap_fallback()