from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import UploadFile

from app.config import settings


class DocumentService:
    def __init__(self) -> None:
        self.upload_dir = Path(settings.upload_path)
        self.max_upload_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

        self.allowed_extensions = {
            ".pdf",
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
        }

    async def process_upload(
        self,
        file: UploadFile,
        user_id: Optional[str] = None,
        application_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not file.filename:
            raise ValueError("A document file is required.")

        extension = Path(file.filename).suffix.lower()

        if extension not in self.allowed_extensions:
            raise ValueError(
                "Unsupported document type. "
                "Supported types are PDF, PNG, JPG, JPEG, and WEBP."
            )

        content = await file.read()

        if not content:
            raise ValueError("The uploaded document is empty.")

        if len(content) > self.max_upload_size:
            raise ValueError(
                f"Document exceeds the maximum allowed size of "
                f"{settings.MAX_UPLOAD_SIZE_MB} MB."
            )

        document_id = str(uuid.uuid4())

        safe_filename = self._create_safe_filename(
            document_id=document_id,
            extension=extension,
        )

        file_path = self.upload_dir / safe_filename

        file_path.write_bytes(content)

        try:
            extracted_text = await self._extract_text(
                file_path=file_path,
                extension=extension,
            )

            extracted_data = self._extract_structured_data(
                extracted_text
            )

            return {
                "document_id": document_id,
                "filename": file.filename,
                "content_type": file.content_type,
                "file_size": len(content),
                "status": "processed",
                "user_id": user_id,
                "application_id": application_id,
                "extracted_text": extracted_text,
                "extracted_data": extracted_data,
            }

        except Exception:
            if file_path.exists():
                file_path.unlink()

            raise

    async def get_document(
        self,
        document_id: str,
    ) -> Dict[str, Any]:
        document_id = document_id.strip()

        if not document_id:
            raise ValueError("Document ID cannot be empty.")

        document_path = self._find_document(document_id)

        if document_path is None:
            raise FileNotFoundError(
                f"Document '{document_id}' was not found."
            )

        extension = document_path.suffix.lower()

        extracted_text = await self._extract_text(
            file_path=document_path,
            extension=extension,
        )

        extracted_data = self._extract_structured_data(
            extracted_text
        )

        return {
            "document_id": document_id,
            "filename": document_path.name,
            "file_size": document_path.stat().st_size,
            "status": "processed",
            "extracted_text": extracted_text,
            "extracted_data": extracted_data,
        }

    async def delete_document(
        self,
        document_id: str,
    ) -> Dict[str, Any]:
        document_id = document_id.strip()

        if not document_id:
            raise ValueError("Document ID cannot be empty.")

        document_path = self._find_document(document_id)

        if document_path is None:
            raise FileNotFoundError(
                f"Document '{document_id}' was not found."
            )

        document_path.unlink()

        return {
            "document_id": document_id,
            "status": "deleted",
        }

    async def _extract_text(
        self,
        file_path: Path,
        extension: str,
    ) -> str:
        if extension == ".pdf":
            return self._extract_pdf_text(file_path)

        if extension in {".png", ".jpg", ".jpeg", ".webp"}:
            return self._extract_image_text(file_path)

        raise ValueError(
            f"Unsupported document extension: {extension}"
        )

    def _extract_pdf_text(
        self,
        file_path: Path,
    ) -> str:
        try:
            import fitz
        except ImportError as exc:
            raise RuntimeError(
                "PyMuPDF is not installed."
            ) from exc

        text_parts = []

        with fitz.open(file_path) as document:
            for page in document:
                page_text = page.get_text("text")

                if page_text:
                    text_parts.append(page_text.strip())

        extracted_text = "\n\n".join(
            part for part in text_parts if part
        ).strip()

        if extracted_text:
            return extracted_text

        return self._ocr_pdf(file_path)

    def _ocr_pdf(
        self,
        file_path: Path,
    ) -> str:
        try:
            import fitz
            import pytesseract
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError(
                "OCR dependencies are not installed."
            ) from exc

        text_parts = []

        with fitz.open(file_path) as document:
            for page in document:
                pixmap = page.get_pixmap(
                    matrix=fitz.Matrix(2, 2),
                    alpha=False,
                )

                image = Image.frombytes(
                    "RGB",
                    [
                        pixmap.width,
                        pixmap.height,
                    ],
                    pixmap.samples,
                )

                page_text = pytesseract.image_to_string(
                    image,
                )

                if page_text:
                    text_parts.append(page_text.strip())

        return "\n\n".join(
            part for part in text_parts if part
        ).strip()

    def _extract_image_text(
        self,
        file_path: Path,
    ) -> str:
        try:
            import pytesseract
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError(
                "OCR dependencies are not installed."
            ) from exc

        image = Image.open(file_path)

        extracted_text = pytesseract.image_to_string(
            image,
        )

        return extracted_text.strip()

    def _extract_structured_data(
        self,
        extracted_text: str,
    ) -> Dict[str, Any]:
        if not extracted_text:
            return {}

        return {
            "text_available": True,
            "character_count": len(extracted_text),
        }

    def _create_safe_filename(
        self,
        document_id: str,
        extension: str,
    ) -> str:
        return f"{document_id}{extension}"

    def _find_document(
        self,
        document_id: str,
    ) -> Optional[Path]:
        for extension in self.allowed_extensions:
            document_path = (
                self.upload_dir
                / f"{document_id}{extension}"
            )

            if document_path.is_file():
                return document_path

        return None