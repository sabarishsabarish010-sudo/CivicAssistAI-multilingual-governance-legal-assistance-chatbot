from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(
    prefix="/api/legal",
    tags=["Legal Assistance"],
)


# ============================================================
# Request Models
# ============================================================

class LegalQueryRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Citizen's legal problem or question",
    )

    user_id: Optional[str] = Field(
        default=None,
        description="Optional user identifier",
    )

    conversation_id: Optional[str] = Field(
        default=None,
        description="Optional legal conversation identifier",
    )

    language: str = Field(
        default="en",
        min_length=2,
        max_length=10,
        description="Language used by the citizen",
    )


class LegalSearchRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Legal topic or problem to search",
    )

    language: str = Field(
        default="en",
        min_length=2,
        max_length=10,
    )

    limit: int = Field(
        default=10,
        ge=1,
        le=50,
    )


# ============================================================
# Response Models
# ============================================================

class LegalSource(BaseModel):
    title: str
    source_type: str
    reference: Optional[str] = None


class LegalResponse(BaseModel):
    response: str
    language: str
    conversation_id: Optional[str] = None
    legal_topic: Optional[str] = None
    immediate_actions: List[str] = Field(default_factory=list)
    documents_to_preserve: List[str] = Field(default_factory=list)
    authorities_or_services: List[str] = Field(default_factory=list)
    sources: List[LegalSource] = Field(default_factory=list)


class LegalDocument(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    source_type: Optional[str] = None
    reference: Optional[str] = None


# ============================================================
# Legal Engine Loader
# ============================================================

def get_legal_engine():
    """
    Load the legal engine.

    The legal engine is responsible for:

    - legal knowledge retrieval
    - legal-topic identification
    - source-grounded legal information
    - citizen problem analysis
    - relevant legal provisions
    - immediate action guidance
    - document/evidence guidance
    - appropriate legal-aid services
    """

    try:
        from app.engines.legal_engine import LegalEngine

    except ImportError as exc:
        raise HTTPException(
            status_code=500,
            detail="Legal engine is not available.",
        ) from exc

    try:
        return LegalEngine()

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to initialize legal engine: {str(exc)}",
        ) from exc


# ============================================================
# Helper
# ============================================================

def normalize_source(source: Any) -> LegalSource:
    """
    Convert a legal-engine source into the API response format.
    """

    if isinstance(source, LegalSource):
        return source

    if not isinstance(source, dict):
        raise HTTPException(
            status_code=500,
            detail="Invalid legal source returned by legal engine.",
        )

    return LegalSource(
        title=str(
            source.get(
                "title",
                "Unknown source",
            )
        ),
        source_type=str(
            source.get(
                "source_type",
                "official",
            )
        ),
        reference=source.get("reference"),
    )


# ============================================================
# POST /api/legal/query
# ============================================================

@router.post(
    "/query",
    response_model=LegalResponse,
)
async def legal_query(
    request: LegalQueryRequest,
) -> LegalResponse:
    """
    Process a citizen's legal problem or question.

    The legal engine determines:

        Citizen's situation
                ↓
        Legal problem
                ↓
        Relevant legal information
                ↓
        Possible protections/options
                ↓
        Evidence/documents to preserve
                ↓
        Immediate next steps
                ↓
        Appropriate legal-aid service
    """

    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Legal question cannot be empty.",
        )

    language = request.language.strip().lower()

    if not language:
        raise HTTPException(
            status_code=400,
            detail="Language cannot be empty.",
        )

    engine = get_legal_engine()

    try:
        result = await engine.process_legal_query(
            message=message,
            language=language,
            user_id=request.user_id,
            conversation_id=request.conversation_id,
        )

    except AttributeError as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Legal engine does not implement "
                "process_legal_query()."
            ),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to process the legal request: {str(exc)}"
            ),
        ) from exc

    if result is None:
        raise HTTPException(
            status_code=500,
            detail="Legal engine returned no response.",
        )

    if isinstance(result, LegalResponse):
        return result

    if not isinstance(result, dict):
        raise HTTPException(
            status_code=500,
            detail="Invalid response returned by legal engine.",
        )

    response_text = result.get("response")

    if not response_text:
        raise HTTPException(
            status_code=500,
            detail="Legal engine returned an empty response.",
        )

    source_list = result.get("sources", []) or []

    sources = [
        normalize_source(source)
        for source in source_list
    ]

    return LegalResponse(
        response=str(response_text),
        language=str(
            result.get(
                "language",
                language,
            )
        ),
        conversation_id=result.get(
            "conversation_id",
            request.conversation_id,
        ),
        legal_topic=result.get("legal_topic"),
        immediate_actions=result.get(
            "immediate_actions",
            [],
        ) or [],
        documents_to_preserve=result.get(
            "documents_to_preserve",
            [],
        ) or [],
        authorities_or_services=result.get(
            "authorities_or_services",
            [],
        ) or [],
        sources=sources,
    )


# ============================================================
# POST /api/legal/search
# ============================================================

@router.post(
    "/search",
    response_model=List[LegalDocument],
)
async def search_legal_information(
    request: LegalSearchRequest,
) -> List[LegalDocument]:
    """
    Search the CivicAssist legal knowledge base.

    The actual search is performed by the legal engine/RAG layer.
    """

    query = request.query.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Legal search query cannot be empty.",
        )

    engine = get_legal_engine()

    try:
        result = await engine.search_legal_information(
            query=query,
            language=request.language,
            limit=request.limit,
        )

    except AttributeError as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Legal engine does not implement "
                "search_legal_information()."
            ),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to search legal information: {str(exc)}"
            ),
        ) from exc

    if result is None:
        return []

    if not isinstance(result, list):
        raise HTTPException(
            status_code=500,
            detail="Invalid legal search result.",
        )

    documents: List[LegalDocument] = []

    for item in result:

        if isinstance(item, LegalDocument):
            documents.append(item)
            continue

        if not isinstance(item, dict):
            raise HTTPException(
                status_code=500,
                detail="Invalid legal document returned by engine.",
            )

        documents.append(
            LegalDocument(
                id=str(item.get("id", "")),
                title=str(item.get("title", "")),
                description=item.get("description"),
                source_type=item.get("source_type"),
                reference=item.get("reference"),
            )
        )

    return documents


# ============================================================
# GET /api/legal/sources
# ============================================================

@router.get(
    "/sources",
    response_model=List[LegalDocument],
)
async def get_legal_sources() -> List[LegalDocument]:
    """
    Return legal documents currently available in the
    CivicAssist legal knowledge base.
    """

    engine = get_legal_engine()

    try:
        result = await engine.get_legal_sources()

    except AttributeError as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Legal engine does not implement "
                "get_legal_sources()."
            ),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to retrieve legal sources: {str(exc)}"
            ),
        ) from exc

    if result is None:
        return []

    if not isinstance(result, list):
        raise HTTPException(
            status_code=500,
            detail="Invalid legal source list.",
        )

    documents: List[LegalDocument] = []

    for item in result:

        if isinstance(item, LegalDocument):
            documents.append(item)
            continue

        if not isinstance(item, dict):
            raise HTTPException(
                status_code=500,
                detail="Invalid legal source returned by engine.",
            )

        documents.append(
            LegalDocument(
                id=str(item.get("id", "")),
                title=str(item.get("title", "")),
                description=item.get("description"),
                source_type=item.get("source_type"),
                reference=item.get("reference"),
            )
        )

    return documents


# ============================================================
# GET /api/legal/health
# ============================================================

@router.get(
    "/health/status",
)
async def legal_health() -> Dict[str, str]:
    """
    Health check for the legal assistance router.
    """

    return {
        "status": "ok",
        "service": "legal",
    }