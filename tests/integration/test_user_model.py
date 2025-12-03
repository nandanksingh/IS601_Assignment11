# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/16/2025
# Assignment-11: User Model Tests
# File: tests/integration/test_user_model.py
# ----------------------------------------------------------
# Description:
# Integration tests for SQLAlchemy User model:
#   • DB creation and connection
#   • Insert / commit / rollback behavior
#   • Unique constraints
#   • Password hashing + verification
#   • ORM → Pydantic UserRead conversion
#   • __repr__ fallback behavior
# ----------------------------------------------------------

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.models.user_model import User
from app.auth.security import hash_password
from app.database.dbase import Base, engine, SessionLocal


# ----------------------------------------------------------
# Database Reset
# ----------------------------------------------------------
@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def make_user():
    """Create valid user objects with hashed password."""
    def _create(username, email, first_name=None, last_name=None):
        return User(
            username=username,
            email=email,
            password_hash=hash_password("SecurePass123"),
            first_name=first_name,
            last_name=last_name
        )
    return _create


# ----------------------------------------------------------
# Connection
# ----------------------------------------------------------
def test_database_connection(db_session):
    result = db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


# ----------------------------------------------------------
# Insert / rollback
# ----------------------------------------------------------
def test_user_commit_and_rollback(db_session, make_user):
    u1 = make_user("alpha", "alpha@example.com")
    db_session.add(u1)
    db_session.commit()

    u2 = make_user("beta", "alpha@example.com")
    db_session.add(u2)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()
    assert db_session.query(User).count() == 1


# ----------------------------------------------------------
# Query methods
# ----------------------------------------------------------
def test_user_query_methods(db_session, make_user):
    users = [
        make_user("u1", "u1@example.com"),
        make_user("u2", "u2@example.com"),
        make_user("u3", "u3@example.com"),
    ]
    db_session.add_all(users)
    db_session.commit()

    found = db_session.query(User).filter_by(username="u2").first()
    assert found.email == "u2@example.com"

    ordered = db_session.query(User).order_by(User.email).all()
    assert [u.email for u in ordered] == sorted([u.email for u in ordered])


# ----------------------------------------------------------
# Update + refresh
# ----------------------------------------------------------
def test_user_update_and_refresh(db_session, make_user):
    user = make_user("nandan", "nandan@example.com")
    db_session.add(user)
    db_session.commit()

    user.email = "updated@example.com"
    db_session.commit()
    db_session.refresh(user)

    assert user.email == "updated@example.com"


# ----------------------------------------------------------
# Unique constraints
# ----------------------------------------------------------
def test_unique_constraints(db_session, make_user):
    u1 = make_user("unique", "unique@example.com")
    db_session.add(u1)
    db_session.commit()

    u2 = make_user("unique", "new@example.com")
    db_session.add(u2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    u3 = make_user("other", "unique@example.com")
    db_session.add(u3)
    with pytest.raises(IntegrityError):
        db_session.commit()


# ----------------------------------------------------------
# Transaction rollback
# ----------------------------------------------------------
def test_transaction_rollback(db_session, make_user):
    user = make_user("rollback", "rollback@example.com")
    db_session.add(user)

    with pytest.raises(SQLAlchemyError):
        db_session.execute(text("SELECT * FROM table_does_not_exist"))
        db_session.commit()

    db_session.rollback()
    assert db_session.query(User).filter_by(username="rollback").first() is None


# ----------------------------------------------------------
# Password hashing, verifying, repr
# ----------------------------------------------------------
def test_user_password_methods(db_session):
    user = User(username="demo", email="demo@example.com")
    user.set_password("StrongPass123")

    db_session.add(user)
    db_session.commit()

    assert user.verify_password("StrongPass123") is True
    assert user.verify_password("WrongPass") is False

    rep = repr(user)
    assert "demo" in rep
    assert "demo@example.com" in rep


# ----------------------------------------------------------
# ORM → Pydantic UserRead conversion
# Covers None → "" branch
# ----------------------------------------------------------
def test_user_to_read_schema_handles_none_names(db_session, make_user):
    user = make_user("convert", "convert@example.com", first_name=None, last_name=None)
    db_session.add(user)
    db_session.commit()

    schema = user.to_read_schema()
    assert schema.username == "convert"
    assert schema.email == "convert@example.com"
    assert schema.id == user.id
    # Must convert None → ""
    assert schema.first_name == ""
    assert schema.last_name == ""


# ----------------------------------------------------------
# __repr__ fallback
# ----------------------------------------------------------
def test_user_repr_fallback(db_session, make_user):
    user = make_user("repr", "repr@example.com")
    db_session.add(user)
    db_session.commit()

    # Force exception in __repr__ by deleting attributes
    del user.username
    del user.email

    rep = repr(user)
    assert rep.startswith("<User id=")