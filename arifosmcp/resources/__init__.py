"""
arifOS Resources — Canonical URI Surface
════════════════════════════════════════

10 Canonical Resources (intelligence, not chaos):

  arifos://doctrine       — Immutable law (F1–L13)
  arifos://trinity        — AAA lane definitions and separation of powers
  arifos://schema         — Complete blueprint (tools, lanes, forge bridge)
  arifos://civilization   — Organs, strata, and constitutional boundaries
  arifos://seal-readiness — Vault integrity and seal gate
  arifos://jurisdiction   — Autonomy bands and capability grants
  arifos://identity       — Sovereign identity manifest and authority chain
  arifos://memory         — 6-layer memory architecture (L1–L6)
  arifos://vitals         — Metric reference and thresholds
  tree777://index         — TREE777 wiki index

REMOVED (chaos reduction):
  arifos://philosophy — beautiful, not operational. Agents don't load it.
  arifos://forge      — merged into arifos://schema
  source://list       — dynamic data → belongs in arif_evidence_fetch tool
  receipt://list      — dynamic data → belongs in arif_evidence_fetch tool
  tree777://search    — search → belongs in arif_memory_recall tool
"""

from __future__ import annotations

from fastmcp import FastMCP

from .civilization import register_civilization
from .doctrine import register_doctrine
from .embodied_resources import register_embodied_resources
from .evidence import register_evidence_resources
from .identity import register_identity
from .jurisdiction import register_jurisdiction
from .memory import register_memory
from .schema import register_schema
from .seal_readiness import register_seal_readiness
from .tree777 import register_tree777_resources
from .trinity import register_trinity
from .vitals import register_vitals

CANONICAL_RESOURCES = (
    "arifos://doctrine",
    "arifos://trinity",
    "arifos://schema",
    "arifos://civilization",
    "arifos://seal-readiness",
    "arifos://jurisdiction",
    "arifos://identity",
    "arifos://memory",
    "arifos://vitals",
)

TREE777_RESOURCES = (
    "tree777://index",
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
    "receipt://web/{id}",
    "contrast://{id}",
    "void://{id}",
)


def register_resources(mcp: FastMCP) -> list[str]:
    """Register 10 canonical resources + evidence, embodied, and TREE777 families."""
    registered: list[str] = []
    registered.extend(register_doctrine(mcp))
    registered.extend(register_trinity(mcp))
    registered.extend(register_schema(mcp))
    registered.extend(register_civilization(mcp))
    registered.extend(register_seal_readiness(mcp))
    registered.extend(register_jurisdiction(mcp))
    registered.extend(register_identity(mcp))
    registered.extend(register_memory(mcp))
    registered.extend(register_vitals(mcp))
    registered.extend(register_evidence_resources(mcp))
    registered.extend(register_embodied_resources(mcp))
    registered.extend(register_tree777_resources(mcp))
    return registered
