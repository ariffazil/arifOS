"""
arifosmcp/runtime/tavily_bridge.py — Tavily REST API bridge for 111_SENSE

Wires tavily__search into the canonical arifOS tool surface
via Tavily REST API (https://api.tavily.com/).
Falls back to MCP only when REST fails.

Tools (canonical surface, arif_sense_observe modes):
  tavily-search             — basic/advanced web search
  tavily-extract            — URL content extraction
  tavily-context            — RAG-ready joined context string (added 2026-06-16)
  tavily-qna                — one-shot LLM-curated Q&A answer (added 2026-06-16)
  tavily-crawl              — multi-page site traversal, invite-only (added 2026-06-16)
  tavily-map                — site structure discovery, URL list (added 2026-06-16)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx
from core.shared.laws import get_law_threshold

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

    # ──────────────────────────────────────────────────────────────────────
    # Phase 0 additions — 2026-06-16
    # Four new endpoints from the tavily-python SDK, exposed via the bridge
    # with the same F2/F7/F9 discipline as the canonical search/extract.
    # ──────────────────────────────────────────────────────────────────────

    async def _post_tavily(
        self,
        endpoint: str,
        payload: dict[str, Any],
        bridge_name: str,
    ) -> dict[str, Any]:
        """
        Shared POST helper. Returns the raw Tavily response dict, or an
        error envelope. Caller is responsible for shape, hits, verdict.
        """
        client = self._get_client()
        try:
            resp = await client.post(
                f"{_TAVILY_REST_URL}/{endpoint}",
                json=payload,
                headers={"Authorization": f"Bearer {_TAVILY_API_KEY}"},
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            body = exc.response.text[:200]
            logger.error(
                "Tavily REST %s HTTP %s: %s", endpoint, status, body
            )
            # 403 on /crawl or /map is expected for non-invited keys.
            invite_only = endpoint in ("crawl", "map") and status == 403
            return {
                "_bridge_error": True,
                "error": f"HTTP {status}: {body}",
                "error_class": "invite_only" if invite_only else "bridge_failure",
                "bridge": bridge_name,
                "invite_only_endpoint": invite_only,
                "invite_url": "https://crawl.tavily.com" if invite_only else None,
            }
        except Exception as exc:
            logger.error("TavilyMCPBridge.%s failed: %s", bridge_name, exc)
            return {
                "_bridge_error": True,
                "error": str(exc),
                "error_class": "bridge_failure",
                "bridge": bridge_name,
            }

    async def _missing_key_envelope(
        self,
        bridge_name: str,
        metrics: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Standard SABAR envelope when TAVILY_API_KEY is not set."""
        return {
            "status": "error",
            "verdict": "SABAR",
            "error": "TAVILY_API_KEY not set",
            "error_class": "config_missing",
            "bridge": bridge_name,
            "witness_debug": {
                "human": True,
                "ai": False,
                "earth": False,
            },
            "metrics": metrics or {"f2_truth_score": 0.0},
        }

    async def get_search_context(
        self,
        query: str,
        max_tokens: int = 4000,
    ) -> dict[str, Any]:
        """
        Tavily /search with RAG-ready joined context string.

        Returns a single concatenated context string suitable for direct
        LLM ingestion, plus the underlying hit list. F2 epistemic tag
        is INTERPRETATION — content is AI-curated, not raw fact.

        Args:
          query: Free-text search query.
          max_tokens: Rough token budget for the joined context
            (1 token ≈ 4 chars). Default 4000.
        """
        bridge_name = "tavily_get_search_context"
        if not _TAVILY_API_KEY:
            return await self._missing_key_envelope(bridge_name)

        sanitized = await self._sanitize_query(query)
        if not sanitized:
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": "empty query after sanitization",
                "error_class": "invalid_input",
                "bridge": bridge_name,
                "witness_debug": {"human": True, "ai": False, "earth": False},
                "metrics": {"f2_truth_score": 0.0},
            }

        raw = await self._post_tavily(
            "search",
            {
                "query": sanitized,
                "max_results": 10,
                "search_depth": "advanced",
                "include_answer": False,
            },
            bridge_name,
        )
        if raw.get("_bridge_error"):
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": raw.get("error", "unknown bridge failure"),
                "error_class": raw.get("error_class", "bridge_failure"),
                "bridge": bridge_name,
                "witness_debug": {"human": True, "ai": False, "earth": False},
                "metrics": {"f2_truth_score": 0.0},
            }

        results = raw.get("results", [])
        context_parts: list[str] = []
        for r in results:
            content = r.get("content", "")
            url = r.get("url", "")
            if content:
                context_parts.append(f"[Source: {url}]\n{content}")
        context = "\n\n".join(context_parts)

        # Rough truncation to token budget.
        max_chars = max(1, max_tokens) * 4
        truncated = False
        if len(context) > max_chars:
            context = context[:max_chars] + "..."
            truncated = True

        f2 = 0.95 if len(results) >= 5 else 0.85 if results else 0.33

        return {
            "status": "success",
            "verdict": "SEAL" if context else "SABAR",
            "epistemic_tag": "INTERPRETATION",  # F2: AI-curated, not OBSERVED
            "context": context,
            "context_length_chars": len(context),
            "context_length_tokens_est": len(context) // 4,
            "truncated": truncated,
            "max_tokens": max_tokens,
            "hits": [
                {
                    "title": r.get("title", ""),
                    "link": r.get("url", ""),
                    "snippet": r.get("content", ""),
                }
                for r in results
            ],
            "result_count": len(results),
            "witness_debug": {
                "human": True,
                "ai": True,
                "earth": True,
                "bridge": bridge_name,
            },
            "metrics": {
                "f2_truth_score": round(f2, 4),
                "f3_earth_witness": get_law_threshold("F3"),
                "f7_humility_band": 0.05,
            },
        }

    async def qna_search(
        self,
        query: str,
    ) -> dict[str, Any]:
        """
        Tavily /search with include_answer=True — one-shot Q&A.

        Returns the LLM-curated answer string plus the source list.
        F2 epistemic tag is INTERPRETATION — answer is LLM-generated.

        Args:
          query: Natural-language question.
        """
        bridge_name = "tavily_qna_search"
        if not _TAVILY_API_KEY:
            return await self._missing_key_envelope(bridge_name)

        sanitized = await self._sanitize_query(query)
        if not sanitized:
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": "empty query after sanitization",
                "error_class": "invalid_input",
                "bridge": bridge_name,
                "witness_debug": {"human": True, "ai": False, "earth": False},
                "metrics": {"f2_truth_score": 0.0},
            }

        raw = await self._post_tavily(
            "search",
            {
                "query": sanitized,
                "max_results": 5,
                "search_depth": "advanced",
                "include_answer": True,
            },
            bridge_name,
        )
        if raw.get("_bridge_error"):
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": raw.get("error", "unknown bridge failure"),
                "error_class": raw.get("error_class", "bridge_failure"),
                "bridge": bridge_name,
                "witness_debug": {"human": True, "ai": False, "earth": False},
                "metrics": {"f2_truth_score": 0.0},
            }

        answer = raw.get("answer")
        results = raw.get("results", [])
        f2 = 0.85 if answer else 0.55 if results else 0.20

        # F9 hantu scan on the answer text
        if answer:
            _filtered, hantu_score = await self._f9_filter(answer)
        else:
            hantu_score = 0.0

        verdict = "SEAL" if answer and hantu_score < 0.5 else "VOID" if hantu_score >= 0.5 else "SABAR"

        return {
            "status": "success",
            "verdict": verdict,
            "epistemic_tag": "INTERPRETATION",  # F2: LLM-curated answer
            "answer": answer,
            "follow_up_questions": raw.get("follow_up_questions"),
            "hits": [
                {
                    "title": r.get("title", ""),
                    "link": r.get("url", ""),
                    "snippet": r.get("content", ""),
                }
                for r in results
            ],
            "result_count": len(results),
            "witness_debug": {
                "human": True,
                "ai": True,
                "earth": bool(results),
                "bridge": bridge_name,
            },
            "metrics": {
                "f2_truth_score": round(f2, 4),
                "f9_hantu_score": round(hantu_score, 4),
                "f7_humility_band": 0.10,  # wider band for LLM-generated text
            },
        }

    async def crawl(
        self,
        url: str,
        max_depth: int = 2,
        limit: int = 20,
        instructions: str | None = None,
    ) -> dict[str, Any]:
        """
        Tavily /crawl — multi-page site traversal.

        NOTE: /crawl is invite-only as of 2026-06-16. Non-invited keys
        receive HTTP 403. Bridge returns a clear invite_only envelope
        with the request URL so the operator can request access.

        Args:
          url: Starting URL.
          max_depth: Maximum link depth to traverse.
          limit: Maximum pages to return.
          instructions: Natural-language focus instructions.
        """
        bridge_name = "tavily_crawl"
        if not _TAVILY_API_KEY:
            return await self._missing_key_envelope(bridge_name)

        try:
            sanitized_url = await self._sanitize_url(url)
        except ValueError as exc:
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": str(exc),
                "error_class": "invalid_input",
                "bridge": bridge_name,
                "witness_debug": {"human": True, "ai": False, "earth": False},
                "metrics": {"f2_truth_score": 0.0},
            }

        payload: dict[str, Any] = {
            "url": sanitized_url,
            "max_depth": max(1, min(int(max_depth), 5)),
            "limit": max(1, min(int(limit), 50)),
        }
        if instructions:
            payload["instructions"] = await self._sanitize_query(instructions)

        raw = await self._post_tavily("crawl", payload, bridge_name)
        if raw.get("_bridge_error"):
            envelope = {
                "status": "error",
                "verdict": "SABAR",
                "error": raw.get("error", "unknown bridge failure"),
                "error_class": raw.get("error_class", "bridge_failure"),
                "bridge": bridge_name,
                "witness_debug": {"human": True, "ai": False, "earth": False},
                "metrics": {"f2_truth_score": 0.0},
            }
            if raw.get("invite_only_endpoint"):
                envelope["invite_only"] = True
                envelope["invite_url"] = raw.get("invite_url")
                envelope["note"] = (
                    "Tavily /crawl is invite-only. Request access at "
                    "https://crawl.tavily.com and the bridge will activate."
                )
            return envelope

        pages = raw.get("results", [])
        return {
            "status": "success",
            "verdict": "SEAL" if pages else "SABAR",
            "epistemic_tag": "INTERPRETATION",  # F2: AI-extracted content
            "url": sanitized_url,
            "pages": pages,
            "page_count": len(pages),
            "witness_debug": {
                "human": True,
                "ai": True,
                "earth": bool(pages),
                "bridge": bridge_name,
            },
            "metrics": {
                "f2_truth_score": 0.85 if pages else 0.33,
                "f7_humility_band": 0.05,
            },
        }

    async def map_site(
        self,
        url: str,
        max_depth: int = 2,
        limit: int = 20,
        instructions: str | None = None,
    ) -> dict[str, Any]:
        """
        Tavily /map — site structure discovery (URL list only).

        Unlike /crawl, /map returns ONLY URLs — no content extraction.
        F2 epistemic tag is OBSERVED — the URL list is a graph signal,
        not LLM-curated prose.

        Args:
          url: Starting URL.
          max_depth: Maximum link depth to traverse.
          limit: Maximum URLs to return.
          instructions: Natural-language focus instructions.
        """
        bridge_name = "tavily_map"
        if not _TAVILY_API_KEY:
            return await self._missing_key_envelope(bridge_name)

        try:
            sanitized_url = await self._sanitize_url(url)
        except ValueError as exc:
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": str(exc),
                "error_class": "invalid_input",
                "bridge": bridge_name,
                "witness_debug": {"human": True, "ai": False, "earth": False},
                "metrics": {"f2_truth_score": 0.0},
            }

        payload: dict[str, Any] = {
            "url": sanitized_url,
            "max_depth": max(1, min(int(max_depth), 5)),
            "limit": max(1, min(int(limit), 50)),
        }
        if instructions:
            payload["instructions"] = await self._sanitize_query(instructions)

        raw = await self._post_tavily("map", payload, bridge_name)
        if raw.get("_bridge_error"):
            envelope = {
                "status": "error",
                "verdict": "SABAR",
                "error": raw.get("error", "unknown bridge failure"),
                "error_class": raw.get("error_class", "bridge_failure"),
                "bridge": bridge_name,
                "witness_debug": {"human": True, "ai": False, "earth": False},
                "metrics": {"f2_truth_score": 0.0},
            }
            if raw.get("invite_only_endpoint"):
                envelope["invite_only"] = True
                envelope["invite_url"] = raw.get("invite_url")
                envelope["note"] = (
                    "Tavily /map is invite-only. Request access at "
                    "https://crawl.tavily.com and the bridge will activate."
                )
            return envelope

        # /map returns a list of URL strings (or dicts, depending on Tavily version).
        results = raw.get("results", [])
        urls: list[str] = []
        for r in results:
            if isinstance(r, str):
                urls.append(r)
            elif isinstance(r, dict):
                u = r.get("url")
                if u:
                    urls.append(u)

        return {
            "status": "success",
            "verdict": "SEAL" if urls else "SABAR",
            "epistemic_tag": "OBSERVED",  # F2: URL list is a graph signal, not prose
            "url": sanitized_url,
            "urls": urls,
            "url_count": len(urls),
            "witness_debug": {
                "human": True,
                "ai": False,  # no AI curation
                "earth": bool(urls),
                "bridge": bridge_name,
            },
            "metrics": {
                "f2_truth_score": 0.95 if urls else 0.33,
                "f7_humility_band": 0.03,
            },
        }


tavily_bridge = TavilyMCPBridge()
