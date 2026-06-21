"""
arifosmcp/tools/chatgpt_shim.py — ChatGPT Discovery Shim (Hardened)
═══════════════════════════════════════════════════════════════════════

Two thin tools that satisfy ChatGPT's mandatory search/fetch discovery
requirement without touching kernel logic. Routes internally to the
canonical arif_sense_observe and arif_evidence_fetch handlers.

ART ALIGNMENT:
  Both tools are OBSERVE-class (action_class="observe", blast_radius="low").
  ART Check 1 (POWER): no mutation, no actor required, read-only.
  ART Check 2 (TRUST): returns raw evidence, no charisma markers.
  ART Check 3 (STATE): degraded system → DEFAULT_OBSERVE (same as parent).

ACT ALIGNMENT:
  Both are single-call programs. They compose into any ACT sequence
  as atomic observation stages. No multi-call ceremony needed.

CONSTITUTIONAL FLOORS:
  arif_search  → L02 (TRUTH), L07 (HUMILITY)
  arif_fetch   → L02 (TRUTH), L03 (WITNESS), L05 (PEACE), L12 (INJECTION)

MCP ANNOTATIONS (derived from OBSERVE action_class):
  readOnlyHint: true, destructiveHint: false,
  idempotentHint: true, openWorldHint: true

SCHEMA CONTRACT (OpenAI-compliant):
  Single-string params. No anyOf, no optional-heavy unions.
  Stable output keys: results/sources/content/status/query_used/canonical_url.

CONDITIONAL REGISTRATION:
  Only registered when ARIFOS_CHATGPT_COMPAT=true.

PERSISTENCE CONTRACT:
  search = never persists. Returns results only.
  fetch  = never persists by default. Returns content only.
         Set persist=True to route through evidence_fetch ingest mode.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


# ── Output schemas (OpenAI-compliant, stable keys) ────────────────────────────
# These schemas are declared so ChatGPT can parse structured output.
# Keys match what the parent tools actually return.

SEARCH_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "description": "ok | error | degraded"},
        "tool": {"type": "string"},
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "url": {"type": "string"},
                    "snippet": {"type": "string"},
                },
            },
            "description": "Search result list.",
        },
        "query_used": {"type": "string", "description": "The query that was executed."},
        "result_count": {"type": "integer"},
        "sources": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Source URLs.",
        },
    },
    "required": ["status", "tool"],
}

FETCH_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "description": "ok | error | degraded"},
        "tool": {"type": "string"},
        "content": {"type": "string", "description": "Fetched page content as text."},
        "canonical_url": {"type": "string", "description": "Final URL after redirects."},
        "content_type": {"type": "string", "description": "MIME type of the response."},
        "fetch_status": {"type": "string", "description": "success | timeout | blocked | error"},
    },
    "required": ["status", "tool"],
}


# ── Handler implementations ───────────────────────────────────────────────────
# Thin wrappers that delegate to the real kernel handlers.
# Accept **kwargs to tolerate client _meta injection (OpenAI Apps SDK).


async def arif_search(
    query: str,
    _envelope: dict[str, Any] | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """ChatGPT-compatible search shim → arif_sense_observe(mode=search).

    Read-only, open-world, idempotent. Never persists.
    Returns search results with titles, URLs, and snippets.
    """
    from arifosmcp.runtime.tools import _CANONICAL_HANDLERS

    handler = _CANONICAL_HANDLERS.get("arif_sense_observe")
    if handler is None:
        return {
            "status": "error",
            "tool": "arif_search",
            "results": [],
            "query_used": query,
            "error": "arif_sense_observe handler not available",
        }

    try:
        result = await handler(
            mode="search",
            query=query,
            _envelope=_envelope,
            actor_id=actor_id,
            session_id=session_id,
        )
        # Normalize to stable output keys
        if isinstance(result, dict):
            result.setdefault("tool", "arif_search")
            result.setdefault("query_used", query)
        return result
    except Exception as e:
        logger.warning("arif_search failed: %s", e, exc_info=True)
        return {
            "status": "error",
            "tool": "arif_search",
            "results": [],
            "query_used": query,
            "error": str(e),
        }


async def arif_fetch(
    url: str,
    persist: bool = False,
    _envelope: dict[str, Any] | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """ChatGPT-compatible fetch shim → arif_evidence_fetch(mode=fetch).

    Read-only, open-world, idempotent. Never persists by default.
    Returns page content as text with canonical URL.

    Set persist=True to route through evidence_fetch ingest mode
    (governed, requires session).
    """
    from arifosmcp.runtime.tools import _CANONICAL_HANDLERS

    # Default: fetch-only (no persistence). If persist=True, use ingest mode.
    mode = "ingest" if persist else "fetch"

    handler = _CANONICAL_HANDLERS.get("arif_evidence_fetch")
    if handler is None:
        return {
            "status": "error",
            "tool": "arif_fetch",
            "content": "",
            "canonical_url": url,
            "fetch_status": "error",
            "error": "arif_evidence_fetch handler not available",
        }

    try:
        result = await handler(
            mode=mode,
            url=url,
            _envelope=_envelope,
            actor_id=actor_id,
            session_id=session_id,
        )
        # Normalize to stable output keys
        if isinstance(result, dict):
            result.setdefault("tool", "arif_fetch")
            result.setdefault("canonical_url", url)
        return result
    except Exception as e:
        logger.warning("arif_fetch failed: %s", e, exc_info=True)
        return {
            "status": "error",
            "tool": "arif_fetch",
            "content": "",
            "canonical_url": url,
            "fetch_status": "error",
            "error": str(e),
        }


# ── Handler/schema map for registration ───────────────────────────────────────

SHIM_HANDLERS: dict[str, Any] = {
    "arif_search": arif_search,
    "arif_fetch": arif_fetch,
}

SHIM_OUTPUT_SCHEMAS: dict[str, dict[str, Any]] = {
    "arif_search": SEARCH_OUTPUT_SCHEMA,
    "arif_fetch": FETCH_OUTPUT_SCHEMA,
}

# ── Tool definitions (for registration metadata) ──────────────────────────────

SHIM_TOOLS: dict[str, dict[str, Any]] = {
    "arif_search": {
        "name": "arif_search",
        "description": (
            "Search the web for information. Use when you need to find current "
            "facts, documentation, or real-world data. Returns search results "
            "with titles, URLs, and snippets."
        ),
        "routes_to": "arif_sense_observe",
        "route_mode": "search",
    },
    "arif_fetch": {
        "name": "arif_fetch",
        "description": (
            "Fetch content from a URL. Use when you need to read the contents "
            "of a specific webpage or document. Returns the page content as text."
        ),
        "routes_to": "arif_evidence_fetch",
        "route_mode": "fetch",
    },
}
