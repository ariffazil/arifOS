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

A2A Discovery Consolidation (FEDERATION_CONTRACT §5.4.5):
Canonical A2A agent card discovery is owned exactly once — by AAA — and
is served at `https://aaa.arif-fazil.com/.well-known/agent.json` (v1.0)
and `https://aaa.arif-fazil.com/.well-known/agent-card.json` (v2.x
extended, authenticated). arifOS no longer publishes a local card body;
its `/.well-known/agent.json` returns 410 Gone with a pointer. Organs
listed below advertise their discovery endpoints through this contract;
only the AAA A2A Gateway entry is the binding peer-discovery surface.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


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
    mcp_endpoint: str | None = None
    status: str = "unknown"


# Central A2A discovery URLs (FEDERATION_CONTRACT §5.4.5).
# AAA owns the canonical A2A agent card; every organ's local `/.well-known/agent.json`
# is either an MCP manifest (for arifOS / WEALTH / WELL / GEOX) or a deprecated
# pointer (for arifOS, see `rest_routes.py:agent_well_known`). The single binding
# peer-discovery URL is the AAA A2A Gateway card below.
AAA_A2A_GATEWAY_BASE = "https://aaa.arif-fazil.com"
AAA_A2A_CARD_URL = f"{AAA_A2A_GATEWAY_BASE}/.well-known/agent.json"
AAA_A2A_CARD_URL_V2 = f"{AAA_A2A_GATEWAY_BASE}/.well-known/agent-card.json"


CANONICAL_ORGANS: list[OrganDescriptor] = [
    OrganDescriptor(
        name="arifOS",
        port=8088,
        role="Constitutional Kernel",
        health_endpoint="http://localhost:8088/health",
        # arifOS does NOT publish a local A2A card. Its `/.well-known/mcp/server.json`
        # is the MCP manifest (different protocol). The A2A card for arifOS is
        # served by AAA at the URL below.
        agent_card_endpoint=AAA_A2A_CARD_URL,
        mcp_endpoint="http://localhost:8088/mcp",
    ),
    OrganDescriptor(
        name="arifosd",
        port=18081,
        role="Constitutional Daemon",
        health_endpoint="http://localhost:18081/health",
        agent_card_endpoint=AAA_A2A_CARD_URL,
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
        role="Control Plane + A2A Gateway",
        health_endpoint="http://localhost:3001/health",
        # AAA publishes the canonical federation A2A card (binding peer discovery).
        agent_card_endpoint=AAA_A2A_CARD_URL_V2,
    ),
    # AAA A2A Gateway — the explicit consolidated discovery surface added
    # 2026-07-15 to make the canonical A2A peer-discovery endpoint first-class
    # in the organ list. Peers that want to discover the federation hit this
    # entry; routing then goes through AAA to arifOS / A-FORGE / organs.
    OrganDescriptor(
        name="AAA A2A Gateway",
        port=3001,
        role="Canonical A2A Peer Discovery (consolidation)",
        health_endpoint="http://localhost:3001/health",
        agent_card_endpoint=AAA_A2A_CARD_URL_V2,
    ),
]


def get_discovery_organs() -> list[OrganDescriptor]:
    """Return the list of discoverable organs (read-only, no auth needed)."""
    return CANONICAL_ORGANS
