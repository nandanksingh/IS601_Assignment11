# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/17/2025
# Assignment-11: Calculation Pydantic Schemas 
# File: app/schemas/cal_schemas.py
# ----------------------------------------------------------

from pydantic import BaseModel, field_validator
from typing import Optional

VALID_OPERATIONS = {"add", "subtract", "multiply", "divide"}


class CalculationCreate(BaseModel):
    type: str
    a: float
    b: float

    # Normalize + validate type
    @field_validator("type")
    def validate_type(cls, v: str):
        normalized = v.strip().lower()
        if normalized not in VALID_OPERATIONS:
            raise ValueError(f"Invalid operation: {v}")
        return normalized

    # Validate numeric fields
    @field_validator("a", "b")
    def validate_numeric(cls, v):
        if not isinstance(v, (int, float)):
            raise ValueError("Inputs must be numeric.")
        return float(v)

    # Prevent divide-by-zero
    @field_validator("b")
    def check_div_zero(cls, v, info):
        op = info.data.get("type")
        if op == "divide" and v == 0:
            raise ValueError("Cannot divide by zero.")
        return v

    # REQUIRED BY TESTS
    def compute_result(self) -> float:
        if self.type == "add":
            return float(self.a + self.b)
        if self.type == "subtract":
            return float(self.a - self.b)
        if self.type == "multiply":
            return float(self.a * self.b)
        if self.type == "divide":
            return float(self.a / self.b)
        raise ValueError("Invalid operation")


class CalculationRead(BaseModel):
    id: int
    type: str
    a: float
    b: float
    result: float
    user_id: Optional[int] = None

    class Config:
        from_attributes = True
