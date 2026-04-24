"""
arifosmcp/tools/gateway_connect.py — 666g_GATEWAY
═════════════════════════════════════════════════

Cross-agent routing (A2A) and federation hub.
"""
from __future__ import annotations

import uuid
from typing import Any

from arifosmcp.runtime.floors import check_floors
from arifosmcp.runtime.tools import _hold, _ok


def arif_gateway_connect(
    mode: str = "route",
    target_agent: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    floor_check = check_floors("arif_gateway_connect", {"target_agent": target_agent or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_gateway_connect", floor_check["reason"], floor_check["failed_floors"])

    if mode == "route":
        return _ok("arif_gateway_connect", {"target": target_agent, "protocol": "A2A", "status": "routed"})
    if mode == "discover":
        return _ok("arif_gateway_connect", {"agents": ["kimi", "claude", "gemini"], "protocol": "A2A"})
    if mode == "handshake":
        return _ok("arif_gateway_connect", {
            "target": target_agent,
            "handshake": "OK",
            "capability_token": uuid.uuid4().hex[:16],
        })
    if mode == "seal":
        return _ok("arif_gateway_connect", {
            "target": target_agent,
            "seal": "cross-agent-SEAL",
            "status": "pending_888",
        })

    return _hold("arif_gateway_connect", f"Unknown mode: {mode}")
