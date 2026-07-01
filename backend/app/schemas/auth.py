"""
FinRelief AI — Authentication Pydantic schemas.
"""
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Payload for new user registration."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    full_name: str = Field(..., min_length=1, max_length=255, description="User's full name")


class UserLogin(BaseModel):
    """Payload for user login (JSON body alternative to OAuth2 form)."""

    email: EmailStr = Field(..., description="Registered email address")
    password: str = Field(..., description="Account password")


class Token(BaseModel):
    """JWT token response returned after successful authentication."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Decoded data extracted from a JWT payload."""

    email: Optional[str] = None
