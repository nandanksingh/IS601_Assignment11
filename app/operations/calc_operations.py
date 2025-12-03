# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/17/2025
# Assignment-11: Arithmetic Operation Functions + Classes
# File: app/operations/calc_operations.py
# ----------------------------------------------------------
# Description:
# Provides:
#   • Function-based arithmetic operations (add, subtract, multiply, divide)
#   • Class-based operation objects used by CalculationFactory
#   • Strict numeric validation required by unit tests
#
# Requirements from tests:
#   add(), subtract(), multiply(), divide() must exist as pure functions
#   Division by zero must raise ValueError("Division by zero")
#   All operations must validate numeric inputs EXACTLY with:
#         ValueError("Input must be numeric.")
#   Four operation classes:
#         AddOperation, SubtractOperation, MultiplyOperation, DivideOperation
#   each exposing compute() → float
# ----------------------------------------------------------

from typing import Union

# Allow ints or floats
Number = Union[int, float]


# ----------------------------------------------------------
# Shared numeric validator
# ----------------------------------------------------------
def _validate(value: Number) -> float:
    """
    Convert value to float if numeric.
    Required behavior:
        • Accept int or float only
        • On anything else: raise ValueError("Input must be numeric.")
    """
    if not isinstance(value, (int, float)):
        raise ValueError("Input must be numeric.")
    return float(value)


# ----------------------------------------------------------
# FUNCTION-BASED OPERATIONS
# (Unit tests directly import and call these)
# ----------------------------------------------------------
def add(a: Number, b: Number) -> float:
    a, b = _validate(a), _validate(b)
    return a + b


def subtract(a: Number, b: Number) -> float:
    a, b = _validate(a), _validate(b)
    return a - b


def multiply(a: Number, b: Number) -> float:
    a, b = _validate(a), _validate(b)
    return a * b


def divide(a: Number, b: Number) -> float:
    a, b = _validate(a), _validate(b)
    if b == 0:
        raise ValueError("Division by zero")
    return a / b


# ----------------------------------------------------------
# CLASS-BASED OPERATIONS
# (Used ONLY by CalculationFactory)
# Tests require that compute() calls the pure functions above.
# ----------------------------------------------------------
class AddOperation:
    """Object that performs addition via compute()."""

    def __init__(self, a: Number, b: Number):
        self.a = a
        self.b = b

    def compute(self) -> float:
        return add(self.a, self.b)


class SubtractOperation:
    """Object that performs subtraction."""

    def __init__(self, a: Number, b: Number):
        self.a = a
        self.b = b

    def compute(self) -> float:
        return subtract(self.a, self.b)


class MultiplyOperation:
    """Object that performs multiplication."""

    def __init__(self, a: Number, b: Number):
        self.a = a
        self.b = b

    def compute(self) -> float:
        return multiply(self.a, self.b)


class DivideOperation:
    """Object that performs safe division."""

    def __init__(self, a: Number, b: Number):
        self.a = a
        self.b = b

    def compute(self) -> float:
        return divide(self.a, self.b)


# Explicit exports for import *
__all__ = [
    "add",
    "subtract",
    "multiply",
    "divide",
    "AddOperation",
    "SubtractOperation",
    "MultiplyOperation",
    "DivideOperation",
]
