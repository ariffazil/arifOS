"""
Gateway Discovery Contract — arifOS Federation
══════════════════════════════════════════════

P1.1 from the 2026-06-09 readiness audit:
"Discovery should not require unsafe authority. Relay/route can stay gated,
but discover should be clean."

This contract defines the discovery-only mode for gateway_connect that
does NOT trip constitutional HOLD. Discovery is read-only topology —
it tells you what organs exist and what they expose, without routing
any traffic through them.

DITEMPA BUKAN DIBERI — Knowing the map is not the same as crossing the border.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Optional


class DiscoveryMode(StrEnum):
    """Safe discovery modes that never trigger HOLD."""

    LIST_ORGANS = "list_organs"  # List all federation organs
    ORGAN_STATUS = "organ_status"  # Get status of a specific organ
    TOPOLOGY = "topology"  # Full topology map
    AGENT_CARD = "agent_card"  # Get agent card for an organ
    CAPABILITIES = "capabilities"  # List available capabilities


class GatewayAction(StrEnum):
    """Gateway actions and their authority requirements."""

    DISCOVER = "discover"  # Read-only — no authority needed
    ROUTE = "route"  # Requires AGENT tier — routes tool calls
    RELAY = "relay"  # Requires JUDGE tier — cross-organ relay
    DELEGATE = "delegate"  # Requires SOVEREIGN — delegates authority


# ── Action → Authority Mapping ──
# This is the canonical table that prevents discovery from tripping HOLD.

GATEWAY_AUTHORITY_MAP: dict[GatewayAction, int] = {
    GatewayAction.DISCOVER: 0,  # Tier 0 (OBSERVER) — anyone can discover
    GatewayAction.ROUTE: 2,  # Tier 2 (AGENT) — needs execution authority
    GatewayAction.RELAY: 3,  # Tier 3 (JUDGE) — needs constitutional authority
    GatewayAction.DELEGATE: 4,  # Tier 4 (SOVEREIGN) — Arif only
}


# ── Known Federation Organs (canonical) ──


@dataclass
class OrganDescriptor:
    """Describes a federation organ for discovery."""

    name: str
    port: int
    role: str
    health_endpoint: str
    agent_card_endpoint: str
    mcp_endpoint: Optional[str] = None
    status: str = "unknown"


CANONICAL_ORGANS: list[OrganDescriptor] = [
    OrganDescriptor(
        name="arifOS",
        port=8088,
        role="Constitutional Kernel",
        health_endpoint="http://localhost:8088/health",
        agent_card_endpoint="http://localhost:8088/.well-known/mcp/server.json",
        mcp_endpoint="http://localhost:8088/mcp",
    ),
    OrganDescriptor(
        name="arifosd",
        port=18081,
        role="Constitutional Daemon",
        health_endpoint="http://localhost:18081/health",
        agent_card_endpoint="http://localhost:18081/.well-known/agent-card.json",
    ),
    OrganDescriptor(
        name="WEALTH",
        port=18082,
        role="Capital Intelligence",
        health_endpoint="http://localhost:18082/health",
        agent_card_endpoint="http://localhost:18082/.well-known/mcp/server.json",
        mcp_endpoint="http://localhost:18082/mcp",
    ),
    OrganDescriptor(
        name="WELL",
        port=18083,
        role="Human Readiness",
        health_endpoint="http://localhost:18083/health",
        agent_card_endpoint="http://localhost:18083/.well-known/mcp/server.json",
        mcp_endpoint="http://localhost:18083/mcp",
    ),
    OrganDescriptor(
        name="GEOX",
        port=8081,
        role="Earth Intelligence",
        health_endpoint="http://localhost:8081/health",
        agent_card_endpoint="http://localhost:8081/.well-known/mcp/server.json",
        mcp_endpoint="http://localhost:8081/mcp",
    ),
    OrganDescriptor(
        name="A-FORGE",
        port=7071,
        role="Execution Shell",
        health_endpoint="http://localhost:7071/health",
        agent_card_endpoint="http://localhost:7071/contract",
    ),
    OrganDescriptor(
        name="AAA",
        port=3001,
        role="Control Plane",
        health_endpoint="http://localhost:3001/health",
        agent_card_endpoint="http://localhost:3001/.well-known/agent-card.json",
    ),
    OrganDescriptor(
        name="APEX",
        port=3002,
        role="888 JUDGE",
        health_endpoint="http://localhost:3002/health",
        agent_card_endpoint="http://localhost:3002/.well-known/agent-card.json",
    ),
]


def get_discovery_organs() -> list[OrganDescriptor]:
    """Return the list of discoverable organs (read-only, no auth needed)."""
    return CANONICAL_ORGANS
