# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/17/2025
# Assignment-11: Calculation Router (Factory + DB Storage)
# File: app/routers/calc.py
# ----------------------------------------------------------

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.factory.calculation_factory import CalculationFactory
from app.models.cal_models import Calculation
from app.schemas.cal_schemas import CalculationCreate, CalculationRead
from app.database.dbase import get_session

router = APIRouter(prefix="/calc", tags=["Calculation"])


@router.post("/compute", response_model=CalculationRead)
def compute_calculation(
    payload: CalculationCreate,
    db: Session = Depends(get_session),
):
    """
    Compute result using CalculationFactory, store in DB,
    return CalculationRead schema.
    """

    # 1. Factory computation
    try:
        operation = CalculationFactory.create(
            payload.type, payload.a, payload.b
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    result_value = operation.result

    # 2. Default user_id to avoid FK failures
    user_id = getattr(payload, "user_id", None) or 1

    # 3. ORM Insert
    calc_entry = Calculation(
        type=payload.type,
        a=payload.a,
        b=payload.b,
        result=result_value,
        user_id=user_id,
    )

    try:
        db.add(calc_entry)
        db.commit()
        db.refresh(calc_entry)
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"error": f"Database error: {str(e)}"},
        )

    return CalculationRead.from_orm(calc_entry)