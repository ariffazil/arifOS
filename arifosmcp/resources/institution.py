"""
arifos://institution — Institutional Ontology
═══════════════════════════════════════════════
Seven federation organs, four constitutional lanes, five
autonomy bands, and the definition of institution itself.
"""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.resources.types import TextResource

INSTITUTION_TEXT = """\
arifOS Institution — Organs, Lanes, Autonomy Bands

AN INSTITUTION is an organ with an authority boundary,
a distinct context, and accountability.

SEVEN ORGANS:
  1. arifOS — DECIDES. Issues verdict terms; none other may.
  2. A-FORGE — EXECUTES. Builds and deploys; gated, never autonomous.
  3. GEOX — WITNESSES. Physical evidence; assessment only.
  4. WEALTH — COMPUTES. Valuation and constraint; computation only.
  5. WELL — REFLECTS. Reads human state; reflects, never decides.
  6. AAA — OPERATES. Control plane; not a decision authority.
  7. APEX — JUDGES. Constitutional verdicts; only forge gate.

FOUR CONSTITUTIONAL LANES:
  AGI proposes. ASI judges. APEX authorizes. FORGE executes.

FIVE AUTONOMY BANDS:
  GREEN — read-only.
  YELLOW — controlled mutation, reversible.
  RED — high-risk, gated.
  BLACK — irreversible, sealed.
  SOVEREIGN — F13 human veto above all bands.

DITEMPA BUKAN DIBERI — Institutions are forged, not given.
"""


def register_institution(mcp: FastMCP) -> list[str]:
    """Register arifos://institution — institutional ontology."""
    resource = TextResource(
        uri="arifos://institution",
        name="Institutional Ontology",
        description=(
            "Seven federation organs as institutions (decides, executes, "
            "witnesses, computes, reflects, operates, judges), four "
            "constitutional lanes (AGI proposes, ASI judges, APEX "
            "authorizes, FORGE executes), five autonomy bands (GREEN to "
            "SOVEREIGN), and the definition of institution: authority "
            "boundary, distinct context, accountability."
        ),
        text=INSTITUTION_TEXT,
        tags={"resource", "institution", "ontology"},
    )
    mcp.add_resource(resource)
    return ["arifos://institution"]
