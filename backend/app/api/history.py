"""
FinRelief AI — History API router.
Endpoints: settlement history, letter history, activity log, summary counts.
"""
import json
from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user, get_db
from app.models.activity_log import ActivityLog
from app.models.loan import Loan
from app.models.negotiation import NegotiationHistory
from app.models.settlement import SettlementHistory
from app.models.user import User

router = APIRouter(prefix="/history", tags=["History"])


@router.get(
    "/settlements",
    summary="Paginated settlement calculation history",
)
def get_settlements_history(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Return a paginated list of past settlement calculations with totals.
    """
    query = (
        db.query(SettlementHistory)
        .filter(SettlementHistory.user_id == current_user.id)
        .order_by(SettlementHistory.created_at.desc())
    )

    total = query.count()
    records = query.offset(skip).limit(limit).all()

    items = []
    for record in records:
        strategy_data: dict = {}
        if record.strategy_json:
            try:
                strategy_data = json.loads(record.strategy_json)
            except (json.JSONDecodeError, ValueError):
                strategy_data = {}

        items.append(
            {
                "id": record.id,
                "loan_id": record.loan_id,
                "lender_name": strategy_data.get("lender_name", "Unknown"),
                "loan_type": strategy_data.get("loan_type", "Unknown"),
                "outstanding_balance": strategy_data.get("outstanding_balance", 0.0),
                "settlement_percentage": record.settlement_percentage,
                "settlement_amount": record.settlement_amount,
                "savings_amount": record.savings_amount,
                "ai_generated": record.ai_generated,
                "created_at": record.created_at.isoformat(),
            }
        )

    return {"total": total, "skip": skip, "limit": limit, "items": items}


@router.get(
    "/letters",
    summary="Paginated negotiation letter history",
)
def get_letters_history(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Return a paginated list of all generated negotiation letters (content excluded).
    Use the /letters/{id} endpoint to retrieve full content.
    """
    query = (
        db.query(NegotiationHistory)
        .filter(NegotiationHistory.user_id == current_user.id)
        .order_by(NegotiationHistory.created_at.desc())
    )

    total = query.count()
    records = query.offset(skip).limit(limit).all()

    items = []
    for record in records:
        loan_type = None
        if record.loan_id:
            loan = db.query(Loan).filter(Loan.id == record.loan_id).first()
            if loan:
                loan_type = loan.loan_type

        items.append(
            {
                "id": record.id,
                "loan_id": record.loan_id,
                "lender_name": record.lender_name,
                "loan_type": loan_type,
                "ai_generated": record.ai_generated,
                "created_at": record.created_at.isoformat(),
                # Truncate preview to 200 chars
                "preview": record.letter_content[:200] + "..."
                if len(record.letter_content) > 200
                else record.letter_content,
            }
        )

    return {"total": total, "skip": skip, "limit": limit, "items": items}


@router.get(
    "/activity",
    summary="Recent 50 activity log entries",
)
def get_activity_log(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[Dict[str, Any]]:
    """
    Return the 50 most recent activity log entries for the authenticated user.
    """
    logs = (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == current_user.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(50)
        .all()
    )

    return [
        {
            "id": log.id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "metadata": json.loads(log.metadata_json) if log.metadata_json else None,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]


@router.get(
    "/summary",
    summary="Dashboard summary counts",
)
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Return aggregate counts for the user's loans, settlements, and letters.
    Designed for the dashboard summary widget.
    """
    loans = db.query(Loan).filter(Loan.user_id == current_user.id).all()

    total_loans = len(loans)
    active_loans = sum(1 for l in loans if l.loan_status == "active")
    overdue_loans = sum(1 for l in loans if l.loan_status == "overdue")
    defaulted_loans = sum(1 for l in loans if l.loan_status == "defaulted")
    settled_loans = sum(1 for l in loans if l.loan_status == "settled")
    total_outstanding = sum(l.outstanding_balance for l in loans if l.loan_status != "settled")
    total_emi = sum(l.monthly_emi for l in loans if l.loan_status != "settled")

    settlement_count = (
        db.query(SettlementHistory)
        .filter(SettlementHistory.user_id == current_user.id)
        .count()
    )

    letter_count = (
        db.query(NegotiationHistory)
        .filter(NegotiationHistory.user_id == current_user.id)
        .count()
    )

    activity_count = (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == current_user.id)
        .count()
    )

    return {
        "loans": {
            "total": total_loans,
            "active": active_loans,
            "overdue": overdue_loans,
            "defaulted": defaulted_loans,
            "settled": settled_loans,
            "total_outstanding": round(total_outstanding, 2),
            "total_monthly_emi": round(total_emi, 2),
        },
        "settlements_calculated": settlement_count,
        "letters_generated": letter_count,
        "total_activity_events": activity_count,
    }
