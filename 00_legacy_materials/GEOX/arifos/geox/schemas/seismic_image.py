"""
GEOX Seismic Image Schemas — Perception Layer v0.3.1
DITEMPA BUKAN DIBERI

Governed data models for seismic image interpretation (Plane 2).
Enforces Contrast Canon and Plane 2 Perception Bridge floors.
"""

from __future__ import annotations

import logging
from typing import Any, Literal

from pydantic import BaseModel, Field

from .geox_schemas import ProvenanceRecord

logger = logging.getLogger(__name__)


class GEOX_SEISMIC_IMAGE_INPUT(BaseModel):
    """Input for a single seismic image line."""

    image_path: str = Field(
        ..., description="Path to the seismic image file (PNG, JPG, etc.)"
    )
    line_id: str = Field(..., description="User-supplied identifier for the line")
    domain: Literal["time", "depth", "unknown"] = "unknown"
    polarity: Literal["normal", "reverse", "unknown"] = "unknown"
    vertical_exaggeration: float | None = Field(
        default=None, description="Visual scale exaggerated factor"
    )
    scale_known: bool = Field(
        default=False, description="Whether horizontal/vertical scale is verified"
    )
    play_type: Literal["structural", "stratigraphic", "hybrid"] = "structural"
    notes: str | None = None
    provenance: ProvenanceRecord = Field(
        ..., description="Mandatory audit trail for the input"
    )


class GEOX_SEISMIC_RASTER(BaseModel):
    """Normalized 2D seismic raster data (Plane 2 Bridge)."""

    line_id: str
    raw_path: str
    normalized_path: str
    dimensions: list[int] = Field(..., description="[height, width]")
    metadata: dict[str, Any] = Field(default_factory=dict)


class GEOX_SEISMIC_VIEW(BaseModel):
    """A processed view of a seismic image (contrast-governed)."""

    view_id: str
    parent_raster_id: str
    preset: str = Field(..., description="Filter preset used (e.g. 'sobel', 'clahe')")
    image_ref: str | None = Field(default=None, description="Path to display image")
    data_ref: str | None = Field(default=None, description="Path to numpy data")
    data: list[list[float]] | None = None  # For tool return if needed


class GEOPROXY_LINEAMENT(BaseModel):
    """Image-derived proxy (perceptual lineament). NOT geological truth."""

    lineament_id: str
    centroid_pixel: list[float]
    confidence: float = Field(ge=0.0, le=1.0)
    contrast_origin: str = Field(..., description="The preset this was extracted from")


class GEOX_FEATURE_SET(BaseModel):
    """Collection of extracted lineaments and discontinuities."""

    view_id: str
    lineaments: list[GEOPROXY_LINEAMENT] = Field(default_factory=list)
    discontinuities: list[Any] = Field(default_factory=list)


class STRUCT_CANDIDATE(BaseModel):
    """A potential structural interpretation candidate (Stage 4)."""

    candidate_id: str
    family: Literal[
        "normal_fault",
        "reverse_fault",
        "fold",
        "duplex",
        "stratigraphic",
        "flower",
        "other",
    ]
    stability_score: float = Field(
        ge=0.0, le=1.0, description="Persistence across contrast views"
    )
    bias_risk: float = Field(
        ge=0.0, le=1.0, description="Risk that this is a display artifact"
    )
    uncertainty_floor: float = Field(default=0.15, ge=0.10)
    plausibility_rule_failed: list[str] = Field(default_factory=list)
    final_audit_passed: bool = False


class GEOX_INTERPRETATION_SUMMARY(BaseModel):
    """Final governed interpretation record (Minimum Artifact Set)."""

    line_id: str
    input_raster: GEOX_SEISMIC_RASTER  # Metric 1
    contrast_views: list[GEOX_SEISMIC_VIEW]  # Metric 2
    feature_layers: list[GEOX_FEATURE_SET]  # Metric 3
    candidates: list[STRUCT_CANDIDATE] = Field(default_factory=list)  # Metric 4 & 5
    bias_audit: dict[str, Any] = Field(
        default_factory=lambda: {"display_sensitivity": "medium", "audit_notes": []}
    )  # Metric 6
    human_report: str | None = None  # Metric 7
    provenance: ProvenanceRecord
    verdict: Literal["PASS", "QUALIFY", "HOLD", "BLOCK"] = "QUALIFY"
