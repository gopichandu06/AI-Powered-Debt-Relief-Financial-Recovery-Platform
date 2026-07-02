"""
FinRelief AI — Application Configuration
Loads settings from environment variables or .env file.
"""
from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # JWT
    SECRET_KEY: str = "dev-secret-key-change-in-production-32chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database
    DATABASE_URL: str = "sqlite:///./finrelief.db"

    # Google Gemini AI
    GEMINI_API_KEY: str = ""

    # App metadata
    APP_NAME: str = "FinRelief AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    from pydantic import field_validator
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
