from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.config import settings
from app.services.document_service import get_document_service
from app.services.web_research_service import get_web_research_service


class ApplicationEngine:
    """
    Handles the application-assistance workflow for supported
    government schemes and services.

    The engine researches official application procedures, collects
    documents, prepares application information, and keeps the
    citizen in control of sensitive and final actions.

    It does not bypass OTP, CAPTCHA, digital signatures, payments,
    declarations, or final submission controls.
    """

    def __init__(self) -> None:
        self.document_service = get_document_service()
        self.web_research_service = get_web_research_service()

        self.upload_directory = settings.upload_path
        self.upload_directory.mkdir(parents=True, exist_ok=True)

        self.application_directory = (
            self.upload_directory / "applications"
        )
        self.application_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    async def start_application(
        self,
        user_id: Optional[str] = None,
        scheme_id: Optional[str] = None,
        service_id: Optional[str] = None,
        language: str = "en",
        user_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        language = language.strip().lower()

        if not scheme_id and not service_id:
            raise ValueError(
                "Either scheme_id or service_id is required."
            )

        if scheme_id and service_id:
            raise ValueError(
                "Provide either scheme_id or service_id, not both."
            )

        if not language:
            raise ValueError("Language cannot be empty.")

        application_id = str(uuid.uuid4())

        application = {
            "application_id": application_id,
            "status": "created",
            "scheme_id": scheme_id,
            "service_id": service_id,
            "user_id": user_id,
            "language": language,
            "user_data": user_data or {},
            "required_documents": [],
            "submitted_documents": [],
            "form_data": {},
            "portal_url": None,
            "next_step": (
                "Application target identified. "
                "Official application procedure must be researched."
            ),
        }

        await self._save_application(application)

        return {
            "application_id": application_id,
            "status": application["status"],
            "scheme_id": scheme_id,
            "service_id": service_id,
            "required_documents": [],
            "next_step": application["next_step"],
        }

    async def process_application_document(
        self,
        application_id: str,
        file: Any,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        application = await self.get_application(
            application_id=application_id,
            user_id=user_id,
        )

        if application is None:
            raise ValueError("Application was not found.")

        document_result = await self.document_service.process_upload(
            file=file,
            user_id=user_id,
            application_id=application_id,
        )

        submitted_documents = application.get(
            "submitted_documents",
            [],
        )

        submitted_documents.append(
            {
                "document_id": document_result.get("document_id"),
                "filename": document_result.get("filename"),
                "content_type": document_result.get("content_type"),
                "status": document_result.get("status"),
                "extracted_data": document_result.get(
                    "extracted_data",
                    {},
                ),
            }
        )

        application["submitted_documents"] = submitted_documents
        application["status"] = "documents_received"
        application["next_step"] = (
            "Review the uploaded document information and "
            "continue collecting any remaining required documents."
        )

        await self._save_application(application)

        return {
            "application_id": application_id,
            "document_id": document_result.get("document_id"),
            "status": application["status"],
            "message": (
                "Application document received and processed."
            ),
        }

    async def get_application(
        self,
        application_id: str,
        user_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        application_id = application_id.strip()

        if not application_id:
            raise ValueError("Application ID cannot be empty.")

        application_file = (
            self.application_directory
            / f"{application_id}.json"
        )

        if not application_file.exists():
            return None

        try:
            data = json.loads(
                application_file.read_text(
                    encoding="utf-8",
                )
            )
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(
                "Unable to read application data."
            ) from exc

        stored_user_id = data.get("user_id")

        if (
            user_id is not None
            and stored_user_id is not None
            and stored_user_id != user_id
        ):
            raise PermissionError(
                "You do not have access to this application."
            )

        return data

    async def confirm_application(
        self,
        application_id: str,
        user_id: Optional[str] = None,
        confirmation: bool = False,
    ) -> Dict[str, Any]:
        application = await self.get_application(
            application_id=application_id,
            user_id=user_id,
        )

        if application is None:
            raise ValueError("Application was not found.")

        if not confirmation:
            return {
                "application_id": application_id,
                "status": application.get(
                    "status",
                    "created",
                ),
                "message": (
                    "Application confirmation was not provided. "
                    "No final action was performed."
                ),
                "next_step": (
                    "Review the application information and "
                    "confirm when ready."
                ),
                "portal_url": application.get(
                    "portal_url"
                ),
            }

        application["status"] = "ready_for_user_submission"
        application["next_step"] = (
            "Review the completed application on the official "
            "government portal. Complete any OTP, CAPTCHA, "
            "digital signature, payment, declaration, and final "
            "submission steps yourself."
        )

        await self._save_application(application)

        return {
            "application_id": application_id,
            "status": application["status"],
            "message": (
                "Application information is ready for citizen "
                "review. Final submission remains under citizen control."
            ),
            "next_step": application["next_step"],
            "portal_url": application.get("portal_url"),
        }

    async def research_application_procedure(
        self,
        application_id: str,
    ) -> Dict[str, Any]:
        application = await self.get_application(
            application_id=application_id,
        )

        if application is None:
            raise ValueError("Application was not found.")

        target_id = (
            application.get("scheme_id")
            or application.get("service_id")
        )

        if not target_id:
            raise ValueError(
                "Application does not contain a scheme or service."
            )

        research_query = (
            f"{target_id} official government application "
            "procedure required documents application portal"
        )

        search_results = await self.web_research_service.research_urls(
            urls=[
                settings.MYSCHEME_URL,
                settings.DATA_GOV_URL,
            ],
            query=research_query,
        )

        application["status"] = "procedure_researched"
        application["next_step"] = (
            "Review the researched official information and "
            "collect the required documents."
        )

        await self._save_application(application)

        return {
            "application_id": application_id,
            "status": application["status"],
            "research": search_results,
            "next_step": application["next_step"],
        }

    async def _save_application(
        self,
        application: Dict[str, Any],
    ) -> None:
        application_id = application.get("application_id")

        if not application_id:
            raise ValueError(
                "Application ID is required."
            )

        application_file = (
            self.application_directory
            / f"{application_id}.json"
        )

        temporary_file = application_file.with_suffix(
            ".json.tmp"
        )

        try:
            temporary_file.write_text(
                json.dumps(
                    application,
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            temporary_file.replace(application_file)
        except OSError as exc:
            raise RuntimeError(
                "Unable to save application data."
            ) from exc


_application_engine: Optional[ApplicationEngine] = None


def get_application_engine() -> ApplicationEngine:
    global _application_engine

    if _application_engine is None:
        _application_engine = ApplicationEngine()

    return _application_engine