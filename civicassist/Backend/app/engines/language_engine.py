from __future__ import annotations

from typing import Any, Dict, Optional

from app.services.llm_service import get_llm_service


class LanguageEngine:
    """
    Handles language detection and language-aware processing
    for CivicAssist AI.
    """

    def __init__(self) -> None:
        self.llm_service = get_llm_service()

    async def process_language(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None,
    ) -> Dict[str, Any]:
        text = text.strip()
        target_language = target_language.strip().lower()

        if not text:
            raise ValueError("Text cannot be empty.")

        if not target_language:
            raise ValueError("Target language cannot be empty.")

        detected_language = source_language.strip().lower() if source_language else None

        if not detected_language:
            detected_language = await self.detect_language(text)

        if detected_language == target_language:
            translated_text = text
        else:
            prompt = (
                "Translate the following citizen-facing text accurately into "
                f"{target_language}. Preserve the meaning, legal terminology, "
                "government scheme names, names, numbers, dates, and document "
                "requirements. Do not add information.\n\n"
                f"Text:\n{text}"
            )

            translated_text = await self.llm_service.generate(
                message=prompt,
                language=target_language,
            )

        return {
            "text": translated_text,
            "source_language": detected_language,
            "target_language": target_language,
        }

    async def detect_language(self, text: str) -> str:
        text = text.strip()

        if not text:
            raise ValueError("Text cannot be empty.")

        prompt = (
            "Identify the primary language of the following citizen message. "
            "Return only the standard language code, such as en, ta, hi, ml, "
            "te, kn, or bn. Do not return any explanation.\n\n"
            f"Message:\n{text}"
        )

        detected_language = await self.llm_service.generate(
            message=prompt,
            language="en",
        )

        detected_language = detected_language.strip().lower()

        if not detected_language:
            raise ValueError("Language detection returned an empty result.")

        return detected_language


_language_engine: Optional[LanguageEngine] = None


def get_language_engine() -> LanguageEngine:
    global _language_engine

    if _language_engine is None:
        _language_engine = LanguageEngine()

    return _language_engine


async def process_language(
    text: str,
    target_language: str,
    source_language: Optional[str] = None,
) -> Dict[str, Any]:
    engine = get_language_engine()

    return await engine.process_language(
        text=text,
        target_language=target_language,
        source_language=source_language,
    )


async def detect_language(text: str) -> str:
    engine = get_language_engine()

    return await engine.detect_language(text)