"""
arifosmcp/runtime/federation_bridge.py — WEALTH + WELL Federation Bridge

DITEMPA BUKAN DIBERI — Forged, Not Given

Bridges arifOS kernel to WEALTH and WELL organs via their public MCP endpoints.

WEALTH:   Stateless JSON — POST /mcp with Accept: application/json
WELL:     Sessionful SSE — POST /mcp with Accept: text/event-stream
          Requires initialize → get sessionId → use mcp-session-id header

Key distinction (FED-SSE-001 fix):
  WEALTH speaks JSON only (streamable-http with JSON response).
  WELL speaks SSE (text/event-stream) and REQUIRES a sessionId.
  GEOX speaks JSON (stateless) — handled by geox_bridge.py.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any

import httpx

logger = logging.getLogger("arifosmcp.federation_bridge")

# ── Endpoint defaults ─────────────────────────────────────────────────────────
WEALTH_HOST = "wealth.arif-fazil.com"
WEALTH_BASE = f"https://{WEALTH_HOST}"

WELL_HOST = "well.arif-fazil.com"
WELL_BASE = f"https://{WELL_HOST}"

# ── Session cache for WELL ──────────────────────────────────────────────────────
_WELL_SESSIONS: dict[str, float] = {}  # session_id → last_used_ts
_SESSION_TTL_SEC = 300  # 5 minutes


def _clean_expired_sessions() -> None:
    """Remove WELL sessions older than _SESSION_TTL_SEC."""
    now = time.time()
    for sid in list(_WELL_SESSIONS.keys()):
        if now - _WELL_SESSIONS[sid] > _SESSION_TTL_SEC:
            del _WELL_SESSIONS[sid]


async def _init_well_session() -> str:
    """
    Initialize a WELL session and return the sessionId.

    WELL requires:
      1. POST /mcp with initialize method
      2. Parse sessionId from SSE response header mcp-session-id
      3. Use mcp-session-id header on all subsequent calls
    """
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "arifOS-federation-bridge", "version": "1.0"},
        },
    }
    headers = {
        "Content-Type": "application/json",
        # BOTH required: WELL 406s without application/json even when using SSE
        "Accept": "application/json, text/event-stream",
    }

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        resp = await client.post(f"{WELL_BASE}/mcp", json=payload, headers=headers)
        if resp.status_code >= 400:
            raise ConnectionError(f"WELL initialize HTTP {resp.status_code}: {resp.text[:200]}")

        # Extract session ID from SSE content
        session_id = None
        # Check response headers
        session_id = resp.headers.get("mcp-session-id")

        # Also parse from SSE body for compatibility
        if not session_id:
            for line in resp.text.splitlines():
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        result = data.get("result", {})
                        session_id = result.get("sessionId")
                        if session_id:
                            break
                    except Exception:
                        pass

        if not session_id:
            raise ConnectionError("WELL initialize succeeded but no sessionId returned")

        return session_id


async def _get_well_session() -> str:
    """Get a valid WELL session, reusing existing or creating new."""
    _clean_expired_sessions()
    # Reuse most recent session if available
    if _WELL_SESSIONS:
        most_recent = max(_WELL_SESSIONS, key=_WELL_SESSIONS.get)
        if time.time() - _WELL_SESSIONS[most_recent] < _SESSION_TTL_SEC:
            return most_recent
    sid = await _init_well_session()
    _WELL_SESSIONS[sid] = time.time()
    return sid


async def _well_json_rpc(
    method: str,
    params: dict[str, Any],
    session_id: str | None = None,
) -> dict[str, Any]:
    """
    Send a JSON-RPC call to WELL and collect SSE response.

    Handles:
      - Automatic session creation (initialize)
      - SSE parsing (data: <json> lines)
      - JSON fallback
      - Error extraction
    """
    if not session_id:
        session_id = await _get_well_session()

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params,
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "mcp-session-id": session_id,
    }

    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        resp = await client.post(f"{WELL_BASE}/mcp", json=payload, headers=headers)
        if resp.status_code >= 400:
            # Session may have expired — retry with fresh session
            if resp.status_code == 400 and "session" in resp.text.lower():
                sid = await _init_well_session()
                _WELL_SESSIONS[sid] = time.time()
                headers["mcp-session-id"] = sid
                resp = await client.post(f"{WELL_BASE}/mcp", json=payload, headers=headers)
                if resp.status_code >= 400:
                    raise ConnectionError(f"WELL HTTP {resp.status_code}: {resp.text[:200]}")

        content_type = resp.headers.get("content-type", "")
        text = resp.text

        # Parse SSE or JSON
        if "text/event-stream" in content_type:
            buffer = ""
            for line in text.splitlines():
                if line.startswith("data: "):
                    buffer += line[6:]
                elif line.startswith("{") and not buffer:
                    buffer = line
            if not buffer:
                raise ConnectionError("WELL returned empty SSE stream")
            parsed = json.loads(buffer)
        else:
            parsed = json.loads(text)

        if parsed.get("error"):
            raise ConnectionError(f"WELL JSON-RPC error: {parsed['error']}")

        return parsed.get("result", {})


async def _wealth_json_rpc(
    method: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    """
    Send a JSON-RPC call to WEALTH.

    WEALTH responds with plain JSON (no SSE), even with Accept: application/json.
    Simple stateless POST — no session management required.
    """
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params,
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }

    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        resp = await client.post(f"{WEALTH_BASE}/mcp", json=payload, headers=headers)
        if resp.status_code >= 400:
            try:
                err = resp.json()
                msg = err.get("error", {}).get("message", resp.text[:200])
            except Exception:
                msg = resp.text[:200]
            raise ConnectionError(f"WEALTH HTTP {resp.status_code}: {msg}")

        parsed = resp.json()
        if parsed.get("error"):
            raise ConnectionError(f"WEALTH JSON-RPC error: {parsed['error']}")

        return parsed.get("result", {})


# ── Public API ─────────────────────────────────────────────────────────────────


async def call_wealth_tool(
    tool_name: str,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Call a WEALTH MCP tool by name with arguments.

    Example:
        result = await call_wealth_tool("wealth_sense_health", {})
    """
    result = await _wealth_json_rpc(
        "tools/call",
        {"name": tool_name, "arguments": arguments or {}},
    )
    return result


async def list_wealth_tools() -> list[dict[str, Any]]:
    """List all tools available from WEALTH MCP server."""
    result = await _wealth_json_rpc("tools/list", {})
    return result.get("tools", [])


async def wealth_health_check() -> dict[str, Any]:
    """Check WEALTH MCP server health."""
    try:
        await _wealth_json_rpc(
            "tools/call",
            {"name": "mcp_health_check", "arguments": {}},
        )
        return {"status": "healthy", "organ": "WEALTH", "host": WEALTH_HOST}
    except Exception as e:
        return {"status": "unhealthy", "organ": "WEALTH", "error": str(e)}


async def call_well_tool(
    tool_name: str,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Call a WELL MCP tool by name with arguments.

    Handles session management automatically.

    Example:
        result = await call_well_tool("well_state", {})
    """
    result = await _well_json_rpc(
        "tools/call",
        {"name": tool_name, "arguments": arguments or {}},
    )
    return result


async def list_well_tools() -> list[dict[str, Any]]:
    """List all tools available from WELL MCP server."""
    result = await _well_json_rpc("tools/list", {})
    return result.get("tools", [])


async def well_health_check() -> dict[str, Any]:
    """Check WELL MCP server health."""
    try:
        # well_state is a reliable lightweight tool
        await call_well_tool("well_state", {})
        return {"status": "healthy", "organ": "WELL", "host": WELL_HOST}
    except Exception as e:
        return {"status": "unhealthy", "organ": "WELL", "error": str(e)}


# ── Combined federation health ─────────────────────────────────────────────────
async def federation_health_all() -> dict[str, Any]:
    """Run health checks on all three federation organs in parallel."""

    w_health, g_health, well_health = await asyncio.gather(
        wealth_health_check(),
        _geox_fallback_health(),
        well_health_check(),
        return_exceptions=True,
    )
    return {
        "WEALTH": (
            w_health
            if not isinstance(w_health, Exception)
            else {"status": "error", "error": str(w_health)}
        ),
        "GEOX": (
            g_health
            if not isinstance(g_health, Exception)
            else {"status": "error", "error": str(g_health)}
        ),
        "WELL": (
            well_health
            if not isinstance(well_health, Exception)
            else {"status": "error", "error": str(well_health)}
        ),
    }


async def _geox_fallback_health() -> dict[str, Any]:
    """Health check for GEOX via simple HTTP (no SSE complexity)."""
    try:
        import httpx

        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                f"{WELL_BASE.rreplace('well.', 'geox.', 1)}/health",
                headers={"Accept": "application/json"},
            )
            if resp.status_code == 200:
                return {"status": "healthy", "organ": "GEOX"}
    except Exception:
        pass
    # Fallback to internal call
    try:
        result = await _well_json_rpc(
            "tools/call",
            {"name": "geox_system_registry_status", "arguments": {}},
        )
        return {"status": "healthy", "organ": "GEOX", "detail": result}
    except Exception as e:
        return {"status": "unhealthy", "organ": "GEOX", "error": str(e)}
