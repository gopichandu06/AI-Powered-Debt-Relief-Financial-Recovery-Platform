"""
FinRelief AI — Settlement API router.
Endpoints: calculate settlement, request AI advice, view history.
"""
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user, get_db
from app.models.activity_log import ActivityLog
from app.models.ai_response import AIResponse
from app.models.loan import Loan
from app.models.profile import Profile
from app.models.settlement import SettlementHistory
from app.models.user import User
from app.services.financial_engine import FinancialEngine
from app.services.gemini_service import gemini_service
from app.services.settlement_engine import SettlementEngine

router = APIRouter(prefix="/settlement", tags=["Settlement"])


def _require_loans(loans: list) -> None:
    if not loans:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No loans found. Please add at least one loan before running settlement analysis.",
        )


def _require_profile(profile) -> None:
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Financial profile not found. Please complete your profile before running analysis.",
        )


@router.post(
    "/calculate",
    summary="Run settlement analysis for all user loans",
)
def calculate_settlement(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Run the settlement engine against the current user's profile and loans.

    Computes optimal settlement percentages, savings, and strategy for every
    active loan. Results are persisted to settlement history.
    """
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    loans = (
        db.query(Loan)
        .filter(Loan.user_id == current_user.id, Loan.loan_status != "settled")
        .all()
    )

    _require_loans(loans)
    _require_profile(profile)

    # Run engines
    financial_metrics = FinancialEngine.calculate_all_metrics(profile, loans)
    settlement_result = SettlementEngine.calculate_all_settlements(
        profile, loans, financial_metrics
    )

    # Persist a summary record per loan
    for loan_settlement in settlement_result["loans"]:
        record = SettlementHistory(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            loan_id=loan_settlement["loan_id"],
            settlement_percentage=loan_settlement["settlement_percentage"],
            settlement_amount=loan_settlement["settlement_amount"],
            savings_amount=loan_settlement["savings_amount"],
            strategy_json=json.dumps(loan_settlement),
            reasoning=settlement_result["reasoning"],
            ai_generated=False,
        )
        db.add(record)

    # Log activity
    activity = ActivityLog(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        action="settlement_calculated",
        entity_type="settlement",
        metadata_json=json.dumps(
            {
                "total_outstanding": settlement_result["total_outstanding"],
                "total_settlement_amount": settlement_result["total_settlement_amount"],
                "total_savings": settlement_result["total_savings"],
                "health_score": settlement_result["financial_health_score"],
            }
        ),
    )
    db.add(activity)
    db.commit()

    settlement_result["calculated_at"] = datetime.now(timezone.utc).isoformat()
    return settlement_result


@router.post(
    "/ai-advice",
    summary="Get AI-powered settlement advice from Gemini",
)
async def get_ai_advice(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Generate Gemini-powered settlement advice.

    The endpoint computes all financial metrics and settlement data internally,
    then sends them to Gemini for contextual analysis.
    Falls back to the deterministic engine when Gemini is unavailable.
    """
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    loans = (
        db.query(Loan)
        .filter(Loan.user_id == current_user.id, Loan.loan_status != "settled")
        .all()
    )

    _require_loans(loans)
    _require_profile(profile)

    financial_metrics = FinancialEngine.calculate_all_metrics(profile, loans)
    settlement_data = SettlementEngine.calculate_all_settlements(
        profile, loans, financial_metrics
    )

    # Call Gemini (or fallback)
    advice = await gemini_service.get_settlement_advice(financial_metrics, settlement_data)

    # Persist AI response for caching / auditing
    prompt_content = json.dumps(
        {"financial_metrics": financial_metrics, "settlement_data": settlement_data},
        default=str,
    )
    ai_record = AIResponse(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        prompt_type="settlement",
        prompt_hash=gemini_service._hash_prompt(prompt_content),
        response=json.dumps(advice, default=str),
        model_used="gemini-2.0-flash" if advice.get("ai_generated") else "fallback",
        tokens_used=0,
    )
    db.add(ai_record)

    # Log activity
    activity = ActivityLog(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        action="ai_advice_requested",
        entity_type="ai_response",
        entity_id=ai_record.id,
        metadata_json=json.dumps({"ai_generated": advice.get("ai_generated", False)}),
    )
    db.add(activity)
    db.commit()

    return advice


@router.get(
    "/history",
    summary="Get settlement history for the current user",
)
def get_settlement_history(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[Dict[str, Any]]:
    """
    Return a paginated list of past settlement calculations for the user.
    """
    records = (
        db.query(SettlementHistory)
        .filter(SettlementHistory.user_id == current_user.id)
        .order_by(SettlementHistory.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    results = []
    for record in records:
        strategy_data = {}
        if record.strategy_json:
            try:
                strategy_data = json.loads(record.strategy_json)
            except (json.JSONDecodeError, ValueError):
                strategy_data = {}

        results.append(
            {
                "id": record.id,
                "loan_id": record.loan_id,
                "lender_name": strategy_data.get("lender_name", "Unknown"),
                "loan_type": strategy_data.get("loan_type", "Unknown"),
                "settlement_percentage": record.settlement_percentage,
                "settlement_amount": record.settlement_amount,
                "savings_amount": record.savings_amount,
                "ai_generated": record.ai_generated,
                "created_at": record.created_at.isoformat(),
            }
        )

    return results
