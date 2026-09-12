from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)

# ============================================================
# REQUEST
# ============================================================

class ChatRequest(BaseModel):

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Citizen's message",
    )

    user_id: Optional[str] = Field(
        default=None,
        description="Optional user identifier",
    )

    conversation_id: Optional[str] = Field(
        default=None,
        description="Existing conversation identifier",
    )

    language: str = Field(
        default="en",
        min_length=2,
        max_length=10,
        description="Language code",
    )


# ============================================================
# RESPONSE
# ============================================================

class Source(BaseModel):

    title: str

    source_type: str

    reference: Optional[str] = None


class ChatResponse(BaseModel):

    response: str

    language: str

    conversation_id: Optional[str] = None

    sources: List[Source] = Field(
        default_factory=list
    )


# ============================================================
# CHAT
# ============================================================

@router.post(
    "",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
) -> ChatResponse:

    message = request.message.strip()

    if not message:

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    language = (
        request.language
        .strip()
        .lower()
    )

    if not language:

        raise HTTPException(
            status_code=400,
            detail="Language cannot be empty.",
        )

    try:

        # ====================================================
        # 1. CLASSIFY QUESTION
        # ====================================================

        from app.services.query_classifier import (
            get_query_classifier,
        )

        classifier = (
            get_query_classifier()
        )

        query_type = await classifier.classify(
            message
        )

        print(
            f"[CivicAssist] "
            f"Query type: {query_type}"
        )

        # ====================================================
        # 2. GENERAL QUESTION
        #
        # NO Tavily
        # NO website
        # NO ChromaDB
        #
        # Directly → LLM
        # ====================================================

        if query_type == "general":

            print(
                "[CivicAssist] "
                "General question → direct LLM"
            )

            from app.services.llm_service import (
                generate_response,
            )

            result = await generate_response(
                message=message,
                language=language,
                user_id=request.user_id,
                conversation_id=(
                    request.conversation_id
                ),
                context=None,
            )

            return _build_chat_response(
                result=result,
                language=language,
                conversation_id=(
                    request.conversation_id
                ),
                sources=[],
            )

        # ====================================================
        # 3. SCHEME / LEGAL
        #
        # Tavily → ONE official website
        # ====================================================

        from app.services.tavily_service import (
            get_tavily_service,
        )

        tavily = get_tavily_service()

        source = (
            await tavily.search_official_source(
                query=message,
                category=query_type,
            )
        )

        if not source:

            print(
                "[CivicAssist] "
                "No official website found; using ChromaDB fallback."
            )

            # ----------------------------------------------
            # Fallback to existing ChromaDB
            # ----------------------------------------------

            return await _fallback_to_rag(
                request=request,
                message=message,
                language=language,
            )

        website_url = source["url"]

        print(
            "[CivicAssist] "
            f"Selected ONE source: {website_url}"
        )

        # ====================================================
        # 4. FETCH + EXTRACT ONE WEBSITE
        #
        # IMPORTANT:
        # The extracted text is temporary.
        #
        # It is NOT added to ChromaDB.
        # ====================================================

        from app.services.web_research_service import (
            get_web_research_service,
        )

        web_service = (
            get_web_research_service()
        )

        page = await web_service.extract_page(
            website_url
        )

        print(
            "[CivicAssist] Website source used:",
            page.get("url") if page else website_url,
        )

        if not page:
            website_text = (source.get("content") or "").strip()
            if website_text:
                print(
                    "[CivicAssist] Direct extraction failed; "
                    "using Tavily's official-source content."
                )
                page = {
                    "url": website_url,
                    "title": source.get("title", ""),
                    "text": website_text,
                }
            else:
                print(
                    "[CivicAssist] Website could not be extracted and "
                    "Tavily returned no content; using ChromaDB fallback."
                )

                return await _fallback_to_rag(
                    request=request,
                    message=message,
                    language=language,
                )

        website_text = (
            page.get("text", "")
            .strip()
        )

        if not website_text:

            tavily_text = (source.get("content") or "").strip()
            if tavily_text:
                print(
                    "[CivicAssist] Direct page had no text; "
                    "using Tavily's official-source content."
                )
                website_text = tavily_text
            else:
                print(
                    "[CivicAssist] Website and Tavily content are empty; "
                    "using ChromaDB fallback."
                )

                return await _fallback_to_rag(
                    request=request,
                    message=message,
                    language=language,
                )

        # ====================================================
        # 5. SEND WEBSITE TEXT DIRECTLY TO LLM
        #
        # NEVER:
        #
        # rag.add_documents(...)
        #
        # Therefore website text is NOT stored.
        # ====================================================

        context = f"""
OFFICIAL SOURCE
Title: {page.get("title") or source.get("title")}
URL: {page.get("url")}

OFFICIAL WEBSITE CONTENT:
{website_text}
"""
        from app.services.llm_service import (
            generate_response,
        )

        result = await generate_response(
            message=message,
            language=language,
            user_id=request.user_id,
            conversation_id=(
                request.conversation_id
            ),
            context=context,
        )

        # ====================================================
        # 6. RETURN ONE SOURCE
        # ====================================================

        sources = [
            Source(
                title=(
                    page.get("title")
                    or source.get("title")
                    or "Official Government Source"
                ),
                source_type=query_type,
                reference=page.get(
                    "url",
                    website_url,
                ),
            )
        ]

        return _build_chat_response(
            result=result,
            language=language,
            conversation_id=(
                request.conversation_id
            ),
            sources=sources,
        )

    except Exception as exc:

        print(
            "[CivicAssist] Chat error:",
            repr(exc),
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to process the chat "
                f"request: {str(exc)}"
            ),
        )


# ============================================================
# RAG FALLBACK
# ============================================================

async def _fallback_to_rag(
    request: ChatRequest,
    message: str,
    language: str,
) -> ChatResponse:

    print(
        "[CivicAssist] "
        "Using ChromaDB fallback; no live website content was sent to the LLM."
    )

    try:

        from app.services.rag_service import (
            get_rag_service,
        )

        rag = get_rag_service()

        search_results = rag.search(
            query=message,
            limit=5,
        )

        results = search_results.get("results", [])

        context = None

        sources = []

        if results:

            context = rag.build_context(search_results)

            for item in results:

                metadata = (
                    item.get(
                        "metadata",
                        {},
                    )
                    or {}
                )

                sources.append(
                    Source(
                        title=str(
                            metadata.get(
                                "source",
                                metadata.get(
                                    "title",
                                    "CivicAssist source",
                                ),
                            )
                        ),
                        source_type=str(
                            metadata.get(
                                "document_type",
                                "official",
                            )
                        ),
                        reference=str(
                            metadata.get(
                                "page",
                                "",
                            )
                        ),
                    )
                )

        from app.services.llm_service import (
            generate_response,
        )

        result = await generate_response(
            message=message,
            language=language,
            user_id=request.user_id,
            conversation_id=(
                request.conversation_id
            ),
            context=context,
        )

        return _build_chat_response(
            result=result,
            language=language,
            conversation_id=(
                request.conversation_id
            ),
            sources=sources,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to process the "
                f"fallback request: {str(exc)}"
            ),
        )


# ============================================================
# RESPONSE BUILDER
# ============================================================

def _build_chat_response(
    result,
    language: str,
    conversation_id: Optional[str],
    sources: List[Source],
) -> ChatResponse:

    if isinstance(
        result,
        ChatResponse,
    ):

        return result

    if not isinstance(
        result,
        dict,
    ):

        raise HTTPException(
            status_code=500,
            detail=(
                "Invalid response received "
                "from the LLM service."
            ),
        )

    response_text = result.get(
        "response"
    )

    if not response_text:

        raise HTTPException(
            status_code=500,
            detail=(
                "LLM service returned "
                "an empty response."
            ),
        )

    return ChatResponse(
        response=str(
            response_text
        ),
        language=str(
            result.get(
                "language",
                language,
            )
        ),
        conversation_id=result.get(
            "conversation_id",
            conversation_id,
        ),
        sources=sources,
    )


# ============================================================
# HEALTH
# ============================================================

@router.get(
    "/health"
)
async def chat_health() -> dict:

    return {
        "status": "ok",
        "service": "chat",
    }