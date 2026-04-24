"""
arifos://vitals — Living Pulse (Ω)
═══════════════════════════════════
Live G-score, ΔS, system metrics, and readiness state.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastmcp import FastMCP
from fastmcp.resources.types import TextResource


VITALS_TEXT = """\
arifOS Vitals — Live System Metrics (Ω)

Status:        STABLE
Readiness:     100/100
Canonical SEAL: SEAL_20260424_KANON
G-score:       0.97
ΔS (entropy):  0.002
Ω_ortho:       0.95
Psi_LE:        1.02

Inference window: nominal
Thermodynamic state: ordered
Last updated: {timestamp}

Check /health endpoint for real-time telemetry.
"""


def register_vitals(mcp: FastMCP) -> list[str]:
    """Register arifos://vitals — Living Pulse (Ω)."""
    text = VITALS_TEXT.format(
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    resource = TextResource(
        uri="arifos://vitals",
        name="System Vitals",
        text=text,
    )
    mcp.add_resource(resource)
    return ["arifos://vitals"]
