from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SchemeBase(BaseModel):
    scheme_id: str = Field(..., min_length=1, max_length=200)
    name: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    category: Optional[str] = None
    state: Optional[str] = None


class SchemeCreate(SchemeBase):
    eligibility: List[Dict[str, Any]] = Field(default_factory=list)
    benefits: List[Dict[str, Any]] = Field(default_factory=list)
    required_documents: List[Dict[str, Any]] = Field(default_factory=list)
    application_process: List[Dict[str, Any]] = Field(default_factory=list)
    official_source: Optional[str] = None
    official_portal: Optional[str] = None


class SchemeUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = None
    category: Optional[str] = None
    state: Optional[str] = None
    eligibility: Optional[List[Dict[str, Any]]] = None
    benefits: Optional[List[Dict[str, Any]]] = None
    required_documents: Optional[List[Dict[str, Any]]] = None
    application_process: Optional[List[Dict[str, Any]]] = None
    official_source: Optional[str] = None
    official_portal: Optional[str] = None


class SchemeResponse(SchemeBase):
    model_config = ConfigDict(from_attributes=True)

    eligibility: List[Dict[str, Any]] = Field(default_factory=list)
    benefits: List[Dict[str, Any]] = Field(default_factory=list)
    required_documents: List[Dict[str, Any]] = Field(default_factory=list)
    application_process: List[Dict[str, Any]] = Field(default_factory=list)
    official_source: Optional[str] = None
    official_portal: Optional[str] = None


class SchemeSearchRequest(BaseModel):
    query: Optional[str] = Field(default=None, max_length=1000)
    category: Optional[str] = Field(default=None, max_length=200)
    state: Optional[str] = Field(default=None, max_length=100)
    language: str = Field(default="en", min_length=2, max_length=20)
    limit: int = Field(default=20, ge=1, le=100)


class SchemeSearchResponse(BaseModel):
    schemes: List[SchemeResponse] = Field(default_factory=list)
    total: int = Field(default=0, ge=0)


class EligibilityRequest(BaseModel):
    user_data: Dict[str, Any] = Field(default_factory=dict)
    language: str = Field(default="en", min_length=2, max_length=20)


class EligibilityResponse(BaseModel):
    scheme_id: str
    eligible: Optional[bool] = None
    reasons: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    required_documents: List[Dict[str, Any]] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
    