"""
GEOX Stage 2: Contrast Canon Views

DITEMPA BUKAN DIBERI

Generate 6 canonical contrast view variants from canonical grayscale seismic.
Each view is a display transformation — NOT physical reality.

Contrast Canon (F9 Anti-Hantu): RGB ≠ physical truth
  - Visual perception carries uncertainty >= 0.15
  - Multiple views test stability of perceived features
  - Features seen across ALL views are more robust

6 Canonical Views:
  1. LINEAR — raw normalized grayscale
  2. CLAHE — contrast-limited adaptive histogram equalization
  3. EDGE_ENHANCED — Sobel/Kirsch edge detection overlay
  4. HISTOGRAM_EQ — global histogram equalization
  5. LOW_BAND_EMPHASIS — emphasizes continuous reflectors
  6. HIGH_BAND_EMPHASIS — emphasizes discontinuities/faults
  7. VE_1X, VE_2X, VE_5X — vertical exaggeration variants

Stage 2: Canonical grayscale → 6 display-transformed views
  - Each view: 2D uint8 array for display
  - contrast_metadata per view: colormap, dynamic_range, gamma, VE
  - uncertainty per view: 0.12-0.18 depending on enhancement type

Constitutional floors:
  F4  Clarity — Visual vs physical explicitly separated
  F7  Humility — Uncertainty >= 0.12 for enhanced views
  F9  Anti-Hantu — Perceptual ≠ physical truth, no SEAL from views alone
"""

from __future__ import annotations

import hashlib

import numpy as np

from arifos.geox.base_tool import _make_provenance
from arifos.geox.geox_mcp_schemas import (
    ContrastViewType,
    GEOXContrastViewSet,
    GEOXSeismicView,
)


def apply_clahe(
    array: np.ndarray,
    clip_limit: float = 2.0,
    tile_grid_size: tuple[int, int] = (8, 8),
) -> np.ndarray:
    """
    Contrast-Limited Adaptive Histogram Equalization.

    Simulated here — in production would use cv2.createCLAHE.
    """
    rng = np.random.default_rng(42)

    h, w = array.shape
    tile_h, tile_w = tile_grid_size

    result = np.zeros_like(array)

    for i in range(0, h, tile_h):
        for j in range(0, w, tile_w):
            tile = array[i : i + tile_h, j : j + tile_w]

            hist, bins = np.histogram(tile.flatten(), 256, (0, 1))
            cdf = np.cumsum(hist)
            cdf = cdf / cdf[-1]

            equalized = np.interp(tile.flatten(), bins[:-1], cdf).reshape(tile.shape)

            mean_val = float(np.mean(tile))
            clip = clip_limit * mean_val / 256.0
            excess = np.maximum(equalized - clip, 0)
            equalized = np.minimum(equalized, clip)
            equalized += (
                excess * (mean_val - clip) / (1.0 - clip) if mean_val > clip else 0
            )

            result[i : i + tile_h, j : j + tile_w] = equalized

    noise = rng.random(array.shape) * 0.01
    result = np.clip(result + noise, 0, 1)

    return result.astype(np.float32)


def apply_edge_enhancement(array: np.ndarray) -> np.ndarray:
    """
    Sobel-based edge enhancement overlay.

    In production: cv2.Sobel or cv2.Kirsch kernels.
    """
    sobel_x = np.zeros_like(array)
    sobel_y = np.zeros_like(array)

    sobel_x[:, 1:-1] = array[:, 2:] - array[:, :-2]
    sobel_y[1:-1, :] = array[2:, :] - array[:-2, :]

    gradient_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)

    enhanced = array + 0.3 * gradient_magnitude

    return np.clip(enhanced, 0, 1).astype(np.float32)


def apply_histogram_equalization(array: np.ndarray) -> np.ndarray:
    """Global histogram equalization."""
    flat = array.flatten()
    hist, bins = np.histogram(flat, 256, (0, 1))
    cdf = np.cumsum(hist)
    cdf = cdf / cdf[-1]

    equalized = np.interp(flat, bins[:-1], cdf).reshape(array.shape)
    return equalized.astype(np.float32)


def apply_low_band_emphasis(array: np.ndarray, kernel_size: int = 5) -> np.ndarray:
    """Low-pass filter emphasizing continuous reflectors."""
    kernel = np.ones((kernel_size, kernel_size)) / (kernel_size * kernel_size)
    h, w = array.shape
    pad = kernel_size // 2

    padded = np.pad(array, pad, mode="edge")
    smoothed = np.zeros_like(array)

    for i in range(h):
        for j in range(w):
            smoothed[i, j] = float(
                np.sum(padded[i : i + kernel_size, j : j + kernel_size] * kernel)
            )

    return 0.7 * array + 0.3 * smoothed.astype(np.float32)


def apply_high_band_emphasis(array: np.ndarray) -> np.ndarray:
    """High-pass filter emphasizing discontinuities."""
    low_passed = apply_low_band_emphasis(array, kernel_size=5)
    high_passed = array - 0.5 * low_passed
    return np.clip(high_passed, 0, 1).astype(np.float32)


def to_uint8_display(array: np.ndarray) -> np.ndarray:
    """Convert float32 [0,1] to uint8 [0,255] display array."""
    return (np.clip(array, 0, 1) * 255).astype(np.uint8)


async def generate_contrast_views(
    canonical_array: np.ndarray,
    image_ref: str,
    include_ve_variants: bool = True,
    provenance_hash: str | None = None,
) -> GEOXContrastViewSet:
    """
    Stage 2: Generate 6 canonical contrast views from grayscale seismic.

    Args:
        canonical_array: 2D float32 [0, 1] grayscale seismic
        image_ref: Unique image reference
        include_ve_variants: Include VE_1X, VE_2X, VE_5X variants
        provenance_hash: Optional hash for provenance

    Returns:
        GEOXContrastViewSet with 6-9 views, each carrying uncertainty
    """
    if canonical_array.ndim != 2:
        raise ValueError(f"Expected 2D array, got {canonical_array.ndim}D")

    h, w = canonical_array.shape
    prov_base = provenance_hash or hashlib.sha256(image_ref.encode()).hexdigest()[:8]

    views: list[GEOXSeismicView] = []

    view_configs = [
        (
            ContrastViewType.LINEAR,
            canonical_array.copy(),
            0.12,
            {"colormap": "gray_inverted", "dynamic_range": "p2-p98", "gamma": 1.0},
        ),
        (
            ContrastViewType.CLAHE,
            apply_clahe(canonical_array, clip_limit=2.0),
            0.14,
            {
                "colormap": "gray_inverted",
                "dynamic_range": "full",
                "gamma": 1.0,
                "clahe_clip": 2.0,
            },
        ),
        (
            ContrastViewType.EDGE_ENHANCED,
            apply_edge_enhancement(canonical_array),
            0.16,
            {
                "colormap": "gray_inverted",
                "dynamic_range": "p1-p99",
                "gamma": 0.8,
                "edge_weight": 0.3,
            },
        ),
        (
            ContrastViewType.HISTOGRAM_EQ,
            apply_histogram_equalization(canonical_array),
            0.15,
            {"colormap": "gray_inverted", "dynamic_range": "full", "gamma": 1.0},
        ),
        (
            ContrastViewType.LOW_BAND_EMPHASIS,
            apply_low_band_emphasis(canonical_array),
            0.13,
            {
                "colormap": "gray_inverted",
                "dynamic_range": "p2-p98",
                "gamma": 1.0,
                "lowpass_kernel": 5,
            },
        ),
        (
            ContrastViewType.HIGH_BAND_EMPHASIS,
            apply_high_band_emphasis(canonical_array),
            0.16,
            {
                "colormap": "gray_inverted",
                "dynamic_range": "p1-p99",
                "gamma": 0.9,
                "highpass_weight": 0.5,
            },
        ),
    ]

    if include_ve_variants:
        view_configs.extend(
            [
                (
                    ContrastViewType.VE_1X,
                    canonical_array.copy(),
                    0.12,
                    {
                        "colormap": "gray_inverted",
                        "dynamic_range": "p2-p98",
                        "gamma": 1.0,
                        "ve": 1.0,
                    },
                ),
                (
                    ContrastViewType.VE_2X,
                    canonical_array.copy(),
                    0.13,
                    {
                        "colormap": "gray_inverted",
                        "dynamic_range": "p2-p98",
                        "gamma": 1.0,
                        "ve": 2.0,
                    },
                ),
                (
                    ContrastViewType.VE_5X,
                    canonical_array.copy(),
                    0.15,
                    {
                        "colormap": "gray_inverted",
                        "dynamic_range": "p1-p99",
                        "gamma": 1.0,
                        "ve": 5.0,
                    },
                ),
            ]
        )

    for view_type, transformed, uncertainty, display_params in view_configs:
        view_id = f"{image_ref}_{view_type.value}"
        prov = _make_provenance(
            f"VIEW-{view_type.value.upper()}-{prov_base}",
            "LEM",
            confidence=1.0 - uncertainty,
        )

        view = GEOXSeismicView(
            view_id=view_id,
            view_type=view_type,
            display_array=to_uint8_display(transformed),
            colormap=display_params["colormap"],
            dynamic_range=display_params["dynamic_range"],
            gamma=display_params.get("gamma", 1.0),
            vertical_exaggeration_display=display_params.get("ve", 1.0),
            contrast_enhancement_factor=display_params.get("clahe_clip", 1.0),
            provenance=prov,
            uncertainty=uncertainty,
            telemetry={
                "stage": 2,
                "view_type": view_type.value,
                "original_shape": [h, w],
                "floors": ["F4", "F7", "F9"],
                "seal": "DITEMPA BUKAN DIBERI",
            },
        )
        views.append(view)

    canonical_view_ref = next(
        v.view_id for v in views if v.view_type == ContrastViewType.LINEAR
    )

    worst_uncertainty = max(v.uncertainty for v in views)

    prov_set = _make_provenance(
        f"VIEWSET-{prov_base}", "LEM", confidence=1.0 - worst_uncertainty
    )

    return GEOXContrastViewSet(
        image_ref=image_ref,
        views=views,
        canonical_view_ref=canonical_view_ref,
        provenance=prov_set,
        aggregate_uncertainty=worst_uncertainty,
        telemetry={
            "stage": 2,
            "n_views": len(views),
            "floors": ["F4", "F7", "F9"],
            "seal": "DITEMPA BUKAN DIBERI",
        },
    )
