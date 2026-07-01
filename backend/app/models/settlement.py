"""
FinRelief AI — Settlement History ORM model.
Stores records of each settlement calculation performed.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SettlementHistory(Base):
    """Persists a settlement calculation result for auditing and history display."""

    __tablename__ = "settlement_history"

    id: str = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )
    user_id: str = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    loan_id: str = Column(
        String(36), ForeignKey("loans.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Settlement figures
    settlement_percentage: float = Column(Float, nullable=False)
    settlement_amount: float = Column(Float, nullable=False)
    savings_amount: float = Column(Float, nullable=False)

    # Serialised strategy / reasoning
    strategy_json: str = Column(Text, nullable=True)   # JSON string
    reasoning: str = Column(Text, nullable=True)

    # Source
    ai_generated: bool = Column(Boolean, default=False, nullable=False)

    created_at: datetime = Column(DateTime, default=_utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="settlements")
    loan = relationship("Loan", back_populates="settlements")

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<SettlementHistory id={self.id} user_id={self.user_id} "
            f"pct={self.settlement_percentage}%>"
        )
