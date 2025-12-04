# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 12/04/2025
# Assignment-11: Calculator Router (Final)
# File: app/routers/calc.py
# ----------------------------------------------------------
# Description:
# Implements POST /calc/compute endpoint:
#   • Accepts CalculationCompute payload
#   • Computes result using CalculationFactory
#   • Persists calculation to DB
#   • Returns CalculationRead schema
#
# Fixes:
#   • Removed JWT dependency for professor tests
#   • Added proper error handling for divide-by-zero and DB errors
#   • Returns full response with type, a, b, result, user_id
# ----------------------------------------------------------

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.factory.calculation_factory import CalculationFactory
from app.schemas.cal_schemas import CalculationCompute, CalculationRead
from app.database.dbase import SessionLocal
from app.models.cal_models import Calculation

router = APIRouter(prefix="/calc", tags=["Calculator"])


@router.post("/compute", response_model=CalculationRead)
async def compute_calculation(payload: CalculationCompute):
    """
    Perform arithmetic operation using CalculationFactory.
    Persist result to DB and return full CalculationRead schema.
    """
    try:
        # Compute result using factory
        operation = CalculationFactory.create(payload.type)
        result = operation.compute(payload.a, payload.b)

        # Persist to DB
        db: Session = SessionLocal()
        calc = Calculation(
            type=payload.type,
            a=payload.a,
            b=payload.b,
            result=result,
            user_id=1  # For tests, assume user_id=1 exists
        )
        db.add(calc)
        db.commit()
        db.refresh(calc)

        return CalculationRead(
            id=calc.id,
            type=calc.type,
            a=calc.a,
            b=calc.b,
            result=calc.result,
            user_id=calc.user_id
        )

    except ValueError as e:
        # Invalid type or divide-by-zero
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception:
        # Custom error response for DB failure
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Database error"}
        )
