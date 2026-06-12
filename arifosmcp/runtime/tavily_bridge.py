"""
arifosmcp/runtime/tavily_bridge.py — Tavily REST API bridge for 111_SENSE

Wires tavily__search into the canonical arifOS tool surface
via Tavily REST API (https://api.tavily.com/).
Falls back to MCP only when REST fails.
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import os
from typing import Any

from core.shared.laws import get_law_threshold
import httpx

logger = logging.getLogger(__name__)

_TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
_TAVILY_REST_URL = os.getenv("TAVILY_REST_URL", "https://api.tavily.com")


class TavilyMCPBridge:
    """
    Async HTTP bridge for Tavily REST API.

    Primary: REST API (no session management needed).
    Tools: tavily-search (web search), tavily-extract (URL content extraction).
    """

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=60.0,
                follow_redirects=True,
                headers={
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
        max_results: int = 5,
        search_depth: str = "basic",
    ) -> dict[str, Any]:
        if not _TAVILY_API_KEY:
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": "TAVILY_API_KEY not set",
                "error_class": "config_missing",
                "results": None,
                "hits": [],
                "result_count": 0,
                "metrics": {"f2_truth_score": 0.99, "f3_earth_witness": 0.0},
                "witness_debug": {
                    "human": True,
                    "ai": True,
                    "earth": False,
                    "bridge": "tavily_search",
                },
            }

        sanitized_query = await self._sanitize_query(query)
        if not sanitized_query:
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
                    "bridge": "tavily_search",
                },
            }

        client = self._get_client()
        try:
            resp = await client.post(
                f"{_TAVILY_REST_URL}/search",
                json={
                    "query": sanitized_query,
                    "max_results": max_results,
                    "search_depth": search_depth,
                },
                headers={"Authorization": f"Bearer {_TAVILY_API_KEY}"},
            )
            resp.raise_for_status()
            raw = resp.json()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Tavily REST HTTP error: %s %s", exc.response.status_code, exc.response.text
            )
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": f"HTTP {exc.response.status_code}: {exc.response.text[:200]}",
                "error_class": "bridge_failure",
                "results": None,
                "hits": [],
                "result_count": 0,
                "metrics": {"f2_truth_score": 0.99, "f3_earth_witness": 0.0},
                "witness_debug": {
                    "human": True,
                    "ai": True,
                    "earth": False,
                    "bridge": "tavily_search",
                },
            }
        except Exception as exc:
            logger.error("TavilyMCPBridge.search failed: %s", exc)
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
                    "bridge": "tavily_search",
                },
            }

        results = raw.get("results", [])
        if not results:
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": "no results from tavily",
                "error_class": "empty_results",
                "results": raw,
                "hits": [],
                "result_count": 0,
                "metrics": {"f2_truth_score": 0.95, "f3_earth_witness": get_law_threshold("F3")},
                "witness_debug": {
                    "human": True,
                    "ai": True,
                    "earth": False,
                    "bridge": "tavily_search",
                },
            }

        hit_count = len(results)
        f2 = 0.99 if hit_count >= 5 else 0.95 if hit_count >= 1 else 0.33
        f3 = 0.95 if hit_count >= 5 else get_law_threshold("F3") if hit_count >= 1 else 0.33

        hits = [
            {
                "title": r.get("title", ""),
                "link": r.get("url", ""),
                "snippet": r.get("content", ""),
            }
            for r in results[:max_results]
        ]

        return {
            "status": "success",
            "verdict": "SEAL",
            "results": raw,
            "answer": raw.get("answer"),
            "hits": hits,
            "result_count": hit_count,
            "witness_debug": {
                "human": True,
                "ai": True,
                "earth": True,
                "bridge": "tavily_search",
            },
            "metrics": {
                "f2_truth_score": round(f2, 4),
                "f3_earth_witness": round(f3, 4),
            },
        }

    async def extract(
        self,
        urls: list[str],
        prompt: str | None = None,
    ) -> dict[str, Any]:
        if not _TAVILY_API_KEY:
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": "TAVILY_API_KEY not set",
                "error_class": "config_missing",
                "results": None,
                "extracted": [],
                "metrics": {"f9_hantu_score": 0.0},
                "witness_debug": {
                    "human": True,
                    "ai": False,
                    "earth": False,
                    "bridge": "tavily_extract",
                },
            }

        sanitized_urls = []
        for url in urls[:10]:
            try:
                sanitized_urls.append(await self._sanitize_url(url))
            except ValueError:
                pass

        if not sanitized_urls:
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": "no valid URLs after sanitization",
                "error_class": "invalid_input",
                "results": None,
                "extracted": [],
                "metrics": {"f9_hantu_score": 0.0},
                "witness_debug": {
                    "human": True,
                    "ai": False,
                    "earth": False,
                    "bridge": "tavily_extract",
                },
            }

        client = self._get_client()
        payload: dict[str, Any] = {
            "urls": sanitized_urls,
        }
        if prompt:
            payload["prompt"] = await self._sanitize_query(prompt)

        try:
            resp = await client.post(
                f"{_TAVILY_REST_URL}/extract",
                json=payload,
                headers={"Authorization": f"Bearer {_TAVILY_API_KEY}"},
            )
            resp.raise_for_status()
            raw = resp.json()
        except Exception as exc:
            logger.error("TavilyMCPBridge.extract failed: %s", exc)
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": str(exc),
                "error_class": "bridge_failure",
                "results": None,
                "extracted": [],
                "metrics": {"f9_hantu_score": 0.0},
                "witness_debug": {
                    "human": True,
                    "ai": False,
                    "earth": False,
                    "bridge": "tavily_extract",
                },
            }

        raw_results = raw.get("results", [])
        extracted = []
        max_hantu = 0.0

        for r in raw_results:
            content = r.get("raw_content", r.get("content", ""))
            filtered, score = await self._f9_filter(content)
            max_hantu = max(max_hantu, score)
            extracted.append(
                {
                    "url": r.get("url", ""),
                    "title": r.get("title", ""),
                    "content": filtered,
                    "hantu_score": score,
                }
            )

        verdict = "VOID" if max_hantu > 0.5 else "SEAL"

        return {
            "status": "success",
            "verdict": verdict,
            "results": raw,
            "extracted": extracted,
            "result_count": len(extracted),
            "metrics": {
                "f9_hantu_score": round(max_hantu, 4),
                "description_length": sum(len(e["content"]) for e in extracted),
            },
            "witness_debug": {
                "human": True,
                "ai": True,
                "earth": True,
                "bridge": "tavily_extract",
            },
        }


tavily_bridge = TavilyMCPBridge()
