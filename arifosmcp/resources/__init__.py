"""
arifOS Resources — Canonical URI Surface
═════════════════════════════════════════

Registers the 5 Canonical Resources:
  arifos://doctrine      — Immutable law (Ψ)
  arifos://vitals        — Living pulse (Ω)
  arifos://schema        — Complete blueprint (Δ)
  arifos://forge         — Execution bridge
  arifos://civilization  — Organs + strata definition
"""
from __future__ import annotations

from fastmcp import FastMCP

from .civilization import register_civilization
from .doctrine import register_doctrine
from .forge import register_forge
from .schema import register_schema
from .vitals import register_vitals

CANONICAL_RESOURCES = (
    "arifos://doctrine",
    "arifos://vitals",
    "arifos://schema",
    "arifos://forge",
    "arifos://civilization",
)


def register_resources(mcp: FastMCP) -> list[str]:
    """Register all canonical arifos:// resources."""
    registered: list[str] = []
    registered.extend(register_doctrine(mcp))
    registered.extend(register_vitals(mcp))
    registered.extend(register_schema(mcp))
    registered.extend(register_forge(mcp))
    registered.extend(register_civilization(mcp))
    return registered
