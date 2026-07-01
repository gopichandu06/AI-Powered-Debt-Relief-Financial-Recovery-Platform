"""
FinRelief AI — Letters (Negotiation) API router.
Endpoints: generate letter, list letters, get specific letter.
"""
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user, get_db
from app.models.activity_log import ActivityLog
from app.models.loan import Loan
from app.models.negotiation import NegotiationHistory
from app.models.profile import Profile
from app.models.user import User
from app.schemas.settlement import LetterListItem, LetterRequest, LetterResponse
from app.services.gemini_service import gemini_service

router = APIRouter(prefix="/letters", tags=["Negotiation Letters"])


@router.post(
    "/generate",
    response_model=LetterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a negotiation letter for a specific loan",
)
async def generate_letter(
    request: LetterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> LetterResponse:
    """
    Generate a professional debt negotiation letter for the specified loan.

    The letter is addressed to the lender and includes:
    - Borrower details
    - Loan account information
    - Hardship explanation
    - One-Time Settlement (OTS) offer
    - Acceptance conditions

    Uses Gemini AI when available, otherwise uses the deterministic fallback engine.
    """
    # Fetch loan
    loan = (
        db.query(Loan)
        .filter(Loan.id == request.loan_id, Loan.user_id == current_user.id)
        .first()
    )
    if loan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Loan '{request.loan_id}' not found.",
        )

    # Fetch profile
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()

    # Build data payloads
    loan_data = {
        "loan_id": loan.id,
        "lender_name": loan.lender_name,
        "loan_type": loan.loan_type,
        "outstanding_balance": loan.outstanding_balance,
        "loan_amount": loan.loan_amount,
        "interest_rate": loan.interest_rate,
        "monthly_emi": loan.monthly_emi,
        "overdue_months": loan.overdue_months,
        "loan_status": loan.loan_status,
        "notes": loan.notes,
    }

    profile_data = {
        "full_name": current_user.full_name,
        "email": current_user.email,
        "city": profile.city if profile else None,
        "state": profile.state if profile else None,
        "employment_type": profile.employment_type if profile else "salaried",
        "credit_score": profile.credit_score if profile else 650,
        "dependents": profile.dependents if profile else 0,
    }

    if request.include_income and profile:
        profile_data["monthly_income"] = profile.monthly_income

    # Call Gemini or fallback
    result = await gemini_service.generate_negotiation_letter(
        loan_data=loan_data,
        profile_data=profile_data,
        tone=request.tone,
        include_income=request.include_income,
    )

    letter_text: str = result["letter"]
    ai_generated: bool = result["ai_generated"]

    # Persist to DB
    record = NegotiationHistory(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        loan_id=loan.id,
        lender_name=loan.lender_name,
        letter_content=letter_text,
        ai_generated=ai_generated,
    )
    db.add(record)

    # Log activity
    activity = ActivityLog(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        action="letter_generated",
        entity_type="negotiation",
        entity_id=record.id,
        metadata_json=json.dumps(
            {
                "loan_id": loan.id,
                "lender_name": loan.lender_name,
                "tone": request.tone,
                "ai_generated": ai_generated,
            }
        ),
    )
    db.add(activity)
    db.commit()
    db.refresh(record)

    return LetterResponse(
        id=record.id,
        letter_content=letter_text,
        lender_name=loan.lender_name,
        loan_type=loan.loan_type,
        outstanding_balance=loan.outstanding_balance,
        tone=request.tone,
        ai_generated=ai_generated,
        created_at=record.created_at,
    )


@router.get(
    "/",
    response_model=List[LetterListItem],
    summary="List all negotiation letters for the current user",
)
def list_letters(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[LetterListItem]:
    """
    Return a paginated list of all previously generated negotiation letters.
    """
    records = (
        db.query(NegotiationHistory)
        .filter(NegotiationHistory.user_id == current_user.id)
        .order_by(NegotiationHistory.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    results = []
    for record in records:
        # Fetch loan_type from related loan if available
        loan_type = None
        if record.loan_id:
            loan = db.query(Loan).filter(Loan.id == record.loan_id).first()
            if loan:
                loan_type = loan.loan_type

        results.append(
            LetterListItem(
                id=record.id,
                lender_name=record.lender_name,
                loan_type=loan_type,
                ai_generated=record.ai_generated,
                created_at=record.created_at,
            )
        )

    return results


@router.get(
    "/{letter_id}",
    summary="Get a specific negotiation letter by ID",
)
def get_letter(
    letter_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Retrieve the full content of a specific negotiation letter."""
    record = (
        db.query(NegotiationHistory)
        .filter(
            NegotiationHistory.id == letter_id,
            NegotiationHistory.user_id == current_user.id,
        )
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Letter '{letter_id}' not found.",
        )

    loan_type = None
    loan_outstanding = None
    if record.loan_id:
        loan = db.query(Loan).filter(Loan.id == record.loan_id).first()
        if loan:
            loan_type = loan.loan_type
            loan_outstanding = loan.outstanding_balance

    return {
        "id": record.id,
        "loan_id": record.loan_id,
        "lender_name": record.lender_name,
        "loan_type": loan_type,
        "outstanding_balance": loan_outstanding,
        "letter_content": record.letter_content,
        "ai_generated": record.ai_generated,
        "created_at": record.created_at.isoformat(),
    }
