from typing import Any, Dict, Optional

from google import genai
from google.genai import types

from app.config import settings


class LLMService:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not configured.")

        self.model = settings.GEMINI_MODEL.strip()

        if not self.model:
            raise RuntimeError("GEMINI_MODEL is not configured.")

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    async def generate(
        self,
        message: str,
        language: str = "en",
        context: Optional[str] = None
    ) -> str:

        system_prompt = self._build_system_prompt(
            language=language,
            context=context
        )

        prompt = f"""
{system_prompt}

Citizen's question:
{message}
"""

        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=2048,
            )
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        return response.text.strip()

    async def generate_response(
        self,
        message: str,
        language: str = "en",
        context: Optional[str] = None,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:

        response_text = await self.generate(
            message=message,
            language=language,
            context=context
        )

        return {
            "response": response_text,
            "language": language,
            "conversation_id": conversation_id,
            "sources": [],
        }

    def _build_system_prompt(
        self,
        language: str,
        context: Optional[str] = None
    ) -> str:

        prompt = f"""
You are CivicAssist AI, a citizen assistance platform.

Your role is to help citizens understand:
- Government schemes and services
- Eligibility requirements
- Required documents
- Application procedures
- General legal information
- Citizen service options

Answer in the requested language: {language}

Important rules:

1. Be clear, simple, and practical.
2. Do not invent government scheme rules, legal provisions, eligibility requirements, or documents.
3. When authoritative information is supplied in the context, base your answer on that information.
4. If authoritative information is not available in the supplied context, clearly state that verification may be required.
5. For legal questions, provide general information and encourage professional/legal-aid assistance when appropriate.
6. Never claim that you have completed an official application unless the system actually confirms it.
7. Do not ask the citizen to share passwords, OTPs, CAPTCHA answers, or other sensitive authentication information.
8. When explaining a process, present the next practical steps clearly.
"""

        if context:
            prompt += """

Authoritative context supplied by CivicAssist:
--------------------
""" + context.strip() + """
--------------------
"""

        return prompt


_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    global _service

    if _service is None:
        _service = LLMService()

    return _service


async def generate_response(
    message: str,
    language: str = "en",
    context: Optional[str] = None,
    user_id: Optional[str] = None,
    conversation_id: Optional[str] = None
) -> Dict[str, Any]:

    service = get_llm_service()

    return await service.generate_response(
        message=message,
        language=language,
        context=context,
        user_id=user_id,
        conversation_id=conversation_id
    )