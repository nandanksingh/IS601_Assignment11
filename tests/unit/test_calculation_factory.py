# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/17/2025
# Assignment-11: Calculation Model + Factory Pattern
# File: tests/unit/test_calculation_factory.py
# ----------------------------------------------------------
# Description:
# Unit tests for the CalculationFactory and operation strategy
# classes (Add, Subtract, Multiply, Divide). Ensures correct
# factory behavior, strategy computation, invalid type handling,
# and error propagation. Provides full coverage of the factory
# pattern implementation in app/factory/calculation_factory.py.
# ----------------------------------------------------------

import pytest

from app.factory.calculation_factory import (
    CalculationFactory,
    AddOperation,
    SubtractOperation,
    MultiplyOperation,
    DivideOperation,
)

# ----------------------------------------------------------
# Factory: Valid Operation Types
# ----------------------------------------------------------
@pytest.mark.parametrize(
    "calc_type, expected_class",
    [
        ("add", AddOperation),
        ("subtract", SubtractOperation),
        ("sub", SubtractOperation),
        ("minus", SubtractOperation),
        ("multiply", MultiplyOperation),
        ("mul", MultiplyOperation),
        ("divide", DivideOperation),
        ("div", DivideOperation),
    ],
)
def test_factory_returns_correct_operation(calc_type, expected_class):
    """Factory must return correct strategy instance per operation name."""
    op = CalculationFactory.create(calc_type)
    assert isinstance(op, expected_class)

# ----------------------------------------------------------
# Factory: Invalid Operation Types
# ----------------------------------------------------------
@pytest.mark.parametrize("invalid_type", ["", "   ", "xyz", "unknown", "power"])
def test_factory_invalid_type_raises(invalid_type):
    """Unsupported operation types must raise ValueError."""
    with pytest.raises(ValueError, match="Unsupported calculation type"):
        CalculationFactory.create(invalid_type)

# ----------------------------------------------------------
# Strategy: AddOperation
# ----------------------------------------------------------
def test_add_operation_compute():
    op = AddOperation()
    assert op.compute(5, 7) == 12

# ----------------------------------------------------------
# Strategy: SubtractOperation
# ----------------------------------------------------------
def test_subtract_operation_compute():
    op = SubtractOperation()
    assert op.compute(10, 4) == 6

# ----------------------------------------------------------
# Strategy: MultiplyOperation
# ----------------------------------------------------------
def test_multiply_operation_compute():
    op = MultiplyOperation()
    assert op.compute(3, 5) == 15

# ----------------------------------------------------------
# Strategy: DivideOperation (normal case)
# ----------------------------------------------------------
def test_divide_operation_compute():
    op = DivideOperation()
    assert op.compute(20, 5) == 4

# ----------------------------------------------------------
# Strategy: DivideOperation (division by zero)
# ----------------------------------------------------------
def test_divide_operation_zero_error():
    op = DivideOperation()
    with pytest.raises(ValueError, match="Division by zero"):
        op.compute(10, 0)
