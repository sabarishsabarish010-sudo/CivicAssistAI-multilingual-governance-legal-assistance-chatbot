from typing import Any, Dict, Optional
from urllib.parse import urlparse

import httpx

from app.config import settings


class TavilyService:
    SEARCH_URL = "https://api.tavily.com/search"

    def __init__(self):
        self.api_key = settings.TAVILY_API_KEY

        if not self.api_key:
            raise RuntimeError("TAVILY_API_KEY is not configured.")

    async def search_official_source(
        self,
        query: str,
        category: str
    ) -> Optional[Dict[str, Any]]:

        if category == "scheme":
            domains = [
                "myscheme.gov.in",
                "gov.in",
                "nic.in",
            ]
        elif category == "legal":
            domains = [
                "indiacode.nic.in",
                "nalsa.gov.in",
                "gov.in",
                "nic.in",
            ]
        else:
            return None

        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": 3,
            "include_domains": domains,
        }

        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                response = await client.post(
                    self.SEARCH_URL,
                    json=payload
                )

                response.raise_for_status()
                data = response.json()

        except Exception as exc:
            print(f"[Tavily] Search failed: {exc}")
            return None

        results = data.get("results", [])

        for result in results:
            url = result.get("url", "")

            if self._is_official_url(url, domains):
                return {
                    "title": result.get("title", ""),
                    "url": url,
                    "content": result.get("content", ""),
                }

        return None

    def _is_official_url(
        self,
        url: str,
        allowed_domains: list[str]
    ) -> bool:

        try:
            hostname = urlparse(url).hostname

            if not hostname:
                return False

            hostname = hostname.lower()

            return any(
                hostname == domain or
                hostname.endswith("." + domain)
                for domain in allowed_domains
            )

        except Exception:
            return False


_service: Optional[TavilyService] = None


def get_tavily_service() -> TavilyService:
    global _service

    if _service is None:
        _service = TavilyService()

    return _service