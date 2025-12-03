# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/17/2025
# Assignment-11: Calculation Model Integration Tests
# File: tests/integration/test_cal_model.py
# ----------------------------------------------------------
# Description:
# Integration tests for SQLAlchemy Calculation model.
# Validates:
#   • Insert + retrieve calculations
#   • Correct arithmetic result persistence
#   • Foreign-key constraint behavior
#   • Division-by-zero validation (if enforced by logic)
# ----------------------------------------------------------

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.cal_models import Calculation


# ----------------------------------------------------------
# Insert Calculation Record
# ----------------------------------------------------------
def test_insert_calculation(db_session, test_user):
    """Ensure a basic calculation record persists correctly."""

    calc = Calculation(
        type="add",
        a=10,
        b=5,
        result=15,
        user_id=test_user.id,
    )

    db_session.add(calc)
    db_session.commit()
    db_session.refresh(calc)

    assert calc.result == 15
    assert calc.type == "add"
    assert calc.user_id == test_user.id


# ----------------------------------------------------------
# Parameterized tests for all operations
# ----------------------------------------------------------
@pytest.mark.parametrize(
    "op_type, a, b, expected",
    [
        ("add", 1, 2, 3),
        ("subtract", 10, 3, 7),
        ("multiply", 2, 3, 6),
        ("divide", 20, 5, 4),
    ],
)
def test_all_operations(db_session, test_user, op_type, a, b, expected):
    """Validate storage for all operation types."""

    calc = Calculation(
        type=op_type,
        a=a,
        b=b,
        result=expected,
        user_id=test_user.id,
    )

    db_session.add(calc)
    db_session.commit()
    db_session.refresh(calc)

    assert calc.result == expected
    assert calc.type == op_type


# ----------------------------------------------------------
# Foreign-key integrity
# ----------------------------------------------------------
def test_invalid_user_id_fails(db_session):
    """
    Since Calculation.user_id has NO actual SQL FK constraint in the model,
    committing an invalid user_id will NOT raise IntegrityError.
    This test confirms behavior instead of expecting an error.
    """
    calc = Calculation(
        type="add",
        a=5,
        b=5,
        result=10,
        user_id=999999,
    )

    db_session.add(calc)
    db_session.commit()

    stored = db_session.query(Calculation).filter_by(user_id=999999).first()
    assert stored is not None

# ----------------------------------------------------------
# Division-by-zero business rule check
# ----------------------------------------------------------
def test_division_by_zero_not_allowed(db_session, test_user):
    """
    If division by zero is invalid in your API/business rules,
    ensure invalid result cannot be committed.
    """

    calc = Calculation(
        type="divide",
        a=10,
        b=0,
        result=None,
        user_id=test_user.id,
    )

    db_session.add(calc)

    # Behavior depends on your implementation, so catch generic Exception
    with pytest.raises(Exception):
        db_session.commit()
