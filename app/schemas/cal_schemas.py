# ----------------------------------------------------------
# Author: Nandan Kumar
# Assignment-11: Calculator Schemas 
# File: app/schemas/cal_schemas.py
# ----------------------------------------------------------
# Description:
#   Defines Pydantic schemas for:
#     • Request payload for /calc/compute
#     • Response schema for API
#     • Internal schemas for DB operations
#
# Fixes:
#   • Added compute_result() logic in CalculationCreate
#   • Added validation for supported types and zero division
#   • CalculationRead now includes id, type, a, b, result, user_id
# ----------------------------------------------------------

from pydantic import BaseModel, Field, model_validator
from typing import Optional


# ==========================================================
# 1) Request schema for POST /calc/compute
# ==========================================================
class CalculationCompute(BaseModel):
    type: str = Field(..., description="Operation type: add/subtract/multiply/divide")
    a: float = Field(..., description="Operand A")
    b: float = Field(..., description="Operand B")


# ==========================================================
# 2) Response schema returned by API
# ==========================================================
class CalculationRead(BaseModel):
    id: Optional[int] = None
    type: str
    a: float
    b: float
    result: float
    user_id: Optional[int] = None


# ==========================================================
# 3) Schema used for DB creation in tests
# ==========================================================
class CalculationCreate(BaseModel):
    type: str
    a: float
    b: float
    result: Optional[float] = None
    user_id: Optional[int] = None

    @model_validator(mode="after")
    def compute_and_validate(cls, values):
        op_type = values.type.lower()
        a, b = values.a, values.b

        if op_type not in {"add", "subtract", "multiply", "divide"}:
            raise ValueError("Unsupported calculation type")

        if op_type == "divide" and b == 0:
            raise ValueError("Division by zero is not allowed")

        # Compute result
        if op_type == "add":
            values.result = a + b
        elif op_type == "subtract":
            values.result = a - b
        elif op_type == "multiply":
            values.result = a * b
        elif op_type == "divide":
            values.result = a / b

        return values

    def compute_result(self) -> float:
        return self.result


# ==========================================================
# 4) Schema for ORM → Schema conversion
# ==========================================================
class CalculationDBRead(BaseModel):
    id: int
    type: str
    a: float
    b: float
    result: float
    user_id: Optional[int]

    model_config = {"from_attributes": True}
