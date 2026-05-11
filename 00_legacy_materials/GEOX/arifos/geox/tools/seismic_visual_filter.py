"""
arifos/geox/tools/seismic_visual_filter.py — Seismic Visual Filter Tool
DITEMPA BUKAN DIBERI

Plane 2 — Perception Layer: Classical image filtering for seismic data.

Implements five filter families for seismic image enhancement:
  1. Gaussian   — denoise and continuity enhancement
  2. Mean       — baseline blur for comparison
  3. Kuwahara   — edge-preserving smoothing (reflector continuity + boundary retention)
  4. Sobel/Canny — gradient/edge detection (fault-edge, reflector-boundary emphasis)
  5. CLAHE      — adaptive histogram equalization (amplitude contrast in grayscale)

PERCEPTION BRIDGE RULE (Contract 2):
  RGB ≠ truth. Visual enhancement is hypothesis support, not geological confirmation.
  All outputs carry uncertainty ≥ 0.15 and require non-visual corroboration.

Constitutional notes:
  F4  Clarity: every output carries units, filter parameters, and provenance
  F7  Humility: VLM/perception uncertainty ≥ 0.15 (Perception Bridge floor)
  F9  Anti-Hantu: no hallucinated geology — filter outputs are labelled as
      "visual_enhancement_only", never as geological truth
  F11 Authority: full provenance chain for every filter result
"""

from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np

from arifos.geox.base_tool import (
    BaseTool,
    GeoToolResult,
    _make_provenance,
    _make_quantity,
)
from arifos.geox.geox_schemas import CoordinatePoint

logger = logging.getLogger("geox.tools.seismic_visual_filter")


# ---------------------------------------------------------------------------
# Filter Type Enum
# ---------------------------------------------------------------------------


class FilterType(str, Enum):
    """Supported seismic visual filter families."""

    GAUSSIAN = "gaussian"
    MEAN = "mean"
    KUWAHARA = "kuwahara"
    SOBEL = "sobel"
    CANNY = "canny"
    CLAHE = "clahe"


# ---------------------------------------------------------------------------
# Filter Result (internal)
# ---------------------------------------------------------------------------


@dataclass
class FilterResult:
    """Internal result from a single filter application."""

    filter_type: str
    params: dict[str, Any]
    output_array: np.ndarray
    metric_contrast: float  # contrast ratio after filtering
    metric_edge_density: float  # edge pixel density (Sobel magnitude > threshold)
    processing_time_ms: float
    notes: str


# ---------------------------------------------------------------------------
# Core Filter Implementations (NumPy-only, no OpenCV required for mock)
# ---------------------------------------------------------------------------


def _gaussian_filter(image: np.ndarray, kernel_size: int = 5, sigma: float = 1.4) -> FilterResult:
    """Gaussian smoothing for denoise and continuity enhancement."""
    start = time.perf_counter()

    # Build Gaussian kernel
    ks = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
    ax = np.arange(-ks // 2 + 1.0, ks // 2 + 1.0)
    xx, yy = np.meshgrid(ax, ax)
    kernel = np.exp(-(xx**2 + yy**2) / (2.0 * sigma**2))
    kernel /= kernel.sum()

    output = _convolve2d(image, kernel)
    elapsed = (time.perf_counter() - start) * 1000

    return FilterResult(
        filter_type="gaussian",
        params={"kernel_size": ks, "sigma": sigma},
        output_array=output,
        metric_contrast=_compute_contrast(output),
        metric_edge_density=_compute_edge_density(output),
        processing_time_ms=round(elapsed, 2),
        notes="Gaussian smoothing applied. Reduces noise, enhances reflector continuity.",
    )


def _mean_filter(image: np.ndarray, kernel_size: int = 5) -> FilterResult:
    """Mean (box) filter for baseline blur comparison."""
    start = time.perf_counter()

    ks = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
    kernel = np.ones((ks, ks), dtype=np.float64) / (ks * ks)

    output = _convolve2d(image, kernel)
    elapsed = (time.perf_counter() - start) * 1000

    return FilterResult(
        filter_type="mean",
        params={"kernel_size": ks},
        output_array=output,
        metric_contrast=_compute_contrast(output),
        metric_edge_density=_compute_edge_density(output),
        processing_time_ms=round(elapsed, 2),
        notes="Mean filter applied. Uniform blur for baseline comparison against edge-preserving methods.",
    )


def _kuwahara_filter(image: np.ndarray, window_size: int = 5) -> FilterResult:
    """
    Kuwahara filter — edge-preserving smoothing.

    Divides each pixel neighbourhood into four overlapping quadrants,
    computes mean and variance in each, and assigns the pixel the mean
    of the quadrant with lowest variance. Preserves discontinuity
    boundaries while smoothing reflector textures.
    """
    start = time.perf_counter()

    ws = window_size if window_size % 2 == 1 else window_size + 1
    r = ws // 2
    h, w = image.shape[:2]
    img = image.astype(np.float64)

    # Zero-pad
    padded = np.pad(img, r, mode="reflect")
    output = np.zeros_like(img)

    for y in range(h):
        for x in range(w):
            py, px = y + r, x + r
            # Four quadrants (overlapping sub-windows)
            quads = [
                padded[py - r : py + 1, px - r : px + 1],  # top-left
                padded[py - r : py + 1, px : px + r + 1],  # top-right
                padded[py : py + r + 1, px - r : px + 1],  # bottom-left
                padded[py : py + r + 1, px : px + r + 1],  # bottom-right
            ]
            means = [q.mean() for q in quads]
            variances = [q.var() for q in quads]
            best = int(np.argmin(variances))
            output[y, x] = means[best]

    output = np.clip(output, 0, 255).astype(np.uint8) if image.dtype == np.uint8 else output
    elapsed = (time.perf_counter() - start) * 1000

    return FilterResult(
        filter_type="kuwahara",
        params={"window_size": ws},
        output_array=output,
        metric_contrast=_compute_contrast(output),
        metric_edge_density=_compute_edge_density(output),
        processing_time_ms=round(elapsed, 2),
        notes=(
            "Kuwahara edge-preserving filter applied. Smooths reflector texture while "
            "retaining discontinuity boundaries. Interesting for fault-boundary emphasis."
        ),
    )


def _sobel_filter(image: np.ndarray) -> FilterResult:
    """Sobel gradient filter for fault-edge and reflector-boundary emphasis."""
    start = time.perf_counter()

    img = image.astype(np.float64)
    # Sobel kernels
    kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64)
    ky = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float64)

    gx = _convolve2d(img, kx)
    gy = _convolve2d(img, ky)
    magnitude = np.sqrt(gx**2 + gy**2)

    # Normalize to [0, 255] for visualization
    if magnitude.max() > 0:
        magnitude = (magnitude / magnitude.max() * 255).astype(np.uint8)

    elapsed = (time.perf_counter() - start) * 1000

    return FilterResult(
        filter_type="sobel",
        params={"operator": "3x3_sobel"},
        output_array=magnitude,
        metric_contrast=_compute_contrast(magnitude),
        metric_edge_density=_compute_edge_density(magnitude),
        processing_time_ms=round(elapsed, 2),
        notes=(
            "Sobel gradient magnitude computed. Emphasizes fault-edges and reflector "
            "boundaries. PLAUSIBLE as engineering starter — not geological truth."
        ),
    )


def _canny_filter(
    image: np.ndarray,
    low_threshold: float = 50.0,
    high_threshold: float = 150.0,
) -> FilterResult:
    """
    Simplified Canny edge detection.

    For seismic: emphasizes discontinuities (faults, unconformities).
    Uses Sobel gradient + non-maximum suppression + double thresholding.
    """
    start = time.perf_counter()

    # Step 1: Gaussian pre-smooth (σ=1.4)
    gauss_result = _gaussian_filter(image, kernel_size=5, sigma=1.4)
    smoothed = gauss_result.output_array.astype(np.float64)

    # Step 2: Sobel gradients
    kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64)
    ky = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float64)
    gx = _convolve2d(smoothed, kx)
    gy = _convolve2d(smoothed, ky)
    magnitude = np.sqrt(gx**2 + gy**2)

    # Step 3: Double threshold
    strong = magnitude > high_threshold
    weak = (magnitude >= low_threshold) & (magnitude <= high_threshold)

    # Simple hysteresis: weak pixels adjacent to strong become strong
    output = np.zeros_like(magnitude, dtype=np.uint8)
    output[strong] = 255

    # One-pass connectivity for weak edges
    h, w = output.shape[:2]
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if weak[y, x]:
                if output[y - 1 : y + 2, x - 1 : x + 2].max() == 255:
                    output[y, x] = 255

    elapsed = (time.perf_counter() - start) * 1000

    return FilterResult(
        filter_type="canny",
        params={"low_threshold": low_threshold, "high_threshold": high_threshold},
        output_array=output,
        metric_contrast=_compute_contrast(output),
        metric_edge_density=_compute_edge_density(output),
        processing_time_ms=round(elapsed, 2),
        notes=(
            "Canny edge detection applied. Detects discontinuities (faults, unconformities). "
            "PLAUSIBLE for structural boundary detection — requires geophysical verification."
        ),
    )


def _clahe_filter(
    image: np.ndarray,
    clip_limit: float = 2.0,
    tile_size: int = 8,
) -> FilterResult:
    """
    Contrast Limited Adaptive Histogram Equalization (CLAHE).

    Enhances amplitude contrast in grayscale seismic slices.
    Operates on tiles to adapt to local contrast variations.
    """
    start = time.perf_counter()

    img = image.astype(np.float64)
    h, w = img.shape[:2]
    output = np.zeros_like(img)

    # Tile-based adaptive equalization
    ty = max(1, h // tile_size)
    tx = max(1, w // tile_size)

    for i in range(tile_size):
        for j in range(tile_size):
            y0 = i * ty
            y1 = min((i + 1) * ty, h)
            x0 = j * tx
            x1 = min((j + 1) * tx, w)

            if y1 <= y0 or x1 <= x0:
                continue

            tile = img[y0:y1, x0:x1]

            # Local histogram equalization with clipping
            tile_flat = tile.flatten()
            if tile_flat.max() == tile_flat.min():
                output[y0:y1, x0:x1] = tile
                continue

            # Normalize to [0, 255] range for histogram
            normalized = ((tile - tile.min()) / (tile.max() - tile.min()) * 255).astype(np.uint8)
            hist, bins = np.histogram(normalized.flatten(), bins=256, range=(0, 256))

            # Clip histogram
            excess = 0
            clip_val = int(clip_limit * hist.mean())
            for k in range(256):
                if hist[k] > clip_val:
                    excess += hist[k] - clip_val
                    hist[k] = clip_val

            # Redistribute excess
            redistribute = excess // 256
            hist += redistribute

            # CDF
            cdf = hist.cumsum()
            cdf_min = cdf[cdf > 0].min() if (cdf > 0).any() else 0
            total = cdf.max()
            if total > cdf_min:
                cdf_normalized = (cdf - cdf_min) / (total - cdf_min) * 255
            else:
                cdf_normalized = np.zeros(256)

            equalized = cdf_normalized[normalized].reshape(tile.shape)
            output[y0:y1, x0:x1] = equalized

    output = np.clip(output, 0, 255).astype(np.uint8) if image.dtype == np.uint8 else output
    elapsed = (time.perf_counter() - start) * 1000

    return FilterResult(
        filter_type="clahe",
        params={"clip_limit": clip_limit, "tile_size": tile_size},
        output_array=output,
        metric_contrast=_compute_contrast(output),
        metric_edge_density=_compute_edge_density(output),
        processing_time_ms=round(elapsed, 2),
        notes=(
            "CLAHE applied. Enhances local amplitude contrast in seismic slices. "
            "Suitable as preprocessing for downstream attribute analysis."
        ),
    )


# ---------------------------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------------------------


def _convolve2d(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Simple 2D convolution with reflect-padding. Pure NumPy."""
    kh, kw = kernel.shape
    ph, pw = kh // 2, kw // 2
    padded = np.pad(image, ((ph, ph), (pw, pw)), mode="reflect")
    h, w = image.shape[:2]
    output = np.zeros((h, w), dtype=np.float64)

    for y in range(h):
        for x in range(w):
            region = padded[y : y + kh, x : x + kw]
            output[y, x] = (region * kernel).sum()

    return output


def _compute_contrast(image: np.ndarray) -> float:
    """RMS contrast of the image (normalized)."""
    img = image.astype(np.float64)
    if img.max() == img.min():
        return 0.0
    normalized = (img - img.min()) / (img.max() - img.min())
    return float(np.std(normalized))


def _compute_edge_density(image: np.ndarray, threshold_frac: float = 0.3) -> float:
    """Fraction of pixels above a gradient threshold (edge density metric)."""
    img = image.astype(np.float64)
    if img.max() == 0:
        return 0.0
    normalized = img / img.max()
    return float(np.mean(normalized > threshold_frac))


def _image_checksum(image: np.ndarray) -> str:
    """SHA-256 checksum of image data for F1 auditability."""
    return hashlib.sha256(image.tobytes()).hexdigest()[:16]


def load_seismic_slice(path: str | Path) -> np.ndarray:
    """
    Load a seismic slice from file. Supports:
      - .npy (NumPy array)
      - .png/.jpg/.tif (via PIL/Pillow, auto-converted to grayscale)

    Returns a 2D grayscale numpy array.
    """
    path = Path(path)

    if path.suffix == ".npy":
        arr = np.load(str(path))
        if arr.ndim == 3:
            # Convert RGB to grayscale: 0.299R + 0.587G + 0.114B
            arr = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
        return arr.astype(np.float64)

    # Try PIL for image formats
    try:
        from PIL import Image

        img = Image.open(str(path)).convert("L")  # Grayscale
        return np.array(img, dtype=np.float64)
    except ImportError as exc:
        raise ImportError(
            "Pillow is required for image file loading. " "Install with: pip install Pillow"
        ) from exc


# ---------------------------------------------------------------------------
# Filter Dispatch Map
# ---------------------------------------------------------------------------

_FILTER_DISPATCH: dict[str, Any] = {
    FilterType.GAUSSIAN: _gaussian_filter,
    FilterType.MEAN: _mean_filter,
    FilterType.KUWAHARA: _kuwahara_filter,
    FilterType.SOBEL: _sobel_filter,
    FilterType.CANNY: _canny_filter,
    FilterType.CLAHE: _clahe_filter,
}


# ---------------------------------------------------------------------------
# Public API Functions
# ---------------------------------------------------------------------------


def apply_filter(
    image: np.ndarray,
    filter_type: str | FilterType,
    params: dict[str, Any] | None = None,
) -> FilterResult:
    """
    Apply a single filter to a seismic image.

    Args:
        image: 2D grayscale numpy array (seismic slice).
        filter_type: One of 'gaussian', 'mean', 'kuwahara', 'sobel', 'canny', 'clahe'.
        params: Optional filter-specific parameters (kernel_size, sigma, etc.).

    Returns:
        FilterResult with output array, metrics, and notes.
    """
    ft = FilterType(filter_type) if isinstance(filter_type, str) else filter_type
    fn = _FILTER_DISPATCH[ft]
    kwargs = params or {}
    return fn(image, **kwargs)


def generate_filter_stack(image: np.ndarray) -> list[FilterResult]:
    """
    Apply all five filter families to a seismic image.

    Returns a list of FilterResults — one per filter type.
    Useful for comparative analysis of which filter best
    highlights discontinuities or reflectors.
    """
    stack = []
    for ft in [
        FilterType.GAUSSIAN,
        FilterType.MEAN,
        FilterType.KUWAHARA,
        FilterType.SOBEL,
        FilterType.CANNY,
        FilterType.CLAHE,
    ]:
        try:
            result = apply_filter(image, ft)
            stack.append(result)
        except Exception as exc:
            logger.warning(f"Filter {ft.value} failed: {exc}")
    return stack


def compare_filter_response(filter_stack: list[FilterResult]) -> dict[str, Any]:
    """
    Rank filter results by which best highlights discontinuities or reflectors.

    Uses composite score: 0.4 * contrast + 0.6 * edge_density.

    Returns a ranked comparison dict with scores and recommended filter.
    """
    if not filter_stack:
        return {"error": "Empty filter stack", "ranking": []}

    scored = []
    for result in filter_stack:
        composite = 0.4 * result.metric_contrast + 0.6 * result.metric_edge_density
        scored.append(
            {
                "filter": result.filter_type,
                "contrast": round(result.metric_contrast, 4),
                "edge_density": round(result.metric_edge_density, 4),
                "composite_score": round(composite, 4),
                "processing_time_ms": result.processing_time_ms,
                "notes": result.notes,
            }
        )

    scored.sort(key=lambda x: x["composite_score"], reverse=True)

    return {
        "ranking": scored,
        "best_filter": scored[0]["filter"],
        "best_score": scored[0]["composite_score"],
        "disclaimer": (
            "VISUAL ENHANCEMENT ONLY. This ranking reflects image-processing "
            "metrics (contrast, edge density), NOT geological significance. "
            "RGB ≠ truth. Require non-visual confirmation (LEM, well logs, "
            "simulator) before treating any visual enhancement as geological evidence."
        ),
    }


def emit_visual_hypothesis(
    comparison: dict[str, Any],
    image_path: str = "",
    context: str = "",
) -> dict[str, Any]:
    """
    Emit a structured visual hypothesis with mandatory uncertainty
    and perception bridge disclaimer.

    This is the final output wrapper — never claims geological truth.
    """
    return {
        "hypothesis_type": "visual_enhancement_hypothesis",
        "pipeline_stage": "222_REFLECT",
        "source_image": image_path,
        "context": context,
        "best_filter": comparison.get("best_filter", "unknown"),
        "composite_score": comparison.get("best_score", 0.0),
        "ranking": comparison.get("ranking", []),
        "uncertainty": 0.15,  # F7 Perception Bridge floor
        "status": "unverified",  # Always unverified until non-visual confirmation
        "perception_bridge_warning": (
            "CONTRACT 2 ACTIVE: This output is visual enhancement only, "
            "not geological confirmation. VLM/perception uncertainty floor "
            "is 0.15. Must be confirmed by non-visual Earth tool before "
            "status can be promoted to 'supported'. "
            "RGB ≠ truth (F9 Anti-Hantu)."
        ),
        "requires_confirmation_by": [
            "EarthModelTool",
            "SimulatorTool",
            "GeoRAGTool",
            "well_log_data",
        ],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "seal": "DITEMPA BUKAN DIBERI",
    }


# ---------------------------------------------------------------------------
# SeismicVisualFilterTool — GEOX BaseTool Implementation
# ---------------------------------------------------------------------------


class SeismicVisualFilterTool(BaseTool):
    """
    GEOX Plane 2 Perception Tool: Seismic Visual Filtering.

    Applies classical image filters to seismic data for visual
    enhancement and hypothesis generation. Implements all five
    filter families: Gaussian, Mean, Kuwahara, Sobel/Canny, CLAHE.

    CRITICAL — Perception Bridge Rule (Contract 2, F7 + F9):
        All outputs carry uncertainty ≥ 0.15.
        "visual_enhancement_only" — never geological truth.
        Corroborate with LEM, well logs, or simulator before acting.

    Inputs:
        image_path   (str)  — path to seismic slice (.npy, .png, .jpg, .tif)
        filter_type  (str)  — 'gaussian'|'mean'|'kuwahara'|'sobel'|'canny'|'clahe'|'all'
        params       (dict) — optional filter-specific parameters
        location     (CoordinatePoint) — optional geographic anchor

    Outputs (GeoQuantity types):
        - visual_contrast          [fraction] — RMS contrast ratio
        - visual_edge_density      [fraction] — edge pixel density
        - visual_composite_score   [fraction] — weighted enhancement score

    All outputs flagged as perception_only=True.
    """

    @property
    def name(self) -> str:
        return "SeismicVisualFilterTool"

    @property
    def description(self) -> str:
        return (
            "Seismic visual filter tool (Plane 2 Perception). Applies Gaussian, "
            "Mean, Kuwahara, Sobel/Canny, and CLAHE filters to seismic images. "
            "Returns visual enhancement metrics with mandatory uncertainty ≥ 0.15. "
            "RGB ≠ truth — all outputs require non-visual confirmation (Contract 2)."
        )

    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        if "image_path" not in inputs and "image_array" not in inputs:
            return False
        if "filter_type" not in inputs:
            return False
        ft = inputs["filter_type"]
        valid_types = {"gaussian", "mean", "kuwahara", "sobel", "canny", "clahe", "all"}
        if ft not in valid_types:
            return False
        return True

    async def run(self, inputs: dict[str, Any]) -> GeoToolResult:
        """Execute seismic visual filtering pipeline."""
        if not self.validate_inputs(inputs):
            return GeoToolResult(
                tool_name=self.name,
                success=False,
                error=(
                    "Invalid inputs. Required: 'image_path' (str) or 'image_array' (ndarray), "
                    "'filter_type' ('gaussian'|'mean'|'kuwahara'|'sobel'|'canny'|'clahe'|'all')."
                ),
            )

        start = time.perf_counter()
        filter_type: str = inputs["filter_type"]
        params: dict[str, Any] = inputs.get("params", {})

        # Load image
        try:
            if "image_array" in inputs:
                image = inputs["image_array"]
                if image.ndim == 3:
                    image = 0.299 * image[:, :, 0] + 0.587 * image[:, :, 1] + 0.114 * image[:, :, 2]
                image = image.astype(np.float64)
                image_path = inputs.get("image_path", "<in-memory>")
            else:
                image_path = inputs["image_path"]
                image = load_seismic_slice(image_path)
        except Exception as exc:
            return GeoToolResult(
                tool_name=self.name,
                success=False,
                error=f"Failed to load seismic image: {exc}",
            )

        # Location anchor (optional — defaults to 0,0 for non-georeferenced images)
        location = inputs.get("location", CoordinatePoint(latitude=0.0, longitude=0.0))
        if isinstance(location, dict):
            location = CoordinatePoint(**location)

        # Provenance — perception source, capped confidence
        checksum = _image_checksum(image)
        source_id = f"SVF-{checksum}"
        prov = _make_provenance(
            source_id=source_id,
            source_type="sensor",  # image data = sensor input
            confidence=0.60,  # perception-only confidence cap
            checksum=checksum,
        )

        # --- Apply filters ---
        if filter_type == "all":
            filter_results = generate_filter_stack(image)
            comparison = compare_filter_response(filter_results)
            hypothesis = emit_visual_hypothesis(comparison, str(image_path))
        else:
            filter_result = apply_filter(image, filter_type, params)
            filter_results = [filter_result]
            comparison = compare_filter_response(filter_results)
            hypothesis = emit_visual_hypothesis(comparison, str(image_path))

        # --- Build GeoQuantity outputs ---
        # Perception Bridge: uncertainty always ≥ 0.15
        perception_uncertainty = 0.15

        quantities = []
        for fr in filter_results:
            quantities.append(
                _make_quantity(
                    round(fr.metric_contrast, 4),
                    "fraction",
                    f"visual_contrast_{fr.filter_type}",
                    location,
                    prov,
                    perception_uncertainty,
                )
            )
            quantities.append(
                _make_quantity(
                    round(fr.metric_edge_density, 4),
                    "fraction",
                    f"visual_edge_density_{fr.filter_type}",
                    location,
                    prov,
                    perception_uncertainty,
                )
            )

        # Composite score for best filter
        if comparison.get("best_score"):
            quantities.append(
                _make_quantity(
                    round(comparison["best_score"], 4),
                    "fraction",
                    "visual_composite_score",
                    location,
                    prov,
                    perception_uncertainty,
                )
            )

        # --- Raw output with full audit trail ---
        raw_output = {
            "image_path": str(image_path),
            "image_shape": list(image.shape),
            "image_checksum_sha256": checksum,
            "filter_type_requested": filter_type,
            "filters_applied": [
                {
                    "filter": fr.filter_type,
                    "params": fr.params,
                    "contrast": round(fr.metric_contrast, 4),
                    "edge_density": round(fr.metric_edge_density, 4),
                    "processing_time_ms": fr.processing_time_ms,
                    "notes": fr.notes,
                }
                for fr in filter_results
            ],
            "comparison": comparison,
            "hypothesis": hypothesis,
            "perception_bridge_warning": (
                "CONTRACT 2 ACTIVE: Visual enhancement only, not geological "
                "confirmation. Uncertainty floor = 0.15. RGB ≠ truth. "
                "Corroborate with EarthModelTool, SimulatorTool, or well logs."
            ),
        }

        latency_ms = (time.perf_counter() - start) * 1000

        return GeoToolResult(
            quantities=quantities,
            raw_output=raw_output,
            metadata={
                "tool_version": "SVF-GEOX-v0.1.0",
                "perception_only": True,
                "multisensor_required": True,
                "uncertainty_floor": perception_uncertainty,
                "filters_applied": [fr.filter_type for fr in filter_results],
                "best_filter": comparison.get("best_filter", "unknown"),
                "image_checksum": checksum,
                "contract_2_active": True,
            },
            tool_name=self.name,
            latency_ms=round(latency_ms, 2),
            success=True,
        )
