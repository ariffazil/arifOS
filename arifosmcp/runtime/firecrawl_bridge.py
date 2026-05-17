"""
arifosmcp/runtime/firecrawl_bridge.py — Firecrawl REST API bridge for 111_SENSE

Wires firecrawl__search and firecrawl__scrape into the canonical arifOS tool surface
via Firecrawl REST API v2 (https://api.firecrawl.dev/v2/).
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

_FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")
_FIRECRAWL_BASE_URL = os.getenv("FIRECRAWL_BASE_URL", "https://api.firecrawl.dev/v2")


class FirecrawlBridge:
    """
    Async HTTP bridge for Firecrawl REST API v2.

    Tools: firecrawl-search (web search), firecrawl-scrape (URL content extraction).
    Firecrawl handles anti-bot, JavaScript rendering, and returns clean markdown/HTML.
    """

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=60.0,
                follow_redirects=True,
                headers={
                    "Authorization": f"Bearer {_FIRECRAWL_API_KEY}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
        return self._client

    async def _sanitize_query(self, query: str) -> str:
        dangerous = ["\x00", "\n", "\r", "$$", "<!--", "-->", "<script", "</script", "<?php", "?>"]
        sanitized = query
        for pattern in dangerous:
            sanitized = sanitized.replace(pattern, " ")
        return sanitized.strip()[:2048]

    async def _sanitize_url(self, url: str) -> str:
        sanitized = url.strip()
        for prefix in ("javascript:", "data:", "vbscript:", "file:"):
            if sanitized.lower().startswith(prefix):
                raise ValueError(f"URL scheme blocked: {prefix}")
        return sanitized[:4096]

    async def _f9_filter(self, text: str) -> tuple[str, float]:
        hantu_words = [
            "i feel",
            "i think",
            "my opinion",
            "i believe",
            "i wish",
            "i want",
            "i hope",
            "i fear",
            "conscious",
            "sentient",
            "self-aware",
            "i experience",
        ]
        lower = text.lower()
        score = sum(1 for w in hantu_words if w in lower) / len(hantu_words)
        for hw in hantu_words:
            lower = lower.replace(hw, f"[REDACTED-{hw.strip()}]")
        return lower, score

    async def search(
        self,
        query: str,
        limit: int = 5,
    ) -> dict[str, Any]:
        if not _FIRECRAWL_API_KEY:
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": "FIRECRAWL_API_KEY not set",
                "error_class": "config_missing",
                "results": None,
                "hits": [],
                "result_count": 0,
                "metrics": {"f2_truth_score": 0.99, "f3_earth_witness": 0.0},
                "witness_debug": {
                    "human": True,
                    "ai": True,
                    "earth": False,
                    "bridge": "firecrawl_search",
                },
            }

        sanitized = await self._sanitize_query(query)
        if not sanitized:
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": "empty query after sanitization",
                "error_class": "invalid_input",
                "results": None,
                "hits": [],
                "result_count": 0,
                "metrics": {"f2_truth_score": 0.99, "f3_earth_witness": 0.0},
                "witness_debug": {
                    "human": True,
                    "ai": True,
                    "earth": False,
                    "bridge": "firecrawl_search",
                },
            }

        client = self._get_client()
        try:
            resp = await client.post(
                f"{_FIRECRAWL_BASE_URL}/search",
                json={"query": sanitized, "limit": limit},
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            logger.error("FirecrawlBridge.search failed: %s", exc)
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": str(exc),
                "error_class": "bridge_failure",
                "results": None,
                "hits": [],
                "result_count": 0,
                "metrics": {"f2_truth_score": 0.99, "f3_earth_witness": 0.0},
                "witness_debug": {
                    "human": True,
                    "ai": True,
                    "earth": False,
                    "bridge": "firecrawl_search",
                },
            }

        if not data.get("success"):
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": data.get("error", "firecrawl returned success=false"),
                "error_class": "api_error",
                "results": data,
                "hits": [],
                "result_count": 0,
                "metrics": {"f2_truth_score": 0.95, "f3_earth_witness": 0.7},
                "witness_debug": {
                    "human": True,
                    "ai": True,
                    "earth": False,
                    "bridge": "firecrawl_search",
                },
            }

        web_results = data.get("data", {}).get("web", [])
        if not web_results:
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": "no web results from firecrawl",
                "error_class": "empty_results",
                "results": data,
                "hits": [],
                "result_count": 0,
                "metrics": {"f2_truth_score": 0.95, "f3_earth_witness": 0.7},
                "witness_debug": {
                    "human": True,
                    "ai": True,
                    "earth": False,
                    "bridge": "firecrawl_search",
                },
            }

        hit_count = len(web_results)
        f2 = 0.99 if hit_count >= 5 else 0.95 if hit_count >= 1 else 0.33
        f3 = 0.95 if hit_count >= 5 else 0.7 if hit_count >= 1 else 0.33

        hits = [
            {
                "title": r.get("title", ""),
                "link": r.get("url", ""),
                "snippet": r.get("description", ""),
            }
            for r in web_results[:limit]
        ]

        return {
            "status": "success",
            "verdict": "SEAL",
            "results": data,
            "hits": hits,
            "result_count": hit_count,
            "witness_debug": {
                "human": True,
                "ai": True,
                "earth": True,
                "bridge": "firecrawl_search",
            },
            "metrics": {
                "f2_truth_score": round(f2, 4),
                "f3_earth_witness": round(f3, 4),
            },
        }

    async def scrape(
        self,
        url: str,
        formats: list[str] | None = None,
    ) -> dict[str, Any]:
        if not _FIRECRAWL_API_KEY:
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": "FIRECRAWL_API_KEY not set",
                "error_class": "config_missing",
                "results": None,
                "description": None,
                "metrics": {"f9_hantu_score": 0.0},
                "witness_debug": {
                    "human": True,
                    "ai": False,
                    "earth": False,
                    "bridge": "firecrawl_scrape",
                },
            }

        sanitized = await self._sanitize_url(url)
        if not sanitized:
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": "invalid URL after sanitization",
                "error_class": "invalid_input",
                "results": None,
                "description": None,
                "metrics": {"f9_hantu_score": 0.0},
                "witness_debug": {
                    "human": True,
                    "ai": False,
                    "earth": False,
                    "bridge": "firecrawl_scrape",
                },
            }

        client = self._get_client()
        payload: dict[str, Any] = {
            "url": sanitized,
            "formats": formats or ["markdown"],
        }
        try:
            resp = await client.post(
                f"{_FIRECRAWL_BASE_URL}/scrape",
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            logger.error("FirecrawlBridge.scrape failed: %s", exc)
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": str(exc),
                "error_class": "bridge_failure",
                "results": None,
                "description": None,
                "metrics": {"f9_hantu_score": 0.0},
                "witness_debug": {
                    "human": True,
                    "ai": False,
                    "earth": False,
                    "bridge": "firecrawl_scrape",
                },
            }

        if not data.get("success"):
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": data.get("error", "firecrawl returned success=false"),
                "error_class": "api_error",
                "results": data,
                "description": None,
                "metrics": {"f9_hantu_score": 0.0},
                "witness_debug": {
                    "human": True,
                    "ai": False,
                    "earth": False,
                    "bridge": "firecrawl_scrape",
                },
            }

        page_data = data.get("data", {})
        markdown = page_data.get("markdown", "")
        filtered, score = await self._f9_filter(markdown)
        verdict = "VOID" if score > 0.5 else "SEAL"

        return {
            "status": "success",
            "verdict": verdict,
            "results": data,
            "url": sanitized,
            "title": page_data.get("metadata", {}).get("title", ""),
            "description": filtered,
            "metrics": {
                "f9_hantu_score": round(score, 4),
                "description_length": len(filtered),
            },
            "witness_debug": {
                "human": True,
                "ai": True,
                "earth": True,
                "bridge": "firecrawl_scrape",
            },
        }


firecrawl_bridge = FirecrawlBridge()
