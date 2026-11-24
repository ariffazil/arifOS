"""floor_projections.py -- P0-2 single-state floor measurement projections.

One canonical per-floor measurement state (_floor_detail) -> every projection
derives from it. Provenance stays visible as evidence; it never votes on
measurement class (the old provenance-prefix filter double-classified a stale
floor as measured while the detail called it unmeasured: "13 measured +
1 unmeasured / 13").

Falsifier: any output where len(measured) + len(unmeasured) != len(detail),
where a floor lands in both lists, or where an unmeasured floor renders as
healthy.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping

UNMEASURED = "unmeasured"
MEASURED = "measured"


def derive_measurement_state(floor_detail: Mapping[str, Any]) -> Dict[str, str]:
    return {fid: (UNMEASURED if st == UNMEASURED else MEASURED) for fid, st in floor_detail.items()}


def derive_projections(
    floor_detail: Mapping[str, Any],
    floor_provenance: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    state = derive_measurement_state(floor_detail)
    prov = dict(floor_provenance or {})
    return {
        "floors_measurement_status": state,
        "floors_measured": sorted(f for f, s in state.items() if s == MEASURED),
        "floors_unmeasured": sorted(f for f, s in state.items() if s == UNMEASURED),
        "floors_defaulted": sorted(f for f, src in prov.items() if str(src).startswith("unmeasured_default")),
    }


def constitutional_status(floors_failing, floors_unmeasured, floors_pass_count, floors_total) -> str:
    """Three states, not two: an unmeasured floor is never silently healthy."""
    return (
        "degraded"
        if floors_failing
        else "healthy"
        if not floors_unmeasured and floors_pass_count >= floors_total
        else "partial"
    )
