"""
arifosmcp/runtime/geox_bridge.py — GEOX SSE MCP Client Bridge

DITEMPA BUKAN DIBERI — Forged, Not Given

Bridges arifOS kernel (port 8080) to GEOX organ (port 8081) via SSE + JSON-RPC POST.
The GEOX FastMCP server uses StreamableHTTP with SSE responses.

Pattern:
1. POST JSON-RPC to /mcp with Accept: text/event-stream
2. Server responds with SSE stream (event: message, data: <json>)
3. Parse SSE events to extract JSON-RPC responses
"""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

logger = logging.getLogger("arifosmcp.geox_bridge")

GEOX_HOST = "geox_eic"
GEOX_PORT = 8081
GEOX_BASE = f"http://{GEOX_HOST}:{GEOX_PORT}"


async def _post_json_rpc(endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
    """
    Send a JSON-RPC request to GEOX and collect SSE response events.

    Returns the parsed JSON-RPC result dict.
    Raises on error responses.
    """
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        resp = await client.post(
            f"{GEOX_BASE}{endpoint}",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
        )

        if resp.status_code == 406:
            raise ConnectionError(
                "GEOX 406: Client must accept both application/json and text/event-stream. "
                "Check FastMCP transport configuration."
            )

        if resp.status_code >= 400:
            # Try to parse error from JSON body
            try:
                err_data = resp.json()
                msg = err_data.get("error", {}).get("message", resp.text[:200])
            except Exception:
                msg = resp.text[:200]
            raise ConnectionError(f"GEOX HTTP {resp.status_code}: {msg}")

        # Collect all SSE data: lines starting with "data: "
        buffer = b""
        async for line in resp.aiter_lines():
            if line.startswith("data: "):
                buffer += line[6:].encode()

        if not buffer:
            raise ConnectionError("GEOX returned empty SSE response")

        parsed = json.loads(buffer)
        if parsed.get("error"):
            raise ConnectionError(f"GEOX JSON-RPC error: {parsed['error']}")

        return parsed.get("result", {})


async def call_geox_tool(
    tool_name: str,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Call a GEOX MCP tool by name with arguments.

    Example:
        result = await call_geox_tool("geox_well_compute_petrophysics", {
            "well_id": "WELL_001",
            "computation": "rhob",
            "params": {}
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
    result = await _post_json_rpc("/mcp", payload)
    return result


async def list_geox_tools() -> list[dict[str, Any]]:
    """List all tools available from GEOX MCP server."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {},
    }
    result = await _post_json_rpc("/mcp", payload)
    return result.get("tools", [])


async def geox_health_check() -> dict[str, Any]:
    """Check GEOX server health via MCP ping."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "ping",
        "params": {},
    }
    try:
        await _post_json_rpc("/mcp", payload)
        return {"status": "healthy", "organ": "GEOX", "host": GEOX_HOST}
    except Exception as e:
        return {"status": "unhealthy", "organ": "GEOX", "error": str(e)}
