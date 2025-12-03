# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/17/2025
# Assignment-11: Secure User Model (SQLAlchemy Integration Tests)
# File: tests/integration/test_user_model.py
# ----------------------------------------------------------
# Description:
# Full SQLAlchemy integration test suite for the User model.
#
# Covers:
#   • Table creation, inserts, queries, and updates
#   • Commit + rollback behavior
#   • Unique constraint enforcement
#   • Password hashing + verification
#   • __repr__ coverage (normal + fallback)
#   • ORM → Pydantic schema conversion
# ----------------------------------------------------------

import pytest
import logging
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.models.user_model import User
from app.database.dbase import Base, engine, SessionLocal
from app.auth.security import hash_password

logger = logging.getLogger(__name__)


# ----------------------------------------------------------
# Database Setup Fixtures
# ----------------------------------------------------------
@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Clean reset of all tables before and after every test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Provide a clean SQLAlchemy session for each test."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def make_user():
    """Factory to create users with valid hashed password."""
    def _make(username: str, email: str):
        return User(
            username=username,
            email=email,
            password_hash=hash_password("SecurePass123"),
        )
    return _make


# ----------------------------------------------------------
# Basic Connectivity
# ----------------------------------------------------------
def test_database_connection(db_session):
    """Ensure database connection and SQL execution works."""
    result = db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


# ----------------------------------------------------------
# Insert / Commit / Rollback Tests
# ----------------------------------------------------------
def test_user_commit_and_rollback(db_session, make_user):
    """Verify commit success and correct rollback after IntegrityError."""
    u1 = make_user("alpha", "alpha@example.com")
    db_session.add(u1)
    db_session.commit()

    # Insert duplicate email → trigger rollback
    u2 = make_user("beta", "alpha@example.com")
    db_session.add(u2)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()
    assert db_session.query(User).count() == 1


# ----------------------------------------------------------
# Querying Users
# ----------------------------------------------------------
def test_user_query_methods(db_session, make_user):
    """Ensure filtering, ordering, and retrieval work correctly."""
    db_session.add_all([
        make_user("user1", "u1@example.com"),
        make_user("user2", "u2@example.com"),
        make_user("user3", "u3@example.com"),
    ])
    db_session.commit()

    found = db_session.query(User).filter_by(username="user2").first()
    assert found.email == "u2@example.com"

    ordered = db_session.query(User).order_by(User.email).all()
    assert [u.email for u in ordered] == sorted([u.email for u in ordered])


# ----------------------------------------------------------
# Update + Refresh
# ----------------------------------------------------------
def test_user_update_and_refresh(db_session, make_user):
    """Update user fields and verify refresh syncs DB state."""
    user = make_user("nandan", "nandan@example.com")
    db_session.add(user)
    db_session.commit()

    user.email = "updated@example.com"
    db_session.commit()
    db_session.refresh(user)

    assert user.email == "updated@example.com"


# ----------------------------------------------------------
# Bulk Insert
# ----------------------------------------------------------
@pytest.mark.slow
def test_bulk_user_insert(db_session, make_user):
    """Insert multiple users using bulk save."""
    users = [make_user(f"bulk{i}", f"bulk{i}@example.com") for i in range(5)]
    db_session.bulk_save_objects(users)
    db_session.commit()

    assert db_session.query(User).count() >= 5


# ----------------------------------------------------------
# Unique Constraints
# ----------------------------------------------------------
def test_unique_constraints(db_session, make_user):
    """Duplicate username + duplicate email must raise IntegrityError."""
    u1 = make_user("dupuser", "dup@example.com")
    db_session.add(u1)
    db_session.commit()

    # Duplicate username
    u2 = make_user("dupuser", "other@example.com")
    db_session.add(u2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # Duplicate email
    u3 = make_user("otheruser", "dup@example.com")
    db_session.add(u3)
    with pytest.raises(IntegrityError):
        db_session.commit()


# ----------------------------------------------------------
# Transaction Rollback Behavior
# ----------------------------------------------------------
def test_transaction_rollback(db_session, make_user):
    """Failure mid-transaction should leave DB unchanged."""
    user = make_user("rollback", "rollback@example.com")
    db_session.add(user)

    with pytest.raises(SQLAlchemyError):
        db_session.execute(text("SELECT * FROM __table_does_not_exist__"))
        db_session.commit()

    db_session.rollback()
    assert db_session.query(User).filter_by(username="rollback").first() is None


# ----------------------------------------------------------
# Password Hashing + __repr__
# ----------------------------------------------------------
def test_user_password_methods(db_session):
    """Validate password hashing, checking, and readable __repr__."""
    user = User(username="demo", email="demo@example.com")
    user.set_password("MySecurePass123")
    db_session.add(user)
    db_session.commit()

    assert user.password_hash != "MySecurePass123"
    assert user.verify_password("MySecurePass123") is True
    assert user.verify_password("WrongPass") is False

    rep = repr(user)
    assert "demo" in rep
    assert "demo@example.com" in rep


# ----------------------------------------------------------
# Schema Conversion
# ----------------------------------------------------------
def test_user_to_read_schema(db_session, make_user):
    """Convert ORM → Pydantic schema and validate fields."""
    user = make_user("convert", "convert@example.com")
    db_session.add(user)
    db_session.commit()

    schema = user.to_read_schema()
    assert schema.username == "convert"
    assert schema.email == "convert@example.com"


# ----------------------------------------------------------
# __repr__ Fallback Coverage
# ----------------------------------------------------------
def test_user_repr_never_crashes(db_session, make_user):
    """
    Delete username after commit → triggers fallback inside __repr__.
    Ensures __repr__ NEVER raises exceptions.
    """
    user = make_user("reprcheck", "reprcheck@example.com")
    db_session.add(user)
    db_session.commit()

    # Force AttributeError inside __repr__
    del user.username

    output = repr(user)
    assert "User" in output or "object" in output
