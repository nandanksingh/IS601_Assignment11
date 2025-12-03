# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/14/2025
# Assignment-11: Calculation Model Integration Tests 
# File: tests/integration/test_cal_model.py
# ----------------------------------------------------------

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.cal_models import Calculation


def test_insert_calculation(db_session, test_user):
    calc = Calculation(type="add", a=10, b=5, user_id=test_user.id)
    calc.compute_and_set_result()

    db_session.add(calc)
    db_session.commit()
    db_session.refresh(calc)

    assert calc.result == 15
    assert calc.user_id == test_user.id


@pytest.mark.parametrize(
    "op,a,b,expected",
    [
        ("add", 1, 2, 3),
        ("subtract", 10, 3, 7),
        ("multiply", 2, 3, 6),
        ("divide", 20, 5, 4),
    ],
)
def test_all_operations(db_session, test_user, op, a, b, expected):
    calc = Calculation(type=op, a=a, b=b, user_id=test_user.id)
    calc.compute_and_set_result()

    db_session.add(calc)
    db_session.commit()
    assert calc.result == expected


def test_invalid_user_id_fails(db_session):
    calc = Calculation(type="add", a=3, b=3, user_id=999999)
    calc.compute_and_set_result()

    db_session.add(calc)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_division_by_zero_not_allowed(db_session, test_user):
    calc = Calculation(type="divide", a=10, b=0, user_id=test_user.id)
    with pytest.raises(ValueError):
        calc.compute_and_set_result()
