"""
GEOX Subsurface Forge — Seismic Candidate Ranker
DITEMPA BUKAN DIBERI

Implements stability-based ranking of structural candidates.
"""

from __future__ import annotations

import logging

from ..contrast_wrapper import contrast_governed_tool
from ..schemas.seismic_image import GEOPROXY_LINEAMENT, STRUCT_CANDIDATE

logger = logging.getLogger(__name__)


@contrast_governed_tool(physical_axes=["inline", "depth"])
async def rank_candidates(
    lineaments_per_view: list[list[GEOPROXY_LINEAMENT]],
) -> list[STRUCT_CANDIDATE]:
    """
    Rank structural candidates by stability across different contrast views.
    """
    # Stability algorithm: how many views found a similar lineament?
    candidate_map = {}

    view_count = len(lineaments_per_view)
    if view_count == 0:
        return []

    for view_features in lineaments_per_view:
        for feat in view_features:
            # Simple spatial binning for stability matching (mock)
            bin_id = f"pos_{int(feat.centroid_pixel[0]/5)}_{int(feat.centroid_pixel[1]/5)}"
            if bin_id not in candidate_map:
                candidate_map[bin_id] = {"lineaments": [], "stability": 0.0}
            candidate_map[bin_id]["lineaments"].append(feat)
            candidate_map[bin_id]["stability"] = (
                len(candidate_map[bin_id]["lineaments"]) / view_count
            )

    candidates = []
    for bin_id, data in candidate_map.items():
        candidates.append(
            STRUCT_CANDIDATE(
                candidate_id=bin_id,
                family="normal_fault",  # default for proxy
                stability_score=data["stability"],
                bias_risk=0.5 if data["stability"] < 0.8 else 0.1,
                uncertainty_floor=0.15,
            )
        )

    return sorted(candidates, key=lambda x: x.stability_score, reverse=True)
