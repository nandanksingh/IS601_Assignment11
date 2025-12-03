# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/15/2025
# Assignment-11: Test Configuration 
# File: tests/conftest.py
# ----------------------------------------------------------
# Description:
# Central pytest configuration for Module 11.
# Ensures every test runs on a clean, isolated database.
# Provides safe SQLAlchemy session fixtures.
# Prevents unique-constraint conflicts and seed collisions.
# Used by all unit + integration tests.
# ----------------------------------------------------------

import os
import pytest
from sqlalchemy.orm import sessionmaker

# Force test mode BEFORE importing DB engine
os.environ["ENV"] = "testing"

from app.database.dbase import (
    Base,
    get_engine,
    reload_db,
)

# ----------------------------------------------------------
# 1: Reset database before EACH test
# ----------------------------------------------------------
@pytest.fixture(autouse=True)
def reset_database():
    """
    Ensures every test executes on a clean, fresh database.
    Drops and recreates all tables before each test to avoid:
      • UNIQUE constraint conflicts
      • Seed user collisions
      • Cross-test FK contamination
    """
    reload_db()
    engine = get_engine()

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)

# ----------------------------------------------------------
# 2: Provide safe SQLAlchemy session per test
# ----------------------------------------------------------
@pytest.fixture
def db_session():
    """
    Returns a clean SQLAlchemy session.
    Rolls back and closes automatically after each test.
    """
    engine = get_engine()
    TestSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = TestSession()

    try:
        yield session
    finally:
        session.rollback()
        session.close()

# Alias “db” used across test suite
@pytest.fixture
def db(db_session):
    return db_session

# ----------------------------------------------------------
# 3: Auto-created test user for calculation tests
# ----------------------------------------------------------
@pytest.fixture
def test_user(db_session):
    """
    Creates a unique test user for operations requiring a user_id.
    Avoids id=1 to prevent default-seed collisions.
    """
    from app.models.user_model import User

    user = User(
        first_name="Temp",
        last_name="User",
        username="tempuser_fixture",
        email="temp_fixture@example.com",
        is_active=True,
    )
    user.set_password("pass123")

    db_session.add(user)
    db_session.commit()

    return user
