"""
arifOS Resources — Canonical URI Surface
════════════════════════════════════════

Registers the 5 Canonical Resources:
  arifos://doctrine      — Immutable law (Ψ)
  arifos://vitals        — Living pulse (Ω)
  arifos://schema        — Complete blueprint (Δ)
  arifos://forge         — Execution bridge
  arifos://civilization  — Organs + strata definition

Plus F-WEB Evidence Resource families:
  source://{hash}       — Ingested source content (SSRF-gated)
  source://list          — List all stored sources
  receipt://web/{id}    — Evidence receipt for web operations
  receipt://list         — List all evidence receipts
  contrast://{id}        — Cross-source contrast report
  void://{id}            — Missing data taxonomy report
"""

from __future__ import annotations

from fastmcp import FastMCP

from .civilization import register_civilization
from .doctrine import register_doctrine
from .evidence import register_evidence_resources
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

EVIDENCE_RESOURCES = (
    "source://{hash}",
    "source://list",
    "receipt://web/{id}",
    "receipt://list",
    "contrast://{id}",
    "void://{id}",
)


def register_resources(mcp: FastMCP) -> list[str]:
    """Register all canonical arifos:// resources and F-WEB evidence resources."""
    registered: list[str] = []
    registered.extend(register_doctrine(mcp))
    registered.extend(register_vitals(mcp))
    registered.extend(register_schema(mcp))
    registered.extend(register_forge(mcp))
    registered.extend(register_civilization(mcp))
    registered.extend(register_evidence_resources(mcp))
    return registered
