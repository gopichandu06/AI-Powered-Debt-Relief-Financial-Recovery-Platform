"""
FinRelief AI — Negotiation History ORM model.
Stores generated negotiation/settlement letters.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class NegotiationHistory(Base):
    """Persists a generated lender negotiation letter."""

    __tablename__ = "negotiation_history"

    id: str = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )
    user_id: str = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    loan_id: str = Column(
        String(36), ForeignKey("loans.id", ondelete="SET NULL"), nullable=True, index=True
    )

    lender_name: str = Column(String(255), nullable=False)
    letter_content: str = Column(Text, nullable=False)
    ai_generated: bool = Column(Boolean, default=False, nullable=False)

    created_at: datetime = Column(DateTime, default=_utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="negotiations")
    loan = relationship("Loan", back_populates="negotiations")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<NegotiationHistory id={self.id} lender={self.lender_name}>"
