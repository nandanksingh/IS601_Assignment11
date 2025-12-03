# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/17/2025
# Assignment-11: Calculator API Schemas (Final)
# File: app/schemas/cal_schemas.py
# ----------------------------------------------------------
# Description:
#   Schemas required by professor test suite.
#
#   MUST support:
#      • /calc/compute          → CalculationCompute
#      • Only returns { result }
#      • No user_id required for compute route
#
#   Additional schemas kept minimal to satisfy:
#      • test_cal_model.py
#      • test_calculation_factory.py
# ----------------------------------------------------------

from pydantic import BaseModel, Field


# ==========================================================
# 1) Schema used by POST /calc/compute
# ==========================================================
class CalculationCompute(BaseModel):
    type: str = Field(..., description="Operation type: add/subtract/multiply/divide")
    a: float = Field(..., description="Operand A")
    b: float = Field(..., description="Operand B")


# ==========================================================
# 2) Response schema returned by API
# ==========================================================
class CalculationRead(BaseModel):
    result: float


# ==========================================================
# 3) Schema used INTERNALLY in tests (DB creation)
# ----------------------------------------------------------

class CalculationCreate(BaseModel):
    type: str
    a: float
    b: float
    result: float
    user_id: int | None = None

    model_config = {"from_attributes": True}


# ==========================================================
# 4) Schema used for ORM → Schema conversion
# ----------------------------------------------------------
class CalculationDBRead(BaseModel):
    id: int
    type: str
    a: float
    b: float
    result: float
    user_id: int | None

    model_config = {"from_attributes": True}
