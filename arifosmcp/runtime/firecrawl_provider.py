# arifOS SENSE Pipeline — Firecrawl Provider
# Async deep-page scrape via Firecrawl API
# DITEMPA BUKAN DIBERI

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

import httpx

from .result_normalizer import NormalizedResult

logger = logging.getLogger(__name__)

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")
FIRECRAWL_BASE_URL = "https://api.firecrawl.dev/v0"


@dataclass
class FirecrawlResponse:
    success: bool
    title: str | None
    description: str | None
    content: str | None
    url: str
    raw: dict[str, Any]


class FirecrawlProvider:
    __slots__ = ("_api_key", "_base_url", "_timeout")

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        self._api_key = api_key or FIRECRAWL_API_KEY
        self._base_url = base_url or FIRECRAWL_BASE_URL
        self._timeout = timeout

    @property
    def is_live(self) -> bool:
        return bool(self._api_key)

    async def scrape_url(self, url: str) -> NormalizedResult | None:
        if not self._api_key:
            return None
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(
                    f"{self._base_url}/scrape",
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "url": url,
                        "pageOptions": {"onlyMainContent": True},
                    },
                )
                if resp.status_code != 200:
                    return None
                data = resp.json()
                return self._normalize_response(data, url)
        except Exception as e:
            logger.error(f"Firecrawl scrape failed for {url}: {e}")
            return None

    async def search(self, query: str, limit: int = 5) -> list[NormalizedResult]:
        if not self._api_key:
            return []
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(
                    f"{self._base_url}/search",
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    json={"query": query, "limit": limit},
                )
                if resp.status_code != 200:
                    return []
                data = resp.json()
                return [
                    self._normalize_response(item, item.get("url", ""))
                    for item in data.get("data", [])[:limit]
                    if item.get("url")
                ]
        except Exception as e:
            logger.error(f"Firecrawl search failed: {e}")
            return []

    def _normalize_response(self, data: dict[str, Any], original_url: str) -> NormalizedResult:
        return NormalizedResult(
            url=data.get("metadata", {}).get("ogUrl", original_url) or original_url,
            title=data.get("title", "") or data.get("metadata", {}).get("title", ""),
            snippet=data.get("description", "") or (data.get("content", "") or "")[:300],
            source="firecrawl",
            score=0.8,
            published_date=None,
            author=data.get("author"),
            provider_type="firecrawl",
            extra={"raw_content": (data.get("content") or "")[:1000]},
        )
