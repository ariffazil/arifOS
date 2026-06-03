"""
arifosmcp/runtime/l5_graphiti_bridge.py
═══════════════════════════════════════════════════════════════════════════
555_MEMORY → L5 (Graphiti) bridge.

PURPOSE
-------
arif_memory_recall already dual-writes to L3 (Qdrant) + L4 (Supabase).
This module adds the THIRD leg of the federation: L5 (Graphiti entity graph).

PHILOSOPHY
----------
- Fire-and-forget. L5 must NEVER block L3/L4 success. L5 is enrichment.
- Best-effort. If Graphiti is down, log + continue. Memory is still in L3+L4.
- Per-session entity isolation via Graphiti group_id = "af_forge".
- Reuses the F4 entity_tags already extracted by memory_store (regex_fallback).

CALLER
------
memory_store.store() calls `bridge_forge_episode(...)` after a successful
Qdrant write and before returning the store result to the caller.

REVERSIBILITY
-------------
- All calls are fire-and-forget HTTP POSTs. No local state.
- Removing the import + call from memory_store.store() = full rollback.
- Graphiti episodes are individually deleteable via `delete_episode(uuid)`.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
import uuid
from typing import Any

logger = logging.getLogger(__name__)

# ── Configuration ──────────────────────────────────────────────────────────
_GRAPHITI_URL = os.getenv("GRAPHITI_MCP_URL", "http://localhost:8000")
_GRAPHITI_GROUP_ID = os.getenv("GRAPHITI_GROUP_ID", "af_forge")
_GRAPHITI_TIMEOUT_S = float(os.getenv("GRAPHITI_TIMEOUT_S", "2.0"))
_GRAPHITI_ENABLED = os.getenv("GRAPHITI_L5_ENABLED", "true").lower() == "true"


# ── Entity extraction (lightweight, F4-style regex) ──────────────────────
_FILE_PATTERN = re.compile(
    r"\b([a-zA-Z_][\w/\-]*\.(py|html|js|ts|tsx|json|yaml|yml|md|toml|sh|cfg|env))\b"
)
_PATH_PATTERN = re.compile(r"\b(/root/[\w/\-.]+|/etc/[\w/\-.]+)\b")
# Stop-words that look like files but aren't
_FILE_BLACKLIST = {"index.json", ".qdrant_index.json", "requirements.txt"}


def _extract_entities(text: str, tags: list[str] | None) -> dict[str, list[str]]:
    """Pull lightweight entities out of memory text for L5 episode body."""
    if not text:
        return {}

    files: set[str] = set()
    paths: set[str] = set()
    for m in _FILE_PATTERN.finditer(text):
        f = m.group(1)
        if f.lower() not in _FILE_BLACKLIST:
            files.add(f)
    for m in _PATH_PATTERN.finditer(text):
        paths.add(m.group(1))

    return {
        "files": sorted(files)[:25],
        "paths": sorted(paths)[:10],
        "tags": (tags or [])[:20],
    }


def _build_episode_body(
    *,
    memory_id: str,
    content: str,
    summary: str | None,
    session_id: str | None,
    actor_id: str | None,
    tier: str | None,
    tags: list[str] | None,
    l3_point_id: str | None,
    l4_row_id: str | None,
    phoenix_id: str | None,
    entity_tags: list[str] | None,
    phoenix_state: str | None,
) -> str:
    """Build a structured JSON episode body for Graphiti."""
    extracted = _extract_entities(content, tags)
    episode = {
        "memory_id": memory_id,
        "session_id": session_id,
        "actor_id": actor_id,
        "tier": tier,
        "summary": summary or (content[:160] if content else ""),
        "content": content,
        "tags": tags or [],
        "extracted_entities": extracted,
        "f4_entity_tags": entity_tags or [],
        "phoenix_id": phoenix_id,
        "phoenix_state": phoenix_state,
        "cross_refs": {
            "l3_qdrant_point": l3_point_id,
            "l4_pg_row": l4_row_id,
        },
        "federation_leg": "L5",
        "forge_ts": int(time.time()),
    }
    return json.dumps(episode, ensure_ascii=False)


# ── Public API ─────────────────────────────────────────────────────────────
def bridge_forge_episode(
    *,
    memory_id: str,
    content: str,
    summary: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    tier: str | None = None,
    tags: list[str] | None = None,
    l3_point_id: str | None = None,
    l4_row_id: str | None = None,
    phoenix_id: str | None = None,
    entity_tags: list[str] | None = None,
    phoenix_state: str | None = None,
    name: str | None = None,
) -> dict[str, Any]:
    """Fire-and-forget L5 Graphiti episode forge.

    Returns a status dict. NEVER raises. Logged + swallowed.
    """
    if not _GRAPHITI_ENABLED:
        return {"federation_leg": "L5", "status": "disabled", "memory_id": memory_id}

    if not content:
        return {"federation_leg": "L5", "status": "skipped", "reason": "empty_content"}

    try:
        import httpx  # noqa: PLC0415
    except ImportError:
        return {"federation_leg": "L5", "status": "skipped", "reason": "httpx_unavailable"}

    body = _build_episode_body(
        memory_id=memory_id,
        content=content,
        summary=summary,
        session_id=session_id,
        actor_id=actor_id,
        tier=tier,
        tags=tags,
        l3_point_id=l3_point_id,
        l4_row_id=l4_row_id,
        phoenix_id=phoenix_id,
        entity_tags=entity_tags,
        phoenix_state=phoenix_state,
    )

    episode_name = name or f"memory:{memory_id[:12]}:{(summary or content)[:60].strip()}"
    payload = {
        "jsonrpc": "2.0",
        "id": int(time.time() * 1000) % 1000000,
        "method": "tools/call",
        "params": {
            "name": "add_memory",
            "arguments": {
                "name": episode_name,
                "episode_body": body,
                "group_id": _GRAPHITI_GROUP_ID,
                "source": "json",
                "source_description": (
                    f"arifOS federation L5 forge — memory_id={memory_id} "
                    f"session={session_id or 'unknown'}"
                ),
            },
        },
    }

    try:
        # Two-step Graphiti MCP: initialize → call (session-id is returned)
        sid = _ensure_session()
        if not sid:
            return {"federation_leg": "L5", "status": "skipped", "reason": "no_session"}
        with httpx.Client(timeout=_GRAPHITI_TIMEOUT_S) as client:
            r = client.post(
                f"{_GRAPHITI_URL}/mcp",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                    "mcp-session-id": sid,
                },
            )
            ok = r.status_code == 200
            return {
                "federation_leg": "L5",
                "status": "queued" if ok else "deferred",
                "http_status": r.status_code,
                "memory_id": memory_id,
                "graphiti_group_id": _GRAPHITI_GROUP_ID,
            }
    except Exception as exc:  # pragma: no cover — fire-and-forget
        logger.warning("L5 Graphiti forge skipped: %s", exc)
        return {
            "federation_leg": "L5",
            "status": "skipped",
            "reason": f"{type(exc).__name__}",
            "memory_id": memory_id,
        }


# ── Session cache (Graphiti MCP needs mcp-session-id) ─────────────────────
_SESSION_ID: str | None = None
_SESSION_TS: float = 0.0
_SESSION_TTL_S = 300.0  # re-init every 5 min


def _ensure_session() -> str | None:
    """Ensure we have a fresh Graphiti MCP session-id."""
    global _SESSION_ID, _SESSION_TS
    now = time.time()
    if _SESSION_ID and (now - _SESSION_TS) < _SESSION_TTL_S:
        return _SESSION_ID
    try:
        import httpx  # noqa: PLC0415

        with httpx.Client(timeout=_GRAPHITI_TIMEOUT_S) as client:
            r = client.post(
                f"{_GRAPHITI_URL}/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2025-03-26",
                        "capabilities": {},
                        "clientInfo": {"name": "arifOS-federation", "version": "0.1"},
                    },
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                },
            )
            sid = r.headers.get("mcp-session-id")
            if sid:
                _SESSION_ID = sid
                _SESSION_TS = now
                return sid
    except Exception as exc:
        logger.debug("Graphiti session init failed: %s", exc)
    return None


def bridge_search(
    query: str,
    *,
    group_ids: list[str] | None = None,
    max_nodes: int = 10,
) -> dict[str, Any]:
    """Query L5 entity graph. Wraps Graphiti search_nodes."""
    if not _GRAPHITI_ENABLED:
        return {"status": "disabled", "nodes": []}
    try:
        import httpx  # noqa: PLC0415

        sid = _ensure_session()
        if not sid:
            return {"status": "no_session", "nodes": []}
        with httpx.Client(timeout=_GRAPHITI_TIMEOUT_S) as client:
            r = client.post(
                f"{_GRAPHITI_URL}/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": int(time.time() * 1000) % 1000000,
                    "method": "tools/call",
                    "params": {
                        "name": "search_nodes",
                        "arguments": {
                            "query": query,
                            "group_ids": group_ids or [_GRAPHITI_GROUP_ID],
                            "max_nodes": max_nodes,
                        },
                    },
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                    "mcp-session-id": sid,
                },
            )
            return {
                "status": "ok" if r.status_code == 200 else "degraded",
                "http_status": r.status_code,
                "raw": r.text[:800],
            }
    except Exception as exc:
        return {"status": "skipped", "reason": f"{type(exc).__name__}: {exc}"}
