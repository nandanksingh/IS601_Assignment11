# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/17/2025
# Assignment-11: Implement and Test a Calculation Model
# FastAPI Calculator Logic (Reusable Arithmetic Operations)
# File: app/operations/__init__.py
# ----------------------------------------------------------
# Description:
# Stateless arithmetic operations used throughout the application.
# These functions:
#   • Validate numeric input
#   • Perform Add, Subtract, Multiply, Divide
#   • Provide structured logging for debugging
#
# Used by:
#   • FastAPI endpoints 
#   • CalculationFactory 
#   • Calculation SQLAlchemy model 
# ----------------------------------------------------------

import logging
from typing import Union

# ----------------------------------------------------------
# Type Alias and Logger Configuration
# ----------------------------------------------------------
Number = Union[int, float]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# ----------------------------------------------------------
# Helper: Validate Numeric Input
# ----------------------------------------------------------
def validate_number(value: Number) -> Number:
    """
    Ensure that the provided value is numeric.
    Raises:
        ValueError: If input is not int or float.
    """
    if not isinstance(value, (int, float)):
        logger.error(f"Invalid input type: {type(value)} - must be numeric.")
        raise ValueError("Input must be numeric (int or float).")
    return value


# ----------------------------------------------------------
# Arithmetic Operations
# ----------------------------------------------------------
def add(a: Number, b: Number) -> float:
    """Perform addition."""
    a, b = validate_number(a), validate_number(b)
    result = a + b
    logger.info(f"Add operation: {a} + {b} = {result}")
    return float(result)


def subtract(a: Number, b: Number) -> float:
    """Perform subtraction."""
    a, b = validate_number(a), validate_number(b)
    result = a - b
    logger.info(f"Subtract operation: {a} - {b} = {result}")
    return float(result)


def multiply(a: Number, b: Number) -> float:
    """Perform multiplication."""
    a, b = validate_number(a), validate_number(b)
    result = a * b
    logger.info(f"Multiply operation: {a} * {b} = {result}")
    return float(result)


def divide(a: Number, b: Number) -> float:
    """
    Perform division with zero protection.
    Raises:
        ValueError: When attempting to divide by zero.
    """
    a, b = validate_number(a), validate_number(b)
    if b == 0:
        logger.warning(f"Division by zero attempt: a={a}, b={b}")
        raise ValueError("Division by zero is not allowed.")
    result = a / b
    logger.info(f"Divide operation: {a} / {b} = {result}")
    return float(result)


# ----------------------------------------------------------
# Public Exports
# ----------------------------------------------------------
__all__ = ["add", "subtract", "multiply", "divide"]
