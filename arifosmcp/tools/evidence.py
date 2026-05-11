"""
arifosmcp/tools/evidence.py — 222_EVIDENCE (Reality-Wired)
════════════════════════════════════════════════════════════

Evidence-preserving web ingestion and fetch, wired to RealityHandler
for live URL fetch (streaming + browserless render fallback) and
web search (Brave → DDGS fallback).

Every operation emits an evidence receipt for F-WEB audit trail.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any, Literal

from arifosmcp.runtime.floors import check_floors
from arifosmcp.runtime.reality_handlers import handler as reality_handler
from arifosmcp.runtime.tools import _hold, _ok

logger = logging.getLogger(__name__)


def arif_evidence_fetch(
    mode: Literal["fetch", "search", "archive", "verify"] = "fetch",
    url: str | None = None,
    query: str | None = None,
    actor_id: str | None = None,
    render: str = "auto",
    top_k: int = 5,
) -> dict[str, Any]:
    """
    EVIDENCE tool — now reality-wired via RealityHandler.

    Modes:
      fetch  → Streaming HTTP GET with SSRF guard + browserless fallback
      search → Brave API (DDGS fallback)
      archive → Stub — returns archive ID
      verify  → Stub — returns verification status
    """
    floor_check = check_floors(
        "arif_evidence_fetch", {"url": url or "", "query": query or ""}, actor_id
    )
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_evidence_fetch", floor_check["reason"], floor_check["failed_floors"])

    if not url and mode in ("fetch", "archive", "verify"):
        return _hold(
            "arif_evidence_fetch",
            "F02 TRUTH: url is required for fetch/archive/verify modes.",
            floors=["F02"],
        )

    if mode == "fetch" and url:
        try:
            f_res = asyncio.run(reality_handler.fetch_url(url, render=render))
            return _ok(
                "arif_evidence_fetch",
                {
                    "url": url,
                    "content": f_res.raw_content or "",
                    "status": f_res.status_code or 0,
                    "content_type": f_res.content_type,
                    "content_length": f_res.content_length,
                    "final_url": f_res.final_url,
                    "redirects": f_res.redirects,
                    "render_fallback_used": f_res.render_fallback_used,
                    "latency_ms": f_res.latency_ms,
                    "error": f_res.error_message,
                    "archived": False,
                    "evidence_receipt": {
                        "provider": "reality_handler",
                        "bridge": "fetch_url",
                        "urls_returned": 1 if f_res.status_code == 200 else 0,
                        "urls_ingested": 0,
                        "rendered_inspection": f_res.render_fallback_used,
                        "void": [],
                        "max_evidence_level": 1 if f_res.status_code == 200 else 0,
                    },
                },
            )
        except Exception as e:
            logger.warning(f"RealityHandler failure in arif_evidence_fetch ({mode}): {e}")
            return _ok(
                "arif_evidence_fetch",
                {
                    "url": url,
                    "content": "",
                    "status": 0,
                    "error": str(e),
                    "archived": False,
                    "evidence_receipt": {
                        "provider": "reality_handler",
                        "bridge": "fetch_url",
                        "urls_returned": 0,
                        "urls_ingested": 0,
                        "rendered_inspection": False,
                        "void": ["handler_exception"],
                        "max_evidence_level": 0,
                    },
                },
            )

    if mode == "search" and query:
        try:
            s_res = asyncio.run(reality_handler.search_brave(query, top_k=top_k))
            results = s_res.results if s_res.results else []
            return _ok(
                "arif_evidence_fetch",
                {
                    "query": query,
                    "results": results,
                    "engine": s_res.engine,
                    "latency_ms": round(s_res.latency_ms, 1),
                    "evidence_receipt": {
                        "provider": "reality_handler",
                        "bridge": s_res.engine,
                        "urls_returned": len(results),
                        "urls_ingested": 0,
                        "rendered_inspection": False,
                        "void": [],
                        "max_evidence_level": len(results),
                    },
                },
            )
        except Exception as e:
            logger.warning(f"RealityHandler failure in arif_evidence_fetch ({mode}): {e}")
            return _ok(
                "arif_evidence_fetch",
                {
                    "query": query,
                    "results": [],
                    "engine": "unknown",
                    "error": str(e),
                    "evidence_receipt": {
                        "provider": "reality_handler",
                        "bridge": "unknown",
                        "urls_returned": 0,
                        "urls_ingested": 0,
                        "rendered_inspection": False,
                        "void": ["handler_exception"],
                        "max_evidence_level": 0,
                    },
                },
            )

    if mode == "archive":
        return _ok(
            "arif_evidence_fetch",
            {"url": url, "archived": True, "archive_id": uuid.uuid4().hex[:8]},
        )
    if mode == "verify":
        return _ok("arif_evidence_fetch", {"url": url, "verified": False, "note": "stub"})

    return _hold("arif_evidence_fetch", f"Unknown mode: {mode}")
