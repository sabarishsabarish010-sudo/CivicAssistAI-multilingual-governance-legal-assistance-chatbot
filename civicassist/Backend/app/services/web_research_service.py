from typing import Any, Dict, List, Optional

import httpx
import fitz  # PyMuPDF
from bs4 import BeautifulSoup


class WebResearchService:

    def __init__(self):
        self.timeout = 10.0
        self.max_response_size = 20 * 1024 * 1024
        self.max_text_length = 30000

    async def fetch_url(self, url: str) -> Optional[Dict[str, Any]]:

        if not self._validate_url(url):
            return None

        headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/pdf;q=0.9,*/*;q=0.8"
            ),
        }

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                headers=headers
            ) as client:

                response = await client.get(url)

                response.raise_for_status()

                content = response.content

                if len(content) > self.max_response_size:
                    print("[WebResearch] Response too large")
                    return None

                content_type = response.headers.get(
                    "content-type",
                    ""
                ).lower()

                return {
                    "url": str(response.url),
                    "status_code": response.status_code,
                    "content_type": content_type,
                    "content": content,
                }

        except Exception as exc:
            print(
                f"[WebResearch] Fetch failed: "
                f"{type(exc).__name__}: {exc}"
            )
            return None

    async def extract_page(
        self,
        url: str
    ) -> Optional[Dict[str, Any]]:

        result = await self.fetch_url(url)

        if not result:
            return None

        content = result["content"]
        content_type = result["content_type"]

        # --------------------------------------------------
        # PDF
        # --------------------------------------------------

        if (
            "application/pdf" in content_type
            or url.lower().split("?")[0].endswith(".pdf")
        ):
            return self._extract_pdf(
                content,
                result["url"]
            )

        # --------------------------------------------------
        # HTML
        # --------------------------------------------------

        return self._extract_html(
            content,
            result["url"]
        )

    def _extract_pdf(
        self,
        content: bytes,
        url: str
    ) -> Optional[Dict[str, Any]]:

        try:
            document = fitz.open(
                stream=content,
                filetype="pdf"
            )

            pages = []

            for page in document:
                text = page.get_text("text")

                if text:
                    pages.append(text)

            document.close()

            full_text = "\n".join(pages)

            full_text = " ".join(
                full_text.split()
            )

            if not full_text:
                print(
                    "[WebResearch] PDF contains no extractable text"
                )
                return None

            full_text = full_text[
                :self.max_text_length
            ]

            return {
                "url": url,
                "title": "Official PDF Document",
                "text": full_text,
                "type": "pdf",
            }

        except Exception as exc:
            print(
                f"[WebResearch] PDF extraction failed: "
                f"{type(exc).__name__}: {exc}"
            )
            return None

    def _extract_html(
        self,
        content: bytes,
        url: str
    ) -> Optional[Dict[str, Any]]:

        try:
            soup = BeautifulSoup(
                content,
                "lxml"
            )

            for tag in soup([
                "script",
                "style",
                "noscript",
                "svg",
                "iframe",
                "nav",
                "footer",
                "header",
                "form",
            ]):
                tag.decompose()

            title = ""

            if soup.title:
                title = soup.title.get_text(
                    " ",
                    strip=True
                )

            main = (
                soup.find("main")
                or soup.find("article")
                or soup.body
                or soup
            )

            text = main.get_text(
                " ",
                strip=True
            )

            text = " ".join(
                text.split()
            )

            if not text:
                print(
                    "[WebResearch] HTML page has no extractable text"
                )
                return None

            text = text[
                :self.max_text_length
            ]

            return {
                "url": url,
                "title": title,
                "text": text,
                "type": "html",
            }

        except Exception as exc:
            print(
                f"[WebResearch] HTML extraction failed: "
                f"{type(exc).__name__}: {exc}"
            )
            return None

    async def research_urls(
        self,
        urls: List[str]
    ) -> List[Dict[str, Any]]:

        results = []

        for url in urls:

            page = await self.extract_page(url)

            if page:
                results.append(page)

        return results

    async def verify_source(
        self,
        url: str
    ) -> bool:

        result = await self.fetch_url(url)

        return result is not None

    def _validate_url(
        self,
        url: str
    ) -> bool:

        return (
            url.startswith("http://")
            or url.startswith("https://")
        )


_service: Optional[WebResearchService] = None


def get_web_research_service() -> WebResearchService:

    global _service

    if _service is None:
        _service = WebResearchService()

    return _service