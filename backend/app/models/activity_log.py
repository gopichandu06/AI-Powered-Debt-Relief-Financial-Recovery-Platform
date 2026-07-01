"""
FinRelief AI — Activity Log ORM model.
Tracks every significant user action for audit trails and dashboard widgets.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ActivityLog(Base):
    """Immutable audit record of a user action."""

    __tablename__ = "activity_logs"

    id: str = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )
    user_id: str = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Action descriptor (e.g. 'loan_added', 'settlement_calculated', 'letter_generated')
    action: str = Column(String(255), nullable=False)

    # Optional reference to the affected entity
    entity_type: str = Column(String(100), nullable=True)
    entity_id: str = Column(String(36), nullable=True)

    # Arbitrary JSON payload (serialised dict)
    metadata_json: str = Column(Text, nullable=True)

    created_at: datetime = Column(DateTime, default=_utcnow, nullable=False)

    # Relationship
    user = relationship("User", back_populates="activity_logs")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ActivityLog id={self.id} action={self.action} user={self.user_id}>"
