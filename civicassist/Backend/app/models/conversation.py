from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ConversationMessage(BaseModel):
    role: str = Field(..., min_length=1, max_length=30)
    content: str = Field(..., min_length=1)
    language: Optional[str] = Field(default=None, max_length=20)
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConversationCreate(BaseModel):
    user_id: Optional[str] = Field(default=None, max_length=100)
    language: str = Field(default="en", min_length=2, max_length=20)
    title: Optional[str] = Field(default=None, max_length=200)


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    conversation_id: str
    user_id: Optional[str] = None
    title: Optional[str] = None
    language: str
    messages: List[ConversationMessage] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ConversationHistoryResponse(BaseModel):
    conversations: List[ConversationResponse] = Field(default_factory=list)
