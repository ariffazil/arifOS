"""
GEOX Subsurface Forge — Seismic Feature Extraction
DITEMPA BUKAN DIBERI

Implements perceptual lineament extraction from contrast views.
"""

from __future__ import annotations

import logging

import numpy as np
from scipy.ndimage import center_of_mass, label

from ..contrast_wrapper import contrast_governed_tool
from ..schemas.seismic_image import GEOPROXY_LINEAMENT, GEOX_SEISMIC_VIEW

logger = logging.getLogger(__name__)


@contrast_governed_tool(physical_axes=["inline", "depth"])
async def extract_lineaments(
    views: list[GEOX_SEISMIC_VIEW],
) -> list[list[GEOPROXY_LINEAMENT]]:
    """
    Extract perceptual lineaments from a set of contrast views.
    """
    all_lineaments = []

    for view in views:
        view_lineaments = []
        arr = np.array(view.data)

        # Simple threshold-based "lineament" extraction (proxy)
        mask = arr > 0.8
        labeled_arr, num_features = label(mask)
        centers = center_of_mass(mask, labeled_arr, range(1, num_features + 1))

        for i, center in enumerate(centers):
            view_lineaments.append(
                GEOPROXY_LINEAMENT(
                    lineament_id=f"{view.view_id}_feat_{i}",
                    centroid_pixel=list(center),
                    confidence=0.7,  # constant for proxy
                    contrast_origin=view.preset,
                )
            )

        all_lineaments.append(view_lineaments)

    return all_lineaments
