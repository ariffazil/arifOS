"""
arifos://schema — Complete Blueprint (Δ)
═════════════════════════════════════════
Canonical tool surface, Trinity lanes, and floor bindings.
"""
from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.resources.types import TextResource


SCHEMA_TEXT = """\
arifOS Schema — Canonical Blueprint (Δ)

Tools (13 canonical):
  000 init    | 111 sense  | 222 fetch   | 333 mind
  444 kernel  | 444r reply | 555 memory  | 666 heart
  666g gateway| 777 ops    | 888 judge   | 999 vault
  010 forge

Trinity Lanes:
  AGI  (Tactical)   | stages 000–777
  ASI  (Strategic)  | stage 888
  APEX (Authority)  | stage 999

Floors:
  F01 AMANAH   | F02 TRUTH    | F03 WITNESS
  F04 CLARITY  | F05 PEACE    | F06 EMPATHY
  F07 HUMILITY | F08 GENIUS   | F09 ANTIHANTU
  F10 ONTOLOGY | F11 AUTH     | F12 INJECTION
  F13 SOVEREIGN

Conflict Resolution Protocol (CRP v1.0):
  AGI proposes → ASI evaluates → APEX authorizes
  Disagreement is a Stability Event, not a failure.

DITEMPA BUKAN DIBERI
"""


def register_schema(mcp: FastMCP) -> list[str]:
    """Register arifos://schema — Complete Blueprint (Δ)."""
    resource = TextResource(
        uri="arifos://schema",
        name="Canonical Schema",
        text=SCHEMA_TEXT,
    )
    mcp.add_resource(resource)
    return ["arifos://schema"]
