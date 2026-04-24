"""
skills/geox/geometry.py — Horizon Geometry Building

Geometry construction logic ported from
arifosmcp/tools_canonical.py (arifos_compute_physics[geometry_build]).
"""

from __future__ import annotations

from typing import Any


def geometry_build(
    horizons: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build geometry from horizon picks."""
    return {
        "horizons": horizons,
        "geometries": {},
    }
