from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(
    prefix="/api/language",
    tags=["Language"],
)


class LanguageRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=20000)
    source_language: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=10,
    )
    target_language: str = Field(
        ...,
        min_length=2,
        max_length=10,
    )


class LanguageResponse(BaseModel):
    text: str
    source_language: Optional[str] = None
    target_language: str
    detected_language: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


def get_language_engine():
    try:
        from app.engines.language_engine import LanguageEngine
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Language engine is not available.",
        )

    try:
        return LanguageEngine()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to initialize language engine: {str(exc)}",
        )


def normalize_response(result: Any) -> LanguageResponse:
    if isinstance(result, LanguageResponse):
        return result

    if not isinstance(result, dict):
        raise HTTPException(
            status_code=500,
            detail="Invalid response received from the language engine.",
        )

    try:
        return LanguageResponse.model_validate(result)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid language engine response: {str(exc)}",
        )


@router.post("", response_model=LanguageResponse)
async def process_language(
    request: LanguageRequest,
) -> LanguageResponse:
    text = request.text.strip()
    target_language = request.target_language.strip().lower()
    source_language = (
        request.source_language.strip().lower()
        if request.source_language
        else None
    )

    if not text:
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty.",
        )

    if not target_language:
        raise HTTPException(
            status_code=400,
            detail="Target language cannot be empty.",
        )

    engine = get_language_engine()

    try:
        result = await engine.process_language(
            text=text,
            source_language=source_language,
            target_language=target_language,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to process language request: {str(exc)}",
        )

    return normalize_response(result)


@router.post("/detect", response_model=LanguageResponse)
async def detect_language(
    request: LanguageRequest,
) -> LanguageResponse:
    text = request.text.strip()

    if not text:
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty.",
        )

    engine = get_language_engine()

    try:
        result = await engine.detect_language(text=text)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to detect language: {str(exc)}",
        )

    return normalize_response(result)


@router.get("/health/status")
async def language_health():
    return {
        "status": "ok",
        "service": "language",
    }