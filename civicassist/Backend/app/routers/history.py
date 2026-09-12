from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(
    prefix="/api/history",
    tags=["History"],
)


class HistoryMessage(BaseModel):
    role: str
    content: str
    language: Optional[str] = None
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConversationHistory(BaseModel):
    conversation_id: str
    user_id: Optional[str] = None
    title: Optional[str] = None
    language: Optional[str] = None
    messages: List[HistoryMessage] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class HistoryResponse(BaseModel):
    conversations: List[ConversationHistory] = Field(default_factory=list)


class NewConversationRequest(BaseModel):
    user_id: Optional[str] = None
    language: str = Field(default="en", min_length=2, max_length=10)
    title: Optional[str] = Field(default=None, max_length=200)


class NewConversationResponse(BaseModel):
    conversation_id: str
    user_id: Optional[str] = None
    language: str
    title: Optional[str] = None
    status: str


def get_history_service():
    try:
        from app.services.history_service import HistoryService
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="History service is not available.",
        )

    try:
        return HistoryService()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to initialize history service: {str(exc)}",
        )


def normalize_response(
    result: Any,
    response_model: type[BaseModel],
) -> BaseModel:
    if isinstance(result, response_model):
        return result

    if not isinstance(result, dict):
        raise HTTPException(
            status_code=500,
            detail="Invalid response received from the history service.",
        )

    try:
        return response_model.model_validate(result)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid history service response: {str(exc)}",
        )


@router.get("", response_model=HistoryResponse)
async def get_history(
    user_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
) -> HistoryResponse:
    service = get_history_service()

    try:
        result = await service.get_history(
            user_id=user_id,
            conversation_id=conversation_id,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve conversation history: {str(exc)}",
        )

    return normalize_response(result, HistoryResponse)


@router.post("/new", response_model=NewConversationResponse)
async def create_new_conversation(
    request: NewConversationRequest,
) -> NewConversationResponse:
    language = request.language.strip().lower()

    if not language:
        raise HTTPException(
            status_code=400,
            detail="Language cannot be empty.",
        )

    title = request.title.strip() if request.title else None

    service = get_history_service()

    try:
        result = await service.create_conversation(
            user_id=request.user_id,
            language=language,
            title=title,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to create conversation: {str(exc)}",
        )

    return normalize_response(result, NewConversationResponse)


@router.get("/health/status")
async def history_health():
    return {
        "status": "ok",
        "service": "history",
    }