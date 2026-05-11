"""
arifosmcp/runtime/wealth_bridge.py — WEALTH SSE MCP Client Bridge

DITEMPA BUKAN DIBERI — Forged, Not Given

Bridges arifOS kernel (port 8080) to WEALTH organ (port 8082) via SSE + JSON-RPC POST.
WEALTH FastMCP uses StreamableHTTP with server-generated session IDs.

Protocol (MCP StreamableHTTP):
1. Client sends POST with X-MCP-Session-ID header (any UUID)
2. Server responds with its OWN session ID in mcp-session-id response header
3. Client MUST use the server's session ID for all subsequent calls
4. Each POST is a new HTTP request; SSE events contain responses
"""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

logger = logging.getLogger("arifosmcp.wealth_bridge")

WEALTH_HOST = "wealth-organ"
WEALTH_PORT = 8082
WEALTH_BASE = f"http://{WEALTH_HOST}:{WEALTH_PORT}"

_WEALTH_SESSION_ID: str | None = None


async def _ensure_session() -> str:
    """Establish or reuse a WEALTH session ID."""
    global _WEALTH_SESSION_ID
    if _WEALTH_SESSION_ID is not None:
        return _WEALTH_SESSION_ID

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        resp = await client.post(
            f"{WEALTH_BASE}/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "arifOS-kernel", "version": "1.0"},
                },
            },
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
        )

        if resp.status_code != 200:
            raise ConnectionError(
                f"WEALTH session init failed: {resp.status_code} {resp.text[:200]}"
            )

        server_session = resp.headers.get("mcp-session-id")
        if not server_session:
            raise ConnectionError("WEALTH did not return mcp-session-id header")

        async for _ in resp.aiter_lines():
            pass

        _WEALTH_SESSION_ID = server_session
        logger.info(f"WEALTH session established: {server_session}")
        return server_session


async def _post_json_rpc(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Send a JSON-RPC request to WEALTH using the established session.
    """
    session_id = await _ensure_session()

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        resp = await client.post(
            f"{WEALTH_BASE}/mcp",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "x-mcp-session-id": session_id,
                "mcp-session-id": session_id,
            },
        )

        if resp.status_code == 406:
            raise ConnectionError("WEALTH 406: Accept header issue")

        if resp.status_code >= 400:
            try:
                err_data = resp.json()
                msg = err_data.get("error", {}).get("message", resp.text[:200])
            except Exception:
                msg = resp.text[:200]
            raise ConnectionError(f"WEALTH HTTP {resp.status_code}: {msg}")

        buffer = b""
        async for line in resp.aiter_lines():
            if line.startswith("data: "):
                buffer += line[6:].encode()

        if not buffer:
            raise ConnectionError("WEALTH returned empty SSE response")

        parsed = json.loads(buffer)
        if parsed.get("error"):
            raise ConnectionError(f"WEALTH JSON-RPC error: {parsed['error']}")

        return parsed.get("result", {})


async def call_wealth_tool(
    tool_name: str,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Call a WEALTH MCP tool by name with arguments.

    Example:
        result = await call_wealth_tool("wealth_npv_rank", {
            "cashflows": [...],
            "discount_rate": 0.12
        })
    """
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments or {},
        },
    }
    result = await _post_json_rpc(payload)
    return result


async def list_wealth_tools() -> list[dict[str, Any]]:
    """List all tools available from WEALTH MCP server."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {},
    }
    result = await _post_json_rpc(payload)
    return result.get("tools", [])


async def wealth_health_check() -> dict[str, Any]:
    """Check WEALTH server health via MCP ping."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "ping",
        "params": {},
    }
    try:
        await _post_json_rpc(payload)
        return {"status": "healthy", "organ": "WEALTH", "host": WEALTH_HOST}
    except Exception as e:
        return {"status": "unhealthy", "organ": "WEALTH", "error": str(e)}


def reset_session() -> None:
    """Reset the cached session ID (for testing or reconnection)."""
    global _WEALTH_SESSION_ID
    _WEALTH_SESSION_ID = None
