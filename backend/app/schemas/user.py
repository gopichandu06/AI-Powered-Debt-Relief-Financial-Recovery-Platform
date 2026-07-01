"""
FinRelief AI — User and Profile Pydantic schemas.
"""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


# ---------------------------------------------------------------------------
# User schemas
# ---------------------------------------------------------------------------


class UserBase(BaseModel):
    """Shared fields between user request/response schemas."""

    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)


class UserCreate(UserBase):
    """Payload to create a new user (includes plain-text password)."""

    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    """Public user representation returned from the API."""

    id: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Profile schemas
# ---------------------------------------------------------------------------

EmploymentType = Literal["salaried", "self_employed", "unemployed", "retired"]


class ProfileBase(BaseModel):
    """Fields that make up a financial profile."""

    monthly_income: float = Field(default=0.0, ge=0)
    monthly_expenses: float = Field(default=0.0, ge=0)
    employment_type: EmploymentType = "salaried"
    credit_score: int = Field(default=650, ge=300, le=900)
    dependents: int = Field(default=0, ge=0)
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)


class ProfileCreate(ProfileBase):
    """Payload to create or fully replace a profile."""
    pass


class ProfileUpdate(BaseModel):
    """Payload to partially update a profile — all fields optional."""

    monthly_income: Optional[float] = Field(default=None, ge=0)
    monthly_expenses: Optional[float] = Field(default=None, ge=0)
    employment_type: Optional[EmploymentType] = None
    credit_score: Optional[int] = Field(default=None, ge=300, le=900)
    dependents: Optional[int] = Field(default=None, ge=0)
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)


class ProfileResponse(ProfileBase):
    """Profile representation returned from the API."""

    id: str
    user_id: str
    created_at: datetime

    model_config = {"from_attributes": True}
