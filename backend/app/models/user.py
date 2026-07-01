"""
FinRelief AI — User ORM model.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.orm import relationship

from app.db.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    """Registered application user."""

    __tablename__ = "users"

    id: str = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )
    email: str = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password: str = Column(String(255), nullable=False)
    full_name: str = Column(String(255), nullable=False)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    created_at: datetime = Column(DateTime, default=_utcnow, nullable=False)
    updated_at: datetime = Column(
        DateTime, default=_utcnow, onupdate=_utcnow, nullable=False
    )

    # Relationships
    profile = relationship(
        "Profile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    loans = relationship(
        "Loan", back_populates="user", cascade="all, delete-orphan"
    )
    settlements = relationship(
        "SettlementHistory", back_populates="user", cascade="all, delete-orphan"
    )
    negotiations = relationship(
        "NegotiationHistory", back_populates="user", cascade="all, delete-orphan"
    )
    ai_responses = relationship(
        "AIResponse", back_populates="user", cascade="all, delete-orphan"
    )
    activity_logs = relationship(
        "ActivityLog", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User id={self.id} email={self.email}>"
