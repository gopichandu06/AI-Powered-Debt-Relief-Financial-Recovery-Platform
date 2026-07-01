"""
FinRelief AI — Users and Profile API router.
Endpoints: user info, update name, profile CRUD.
"""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user, get_db
from app.models.profile import Profile
from app.models.user import User
from app.schemas.user import ProfileCreate, ProfileResponse, ProfileUpdate, UserResponse

router = APIRouter(prefix="/users", tags=["Users & Profile"])


# ─────────────────────────────────────────────────────────────────────────────
# User endpoints
# ─────────────────────────────────────────────────────────────────────────────


@router.get(
    "/",
    response_model=UserResponse,
    summary="Get current user information",
)
def get_user(current_user: User = Depends(get_current_active_user)) -> UserResponse:
    """Return the current authenticated user's account information."""
    return current_user


@router.put(
    "/",
    response_model=UserResponse,
    summary="Update user display name",
)
def update_user(
    full_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """Update the authenticated user's full name."""
    if not full_name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="full_name cannot be empty.",
        )
    current_user.full_name = full_name.strip()
    current_user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(current_user)
    return current_user


# ─────────────────────────────────────────────────────────────────────────────
# Profile endpoints
# ─────────────────────────────────────────────────────────────────────────────


def _get_or_create_profile(db: Session, user: User) -> Profile:
    """Return existing profile or auto-create a default one."""
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if profile is None:
        profile = Profile(
            id=str(uuid.uuid4()),
            user_id=user.id,
            monthly_income=0.0,
            monthly_expenses=0.0,
            employment_type="salaried",
            credit_score=650,
            dependents=0,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.get(
    "/profile",
    response_model=ProfileResponse,
    summary="Get the current user's financial profile",
)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ProfileResponse:
    """
    Retrieve the authenticated user's financial profile.
    A default profile is created automatically on first access.
    """
    profile = _get_or_create_profile(db, current_user)
    return profile


@router.put(
    "/profile",
    response_model=ProfileResponse,
    summary="Create or update the current user's financial profile",
)
def update_profile(
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ProfileResponse:
    """
    Update one or more fields of the authenticated user's financial profile.
    Only provided fields are updated (partial update / PATCH semantics).
    """
    profile = _get_or_create_profile(db, current_user)

    update_fields = profile_data.model_dump(exclude_none=True)
    for field, value in update_fields.items():
        setattr(profile, field, value)

    profile.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(profile)
    return profile
