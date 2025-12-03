# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/17/2025
# Assignment-11: Global Pytest Fixtures (DB + Users)
# File: tests/conftest.py
# ----------------------------------------------------------
# Description:
# Centralized pytest fixtures shared across all unit and
# integration tests. Provides:
#   • SQLite test database (isolated)
#   • SQLAlchemy session fixture
#   • Faker-generated users
# ----------------------------------------------------------

import os
import pytest
from faker import Faker

# ----------------------------------------------------------
# Force SQLite for ALL tests before importing app modules
# ----------------------------------------------------------
os.environ["ENV"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

# Import AFTER environment override
from app.database.dbase import Base, engine, SessionLocal
from app.models.user_model import User
from app.auth.security import hash_password


fake = Faker()
Faker.seed(12345)


# ----------------------------------------------------------
# GLOBAL TEST DATABASE SETUP (Runs Once)
# ----------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create test schema once per session; drop at end."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ----------------------------------------------------------
# CLEAN DB BEFORE EACH TEST
# ----------------------------------------------------------
@pytest.fixture(autouse=True)
def reset_db():
    """Ensures every test starts with a fresh DB."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ----------------------------------------------------------
# SQLAlchemy Session Fixture
# ----------------------------------------------------------
@pytest.fixture
def db_session():
    """
    Provides a fresh DB session for each test.
    Handles commit/rollback automatically.
    """
    session = SessionLocal()
    try:
        yield session
        if session.is_active:
            try:
                session.commit()
            except Exception:
                session.rollback()
    finally:
        session.close()


# ----------------------------------------------------------
# USER FIXTURES
# ----------------------------------------------------------
@pytest.fixture
def fake_user_data():
    """Return a valid random user payload."""
    return {
        "username": fake.unique.user_name(),
        "email": fake.unique.email(),
        "password_hash": hash_password("TestPass123"),
    }


@pytest.fixture
def test_user(db_session, fake_user_data):
    """Insert and return a single persisted User."""
    user = User(**fake_user_data)
    db_session.add(user)
    db_session.flush()
    db_session.refresh(user)
    return user


@pytest.fixture
def seed_users(db_session):
    """Insert and return multiple users."""
    users = []
    for _ in range(5):
        data = {
            "username": fake.unique.user_name(),
            "email": fake.unique.email(),
            "password_hash": hash_password("TempPass123"),
        }
        user = User(**data)
        db_session.add(user)
        users.append(user)
    return users
