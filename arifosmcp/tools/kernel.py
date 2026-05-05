"""
arifosmcp/tools/kernel_route.py — 444_KERNEL
═══════════════════════════════════════════

Kernel syscall, routing, and telemetry.
Routes external domain calls (GEOX, WEALTH) via bridge protocol.
"""

from __future__ import annotations

import time
from typing import Any

from arifosmcp.runtime.floors import check_floors
from arifosmcp.runtime.tools import _hold, _ok


def arif_kernel_route(
    mode: str = "route",
    target: str | None = None,
    task: str | None = None,
    stage: str | None = None,
    actor_id: str | None = None,
    organ: str | None = None,
    tool_name: str | None = None,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Routes tasks to correct organ or bridges external domain calls.

    Modes:
      route        — basic routing decision
      delegate     — dispatch to target agent
      status       — kernel session status
      telemetry    — thermodynamic metrics
      bridge       — direct organ bridge call (geox, wealth)

    Bridge protocol (mode="bridge"):
      organ:   "geox" | "wealth"
      tool:   the MCP tool name on the organ
      arguments: dict of tool arguments
    """
    floor_check = check_floors("arif_kernel_route", {"target": target or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_kernel_route", floor_check["reason"], floor_check["failed_floors"])

    if mode == "route":
        return _ok(
            "arif_kernel_route", {"target": target, "path": ["init", "sense", "mind"], "hops": 3}
        )

    if mode == "kernel":
        return _ok("arif_kernel_route", {"status": "running", "uptime": time.time() % 10000})

    if mode == "triage":
        return _ok("arif_kernel_route", {"priority": "normal", "queue": 0})

    if mode == "delegate":
        return _ok("arif_kernel_route", {"agent": target, "task": task, "status": "delegated"})

    if mode == "status":
        from arifosmcp.runtime.tools import _SESSIONS

        return _ok(
            "arif_kernel_route", {"active_sessions": len(_SESSIONS), "stage": stage or "000"}
        )

    if mode == "telemetry":
        return _ok("arif_kernel_route", {"g_score": 0.97, "delta_S": 0.002, "omega": 0.91})

    if mode == "bridge":
        return _bridge_organ_call(organ, tool_name, arguments)

    if mode == "command_center":
        return _command_center_cockpit()

    return _hold("arif_kernel_route", f"Unknown mode: {mode}")


async def _bridge_organ_call(
    organ: str | None,
    tool_name: str | None,
    arguments: dict[str, Any] | None,
) -> dict[str, Any]:
    """Bridge a call to GEOX or WEALTH organ via their public MCP endpoints."""
    if not organ or not tool_name:
        return _hold("arif_kernel_route", "bridge mode requires organ and tool_name")

    if organ == "geox":
        from arifosmcp.runtime.geox_bridge import call_geox_tool

        try:
            result = await call_geox_tool(tool_name, arguments or {})
            return _ok(
                "arif_kernel_route",
                {
                    "organ": "GEOX",
                    "tool": tool_name,
                    "result": result,
                    "status": "bridged",
                },
            )
        except Exception as e:
            return _hold("arif_kernel_route", f"GEOX bridge failed: {e}")

    if organ == "wealth":
        from arifosmcp.runtime.wealth_bridge import call_wealth_tool

        try:
            result = await call_wealth_tool(tool_name, arguments or {})
            return _ok(
                "arif_kernel_route",
                {
                    "organ": "WEALTH",
                    "tool": tool_name,
                    "result": result,
                    "status": "bridged",
                },
            )
        except Exception as e:
            return _hold("arif_kernel_route", f"WEALTH bridge failed: {e}")

    return _hold("arif_kernel_route", f"Unknown organ: {organ}")


def _command_center_cockpit() -> dict[str, Any]:
    """Return command center cockpit data (read-only, no mutation)."""
    from arifosmcp.runtime.rest_routes import _build_governance_status_payload

    payload = _build_governance_status_payload()
    return _ok(
        "arif_kernel_route",
        {
            "mode": "command_center",
            "session_status": {
                "active_sessions": payload.get("session_count", 0),
                "stage": "000",
            },
            "vitals": payload.get("telemetry", {}),
            "floors": payload.get("floors", {}),
            "witness": payload.get("witness", {}),
            "tabs": [
                "session_status",
                "vitals",
                "judge",
                "forge",
                "gateway",
                "vault",
            ],
            "доступ": (
                "Use arif_judge_deliberate for judge, arif_forge_execute for forge, "
                "arif_gateway_connect for gateway, arif_vault_seal for vault"
            ),
        },
    )
