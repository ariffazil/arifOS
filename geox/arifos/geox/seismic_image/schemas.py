"""
Pydantic schemas for seismic image processing.

All schemas enforce:
- F4 Clarity: Units and scales mandatory
- F7 Humility: Uncertainty quantified
- F2 Truth: Proxy nature labeled
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


# =============================================================================
# Enums
# =============================================================================

class ImageType(str, Enum):
    RAW_SEISMIC = "raw_seismic"
    ATTRIBUTE_DISPLAY = "attribute_display"
    INTERPRETATION_OVERLAY = "interpretation_overlay"
    UNKNOWN = "unknown"


class VerticalUnit(str, Enum):
    METERS = "meters"
    FEET = "feet"
    SECONDS_TWT = "seconds_TWT"
    MILLISECONDS_TWT = "milliseconds_TWT"
    SAMPLES = "samples"


class PolarityStandard(str, Enum):
    SEG_NORMAL = "SEG_normal"
    SEG_REVERSE = "SEG_reverse"
    UNKNOWN = "unknown"


class TextureMethod(str, Enum):
    LBP = "lbp"
    GLCM = "glcm"
    GABOR = "gabor"
    STRUCTURE_TENSOR = "structure_tensor"
    STEERABLE_PYRAMID = "steerable_pyramid"
    CURVELET = "curvelet"


class Verdict(str, Enum):
    SEAL = "SEAL"
    PARTIAL = "PARTIAL"
    SABAR = "SABAR"
    VOID = "VOID"


# =============================================================================
# Ingest Schemas
# =============================================================================

class SeismicImageIngestRequest(BaseModel):
    """Request to ingest a seismic section image."""
    
    image_path: str = Field(..., description="Path to image file (PNG, JPG, TIFF)")
    image_type: ImageType = Field(..., description="Type of image content")
    basin: str = Field(..., description="Sedimentary basin name")
    line_name: str = Field(..., description="Seismic line or survey identifier")
    vertical_unit: VerticalUnit = Field(..., description="Vertical axis unit — F4 MANDATORY")
    vertical_scale: float = Field(..., gt=0, description="Vertical scale: units per pixel")
    horizontal_scale: float = Field(..., gt=0, description="Horizontal scale: distance per pixel")
    polarity_known: bool = Field(default=False, description="Whether SEG standard polarity is known")
    polarity_standard: PolarityStandard = Field(default=PolarityStandard.UNKNOWN)
    requester_id: str = Field(..., description="Unique requester identifier — F11 AUTH")
    
    @field_validator("vertical_scale", "horizontal_scale")
    @classmethod
    def validate_scales(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Scale must be positive")
        return v


class ScaleValidation(BaseModel):
    """Validation of declared scales."""
    
    vertical_scale_declared: float
    horizontal_scale_declared: float
    aspect_ratio_valid: bool
    aspect_ratio_distortion_pct: float = Field(..., ge=0)
    estimated_true_vertical_extent_m: float | None = None
    estimated_true_horizontal_extent_m: float | None = None


class IngestMetadata(BaseModel):
    """Metadata extracted during ingest."""
    
    width_px: int
    height_px: int
    format: str
    color_mode: str
    file_size_mb: float
    bits_per_pixel: int | None = None


class ConstitutionalCompliance(BaseModel):
    """Constitutional floor compliance report."""
    
    F4_clarity: str = Field(..., description="F4 Clarity compliance")
    F11_authority: str = Field(..., description="F11 Authority compliance")
    F2_truth: str = Field(default="PENDING", description="F2 Truth compliance")
    F7_humility: str = Field(default="PENDING", description="F7 Humility compliance")


class SeismicImageIngestResponse(BaseModel):
    """Response from seismic image ingest."""
    
    success: bool
    image_id: str = Field(..., description="Unique image identifier")
    verdict: Verdict
    ingest_metadata: IngestMetadata
    scale_validation: ScaleValidation
    constitutional_compliance: ConstitutionalCompliance
    next_steps: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    seal: str = Field(default="DITEMPA BUKAN DIBERI")


# =============================================================================
# QC Schemas
# =============================================================================

class QCCheck(BaseModel):
    """Individual QC check result."""
    
    status: Literal["PASS", "WARNING", "FAIL"]
    confidence: float = Field(..., ge=0, le=1)
    details: dict[str, Any] = Field(default_factory=dict)
    recommendation: str | None = None


class QCResult(BaseModel):
    """Full QC result."""
    
    success: bool
    image_id: str
    verdict: Verdict
    qc_score: float = Field(..., ge=0, le=1)
    checks: dict[str, QCCheck]
    recommendations: list[str]
    warnings: list[str]
    seal: str = Field(default="DITEMPA BUKAN DIBERI")


# =============================================================================
# Texture Attribute Schemas
# =============================================================================

class TextureAttributeRequest(BaseModel):
    """Request for texture attribute extraction."""
    
    image_id: str
    methods: list[TextureMethod] = Field(default_factory=lambda: [TextureMethod.STRUCTURE_TENSOR])
    window_size_px: int = Field(default=32, ge=8, le=256)
    overlap_pct: float = Field(default=50, ge=0, le=90)
    
    @field_validator("methods")
    @classmethod
    def validate_methods(cls, v: list[TextureMethod]) -> list[TextureMethod]:
        if not v:
            raise ValueError("At least one method required")
        return v


class StructureTensorOutput(BaseModel):
    """Structure tensor analysis output."""
    
    coherence: list[list[float]] = Field(..., description="Local coherence (0-1)")
    orientation_deg: list[list[float]] = Field(..., description="Local orientation in degrees")
    energy: list[list[float]] = Field(..., description="Gradient energy")
    eigenvalue_ratio: list[list[float]] | None = Field(None, description="λ₁/λ₂ ratio")
    
    # Physics interpretation
    geological_proxy: str = Field(
        default="Reflector continuity and dip direction",
        description="What this measures in geological terms"
    )
    uncertainty_note: str = Field(
        default="Image-domain proxy — not true dip from trace analysis"
    )


class LBPOutput(BaseModel):
    """Local Binary Pattern output."""
    
    histograms: list[list[int]]
    uniformity_score: float = Field(..., ge=0, le=1)
    geological_proxy: str = Field(default="Amplitude roughness, bedform style")
    uncertainty_note: str = Field(default="Texture proxy — not grain size measurement")


class GLCMOutput(BaseModel):
    """Gray Level Co-occurrence Matrix output."""
    
    contrast: list[list[float]]
    correlation: list[list[float]]
    energy: list[list[float]]
    homogeneity: list[list[float]]
    dissimilarity: list[list[float]] | None = None
    geological_proxy: str = Field(default="Facies heterogeneity, layering uniformity")
    uncertainty_note: str = Field(default="Statistical texture measure — not lithology")


class TextureAttributeOutput(BaseModel):
    """Container for all texture attribute outputs."""
    
    structure_tensor: StructureTensorOutput | None = None
    lbp: LBPOutput | None = None
    glcm: GLCMOutput | None = None
    gabor: dict[str, Any] | None = None


class TextureAttributeResponse(BaseModel):
    """Response from texture attribute extraction."""
    
    success: bool
    image_id: str
    verdict: Verdict
    attributes: TextureAttributeOutput
    metadata: dict[str, Any] = Field(
        default_factory=lambda: {
            "proxy_nature": "IMAGE_DOMAIN_PROXY",
            "not_equivalent_to": ["instantaneous_attributes", "trace_derived_attributes"],
            "physical_basis": "Local intensity variation patterns correlated with reflector geometry"
        }
    )
    uncertainty: dict[str, float] = Field(
        default_factory=lambda: {
            "pixel_scale_confidence": 0.92,
            "texture_reliability": 0.88,
            "geological_interpretation_ceiling": 0.75
        }
    )
    seal: str = Field(default="DITEMPA BUKAN DIBERI")


# =============================================================================
# Reflector Detection Schemas
# =============================================================================

class Reflector(BaseModel):
    """Detected reflector candidate."""
    
    reflector_id: str
    pixels: list[list[int]] = Field(..., description="[[x1, y1], [x2, y2], ...]")
    length_px: int
    length_m: float | None = None  # Computed from scale
    average_dip_deg: float | None = None
    dip_variance: float | None = None
    coherence: float = Field(..., ge=0, le=1)
    continuity_score: float = Field(..., ge=0, le=1)
    termination_type: Literal["gradual", "abrupt", "faulted", "unknown"] = "unknown"


class ReflectorDetectionResponse(BaseModel):
    """Response from reflector detection."""
    
    success: bool
    image_id: str
    verdict: Verdict
    reflectors: list[Reflector]
    statistics: dict[str, Any]
    uncertainty: dict[str, Any] = Field(
        default_factory=lambda: {
            "detection_confidence": 0.82,
            "dip_accuracy_estimate": "±3 degrees (image domain)",
            "physical_validation": "REQUIRES_TRACE_DOMAIN_CONFIRMATION",
            "verdict_reason": "Reflectors are candidates, not true horizons"
        }
    )
    seal: str = Field(default="DITEMPA BUKAN DIBERI")


# =============================================================================
# Fault Detection Schemas
# =============================================================================

class FaultCandidate(BaseModel):
    """Detected fault candidate."""
    
    fault_id: str
    pixels: list[list[int]]
    length_px: int
    dip_direction: str | None = None
    likelihood_score: float = Field(..., ge=0, le=1)
    offset_estimate_px: int | None = None
    confidence: float = Field(..., ge=0, le=1)


class FaultDetectionResponse(BaseModel):
    """Response from fault candidate detection."""
    
    success: bool
    image_id: str
    verdict: Verdict
    fault_likelihood_map: str | None = Field(None, description="base64 PNG")
    candidates: list[FaultCandidate]
    uncertainty: dict[str, str] = Field(
        default_factory=lambda: {
            "false_positive_risk": "HIGH — many discontinuities are not faults",
            "validation_required": "Cross-line confirmation and trace-domain analysis"
        }
    )
    seal: str = Field(default="DITEMPA BUKAN DIBERI")


# =============================================================================
# Facies Segmentation Schemas
# =============================================================================

class FaciesSegmentationResponse(BaseModel):
    """Response from facies segmentation."""
    
    success: bool
    image_id: str
    verdict: Verdict
    segmentation_map: str | None = Field(None, description="base64 PNG")
    class_probabilities: dict[str, list[list[float]]]
    uncertainty_map: list[list[float]]
    statistics: dict[str, Any]
    model_info: dict[str, Any] = Field(
        default_factory=lambda: {
            "architecture": "DeepLabv3+",
            "confidence_ceiling": 0.95,
            "F7_compliance": "Uncertainty quantified and exposed"
        }
    )
    warnings: list[str] = Field(
        default_factory=lambda: [
            "Segmentation is image-domain prediction, not lithology identification",
            "Classes are seismic facies proxies, not rock types",
            "High uncertainty regions require interpreter attention"
        ]
    )
    seal: str = Field(default="DITEMPA BUKAN DIBERI")


# =============================================================================
# Audit Schema
# =============================================================================

class FloorAudit(BaseModel):
    """Audit result for a single constitutional floor."""
    
    floor: str
    status: Literal["PASS", "WARNING", "VIOLATION"]
    details: str
    action: Literal["NONE", "FLAG", "HOLD", "VOID"]


class AuditResponse(BaseModel):
    """Response from 888 AUDIT."""
    
    success: bool
    result_id: str
    verdict: Verdict
    floor_audits: list[FloorAudit]
    overall_confidence: float
    human_signoff_required: bool
    seal: str = Field(default="DITEMPA BUKAN DIBERI")
