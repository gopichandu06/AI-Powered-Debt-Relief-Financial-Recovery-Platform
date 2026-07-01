"""
FinRelief AI — Authentication service.
Business logic for creating and authenticating users.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import UserRegister


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Look up a user by their email address.

    Args:
        db: Active database session.
        email: Email to query.

    Returns:
        User instance or None if not found.
    """
    return db.query(User).filter(User.email == email.lower().strip()).first()


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """
    Look up a user by their primary key (UUID string).

    Args:
        db: Active database session.
        user_id: UUID string.

    Returns:
        User instance or None if not found.
    """
    return db.query(User).filter(User.id == user_id).first()


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Verify the email/password combination.

    Returns:
        The User on success, None on failure.
    """
    user = get_user_by_email(db, email)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user(db: Session, user_data: UserRegister) -> User:
    """
    Create a new user record in the database.

    Args:
        db: Active database session.
        user_data: Validated registration payload.

    Returns:
        Newly created User instance (already committed).

    Raises:
        ValueError: If the email is already registered.
    """
    existing = get_user_by_email(db, user_data.email)
    if existing is not None:
        raise ValueError(f"Email '{user_data.email}' is already registered.")

    user = User(
        email=user_data.email.lower().strip(),
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name.strip(),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
