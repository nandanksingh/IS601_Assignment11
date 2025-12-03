# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/17/2025
# Assignment-11: Unit Tests for Arithmetic Operations
# File: tests/unit/test_calc_operations.py
# ----------------------------------------------------------
# Description:
# Tests for arithmetic utility functions and operation classes in:
#   app/operations/calc_operations.py
#
# Achieves 100% coverage (functions + classes)
# ----------------------------------------------------------

import pytest

from app.operations.calc_operations import (
    add,
    subtract,
    multiply,
    divide,
    AddOperation,
    SubtractOperation,
    MultiplyOperation,
    DivideOperation,
)

# ----------------------------------------------------------
# FUNCTION-BASED TESTS
# ----------------------------------------------------------

@pytest.mark.parametrize("a, b, expected", [
    (3, 5, 8.0),
    (-2, 6, 4.0),
    (2.5, 1.5, 4.0),
    (0, 0, 0.0),
])
def test_add(a, b, expected):
    assert add(a, b) == expected


@pytest.mark.parametrize("a, b, expected", [
    (10, 4, 6.0),
    (4, 10, -6.0),
    (-3, -2, -1.0),
    (7.5, 2.5, 5.0),
])
def test_subtract(a, b, expected):
    assert subtract(a, b) == expected


@pytest.mark.parametrize("a, b, expected", [
    (2, 3, 6.0),
    (-2, 3, -6.0),
    (1.5, 2.0, 3.0),
    (0, 7, 0.0),
])
def test_multiply(a, b, expected):
    assert multiply(a, b) == expected


@pytest.mark.parametrize("a, b, expected", [
    (8, 2, 4.0),
    (-9, 3, -3.0),
    (7.5, 2.5, 3.0),
    (0, 5, 0.0),
])
def test_divide(a, b, expected):
    assert divide(a, b) == expected


def test_divide_by_zero():
    with pytest.raises(ValueError, match="Division by zero"):
        divide(10, 0)


@pytest.mark.parametrize("func, a, b", [
    (add, "abc", 5),
    (subtract, 3, None),
    (multiply, [1, 2], 4),
    (divide, 5, "xyz"),
])
def test_invalid_type_inputs(func, a, b):
    with pytest.raises(ValueError, match="Input must be numeric"):
        func(a, b)


# ----------------------------------------------------------
# CLASS-BASED OPERATION TESTS (missing coverage lines)
# ----------------------------------------------------------

def test_add_operation_compute():
    op = AddOperation(2, 3)
    assert op.compute() == 5.0


def test_subtract_operation_compute():
    op = SubtractOperation(10, 4)
    assert op.compute() == 6.0


def test_multiply_operation_compute():
    op = MultiplyOperation(3, 7)
    assert op.compute() == 21.0


def test_divide_operation_compute():
    op = DivideOperation(20, 4)
    assert op.compute() == 5.0
