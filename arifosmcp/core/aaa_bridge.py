"""
AAA Bridge — arifOS ↔ AAA State Synchronization
═══════════════════════════════════════════════════════

FORGED 2026-06-09 by Ω from MXC-arifOS contrast analysis.

PURPOSE:
  Wire the AAA AgentLifecycle (state layer) into the arifOS MCP runtime.
  Every agent session now flows through: AAA → arifOS → AAA → VAULT999.

ARCHITECTURE:
  ┌─────────┐    register()     ┌─────────┐
  │   AAA   │ ───────────────▶  │ arifOS  │
  │  (3001) │                   │  (8088) │
  │         │ ◀───────────────  │         │
  │lifecycle│  state_sync()     │ session │
  │ manager │                   │  init   │
  └─────────┘                   └─────────┘
       │                              │
       │    transition()              │   vault_seal()
       └──────────────────────────────┘
              VAULT999 (L4/L6)

CONNECTIVITY PIPELINE:
  1. AAA registers agent → arifOS loads AgentPolicy
  2. arifOS session_init → AAA.bindSession() → PROVISIONED
  3. arifOS floor_evaluate → AAA.authorize() → AUTHORIZED
  4. arifOS tool_execute → AAA.startExecution() → EXECUTING
  5. arifOS vault_seal → AAA.completeExecution() → AUDITING
  6. arifOS session_close → AAA.stop() → STOPPED
  7. AAA operator → AAA.deprovision() → DEPROVISIONED

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import UTC, datetime
from typing import Any

import httpx

from arifosmcp.core.agent_policy import AgentPolicy, AgentRole

logger = logging.getLogger("arifosmcp.aaa_bridge")

# ═════════════════════════════════════════════════════════════════════════════
# CONFIG
# ═════════════════════════════════════════════════════════════════════════════

AAA_URL = "http://127.0.0.1:3001"
AAA_TIMEOUT = 5.0  # seconds — non-blocking; fail-soft


# ═════════════════════════════════════════════════════════════════════════════
# AAA HTTP CLIENT
# ═════════════════════════════════════════════════════════════════════════════


class AAABridgeError(Exception):
    """AAA bridge communication error. Always fail-soft."""

    pass


async def _call_aaa(endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Call AAA API endpoint. Fail-soft — never block arifOS on AAA failure."""
    try:
        async with httpx.AsyncClient(timeout=AAA_TIMEOUT) as client:
            resp = await client.post(
                f"{AAA_URL}/api/agents/{endpoint}",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Agent-Bridge": "arifos-aaa-bridge-v1",
                },
            )
            if resp.status_code == 200:
                return resp.json()
            logger.warning(
                "AAA bridge: %s returned %d: %s",
                endpoint,
                resp.status_code,
                resp.text[:200],
            )
            return {"ok": False, "error": f"AAA_{resp.status_code}"}
    except httpx.TimeoutException:
        logger.warning("AAA bridge: %s timed out after %.1fs", endpoint, AAA_TIMEOUT)
        return {"ok": False, "error": "AAA_TIMEOUT"}
    except Exception as exc:
        logger.warning("AAA bridge: %s failed: %s", endpoint, exc)
        return {"ok": False, "error": str(exc)[:100]}


# ═════════════════════════════════════════════════════════════════════════════
# LIFECYCLE SYNC
# ═════════════════════════════════════════════════════════════════════════════


async def sync_agent_register(
    agent_id: str,
    agent_role: str = "engineer",
    actor_id: str | None = None,
    policy: AgentPolicy | None = None,
) -> dict[str, Any]:
    """Register agent with AAA lifecycle manager.

    MXC equivalent: provision()
    """
    payload = {
        "agent_id": agent_id,
        "agent_role": agent_role,
        "actor_id": actor_id,
    }
    if policy:
        payload["policy"] = policy.to_json()

    result = await _call_aaa("register", payload)
    if result.get("ok"):
        logger.info(
            "AAA bridge: agent %s registered (role=%s, instance=%s)",
            agent_id,
            agent_role,
            result.get("instance_id", "?"),
        )
    return result


async def sync_session_bind(
    agent_id: str,
    session_id: str,
) -> dict[str, Any]:
    """Bind a session to an agent (register → provisioned).

    MXC equivalent: start()
    """
    payload = {
        "agent_id": agent_id,
        "session_id": session_id,
    }
    result = await _call_aaa("bind-session", payload)
    if result.get("ok"):
        logger.info(
            "AAA bridge: session %s bound to %s → %s",
            session_id,
            agent_id,
            result.get("state", "?"),
        )
    return result


async def sync_agent_authorize(
    agent_id: str,
    floor_results: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Authorize agent after floor evaluation (provisioned → authorized).

    MXC equivalent: (implicit — arifOS only step)
    """
    payload = {
        "agent_id": agent_id,
        "floor_results": floor_results or [],
    }
    result = await _call_aaa("authorize", payload)
    if result.get("ok"):
        logger.info(
            "AAA bridge: agent %s authorized → %s",
            agent_id,
            result.get("state", "?"),
        )
    elif result.get("held"):
        logger.warning(
            "AAA bridge: agent %s HELD (floors: %s)",
            agent_id,
            result.get("violations", []),
        )
    return result


async def sync_execution_start(
    agent_id: str,
    tool_name: str,
) -> dict[str, Any]:
    """Mark agent as executing (authorized → executing).

    MXC equivalent: exec()
    """
    payload = {
        "agent_id": agent_id,
        "tool_name": tool_name,
    }
    result = await _call_aaa("start-execution", payload)
    if result.get("ok"):
        logger.info(
            "AAA bridge: agent %s executing tool %s",
            agent_id,
            tool_name,
        )
    return result


async def sync_execution_complete(
    agent_id: str,
    vault_sealed: bool = False,
) -> dict[str, Any]:
    """Mark execution complete (executing → auditing).

    MXC equivalent: (no direct equivalent)
    """
    payload = {
        "agent_id": agent_id,
        "vault_sealed": vault_sealed,
    }
    result = await _call_aaa("complete-execution", payload)
    if result.get("ok"):
        logger.info(
            "AAA bridge: agent %s → AUDITING (sealed=%s)",
            agent_id,
            vault_sealed,
        )
    return result


async def sync_agent_stop(
    agent_id: str,
    reason: str = "session_close",
) -> dict[str, Any]:
    """Stop agent (auditing → stopped).

    MXC equivalent: stop()
    """
    payload = {
        "agent_id": agent_id,
        "reason": reason,
    }
    result = await _call_aaa("stop", payload)
    if result.get("ok"):
        logger.info(
            "AAA bridge: agent %s STOPPED (reason=%s)",
            agent_id,
            reason,
        )
    return result


async def sync_agent_deprovision(
    agent_id: str,
) -> dict[str, Any]:
    """Deprovision agent (stopped → deprovisioned).

    MXC equivalent: deprovision()
    """
    payload = {"agent_id": agent_id}
    result = await _call_aaa("deprovision", payload)
    if result.get("ok"):
        logger.info(
            "AAA bridge: agent %s DEPROVISIONED",
            agent_id,
        )
    return result


async def sync_agent_hold(
    agent_id: str,
    reason: str = "888_HOLD",
) -> dict[str, Any]:
    """Emergency hold on agent — requires human review to release.

    MXC equivalent: (no direct equivalent — arifOS governance feature)
    """
    payload = {
        "agent_id": agent_id,
        "reason": reason,
    }
    result = await _call_aaa("hold", payload)
    if result.get("ok"):
        logger.warning(
            "AAA bridge: agent %s HELD (reason=%s)",
            agent_id,
            reason,
        )
    return result


async def sync_agent_degrade(
    agent_id: str,
    error: str,
) -> dict[str, Any]:
    """Mark agent as degraded after error.

    MXC equivalent: (no direct equivalent)
    """
    payload = {
        "agent_id": agent_id,
        "error": error,
    }
    result = await _call_aaa("degrade", payload)
    if result.get("ok"):
        logger.error(
            "AAA bridge: agent %s DEGRADED (error=%s)",
            agent_id,
            error[:100],
        )
    return result


async def get_federation_status() -> dict[str, Any]:
    """Get full federation agent status from AAA.

    MXC equivalent: (no direct equivalent — arifOS federation feature)
    """
    result = await _call_aaa("federation-status", {})
    return result


# ═════════════════════════════════════════════════════════════════════════════
# INTEGRATION INTO arifOS RUNTIME
# ═════════════════════════════════════════════════════════════════════════════

# To integrate into arifOS MCP runtime, add to server.py:
#
#   from arifosmcp.core.aaa_bridge import (
#       sync_agent_register, sync_session_bind, sync_agent_authorize,
#       sync_execution_start, sync_execution_complete, sync_agent_stop,
#   )
#
# And call at each lifecycle point:
#
#   1. On agent startup:     await sync_agent_register(agent_id, role)
#   2. On session_init:      await sync_session_bind(agent_id, session_id)
#   3. On floor_evaluate:    await sync_agent_authorize(agent_id, results)
#   4. On tool_execute:      await sync_execution_start(agent_id, tool_name)
#   5. On vault_seal:        await sync_execution_complete(agent_id, True)
#   6. On session_close:     await sync_agent_stop(agent_id)
#
# All calls are async, non-blocking, and fail-soft.
# If AAA is down, arifOS continues with degraded state tracking.
