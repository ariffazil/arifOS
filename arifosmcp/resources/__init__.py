"""
arifOS Resources — Canonical URI Surface
════════════════════════════════════════

Registers the 6 Canonical Resources:
  arifos://doctrine      — Immutable law (Ψ)
  arifos://vitals        — Living pulse (Ω)
  arifos://schema        — Complete blueprint (Δ)
  arifos://forge         — Execution bridge
  arifos://civilization  — Organs + strata definition
  arifos://philosophy    — 33-axis human intelligence canon

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
from .embodied_resources import register_embodied_resources
from .evidence import register_evidence_resources
from .forge import register_forge
from .philosophy import register_philosophy
from .schema import register_schema
from .tree777 import register_tree777_resources
from .vitals import register_vitals

CANONICAL_RESOURCES = (
    "arifos://doctrine",
    "arifos://vitals",
    "arifos://schema",
    "arifos://forge",
    "arifos://civilization",
    "arifos://philosophy",
)

TREE777_RESOURCES = (
    "tree777://index",
    "tree777://search",
    "tree777://skills/{category}/{name}",
    "tree777://concepts/{name}",
    "tree777://scars/{name}",
)

EMBODIED_RESOURCES = (
    "arifos://tools/self-model/{view}",
    "arifos://tools/permissions/{scope}",
    "arifos://tools/composition-matrix/{format}",
    "arifos://witness/log/{filter}",
    "arifos://witness/stats/{period}",
    "arifos://boundaries/domain/{domain_id}",
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
    """Register canonical resources plus evidence, embodied, and TREE777 families."""
    registered: list[str] = []
    registered.extend(register_doctrine(mcp))
    registered.extend(register_vitals(mcp))
    registered.extend(register_schema(mcp))
    registered.extend(register_forge(mcp))
    registered.extend(register_civilization(mcp))
    registered.extend(register_philosophy(mcp))
    registered.extend(register_evidence_resources(mcp))
    registered.extend(register_embodied_resources(mcp))
    registered.extend(register_tree777_resources(mcp))
    return registered
