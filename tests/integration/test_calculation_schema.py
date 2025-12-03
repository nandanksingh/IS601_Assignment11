# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/17/2025
# Assignment-11: Calculation Schema Tests
# File: tests/integration/test_calculation_schema.py
# ----------------------------------------------------------
# Description:
# Tests Pydantic schemas:
#   • CalculationCreate
#   • CalculationRead
#   • Validation rules (type, numeric, zero-division)
#   • compute_result() correctness
# ----------------------------------------------------------

import pytest
from pydantic import ValidationError

from app.schemas.cal_schemas import CalculationCreate, CalculationRead


# ----------------------------------------------------------
# Valid schema creation + compute_result()
# ----------------------------------------------------------
@pytest.mark.parametrize(
    "type_, a, b, expected",
    [
        ("add", 3, 5, 8.0),
        ("subtract", 10, 4, 6.0),
        ("multiply", 2, 6, 12.0),
        ("divide", 8, 2, 4.0),
    ],
)
def test_calculation_create_valid(type_, a, b, expected):
    """Ensure CalculationCreate produces correct computed results."""
    schema = CalculationCreate(type=type_, a=a, b=b)
    assert schema.type == type_
    assert schema.compute_result() == expected


# ----------------------------------------------------------
# Invalid type string
# ----------------------------------------------------------
def test_invalid_calculation_type():
    """Unsupported calculation type must fail validation."""
    with pytest.raises(ValidationError):
        CalculationCreate(type="power", a=2, b=3)


# ----------------------------------------------------------
# Non-numeric inputs
# ----------------------------------------------------------
@pytest.mark.parametrize("a, b", [
    ("abc", 5),
    (None, 3),
    ([1, 2], 3),
])
def test_invalid_numeric_values(a, b):
    """Non-numeric values must raise ValidationError."""
    with pytest.raises(ValidationError):
        CalculationCreate(type="add", a=a, b=b)


# ----------------------------------------------------------
# Zero division validation
# ----------------------------------------------------------
def test_zero_division_validation():
    """Division by zero must raise ValidationError."""
    with pytest.raises(ValidationError):
        CalculationCreate(type="divide", a=10, b=0)


# ----------------------------------------------------------
# CalculationRead must include stored result
# ----------------------------------------------------------
def test_calculation_read_schema():
    """Ensure CalculationRead schema returns stored result correctly."""
    read = CalculationRead(
        id=1,
        type="add",
        a=2,
        b=3,
        result=5.0,
        user_id=10
    )

    assert read.id == 1
    assert read.type == "add"
    assert read.result == 5.0
    assert read.user_id == 10
