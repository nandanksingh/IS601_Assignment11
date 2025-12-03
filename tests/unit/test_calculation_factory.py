# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/16/2025
# Assignment-11: Factory Unit Tests
# File: tests/unit/test_calculation_factory.py
# ----------------------------------------------------------

import pytest
from app.factory.calculation_factory import CalculationFactory
from app.models.cal_models import Calculation


@pytest.mark.parametrize(
    "op,a,b,expected",
    [
        ("add", 3, 5, 8.0),
        ("subtract", 10, 4, 6.0),
        ("multiply", 2, 6, 12.0),
        ("divide", 8, 2, 4.0),
    ],
)
def test_factory_creates_valid_calc(op, a, b, expected):
    calc = CalculationFactory.create(op, a, b)
    assert isinstance(calc, Calculation)
    assert calc.type == op
    assert calc.a == a
    assert calc.b == b
    assert calc.result == expected


def test_factory_mixed_case():
    calc = CalculationFactory.create("ADD", 2, 3)
    assert calc.type == "add"
    assert calc.result == 5.0


def test_factory_invalid_type():
    with pytest.raises(ValueError):
        CalculationFactory.create("power", 2, 3)


@pytest.mark.parametrize("a,b", [
    ("abc", 5),
    (None, 3),
    ([1, 2], 3),
])
def test_factory_invalid_numeric(a, b):
    with pytest.raises(ValueError):
        CalculationFactory.create("add", a, b)


def test_factory_division_by_zero():
    with pytest.raises(ValueError):
        CalculationFactory.create("divide", 10, 0)
