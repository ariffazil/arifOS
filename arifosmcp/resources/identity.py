"""
arifos://identity — Sovereign Identity Manifest
════════════════════════════════════════════════
Bound at boot from identity.toml. Identity is the root of accountability.
"""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.resources.types import TextResource

IDENTITY_TEXT = """\
arifOS Identity Manifest

Sovereign:       Muhammad Arif bin Fazil
Role:            L13 SOVEREIGN — final veto authority
VPS:             af-forge (72.62.71.199)
Identity Source: identity.toml
Identity Hash:   BLAKE3 (verified at boot)

Federation Identity:
  Kernel:        arifOS MCP (Ω — Constitutional)
  Ag entry:      A-FORGE (forge execution shell)
  Earth witness: GEOX (evidence only)
  Capital:       WEALTH (evidence only)
  Vitality:      WELL (reflect only)
  Cockpit:       AAA (control plane)
  Judge:         APEX (888 verdict relay)

Authority Chain:
  APEX (Arif Fazil, L13 SOVEREIGN)
    → arifOS constitutional kernel
      → F1–L13 floor receipts
        → domain organ advisory output (GEOX/WEALTH/WELL)
          → AAA operator surface
            → VAULT999 audit seal
              → A-FORGE execution

No organ may authorize its own execution.
APEX is the only path to a forge gate.

Architecture Principle:
  Bare-metal systemd (organs) + Docker (supporting services only).
  Federation runs on ports 8088/18081/18082/18083/8081/7071/3001/3002/18789.

Localhost IS the password (ADR-001).
All data services bind to 127.0.0.1, no auth required internally.
UFW handles the outside world.

DITEMPA BUKAN DIBERI
"""


def register_identity(mcp: FastMCP) -> list[str]:
    """Register arifos://identity — sovereign identity manifest."""
    resource = TextResource(
        uri="arifos://identity",
        name="Sovereign Identity Manifest",
        description=(
            "Sovereign identity manifest bound from identity.toml at boot. "
            "Defines the authority chain from APEX (Arif) through arifOS kernel "
            "to domain organs and execution. Includes ADR-001 localhost doctrine. "
            "Identity is the root of accountability — all attestation chains begin here."
        ),
        text=IDENTITY_TEXT,
    )
    mcp.add_resource(resource)
    return ["arifos://identity"]
