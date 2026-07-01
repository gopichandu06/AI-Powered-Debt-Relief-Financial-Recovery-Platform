"""
FinRelief AI — Loan ORM model.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Loan(Base):
    """Represents a single loan/debt obligation of a user."""

    __tablename__ = "loans"

    id: str = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )
    user_id: str = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Loan classification
    loan_type: str = Column(
        String(50), nullable=False
    )  # personal / home / auto / student / credit_card / business
    lender_name: str = Column(String(255), nullable=False)

    # Financials
    loan_amount: float = Column(Float, nullable=False)          # Original sanctioned amount
    outstanding_balance: float = Column(Float, nullable=False)  # Current remaining balance
    interest_rate: float = Column(Float, nullable=False)        # % per annum
    monthly_emi: float = Column(Float, nullable=False)

    # Status
    overdue_months: int = Column(Integer, default=0, nullable=False)
    loan_status: str = Column(
        String(30), default="active", nullable=False
    )  # active / overdue / defaulted / settled

    # Notes
    notes: str = Column(Text, nullable=True)

    created_at: datetime = Column(DateTime, default=_utcnow, nullable=False)
    updated_at: datetime = Column(
        DateTime, default=_utcnow, onupdate=_utcnow, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="loans")
    settlements = relationship(
        "SettlementHistory", back_populates="loan", cascade="all, delete-orphan"
    )
    negotiations = relationship(
        "NegotiationHistory", back_populates="loan", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Loan id={self.id} lender={self.lender_name} status={self.loan_status}>"
