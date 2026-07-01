"""
FinRelief AI — Settlement and Letter Pydantic schemas.
"""
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

ToneType = Literal["professional", "urgent", "hardship"]


# ---------------------------------------------------------------------------
# Settlement schemas
# ---------------------------------------------------------------------------


class SettlementRequest(BaseModel):
    """
    Settlement calculation request.
    Uses the authenticated user's stored profile and loan data — no body required.
    """
    pass


class PerLoanSettlement(BaseModel):
    """Settlement details for a single loan."""

    loan_id: str
    loan_type: str
    lender_name: str
    outstanding_balance: float
    settlement_percentage: float = Field(..., description="Discount percentage offered (e.g. 45.0)")
    settlement_amount: float = Field(..., description="Amount to pay in settlement")
    savings_amount: float = Field(..., description="Amount saved vs. full repayment")
    priority: int = Field(..., description="Repayment priority (1 = highest urgency)")
    strategy: str = Field(..., description="Suggested action for this specific loan")
    loan_status: str
    overdue_months: int


class SettlementResponse(BaseModel):
    """Full settlement analysis response."""

    financial_health_score: int
    debt_stress_level: str
    risk_category: str
    total_outstanding: float
    total_settlement_amount: float
    total_savings: float
    total_loans: int
    loans: List[PerLoanSettlement]
    overall_strategy: str
    payment_strategy: str
    reasoning: str
    ai_generated: bool
    calculated_at: datetime


# ---------------------------------------------------------------------------
# Letter schemas
# ---------------------------------------------------------------------------


class LetterRequest(BaseModel):
    """Payload to request a negotiation letter."""

    loan_id: str = Field(..., description="ID of the loan to write a letter for")
    tone: ToneType = Field(default="professional", description="Letter tone/style")
    include_income: bool = Field(
        default=True, description="Whether to include income details in the letter"
    )


class LetterResponse(BaseModel):
    """Generated negotiation letter response."""

    id: str
    letter_content: str
    lender_name: str
    loan_type: str
    outstanding_balance: float
    tone: str
    ai_generated: bool
    created_at: datetime


class LetterListItem(BaseModel):
    """Summary item for listing letters."""

    id: str
    lender_name: str
    loan_type: Optional[str] = None
    ai_generated: bool
    created_at: datetime

    model_config = {"from_attributes": True}
