from __future__ import annotations

from typing import Any, Dict, List, Optional

import chromadb
from sentence_transformers import SentenceTransformer

from app.config import settings


class RAGService:
    """
    Retrieval-Augmented Generation service for CivicAssist.

    Responsibilities:
    - Connect to ChromaDB
    - Load the multilingual embedding model
    - Search indexed document chunks
    - Build context for the LLM
    - Return source information
    """

    COLLECTION_NAME = "civicassist"

    EMBEDDING_MODEL = (
        "sentence-transformers/"
        "paraphrase-multilingual-mpnet-base-v2"
    )

    def __init__(self) -> None:
        print(
            f"Loading RAG embedding model: "
            f"{self.EMBEDDING_MODEL}"
        )

        self.embedding_model = SentenceTransformer(
            self.EMBEDDING_MODEL
        )

        # Get ChromaDB path from settings if available.
        vector_db_path = getattr(
            settings,
            "VECTOR_DB_PATH",
            "vector_db",
        )

        print(
            f"Connecting to ChromaDB: "
            f"{vector_db_path}"
        )

        self.client = chromadb.PersistentClient(
            path=str(vector_db_path)
        )

        try:
            self.collection = self.client.get_collection(
                self.COLLECTION_NAME
            )
        except Exception as exc:
            raise RuntimeError(
                f"ChromaDB collection "
                f"'{self.COLLECTION_NAME}' does not exist. "
                f"Run your ingestion script first. "
                f"Original error: {exc}"
            ) from exc

        print(
            f"RAG collection loaded: "
            f"{self.COLLECTION_NAME}"
        )

        print(
            f"Indexed chunks: "
            f"{self.collection.count()}"
        )

    # ---------------------------------------------------------
    # Search ChromaDB
    # ---------------------------------------------------------

    def search(
        self,
        query: str,
        limit: int = 5,
        document_type: Optional[str] = None,
        top_k: Optional[int] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        query = query.strip()

        if not query:
            raise ValueError(
                "Search query cannot be empty."
            )

        if top_k is not None:
            limit = top_k

        if limit < 1:
            limit = 1

        # Prevent unnecessarily large retrieval.
        limit = min(limit, 20)

        # Create embedding for user query.
        query_embedding = self.embedding_model.encode(
            query,
            normalize_embeddings=True,
        ).tolist()

        # Optional metadata filter.
        where = None

        filters = dict(metadata_filter or {})

        if document_type:
            filters["document_type"] = document_type.strip().lower()

        if filters:
            clauses = [
                {key: value}
                for key, value in filters.items()
                if value is not None and str(value).strip()
            ]
            where = clauses[0] if len(clauses) == 1 else {"$and": clauses}

        # Query ChromaDB.
        if where:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where,
                include=[
                    "documents",
                    "metadatas",
                    "distances",
                ],
            )
        else:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                include=[
                    "documents",
                    "metadatas",
                    "distances",
                ],
            )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        matches: List[Dict[str, Any]] = []

        for index, document in enumerate(documents):

            metadata = (
                metadatas[index]
                if index < len(metadatas)
                else {}
            )

            distance = (
                distances[index]
                if index < len(distances)
                else None
            )

            matches.append(
                {
                    "text": document,
                    "metadata": metadata,
                    "distance": distance,
                }
            )

        return {
            "query": query,
            "results": matches,
        }

    # ---------------------------------------------------------
    # Retrieve context
    # ---------------------------------------------------------

    def retrieve_context(
        self,
        query: str,
        limit: int = 5,
        document_type: Optional[str] = None,
    ) -> Dict[str, Any]:

        search_results = self.search(
            query=query,
            limit=limit,
            document_type=document_type,
        )

        results = search_results["results"]

        context_parts: List[str] = []
        sources: List[Dict[str, Any]] = []

        for index, result in enumerate(results, start=1):

            text = result.get("text", "").strip()
            metadata = result.get("metadata") or {}
            distance = result.get("distance")

            if not text:
                continue

            source = str(
                metadata.get(
                    "source",
                    "Unknown source",
                )
            )

            page = metadata.get("page")

            document_type_value = str(
                metadata.get(
                    "document_type",
                    "unknown",
                )
            )

            # Build context block for LLM.
            context_parts.append(
                f"[Source {index}]\n"
                f"Document Type: {document_type_value}\n"
                f"Source: {source}\n"
                f"Page: {page}\n"
                f"Content:\n{text}"
            )

            # Source metadata returned to API.
            sources.append(
                {
                    "title": source,
                    "source": source,
                    "source_type": document_type_value,
                    "document_type": document_type_value,
                    "page": page,
                    "distance": distance,
                }
            )

        context = "\n\n".join(context_parts)

        return {
            "query": query,
            "context": context,
            "sources": sources,
            "results": results,
        }

    # ---------------------------------------------------------
    # Build context manually
    # ---------------------------------------------------------

    def build_context(
        self,
        results: Dict[str, Any],
    ) -> str:

        result_list = results.get(
            "results",
            [],
        )

        context_parts: List[str] = []

        for index, result in enumerate(
            result_list,
            start=1,
        ):

            text = str(
                result.get("text", "")
            ).strip()

            metadata = (
                result.get("metadata")
                or {}
            )

            if not text:
                continue

            source = metadata.get(
                "source",
                "Unknown source",
            )

            page = metadata.get(
                "page",
                "Unknown",
            )

            document_type = metadata.get(
                "document_type",
                "Unknown",
            )

            context_parts.append(
                f"[Source {index}]\n"
                f"Document Type: {document_type}\n"
                f"Source: {source}\n"
                f"Page: {page}\n"
                f"Content:\n{text}"
            )

        return "\n\n".join(context_parts)

    # ---------------------------------------------------------
    # Add documents
    # ---------------------------------------------------------

    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:

        if not documents:
            return {
                "status": "ok",
                "added": 0,
            }

        if len(documents) != len(metadatas):
            raise ValueError(
                "documents and metadatas "
                "must have the same length."
            )

        if ids is None:
            ids = [
                f"civicassist_{i}"
                for i in range(len(documents))
            ]

        if len(ids) != len(documents):
            raise ValueError(
                "ids and documents "
                "must have the same length."
            )

        embeddings = self.embedding_model.encode(
            documents,
            normalize_embeddings=True,
        ).tolist()

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        return {
            "status": "ok",
            "added": len(documents),
        }

    # ---------------------------------------------------------
    # Delete documents
    # ---------------------------------------------------------

    def delete_documents(
        self,
        ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:

        if not ids:
            return {
                "status": "ok",
                "deleted": 0,
            }

        self.collection.delete(
            ids=ids
        )

        return {
            "status": "ok",
            "deleted": len(ids),
        }

    # ---------------------------------------------------------
    # Count chunks
    # ---------------------------------------------------------

    def count(self) -> int:
        return self.collection.count()

    # ---------------------------------------------------------
    # Health
    # ---------------------------------------------------------

    def health(self) -> Dict[str, Any]:

        try:
            count = self.collection.count()

            return {
                "status": "ok",
                "collection": self.COLLECTION_NAME,
                "chunks": count,
                "embedding_model": self.EMBEDDING_MODEL,
            }

        except Exception as exc:

            return {
                "status": "error",
                "collection": self.COLLECTION_NAME,
                "message": str(exc),
            }


# -------------------------------------------------------------
# Singleton
# -------------------------------------------------------------

_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:

    global _service

    if _service is None:
        _service = RAGService()

    return _service


# -------------------------------------------------------------
# Convenience functions
# -------------------------------------------------------------

def search(
    query: str,
    limit: int = 5,
    document_type: Optional[str] = None,
    top_k: Optional[int] = None,
    metadata_filter: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:

    service = get_rag_service()

    return service.search(
        query=query,
        limit=limit,
        document_type=document_type,
        top_k=top_k,
        metadata_filter=metadata_filter,
    )


def retrieve_context(
    query: str,
    limit: int = 5,
    document_type: Optional[str] = None,
) -> Dict[str, Any]:

    service = get_rag_service()

    return service.retrieve_context(
        query=query,
        limit=limit,
        document_type=document_type,
    )


def build_context(
    results: Dict[str, Any],
) -> str:

    service = get_rag_service()

    return service.build_context(
        results
    )


def get_rag_health() -> Dict[str, Any]:

    service = get_rag_service()

    return service.health()