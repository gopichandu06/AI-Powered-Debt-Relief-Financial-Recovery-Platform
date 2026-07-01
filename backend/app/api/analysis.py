"""
FinRelief AI — Financial Analysis API router.
Endpoints: financial-health metrics, debt summary breakdown.
"""
from collections import defaultdict
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user, get_db
from app.models.loan import Loan
from app.models.profile import Profile
from app.models.user import User
from app.services.financial_engine import FinancialEngine

router = APIRouter(prefix="/analysis", tags=["Financial Analysis"])


def _load_user_data(db: Session, user_id: str):
    """Load the user's profile and all active loans from the database."""
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    loans = db.query(Loan).filter(Loan.user_id == user_id).all()
    return profile, loans


@router.get(
    "/financial-health",
    summary="Compute complete financial health metrics",
)
def get_financial_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Calculate and return all financial health metrics for the authenticated user.

    Requires the user to have a profile and at least one loan on file.
    Returns comprehensive metrics including DTI, health score, surplus, and risk category.
    """
    profile, loans = _load_user_data(db, current_user.id)

    metrics = FinancialEngine.calculate_all_metrics(profile, loans)

    # Enrich with profile data for frontend convenience
    metrics["monthly_income"] = profile.monthly_income if profile else 0.0
    metrics["monthly_expenses"] = profile.monthly_expenses if profile else 0.0
    metrics["credit_score"] = profile.credit_score if profile else 650
    metrics["employment_type"] = profile.employment_type if profile else "salaried"
    metrics["has_profile"] = profile is not None

    return metrics


@router.get(
    "/debt-summary",
    summary="Get debt breakdown by loan type and status",
)
def get_debt_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Return a categorised breakdown of the user's loans by type and status.

    Useful for rendering pie charts and summary cards on the dashboard.
    """
    profile, loans = _load_user_data(db, current_user.id)

    # Breakdown by loan type
    by_type: Dict[str, Dict] = defaultdict(
        lambda: {"count": 0, "total_outstanding": 0.0, "total_emi": 0.0}
    )
    # Breakdown by status
    by_status: Dict[str, Dict] = defaultdict(
        lambda: {"count": 0, "total_outstanding": 0.0}
    )

    for loan in loans:
        lt = loan.loan_type
        by_type[lt]["count"] += 1
        by_type[lt]["total_outstanding"] += loan.outstanding_balance
        by_type[lt]["total_emi"] += loan.monthly_emi

        ls = loan.loan_status
        by_status[ls]["count"] += 1
        by_status[ls]["total_outstanding"] += loan.outstanding_balance

    # Round all floats
    for data in by_type.values():
        data["total_outstanding"] = round(data["total_outstanding"], 2)
        data["total_emi"] = round(data["total_emi"], 2)

    for data in by_status.values():
        data["total_outstanding"] = round(data["total_outstanding"], 2)

    # Top 3 loans by outstanding balance
    top_loans = sorted(loans, key=lambda l: l.outstanding_balance, reverse=True)[:3]
    top_loans_data = [
        {
            "id": loan.id,
            "lender_name": loan.lender_name,
            "loan_type": loan.loan_type,
            "outstanding_balance": loan.outstanding_balance,
            "interest_rate": loan.interest_rate,
            "loan_status": loan.loan_status,
        }
        for loan in top_loans
    ]

    total_outstanding = sum(loan.outstanding_balance for loan in loans)
    total_emi = sum(loan.monthly_emi for loan in loans)

    return {
        "total_loans": len(loans),
        "total_outstanding": round(total_outstanding, 2),
        "total_monthly_emi": round(total_emi, 2),
        "by_type": dict(by_type),
        "by_status": dict(by_status),
        "top_loans_by_balance": top_loans_data,
        "has_overdue": any(loan.loan_status == "overdue" for loan in loans),
        "has_defaulted": any(loan.loan_status == "defaulted" for loan in loans),
    }
