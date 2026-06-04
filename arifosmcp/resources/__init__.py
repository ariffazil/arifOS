"""
arifOS Resources — Canonical URI Surface
════════════════════════════════════════

Registers 11 Canonical Resources:
  arifos://doctrine       — Immutable law (F1–F13)
  arifos://vitals         — Metric reference thresholds
  arifos://schema         — Complete AAA Trinity blueprint
  arifos://trinity        — AAA lane definitions and separation of powers
  arifos://forge          — Execution bridge contract
  arifos://civilization   — Organs, strata, and constitutional boundaries
  arifos://philosophy     — 33-axis human intelligence canon
  arifos://identity       — Sovereign identity manifest
  arifos://jurisdiction   — Autonomy bands and capability grants
  arifos://memory         — 6-layer memory architecture (L1–L6)
  arifos://seal-readiness — Vault integrity and seal gate

Plus F-WEB Evidence Resource families and TREE777 wiki resources.
"""

from __future__ import annotations

from fastmcp import FastMCP

from .civilization import register_civilization
from .doctrine import register_doctrine
from .embodied_resources import register_embodied_resources
from .evidence import register_evidence_resources
from .forge import register_forge
from .identity import register_identity
from .jurisdiction import register_jurisdiction
from .memory import register_memory
from .philosophy import register_philosophy
from .schema import register_schema
from .seal_readiness import register_seal_readiness
from .tree777 import register_tree777_resources
from .trinity import register_trinity
from .vitals import register_vitals

CANONICAL_RESOURCES = (
    "arifos://doctrine",
    "arifos://vitals",
    "arifos://schema",
    "arifos://trinity",
    "arifos://forge",
    "arifos://civilization",
    "arifos://philosophy",
    "arifos://identity",
    "arifos://jurisdiction",
    "arifos://memory",
    "arifos://seal-readiness",
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
    registered.extend(register_trinity(mcp))
    registered.extend(register_forge(mcp))
    registered.extend(register_civilization(mcp))
    registered.extend(register_philosophy(mcp))
    registered.extend(register_identity(mcp))
    registered.extend(register_jurisdiction(mcp))
    registered.extend(register_memory(mcp))
    registered.extend(register_seal_readiness(mcp))
    registered.extend(register_evidence_resources(mcp))
    registered.extend(register_embodied_resources(mcp))
    registered.extend(register_tree777_resources(mcp))
    return registered
