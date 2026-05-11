"""
GEOX View Services — UI view building logic.
Transport-agnostic view construction.
DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

from typing import Any, Literal

ViewType = Literal[
    "seismic_section",
    "structural_candidates",
    "feasibility_check",
    "geospatial",
    "prospect_verdict",
]


def build_prefab_view(
    view_type: ViewType,
    prefab_available: bool = False,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Build a prefab view structure.

    If prefab UI is available, this would call the actual view builder.
    Otherwise, returns a fallback structure with the data.

    Args:
        view_type: Type of view to build
        prefab_available: Whether the prefab UI module is available
        **kwargs: View-specific parameters

    Returns:
        View structure (dict)
    """
    # Base view structure
    view = {
        "view_type": view_type,
        "mode": "prefab" if prefab_available else "text_fallback",
    }

    # Add all kwargs
    view.update(kwargs)

    # Add timestamp if not provided
    if "timestamp" not in view:
        from datetime import datetime, timezone

        view["timestamp"] = datetime.now(timezone.utc).isoformat()

    return view


def build_seismic_section_view(
    line_id: str,
    survey_path: str,
    status: str,
    views: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build seismic section view structure."""
    return {
        "view_type": "seismic_section",
        "line_id": line_id,
        "survey_path": survey_path,
        "status": status,
        "views": views,
    }


def build_structural_candidates_view(
    line_id: str,
    candidates: list[dict[str, Any]] | None,
    verdict: str,
    confidence: float,
) -> dict[str, Any]:
    """Build structural candidates view structure."""
    return {
        "view_type": "structural_candidates",
        "line_id": line_id,
        "candidates": candidates or [],
        "count": len(candidates) if candidates else 0,
        "verdict": verdict,
        "confidence": confidence,
    }


def build_feasibility_view(
    plan_id: str,
    constraints: list[str],
    verdict: str,
    grounding_confidence: float,
) -> dict[str, Any]:
    """Build feasibility check view structure."""
    return {
        "view_type": "feasibility_check",
        "plan_id": plan_id,
        "constraints": constraints,
        "verdict": verdict,
        "grounding_confidence": grounding_confidence,
    }


def build_geospatial_view(
    lat: float,
    lon: float,
    radius_m: float,
    geological_province: str,
    jurisdiction: str,
    verdict: str,
) -> dict[str, Any]:
    """Build geospatial verification view structure."""
    return {
        "view_type": "geospatial",
        "lat": lat,
        "lon": lon,
        "radius_m": radius_m,
        "geological_province": geological_province,
        "jurisdiction": jurisdiction,
        "verdict": verdict,
        "crs": "WGS84",
    }


def build_prospect_verdict_view(
    prospect_id: str,
    interpretation_id: str,
    verdict: str,
    confidence: float,
    status: str,
    reason: str,
) -> dict[str, Any]:
    """Build prospect verdict view structure."""
    return {
        "view_type": "prospect_verdict",
        "prospect_id": prospect_id,
        "interpretation_id": interpretation_id,
        "verdict": verdict,
        "confidence": confidence,
        "status": status,
        "reason": reason,
    }
