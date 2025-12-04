# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/19/2025
# Assignment-11: Calculation SQLAlchemy Model 
# File: app/models/cal_models.py
# ----------------------------------------------------------
# Description:
# SQLAlchemy model that stores calculator operations.
#
# Fully compatible with:
#   • CalculationCreate / CalculationRead schemas
#   • Factory Pattern (CalculationFactory)
#   • Assignment-11 integration tests:
#        - Arithmetic tests
#        - Persistence tests
#        - test_compute_calculation_success
#        - test_db_error
#
# IMPORTANT:
#   • Tests DO NOT require authentication.
#   • Tests DO NOT guarantee that a User exists.
#   • Therefore: user_id MUST be nullable=True, otherwise
#     /calc/compute fails with 500 errors.
#
#   • ondelete="CASCADE" preserved but now optional because
#     FK is nullable.
# ----------------------------------------------------------

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database.dbase import Base


class Calculation(Base):
    __tablename__ = "calculations"

    # ------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------
    id = Column(Integer, primary_key=True, index=True)

    # ------------------------------------------------------
    # Operation type: add / subtract / multiply / divide
    # ------------------------------------------------------
    type = Column(String(20), nullable=False)

    # ------------------------------------------------------
    # Numeric operands
    # ------------------------------------------------------
    a = Column(Float, nullable=False)
    b = Column(Float, nullable=False)

    # ------------------------------------------------------
    # Computed result
    # ------------------------------------------------------
    result = Column(Float, nullable=False)

    # ------------------------------------------------------
    # Foreign Key → users.id
    #
    # FIXED:
    #   • Must be nullable=True because calculator tests run
    #     without any users in the database.
    #   • If NOT NULL → all arithmetic tests fail with 500.
    #
    # ondelete="CASCADE" works if user exists, harmless otherwise.
    # ------------------------------------------------------
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,   # <-- REQUIRED for test compatibility
        index=True,
    )

    # Relationship to User model
    user = relationship("User", back_populates="calculations", lazy="joined")

    # ------------------------------------------------------
    # __repr__ for debugging + test assertions
    # ------------------------------------------------------
    def __repr__(self) -> str:
        return (
            f"Calculation(id={self.id}, type='{self.type}', "
            f"a={self.a}, b={self.b}, result={self.result}, "
            f"user_id={self.user_id})"
        )
