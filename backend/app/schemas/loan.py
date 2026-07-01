"""
FinRelief AI — Loan Pydantic schemas.
"""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

LoanType = Literal["personal", "home", "auto", "student", "credit_card", "business"]
LoanStatus = Literal["active", "overdue", "defaulted", "settled"]


class LoanBase(BaseModel):
    """Fields shared across loan request/response schemas."""

    loan_type: LoanType
    lender_name: str = Field(..., min_length=1, max_length=255)
    loan_amount: float = Field(..., gt=0, description="Original sanctioned amount")
    outstanding_balance: float = Field(..., ge=0, description="Current outstanding balance")
    interest_rate: float = Field(..., ge=0, description="Interest rate % per annum")
    monthly_emi: float = Field(..., ge=0, description="Monthly instalment amount")
    overdue_months: int = Field(default=0, ge=0)
    loan_status: LoanStatus = "active"
    notes: Optional[str] = None


class LoanCreate(LoanBase):
    """Payload to add a new loan."""
    pass


class LoanUpdate(BaseModel):
    """Payload to partially update a loan — all fields optional."""

    loan_type: Optional[LoanType] = None
    lender_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    loan_amount: Optional[float] = Field(default=None, gt=0)
    outstanding_balance: Optional[float] = Field(default=None, ge=0)
    interest_rate: Optional[float] = Field(default=None, ge=0)
    monthly_emi: Optional[float] = Field(default=None, ge=0)
    overdue_months: Optional[int] = Field(default=None, ge=0)
    loan_status: Optional[LoanStatus] = None
    notes: Optional[str] = None


class LoanResponse(LoanBase):
    """Loan representation returned from the API."""

    id: str
    user_id: str
    created_at: datetime

    model_config = {"from_attributes": True}
