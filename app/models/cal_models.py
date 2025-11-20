# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/19/2025
# Assignment-11: Calculation SQLAlchemy Model 
# File: app/models/cal_models.py
# ----------------------------------------------------------
# Description:
# SQLAlchemy model that stores all calculator operations
# performed by authenticated users.
#
# Fully compatible with:
#   • CalculationCreate / CalculationRead (Pydantic v2)
#   • Factory Pattern (CalculationFactory)
#   • Assignment-11 integration tests:
#        - FK integrity tests
#        - ORM persistence tests
#        - test_invalid_user_id_fails
#
# Notes:
#   • ForeignKey includes ondelete="CASCADE"
#     ensuring test_invalid_user_id_fails correctly triggers
#     sqlalchemy.exc.IntegrityError when invalid user_id is used.
# ----------------------------------------------------------

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database.dbase import Base


class Calculation(Base):
    __tablename__ = "calculations"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Operation type: add / subtract / multiply / divide
    type = Column(String(20), nullable=False)

    # Numeric operands
    a = Column(Float, nullable=False)
    b = Column(Float, nullable=False)

    # Computed result of the operation
    result = Column(Float, nullable=False)

    # FK → users.id
    # CASCADE ensures proper behavior in test_invalid_user_id_fails
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationship to User model
    user = relationship("User", back_populates="calculations")

    def __repr__(self) -> str:
        """
        Safe string representation used in multiple test cases.
        Never raises errors even if fields are None.
        """
        return (
            f"Calculation(id={self.id}, type='{self.type}', "
            f"a={self.a}, b={self.b}, result={self.result}, "
            f"user_id={self.user_id})"
        )
