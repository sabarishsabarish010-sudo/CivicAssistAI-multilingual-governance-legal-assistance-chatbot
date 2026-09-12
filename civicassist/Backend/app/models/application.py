from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ApplicationStartRequest(BaseModel):
    user_id: Optional[str] = Field(default=None, max_length=100)
    scheme_id: Optional[str] = Field(default=None, max_length=200)
    service_id: Optional[str] = Field(default=None, max_length=200)
    language: str = Field(default="en", min_length=2, max_length=20)
    user_data: Dict[str, Any] = Field(default_factory=dict)


class ApplicationStartResponse(BaseModel):
    application_id: str
    status: str
    scheme_id: Optional[str] = None
    service_id: Optional[str] = None
    required_documents: List[Dict[str, Any]] = Field(default_factory=list)
    next_step: Optional[str] = None


class ApplicationDocumentResponse(BaseModel):
    application_id: str
    document_id: str
    status: str
    message: Optional[str] = None


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    application_id: str
    user_id: Optional[str] = None
    scheme_id: Optional[str] = None
    service_id: Optional[str] = None
    status: str
    language: Optional[str] = None
    user_data: Dict[str, Any] = Field(default_factory=dict)
    form_data: Dict[str, Any] = Field(default_factory=dict)
    required_documents: List[Dict[str, Any]] = Field(default_factory=list)
    submitted_documents: List[Dict[str, Any]] = Field(default_factory=list)
    portal_url: Optional[str] = None
    next_step: Optional[str] = None
    message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ApplicationConfirmRequest(BaseModel):
    user_id: Optional[str] = Field(default=None, max_length=100)
    confirmation: bool


class ApplicationConfirmResponse(BaseModel):
    application_id: str
    status: str
    message: str
    next_step: Optional[str] = None
    portal_url: Optional[str] = None