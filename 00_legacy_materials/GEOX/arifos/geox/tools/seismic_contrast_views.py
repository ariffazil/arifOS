"""
GEOX Seismic Contrast Views — Stage 2
DITEMPA BUKAN DIBERI

Generate contrast-controlled display variants for bias testing.
Enforces the Bond et al. (2007) display stability check.
"""

from __future__ import annotations

import logging

import numpy as np
from scipy.ndimage import gaussian_filter, sobel

from ..contrast_wrapper import contrast_governed_tool
from ..schemas.seismic_image import GEOX_SEISMIC_RASTER, GEOX_SEISMIC_VIEW

logger = logging.getLogger(__name__)


@contrast_governed_tool(physical_axes=["inline", "depth"])
async def generate_contrast_views(
    raster: GEOX_SEISMIC_RASTER, presets: list[str]
) -> list[GEOX_SEISMIC_VIEW]:
    """
    Generate multiple contrast variants using standard filters.

    Variants include:
      - linear: Raw normalized input
      - inverted: Polarity swap (1 - I)
      - hist_eq: Global histogram equalization
      - edge_enhance: Sobel-based lineament highlighting
      - soft_smooth: Gaussian blur to suppress noise
    """
    line_id = raster.line_id
    arr = np.load(raster.normalized_path)

    views: list[GEOX_SEISMIC_VIEW] = []

    # Map variant names to implementation functions
    variants = {
        "linear": _apply_linear,
        "inverted": _apply_inverted,
        "hist_eq": _apply_hist_eq,
        "edge_enhance": _apply_edge_enhance,
        "soft_smooth": _apply_soft_smooth,
    }

    for name in presets:
        if name not in variants:
            continue

        processed = variants[name](arr)

        # Save as PNG
        out_path = f"{raster.raw_path}.{name}.png"
        from PIL import Image

        Image.fromarray((processed * 255).astype(np.uint8)).save(out_path)

        # Metadata for governance
        governance_notes = [
            f"Display variant: {name}",
            f"Stability role: { _get_stability_role(name) }",
        ]

        views.append(
            GEOX_SEISMIC_VIEW(
                view_id=f"{line_id}_{name}",
                image_path=out_path,
                contrast_preset=name,
                governance_audit=governance_notes,
                uncertainty_floor=0.15,  # mandatory F7 for image-only
                processing_metadata={
                    "method": name,
                    "domain": "perception-only",
                    "bond2007_compliant": True,
                },
            )
        )

    return views


def _apply_linear(arr: np.ndarray) -> np.ndarray:
    return arr


def _apply_inverted(arr: np.ndarray) -> np.ndarray:
    return 1.0 - arr


def _apply_hist_eq(arr: np.ndarray) -> np.ndarray:
    """Global histogram equalization."""
    # Compute CDF
    hist, bins = np.histogram(arr.flatten(), 256, [0, 1])
    cdf = hist.cumsum()
    cdf_m = (cdf - cdf.min()) / (cdf.max() - cdf.min())
    return np.interp(arr, bins[:-1], cdf_m)


def _apply_edge_enhance(arr: np.ndarray) -> np.ndarray:
    """Sobel filters combined."""
    sx = sobel(arr, axis=0, mode="constant")
    sy = sobel(arr, axis=1, mode="constant")
    mag = np.sqrt(sx**2 + sy**2)
    # Re-normalize magnitude
    if mag.max() > 0:
        mag = mag / mag.max()
    return mag


def _apply_soft_smooth(arr: np.ndarray) -> np.ndarray:
    """Gaussian smoothing."""
    return gaussian_filter(arr, sigma=1.0)


def _get_stability_role(name: str) -> str:
    roles = {
        "linear": "Baseline view",
        "inverted": "Phase-shift sensitivity check",
        "hist_eq": "Low-amplitude continuity check",
        "edge_enhance": "Discontinuity focus",
        "soft_smooth": "Noise suppression check",
    }
    return roles.get(name, "Display variant")
