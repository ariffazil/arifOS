"""
arifos://forge — Execution Bridge
══════════════════════════════════
Runtime contract and A-FORGE boundary specification.
"""
from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.resources.types import TextResource


FORGE_TEXT = """\
arifOS Forge — Execution Audit Bridge

Runtime contract version: 2026.04.24-KANON
A-FORGE boundary: TypeScript execution runtime.

Interface contract:
  - Query live /health for current runtime capabilities.
  - Hardcoded source-file paths to A-FORGE internals are PROHIBITED.
  - The bridge is versioned via the runtime_contract field.

Authority flow:
  1. AGI proposes  → emits CandidateAction + CapabilityClaim
  2. ASI evaluates → checks Ω_ortho + Floor compliance
  3. APEX authorizes → validates ActorBinding + CapabilityToken
  4. Forge executes → signed manifest bridge to A-FORGE

Output contract: Generated artifact + delta_S reduction metric.

DITEMPA BUKAN DIBERI
"""


def register_forge(mcp: FastMCP) -> list[str]:
    """Register arifos://forge — Execution Bridge."""
    resource = TextResource(
        uri="arifos://forge",
        name="Execution Bridge",
        text=FORGE_TEXT,
    )
    mcp.add_resource(resource)
    return ["arifos://forge"]
