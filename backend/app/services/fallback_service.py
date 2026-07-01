"""
FinRelief AI — Deterministic Fallback Service.
Provides rule-based AI-quality responses when Gemini is unavailable.
All output is meaningful, actionable, and contextually accurate.
"""
from datetime import date
from typing import Any, Dict


class FallbackService:
    """
    Rule-based alternative to Gemini AI.
    Produces professional, context-aware output using financial heuristics.
    """

    # ─────────────────────────────────────────────────────────────────────────
    # Settlement Advice
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def get_settlement_advice(
        financial_data: dict, settlement_data: dict
    ) -> dict:
        """
        Generate deterministic, meaningful settlement advice.

        Returns the same structure expected from Gemini:
            advice, strategies, priority_order, recovery_timeline, warnings
        """
        health_score: int = financial_data.get("health_score", 50)
        stress_level: str = financial_data.get("debt_stress_level", "Moderate")
        dti: float = financial_data.get("dti_ratio", 0.0)
        surplus: float = financial_data.get("monthly_surplus", 0.0)
        total_outstanding: float = settlement_data.get("total_outstanding", 0.0)
        total_settlement: float = settlement_data.get("total_settlement_amount", 0.0)
        total_savings: float = settlement_data.get("total_savings", 0.0)
        total_loans: int = settlement_data.get("total_loans", 0)
        overdue_loans: int = financial_data.get("overdue_loans", 0)
        defaulted_loans: int = financial_data.get("defaulted_loans", 0)

        # ── Build contextual advice paragraph ─────────────────────────────────
        if stress_level == "Critical":
            advice = (
                f"Your financial health score of {health_score}/100 places you in the "
                f"Critical category. With a debt-to-income ratio of {dti:.1f}% and "
                f"{defaulted_loans} defaulted loan(s), you are facing serious financial "
                f"distress. However, your total outstanding balance of "
                f"₹{total_outstanding:,.0f} can potentially be settled for just "
                f"₹{total_settlement:,.0f}, saving you ₹{total_savings:,.0f}. "
                "Act immediately: lenders of defaulted accounts are most receptive to "
                "negotiated settlements right now. Every additional month of default "
                "increases legal risk and reduces your negotiating power. Engage a "
                "certified debt counsellor if needed — many non-profit credit "
                "counselling agencies offer free initial consultations."
            )
        elif stress_level == "High":
            advice = (
                f"With a financial health score of {health_score}/100 and a "
                f"debt-to-income ratio of {dti:.1f}%, your debt burden is High. "
                f"You have {overdue_loans} overdue loan(s) that need immediate attention. "
                f"By settling strategically, you could reduce your total obligation from "
                f"₹{total_outstanding:,.0f} to ₹{total_settlement:,.0f}, "
                f"freeing up ₹{total_savings:,.0f} in the process. "
                "Focus your available cash on the highest-priority loans first. "
                "Contact lenders proactively — explaining your hardship situation "
                "strengthens your negotiating position significantly."
            )
        elif stress_level == "Moderate":
            advice = (
                f"Your financial health score of {health_score}/100 indicates a Moderate "
                f"stress level. Your DTI of {dti:.1f}% is above the recommended 30% "
                "threshold. While your situation is manageable, taking action now "
                "prevents it from deteriorating further. "
                f"Across your {total_loans} loan(s), strategic settlement could save "
                f"₹{total_savings:,.0f}. Consider using any annual bonuses, tax refunds, "
                "or additional income streams to make lump-sum prepayments on your "
                "highest-interest obligations."
            )
        else:
            advice = (
                f"Your financial health score of {health_score}/100 indicates a Low "
                "stress level — well done for managing your obligations responsibly. "
                f"Your DTI of {dti:.1f}% is within the healthy range. "
                "Continue your disciplined repayment approach. "
                "To further optimise your finances, consider the Debt Avalanche method: "
                "direct any surplus income to the highest-interest loan while maintaining "
                "minimum payments on all others. This minimises total interest paid."
            )

        # ── Strategies list ───────────────────────────────────────────────────
        strategies = []

        if defaulted_loans > 0:
            strategies.append(
                "Immediate Priority — Default Resolution: Contact lenders of defaulted "
                "accounts this week. Offer the settlement amounts calculated above as a "
                "one-time full-and-final payment. Get any agreement in writing before "
                "transferring funds."
            )

        if overdue_loans > 0:
            strategies.append(
                "Short-Term — Overdue Account Recovery: Call the collections department "
                "of each overdue lender. Propose a catch-up plan or one-time settlement. "
                "Most lenders prefer partial recovery over a complete write-off."
            )

        if surplus > 0:
            strategies.append(
                f"Medium-Term — Surplus Deployment: Your monthly surplus of "
                f"₹{surplus:,.0f} should be directed to the highest-interest active loan "
                "as an additional principal payment each month. This reduces your "
                "outstanding balance faster and saves significant interest."
            )
        else:
            strategies.append(
                "Expense Reduction: Your current expenses exceed your income surplus. "
                "Identify at least 3 discretionary expenses (subscriptions, dining out, "
                "entertainment) you can temporarily reduce to create a positive monthly "
                "surplus for debt repayment."
            )

        strategies.append(
            "Credit Score Improvement: Pay all future bills on time, keep credit card "
            "utilisation below 30%, and avoid applying for new credit for the next "
            "12 months. A higher credit score directly improves your future "
            "negotiating leverage."
        )

        strategies.append(
            "Emergency Fund: Once your most critical debt is resolved, build a "
            "3-month emergency fund equal to your monthly expenses. This prevents "
            "future financial shocks from forcing you back into debt distress."
        )

        # ── Priority order ────────────────────────────────────────────────────
        loans_list: list = settlement_data.get("loans", [])
        priority_order = [
            f"[Priority {loan.get('priority', idx + 1)}] {loan.get('lender_name', 'Unknown')} "
            f"— {loan.get('loan_type', '').replace('_', ' ').title()} "
            f"(₹{loan.get('outstanding_balance', 0):,.0f} outstanding, "
            f"settle at ₹{loan.get('settlement_amount', 0):,.0f})"
            for idx, loan in enumerate(sorted(loans_list, key=lambda x: x.get("priority", 5)))
        ]

        if not priority_order:
            priority_order = ["No active loans requiring settlement."]

        # ── Recovery timeline ─────────────────────────────────────────────────
        if stress_level == "Critical":
            timeline = (
                "Immediate action required. Aim to resolve defaulted accounts within "
                "30–60 days. Full debt stabilisation typically takes 12–24 months with "
                "consistent effort."
            )
        elif stress_level == "High":
            timeline = (
                "Begin outreach to overdue lenders within 2 weeks. "
                "Expect 6–18 months to significantly reduce your debt burden "
                "through settlements and structured repayment."
            )
        elif stress_level == "Moderate":
            timeline = (
                "With consistent effort, you can reduce your DTI below 30% within "
                "12–18 months. Focus on one loan at a time for the most effective progress."
            )
        else:
            timeline = (
                "You are on a healthy trajectory. At your current repayment pace, "
                "you should be debt-free within your existing loan tenures. "
                "Prepayments can accelerate this by 20–30%."
            )

        # ── Warnings ─────────────────────────────────────────────────────────
        warnings = []
        if defaulted_loans > 0:
            warnings.append(
                "⚠️ Defaulted loans may result in legal action, asset seizure, or "
                "wage garnishment. Resolve these immediately."
            )
        if dti > 50:
            warnings.append(
                "⚠️ Your DTI exceeds 50%. Most lenders consider this a high-risk "
                "threshold. Avoid all new credit applications until this ratio improves."
            )
        if surplus < 0:
            warnings.append(
                "⚠️ Your monthly expenses and EMIs exceed your income. "
                "You are operating at a deficit — address this by reducing discretionary "
                "spending or increasing income immediately."
            )
        if not warnings:
            warnings.append(
                "✅ No critical warnings. Continue your disciplined financial management."
            )

        return {
            "advice": advice,
            "strategies": strategies,
            "priority_order": priority_order,
            "recovery_timeline": timeline,
            "warnings": warnings,
            "ai_generated": False,
        }

    # ─────────────────────────────────────────────────────────────────────────
    # Negotiation Letter
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def generate_letter(
        loan_data: dict, profile_data: dict, tone: str = "professional"
    ) -> dict:
        """
        Generate a full, professional debt negotiation letter (500+ words).

        Args:
            loan_data:    Dict with loan details (lender_name, loan_type,
                          outstanding_balance, overdue_months, loan_status, etc.)
            profile_data: Dict with borrower details (full_name, city, state,
                          monthly_income, employment_type, credit_score, etc.)
            tone:         'professional' | 'urgent' | 'hardship'

        Returns:
            { letter: str, ai_generated: False }
        """
        today = date.today().strftime("%d %B %Y")
        borrower_name: str = profile_data.get("full_name", "The Borrower")
        city: str = profile_data.get("city", "")
        state: str = profile_data.get("state", "")
        location_str = f"{city}, {state}".strip(", ") if city or state else "India"

        lender_name: str = loan_data.get("lender_name", "The Lender")
        loan_type: str = loan_data.get("loan_type", "loan").replace("_", " ").title()
        outstanding: float = loan_data.get("outstanding_balance", 0.0)
        overdue_months: int = loan_data.get("overdue_months", 0)
        loan_status: str = loan_data.get("loan_status", "active")
        interest_rate: float = loan_data.get("interest_rate", 0.0)

        # Settlement offer = 55% of outstanding (conservative ask)
        settlement_offer = round(outstanding * 0.55, 2)

        # ── Hardship paragraph tailored to employment ─────────────────────────
        employment_type: str = profile_data.get("employment_type", "salaried")
        monthly_income: float = profile_data.get("monthly_income", 0.0)

        if employment_type == "unemployed":
            hardship_paragraph = (
                "I am currently unemployed and have been actively seeking new employment "
                "for the past several months. Despite my best efforts, securing a position "
                "with sufficient income to meet my financial obligations in full has proven "
                "challenging in the current economic environment. My unemployment has "
                "severely impacted my ability to service this loan, and I am genuinely "
                "concerned about the mounting interest and penalties."
            )
        elif employment_type == "self_employed":
            hardship_paragraph = (
                "As a self-employed individual, my income is inherently variable and has "
                "been significantly impacted by challenging market conditions over the past "
                "year. My business revenue has declined substantially, making it impossible "
                "to continue meeting the full loan obligations as originally agreed. "
                "I have taken every possible step to reduce my operating expenses and "
                "explore alternative revenue streams, but the financial pressure remains severe."
            )
        elif employment_type == "retired":
            hardship_paragraph = (
                "As a retired individual living on a fixed pension, my income is limited "
                "and has not kept pace with rising living costs. Unexpected medical expenses "
                "and family obligations have further strained my fixed monthly budget, making "
                "it increasingly difficult to maintain regular loan repayments. "
                "I sincerely regret that I am unable to service this loan as originally agreed."
            )
        else:  # salaried
            hardship_paragraph = (
                "I am currently employed; however, my household has experienced significant "
                "financial hardship due to a combination of medical expenses, reduced "
                "working hours, and increased cost of living pressures. My monthly income "
                f"of approximately ₹{monthly_income:,.0f} is now fully committed to "
                "essential living expenses, leaving me unable to service this loan "
                "obligation in the manner originally agreed upon."
            )

        # ── Tone-specific opener ──────────────────────────────────────────────
        if tone == "urgent":
            opener = (
                f"I am writing to you with great urgency regarding my {loan_type} account "
                f"with {lender_name}. My account has been overdue for {overdue_months} "
                "month(s), and I am acutely aware of the serious consequences this situation "
                "carries for both parties. I am reaching out today in the hope of finding "
                "an immediate, mutually acceptable resolution before this matter escalates further."
            )
        elif tone == "hardship":
            opener = (
                f"I am writing to you in a spirit of complete transparency and humility "
                f"regarding my {loan_type} account held with {lender_name}. "
                "I find myself in a situation of genuine financial hardship and am sincerely "
                "requesting your compassion and cooperation in helping me resolve this "
                "outstanding obligation in a manner that is realistic given my current circumstances."
            )
        else:  # professional
            opener = (
                f"I am writing to formally request a One-Time Settlement (OTS) arrangement "
                f"for my {loan_type} account currently maintained with {lender_name}. "
                "I believe a mutually beneficial settlement can be reached that allows me "
                "to close this account while providing your organisation with a meaningful "
                "recovery of the outstanding balance."
            )

        # ── Status-specific context ───────────────────────────────────────────
        if loan_status in ("defaulted", "overdue"):
            status_context = (
                f"I acknowledge that my account has been in {loan_status} status for "
                f"approximately {overdue_months} month(s). I deeply regret this situation "
                "and take full responsibility for the distress it may have caused. "
                "I want to assure you that my intention has never been to avoid my "
                "obligations, and I am committed to resolving this matter as swiftly "
                "and fairly as possible."
            )
        else:
            status_context = (
                "While I have made every effort to maintain regular payments, my changed "
                "financial circumstances have made it increasingly difficult to continue "
                "the current repayment schedule. I am proactively approaching you now, "
                "before the situation deteriorates further, to propose a responsible resolution."
            )

        # ── Build the complete letter ─────────────────────────────────────────
        letter = f"""{today}

To,
The Settlement / Collections Department
{lender_name}

Sub: Request for One-Time Settlement (OTS) — {loan_type} Loan
      Outstanding Balance: ₹{outstanding:,.2f}

Dear Sir / Madam,

{opener}

ACCOUNT DETAILS
───────────────────────────────────────────────
Lender Name        : {lender_name}
Loan Type          : {loan_type}
Outstanding Balance: ₹{outstanding:,.2f}
Interest Rate      : {interest_rate:.2f}% per annum
Account Status     : {loan_status.capitalize()}
Overdue Since      : {overdue_months} month(s)
───────────────────────────────────────────────

STATEMENT OF FINANCIAL HARDSHIP

{hardship_paragraph}

{status_context}

SETTLEMENT PROPOSAL

After careful review of my financial position, I would like to formally propose a One-Time Settlement (OTS) as follows:

  Settlement Amount Offered : ₹{settlement_offer:,.2f}
  (Approximately 55% of the current outstanding balance of ₹{outstanding:,.2f})

I am in a position to arrange this lump-sum payment within 15–21 days of receiving your written confirmation and acceptance of this settlement offer. This offer represents a genuine attempt to resolve the outstanding obligation in good faith and within my current financial capacity.

I understand that by accepting this settlement, {lender_name} would be agreeing to:
  1. Accept ₹{settlement_offer:,.2f} as full and final settlement of the outstanding dues.
  2. Issue a No Objection Certificate (NOC) and a Debt Settlement Letter upon receipt of payment.
  3. Report the account as "Settled" (or equivalent) to all relevant Credit Information Bureaus (CIBIL, Experian, Equifax, CRIF) within 30 days of payment.
  4. Waive all remaining penalties, interest charges, and legal recovery costs associated with this account.

WHY AN OTS IS IN BOTH OUR INTERESTS

I wish to be transparent: my financial situation makes it impossible for me to repay the full outstanding balance in the near term. A protracted recovery process — including legal proceedings — would likely cost {lender_name} considerably more in administrative and legal expenses than the proposed settlement amount, while further reducing the likelihood of any meaningful recovery. A negotiated settlement offers a faster, more cost-effective resolution for both parties.

I am genuinely committed to honouring this settlement offer and am prepared to sign any required documentation and provide supporting financial documents upon request.

NEXT STEPS

I respectfully request that you:
  1. Review this settlement proposal at the earliest opportunity.
  2. Provide written confirmation of your acceptance or a counter-proposal within 10 business days.
  3. Share the relevant bank account details for remittance once the OTS is agreed upon.

I can be reached at any time to discuss this proposal further and am happy to provide any additional documentation to support my request.

I sincerely hope that {lender_name} will consider this proposal favourably. I remain committed to resolving this matter respectfully and responsibly.

Thanking you in anticipation of your cooperation.

Yours sincerely,

{borrower_name}
{location_str}
Date: {today}

Enclosures (available upon request):
  - Latest salary slips / income proof
  - Bank statements (last 3 months)
  - Supporting financial hardship documentation
"""

        return {
            "letter": letter,
            "ai_generated": False,
        }

    # ─────────────────────────────────────────────────────────────────────────
    # Financial Recovery Plan
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def get_financial_recovery_plan(financial_data: dict) -> dict:
        """
        Generate a structured, actionable financial recovery plan.

        Returns:
            {
                plan_title, executive_summary, phases (list),
                quick_wins, long_term_goals, ai_generated
            }
        """
        health_score: int = financial_data.get("health_score", 50)
        stress_level: str = financial_data.get("debt_stress_level", "Moderate")
        dti: float = financial_data.get("dti_ratio", 0.0)
        surplus: float = financial_data.get("monthly_surplus", 0.0)
        total_outstanding: float = financial_data.get("total_outstanding", 0.0)
        overdue_loans: int = financial_data.get("overdue_loans", 0)
        defaulted_loans: int = financial_data.get("defaulted_loans", 0)

        plan_title = f"FinRelief AI — Personal Debt Recovery Plan ({stress_level} Stress)"

        executive_summary = (
            f"Based on your current financial health score of {health_score}/100 "
            f"and a debt-to-income ratio of {dti:.1f}%, this plan outlines a structured "
            f"path to financial recovery. Your total outstanding debt of "
            f"₹{total_outstanding:,.0f} is manageable with disciplined execution of the "
            "phases outlined below."
        )

        # ── Phases ────────────────────────────────────────────────────────────
        phases = []

        # Phase 1 — Always: Stabilise
        phase1_actions = [
            "Create a detailed monthly budget using the 50/30/20 rule (needs/wants/savings).",
            "List all income sources and every expense — leave nothing out.",
            "Cancel all unnecessary subscriptions and reduce discretionary spending by 20%.",
            "Contact all lenders to inform them of your situation and intent to resolve.",
        ]
        if defaulted_loans > 0:
            phase1_actions.insert(
                2,
                f"Immediately contact lenders for {defaulted_loans} defaulted loan(s) "
                "to halt further penalty accrual.",
            )
        phases.append(
            {
                "phase": 1,
                "title": "Stabilisation (Weeks 1–4)",
                "description": (
                    "Stop the financial bleeding. Get a complete picture of your "
                    "obligations and commit to no new borrowing."
                ),
                "actions": phase1_actions,
                "milestone": "Complete budget drafted; all lenders contacted.",
            }
        )

        # Phase 2 — Debt Attack
        if stress_level in ("Critical", "High"):
            phase2_desc = (
                "Focus 100% of available cash on settling the most distressed accounts. "
                "Negotiate aggressively using the settlement amounts provided."
            )
            phase2_actions = [
                "Negotiate OTS (One-Time Settlement) for all defaulted accounts.",
                "Prioritise overdue accounts to prevent them from defaulting.",
                "Explore liquidating non-essential assets to fund settlements.",
                "Consider a debt consolidation loan if credit score allows.",
            ]
        else:
            phase2_desc = (
                "Direct surplus income to systematic debt reduction using the "
                "Debt Avalanche method (highest interest rate first)."
            )
            phase2_actions = [
                "Identify the loan with the highest interest rate.",
                f"Direct ₹{max(surplus, 1000):,.0f}/month as additional payment to that loan.",
                "Once the top-rate loan is cleared, redirect its EMI to the next one.",
                "Avoid any new credit purchases during this phase.",
            ]
        phases.append(
            {
                "phase": 2,
                "title": "Debt Reduction (Months 2–12)",
                "description": phase2_desc,
                "actions": phase2_actions,
                "milestone": "At least one loan fully settled or 25% principal reduction achieved.",
            }
        )

        # Phase 3 — Build resilience
        phases.append(
            {
                "phase": 3,
                "title": "Financial Resilience (Months 6–18)",
                "description": (
                    "Build the safety net and credit score that prevent future crises."
                ),
                "actions": [
                    "Build an emergency fund equal to 3 months of living expenses.",
                    "Pay all bills on time — set up auto-debit for every EMI and utility.",
                    "Keep credit card utilisation below 30% at all times.",
                    "Review your credit report quarterly (free on CIBIL/Experian) and "
                    "dispute any inaccuracies.",
                    "Once debts are under control, begin a SIP (Systematic Investment Plan) "
                    "— even ₹500/month builds long-term wealth.",
                ],
                "milestone": "Emergency fund established; credit score improving.",
            }
        )

        # ── Quick wins ────────────────────────────────────────────────────────
        quick_wins = [
            "Cancel 2–3 unused subscriptions today — saves ₹500–₹2,000/month instantly.",
            "Switch to a cheaper mobile/internet plan.",
            "Cook at home 5 days a week instead of ordering delivery.",
            "Sell unused electronics, furniture, or clothing online.",
            "Negotiate a lower interest rate with your primary bank — existing customers "
            "often get 0.5–1% reduction just by asking.",
        ]

        # ── Long-term goals ───────────────────────────────────────────────────
        long_term_goals = [
            "Achieve a CIBIL score of 750+ within 18–24 months.",
            "Reduce DTI below 30% to qualify for better loan terms in the future.",
            f"Clear total outstanding debt of ₹{total_outstanding:,.0f} within "
            f"{'12–18 months' if stress_level in ('Critical', 'High') else '24–36 months'}.",
            "Build investments equal to 6 months of salary as a financial buffer.",
            "Achieve financial health score of 80+ (currently {}).".format(health_score),
        ]

        return {
            "plan_title": plan_title,
            "executive_summary": executive_summary,
            "phases": phases,
            "quick_wins": quick_wins,
            "long_term_goals": long_term_goals,
            "ai_generated": False,
        }
