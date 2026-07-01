"""
FinRelief AI — Financial Engine unit tests.
Tests: DTI edge cases, health score calculation, stress levels,
       risk categories, settlement percentage clamping.
"""
import pytest
from unittest.mock import MagicMock

from app.services.financial_engine import FinancialEngine
from app.services.settlement_engine import SettlementEngine


# ─────────────────────────────────────────────────────────────────────────────
# Helpers — mock loan and profile
# ─────────────────────────────────────────────────────────────────────────────


def make_loan(
    outstanding_balance: float = 100_000.0,
    monthly_emi: float = 5_000.0,
    interest_rate: float = 12.0,
    loan_type: str = "personal",
    loan_status: str = "active",
    overdue_months: int = 0,
) -> MagicMock:
    loan = MagicMock()
    loan.outstanding_balance = outstanding_balance
    loan.monthly_emi = monthly_emi
    loan.interest_rate = interest_rate
    loan.loan_type = loan_type
    loan.loan_status = loan_status
    loan.overdue_months = overdue_months
    return loan


def make_profile(
    monthly_income: float = 50_000.0,
    monthly_expenses: float = 25_000.0,
    credit_score: int = 700,
    employment_type: str = "salaried",
    dependents: int = 0,
) -> MagicMock:
    profile = MagicMock()
    profile.monthly_income = monthly_income
    profile.monthly_expenses = monthly_expenses
    profile.credit_score = credit_score
    profile.employment_type = employment_type
    profile.dependents = dependents
    return profile


# ─────────────────────────────────────────────────────────────────────────────
# DTI calculation
# ─────────────────────────────────────────────────────────────────────────────


class TestDebtToIncomeRatio:
    def test_normal_dti(self) -> None:
        """DTI of 5,000 EMI / 50,000 income = 10 %."""
        result = FinancialEngine.calculate_debt_to_income_ratio(5_000.0, 50_000.0)
        assert result == pytest.approx(10.0)

    def test_zero_income_returns_zero(self) -> None:
        """Division by zero should be handled: return 0.0."""
        result = FinancialEngine.calculate_debt_to_income_ratio(10_000.0, 0.0)
        assert result == 0.0

    def test_zero_emi_returns_zero(self) -> None:
        """No EMI obligations means DTI = 0."""
        result = FinancialEngine.calculate_debt_to_income_ratio(0.0, 50_000.0)
        assert result == 0.0

    def test_dti_above_50_percent(self) -> None:
        """High-debt scenario: 30,000 EMI on 50,000 income = 60 %."""
        result = FinancialEngine.calculate_debt_to_income_ratio(30_000.0, 50_000.0)
        assert result == pytest.approx(60.0)

    def test_dti_exactly_50_percent(self) -> None:
        """Boundary: 25,000 / 50,000 = exactly 50 %."""
        result = FinancialEngine.calculate_debt_to_income_ratio(25_000.0, 50_000.0)
        assert result == pytest.approx(50.0)

    def test_negative_income_returns_zero(self) -> None:
        """Negative income (invalid input) should be treated as zero."""
        result = FinancialEngine.calculate_debt_to_income_ratio(5_000.0, -1.0)
        assert result == 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Monthly surplus / disposable income
# ─────────────────────────────────────────────────────────────────────────────


class TestSurplusAndDisposable:
    def test_positive_surplus(self) -> None:
        result = FinancialEngine.calculate_monthly_surplus(50_000, 20_000, 10_000)
        assert result == pytest.approx(20_000.0)

    def test_negative_surplus(self) -> None:
        result = FinancialEngine.calculate_monthly_surplus(30_000, 20_000, 15_000)
        assert result == pytest.approx(-5_000.0)

    def test_disposable_income(self) -> None:
        result = FinancialEngine.calculate_disposable_income(50_000, 20_000)
        assert result == pytest.approx(30_000.0)

    def test_emi_ratio_normal(self) -> None:
        result = FinancialEngine.calculate_emi_ratio(10_000, 30_000)
        assert result == pytest.approx(33.33, rel=1e-2)

    def test_emi_ratio_zero_disposable(self) -> None:
        """When disposable income is zero, EMI ratio should be capped at 100 %."""
        result = FinancialEngine.calculate_emi_ratio(5_000, 0)
        assert result == 100.0

    def test_emi_ratio_negative_disposable(self) -> None:
        """Negative disposable income should also cap EMI ratio at 100 %."""
        result = FinancialEngine.calculate_emi_ratio(5_000, -1_000)
        assert result == 100.0


# ─────────────────────────────────────────────────────────────────────────────
# Financial health score
# ─────────────────────────────────────────────────────────────────────────────


class TestFinancialHealthScore:
    def test_healthy_profile_scores_high(self) -> None:
        """A borrower with good credit, low DTI, and no overdue loans should score 80+."""
        profile = make_profile(monthly_income=100_000, monthly_expenses=30_000, credit_score=780)
        loans = [make_loan(monthly_emi=10_000)]  # DTI = 10 %
        score = FinancialEngine.calculate_financial_health_score(profile, loans)
        assert score >= 80

    def test_defaulted_loans_lower_score_significantly(self) -> None:
        """Each defaulted loan deducts 20 points."""
        profile = make_profile()
        loans = [
            make_loan(loan_status="defaulted"),
            make_loan(loan_status="defaulted"),
        ]
        score = FinancialEngine.calculate_financial_health_score(profile, loans)
        # Should be notably below 100
        assert score <= 60

    def test_overdue_loans_lower_score(self) -> None:
        """Each overdue loan deducts 10 points."""
        profile = make_profile()
        loans = [make_loan(loan_status="overdue")]
        score = FinancialEngine.calculate_financial_health_score(profile, loans)
        # At a minimum, 10 points deducted
        assert score <= 90

    def test_low_credit_score_deducts_points(self) -> None:
        """Credit score below 500 deducts 25 points."""
        profile = make_profile(credit_score=480)
        loans = []
        score = FinancialEngine.calculate_financial_health_score(profile, loans)
        assert score <= 75

    def test_unemployed_deducts_10_points(self) -> None:
        """Unemployed employment type should deduct 10 points."""
        profile_employed = make_profile(employment_type="salaried")
        profile_unemployed = make_profile(employment_type="unemployed")
        loans = []
        employed_score = FinancialEngine.calculate_financial_health_score(
            profile_employed, loans
        )
        unemployed_score = FinancialEngine.calculate_financial_health_score(
            profile_unemployed, loans
        )
        assert employed_score - unemployed_score >= 10

    def test_negative_surplus_deducts_15_points(self) -> None:
        """When expenses + EMIs exceed income, 15 points should be deducted."""
        profile_surplus = make_profile(monthly_income=50_000, monthly_expenses=20_000)
        profile_deficit = make_profile(monthly_income=30_000, monthly_expenses=40_000)
        loans = [make_loan(monthly_emi=0)]
        surplus_score = FinancialEngine.calculate_financial_health_score(
            profile_surplus, loans
        )
        deficit_score = FinancialEngine.calculate_financial_health_score(
            profile_deficit, loans
        )
        assert surplus_score - deficit_score >= 15

    def test_score_never_exceeds_100(self) -> None:
        """Score must be clamped at 100 for ideal conditions."""
        profile = make_profile(
            monthly_income=200_000,
            monthly_expenses=10_000,
            credit_score=850,
            employment_type="salaried",
        )
        loans = []
        score = FinancialEngine.calculate_financial_health_score(profile, loans)
        assert score <= 100

    def test_score_never_below_zero(self) -> None:
        """Score must be clamped at 0 for catastrophic conditions."""
        profile = make_profile(
            monthly_income=5_000,
            monthly_expenses=60_000,
            credit_score=300,
            employment_type="unemployed",
        )
        loans = [
            make_loan(monthly_emi=10_000, loan_status="defaulted"),
            make_loan(monthly_emi=8_000, loan_status="defaulted"),
            make_loan(monthly_emi=5_000, loan_status="defaulted"),
        ]
        score = FinancialEngine.calculate_financial_health_score(profile, loans)
        assert score >= 0

    def test_no_loans_no_profile_returns_100(self) -> None:
        """No loans and a None profile should not crash; returns a non-negative score."""
        score = FinancialEngine.calculate_financial_health_score(None, [])
        assert 0 <= score <= 100


# ─────────────────────────────────────────────────────────────────────────────
# Debt stress levels
# ─────────────────────────────────────────────────────────────────────────────


class TestDebtStressLevel:
    @pytest.mark.parametrize(
        "score, expected",
        [
            (100, "Low"),
            (80, "Low"),
            (79, "Moderate"),
            (60, "Moderate"),
            (59, "High"),
            (40, "High"),
            (39, "Critical"),
            (0, "Critical"),
        ],
    )
    def test_stress_level_boundaries(self, score: int, expected: str) -> None:
        result = FinancialEngine.get_debt_stress_level(score)
        assert result == expected, f"Score {score} should be '{expected}', got '{result}'"


# ─────────────────────────────────────────────────────────────────────────────
# Risk categories
# ─────────────────────────────────────────────────────────────────────────────


class TestRiskCategory:
    def test_conservative(self) -> None:
        assert FinancialEngine.get_risk_category(90, 10) == "Conservative"

    def test_moderate(self) -> None:
        assert FinancialEngine.get_risk_category(70, 30) == "Moderate"

    def test_elevated(self) -> None:
        assert FinancialEngine.get_risk_category(55, 42) == "Elevated"

    def test_high_risk(self) -> None:
        assert FinancialEngine.get_risk_category(40, 60) == "High Risk"

    def test_critical_by_score(self) -> None:
        assert FinancialEngine.get_risk_category(20, 10) == "Critical"

    def test_critical_by_dti(self) -> None:
        assert FinancialEngine.get_risk_category(60, 75) == "Critical"


# ─────────────────────────────────────────────────────────────────────────────
# Calculate all metrics
# ─────────────────────────────────────────────────────────────────────────────


class TestCalculateAllMetrics:
    def test_returns_all_required_keys(self) -> None:
        profile = make_profile()
        loans = [make_loan()]
        metrics = FinancialEngine.calculate_all_metrics(profile, loans)

        required_keys = [
            "dti_ratio",
            "emi_ratio",
            "monthly_surplus",
            "disposable_income",
            "health_score",
            "debt_stress_level",
            "risk_category",
            "total_outstanding",
            "total_monthly_emi",
            "total_loans",
            "overdue_loans",
            "defaulted_loans",
        ]
        for key in required_keys:
            assert key in metrics, f"Missing key: {key}"

    def test_total_loans_count(self) -> None:
        profile = make_profile()
        loans = [make_loan(), make_loan(), make_loan()]
        metrics = FinancialEngine.calculate_all_metrics(profile, loans)
        assert metrics["total_loans"] == 3

    def test_overdue_count(self) -> None:
        profile = make_profile()
        loans = [
            make_loan(loan_status="active"),
            make_loan(loan_status="overdue"),
            make_loan(loan_status="overdue"),
        ]
        metrics = FinancialEngine.calculate_all_metrics(profile, loans)
        assert metrics["overdue_loans"] == 2
        assert metrics["defaulted_loans"] == 0


# ─────────────────────────────────────────────────────────────────────────────
# Settlement percentage clamping
# ─────────────────────────────────────────────────────────────────────────────


class TestSettlementPercentageClamping:
    def test_minimum_clamp_at_25(self) -> None:
        """Settlement percentage should never go below 25 %."""
        loan = make_loan(
            loan_status="active",
            overdue_months=0,
            loan_type="home",
            interest_rate=7.0,
        )
        profile = make_profile(credit_score=800, employment_type="salaried")
        pct = SettlementEngine.calculate_settlement_percentage(loan, profile)
        assert pct >= 25.0

    def test_maximum_clamp_at_85(self) -> None:
        """Settlement percentage should never exceed 85 %."""
        loan = make_loan(
            loan_status="defaulted",
            overdue_months=30,
            loan_type="credit_card",
            interest_rate=36.0,
        )
        profile = make_profile(
            credit_score=400, employment_type="unemployed"
        )
        pct = SettlementEngine.calculate_settlement_percentage(loan, profile)
        assert pct <= 85.0

    def test_defaulted_loan_higher_than_active(self) -> None:
        """Defaulted loans should yield higher settlement % than active ones."""
        profile = make_profile()
        active_loan = make_loan(loan_status="active", overdue_months=0)
        defaulted_loan = make_loan(loan_status="defaulted", overdue_months=6)

        active_pct = SettlementEngine.calculate_settlement_percentage(active_loan, profile)
        defaulted_pct = SettlementEngine.calculate_settlement_percentage(
            defaulted_loan, profile
        )
        assert defaulted_pct > active_pct

    def test_credit_card_higher_than_home_loan(self) -> None:
        """Credit card loans have higher settlement bonus than home loans."""
        profile = make_profile()
        cc_loan = make_loan(loan_type="credit_card", loan_status="active", overdue_months=0)
        home_loan = make_loan(loan_type="home", loan_status="active", overdue_months=0)

        cc_pct = SettlementEngine.calculate_settlement_percentage(cc_loan, profile)
        home_pct = SettlementEngine.calculate_settlement_percentage(home_loan, profile)
        assert cc_pct > home_pct

    def test_overdue_duration_increases_percentage(self) -> None:
        """More overdue months should increase the settlement percentage."""
        profile = make_profile()
        short_overdue = make_loan(loan_status="overdue", overdue_months=2)
        long_overdue = make_loan(loan_status="overdue", overdue_months=10)

        short_pct = SettlementEngine.calculate_settlement_percentage(short_overdue, profile)
        long_pct = SettlementEngine.calculate_settlement_percentage(long_overdue, profile)
        assert long_pct >= short_pct


# ─────────────────────────────────────────────────────────────────────────────
# Settlement priority
# ─────────────────────────────────────────────────────────────────────────────


class TestLoanPriority:
    def test_defaulted_is_priority_1(self) -> None:
        loan = make_loan(loan_status="defaulted")
        assert SettlementEngine.get_loan_priority(loan) == 1

    def test_overdue_high_interest_is_priority_2(self) -> None:
        loan = make_loan(loan_status="overdue", interest_rate=24.0)
        assert SettlementEngine.get_loan_priority(loan) == 2

    def test_overdue_low_interest_is_priority_3(self) -> None:
        loan = make_loan(loan_status="overdue", interest_rate=12.0)
        assert SettlementEngine.get_loan_priority(loan) == 3

    def test_active_high_interest_is_priority_4(self) -> None:
        loan = make_loan(loan_status="active", interest_rate=20.0)
        assert SettlementEngine.get_loan_priority(loan) == 4

    def test_active_low_interest_is_priority_5(self) -> None:
        loan = make_loan(loan_status="active", interest_rate=10.0)
        assert SettlementEngine.get_loan_priority(loan) == 5
