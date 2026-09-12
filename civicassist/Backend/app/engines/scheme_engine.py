from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from app.services.rag_service import get_rag_service


class SchemeEngine:
    """
    Handles government-scheme discovery, retrieval, and eligibility
    preparation using the CivicAssist knowledge base.

    Scheme information is retrieved from indexed government data and
    documents. No scheme information is hard-coded in this engine.
    """

    def __init__(self) -> None:
        self.rag_service = get_rag_service()

    async def get_schemes(
        self,
        category: Optional[str] = None,
        state: Optional[str] = None,
        language: str = "en",
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        language = language.strip().lower()

        if not language:
            raise ValueError("Language cannot be empty.")

        if limit < 1:
            raise ValueError("Limit must be at least 1.")

        limit = min(limit, 100)

        metadata_filter: Dict[str, Any] = {
            "document_type": "scheme"
        }

        if category:
            metadata_filter["category"] = category.strip()

        if state:
            metadata_filter["state"] = state.strip()

        search_results = self.rag_service.search(
            query="government schemes benefits eligibility application",
            top_k=limit,
            metadata_filter=metadata_filter,
        )
        results = search_results.get("results", [])

        return self._normalize_scheme_results(results)

    async def search_schemes(
        self,
        query: str,
        category: Optional[str] = None,
        state: Optional[str] = None,
        language: str = "en",
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        query = query.strip()
        language = language.strip().lower()

        if not query:
            raise ValueError("Scheme search query cannot be empty.")

        if not language:
            raise ValueError("Language cannot be empty.")

        if limit < 1:
            raise ValueError("Limit must be at least 1.")

        limit = min(limit, 100)

        metadata_filter: Dict[str, Any] = {
            "document_type": "scheme"
        }

        if category:
            metadata_filter["category"] = category.strip()

        if state:
            metadata_filter["state"] = state.strip()

        search_results = self.rag_service.search(
            query=query,
            top_k=limit,
            metadata_filter=metadata_filter,
        )
        results = search_results.get("results", [])

        return self._normalize_scheme_results(results)

    async def get_scheme(
        self,
        scheme_id: str,
        language: str = "en",
    ) -> Optional[Dict[str, Any]]:
        scheme_id = scheme_id.strip()
        language = language.strip().lower()

        if not scheme_id:
            raise ValueError("Scheme ID cannot be empty.")

        if not language:
            raise ValueError("Language cannot be empty.")

        search_results = self.rag_service.search(
            query=scheme_id,
            top_k=20,
            metadata_filter={"document_type": "scheme"},
        )
        results = search_results.get("results", [])

        for result in results:
            metadata = result.get("metadata", {})

            result_scheme_id = str(
                metadata.get("scheme_id", "")
            ).strip()

            if result_scheme_id == scheme_id:
                return self._build_scheme_detail(result)

        return None

    async def check_eligibility(
        self,
        scheme_id: str,
        user_data: Dict[str, Any],
        language: str = "en",
    ) -> Dict[str, Any]:
        scheme_id = scheme_id.strip()
        language = language.strip().lower()

        if not scheme_id:
            raise ValueError("Scheme ID cannot be empty.")

        if not isinstance(user_data, dict):
            raise ValueError("User data must be an object.")

        if not language:
            raise ValueError("Language cannot be empty.")

        scheme = await self.get_scheme(
            scheme_id=scheme_id,
            language=language,
        )

        if scheme is None:
            raise ValueError("Scheme was not found in the knowledge base.")

        eligibility_information = scheme.get(
            "eligibility",
            []
        )

        required_documents = scheme.get(
            "required_documents",
            []
        )

        return {
            "scheme_id": scheme_id,
            "eligible": None,
            "reasons": [],
            "missing_information": self._identify_missing_information(
                eligibility_information,
                user_data,
            ),
            "required_documents": required_documents,
            "next_steps": scheme.get("application_process", []),
        }

    def _normalize_scheme_results(
        self,
        results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        schemes: List[Dict[str, Any]] = []
        seen = set()

        for result in results:
            metadata = result.get("metadata", {})

            scheme_id = str(
                metadata.get("scheme_id", "")
            ).strip()

            title = str(
                metadata.get("title")
                or metadata.get("scheme_name")
                or metadata.get("source_title")
                or metadata.get("filename")
                or "Government Scheme"
            )

            key = scheme_id or title

            if key in seen:
                continue

            seen.add(key)

            schemes.append(
                {
                    "scheme_id": scheme_id or None,
                    "name": title,
                    "description": str(
                        metadata.get("description", "")
                    ),
                    "category": metadata.get("category"),
                    "state": metadata.get("state"),
                    "official_source": (
                        metadata.get("official_source")
                        or metadata.get("source")
                        or metadata.get("url")
                    ),
                    "official_portal": metadata.get(
                        "official_portal"
                    ),
                }
            )

        return schemes

    def _build_scheme_detail(
        self,
        result: Dict[str, Any],
    ) -> Dict[str, Any]:
        metadata = result.get("metadata", {})
        text = str(result.get("text", ""))

        return {
            "scheme_id": metadata.get("scheme_id"),
            "name": (
                metadata.get("title")
                or metadata.get("scheme_name")
                or metadata.get("source_title")
                or metadata.get("filename")
            ),
            "description": metadata.get(
                "description",
                text,
            ),
            "category": metadata.get("category"),
            "state": metadata.get("state"),
            "eligibility": self._parse_metadata_value(
                metadata.get("eligibility", [])
            ),
            "benefits": self._parse_metadata_value(
                metadata.get("benefits", [])
            ),
            "required_documents": self._parse_metadata_value(
                metadata.get("required_documents", [])
            ),
            "application_process": self._parse_metadata_value(
                metadata.get("application_process", [])
            ),
            "official_source": (
                metadata.get("official_source")
                or metadata.get("source")
                or metadata.get("url")
            ),
            "official_portal": metadata.get(
                "official_portal"
            ),
        }

    def _parse_metadata_value(
        self,
        value: Any,
    ) -> Any:
        if value is None:
            return []

        if isinstance(value, (list, dict)):
            return value

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return []

            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return [value]

        return value

    def _identify_missing_information(
        self,
        eligibility_information: Any,
        user_data: Dict[str, Any],
    ) -> List[str]:
        if not eligibility_information:
            return []

        if isinstance(eligibility_information, dict):
            required_fields = eligibility_information.keys()
        elif isinstance(eligibility_information, list):
            required_fields = []

            for item in eligibility_information:
                if isinstance(item, dict):
                    field = (
                        item.get("field")
                        or item.get("attribute")
                        or item.get("information")
                    )

                    if field:
                        required_fields.append(str(field))

        else:
            return []

        missing: List[str] = []

        for field in required_fields:
            field_name = str(field).strip()

            if field_name and field_name not in user_data:
                missing.append(field_name)

        return missing


_scheme_engine: Optional[SchemeEngine] = None


def get_scheme_engine() -> SchemeEngine:
    global _scheme_engine

    if _scheme_engine is None:
        _scheme_engine = SchemeEngine()

    return _scheme_engine


async def get_schemes(
    category: Optional[str] = None,
    state: Optional[str] = None,
    language: str = "en",
    limit: int = 20,
) -> List[Dict[str, Any]]:
    engine = get_scheme_engine()

    return await engine.get_schemes(
        category=category,
        state=state,
        language=language,
        limit=limit,
    )


async def search_schemes(
    query: str,
    category: Optional[str] = None,
    state: Optional[str] = None,
    language: str = "en",
    limit: int = 20,
) -> List[Dict[str, Any]]:
    engine = get_scheme_engine()

    return await engine.search_schemes(
        query=query,
        category=category,
        state=state,
        language=language,
        limit=limit,
    )


async def get_scheme(
    scheme_id: str,
    language: str = "en",
) -> Optional[Dict[str, Any]]:
    engine = get_scheme_engine()

    return await engine.get_scheme(
        scheme_id=scheme_id,
        language=language,
    )


async def check_eligibility(
    scheme_id: str,
    user_data: Dict[str, Any],
    language: str = "en",
) -> Dict[str, Any]:
    engine = get_scheme_engine()

    return await engine.check_eligibility(
        scheme_id=scheme_id,
        user_data=user_data,
        language=language,
    )