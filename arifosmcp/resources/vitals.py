"""
arifos://vitals — Constitutional Vitals Reference (Ω)
═════════════════════════════════════════════════════
Static reference thresholds. Dynamic values via arif_measure.
This resource defines what the metrics MEAN, not what they currently ARE.
"""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.resources.types import TextResource

VITALS_TEXT = """\
---arifos_meta
resource_class: reference
authority_level: SOVEREIGN_CANON
owner: ARIF_FAZIL
version: 2026.06.21
mutation_allowed: false
requires_actor_verified: true
requires_session: true
lease_required: false
blast_radius: LOW
evidence_level: CANONICAL
staleness_policy: fail_closed
last_attested: 2026-06-22T00:00:00Z
truth_level: 1  # SOVEREIGN_CANON (1-7 scale)
---end_arifos_meta

arifOS Vitals — Metric Reference & Thresholds (Ω)

DYNAMIC VALUES: Use arif_measure(mode=health) for live telemetry.
This resource defines the reference thresholds and what each metric means.

METRIC DICTIONARY:

  G-score (genius)
    Range: 0.0–1.0
    Green: ≥ 0.85  |  Yellow: 0.60–0.85  |  Red: < 0.60
    What: Intelligence quality metric — correctness, elegance, efficiency.

  ΔS (entropy delta)
    Range: -1.0–1.0
    Green: ≤ 0.02  |  Yellow: 0.02–0.10  |  Red: > 0.10
    What: Net entropy change. Negative = order increasing (good).

  Ω_ortho (orthogonality)
    Range: 0.0–1.0
    Green: ≥ 0.83  |  Yellow: 0.50–0.83  |  Red: < 0.50
    What: Cross-domain structural independence. Higher = more diverse thinking.

  Ψ (peace squared / paradox tension)
    Range: 0.0–1.0
    Green: ≥ 0.5  |  Yellow: 0.25–0.5  |  Red: < 0.25
    What: Constitutional stability. Low Ψ = floors under stress.

  C_dark (hallucination coefficient)
    Range: 0.0–1.0
    Green: < 0.15  |  Yellow: 0.15–0.30  |  Red: > 0.30
    What: Composite of H (0.25) + ToM (0.25) + Scar (0.20) + Gödel (0.15) + Humility (0.15).
    Threshold for SEAL: C_dark < 0.30.

  metabolic_flux
    Range: 0.0–1.0
    Compulsory reallocation: ≥ 0.65
    System hold: ≥ 0.85
    What: Unified thermodynamic entropy rate across cognitive + machine substrates.

RESOURCE METRICS (via arif_measure):
  CPU, Memory, Disk, Load, Swap — standard system telemetry.
  Check /health endpoint or arif_measure(mode=topology) for federation map.

DITEMPA BUKAN DIBERI
"""


def register_vitals(mcp: FastMCP) -> list[str]:
    """Register arifos://vitals — static metric thresholds reference."""
    resource = TextResource(
        uri="arifos://vitals",
        name="Constitutional Vitals Reference",
        description=(
            "Static reference for constitutional vitals: metric definitions, "
            "green/yellow/red thresholds, and what each metric means. "
            "For LIVE values, use arif_measure(mode=health). "
            "This resource is the dictionary, not the reading."
        ),
        text=VITALS_TEXT,
    )
    mcp.add_resource(resource)
    return ["arifos://vitals"]
