"""
GEOX MCP Schemas — Seismic Interpretation Pipeline

DITEMPA BUKAN DIBERI

Pydantic schemas for the 7-stage seismic interpretation pipeline:
  Stage 1: Image ingest
  Stage 2: Contrast canon views
  Stage 3: Feature extraction
  Stage 4-5: Structural candidates + rule engine
  Stage 6: Ranked structural models
  Stage 7: Human veto (interpretation result)

Every schema carries: provenance, uncertainty, verdict, telemetry.
RGB ≠ physical truth — visual perception carries uncertainty >= 0.15.

Ref: Bond et al. (2007) — 79% of experts mis-interpreted similar synthetic data.
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

from arifos.geox.geox_schemas import ProvenanceRecord


class ImageSourceType(Enum):
    SEGY = "segy"
    RASTER_PNG = "raster_png"
    RASTER_JPG = "raster_jpg"
    TIFF = "tiff"
    UNKNOWN = "unknown"


class TimeDepthDomain(Enum):
    TIME = "time"  # Two-way time (seconds)
    DEPTH = "depth"  # Depth (meters)
    UNKNOWN = "unknown"


class ContrastViewType(Enum):
    LINEAR = "linear"
    CLAHE = "clahe"
    EDGE_ENHANCED = "edge_enhanced"
    HISTOGRAM_EQ = "histogram_eq"
    LOW_BAND_EMPHASIS = "low_band_emphasis"
    HIGH_BAND_EMPHASIS = "high_band_emphasis"
    VE_1X = "ve_1x"
    VE_2X = "ve_2x"
    VE_5X = "ve_5x"


class Line2DVerdict(Enum):
    QUALIFY = "QUALIFY"
    HOLD = "HOLD"
    GEOX_BLOCK = "GEOX_BLOCK"


class StructuralCandidateType(Enum):
    FAULT = "fault"
    HORIZON = "horizon"
    UNCONFORMITY = "unconformity"
    FOLD = "fold"
    CHANNEL = "channel"
    MASS_TRANSPORT = "mass_transport"
    AMBIGUOUS = "ambiguous"


class TectonicSetting(Enum):
    EXTENSIONAL = "extensional"
    COMPRESSIONAL = "compressional"
    STRIKE_SLIP = "strike_slip"
    INVERSION = "inversion"
    PASSIVE_MARGIN = "passive_margin"
    UNCERTAIN = "uncertain"


# ----------------------------------------------------------------------
# Stage 1: Image Ingest
# ----------------------------------------------------------------------


class GEOXSeismicImageInput(BaseModel):
    """
    Stage 1 input — seismic image (SEG-Y or raster).

    Carries source quality flags that propagate uncertainty.
    RASTER input triggers automatic HOLD with 0.15 base uncertainty.
    """

    image_ref: str = Field(..., description="Unique reference for this seismic image")
    source_type: ImageSourceType = Field(..., description="Input data type")
    time_depth_domain: TimeDepthDomain = Field(
        default=TimeDepthDomain.UNKNOWN,
        description="Vertical axis domain",
    )
    vertical_exaggeration_known: bool = Field(
        default=False,
        description="Whether VE is calibrated",
    )
    display_params: dict[str, Any] = Field(
        default_factory=dict,
        description="Display parameters (clip, colormap, gain)",
    )
    source_quality: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Source data quality 0-1 (SEG-Y=1.0, raster=0.6)",
    )
    provenance: ProvenanceRecord = Field(..., description="Provenance of the seismic image")
    telemetry: dict[str, Any] = Field(
        default_factory=dict,
        description="Runtime telemetry",
    )

    @field_validator("source_quality")
    @classmethod
    def raster_low_quality(cls, v: float, info) -> float:
        return v

    model_config = {
        "json_schema_extra": {
            "stage": 1,
            "pipeline": "geox_interpret_single_line",
            "governance": {
                "F7_uncertainty_base": 0.10,
                "raster_uncertainty_add": 0.05,
                "verdict_ceiling": "QUALIFY",
            },
        }
    }


class GEOXIngestResult(BaseModel):
    """
    Stage 1 output — canonical grayscale seismic array + metadata.

    Canonical form: 2D numpy array (traces x samples), float32.
    Axes stripped of labels/title. Display params stored separately.
    """

    image_ref: str
    canonical_array: Any = Field(..., description="2D numpy float32 array")
    n_traces: int = Field(..., ge=1)
    n_samples: int = Field(..., ge=1)
    time_depth_domain: TimeDepthDomain
    vertical_exaggeration: float | None = Field(default=None, description="VE ratio if known")
    frame_detected: bool = Field(default=False, description="Axes/label frame detected")
    source_quality: float
    aggregate_uncertainty: float = Field(..., ge=0.03, le=0.20, description="F7 Humility band")
    verdict: str = Field(
        default="QUALIFY",
        description="SEAL|QUALIFY|HOLD|GEOX_BLOCK — ceiling for 2D is QUALIFY",
    )
    verdict_explanation: str
    provenance: ProvenanceRecord
    telemetry: dict[str, Any] = Field(
        default_factory=lambda: {
            "stage": 1,
            "floors": ["F1", "F4", "F7", "F9"],
            "seal": "DITEMPA BUKAN DIBERI",
        }
    )

    model_config = {"arbitrary_types_allowed": True}


# ----------------------------------------------------------------------
# Stage 2: Contrast Canon Views
# ----------------------------------------------------------------------


class GEOXSeismicView(BaseModel):
    """
    Stage 2 output — single contrast view variant.

    Each view is a display transformation with explicit perceptual
    vs physical separation. RGB != physical truth.
    """

    view_id: str = Field(default_factory=lambda: f"view_{uuid4().hex[:8]}")
    view_type: ContrastViewType = Field(..., description="Contrast transformation type")
    display_array: Any = Field(..., description="2D numpy uint8 display array")
    colormap: str = Field(default="gray_inverted")
    dynamic_range: str = Field(default="p2-p98")
    gamma: float = Field(default=1.0, ge=0.1, le=3.0)
    vertical_exaggeration_display: float = Field(default=1.0)
    contrast_enhancement_factor: float = Field(
        default=1.0, ge=1.0, le=10.0, description="CLAHE clip limit or equivalent"
    )
    provenance: ProvenanceRecord
    uncertainty: float = Field(..., ge=0.03, le=0.20, description="View-specific uncertainty")
    telemetry: dict[str, Any] = Field(default_factory=dict)

    model_config = {"arbitrary_types_allowed": True, "strict": False}


class GEOXContrastViewSet(BaseModel):
    """Stage 2 output — set of 6 canonical contrast views."""

    image_ref: str
    views: list[GEOXSeismicView] = Field(
        ..., min_length=1, max_length=12, description="1-12 canonical views"
    )
    canonical_view_ref: str = Field(..., description="Reference to the primary canonical view")
    provenance: ProvenanceRecord
    aggregate_uncertainty: float = Field(
        ..., ge=0.03, le=0.20, description="Worst-case view uncertainty"
    )
    telemetry: dict[str, Any] = Field(
        default_factory=lambda: {
            "stage": 2,
            "n_views": 6,
            "floors": ["F1", "F4", "F7", "F9"],
            "seal": "DITEMPA BUKAN DIBERI",
        }
    )

    model_config = {"strict": False}


# ----------------------------------------------------------------------
# Stage 3: Feature Extraction
# ----------------------------------------------------------------------


class GEOXFeatureSet(BaseModel):
    """
    Stage 3 output — extracted image features.

    Features are computed attribute values, NOT LLM descriptions.
    Physical axes explicitly separated from visual encoding.
    """

    image_ref: str
    feature_ref: str = Field(default_factory=lambda: f"feat_{uuid4().hex[:8]}")
    lineaments: list[dict[str, Any]] = Field(
        default_factory=list, description="Detected linear features"
    )
    discontinuities: list[dict[str, Any]] = Field(
        default_factory=list, description="Detected discontinuity locations"
    )
    dip_field: Any = Field(default=None, description="2D apparent dip field array")
    dip_field_stats: dict[str, float] = Field(default_factory=dict, description="Dip statistics")
    coherence_map: Any = Field(default=None, description="2D coherence map")
    coherence_stats: dict[str, float] = Field(default_factory=dict)
    curvature_map: Any = Field(default=None, description="2D curvature map")
    curvature_stats: dict[str, float] = Field(default_factory=dict)
    instantaneous_attributes: dict[str, Any] = Field(
        default_factory=dict, description="Envelope, phase, frequency"
    )
    physical_axes: list[str] = Field(
        default_factory=list, description="What each feature physically measures"
    )
    visual_encoding: dict[str, Any] = Field(
        default_factory=dict, description="How feature is displayed"
    )
    anomalous_risk: dict[str, Any] = Field(
        default_factory=dict, description="Contrast Canon risk assessment"
    )
    provenance: ProvenanceRecord
    uncertainty: float = Field(..., ge=0.03, le=0.20)
    telemetry: dict[str, Any] = Field(
        default_factory=lambda: {
            "stage": 3,
            "floors": ["F1", "F2", "F4", "F7", "F9"],
            "seal": "DITEMPA BUKAN DIBERI",
        }
    )

    model_config = {"arbitrary_types_allowed": True, "strict": False}


# ----------------------------------------------------------------------
# Stages 4-5: Structural Candidates + Geological Rule Engine
# ----------------------------------------------------------------------


class GEOXStructuralCandidate(BaseModel):
    """
    Stage 4-5 output — structural interpretation candidate.

    Candidates are rejected by physics-based rules before ranking.
    Every candidate carries uncertainty and alternative interpretations.
    """

    candidate_id: str = Field(default_factory=lambda: f"cand_{uuid4().hex[:8]}")
    candidate_type: StructuralCandidateType = Field(
        ..., description="fault|horizon|unconformity|fold|channel|..."
    )
    location: tuple[int, int] | None = Field(
        default=None, description="(trace_index, sample_index) if applicable"
    )
    geometry_score: float = Field(..., ge=0.0, le=1.0, description="Geometric consistency score")
    stability_score: float = Field(
        ..., ge=0.0, le=1.0, description="Seen in N views / N total views"
    )
    geology_score: float = Field(..., ge=0.0, le=1.0, description="Passes geological rule engine")
    composite_score: float = Field(..., ge=0.0, le=1.0, description="Weighted composite score")
    supporting_features: list[str] = Field(
        default_factory=list, description="Feature IDs supporting this candidate"
    )
    alternative_interpretations: list[str] = Field(
        default_factory=list,
        description="Alternative explanations for same features",
    )
    rejected: bool = Field(default=False, description="True if ruled out by physics")
    rejection_reasons: list[str] = Field(
        default_factory=list, description="Why candidate was rejected"
    )
    tectonic_setting: TectonicSetting = Field(default=TectonicSetting.UNCERTAIN)
    physical_axes: list[str] = Field(default_factory=list)
    anomalous_risk: dict[str, Any] = Field(default_factory=dict)
    provenance: ProvenanceRecord
    uncertainty: float = Field(..., ge=0.03, le=0.20)
    telemetry: dict[str, Any] = Field(default_factory=dict)

    model_config = {"strict": False}


class GEOXStructuralCandidateSet(BaseModel):
    """Stage 4-5 output — collection of structural candidates."""

    image_ref: str
    candidates: list[GEOXStructuralCandidate] = Field(default_factory=list)
    n_rejected: int = Field(default=0)
    verdict: str = Field(default="QUALIFY")
    verdict_explanation: str
    provenance: ProvenanceRecord
    aggregate_uncertainty: float = Field(..., ge=0.03, le=0.20)
    telemetry: dict[str, Any] = Field(
        default_factory=lambda: {
            "stage": "4-5",
            "floors": ["F1", "F2", "F4", "F5", "F7", "F9"],
            "seal": "DITEMPA BUKAN DIBERI",
        }
    )

    model_config = {"strict": False}


# ----------------------------------------------------------------------
# Stage 6: Ranked Structural Models
# ----------------------------------------------------------------------


class GEOXRankedStructuralModel(BaseModel):
    """Stage 6 output — ranked structural interpretation model."""

    model_id: str = Field(default_factory=lambda: f"model_{uuid4().hex[:8]}")
    tectonic_setting: TectonicSetting
    setting_confidence: float = Field(..., ge=0.0, le=1.0)
    candidate_ids: list[str] = Field(
        default_factory=list, description="IDs of candidates in this model"
    )
    geometry_score: float = Field(..., ge=0.0, le=1.0)
    stability_score: float = Field(..., ge=0.0, le=1.0)
    geology_score: float = Field(..., ge=0.0, le=1.0)
    composite_score: float = Field(..., ge=0.0, le=1.0)
    alternative_models: list[dict[str, Any]] = Field(
        default_factory=list, description="Alternative ranked models"
    )
    physical_axes: list[str] = Field(default_factory=list)
    anomalous_risk: dict[str, Any] = Field(default_factory=dict)
    provenance: ProvenanceRecord
    uncertainty: float = Field(..., ge=0.03, le=0.20)
    telemetry: dict[str, Any] = Field(default_factory=dict)

    model_config = {"strict": False}


class GEOXRankedModelSet(BaseModel):
    """Stage 6 output — ranked structural models with stability scores."""

    image_ref: str
    models: list[GEOXRankedStructuralModel] = Field(..., min_length=1)
    best_model_id: str = Field(...)
    provenance: ProvenanceRecord
    aggregate_uncertainty: float = Field(..., ge=0.03, le=0.20)
    verdict: str = Field(
        default="QUALIFY",
        description="2D line verdict ceiling is QUALIFY — never SEAL",
    )
    verdict_explanation: str
    telemetry: dict[str, Any] = Field(
        default_factory=lambda: {
            "stage": 6,
            "floors": ["F1", "F2", "F4", "F5", "F7", "F9", "F13"],
            "seal": "DITEMPA BUKAN DIBERI",
        }
    )

    model_config = {"strict": False}


# ----------------------------------------------------------------------
# Stage 7: Human Veto — Final Interpretation Result
# ----------------------------------------------------------------------


class GEOXConceptualBias(BaseModel):
    """Conceptual bias audit entry referencing Bond et al. (2007)."""

    bias_type: str
    description: str
    mitigation: str
    historical_failure_rate: float | None = Field(
        default=None,
        description="e.g., 0.79 for Bond et al. (2007) synthetic",
    )


class GEOXInterpretationResult(BaseModel):
    """
    Stage 7 output / Final output — governed structural interpretation.

    AI-proposed interpretation. NOT ground truth.
    Human review required before acceptance.
    Verdict ceiling for 2D single line is QUALIFY — never SEAL.

    Hard blocks (trigger GEOX_BLOCK):
    - 3D geometry claims from 2D
    - Volumetric HC estimates
    - Definitive fault network connectivity
    - Channel sinuosity from 2D
    """

    image_ref: str
    best_model: GEOXRankedStructuralModel
    alternative_models: list[GEOXRankedStructuralModel] = Field(default_factory=list)
    validation_recommendations: list[str] = Field(default_factory=list)
    bias_audit: list[GEOXConceptualBias] = Field(
        default_factory=list,
        description="Bond et al. (2007) conceptual bias audit",
    )
    bond_2007_reference: str = Field(
        default=(
            "Bond, C. E., Gibbs, A. D., Shipton, Z. K., & Jones, S. (2007). "
            "'What do you think this is? Conceptual uncertainty in geoscience interpretation.' "
            "GSA Today, 17(11), 4-10. https://doi.org/10.1130/GSAT01711A.1"
        )
    )
    final_verdict: Line2DVerdict = Field(
        ..., description="QUALIFY|HOLD|GEOX_BLOCK for this 2D line"
    )
    verdict_explanation: str
    aggregate_uncertainty: float = Field(..., ge=0.03, le=0.20)
    provenance: ProvenanceRecord
    telemetry: dict[str, Any] = Field(
        default_factory=lambda: {
            "stage": 7,
            "floors": ["F1", "F2", "F4", "F5", "F7", "F9", "F11", "F13"],
            "seal": "DITEMPA BUKAN DIBERI",
            "verdict_ceiling": "QUALIFY",
            "hard_blocks": [
                "3D_geometry_from_2D",
                "volumetric_HC_from_2D",
                "definitive_fault_network",
                "channel_sinuosity_2D",
            ],
        }
    )

    model_config = {"strict": False}

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        if isinstance(data.get("final_verdict"), Line2DVerdict):
            data["final_verdict"] = data["final_verdict"].value
        return data


# ----------------------------------------------------------------------
# Schema Registry
# ----------------------------------------------------------------------

MCP_SCHEMA_CLASSES = [
    GEOXSeismicImageInput,
    GEOXIngestResult,
    GEOXSeismicView,
    GEOXContrastViewSet,
    GEOXFeatureSet,
    GEOXStructuralCandidate,
    GEOXStructuralCandidateSet,
    GEOXRankedStructuralModel,
    GEOXRankedModelSet,
    GEOXInterpretationResult,
]


def export_mcp_schemas() -> dict[str, dict]:
    """Export all GEOX MCP schemas as JSON schema dicts."""
    from arifos.geox.geox_schemas import export_json_schemas

    schemas = export_json_schemas()
    for cls in MCP_SCHEMA_CLASSES:
        schemas[cls.__name__] = cls.model_json_schema()
    return schemas
