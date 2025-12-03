# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/16/2025
# Assignment-11: Calculation ORM Model 
# File: app/models/cal_models.py
# ----------------------------------------------------------
# Description:
# This module defines the Calculation ORM model used for storing
# arithmetic operations in the database. Each record belongs to
# a user and stores operation type, numeric inputs, and computed
# result. The model includes helper methods for computing the
# output using the CalculationFactory in a consistent manner.
# ----------------------------------------------------------

from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.dbase import Base


class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    a = Column(Float, nullable=False)
    b = Column(Float, nullable=False)
    result = Column(Float, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="calculations")

    # ------------------------------------------------------
    # Compute result using the CalculationFactory
    # ------------------------------------------------------
    def compute(self) -> float:
        from app.factory.calculation_factory import CalculationFactory
        operation = CalculationFactory.create(self.type, self.a, self.b)
        return operation.result

    # ------------------------------------------------------
    # Compute and persist result in object attribute
    # ------------------------------------------------------
    def compute_and_set_result(self) -> float:
        self.result = self.compute()
        return self.result

    # ------------------------------------------------------
    # Debug-friendly representation
    # ------------------------------------------------------
    def __repr__(self):
        return (
            f"Calculation(id={self.id}, "
            f"type='{self.type}', a={self.a}, "
            f"b={self.b}, result={self.result})"
        )
