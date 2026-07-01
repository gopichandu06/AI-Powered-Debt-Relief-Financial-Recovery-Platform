"""
FinRelief AI — User Financial Profile ORM model.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Profile(Base):
    """Financial profile linked one-to-one with a User."""

    __tablename__ = "profiles"

    id: str = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )
    user_id: str = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    # Financial details
    monthly_income: float = Column(Float, default=0.0, nullable=False)
    monthly_expenses: float = Column(Float, default=0.0, nullable=False)

    # Employment
    employment_type: str = Column(
        String(50), default="salaried", nullable=False
    )  # salaried / self_employed / unemployed / retired

    # Credit
    credit_score: int = Column(Integer, default=650, nullable=False)

    # Personal
    dependents: int = Column(Integer, default=0, nullable=False)
    city: str = Column(String(100), nullable=True)
    state: str = Column(String(100), nullable=True)

    created_at: datetime = Column(DateTime, default=_utcnow, nullable=False)
    updated_at: datetime = Column(
        DateTime, default=_utcnow, onupdate=_utcnow, nullable=False
    )

    # Relationship
    user = relationship("User", back_populates="profile")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Profile user_id={self.user_id} income={self.monthly_income}>"
