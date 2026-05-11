"""
GEOX Subsurface Forge — Seismic Structure Rules
DITEMPA BUKAN DIBERI

Implements geological rule checks on structural candidates.
"""

from __future__ import annotations

import logging

from ..contrast_wrapper import contrast_governed_tool
from ..schemas.seismic_image import STRUCT_CANDIDATE

logger = logging.getLogger(__name__)


@contrast_governed_tool(physical_axes=["inline", "depth"])
async def check_structure_rules(
    candidates: list[STRUCT_CANDIDATE],
) -> list[STRUCT_CANDIDATE]:
    """
    Apply geological plausibility rules to filter structural candidates.
    """
    valid_candidates = []

    for cand in candidates:
        # Rule 1: No fault can have stability_score of 0 (perceptual ghosts)
        if cand.stability_score <= 0.05:
            cand.plausibility_rule_failed = ["zero_stability"]
            continue

        # Rule 2: Minimum uncertainty floor check
        if cand.uncertainty_floor < 0.1:
            cand.uncertainty_floor = 0.15  # Fix violation

        cand.final_audit_passed = True
        valid_candidates.append(cand)

    return valid_candidates
