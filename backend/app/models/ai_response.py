"""
FinRelief AI — AI Response cache/log ORM model.
Caches Gemini responses keyed by a prompt hash to avoid duplicate API calls.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AIResponse(Base):
    """Stores raw AI (Gemini) responses for caching and auditing."""

    __tablename__ = "ai_responses"

    id: str = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )
    user_id: str = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Classification
    prompt_type: str = Column(
        String(50), nullable=False
    )  # settlement / letter / strategy / advice
    prompt_hash: str = Column(String(64), index=True, nullable=False)

    # Content
    response: str = Column(Text, nullable=False)  # JSON string from Gemini

    # Metadata
    model_used: str = Column(String(100), default="gemini-2.0-flash", nullable=False)
    tokens_used: int = Column(Integer, default=0, nullable=False)

    created_at: datetime = Column(DateTime, default=_utcnow, nullable=False)

    # Relationship
    user = relationship("User", back_populates="ai_responses")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AIResponse id={self.id} type={self.prompt_type} model={self.model_used}>"
