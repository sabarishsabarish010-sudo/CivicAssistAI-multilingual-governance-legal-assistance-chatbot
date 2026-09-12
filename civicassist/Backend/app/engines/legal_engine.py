from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.services.rag_service import get_rag_service


class LegalEngine:
    """
    Handles legal-information retrieval and response preparation.

    Legal knowledge is retrieved from the CivicAssist RAG knowledge base.
    The engine does not contain hard-coded legal advice or legal documents.
    """

    def __init__(self) -> None:
        self.rag_service = get_rag_service()

    async def process_legal_query(
        self,
        query: str,
        language: str = "en",
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        query = query.strip()
        language = language.strip().lower()

        if not query:
            raise ValueError("Legal query cannot be empty.")

        if not language:
            raise ValueError("Language cannot be empty.")

        search_results = self.rag_service.search(
            query=query,
            top_k=8,
            metadata_filter={"document_type": "legal"},
        )
        results = search_results.get("results", [])

        context = self.rag_service.build_context(results)

        sources = self._build_sources(results)

        return {
            "query": query,
            "language": language,
            "context": context,
            "sources": sources,
            "user_id": user_id,
            "conversation_id": conversation_id,
        }

    async def search_legal_information(
        self,
        query: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        query = query.strip()

        if not query:
            raise ValueError("Legal search query cannot be empty.")

        if limit < 1:
            raise ValueError("Limit must be at least 1.")

        if limit > 50:
            limit = 50

        search_results = self.rag_service.search(
            query=query,
            top_k=limit,
            metadata_filter={"document_type": "legal"},
        )
        results = search_results.get("results", [])

        return self._normalize_search_results(results)

    async def get_legal_sources(self) -> List[Dict[str, Any]]:
        search_results = self.rag_service.search(
            query="legal rights legal services acts regulations",
            top_k=50,
            metadata_filter={"document_type": "legal"},
        )
        results = search_results.get("results", [])

        sources: Dict[str, Dict[str, Any]] = {}

        for result in results:
            metadata = result.get("metadata", {})

            title = str(
                metadata.get("title")
                or metadata.get("source_title")
                or metadata.get("filename")
                or "Unknown legal source"
            )

            key = str(
                metadata.get("source")
                or metadata.get("reference")
                or metadata.get("url")
                or title
            )

            if key not in sources:
                sources[key] = {
                    "title": title,
                    "source_type": str(
                        metadata.get("source_type", "official")
                    ),
                    "reference": metadata.get("source")
                    or metadata.get("reference")
                    or metadata.get("url"),
                }

        return list(sources.values())

    def _normalize_search_results(
        self,
        results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []

        for result in results:
            metadata = result.get("metadata", {})

            normalized.append(
                {
                    "text": str(result.get("text", "")),
                    "score": result.get("score"),
                    "metadata": metadata,
                    "title": str(
                        metadata.get("title")
                        or metadata.get("source_title")
                        or metadata.get("filename")
                        or "Unknown legal source"
                    ),
                    "source_type": str(
                        metadata.get("source_type", "official")
                    ),
                    "reference": metadata.get("source")
                    or metadata.get("reference")
                    or metadata.get("url"),
                }
            )

        return normalized

    def _build_sources(
        self,
        results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        sources: List[Dict[str, Any]] = []
        seen = set()

        for result in results:
            metadata = result.get("metadata", {})

            title = str(
                metadata.get("title")
                or metadata.get("source_title")
                or metadata.get("filename")
                or "Unknown legal source"
            )

            reference = (
                metadata.get("source")
                or metadata.get("reference")
                or metadata.get("url")
            )

            source_type = str(
                metadata.get("source_type", "official")
            )

            key = (title, reference, source_type)

            if key in seen:
                continue

            seen.add(key)

            sources.append(
                {
                    "title": title,
                    "source_type": source_type,
                    "reference": reference,
                }
            )

        return sources


_legal_engine: Optional[LegalEngine] = None


def get_legal_engine() -> LegalEngine:
    global _legal_engine

    if _legal_engine is None:
        _legal_engine = LegalEngine()

    return _legal_engine


async def process_legal_query(
    query: str,
    language: str = "en",
    user_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
) -> Dict[str, Any]:
    engine = get_legal_engine()

    return await engine.process_legal_query(
        query=query,
        language=language,
        user_id=user_id,
        conversation_id=conversation_id,
    )


async def search_legal_information(
    query: str,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    engine = get_legal_engine()

    return await engine.search_legal_information(
        query=query,
        limit=limit,
    )


async def get_legal_sources() -> List[Dict[str, Any]]:
    engine = get_legal_engine()

    return await engine.get_legal_sources()