"""
arifos/geox/tools/contrast_metadata.py — Contrast Canon Schema
DITEMPA BUKAN DIBERI

Enforces F9 Anti-Hantu: perceptual contrast must never be silently
confused with physical contrast.

Models:
  ContrastSourceDomain  — Source of seismic data + acquisition geometry
  VisualTransform      — Single step in the processing chain
  PhysicalProxy        — What physical property this attribute proxies
  ConfidenceClass      — Signal vs interpretation confidence + risk
  ContrastMetadata     — Main container (Contrast Canon block)

Governance properties:
  governance_status    — unverified | confirmed | suspicious | high_risk
  is_confirmed         — True if confirmed_by is non-empty
  total_amplification  — Product of all contrast_amplification_factors
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, model_validator

# ---------------------------------------------------------------------------
# ContrastSourceDomain
# ---------------------------------------------------------------------------


class ContrastSourceDomain(BaseModel):
    """
    Source of the seismic data and acquisition geometry.

    Attributes:
        domain:              Geological domain (reflectivity, impedance, frequency, etc.)
        measurement_units:   Units of the measurement
        acquisition_type:    How this was acquired (seismic_3d, seismic_2d, computed)
        vertical_resolution_m:  Vertical resolution in metres
        lateral_resolution_m:   Lateral resolution in metres
    """

    domain: str = Field(
        ...,
        description="Geological domain: reflectivity, impedance, frequency, etc.",
    )
    measurement_units: str = Field(..., description="Units of the measurement")
    acquisition_type: str = Field(
        ...,
        description="Acquisition type: seismic_3d, seismic_2d, computed, unknown",
    )
    vertical_resolution_m: float | None = Field(
        default=None,
        description="Vertical resolution in metres",
    )
    lateral_resolution_m: float | None = Field(
        default=None,
        description="Lateral resolution in metres",
    )

    model_config = {"json_schema_extra": {"title": "ContrastSourceDomain"}}


# ---------------------------------------------------------------------------
# VisualTransform
# ---------------------------------------------------------------------------


class VisualTransform(BaseModel):
    """
    Single step in the attribute processing chain.

    Attributes:
        transform_type:             Type of transform (e.g. gaussian_filter, clahe, sobel)
        parameters:                Transform parameters
        order_index:               Position in chain (0 = first)
        reversible:                True if inverse transform exists
        contrast_amplification_factor: Multiplicative contrast change (1.0 = neutral)
        notes:                     Human-readable description
    """

    transform_type: str = Field(..., description="Type of transform applied")
    parameters: dict[str, Any] = Field(default_factory=dict)
    order_index: int = Field(..., ge=0, description="Position in processing chain")
    reversible: bool = Field(default=False)
    contrast_amplification_factor: float = Field(
        default=1.0,
        ge=0.1,
        le=100.0,
        description="Multiplicative contrast amplification (1.0 = neutral)",
    )
    notes: str = Field(default="")

    model_config = {"json_schema_extra": {"title": "VisualTransform"}}


# ---------------------------------------------------------------------------
# PhysicalProxy
# ---------------------------------------------------------------------------


class PhysicalProxy(BaseModel):
    """
    What physical property this attribute is a proxy for.

    Attributes:
        proxy_name:         Name of the physical proxy
        proxy_type:        Type: calibrated_proxy | qualitative_indicator | speculative
        physical_range:    Expected physical range (min, max)
        physical_units:    Units of the physical property
        calibration_source: Source of calibration (e.g. well log name)
    """

    proxy_name: str = Field(..., description="Name of the physical proxy")
    proxy_type: str = Field(
        default="qualitative_indicator",
        description="calibrated_proxy | qualitative_indicator | speculative",
    )
    physical_range: tuple[float, float] | None = Field(
        default=None,
        description="Expected physical range (min, max)",
    )
    physical_units: str = Field(default="", description="Units of physical property")
    calibration_source: str | None = Field(
        default=None,
        description="Source of calibration (e.g. well log name)",
    )

    model_config = {"json_schema_extra": {"title": "PhysicalProxy"}}


# ---------------------------------------------------------------------------
# ConfidenceClass
# ---------------------------------------------------------------------------


class ConfidenceClass(BaseModel):
    """
    Confidence levels and anomalous contrast risk.

    F9 Anti-Hantu enforcement: interpretation_confidence cannot exceed signal_confidence.

    Attributes:
        signal_confidence:         Confidence in raw signal quality [0.0, 1.0]
        interpretation_confidence: Confidence in geological interpretation [0.0, 1.0]
        anomalous_contrast_risk:   Risk level: low | medium | high | critical
        risk_factors:             List of specific risk factors
    """

    signal_confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in raw signal quality [0.0, 1.0]",
    )
    interpretation_confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in geological interpretation [0.0, 1.0]",
    )
    anomalous_contrast_risk: str = Field(
        default="low",
        description="Risk level: low | medium | high | critical",
    )
    risk_factors: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def interpretation_cannot_exceed_signal(self) -> ConfidenceClass:
        if self.interpretation_confidence > self.signal_confidence:
            raise ValueError(
                f"interpretation_confidence ({self.interpretation_confidence}) "
                f"cannot exceed signal_confidence ({self.signal_confidence})"
            )
        return self

    model_config = {"json_schema_extra": {"title": "ConfidenceClass"}}


# ---------------------------------------------------------------------------
# ContrastMetadata
# ---------------------------------------------------------------------------


class ContrastMetadata(BaseModel):
    """
    Mandatory Contrast Canon block — attached to every attribute/filter output.

    F9 Anti-Hantu enforcement:
      - Perceptual contrast must never be silently confused with physical contrast
      - Unknown source domains force signal_confidence ≤ 0.5
      - All outputs require non-visual confirmation before acting as geological truth

    Governance:
      - governance_status: unverified | confirmed | suspicious | high_risk
      - is_confirmed: True if confirmed_by is non-empty
      - total_contrast_amplification: Product of all amplification factors

    Attributes:
        contrast_id:         Unique ID (auto-generated)
        source_domain:      Source + acquisition geometry
        processing_chain:   Ordered list of transforms applied
        physical_proxy:     What physical property this proxies
        confidence_class:   Signal vs interpretation confidence + risk
        requires_non_visual_confirmation: Must be confirmed by LEM/well/simulator
        created_by:         Tool that created this metadata
        confirmed_by:       List of sources that confirmed this attribute
        confirmed_at:       When confirmation was added
    """

    contrast_id: str = Field(
        default_factory=lambda: f"CC-{uuid.uuid4().hex[:8].upper()}",
        description="Unique Contrast Canon ID",
    )
    source_domain: ContrastSourceDomain = Field(
        ...,
        description="Source + acquisition geometry",
    )
    processing_chain: list[VisualTransform] = Field(
        default_factory=list,
        description="Ordered list of transforms applied",
    )
    physical_proxy: PhysicalProxy = Field(
        ...,
        description="What physical property this is a proxy for",
    )
    confidence_class: ConfidenceClass = Field(
        ...,
        description="Signal vs interpretation confidence + risk",
    )
    requires_non_visual_confirmation: bool = Field(
        default=True,
        description="Must be confirmed by non-visual Earth tool before geological use",
    )
    created_by: str = Field(
        default="",
        description="Tool or function that created this metadata",
    )
    confirmed_by: list[str] = Field(
        default_factory=list,
        description="Sources that have confirmed this attribute (well names, etc.)",
    )
    confirmed_at: datetime | None = Field(
        default=None,
        description="When confirmation was added",
    )

    @model_validator(mode="after")
    def validate_processing_chain_order(self) -> ContrastMetadata:
        """Processing chain must be ordered by order_index."""
        indices = [t.order_index for t in self.processing_chain]
        if indices != sorted(indices):
            raise ValueError("processing_chain must be ordered by order_index")
        return self

    @model_validator(mode="after")
    def validate_unknown_domain_confidence(self) -> ContrastMetadata:
        """F9: unknown source domain forces signal_confidence <= 0.5."""
        if self.source_domain.domain == "unknown":
            if self.confidence_class.signal_confidence > 0.5:
                raise ValueError(
                    f"signal_confidence ({self.confidence_class.signal_confidence}) "
                    f"must be <= 0.5 for unknown source domain"
                )
        return self

    @model_validator(mode="after")
    def auto_set_confirmed_at(self) -> ContrastMetadata:
        """Auto-set confirmed_at when confirmed_by becomes non-empty."""
        if self.confirmed_by and self.confirmed_at is None:
            self.confirmed_at = datetime.now(timezone.utc)
        return self

    @property
    def total_contrast_amplification(self) -> float:
        """Product of all contrast_amplification_factors in chain."""
        if not self.processing_chain:
            return 1.0
        result = 1.0
        for t in self.processing_chain:
            result *= t.contrast_amplification_factor
        return result

    @property
    def is_confirmed(self) -> bool:
        """True if confirmed_by is non-empty."""
        return len(self.confirmed_by) > 0

    @property
    def governance_status(self) -> str:
        """
        Governance status based on confirmation and amplification.

        Returns:
            - 'confirmed': confirmed_by is non-empty
            - 'high_risk': anomalous_contrast_risk == 'critical'
            - 'suspicious': total_amplification > 10x
            - 'unverified': default state
        """
        if self.is_confirmed:
            return "confirmed"
        if self.confidence_class.anomalous_contrast_risk == "critical":
            return "high_risk"
        if self.total_contrast_amplification > 10.0:
            return "suspicious"
        return "unverified"

    model_config = {"json_schema_extra": {"title": "ContrastMetadata"}}


# ---------------------------------------------------------------------------
# Factory Helpers
# ---------------------------------------------------------------------------


def create_filter_contrast_metadata(
    filter_type: str,
    filter_params: dict[str, Any] | None = None,
) -> ContrastMetadata:
    """
    Factory: create ContrastMetadata for a seismic visual filter output.

    Args:
        filter_type:  Filter name (gaussian, sobel, canny, kuwahara, clahe, mean)
        filter_params: Filter parameters dict

    Returns:
        ContrastMetadata with appropriate risk level per filter type
    """
    fp = filter_params or {}

    risk_map = {
        "gaussian": "low",
        "mean": "low",
        "kuwahara": "low",
        "sobel": "medium",
        "canny": "medium",
        "clahe": "medium",
    }
    risk = risk_map.get(filter_type.lower(), "medium")

    signal_conf_map = {"low": 0.75, "medium": 0.65, "high": 0.55}
    signal_conf = signal_conf_map.get(risk, 0.65)
    interp_conf = signal_conf * 0.7

    amplification_map = {
        "gaussian": 1.0,
        "mean": 0.9,
        "kuwahara": 1.1,
        "sobel": 1.5,
        "canny": 1.8,
        "clahe": 2.5,
    }
    amp = amplification_map.get(filter_type.lower(), 1.0)

    return ContrastMetadata(
        source_domain=ContrastSourceDomain(
            domain="reflectivity",
            measurement_units="dimensionless",
            acquisition_type="seismic_3d",
        ),
        processing_chain=[
            VisualTransform(
                transform_type=f"{filter_type}_filter",
                parameters=fp,
                order_index=0,
                reversible=False,
                contrast_amplification_factor=amp,
                notes=f"{filter_type} applied to seismic slice.",
            ),
        ],
        physical_proxy=PhysicalProxy(
            proxy_name="visual_enhancement",
            proxy_type="qualitative_indicator",
        ),
        confidence_class=ConfidenceClass(
            signal_confidence=signal_conf,
            interpretation_confidence=interp_conf,
            anomalous_contrast_risk=risk,
            risk_factors=[f"{filter_type}_filter_amplification"],
        ),
        requires_non_visual_confirmation=True,
        created_by="SeismicVisualFilterTool",
    )


def create_meta_attribute_contrast_metadata(
    attribute_name: str,
    input_attributes: list[str],
    method: str,
    proxy_name: str,
) -> ContrastMetadata:
    """
    Factory: create ContrastMetadata for a meta-intelligence attribute output.

    F9 enforcement: meta-attributes carry 'high' anomalous_contrast_risk by default.

    Args:
        attribute_name:    Name of the meta attribute
        input_attributes:  List of input attribute names
        method:            Fusion method (cnn_segmentation, pca, random_forest, etc.)
        proxy_name:        Physical proxy name

    Returns:
        ContrastMetadata with high anomalous_contrast_risk
    """
    is_high_risk = method in ("cnn_segmentation", "unet", "deep_learning")
    is_speculative = method in ("pca", "clustering")

    risk = "high" if is_high_risk else "medium"
    signal_conf = 0.60 if is_high_risk else 0.70

    chain = [
        VisualTransform(
            transform_type=f"input_{attr}",
            parameters={},
            order_index=i,
            reversible=False,
            contrast_amplification_factor=1.0,
            notes=f"Input attribute: {attr}",
        )
        for i, attr in enumerate(input_attributes)
    ]
    chain.append(
        VisualTransform(
            transform_type=f"{method}_fusion",
            parameters={"method": method, "inputs": input_attributes},
            order_index=len(input_attributes),
            reversible=False,
            contrast_amplification_factor=2.5 if is_high_risk else 1.5,
            notes=f"Meta-attribute fusion via {method}.",
        )
    )

    risk_factors = ["multi_attribute_fusion"]
    if is_high_risk:
        risk_factors.append("learned_nonlinear_contrast_amplification")
    if is_speculative:
        risk_factors.append("unsupervised_clustering_may_miss_geology")

    return ContrastMetadata(
        source_domain=ContrastSourceDomain(
            domain="multi_attribute_fusion",
            measurement_units="probability",
            acquisition_type="computed",
        ),
        processing_chain=chain,
        physical_proxy=PhysicalProxy(
            proxy_name=proxy_name,
            proxy_type="speculative" if is_speculative else "qualitative_indicator",
        ),
        confidence_class=ConfidenceClass(
            signal_confidence=signal_conf,
            interpretation_confidence=signal_conf * 0.5,
            anomalous_contrast_risk=risk,
            risk_factors=risk_factors,
        ),
        requires_non_visual_confirmation=True,
        created_by="SeismicAttributeTool",
    )
