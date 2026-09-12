from typing import Optional

from google import genai
from google.genai import types

from app.config import settings


class QueryClassifier:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not configured.")

        self.model = settings.GEMINI_MODEL.strip()

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    async def classify(self, message: str) -> str:

        prompt = f"""
Classify the citizen's question into exactly ONE category.

Categories:

general
scheme
legal

Definitions:

GENERAL:
Normal knowledge, education, casual, technical, mathematical,
or non-government/non-legal questions.

SCHEME:
Questions about government schemes, government benefits,
subsidies, pensions, welfare programs, eligibility for schemes,
government services, or applying for a government scheme/service.

LEGAL:
Questions about laws, legal rights, disputes, eviction,
property disputes, consumer issues, police/legal procedures,
legal notices, courts, or legal assistance.

Return ONLY one word:
general
scheme
legal

Question:
{message}
"""

        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                max_output_tokens=5,
            )
        )

        result = (response.text or "").strip().lower()

        if result not in {"general", "scheme", "legal"}:
            return self._fallback_classification(message)

        return result

    def _fallback_classification(self, message: str) -> str:

        text = message.lower()

        legal_keywords = [
            "law",
            "legal",
            "lawyer",
            "court",
            "police",
            "eviction",
            "tenant",
            "landlord",
            "rights",
            "legal notice",
            "case",
            "fir",
            "consumer complaint",
            "property dispute",
        ]

        scheme_keywords = [
            "scheme",
            "yojana",
            "subsidy",
            "pension",
            "benefit",
            "government benefit",
            "eligibility",
            "ration",
            "kisan",
            "pm kisan",
            "government service",
            "apply for",
        ]

        if any(keyword in text for keyword in legal_keywords):
            return "legal"

        if any(keyword in text for keyword in scheme_keywords):
            return "scheme"

        return "general"


_classifier: Optional[QueryClassifier] = None


def get_query_classifier() -> QueryClassifier:
    global _classifier

    if _classifier is None:
        _classifier = QueryClassifier()

    return _classifier