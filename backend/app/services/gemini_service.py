"""
FinRelief AI — Google Gemini AI Service.
Wraps the generativeai SDK for settlement advice, letter generation,
and financial recovery planning.  Gracefully falls back to the
deterministic FallbackService when Gemini is unavailable or the API key
is not configured.
"""
import hashlib
import json
import logging
from typing import Any, Dict

import google.generativeai as genai

from app.core.config import settings
from app.services.fallback_service import FallbackService

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Prompt templates
# ─────────────────────────────────────────────────────────────────────────────

_SETTLEMENT_SYSTEM_PROMPT = """
You are a professional Indian debt settlement advisor with 20 years of
experience in personal finance, banking regulations, and debt negotiation.
You provide precise, actionable advice tailored to the borrower's specific
financial situation. Always respond in valid JSON only — no markdown,
no prose outside JSON.

Return this exact structure:
{
  "advice": "<500+ word comprehensive settlement advice paragraph>",
  "strategies": ["<strategy 1>", "<strategy 2>", "<strategy 3>", "<strategy 4>", "<strategy 5>"],
  "priority_order": ["<loan 1 description>", "<loan 2 description>"],
  "recovery_timeline": "<specific timeline with milestones>",
  "warnings": ["<warning 1>", "<warning 2>"]
}
"""

_LETTER_SYSTEM_PROMPT = """
You are an expert financial writer specialising in Indian debt settlement
correspondence.  Generate a complete, professional negotiation letter that
is at least 600 words long.  The letter must be ready to send — no
placeholders, no [INSERT] fields.
Return a JSON object with a single key "letter" containing the full letter text.
No other keys. No markdown.
"""

_RECOVERY_SYSTEM_PROMPT = """
You are a certified Indian financial planner.  Create a structured, detailed
financial recovery plan based on the metrics provided.  Return valid JSON only.

Structure:
{
  "plan_title": "<title>",
  "executive_summary": "<300+ word summary>",
  "phases": [
    {
      "phase": 1,
      "title": "<phase title>",
      "description": "<description>",
      "actions": ["<action 1>", "..."],
      "milestone": "<measurable milestone>"
    }
  ],
  "quick_wins": ["<quick win 1>", "..."],
  "long_term_goals": ["<goal 1>", "..."]
}
"""


class GeminiService:
    """
    Async wrapper around the Google Gemini generative AI API.
    Falls back to FallbackService transparently on any error.
    """

    def __init__(self) -> None:
        self.model: Any = None
        self.available: bool = False

        if settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.model = genai.GenerativeModel("gemini-2.0-flash")
                self.available = True
                logger.info("Gemini AI service initialised successfully.")
            except Exception as exc:
                logger.warning(
                    "Gemini AI initialisation failed — falling back to rule-based engine. "
                    "Error: %s",
                    exc,
                )
                self.available = False
        else:
            logger.info(
                "GEMINI_API_KEY not set. Using deterministic fallback service."
            )

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _hash_prompt(self, prompt: str) -> str:
        """Return SHA-256 hex digest of the prompt string."""
        return hashlib.sha256(prompt.encode("utf-8")).hexdigest()

    def _parse_json_response(self, raw: str) -> dict:
        """
        Attempt to extract a JSON object from Gemini's raw text response.
        Strips markdown code fences if present.
        """
        text = raw.strip()
        if text.startswith("```"):
            # Remove opening fence (```json or ```)
            text = text.split("\n", 1)[-1]
            # Remove closing fence
            if "```" in text:
                text = text.rsplit("```", 1)[0]
        return json.loads(text.strip())

    async def _generate(self, system_prompt: str, user_content: str) -> str:
        """
        Send a combined system + user prompt to Gemini and return the raw text.
        Raises on any API error.
        """
        full_prompt = f"{system_prompt}\n\n{user_content}"
        response = await self.model.generate_content_async(full_prompt)
        return response.text

    # ── Public methods ────────────────────────────────────────────────────────

    async def get_settlement_advice(
        self, financial_data: dict, settlement_data: dict
    ) -> dict:
        """
        Generate AI-powered settlement advice using Gemini.

        Args:
            financial_data:  Output of FinancialEngine.calculate_all_metrics().
            settlement_data: Output of SettlementEngine.calculate_all_settlements().

        Returns:
            dict with keys: advice, strategies, priority_order,
                            recovery_timeline, warnings, ai_generated.
        """
        if not self.available:
            return FallbackService.get_settlement_advice(financial_data, settlement_data)

        user_content = json.dumps(
            {
                "financial_metrics": financial_data,
                "settlement_analysis": settlement_data,
            },
            indent=2,
            default=str,
        )

        try:
            raw = await self._generate(_SETTLEMENT_SYSTEM_PROMPT, user_content)
            result = self._parse_json_response(raw)
            result["ai_generated"] = True
            return result
        except Exception as exc:
            logger.warning(
                "Gemini settlement advice failed (%s). Using fallback.", exc
            )
            return FallbackService.get_settlement_advice(financial_data, settlement_data)

    async def generate_negotiation_letter(
        self,
        loan_data: dict,
        profile_data: dict,
        tone: str = "professional",
        include_income: bool = True,
    ) -> dict:
        """
        Generate a professional lender negotiation letter via Gemini.

        Args:
            loan_data:      Loan details dict.
            profile_data:   Borrower profile dict.
            tone:           'professional' | 'urgent' | 'hardship'
            include_income: Whether to disclose income figures in the letter.

        Returns:
            dict with keys: letter, ai_generated.
        """
        if not self.available:
            result = FallbackService.generate_letter(loan_data, profile_data, tone)
            return {"letter": result["letter"], "ai_generated": False}

        if not include_income:
            # Redact income from profile data sent to Gemini
            profile_data = {k: v for k, v in profile_data.items() if k != "monthly_income"}

        user_content = json.dumps(
            {
                "loan": loan_data,
                "borrower_profile": profile_data,
                "tone": tone,
                "include_income": include_income,
                "instructions": (
                    f"Write a {tone} debt settlement / negotiation letter from the "
                    "borrower to the lender. The letter must be complete, ready to send, "
                    "and at least 600 words. Include: date, salutation, subject line, "
                    "account details table, hardship explanation, specific settlement "
                    "offer with amount (55% of outstanding balance), conditions for "
                    "acceptance (NOC, credit bureau update), and professional closing."
                ),
            },
            indent=2,
            default=str,
        )

        try:
            raw = await self._generate(_LETTER_SYSTEM_PROMPT, user_content)
            result = self._parse_json_response(raw)
            letter_text = result.get("letter", raw)
            return {"letter": letter_text, "ai_generated": True}
        except Exception as exc:
            logger.warning(
                "Gemini letter generation failed (%s). Using fallback.", exc
            )
            fb = FallbackService.generate_letter(loan_data, profile_data, tone)
            return {"letter": fb["letter"], "ai_generated": False}

    async def get_financial_recovery_plan(self, financial_data: dict) -> dict:
        """
        Generate a comprehensive financial recovery plan via Gemini.

        Args:
            financial_data: Dict of all financial metrics.

        Returns:
            dict with plan_title, executive_summary, phases,
                  quick_wins, long_term_goals, ai_generated.
        """
        if not self.available:
            return FallbackService.get_financial_recovery_plan(financial_data)

        user_content = json.dumps(
            {
                "financial_metrics": financial_data,
                "instructions": (
                    "Create a detailed, phased financial recovery plan for an Indian borrower "
                    "based on the metrics above. Include 3 phases, at least 5 quick wins, "
                    "and 5 long-term goals. All amounts should use the ₹ symbol. "
                    "All advice must be specific to the Indian financial system "
                    "(CIBIL, RBI guidelines, Indian bankruptcy laws, etc.)."
                ),
            },
            indent=2,
            default=str,
        )

        try:
            raw = await self._generate(_RECOVERY_SYSTEM_PROMPT, user_content)
            result = self._parse_json_response(raw)
            result["ai_generated"] = True
            return result
        except Exception as exc:
            logger.warning(
                "Gemini recovery plan failed (%s). Using fallback.", exc
            )
            return FallbackService.get_financial_recovery_plan(financial_data)


# Singleton instance — import this throughout the application
gemini_service = GeminiService()
