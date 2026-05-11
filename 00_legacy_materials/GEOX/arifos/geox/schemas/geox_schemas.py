"""
GEOX Schemas — The Constitution in Code
DITEMPA BUKAN DIBERI

Full Pydantic v2 data models for the GEOX geological intelligence coprocessor.
All models enforce arifOS constitutional floors where applicable.

Floor references embedded in validation:
  F1  Amanah / Reversibility
  F2  Truth ≥ 0.99 (accuracy claims)
  F4  Clarity (units, labels)
  F7  Humility — uncertainty in [0.03, 0.15]
  F9  Anti-Hantu (no phantom data)
  F11 Authority (provenance mandatory)
  F13 Sovereign (human veto on high-risk)
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

# ---------------------------------------------------------------------------
# CoordinatePoint
# ---------------------------------------------------------------------------


class CoordinatePoint(BaseModel):
    """
    Geographic coordinate with optional depth.
    Default CRS is WGS-84 (EPSG:4326).

    Example:
        CoordinatePoint(latitude=4.5, longitude=103.7, depth_m=2500.0)
    """

    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="WGS-84 latitude in decimal degrees. Range [-90, 90].",
        examples=[4.5, -3.2, 57.1],
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="WGS-84 longitude in decimal degrees. Range [-180, 180].",
        examples=[103.7, 15.3, -90.2],
    )
    depth_m: float | None = Field(
        default=None,
        description=(
            "Depth below surface in metres (positive = below surface, "
            "negative = above, e.g. elevation). None = surface."
        ),
        examples=[2500.0, 0.0, -50.0],
    )
    crs: str = Field(
        default="EPSG:4326",
        description="Coordinate reference system EPSG code string.",
        examples=["EPSG:4326", "EPSG:32648"],
    )

    @field_validator("depth_m")
    @classmethod
    def depth_finite(cls, v: float | None) -> float | None:
        if v is not None and not (-1e6 < v < 1e6):
            raise ValueError("depth_m must be in range (-1,000,000 m, 1,000,000 m).")
        return v

    model_config = {"json_schema_extra": {"title": "CoordinatePoint"}}


# ---------------------------------------------------------------------------
# ProvenanceRecord
# ---------------------------------------------------------------------------


class ProvenanceRecord(BaseModel):
    """
    Full audit trail for a single piece of data.
    Enforces F1 (traceability), F9 (anti-phantom), F11 (authority).

    Example:
        ProvenanceRecord(
            source_id="LEM-MALAY-2024-001",
            source_type="LEM",
            timestamp=datetime.utcnow(),
            confidence=0.82,
        )
    """

    source_id: str = Field(
        ...,
        min_length=1,
        description="Unique identifier of the data source or model run.",
        examples=["LEM-MALAY-2024-001", "WELL-LOG-PM3-1987"],
    )
    source_type: Literal["LEM", "VLM", "sensor", "simulator", "human", "literature"] = Field(
        ...,
        description=(
            "Category of source. LEM = Large Earth Model, VLM = Vision Language Model, "
            "sensor = physical instrument, simulator = basin/PVT model, "
            "human = expert annotation, literature = published research."
        ),
        examples=["LEM", "sensor"],
    )
    timestamp: datetime = Field(
        ...,
        description="UTC timestamp of data acquisition or model inference.",
        examples=["2024-06-15T08:30:00Z"],
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Source confidence score [0.0, 1.0].",
        examples=[0.82, 0.95],
    )
    checksum: str | None = Field(
        default=None,
        description="SHA-256 hex digest of raw data bytes for integrity verification (F1).",
        examples=["a3f2c1..."],
    )
    citation: str | None = Field(
        default=None,
        description=(
            "Human-readable citation string for literature sources. "
            "Format: Author (Year), Journal/Report, DOI/URL."
        ),
        examples=["Hutchison (1996), Geology of North-West Borneo, ISBN 978-0-444-52862-1"],
    )
    floor_check: dict[str, bool] = Field(
        default_factory=lambda: {
            "F1_amanah": True,
            "F2_truth": True,
            "F4_clarity": True,
            "F7_humility": True,
            "F9_anti_hantu": True,
            "F11_authority": True,
            "F13_sovereign": True,
        },
        description=(
            "Boolean compliance flags for each applicable arifOS Constitutional Floor. "
            "Keys follow pattern 'F<n>_<name>'. False = floor violation detected."
        ),
        examples=[{"F1_amanah": True, "F9_anti_hantu": True}],
    )

    @field_validator("source_id")
    @classmethod
    def source_id_no_whitespace(cls, v: str) -> str:
        if " " in v.strip():
            raise ValueError("source_id must not contain leading/trailing whitespace.")
        return v.strip()

    model_config = {"json_schema_extra": {"title": "ProvenanceRecord"}}


# ---------------------------------------------------------------------------
# ContrastMetadata (Contrast Canon)
# ---------------------------------------------------------------------------


class ContrastMetadata(BaseModel):
    """
    Contrast Canon metadata for seismic attributes.

    Enforces F4 (Clarity) by explicitly separating:
    - Physical axes: What geological signal the attribute measures
    - Visual encoding: How it's displayed (colormap, dynamic range)
    - Anomalous risk: Potential for display-induced misinterpretation

    Prevents the "anomalous risk" where perceptual contrast from
    visualization choices is mistaken for physical geological signal.
    """

    attribute_name: str = Field(
        ...,
        description="Attribute identifier (e.g. coherence_semblance, curvature_max)",
    )
    physical_axes: list[str] = Field(
        ...,
        description="Physical geological quantities measured (impedance, waveform_similarity, flexure)",
    )
    processing_steps: list[str] = Field(
        default_factory=list,
        description="Processing chain: dip_steered, semblance_3x3x3, etc.",
    )
    visual_encoding: dict[str, Any] = Field(
        default_factory=lambda: {
            "colormap": "gray_inverted",
            "dynamic_range": "p2-p98",
            "gamma": 1.0,
        },
        description="Display parameters affecting perceptual contrast",
    )
    anomalous_risk: dict[str, Any] = Field(
        default_factory=lambda: {
            "display_bias": "medium",
            "risk_level": "moderate",
            "notes": "",
            "mitigation": [],
        },
        description="Risk assessment for display-induced misinterpretation",
    )
    equation_reference: str | None = Field(
        default=None,
        description="Literature source (Marfurt et al. 1998, Chopra & Marfurt 2007)",
    )
    uncertainty_factors: list[str] = Field(
        default_factory=list,
        description="Explicit uncertainty sources",
    )
    is_meta_attribute: bool = Field(
        default=False,
        description="True if ML-derived (requires higher scrutiny per F9)",
    )

    model_config = {"json_schema_extra": {"title": "ContrastMetadata"}}


# ---------------------------------------------------------------------------
# GeoQuantity
# ---------------------------------------------------------------------------


class GeoQuantity(BaseModel):
    """
    A single measured or modelled geophysical quantity at a location.
    Uncertainty must satisfy F7 humility band [0.03, 0.15] unless
    explicitly overridden (set f7_override=True with justification).

    Example:
        GeoQuantity(
            value=2450.0,
            units="m/s",
            quantity_type="seismic_velocity",
            uncertainty=0.08,
            ...
        )
    """

    value: float = Field(
        ...,
        description="Numeric value of the measured or modelled quantity.",
        examples=[2450.0, 25.3, 0.18],
    )
    units: str = Field(
        ...,
        min_length=1,
        description=(
            "SI-compatible unit string for this quantity. "
            "Examples: 'm/s', 'MPa', 'degC', 'kg/m3', 'fraction', 'percent'."
        ),
        examples=["m/s", "MPa", "degC", "kg/m3", "fraction"],
    )
    coordinates: CoordinatePoint = Field(
        ...,
        description="Spatial location at which the quantity was measured or modelled.",
    )
    timestamp: datetime = Field(
        ...,
        description="UTC timestamp of measurement or model inference.",
    )
    uncertainty: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description=(
            "Fractional uncertainty [0.0, 1.0]. Per arifOS F7 (Humility), "
            "values must lie in [0.03, 0.15] unless f7_override is True."
        ),
        examples=[0.07, 0.12, 0.15],
    )
    provenance: ProvenanceRecord = Field(
        ...,
        description="Full provenance record for this quantity (F11 authority requirement).",
    )
    quantity_type: str = Field(
        ...,
        min_length=1,
        description=(
            "Semantic type label for the quantity. "
            "Examples: 'pressure', 'temperature', 'porosity', 'seismic_velocity', "
            "'density', 'net_pay', 'saturation'."
        ),
        examples=["seismic_velocity", "porosity", "temperature"],
    )
    f7_override: bool = Field(
        default=False,
        description=(
            "Set True to allow uncertainty outside [0.03, 0.15] band. "
            "Must be accompanied by override_justification."
        ),
    )
    override_justification: str | None = Field(
        default=None,
        description="Required when f7_override=True. Explains why F7 band is not applicable.",
    )

    @model_validator(mode="after")
    def validate_f7_humility(self) -> GeoQuantity:
        """F7: Humility — uncertainty must be in [0.03, 0.15] unless overridden."""
        if not self.f7_override:
            if not (0.03 <= self.uncertainty <= 0.15):
                raise ValueError(
                    f"F7 violation: uncertainty={self.uncertainty} is outside "
                    f"the constitutional humility band [0.03, 0.15]. "
                    f"Set f7_override=True with override_justification if necessary."
                )
        else:
            if not self.override_justification:
                raise ValueError(
                    "override_justification is required when f7_override=True (F7 discipline)."
                )
        return self

    model_config = {"json_schema_extra": {"title": "GeoQuantity"}}


# ---------------------------------------------------------------------------
# GeoPrediction
# ---------------------------------------------------------------------------


class GeoPrediction(BaseModel):
    """
    A testable geological prediction (e.g. net pay, HC column, pressure).
    Anchors GeoInsights to verifiable, range-bounded claims.

    Example:
        GeoPrediction(
            target="net_pay_m",
            expected_range=(15.0, 45.0),
            units="m",
            confidence=0.72,
            method="LEM_ensemble",
            ...
        )
    """

    target: str = Field(
        ...,
        min_length=1,
        description=(
            "What is being predicted. Use snake_case with units suffix where helpful. "
            "Examples: 'net_pay_m', 'hc_column_m', 'reservoir_pressure_mpa', 'porosity_fraction'."
        ),
        examples=["net_pay_m", "hc_column_m", "reservoir_pressure_mpa"],
    )
    location: CoordinatePoint = Field(
        ...,
        description="Spatial location of the prediction.",
    )
    time_window: tuple[datetime, datetime] | None = Field(
        default=None,
        description=(
            "Optional time window [start, end] for which the prediction is valid. "
            "None = present-day / timeless prediction."
        ),
    )
    expected_range: tuple[float, float] = Field(
        ...,
        description="(min, max) predicted range for the target quantity.",
        examples=[(15.0, 45.0), (0.12, 0.28)],
    )
    units: str = Field(
        ...,
        min_length=1,
        description="Unit of the expected_range values (same SI convention as GeoQuantity).",
        examples=["m", "MPa", "fraction"],
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Prediction confidence [0.0, 1.0].",
        examples=[0.72, 0.55],
    )
    supporting_quantities: list[GeoQuantity] = Field(
        default_factory=list,
        description="GeoQuantity observations that support this prediction.",
    )
    method: str = Field(
        ...,
        min_length=1,
        description=(
            "Methodological basis for the prediction. "
            "Examples: 'LEM_ensemble', 'seismic_inversion', "
            "'analogue_matching', 'basin_simulation'."
        ),
        examples=["LEM_ensemble", "seismic_inversion", "analogue_matching"],
    )

    @model_validator(mode="after")
    def validate_range_order(self) -> GeoPrediction:
        lo, hi = self.expected_range
        if lo > hi:
            raise ValueError(f"expected_range min ({lo}) must be ≤ max ({hi}).")
        return self

    model_config = {"json_schema_extra": {"title": "GeoPrediction"}}


# ---------------------------------------------------------------------------
# GeoInsight
# ---------------------------------------------------------------------------


class GeoInsight(BaseModel):
    """
    A governed geological insight — an interpreted conclusion derived
    from predictions and tool outputs.

    Insights with risk_level='high' or 'critical' always require
    human sign-off (F13 Sovereign).

    Example:
        GeoInsight(
            insight_id=str(uuid.uuid4()),
            text="The Blok Selatan anticline shows a probable HC column of 30–80 m.",
            status="supported",
            risk_level="medium",
            ...
        )
    """

    insight_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="UUID4 unique identifier for this insight.",
    )
    text: str = Field(
        ...,
        min_length=10,
        description="Human-readable insight text. Must be ≥10 chars and include units.",
        examples=["Net pay estimated at 25–45 m with moderate confidence."],
    )
    support: list[GeoPrediction] = Field(
        default_factory=list,
        description="List of GeoPredictions that this insight is grounded in.",
    )
    status: Literal["supported", "ambiguous", "contradicted", "unverified"] = Field(
        ...,
        description=(
            "Validation status: "
            "'supported' = backed by consistent tool evidence; "
            "'ambiguous' = conflicting evidence; "
            "'contradicted' = direct counter-evidence exists; "
            "'unverified' = no tool evidence yet."
        ),
        examples=["supported", "ambiguous"],
    )
    floor_verdicts: dict[str, bool] = Field(
        default_factory=lambda: {
            "F1_amanah": True,
            "F2_truth": True,
            "F4_clarity": True,
            "F7_humility": True,
            "F9_anti_hantu": True,
            "F11_authority": True,
            "F13_sovereign": True,
        },
        description="Per-floor constitutional compliance flags for this insight.",
    )
    risk_level: Literal["low", "medium", "high", "critical"] = Field(
        ...,
        description=(
            "Business / geological risk level of acting on this insight. "
            "high and critical always require human sign-off (F13)."
        ),
        examples=["medium", "high"],
    )
    requires_human_signoff: bool = Field(
        default=False,
        description=(
            "True if this insight must not trigger automated action without "
            "human approval (F13 Sovereign gate)."
        ),
    )

    @model_validator(mode="after")
    def enforce_f13_sovereign(self) -> GeoInsight:
        """F13: High/critical risk insights must always require human sign-off."""
        if self.risk_level in ("high", "critical") and not self.requires_human_signoff:
            raise ValueError(
                f"F13 violation: risk_level='{self.risk_level}' requires "
                f"requires_human_signoff=True."
            )
        return self

    model_config = {"json_schema_extra": {"title": "GeoInsight"}}


# ---------------------------------------------------------------------------
# AttributeStack (Contrast Canon Extension)
# ---------------------------------------------------------------------------


class AttributeVolume(BaseModel):
    """
    A single computed seismic attribute volume with full governance metadata.
    """

    name: str = Field(..., description="Attribute identifier")
    data_ref: str = Field(..., description="Path or reference to volume data")
    contrast: ContrastMetadata = Field(..., description="Contrast Canon metadata")
    uncertainty: float = Field(
        ...,
        ge=0.03,
        le=0.15,
        description="F7 Humility: fractional uncertainty [0.03, 0.15]",
    )
    ground_truthing: dict[str, Any] = Field(
        default_factory=dict,
        description="Well ties, horizon picks, or other validation data",
    )

    model_config = {"json_schema_extra": {"title": "AttributeVolume"}}


class AttributeStack(BaseModel):
    """
    Governed multi-attribute volume for Subsurface Forge.

    Enforces Contrast Canon on all attributes, separating physical
    signal from perceptual display artifacts.

    Constitutional Floors:
      F1: Full provenance chain for reversibility
      F4: Clarity through explicit physical_axes vs visual_encoding
      F7: Uncertainty bounds on all attributes
      F9: Anti-Hantu through anomalous_risk assessment
      F13: Human sign-off for high-risk meta-attributes
    """

    stack_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for this attribute stack",
    )
    volume_ref: str = Field(
        ...,
        description="Grounded reference to input seismic volume",
    )
    attributes: dict[str, AttributeVolume] = Field(
        ...,
        description="Named attribute volumes with full metadata",
    )
    provenance: ProvenanceRecord = Field(
        ...,
        description="Full audit trail for the stack computation",
    )
    aggregate_uncertainty: float = Field(
        ...,
        ge=0.03,
        le=0.15,
        description="Stack-wide uncertainty estimate (F7 Humility)",
    )
    verdict: Literal["SEAL", "QUALIFY", "HOLD", "GEOX_BLOCK"] = Field(
        default="QUALIFY",
        description=(
            "SEAL = all attributes grounded and validated; "
            "QUALIFY = proceed with standard QC; "
            "HOLD = elevated risk, requires review; "
            "GEOX_BLOCK = ungrounded meta-attributes, cannot proceed"
        ),
    )
    verdict_explanation: str = Field(
        default="",
        description="Human-readable explanation of verdict",
    )
    has_meta_attributes: bool = Field(
        default=False,
        description="True if any ML-derived attributes present",
    )
    well_ties: list[str] = Field(
        default_factory=list,
        description="Well names used for ground truthing",
    )
    telemetry: dict[str, Any] = Field(
        default_factory=dict,
        description="arifOS telemetry block",
    )

    @model_validator(mode="after")
    def validate_meta_attribute_grounding(self) -> AttributeStack:
        """
        F9 Anti-Hantu: Meta-attributes without well ties are suspect.
        If has_meta_attributes is True but well_ties is empty, downgrade verdict.
        """
        if self.has_meta_attributes and not self.well_ties:
            if self.verdict not in ["HOLD", "GEOX_BLOCK"]:
                self.verdict = "HOLD"
                self.verdict_explanation = (
                    "Meta-attribute(s) present without well tie validation. "
                    "Perceptual contrast risk elevated. "
                    "Provide well_ties to upgrade to QUALIFY."
                )
        return self

    model_config = {"json_schema_extra": {"title": "AttributeStack"}}


# ---------------------------------------------------------------------------
# MCP Envelope (Common Output Wrapper)
# ---------------------------------------------------------------------------


class GeoxUncertainty(BaseModel):
    """
    Standard uncertainty block for GEOX tools.
    """

    level: float = Field(..., ge=0.0, le=1.0, description="Confidence/Uncertainty level [0,1].")
    type: str = Field(..., description="Type of interpretation/analysis domain.")
    notes: list[str] = Field(default_factory=list, description="Specific uncertainty caveats.")


class GeoxGovernance(BaseModel):
    """
    Standard governance/compliance block for GEOX tools.
    """

    floors_ok: list[str] = Field(
        default_factory=list, description="Verified constitutional floors."
    )
    warnings: list[str] = Field(default_factory=list, description="Mandatory governance warnings.")


class GeoxMcpEnvelope(BaseModel):
    """
    Mandatory common output wrapper for all GEOX MCP tools.
    DITEMPA BUKAN DIBERI.
    """

    ok: bool = Field(True, description="Success flag.")
    verdict: Literal["PASS", "FAIL", "PARTIAL", "VOID", "SABAR"] = Field(
        "PASS", description="Tool-level verdict."
    )
    source_domain: str = Field("geox-earth-witness", description="Tool execution domain.")
    uncertainty: GeoxUncertainty = Field(..., description="Mandatory uncertainty reporting.")
    contrast_metadata: ContrastMetadata | None = Field(
        None, description="Contrast/display bias tracking (mandatory for image tools)."
    )
    governance: GeoxGovernance = Field(..., description="Governance and floor verification.")
    result: Any = Field(..., description="The actual tool-specific output.")

    model_config = {"json_schema_extra": {"title": "GeoxMcpEnvelope"}}


# ---------------------------------------------------------------------------
# GeoRequest
# ---------------------------------------------------------------------------


class GeoRequest(BaseModel):
    """
    Incoming prospect evaluation request.
    Captures all context needed for GEOX to plan and execute a full
    geological intelligence pipeline.

    Example:
        GeoRequest(
            query="Evaluate HC potential of Blok Selatan anticline",
            prospect_name="Blok Selatan",
            location=CoordinatePoint(latitude=4.5, longitude=103.7),
            basin="Malay Basin",
            play_type="structural",
            ...
        )
    """

    request_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="UUID4 unique identifier for this request.",
    )
    query: str = Field(
        ...,
        min_length=5,
        description="Natural-language query describing the geological evaluation task.",
        examples=["Evaluate HC potential of Blok Selatan anticline in Malay Basin."],
    )
    prospect_name: str = Field(
        ...,
        min_length=1,
        description="Name of the prospect or geological feature being evaluated.",
        examples=["Blok Selatan", "North Dome Alpha"],
    )
    location: CoordinatePoint = Field(
        ...,
        description="Representative geographic location of the prospect.",
    )
    basin: str = Field(
        ...,
        min_length=1,
        description="Sedimentary basin name.",
        examples=["Malay Basin", "Sabah Basin", "Kutai Basin"],
    )
    play_type: str = Field(
        ...,
        description=(
            "Petroleum play classification. "
            "Examples: 'stratigraphic', 'structural', 'combination', "
            "'carbonate_buildup', 'deltaic'."
        ),
        examples=["structural", "stratigraphic", "combination"],
    )
    available_data: list[str] = Field(
        default_factory=list,
        description=(
            "List of available data type identifiers. "
            "Recognised values: 'seismic_2d', 'seismic_3d', 'well_logs', "
            "'core', 'eo', 'gravity', 'magnetic', 'production'."
        ),
        examples=[["seismic_3d", "well_logs", "core"]],
    )
    risk_tolerance: Literal["low", "medium", "high"] = Field(
        ...,
        description=(
            "Requester's stated risk tolerance. Affects which insights "
            "trigger human sign-off gates."
        ),
        examples=["medium"],
    )
    requester_id: str = Field(
        ...,
        min_length=1,
        description="Unique identifier of the requesting user or system.",
        examples=["USER-geologist-001", "SYSTEM-arif-scheduler"],
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp when the request was created.",
    )

    model_config = {"json_schema_extra": {"title": "GeoRequest"}}


# ---------------------------------------------------------------------------
# GeoResponse
# ---------------------------------------------------------------------------


class GeoResponse(BaseModel):
    """
    Full GEOX pipeline response for a prospect evaluation request.
    Contains insights, predictions, verdict, provenance chain,
    audit log, and the complete arifOS telemetry block.

    Verdict vocabulary: SEAL | PARTIAL | SABAR | VOID

    Example:
        GeoResponse(
            request_id="...",
            verdict="PARTIAL",
            confidence_aggregate=0.63,
            ...
        )
    """

    response_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="UUID4 unique identifier for this response.",
    )
    request_id: str = Field(
        ...,
        description="UUID4 of the originating GeoRequest.",
    )
    insights: list[GeoInsight] = Field(
        default_factory=list,
        description="All GeoInsight objects produced by the pipeline.",
    )
    predictions: list[GeoPrediction] = Field(
        default_factory=list,
        description="All GeoPredictions referenced across all insights.",
    )
    verdict: Literal["SEAL", "PARTIAL", "SABAR", "VOID"] = Field(
        ...,
        description=(
            "Top-level GEOX verdict: "
            "SEAL = high-confidence, fully supported result; "
            "PARTIAL = partially supported, proceed with caution; "
            "SABAR = insufficient data, gather more before acting; "
            "VOID = contradictions detected, result invalid."
        ),
        examples=["PARTIAL", "SEAL"],
    )
    confidence_aggregate: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Aggregate confidence score across all insights [0.0, 1.0].",
        examples=[0.72, 0.55],
    )
    provenance_chain: list[ProvenanceRecord] = Field(
        default_factory=list,
        description="Ordered list of all ProvenanceRecord objects from this pipeline run.",
    )
    audit_log: list[dict[str, Any]] = Field(
        default_factory=list,
        description=(
            "Structured audit event log. Each entry is a dict with keys: "
            "{'event', 'stage', 'timestamp', 'detail'}."
        ),
    )
    human_signoff_required: bool = Field(
        default=False,
        description=(
            "True if any insight requires human approval before action. "
            "When True, arifos_telemetry['hold'] = '888 HOLD'."
        ),
    )
    arifos_telemetry: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "arifOS pipeline telemetry block. Contains pipeline stage, floor compliance, "
            "confidence, verdict, P2 score, hold status, uncertainty range, and seal stamp."
        ),
        examples=[
            {
                "pipeline": "000→111→333→555→777→888→999",
                "stage": "999 SEAL",
                "floors": ["F1", "F2", "F4", "F7", "F13"],
                "confidence": 0.72,
                "verdict": "PARTIAL",
                "P2": 1.0,
                "hold": "CLEAR",
                "uncertainty_range": [0.03, 0.15],
                "seal": "DITEMPA BUKAN DIBERI",
            }
        ],
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Aggregate metadata from all tool results used in the pipeline.",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the response was generated.",
    )

    model_config = {"json_schema_extra": {"title": "GeoResponse"}}


# ---------------------------------------------------------------------------
# Schema export utility
# ---------------------------------------------------------------------------


def export_json_schemas() -> dict[str, dict]:
    """
    Export all GEOX Pydantic v2 models as JSON Schema dicts.

    Returns a mapping of {model_name: json_schema_dict} for all
    top-level models. Useful for documentation, API contracts,
    and MCP tool spec generation.

    Returns:
        dict[str, dict]: {
            "CoordinatePoint": {...},
            "ProvenanceRecord": {...},
            "ContrastMetadata": {...},
            "GeoQuantity": {...},
            "GeoPrediction": {...},
            "GeoInsight": {...},
            "AttributeVolume": {...},
            "AttributeStack": {...},
            "GeoRequest": {...},
            "GeoResponse": {...},
        }
    """
    models = [
        CoordinatePoint,
        ProvenanceRecord,
        ContrastMetadata,
        GeoQuantity,
        GeoPrediction,
        GeoInsight,
        AttributeVolume,
        AttributeStack,
        GeoxMcpEnvelope,
        GeoRequest,
        GeoResponse,
    ]
    return {m.__name__: m.model_json_schema() for m in models}
