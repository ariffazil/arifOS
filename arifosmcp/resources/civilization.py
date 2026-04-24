"""
arifos://civilization — Civilizational Ontology
═══════════════════════════════════════════════
Five SEAL domains and the three intelligence strata.
"""
from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.resources.types import TextResource


CIVILIZATION_TEXT = """\
arifOS Civilization — Organs and Strata

Five SEAL Domains:
  1. arifOS
     Constitutional kernel for identity, orchestration, stage routing,
     governance enforcement, and entropy accounting.

  2. VAULT999
     Immutable memory organ for seals, irreversible actions, epistemic
     snapshots, and temporal continuity.

  3. WELL
     Biological and cognitive substrate for human physiological state,
     cognitive readiness, and metabolic constraint.

  4. WEALTH
     Economic and thermodynamic layer for capital allocation, resource
     constraint, Landauer awareness, and psi_le / omega stability.

  5. GEOX
     Physical and geospatial witness for earth grounding, asset context,
     and spatial-temporal verification.

Three Intelligence Strata:
  AGI
    Tactical intelligence for stages 000–777: local optimization,
    reversible decisions, and operational routing.

  ASI
    Strategic intelligence for stage 888: long-horizon reasoning,
    ethical arbitration, and civilizational contrast detection.

  APEX
    Authority intelligence for stage 999: irreversible sealing,
    commitment to timeline, and entropy responsibility.

Entropy responsibility model:
  - arifOS preserves structural coherence.
  - VAULT999 preserves temporal continuity.
  - WELL preserves embodiment grounding.
  - WEALTH preserves resource constraint.
  - GEOX preserves physical verification.

DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
"""


def register_civilization(mcp: FastMCP) -> list[str]:
    """Register arifos://civilization — civilizational ontology."""
    resource = TextResource(
        uri="arifos://civilization",
        name="Civilizational Ontology",
        text=CIVILIZATION_TEXT,
    )
    mcp.add_resource(resource)
    return ["arifos://civilization"]
