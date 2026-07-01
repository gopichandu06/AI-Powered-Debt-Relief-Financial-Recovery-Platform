"""
FinRelief AI — Financial Engine.
Pure, stateless calculations for debt metrics and financial health scoring.
"""
from typing import List


class FinancialEngine:
    """
    Collection of static financial calculation methods.
    All methods are side-effect free and depend only on their inputs.
    """

    @staticmethod
    def calculate_debt_to_income_ratio(
        total_monthly_emi: float, monthly_income: float
    ) -> float:
        """
        Compute the debt-to-income (DTI) ratio as a percentage.

        DTI = (total monthly EMI / monthly income) * 100

        Returns 0.0 when monthly_income is zero to avoid division-by-zero.
        """
        if monthly_income <= 0:
            return 0.0
        return round((total_monthly_emi / monthly_income) * 100, 2)

    @staticmethod
    def calculate_monthly_surplus(
        monthly_income: float, monthly_expenses: float, total_emi: float
    ) -> float:
        """
        Calculate the leftover cash each month after expenses and EMIs.

        Surplus = income - expenses - total_emi
        A negative value indicates a cash-flow deficit.
        """
        return round(monthly_income - monthly_expenses - total_emi, 2)

    @staticmethod
    def calculate_disposable_income(
        monthly_income: float, monthly_expenses: float
    ) -> float:
        """
        Income available after covering living expenses (before EMIs).
        """
        return round(monthly_income - monthly_expenses, 2)

    @staticmethod
    def calculate_emi_ratio(total_emi: float, disposable_income: float) -> float:
        """
        EMI burden as a percentage of disposable income.

        Returns 100.0 when disposable_income is zero or negative.
        """
        if disposable_income <= 0:
            return 100.0
        return round((total_emi / disposable_income) * 100, 2)

    @staticmethod
    def calculate_financial_health_score(profile, loans: list) -> int:
        """
        Composite financial health score (0–100, higher is better).

        Scoring deductions:
        ─────────────────────────────────────────
        DTI > 50 %            → −25
        DTI > 40 %            → −15
        DTI > 30 %            → −10
        Credit score < 500    → −25
        Credit score < 600    → −15
        Credit score < 700    → −5
        Each overdue loan     → −10
        Each defaulted loan   → −20
        Monthly surplus < 0   → −15
        Unemployed            → −10
        ─────────────────────────────────────────
        Final score is clamped to [0, 100].
        """
        score = 100

        total_emi = sum(loan.monthly_emi for loan in loans)
        monthly_income = profile.monthly_income if profile else 0.0
        monthly_expenses = profile.monthly_expenses if profile else 0.0
        credit_score = profile.credit_score if profile else 650
        employment_type = profile.employment_type if profile else "salaried"

        # ── DTI deductions ──────────────────────────────────────────────────
        dti = FinancialEngine.calculate_debt_to_income_ratio(total_emi, monthly_income)
        if dti > 50:
            score -= 25
        elif dti > 40:
            score -= 15
        elif dti > 30:
            score -= 10

        # ── Credit score deductions ─────────────────────────────────────────
        if credit_score < 500:
            score -= 25
        elif credit_score < 600:
            score -= 15
        elif credit_score < 700:
            score -= 5

        # ── Loan status deductions ──────────────────────────────────────────
        for loan in loans:
            if loan.loan_status == "defaulted":
                score -= 20
            elif loan.loan_status == "overdue":
                score -= 10

        # ── Surplus deduction ────────────────────────────────────────────────
        surplus = FinancialEngine.calculate_monthly_surplus(
            monthly_income, monthly_expenses, total_emi
        )
        if surplus < 0:
            score -= 15

        # ── Employment deduction ─────────────────────────────────────────────
        if employment_type == "unemployed":
            score -= 10

        return max(0, min(100, score))

    @staticmethod
    def get_debt_stress_level(health_score: int) -> str:
        """
        Map a health score to a human-readable stress level.

        ─────────────────────────
        80–100  → Low
        60–79   → Moderate
        40–59   → High
        0–39    → Critical
        ─────────────────────────
        """
        if health_score >= 80:
            return "Low"
        if health_score >= 60:
            return "Moderate"
        if health_score >= 40:
            return "High"
        return "Critical"

    @staticmethod
    def get_risk_category(health_score: int, dti: float) -> str:
        """
        Derive a risk category from the health score and DTI.

        Categories (in descending severity):
        Critical / High Risk / Elevated / Moderate / Conservative
        """
        if health_score < 30 or dti > 70:
            return "Critical"
        if health_score < 45 or dti > 55:
            return "High Risk"
        if health_score < 60 or dti > 40:
            return "Elevated"
        if health_score < 75 or dti > 25:
            return "Moderate"
        return "Conservative"

    @staticmethod
    def calculate_all_metrics(profile, loans: list) -> dict:
        """
        Compute and return every financial metric in a single dict.

        Keys returned:
            dti_ratio, emi_ratio, monthly_surplus, disposable_income,
            health_score, debt_stress_level, risk_category,
            total_outstanding, total_monthly_emi, total_loans,
            overdue_loans, defaulted_loans
        """
        total_emi = sum(loan.monthly_emi for loan in loans)
        total_outstanding = sum(loan.outstanding_balance for loan in loans)

        monthly_income = profile.monthly_income if profile else 0.0
        monthly_expenses = profile.monthly_expenses if profile else 0.0

        dti = FinancialEngine.calculate_debt_to_income_ratio(total_emi, monthly_income)
        disposable = FinancialEngine.calculate_disposable_income(
            monthly_income, monthly_expenses
        )
        surplus = FinancialEngine.calculate_monthly_surplus(
            monthly_income, monthly_expenses, total_emi
        )
        emi_ratio = FinancialEngine.calculate_emi_ratio(total_emi, disposable)
        health_score = FinancialEngine.calculate_financial_health_score(profile, loans)
        stress_level = FinancialEngine.get_debt_stress_level(health_score)
        risk_category = FinancialEngine.get_risk_category(health_score, dti)

        overdue_loans = sum(1 for loan in loans if loan.loan_status == "overdue")
        defaulted_loans = sum(1 for loan in loans if loan.loan_status == "defaulted")

        return {
            "dti_ratio": dti,
            "emi_ratio": emi_ratio,
            "monthly_surplus": surplus,
            "disposable_income": disposable,
            "health_score": health_score,
            "debt_stress_level": stress_level,
            "risk_category": risk_category,
            "total_outstanding": round(total_outstanding, 2),
            "total_monthly_emi": round(total_emi, 2),
            "total_loans": len(loans),
            "overdue_loans": overdue_loans,
            "defaulted_loans": defaulted_loans,
        }
