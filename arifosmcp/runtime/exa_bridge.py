"""
arifosmcp/runtime/exa_bridge.py — Exa REST API bridge for 111_SENSE

Wires exa__search and exa__contents into the canonical arifOS tool surface
via Exa REST API (https://api.exa.ai/).
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

_EXA_API_KEY = os.getenv("EXA_API_KEY", "")
_EXA_BASE_URL = os.getenv("EXA_BASE_URL", "https://api.exa.ai")


class ExaBridge:
    """
    Async HTTP bridge for Exa REST API.

    Tools: exa-search (web search with highlights/text/summary),
           exa-contents (URL content extraction).
    """

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=90.0,
                follow_redirects=True,
                headers={
                    "x-api-key": _EXA_API_KEY,
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
        num_results: int = 10,
        search_type: str = "auto",
        highlights: bool = True,
    ) -> dict[str, Any]:
        if not _EXA_API_KEY:
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": "EXA_API_KEY not set",
                "error_class": "config_missing",
                "results": None,
                "hits": [],
                "result_count": 0,
                "metrics": {"f2_truth_score": 0.99, "f3_earth_witness": 0.0},
                "witness_debug": {
                    "human": True,
                    "ai": True,
                    "earth": False,
                    "bridge": "exa_search",
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
                    "bridge": "exa_search",
                },
            }

        client = self._get_client()
        payload: dict[str, Any] = {
            "query": sanitized,
            "type": search_type,
            "num_results": num_results,
            "contents": {"highlights": highlights} if highlights else {},
        }

        try:
            resp = await client.post(f"{_EXA_BASE_URL}/search", json=payload)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            logger.error("ExaBridge.search failed: %s", exc)
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
                    "bridge": "exa_search",
                },
            }

        results = data.get("results", [])
        if not results:
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": "no results from exa",
                "error_class": "empty_results",
                "results": data,
                "hits": [],
                "result_count": 0,
                "metrics": {"f2_truth_score": 0.95, "f3_earth_witness": 0.7},
                "witness_debug": {
                    "human": True,
                    "ai": True,
                    "earth": False,
                    "bridge": "exa_search",
                },
            }

        hit_count = len(results)
        f2 = 0.99 if hit_count >= 5 else 0.95 if hit_count >= 1 else 0.33
        f3 = 0.95 if hit_count >= 5 else 0.7 if hit_count >= 1 else 0.33

        hits = []
        for r in results[:num_results]:
            highlights_list = r.get("highlights", [])
            snippet = ""
            if isinstance(highlights_list, list) and highlights_list:
                snippet = (
                    highlights_list[0][:500]
                    if isinstance(highlights_list[0], str)
                    else str(highlights_list[0])
                )
            elif isinstance(highlights_list, str):
                snippet = highlights_list[:500]
            else:
                snippet = r.get("text", "")[:500]
            hits.append(
                {
                    "title": r.get("title", ""),
                    "link": r.get("url", ""),
                    "snippet": snippet,
                }
            )

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
                "bridge": "exa_search",
            },
            "metrics": {
                "f2_truth_score": round(f2, 4),
                "f3_earth_witness": round(f3, 4),
            },
        }

    async def contents(
        self,
        urls: list[str],
        highlights: bool = True,
        text_max_chars: int | None = None,
    ) -> dict[str, Any]:
        if not _EXA_API_KEY:
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": "EXA_API_KEY not set",
                "error_class": "config_missing",
                "results": None,
                "extracted": [],
                "metrics": {"f9_hantu_score": 0.0},
                "witness_debug": {
                    "human": True,
                    "ai": False,
                    "earth": False,
                    "bridge": "exa_contents",
                },
            }

        sanitized_urls = []
        for url in urls[:20]:
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
                    "bridge": "exa_contents",
                },
            }

        client = self._get_client()
        payload: dict[str, Any] = {
            "urls": sanitized_urls,
            "highlights": highlights,
        }
        if text_max_chars:
            payload["text"] = {"maxCharacters": text_max_chars}

        try:
            resp = await client.post(f"{_EXA_BASE_URL}/contents", json=payload)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            logger.error("ExaBridge.contents failed: %s", exc)
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
                    "bridge": "exa_contents",
                },
            }

        results_list = data.get("results", [])
        extracted = []
        max_hantu = 0.0

        for r in results_list:
            text_content = r.get("text", "")
            filtered, score = await self._f9_filter(text_content)
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
            "results": data,
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
                "bridge": "exa_contents",
            },
        }


exa_bridge = ExaBridge()
