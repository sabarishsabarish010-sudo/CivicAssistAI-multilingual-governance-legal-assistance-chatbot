from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field


router = APIRouter(
    prefix="/api/applications",
    tags=["Applications"],
)


class ApplicationStartRequest(BaseModel):
    user_id: Optional[str] = None
    scheme_id: Optional[str] = None
    service_id: Optional[str] = None
    language: str = Field(default="en", min_length=2, max_length=10)
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
    application_id: str
    status: str
    scheme_id: Optional[str] = None
    service_id: Optional[str] = None
    user_id: Optional[str] = None
    language: Optional[str] = None
    required_documents: List[Dict[str, Any]] = Field(default_factory=list)
    submitted_documents: List[Dict[str, Any]] = Field(default_factory=list)
    form_data: Dict[str, Any] = Field(default_factory=dict)
    portal_url: Optional[str] = None
    next_step: Optional[str] = None
    message: Optional[str] = None


class ApplicationConfirmRequest(BaseModel):
    user_id: Optional[str] = None
    confirmation: bool


class ApplicationConfirmResponse(BaseModel):
    application_id: str
    status: str
    message: str
    next_step: Optional[str] = None
    portal_url: Optional[str] = None


def get_application_engine():
    try:
        from app.engines.application_engine import ApplicationEngine
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Application engine is not available.",
        )

    try:
        return ApplicationEngine()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to initialize application engine: {str(exc)}",
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
            detail="Invalid response received from the application engine.",
        )

    try:
        return response_model.model_validate(result)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid application engine response: {str(exc)}",
        )


@router.post("/start", response_model=ApplicationStartResponse)
async def start_application(
    request: ApplicationStartRequest,
) -> ApplicationStartResponse:
    if not request.scheme_id and not request.service_id:
        raise HTTPException(
            status_code=400,
            detail="Either scheme_id or service_id is required.",
        )

    if request.scheme_id and request.service_id:
        raise HTTPException(
            status_code=400,
            detail="Provide either scheme_id or service_id, not both.",
        )

    language = request.language.strip().lower()

    if not language:
        raise HTTPException(
            status_code=400,
            detail="Language cannot be empty.",
        )

    engine = get_application_engine()

    try:
        result = await engine.start_application(
            user_id=request.user_id,
            scheme_id=request.scheme_id,
            service_id=request.service_id,
            language=language,
            user_data=request.user_data,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to start application: {str(exc)}",
        )

    return normalize_response(result, ApplicationStartResponse)


@router.post(
    "/{application_id}/documents",
    response_model=ApplicationDocumentResponse,
)
async def upload_application_document(
    application_id: str,
    file: UploadFile = File(...),
    user_id: Optional[str] = None,
) -> ApplicationDocumentResponse:
    application_id = application_id.strip()

    if not application_id:
        raise HTTPException(
            status_code=400,
            detail="Application ID cannot be empty.",
        )

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="A document file is required.",
        )

    engine = get_application_engine()

    try:
        result = await engine.process_application_document(
            application_id=application_id,
            file=file,
            user_id=user_id,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to process application document: {str(exc)}",
        )

    return normalize_response(result, ApplicationDocumentResponse)


@router.get(
    "/{application_id}",
    response_model=ApplicationResponse,
)
async def get_application(
    application_id: str,
    user_id: Optional[str] = None,
) -> ApplicationResponse:
    application_id = application_id.strip()

    if not application_id:
        raise HTTPException(
            status_code=400,
            detail="Application ID cannot be empty.",
        )

    engine = get_application_engine()

    try:
        result = await engine.get_application(
            application_id=application_id,
            user_id=user_id,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve application: {str(exc)}",
        )

    return normalize_response(result, ApplicationResponse)


@router.post(
    "/{application_id}/confirm",
    response_model=ApplicationConfirmResponse,
)
async def confirm_application(
    application_id: str,
    request: ApplicationConfirmRequest,
) -> ApplicationConfirmResponse:
    application_id = application_id.strip()

    if not application_id:
        raise HTTPException(
            status_code=400,
            detail="Application ID cannot be empty.",
        )

    engine = get_application_engine()

    try:
        result = await engine.confirm_application(
            application_id=application_id,
            user_id=request.user_id,
            confirmation=request.confirmation,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to confirm application: {str(exc)}",
        )

    return normalize_response(result, ApplicationConfirmResponse)


@router.get("/health/status")
async def application_health():
    return {
        "status": "ok",
        "service": "applications",
    }