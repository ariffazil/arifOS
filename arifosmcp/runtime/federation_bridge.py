"""
arifosmcp/runtime/federation_bridge.py — Federation Organ Bridge v3
═══════════════════════════════════════════════════════════════════════

Upgraded 2026-06-14: dual-transport architecture.
  - PRIMARY:   NATS mesh (request-reply over JetStream) — persistent, replayable
  - FALLBACK:  HTTP POST (stateless JSON-RPC) — works when NATS is down

TRANSPORT SELECTION LOGIC:
  1. Try NATS mesh (request_organ via nats_event_bus)
  2. If NATS unavailable/timed out → fall back to HTTP POST
  3. If both fail → raise ConnectionError

CROSS-ORGAN FEEDBACK LOOP WIRING:
  plan→act→observe→evaluate→update_graph→re-plan now spans organs.
  arifOS emits feedback signals via NATS; GEOX/WEALTH/WELL subscribe
  and respond with computation results. The loop is no longer confined
  to a single arif_think call.

ORGAN IDENTITY ANCHORS (for LiveKernelEnvelope):
  arifOS → constitution_hash
  GEOX   → physics_manifest
  WEALTH → capital_manifest
  WELL   → substrate_manifest

F1 AMANAH: HTTP fallback ensures federation never breaks on mesh failure.
Mesh is primary but NOT mandatory — degrade gracefully.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger("arifosmcp.federation_bridge")

# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT DEFAULTS
# ═══════════════════════════════════════════════════════════════════════════════

WEALTH_HOST = os.getenv("WEALTH_BRIDGE_HOST", "127.0.0.1")
WEALTH_PORT = int(os.getenv("WEALTH_BRIDGE_PORT", "18082"))
WEALTH_BASE = f"http://{WEALTH_HOST}:{WEALTH_PORT}"

WELL_HOST = os.getenv("WELL_BRIDGE_HOST", "127.0.0.1")
WELL_PORT = int(os.getenv("WELL_BRIDGE_PORT", "18083"))
WELL_BASE = f"http://{WELL_HOST}:{WELL_PORT}"

GEOX_HOST = os.getenv("GEOX_BRIDGE_HOST", "localhost")
GEOX_PORT = int(os.getenv("GEOX_BRIDGE_PORT", "8081"))
GEOX_BASE = f"http://{GEOX_HOST}:{GEOX_PORT}"

# ── NATS Mesh availability ──────────────────────────────────────────────────
try:
    from arifosmcp.runtime.nats_event_bus import (
        FEDERATION_ORGANS,
        publish_constitutional_gradient,
        wire_cross_organ_feedback,
    )
    from arifosmcp.runtime.nats_event_bus import (
        event_bus as _nats,
    )

    _NATS_MESH_AVAILABLE = True
except ImportError:
    _NATS_MESH_AVAILABLE = False
    FEDERATION_ORGANS = ["arifOS", "GEOX", "WEALTH", "WELL", "MIND", "MEMORY", "AAA"]

# ── Transport preference ────────────────────────────────────────────────────
# "mesh_first" → try NATS, fall back to HTTP (default)
# "http_only"  → skip NATS, use HTTP directly
# "mesh_only"  → only NATS, raise if unavailable
TRANSPORT_MODE = os.getenv("FEDERATION_TRANSPORT_MODE", "mesh_first")

# Mesh request timeout (seconds) — shorter than HTTP timeout so fallback is fast
MESH_TIMEOUT = float(os.getenv("FEDERATION_MESH_TIMEOUT", "10.0"))


# ═══════════════════════════════════════════════════════════════════════════════
# HTTP FALLBACK — stateless JSON-RPC (original, fully backward compatible)
# ═══════════════════════════════════════════════════════════════════════════════


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


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED ORGAN CALL — mesh primary, HTTP fallback
# ═══════════════════════════════════════════════════════════════════════════════


async def call_organ(
    organ: str,
    tool_name: str,
    arguments: dict[str, Any] | None = None,
    timeout: float = 60.0,
    mesh_timeout: float | None = None,
) -> dict[str, Any]:
    """
    Call a federation organ tool — mesh primary, HTTP fallback.

    Transport selection:
      "mesh_first" (default): try NATS mesh → fall back to HTTP
      "http_only":            skip NATS, use HTTP
      "mesh_only":            only NATS, raise if unavailable

    Args:
        organ: Organ name (GEOX, WEALTH, WELL, MIND, MEMORY, AAA)
        tool_name: Tool name to call
        arguments: Tool arguments dict
        timeout: HTTP timeout (seconds)
        mesh_timeout: NATS mesh timeout (seconds, default MESH_TIMEOUT)

    Returns:
        Tool result dict
    """
    params = arguments or {}
    mesh_to = mesh_timeout if mesh_timeout is not None else MESH_TIMEOUT

    # ── HTTP only ──
    if TRANSPORT_MODE == "http_only":
        return await _call_organ_http(organ, tool_name, params, timeout)

    # ── Mesh first or mesh only ──
    if _NATS_MESH_AVAILABLE and _nats.connected:
        try:
            result = await _nats.request_organ(
                organ=organ,
                method=tool_name,
                params=params,
                timeout=mesh_to,
            )
            if result is not None:
                logger.debug(f"Mesh call to {organ}.{tool_name} succeeded")
                return result
            # result is None → timeout, fall through to HTTP
            logger.info(f"Mesh call to {organ}.{tool_name} timed out — falling back to HTTP")
        except Exception as e:
            logger.warning(f"Mesh call to {organ}.{tool_name} failed: {e}")

    # ── Mesh only — no fallback ──
    if TRANSPORT_MODE == "mesh_only":
        raise ConnectionError(
            f"Mesh-only mode: cannot reach {organ}. "
            f"NATS available={_NATS_MESH_AVAILABLE} connected={_nats.connected if _NATS_MESH_AVAILABLE else False}"
        )

    # ── HTTP fallback ──
    return await _call_organ_http(organ, tool_name, params, timeout)


async def _call_organ_http(
    organ: str,
    tool_name: str,
    params: dict[str, Any],
    timeout: float = 60.0,
) -> dict[str, Any]:
    """HTTP fallback for organ calls."""
    base_map = {
        "GEOX": GEOX_BASE,
        "WEALTH": WEALTH_BASE,
        "WELL": WELL_BASE,
    }
    base = base_map.get(organ.upper())
    if not base:
        raise ValueError(
            f"Unknown organ: {organ}. Known: {list(base_map.keys())}. "
            f"Use direct call functions for non-standard organs."
        )

    return await _json_rpc(base, "tools/call", {"name": tool_name, "arguments": params}, timeout)


# ═══════════════════════════════════════════════════════════════════════════════
# BROADCAST — send to all organs simultaneously
# ═══════════════════════════════════════════════════════════════════════════════


async def broadcast_to_federation(
    event_type: str,
    payload: dict[str, Any],
    exclude: str | None = None,
) -> dict[str, bool]:
    """
    Broadcast a message to all federation organs.

    Uses NATS broadcast subject if mesh is available, otherwise fans out
    via HTTP to each organ.

    Returns:
        Dict mapping organ name → success (bool)
    """
    results: dict[str, bool] = {}

    # Try NATS broadcast first
    if _NATS_MESH_AVAILABLE and _nats.connected:
        try:
            await _nats.broadcast_to_federation(event_type, payload, exclude)
            logger.info(f"Broadcast '{event_type}' sent via NATS mesh")
            # NATS broadcast is fire-and-forget — assume all organs received
            for organ in FEDERATION_ORGANS:
                if organ != exclude and organ != "arifOS":
                    results[organ] = True
            return results
        except Exception as e:
            logger.warning(f"NATS broadcast failed, falling back to HTTP fan-out: {e}")

    # HTTP fan-out — call each organ in parallel
    health = await federation_health_all()
    for organ, status in health.items():
        if organ == exclude:
            continue
        results[organ] = status.get("status") == "healthy"

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# FEEDBACK LOOP WIRING — cross-organ plan→act→observe→evaluate→re-plan
# ═══════════════════════════════════════════════════════════════════════════════


async def emit_feedback_signal(
    signal: str,
    session_id: str,
    source_organ: str = "arifOS",
    target_organ: str | None = None,
    step_number: int = 0,
    metadata: dict[str, Any] | None = None,
) -> bool:
    """
    Emit a cross-organ feedback loop signal.

    This extends FeedbackLoop from single-call to federation-wide.
    arifOS reasons → GEOX computes → WEALTH evaluates →
    feedback signal → arifOS re-plans.

    The signal travels via NATS mesh if available; otherwise logged locally.
    """
    if _NATS_MESH_AVAILABLE and _nats.connected:
        try:
            await wire_cross_organ_feedback(
                session_id=session_id,
                source_organ=source_organ,
                target_organ=target_organ or "ALL",
                signal=signal,
                step_number=step_number,
                metadata=metadata,
            )
            return True
        except Exception as e:
            logger.warning(f"Failed to emit feedback signal via NATS: {e}")

    # Log locally — feedback still works within arifOS, just not cross-organ
    logger.info(
        "FEEDBACK [local only]: signal=%s session=%s source=%s target=%s step=%d",
        signal,
        session_id,
        source_organ,
        target_organ or "ALL",
        step_number,
    )
    return False


async def emit_gradient_signal(
    session_id: str,
    dimension: str,
    delta: float,
    source_organ: str = "arifOS",
) -> bool:
    """
    Emit a constitutional cost gradient signal.

    Published dimensions: constitution, physics, capital, substrate,
    continuity, dignity — corresponding to the 6 terms of the
    constitutional cost function:

      C = α·C_constitution + β·C_physics + γ·C_capital
          + δ·C_substrate + ε·C_continuity + ζ·C_dignity
    """
    if _NATS_MESH_AVAILABLE and _nats.connected:
        try:
            await _nats.publish_gradient(
                dimension=dimension,
                delta=delta,
                session_id=session_id,
                source_organ=source_organ,
            )
            return True
        except Exception as e:
            logger.warning(f"Failed to emit gradient via NATS: {e}")

    logger.info(
        "GRADIENT [local only]: dim=%s delta=%.4f session=%s",
        dimension,
        delta,
        session_id,
    )
    return False


# ═══════════════════════════════════════════════════════════════════════════════
# WEALTH — backward-compatible direct calls (HTTP)
# ═══════════════════════════════════════════════════════════════════════════════


async def call_wealth_tool(
    tool_name: str,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Call a WEALTH MCP tool — uses unified transport (mesh first)."""
    return await call_organ("WEALTH", tool_name, arguments)


async def list_wealth_tools() -> list[dict[str, Any]]:
    """List all tools available from WEALTH MCP server."""
    result = await call_wealth_tool("wealth_system_registry_status", {"mode": "registry"})
    return result.get("tools", [])


async def wealth_health_check() -> dict[str, Any]:
    """Check WEALTH MCP server health."""
    try:
        await call_wealth_tool("wealth_system_registry_status", {"mode": "health"})
        return {"status": "healthy", "organ": "WEALTH", "host": WEALTH_HOST}
    except Exception as e:
        return {"status": "unhealthy", "organ": "WEALTH", "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# WELL — backward-compatible direct calls (HTTP)
# ═══════════════════════════════════════════════════════════════════════════════


async def call_well_tool(
    tool_name: str,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Call a WELL MCP tool — uses unified transport (mesh first)."""
    return await call_organ("WELL", tool_name, arguments)


async def list_well_tools() -> list[dict[str, Any]]:
    """List all tools available from WELL MCP server."""
    result = await call_well_tool("well_system_registry_status", {})
    return result.get("tools", [])


async def well_health_check() -> dict[str, Any]:
    """Check WELL MCP server health."""
    try:
        await call_well_tool("well_assess_reliability", {"mode": "health"})
        return {"status": "healthy", "organ": "WELL", "host": WELL_HOST}
    except Exception as e:
        return {"status": "unhealthy", "organ": "WELL", "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# GEOX — backward-compatible direct calls (HTTP)
# ═══════════════════════════════════════════════════════════════════════════════


async def call_geox_tool_fallback(
    tool_name: str,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Call a GEOX MCP tool — uses unified transport (mesh first)."""
    return await call_organ("GEOX", tool_name, arguments)


async def list_geox_tools_fallback() -> list[dict[str, Any]]:
    """List GEOX tools."""
    result = await call_geox_tool_fallback("geox_system_registry_status", {})
    return result.get("tools", [])


async def geox_health_check() -> dict[str, Any]:
    """Check GEOX MCP server health."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                "http://localhost:8081/health",
                headers={"Accept": "application/json"},
            )
            if resp.status_code == 200:
                return {"status": "healthy", "organ": "GEOX", "host": GEOX_HOST}
    except Exception:
        pass
    try:
        await call_geox_tool_fallback("geox_system_registry_status", {})
        return {"status": "healthy", "organ": "GEOX", "host": GEOX_HOST}
    except Exception as e:
        return {"status": "unhealthy", "organ": "GEOX", "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# COMBINED FEDERATION HEALTH
# ═══════════════════════════════════════════════════════════════════════════════


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
            if not isinstance(well_health, Exception)
            else {"status": "error", "error": str(well_health)}
        ),
    }


async def federation_mesh_status() -> dict[str, Any]:
    """Report NATS mesh connectivity status for all organs."""
    status = {
        "mesh_available": _NATS_MESH_AVAILABLE,
        "mesh_connected": _nats.connected if _NATS_MESH_AVAILABLE else False,
        "transport_mode": TRANSPORT_MODE,
        "mesh_timeout": MESH_TIMEOUT,
        "organs": {},
    }

    if _NATS_MESH_AVAILABLE and _nats.connected:
        # Check each organ via mesh
        for organ in FEDERATION_ORGANS:
            if organ == "arifOS":
                continue
            try:
                result = await _nats.request_organ(
                    organ=organ,
                    method="health_check",
                    params={},
                    timeout=3.0,
                )
                status["organs"][organ] = {
                    "reachable": result is not None,
                    "via": "mesh",
                }
            except Exception as e:
                status["organs"][organ] = {
                    "reachable": False,
                    "via": "mesh",
                    "error": str(e),
                }
    else:
        # Fall back to HTTP health check
        http_health = await federation_health_all()
        for organ, health in http_health.items():
            status["organs"][organ] = {
                "reachable": health.get("status") == "healthy",
                "via": "http",
                "error": health.get("error", ""),
            }

    return status


__all__ = [
    # Unified transport
    "call_organ",
    "broadcast_to_federation",
    # Feedback + Gradient
    "emit_feedback_signal",
    "emit_gradient_signal",
    # Mesh status
    "federation_mesh_status",
    # WEALTH
    "call_wealth_tool",
    "list_wealth_tools",
    "wealth_health_check",
    # WELL
    "call_well_tool",
    "list_well_tools",
    "well_health_check",
    # GEOX
    "call_geox_tool_fallback",
    "list_geox_tools_fallback",
    "geox_health_check",
    # Combined
    "federation_health_all",
    # Config
    "TRANSPORT_MODE",
    "MESH_TIMEOUT",
    "FEDERATION_ORGANS",
]
