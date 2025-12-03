# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/16/2025
# Assignment-11: Calculation Factory (Polymorphic Operations)
# File: app/factory/calculation_factory.py
# ----------------------------------------------------------
# Description:
# Core factory for creating polymorphic arithmetic operations.
#
# Key Requirements (verified by unit + integration tests):
#   • Return INSTANCE of operation class (not the class itself)
#   • Accept synonyms ("add", "addition", "plus", "sub", "minus", etc.)
#   • Normalize input using strip() + lower()
#   • Raise ValueError("Unsupported calculation type")
#   • Division must raise ValueError("Division by zero")
#
# This module provides pure, stateless operations with predictable
# behavior so backend API routes and test suites function reliably.
# ----------------------------------------------------------

from typing import Callable, Type


# ----------------------------------------------------------
# Concrete operation strategy classes
# ----------------------------------------------------------
class AddOperation:
    """Perform addition: a + b"""

    @staticmethod
    def compute(a: float, b: float) -> float:
        return a + b


class SubtractOperation:
    """Perform subtraction: a - b"""

    @staticmethod
    def compute(a: float, b: float) -> float:
        return a - b


class MultiplyOperation:
    """Perform multiplication: a * b"""

    @staticmethod
    def compute(a: float, b: float) -> float:
        return a * b


class DivideOperation:
    """Perform safe division: a / b"""

    @staticmethod
    def compute(a: float, b: float) -> float:
        # Tests require EXACT wording: "Division by zero"
        if b == 0:
            raise ValueError("Division by zero")
        return a / b


# ----------------------------------------------------------
# Factory Class
# ----------------------------------------------------------
class CalculationFactory:
    """
    Factory responsible for mapping operation names
    (including synonyms) to the correct computation class.

    Returns:
        An **instance** of the operation class (required by unit tests)
    """

    # Synonym map (all keys must be lowercase)
    OPERATIONS: dict[str, Type] = {
        # Addition
        "add": AddOperation,
        "addition": AddOperation,
        "plus": AddOperation,

        # Subtraction
        "subtract": SubtractOperation,
        "sub": SubtractOperation,
        "minus": SubtractOperation,
        "subtraction": SubtractOperation,

        # Multiplication
        "multiply": MultiplyOperation,
        "mul": MultiplyOperation,
        "times": MultiplyOperation,
        "multiplication": MultiplyOperation,

        # Division
        "divide": DivideOperation,
        "div": DivideOperation,
        "division": DivideOperation,
    }

    @classmethod
    def create(cls, op_type: str):
        """
        Normalize incoming string and return an operation instance.

        Args:
            op_type (str): operation name like "add", "mul", "minus"

        Raises:
            ValueError: if operation is not supported

        Returns:
            Instance of operation class
        """
        key = op_type.strip().lower()

        if key not in cls.OPERATIONS:
            raise ValueError("Unsupported calculation type")

        # Tests require instance, not class
        return cls.OPERATIONS[key]()
