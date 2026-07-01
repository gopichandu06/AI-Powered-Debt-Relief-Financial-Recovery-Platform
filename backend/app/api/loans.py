"""
FinRelief AI — Loans API router.
Full CRUD for a user's loan/debt obligations.
"""
import json
import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user, get_db
from app.models.activity_log import ActivityLog
from app.models.loan import Loan
from app.models.user import User
from app.schemas.loan import LoanCreate, LoanResponse, LoanUpdate

router = APIRouter(prefix="/loans", tags=["Loans"])


def _log_activity(
    db: Session,
    user_id: str,
    action: str,
    entity_id: str = None,
    metadata: dict = None,
) -> None:
    """Helper to write an activity log entry."""
    log = ActivityLog(
        id=str(uuid.uuid4()),
        user_id=user_id,
        action=action,
        entity_type="loan",
        entity_id=entity_id,
        metadata_json=json.dumps(metadata) if metadata else None,
    )
    db.add(log)
    # Flush without committing so the log is part of the same transaction


def _get_loan_or_404(db: Session, loan_id: str, user_id: str) -> Loan:
    """Fetch a loan by ID, scoped to the current user. Raises 404 if not found."""
    loan = (
        db.query(Loan)
        .filter(Loan.id == loan_id, Loan.user_id == user_id)
        .first()
    )
    if loan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Loan '{loan_id}' not found.",
        )
    return loan


@router.get(
    "/",
    response_model=List[LoanResponse],
    summary="List all loans for the current user",
)
def list_loans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[LoanResponse]:
    """Return all loan records belonging to the authenticated user."""
    loans = (
        db.query(Loan)
        .filter(Loan.user_id == current_user.id)
        .order_by(Loan.created_at.desc())
        .all()
    )
    return loans


@router.post(
    "/",
    response_model=LoanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new loan",
)
def create_loan(
    loan_data: LoanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> LoanResponse:
    """Create a new loan record for the authenticated user."""
    loan = Loan(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        **loan_data.model_dump(),
    )
    db.add(loan)

    _log_activity(
        db,
        user_id=current_user.id,
        action="loan_added",
        entity_id=loan.id,
        metadata={
            "lender_name": loan.lender_name,
            "loan_type": loan.loan_type,
            "outstanding_balance": loan.outstanding_balance,
        },
    )

    db.commit()
    db.refresh(loan)
    return loan


@router.get(
    "/{loan_id}",
    response_model=LoanResponse,
    summary="Get a specific loan by ID",
)
def get_loan(
    loan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> LoanResponse:
    """Retrieve a single loan record by its UUID."""
    return _get_loan_or_404(db, loan_id, current_user.id)


@router.put(
    "/{loan_id}",
    response_model=LoanResponse,
    summary="Update a loan",
)
def update_loan(
    loan_id: str,
    loan_data: LoanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> LoanResponse:
    """Partially update a loan record. Only provided fields are modified."""
    loan = _get_loan_or_404(db, loan_id, current_user.id)

    update_fields = loan_data.model_dump(exclude_none=True)
    for field, value in update_fields.items():
        setattr(loan, field, value)

    loan.updated_at = datetime.now(timezone.utc)

    _log_activity(
        db,
        user_id=current_user.id,
        action="loan_updated",
        entity_id=loan.id,
        metadata={"updated_fields": list(update_fields.keys())},
    )

    db.commit()
    db.refresh(loan)
    return loan


@router.delete(
    "/{loan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a loan",
)
def delete_loan(
    loan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """Permanently delete a loan record."""
    loan = _get_loan_or_404(db, loan_id, current_user.id)

    _log_activity(
        db,
        user_id=current_user.id,
        action="loan_deleted",
        entity_id=loan_id,
        metadata={"lender_name": loan.lender_name, "loan_type": loan.loan_type},
    )

    db.delete(loan)
    db.commit()
