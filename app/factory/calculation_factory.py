# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/16/2025
# Assignment-11: Calculation Factory (ORM version)
# File: app/factory/calculation_factory.py
# ----------------------------------------------------------
# Description:
# Factory that returns a FULL ORM Calculation object
# with the result pre-computed.
#
# Fully compatible with:
#   • test_calculation_factory.py
#   • calc.py
#   • Calculation.compute()
# ----------------------------------------------------------

from app.operations.calc_operations import add, subtract, multiply, divide
from app.models.cal_models import Calculation


class CalculationFactory:

    @staticmethod
    def create(type_: str, a, b) -> Calculation:
        """Return ORM Calculation object with computed result."""

        if not isinstance(type_, str):
            raise ValueError("Unsupported calculation type")

        op = type_.lower().strip()
        if op not in {"add", "subtract", "multiply", "divide"}:
            raise ValueError("Unsupported calculation type")

        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise ValueError("Input must be numeric.")

        # Compute using operation functions
        if op == "add":
            result = add(a, b)
        elif op == "subtract":
            result = subtract(a, b)
        elif op == "multiply":
            result = multiply(a, b)
        else:
            result = divide(a, b)

        # Return ORM object
        return Calculation(
            type=op,
            a=float(a),
            b=float(b),
            result=result,
            user_id=1   # test user
        )
