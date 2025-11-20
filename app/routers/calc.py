# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/20/2025
# Assignment-11: Calculator Router (Factory + /calc/compute API)
# File: app/routers/calc.py
# ----------------------------------------------------------
# Description:
#   SINGLE endpoint required by professor & test suite:
#       POST /calc/compute
#
#   Accepts:
#       {
#         "type": "add" | "subtract" | "multiply" | "divide",
#         "a": 5,
#         "b": 7
#       }
#
#   Returns:
#       { "result": 12 }
#
#   Fully compatible with:
#       • test_fastapi_calculator.py
#       • test_e2e.py
#       • templates/index.html (UI)
# ----------------------------------------------------------

from fastapi import APIRouter, HTTPException, status
from app.factory.calculation_factory import CalculationFactory
from app.schemas.cal_schemas import CalculationCompute, CalculationRead

router = APIRouter(prefix="/calc", tags=["Calculator"])


@router.post("/compute", response_model=CalculationRead)
async def compute_calculation(payload: CalculationCompute):
    """
    Perform arithmetic operation using CalculationFactory.
    This endpoint is the ONLY one required by professor's tests.
    """
    try:
        operation = CalculationFactory.create(payload.type)
        result = operation.compute(payload.a, payload.b)

    except ValueError as e:
        # Wrong operation name or divide-by-zero
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return CalculationRead(result=result)
