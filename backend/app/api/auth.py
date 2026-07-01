"""
FinRelief AI — Authentication API router.
Endpoints: register, login (OAuth2), /me, logout.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user, get_db
from app.core.security import create_access_token
from app.schemas.auth import Token, UserRegister
from app.schemas.user import UserResponse
from app.services.auth_service import authenticate_user, create_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
def register(user_data: UserRegister, db: Session = Depends(get_db)) -> Token:
    """
    Create a new user account and return a JWT access token.

    - **email**: Must be a valid, unique email address.
    - **password**: Minimum 8 characters.
    - **full_name**: User's display name.
    """
    try:
        user = create_user(db, user_data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token, token_type="bearer")


@router.post(
    "/login",
    response_model=Token,
    summary="Obtain a JWT token (OAuth2 password flow)",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    """
    Authenticate with email + password and receive a Bearer token.
    The **username** field should contain the user's email address.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the currently authenticated user",
)
def get_me(current_user=Depends(get_current_active_user)) -> UserResponse:
    """Return the profile of the currently authenticated user."""
    return current_user


@router.post(
    "/logout",
    summary="Logout (client-side token invalidation)",
)
def logout() -> dict:
    """
    Instruct the client to discard its token.
    JWTs are stateless — actual invalidation happens by deleting the token
    on the client side.
    """
    return {"message": "Successfully logged out. Please discard your access token."}
