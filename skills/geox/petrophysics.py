"""
skills/geox/petrophysics.py — Petrophysics Computation

Porosity, saturation, and volume calculations ported from
arifosmcp/tools_canonical.py (arifos_compute_physics[petrophysics]).
"""

from __future__ import annotations

from typing import Any


def petrophysics_compute(
    well_id: str | None = None,
    computation: str | None = None,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compute petrophysical properties: porosity, saturation, or volume."""
    params = params or {}
    phi = params.get("porosity", 0.0)
    sw = params.get("water_saturation", 1.0)
    h = params.get("thickness", 0.0)
    area = params.get("area", 0.0)
    bf = params.get("formation_volume_factor", 1.0)

    if computation == "porosity":
        value, unit = phi, "fraction"
    elif computation == "saturation":
        value, unit = sw, "fraction"
    elif computation == "volume":
        value = area * h * phi * (1 - sw) / bf if bf > 0 else 0
        unit = "bbl"
    else:
        value, unit = 0.0, "fraction"

    return {
        "well_id": well_id,
        "computation": computation,
        "value": round(value, 4),
        "unit": unit,
    }
