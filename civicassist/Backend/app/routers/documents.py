from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"],
)


# ============================================================
# Response Models
# ============================================================

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    content_type: Optional[str] = None
    size: int
    status: str
    extracted_text: Optional[str] = None
    extracted_data: Dict[str, Any] = Field(default_factory=dict)
    message: str


class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    content_type: Optional[str] = None
    size: int
    status: str
    extracted_text: Optional[str] = None
    extracted_data: Dict[str, Any] = Field(default_factory=dict)


# ============================================================
# Service Loader
# ============================================================

def get_document_service():
    """
    Load the document-processing service.

    The document service is responsible for:

    - secure file storage
    - file validation
    - PDF/image processing
    - OCR
    - text extraction
    - structured data extraction
    - document metadata
    """

    try:
        from app.services.document_service import DocumentService

    except ImportError as exc:
        raise HTTPException(
            status_code=500,
            detail="Document service is not available.",
        ) from exc

    try:
        return DocumentService()

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to initialize document service: {str(exc)}"
            ),
        ) from exc


# ============================================================
# POST /api/documents/upload
# ============================================================

@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
)
async def upload_document(
    file: UploadFile = File(...),
    user_id: Optional[str] = None,
    application_id: Optional[str] = None,
) -> DocumentUploadResponse:
    """
    Upload a citizen document.

    Supported document processing is handled by the document
    service.

    The router does not perform OCR or extraction itself.
    """

    if file is None:
        raise HTTPException(
            status_code=400,
            detail="No document was provided.",
        )

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Document filename is missing.",
        )

    filename = file.filename.strip()

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Document filename cannot be empty.",
        )

    document_service = get_document_service()

    try:
        result = await document_service.process_upload(
            file=file,
            user_id=user_id,
            application_id=application_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to process document: {str(exc)}"
            ),
        ) from exc

    if not isinstance(result, dict):
        raise HTTPException(
            status_code=500,
            detail="Invalid response from document service.",
        )

    document_id = result.get("document_id")

    if not document_id:
        raise HTTPException(
            status_code=500,
            detail="Document service did not return a document ID.",
        )

    return DocumentUploadResponse(
        document_id=str(document_id),
        filename=str(
            result.get(
                "filename",
                filename,
            )
        ),
        content_type=result.get(
            "content_type",
            file.content_type,
        ),
        size=int(
            result.get(
                "file_size",
                0,
            )
        ),
        status=str(
            result.get(
                "status",
                "processed",
            )
        ),
        extracted_text=result.get(
            "extracted_text",
        ),
        extracted_data=result.get(
            "extracted_data",
            {},
        ) or {},
        message=str(
            result.get(
                "message",
                "Document uploaded successfully.",
            )
        ),
    )


# ============================================================
# GET /api/documents/{document_id}
# ============================================================

@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
async def get_document(
    document_id: str,
) -> DocumentResponse:
    """
    Retrieve information about an uploaded document.
    """

    document_id = document_id.strip()

    if not document_id:
        raise HTTPException(
            status_code=400,
            detail="Document ID cannot be empty.",
        )

    document_service = get_document_service()

    try:
        result = await document_service.get_document(
            document_id=document_id,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to retrieve document: {str(exc)}"
            ),
        ) from exc

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    if not isinstance(result, dict):
        raise HTTPException(
            status_code=500,
            detail="Invalid document data returned by service.",
        )

    return DocumentResponse(
        document_id=str(
            result.get(
                "document_id",
                document_id,
            )
        ),
        filename=str(
            result.get(
                "filename",
                "",
            )
        ),
        content_type=result.get(
            "content_type",
        ),
        size=int(
            result.get(
                "file_size",
                0,
            )
        ),
        status=str(
            result.get(
                "status",
                "unknown",
            )
        ),
        extracted_text=result.get(
            "extracted_text",
        ),
        extracted_data=result.get(
            "extracted_data",
            {},
        ) or {},
    )


# ============================================================
# DELETE /api/documents/{document_id}
# ============================================================

@router.delete(
    "/{document_id}",
)
async def delete_document(
    document_id: str,
) -> Dict[str, str]:
    """
    Delete a citizen-uploaded document.

    The actual deletion is performed by the document service.
    """

    document_id = document_id.strip()

    if not document_id:
        raise HTTPException(
            status_code=400,
            detail="Document ID cannot be empty.",
        )

    document_service = get_document_service()

    try:
        deleted = await document_service.delete_document(
            document_id=document_id,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to delete document: {str(exc)}"
            ),
        ) from exc

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return {
        "status": "deleted",
        "document_id": document_id,
    }


# ============================================================
# GET /api/documents/health/status
# ============================================================

@router.get(
    "/health/status",
)
async def documents_health() -> Dict[str, str]:
    """
    Health check for the document router.
    """

    return {
        "status": "ok",
        "service": "documents",
    }