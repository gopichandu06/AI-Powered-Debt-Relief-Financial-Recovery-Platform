"""
FinRelief AI — Settlement Engine.
Deterministic algorithm for computing optimal debt settlement percentages
and per-loan strategies without requiring an AI API call.
"""
from typing import List


class SettlementEngine:
    """
    Rule-based settlement calculator.
    Higher settlement percentage = greater discount the borrower can negotiate.
    """

    # Base negotiating advantage by loan type
    LOAN_TYPE_BONUS: dict = {
        "credit_card": 15,
        "personal": 10,
        "business": 8,
        "auto": 5,
        "student": 3,
        "home": 0,
    }

    @staticmethod
    def calculate_settlement_percentage(loan, profile) -> float:
        """
        Calculate the discount percentage the borrower can realistically negotiate.

        Algorithm:
          base = 40 %
          + min(overdue_months * 2, 20)          — time in distress
          + LOAN_TYPE_BONUS[loan_type]            — asset security of loan
          + 15 if defaulted                       — lender eager to recover anything
          + 8  if overdue (but not defaulted)
          + 10 if credit_score < 600
          + 5  if credit_score < 700
          - 5  if credit_score > 750              — borrower still has leverage
          - 5  if employment == salaried          — perceived ability to repay

        Final value is clamped to [25, 85].
        """
        base = 40.0

        # Overdue duration bonus (capped at 20 %)
        base += min(loan.overdue_months * 2, 20)

        # Loan type structural advantage
        loan_type = loan.loan_type.lower() if loan.loan_type else "personal"
        base += SettlementEngine.LOAN_TYPE_BONUS.get(loan_type, 5)

        # Status bonuses
        if loan.loan_status == "defaulted":
            base += 15
        elif loan.loan_status == "overdue":
            base += 8

        # Credit score modifiers
        credit_score = profile.credit_score if profile else 650
        if credit_score < 600:
            base += 10
        elif credit_score < 700:
            base += 5

        if credit_score > 750:
            base -= 5

        # Employment modifier
        employment_type = profile.employment_type if profile else "salaried"
        if employment_type == "salaried":
            base -= 5

        # Clamp
        return round(max(25.0, min(85.0, base)), 2)

    @staticmethod
    def get_loan_priority(loan) -> int:
        """
        Return a priority rank (1 = most urgent to resolve).

        Priority ordering:
          1 — Defaulted loans
          2 — Overdue with high interest (≥ 20 %)
          3 — Overdue with moderate interest
          4 — Active with high interest (≥ 18 %)
          5 — Active with lower interest
        """
        if loan.loan_status == "defaulted":
            return 1
        if loan.loan_status == "overdue":
            return 2 if loan.interest_rate >= 20 else 3
        if loan.loan_status == "active":
            return 4 if loan.interest_rate >= 18 else 5
        return 5  # settled or unknown

    @staticmethod
    def calculate_settlement_for_loan(loan, profile) -> dict:
        """
        Return a per-loan settlement analysis dictionary.

        Returns:
            {
                loan_id, loan_type, lender_name, outstanding_balance,
                settlement_percentage, settlement_amount, savings_amount,
                priority, strategy, loan_status, overdue_months
            }
        """
        pct = SettlementEngine.calculate_settlement_percentage(loan, profile)
        settlement_amount = round(loan.outstanding_balance * (1 - pct / 100), 2)
        savings_amount = round(loan.outstanding_balance - settlement_amount, 2)
        priority = SettlementEngine.get_loan_priority(loan)

        # Build a specific action strategy for this loan
        if loan.loan_status == "defaulted":
            strategy = (
                f"Contact {loan.lender_name} immediately. Your loan is in default. "
                f"Offer a lump-sum settlement of ₹{settlement_amount:,.0f} "
                f"(saving ₹{savings_amount:,.0f}) to close the account and stop "
                "further penalty accrual."
            )
        elif loan.loan_status == "overdue":
            strategy = (
                f"Call {loan.lender_name}'s collections team and request a settlement "
                f"discussion. Propose ₹{settlement_amount:,.0f} as a one-time full "
                f"and final payment. Stress any financial hardship to strengthen your "
                "negotiating position."
            )
        elif loan.interest_rate >= 18:
            strategy = (
                f"This {loan.loan_type.replace('_', ' ')} loan carries a high interest "
                f"rate of {loan.interest_rate}%. Prioritise settlement or prepayment "
                f"at ₹{settlement_amount:,.0f} to reduce long-term interest burden."
            )
        else:
            strategy = (
                f"Maintain regular EMIs for now. If surplus cash becomes available, "
                f"consider prepaying or negotiating a one-time settlement of "
                f"₹{settlement_amount:,.0f} with {loan.lender_name}."
            )

        return {
            "loan_id": loan.id,
            "loan_type": loan.loan_type,
            "lender_name": loan.lender_name,
            "outstanding_balance": loan.outstanding_balance,
            "settlement_percentage": pct,
            "settlement_amount": settlement_amount,
            "savings_amount": savings_amount,
            "priority": priority,
            "strategy": strategy,
            "loan_status": loan.loan_status,
            "overdue_months": loan.overdue_months,
        }

    @staticmethod
    def get_payment_strategy(financial_metrics: dict, loans: list) -> str:
        """
        Recommend a high-level debt repayment strategy.

        Returns one of:
          'Settlement First' — when loans are defaulted/overdue
          'Debt Avalanche'   — when the borrower has surplus and high-interest debt
          'Debt Snowball'    — when motivation/quick-wins are more important
        """
        has_critical = any(
            loan.loan_status in ("defaulted", "overdue") for loan in loans
        )
        if has_critical:
            return "Settlement First"

        surplus = financial_metrics.get("monthly_surplus", 0)
        if surplus > 0:
            # Avalanche: attack highest interest rate first
            high_interest = any(loan.interest_rate >= 18 for loan in loans)
            if high_interest:
                return "Debt Avalanche"
            return "Debt Snowball"

        return "Debt Avalanche"  # default to cost-minimising strategy

    @staticmethod
    def calculate_all_settlements(
        profile, loans: list, financial_metrics: dict
    ) -> dict:
        """
        Run settlement calculations for every loan and compile the full analysis.

        Returns a complete dict ready to be serialised as the API response body.
        The loans list is sorted by priority (most urgent first).
        """
        # Filter out already settled loans
        active_loans = [loan for loan in loans if loan.loan_status != "settled"]

        loan_settlements = [
            SettlementEngine.calculate_settlement_for_loan(loan, profile)
            for loan in active_loans
        ]

        # Sort by priority (ascending = most urgent first)
        loan_settlements.sort(key=lambda x: x["priority"])

        total_outstanding = sum(s["outstanding_balance"] for s in loan_settlements)
        total_settlement = sum(s["settlement_amount"] for s in loan_settlements)
        total_savings = sum(s["savings_amount"] for s in loan_settlements)

        health_score = financial_metrics.get("health_score", 50)
        stress_level = financial_metrics.get("debt_stress_level", "Moderate")
        risk_category = financial_metrics.get("risk_category", "Moderate")
        payment_strategy = SettlementEngine.get_payment_strategy(
            financial_metrics, active_loans
        )

        # Build overall strategy narrative
        if stress_level == "Critical":
            overall_strategy = (
                "Your financial situation is critical. Immediate action is required. "
                "Contact all lenders with defaulted or overdue accounts TODAY. "
                "Consider engaging a certified debt counsellor. Prioritise stopping "
                "penalty accrual on defaulted accounts through negotiated settlement."
            )
        elif stress_level == "High":
            overall_strategy = (
                "Your debt stress is high. Focus on settling the most distressed loans "
                "first using the one-time settlement amounts shown below. "
                "Avoid taking on any new credit until your financial health improves."
            )
        elif stress_level == "Moderate":
            overall_strategy = (
                "Your debt situation is manageable but needs attention. "
                f"Follow the {payment_strategy} approach: focus additional payments on "
                "the highest-priority loans while maintaining minimum payments on others. "
                "Build a 3-month emergency fund before aggressively prepaying."
            )
        else:
            overall_strategy = (
                "Your financial health is good. Continue maintaining timely payments "
                "to protect your credit score. Use any surplus to prepay the "
                "highest-interest loan first (Debt Avalanche method) to save on "
                "long-term interest costs."
            )

        reasoning = (
            f"Analysis based on {len(active_loans)} active loan(s), "
            f"financial health score of {health_score}/100, "
            f"debt stress level: {stress_level}, "
            f"DTI ratio: {financial_metrics.get('dti_ratio', 0):.1f}%. "
            f"Recommended strategy: {payment_strategy}. "
            f"Settlement percentages are calculated using overdue duration, "
            "loan type, credit score, and employment status."
        )

        return {
            "financial_health_score": health_score,
            "debt_stress_level": stress_level,
            "risk_category": risk_category,
            "total_outstanding": round(total_outstanding, 2),
            "total_settlement_amount": round(total_settlement, 2),
            "total_savings": round(total_savings, 2),
            "total_loans": len(active_loans),
            "loans": loan_settlements,
            "overall_strategy": overall_strategy,
            "payment_strategy": payment_strategy,
            "reasoning": reasoning,
            "ai_generated": False,
        }
