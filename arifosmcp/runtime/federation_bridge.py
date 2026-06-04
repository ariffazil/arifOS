"""
arifosmcp/runtime/federation_bridge.py — WEALTH + WELL Federation Bridge

DITEMPA BUKAN DIBERI — Forged, Not Given

Bridges arifOS kernel to WEALTH and WELL organs via their public MCP endpoints.

All three remote organs (WEALTH, WELL, GEOX via geox_bridge.py) speak stateless
JSON over HTTP POST.  No SSE sessions, no sessionId headers.

Phase-2 simplification (2026-06-04): gutted ~120 lines of stale SSE session code.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import httpx

logger = logging.getLogger("arifosmcp.federation_bridge")

# ── Endpoint defaults ─────────────────────────────────────────────────────────
WEALTH_HOST = "wealth.arif-fazil.com"
WEALTH_BASE = f"https://{WEALTH_HOST}"

WELL_HOST = "well.arif-fazil.com"
WELL_BASE = f"https://{WELL_HOST}"

GEOX_HOST = "geox.arif-fazil.com"
GEOX_BASE = f"https://{GEOX_HOST}"

# ── Generic stateless JSON-RPC helper ─────────────────────────────────────────


async def _json_rpc(
    base_url: str,
    method: str,
    params: dict[str, Any],
    timeout: float = 60.0,
) -> dict[str, Any]:
    """Send a stateless JSON-RPC call to an MCP organ and return the result."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params,
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        resp = await client.post(f"{base_url}/mcp", json=payload, headers=headers)
        if resp.status_code >= 400:
            try:
                err = resp.json()
                msg = err.get("error", {}).get("message", resp.text[:200])
            except Exception:
                msg = resp.text[:200]
            raise ConnectionError(f"MCP HTTP {resp.status_code}: {msg}")

        parsed = resp.json()
        if parsed.get("error"):
            raise ConnectionError(f"MCP JSON-RPC error: {parsed['error']}")

        return parsed.get("result", {})


# ── WEALTH ────────────────────────────────────────────────────────────────────


async def call_wealth_tool(
    tool_name: str,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Call a WEALTH MCP tool by name with arguments."""
    return await _json_rpc(
        WEALTH_BASE,
        "tools/call",
        {"name": tool_name, "arguments": arguments or {}},
    )


async def list_wealth_tools() -> list[dict[str, Any]]:
    """List all tools available from WEALTH MCP server."""
    result = await _json_rpc(WEALTH_BASE, "tools/list", {})
    return result.get("tools", [])


async def wealth_health_check() -> dict[str, Any]:
    """Check WEALTH MCP server health."""
    try:
        await _json_rpc(
            WEALTH_BASE,
            "tools/call",
            {"name": "wealth_health_check", "arguments": {}},
        )
        return {"status": "healthy", "organ": "WEALTH", "host": WEALTH_HOST}
    except Exception as e:
        return {"status": "unhealthy", "organ": "WEALTH", "error": str(e)}


# ── WELL ──────────────────────────────────────────────────────────────────────


async def call_well_tool(
    tool_name: str,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Call a WELL MCP tool by name with arguments."""
    return await _json_rpc(
        WELL_BASE,
        "tools/call",
        {"name": tool_name, "arguments": arguments or {}},
    )


async def list_well_tools() -> list[dict[str, Any]]:
    """List all tools available from WELL MCP server."""
    result = await _json_rpc(WELL_BASE, "tools/list", {})
    return result.get("tools", [])


async def well_health_check() -> dict[str, Any]:
    """Check WELL MCP server health."""
    try:
        await call_well_tool("well_assess_reliability", {"mode": "health"})
        return {"status": "healthy", "organ": "WELL", "host": WELL_HOST}
    except Exception as e:
        return {"status": "unhealthy", "organ": "WELL", "error": str(e)}


# ── GEOX (lightweight fallback — canonical bridge is geox_bridge.py) ──────────


async def call_geox_tool_fallback(
    tool_name: str,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Fallback GEOX call when geox_bridge.py is not imported."""
    return await _json_rpc(
        GEOX_BASE,
        "tools/call",
        {"name": tool_name, "arguments": arguments or {}},
    )


async def list_geox_tools_fallback() -> list[dict[str, Any]]:
    """Fallback GEOX tool list when geox_bridge.py is not imported."""
    result = await _json_rpc(GEOX_BASE, "tools/list", {})
    return result.get("tools", [])


async def geox_health_check() -> dict[str, Any]:
    """Check GEOX MCP server health."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                f"http://localhost:8081/health",
                headers={"Accept": "application/json"},
            )
            if resp.status_code == 200:
                return {"status": "healthy", "organ": "GEOX", "host": GEOX_HOST}
    except Exception:
        pass
    try:
        await call_geox_tool_fallback("geox_health_check", {})
        return {"status": "healthy", "organ": "GEOX", "host": GEOX_HOST}
    except Exception as e:
        return {"status": "unhealthy", "organ": "GEOX", "error": str(e)}


# ── Combined federation health ─────────────────────────────────────────────────
async def federation_health_all() -> dict[str, Any]:
    """Run health checks on all three federation organs in parallel."""

    w_health, g_health, well_health = await asyncio.gather(
        wealth_health_check(),
        geox_health_check(),
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
            if not isinstance(w_health, Exception)
            else {"status": "error", "error": str(w_health)}
        ),
    }
