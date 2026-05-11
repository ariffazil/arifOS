"""
geox/shared/schemas/foundation.py — Sovereign Witness Schema for subsurface intelligence.
═══════════════════════════════════════════════════════════════════════════════
DITEMPA BUKAN DIBERI

This module defines the canonical Pydantic 2.x models for the GEOX 'Causal Scene'.
It enforces the separation between identity, witness geometry, and policy-governed verdicts.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated, Literal, Optional, Union, Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# ══════════════════════════════════════════════════════════════════════════════
# Domain & Enumerations
# ══════════════════════════════════════════════════════════════════════════════


class DomainKind(str, Enum):
    """Naming convention for spatio-temporal domains."""

    twt_ms = "twt_ms"
    tvdss_m = "tvdss_m"
    md_m = "md_m"
    tvd_m = "tvd_m"
    depth_ft = "depth_ft"
    time_s = "time_s"
    inline_crossline = "inline_crossline"
    xy_m = "xy_m"


class WitnessKind(str, Enum):
    """The four essential witnesses of a Causal Scene."""

    manifold = "manifold"
    truth = "truth"
    claim = "claim"
    texture = "texture"


class OperatorKind(str, Enum):
    """The type of comparison being performed."""

    residual_z = "residual_z"
    synthetic_correlation = "synthetic_correlation"
    geometric_intersection = "geometric_intersection"
    volumetric_integration = "volumetric_integration"
    thermodynamic_audit = "thermodynamic_audit"


class ClaimKind(str, Enum):
    """Types of interpreted subsurface claims."""

    horizon3d = "horizon3d"
    fault3d = "fault3d"
    fault_stick_set = "fault_stick_set"
    marker_projection = "marker_projection"
    interpreted_polygon = "interpreted_polygon"


class TextureKind(str, Enum):
    """Types of volumetric evidence / imagery."""

    seismic_amplitude = "seismic_amplitude"
    seismic_similarity = "seismic_similarity"
    seismic_coherence = "seismic_coherence"
    seismic_dip = "seismic_dip"
    synthetic_seismogram = "synthetic_seismogram"
    seismic_stats = "seismic_stats"


class Comparator(str, Enum):
    """Operation for policy band evaluation."""

    lt = "lt"
    le = "le"
    gt = "gt"
    ge = "ge"
    abs_gt = "abs_gt"
    abs_ge = "abs_ge"
    between = "between"


class VerdictCode(str, Enum):
    """Judgment outcomes governed by the 888_JUDGE."""

    pass_green = "pass_green"
    review_amber = "review_amber"
    hold_888 = "hold_888"
    reject_red = "reject_red"
    unknown = "unknown"


class SupportKind(str, Enum):
    """Internal topology of a witness's sampling support."""

    grid = "grid"
    stick = "stick"
    track = "track"
    pointset = "pointset"
    volume = "volume"


# ══════════════════════════════════════════════════════════════════════════════
# Foundational Micro-Models
# ══════════════════════════════════════════════════════════════════════════════


class UnitRef(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str  # e.g. "millisecond"
    symbol: str  # e.g. "ms"
    quantity: str  # e.g. "time", "length", "density"


class DomainRef(BaseModel):
    model_config = ConfigDict(extra="forbid")
    z_kind: DomainKind
    z_unit: UnitRef
    xy_kind: DomainKind = DomainKind.xy_m
    xy_unit: UnitRef
    is_time_domain: bool
    crs_name: Optional[str] = None
    crs_epsg: Optional[int] = None

    @model_validator(mode="after")
    def check_time_flag(self) -> "DomainRef":
        if (
            self.z_kind in {DomainKind.twt_ms, DomainKind.time_s}
            and not self.is_time_domain
        ):
            raise ValueError("z_kind is time-based but is_time_domain is False")
        if (
            self.z_kind not in {DomainKind.twt_ms, DomainKind.time_s}
            and self.is_time_domain
        ):
            raise ValueError("z_kind is depth-based but is_time_domain is True")
        return self


class StorageRef(BaseModel):
    model_config = ConfigDict(extra="forbid")
    platform: str = Field(default="opendtect")
    ioobj_key: Optional[str] = None
    object_name: Optional[str] = None
    object_type: Optional[str] = None
    source_path: Optional[str] = None
    source_ref: Optional[str] = None
    survey_name: Optional[str] = None
    survey_uuid: Optional[str] = None


class ProvenanceStamp(BaseModel):
    model_config = ConfigDict(extra="forbid")
    author: Optional[str] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    machine_generated: bool = False
    workflow_name: Optional[str] = None
    workflow_version: Optional[str] = None
    notes: Optional[str] = None


class SamplingAxis(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    start: float
    stop: float
    step: float
    count: Optional[int] = None
    unit: UnitRef

    @field_validator("step")
    @classmethod
    def step_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("sampling step must be > 0")
        return v

    @model_validator(mode="after")
    def stop_must_exceed_start(self) -> "SamplingAxis":
        if self.stop < self.start:
            raise ValueError("sampling stop must be >= start")
        return self


class XYPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")
    x: float
    y: float


class XYZPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")
    x: float
    y: float
    z: float


class NumericRange(BaseModel):
    model_config = ConfigDict(extra="forbid")
    min_value: float
    max_value: float
    unit: UnitRef

    @model_validator(mode="after")
    def check_order(self) -> "NumericRange":
        if self.max_value < self.min_value:
            raise ValueError("max_value must be >= min_value")
        return self


# ══════════════════════════════════════════════════════════════════════════════
# Support Geometry (Topology Identification)
# ══════════════════════════════════════════════════════════════════════════════


class BaseSupportGeometry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    support_kind: SupportKind
    domain: DomainRef
    label: Optional[str] = None


class GridSupportGeometry(BaseSupportGeometry):
    """Support for surfaces sampled on inline/crossline lattices."""

    support_kind: Literal[SupportKind.grid] = SupportKind.grid
    inline_axis: SamplingAxis
    crossline_axis: SamplingAxis
    z_axis: Optional[SamplingAxis] = None
    bbox_xy: Optional[list[XYPoint]] = None
    is_regular_grid: bool = True


class StickSupportGeometry(BaseSupportGeometry):
    """Support for fault sticks and discontinuous interpreted segments."""

    support_kind: Literal[SupportKind.stick] = SupportKind.stick
    stick_count: int
    point_count: Optional[int] = None
    stick_id_field: str = "stick_id"
    ordering: Literal["top_down", "bottom_up", "unordered"] = "unordered"


class TrackSupportGeometry(BaseSupportGeometry):
    """Support for directional witnesses (Wells/Log tracks)."""

    support_kind: Literal[SupportKind.track] = SupportKind.track
    measured_depth_range: NumericRange
    sample_step: Optional[float] = None
    sample_step_unit: Optional[UnitRef] = None
    trajectory_defined: bool = True


class PointSetSupportGeometry(BaseSupportGeometry):
    """Support for sparse x-y-z samples."""

    support_kind: Literal[SupportKind.pointset] = SupportKind.pointset
    point_count: int
    has_unique_ids: bool = False


class VolumeSupportGeometry(BaseModel):
    """3D Voxel Lattice."""

    support_kind: Literal[SupportKind.volume] = SupportKind.volume
    inl_range: NumericRange
    crl_range: NumericRange
    z_range: NumericRange
    step_inl: int = 1
    step_crl: int = 1
    step_z: float
    lateral_stepout_traces: int = 0
    vertical_window_samples: int = 0
    effective_resolution_m: Optional[float] = None


SupportGeometry = Annotated[
    Union[
        GridSupportGeometry,
        StickSupportGeometry,
        TrackSupportGeometry,
        PointSetSupportGeometry,
        VolumeSupportGeometry,
    ],
    Field(discriminator="support_kind"),
]


# ══════════════════════════════════════════════════════════════════════════════
# Policy Bands (The Laws & Thresholds)
# ══════════════════════════════════════════════════════════════════════════════


class PolicyBand(BaseModel):
    """A versioned, auditable threshold policy."""

    model_config = ConfigDict(extra="forbid")
    policy_name: str
    metric_name: str
    comparator: Comparator
    green_max: Optional[float] = None
    amber_max: Optional[float] = None
    red_min: Optional[float] = None
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    unit: UnitRef
    default_verdict_if_missing: VerdictCode = VerdictCode.unknown
    rationale: Optional[str] = None

    @model_validator(mode="after")
    def validate_band_shape(self) -> "PolicyBand":
        if self.comparator in {
            Comparator.abs_gt,
            Comparator.abs_ge,
            Comparator.gt,
            Comparator.ge,
            Comparator.lt,
            Comparator.le,
        }:
            if (
                self.green_max is None
                and self.red_min is None
                and self.amber_max is None
            ):
                raise ValueError("threshold policy requires at least one threshold")
        if self.comparator == Comparator.between:
            if self.lower_bound is None or self.upper_bound is None:
                raise ValueError(
                    "between comparator requires lower_bound and upper_bound"
                )
            if self.upper_bound < self.lower_bound:
                raise ValueError("upper_bound must be >= lower_bound")
        return self


class PolicyEvaluation(BaseModel):
    """Conclusion of an audit against a specific PolicyBand."""

    model_config = ConfigDict(extra="forbid")
    metric_name: str
    observed_value: Optional[float] = None
    unit: UnitRef
    band: PolicyBand
    verdict: VerdictCode = VerdictCode.unknown
    explanation: Optional[str] = None

    @model_validator(mode="after")
    def metric_names_align(self) -> "PolicyEvaluation":
        if self.metric_name != self.band.metric_name:
            raise ValueError("metric_name must match the policy band's metric_name")
        return self


# ══════════════════════════════════════════════════════════════════════════════
# Witness Definitions
# ══════════════════════════════════════════════════════════════════════════════


class WitnessBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    witness_id: str
    witness_kind: WitnessKind
    name: str
    domain: DomainRef
    support_geometry: SupportGeometry
    storage_ref: Optional[StorageRef] = None
    provenance: Optional[ProvenanceStamp] = None
    tags: list[str] = Field(default_factory=list)
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    active: bool = True


class SurveyBounds(BaseModel):
    model_config = ConfigDict(extra="forbid")
    inline_range: Optional[tuple[int, int]] = None
    crossline_range: Optional[tuple[int, int]] = None
    xy_bbox: Optional[list[XYPoint]] = None
    z_range: NumericRange
    nominal_inline_step: Optional[float] = None
    nominal_crossline_step: Optional[float] = None


class ThermoVolume(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pressure_range_mpa: Optional[tuple[float, float]] = None
    temperature_range_c: Optional[tuple[float, float]] = None
    notes: Optional[str] = None


class ManifoldWitness(WitnessBase):
    """The Law: The spatial and thermodynamic bounds of the world."""

    witness_kind: Literal[WitnessKind.manifold] = WitnessKind.manifold
    survey_bounds: SurveyBounds
    z_sampling: SamplingAxis
    crs_locked: bool = True
    z_transform_name: Optional[str] = None
    thermo_volume: Optional[ThermoVolume] = None
    reject_out_of_bounds: bool = True


class MarkerObservation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    marker_name: str
    md_value: Optional[float] = None
    tvdss_value: Optional[float] = None
    twt_value_ms: Optional[float] = None
    uncertainty: Optional[float] = None
    uncertainty_unit: Optional[UnitRef] = None

    @model_validator(mode="after")
    def at_least_one_position(self) -> "MarkerObservation":
        if (
            self.md_value is None
            and self.tvdss_value is None
            and self.twt_value_ms is None
        ):
            raise ValueError("marker must carry at least one positional value")
        return self


class LogCurveRef(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mnemonic: str
    quantity: str
    unit: UnitRef
    sample_count: Optional[int] = None
    null_value: Optional[float] = None
    support_range: Optional[NumericRange] = None


class D2TCalibration(BaseModel):
    model_config = ConfigDict(extra="forbid")
    exists: bool
    source: Optional[str] = None
    control_point_count: Optional[int] = None
    residual_rms_ms: Optional[float] = None
    quality_flag: Optional[str] = None


class TruthWitness(WitnessBase):
    """The Ground Truth: Absolute anchors (Well Markers, Logs)."""

    witness_kind: Literal[WitnessKind.truth] = WitnessKind.truth
    well_id: Optional[str] = None
    well_name: Optional[str] = None
    markers: list[MarkerObservation] = Field(default_factory=list)
    logs: list[LogCurveRef] = Field(default_factory=list)
    d2t_calibration: Optional[D2TCalibration] = None
    hard_witness: bool = True

    @model_validator(mode="after")
    def requires_truth_payload(self) -> "TruthWitness":
        if not self.markers and not self.logs:
            raise ValueError(
                "truth witness must contain at least one marker or one log"
            )
        return self


class AttributeOverlayRef(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    unit: Optional[UnitRef] = None
    description: Optional[str] = None


class ClaimWitness(WitnessBase):
    """Interpreted subsurface surfaces or bodies."""

    witness_kind: Literal[WitnessKind.claim] = WitnessKind.claim
    claim_kind: ClaimKind
    support: SupportGeometry
    confidence: float = 1.0
    connected_body_count: int = 1
    largest_body_fraction: float = 1.0
    mask_id: Optional[str] = None
    uncertainty: float = 0.0
    interpreted_by_human: bool = True
    source_algorithm: Optional[str] = None
    version_label: Optional[str] = None
    z_range: Optional[NumericRange] = None
    overlays: list[AttributeOverlayRef] = Field(default_factory=list)
    parent_claim_id: Optional[str] = None


class TextureStats(BaseModel):
    model_config = ConfigDict(extra="forbid")
    min_amplitude: Optional[float] = None
    max_amplitude: Optional[float] = None
    mean_amplitude: Optional[float] = None
    std_amplitude: Optional[float] = None


class TextureWitness(WitnessBase):
    """Observation data (Seismic, Attributes, Velocities)."""

    witness_kind: Literal[WitnessKind.texture] = WitnessKind.texture
    texture_kind: str  # amplitude, similarity, coherence, dip, etc.
    support: Union[GridSupportGeometry, VolumeSupportGeometry, TrackSupportGeometry]
    stats: Optional[TextureStats] = None
    parent_attribute_ids: list[str] = Field(default_factory=list)
    operator_name: Optional[str] = None
    operator_params: dict[str, Any] = Field(default_factory=dict)
    active_set_id: Optional[str] = None
    uncertainty: float = 0.0
    u_source: Optional[str] = None
    wavelet_name: Optional[str] = None
    phase_reference: Optional[str] = None
    polarity_convention: Optional[str] = None


# ══════════════════════════════════════════════════════════════════════════════
# Governance & Judgment
# ══════════════════════════════════════════════════════════════════════════════


class FloorPolicy(BaseModel):
    """Structural constraint based on GEOX Constitutional Floors."""

    model_config = ConfigDict(extra="forbid")
    floor_name: str
    enabled: bool = True
    hold_on_fail: bool = True
    note: Optional[str] = None


class IntentEnvelope(BaseModel):
    """Audit record of a requested geological operation."""

    model_config = ConfigDict(extra="forbid")
    intent_id: str
    operation_name: str
    operator_name: Optional[str] = None
    project_name: Optional[str] = None
    reversible: bool = True
    requires_human_confirmation: bool = False
    target_witness_ids: list[str] = Field(default_factory=list)
    floor_policies: list[FloorPolicy] = Field(default_factory=list)
    policy_bands: list[PolicyBand] = Field(default_factory=list)
    io_parameters: dict[str, str | int | float | bool | None] = Field(
        default_factory=dict
    )
    audit_message: Optional[str] = None

    @model_validator(mode="after")
    def irreversible_requires_confirmation(self) -> "IntentEnvelope":
        if not self.reversible and not self.requires_human_confirmation:
            raise ValueError("irreversible actions must require human confirmation")
        return self


class ContrastMetric(BaseModel):
    """Result of a deterministic contrast operation."""

    model_config = ConfigDict(extra="forbid")
    metric_id: str
    metric_name: str
    value: float
    unit: str | UnitRef
    confidence: float = 1.0
    expected_value: Optional[float] = None
    residual_value: Optional[float] = None
    method_tag: Optional[str] = None  # e.g. quad_tessellation_area
    description: Optional[str] = None


class ContrastLink(BaseModel):
    """The relationship between the witnesses in a Verdict."""

    model_config = ConfigDict(extra="forbid")
    left_witness_id: str
    right_witness_id: str
    operation: str


class ContrastOperatorSpec(BaseModel):
    """Rigid definition of an allowable physical comparison."""

    model_config = ConfigDict(extra="forbid")
    op_kind: OperatorKind
    left_kind: WitnessKind
    left_support: SupportKind
    right_kind: WitnessKind
    right_support: SupportKind
    required_domain_match: bool = True
    interpolation_method: Optional[str] = None
    rationale: str

    @model_validator(mode="after")
    def validate_op_logic(self) -> "ContrastOperatorSpec":
        # Example invariant: residual_z always requires a Track (Well) vs Grid/Stick (Horizon/Fault)
        if self.op_kind == OperatorKind.residual_z:
            if self.left_support != SupportKind.track:
                raise ValueError("residual_z requires 1D track as left witness")
        return self


# ══════════════════════════════════════════════════════════════════════════════
# UI Distillation (The exact React payload)
# ══════════════════════════════════════════════════════════════════════════════


class Physics9Item(BaseModel):
    sym: str
    name: str
    val: str
    unit: str


class CausalSceneUISummary(BaseModel):
    """Refined structure for direct UI rendering and LLM prompt assembly."""

    status: Literal["unverified", "verified", "HOLD", "SIMULATED", "sealed"]
    epoch: str
    manifold: dict  # area, grossH, phi, etc.
    physics9: list[Physics9Item] = Field(..., validation_alias="canon9")
    claims: dict[str, bool]  # d2t_tie, fault_intersection, etc.
    truth: dict[str, Any]  # f2_passed, f7_uncertainty, etc.
    holds: list[str] = Field(default_factory=list)
    floor_flags: dict[str, bool] = Field(default_factory=dict)
    simulation_flags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ContrastVerdict(BaseModel):
    """The Final Judgment: A governed conclusion about physical truth."""

    model_config = ConfigDict(extra="forbid")
    verdict_id: str
    intent_id: str
    status: Literal["PASS", "DRIL", "HOLD", "FAIL"]
    verdict_code: Optional[VerdictCode] = VerdictCode.unknown
    metrics: list[ContrastMetric]
    links: list[ContrastLink]
    floors_evaluated: list[str]
    human_override: bool = False
    override_reason: Optional[str] = None
    override_authority_level: Optional[int] = None  # 0-11
    override_timestamp: Optional[datetime] = None
    commentary: str
    policy_evaluations: list[PolicyEvaluation] = Field(default_factory=list)
    triggered_floors: list[str] = Field(default_factory=list)
    requires_hold: bool = False
    human_confirmation_required: bool = False
    witness_snapshot_ids: list[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.now)

    @model_validator(mode="after")
    def synchronize_hold_flags(self) -> "ContrastVerdict":
        if self.status in {"HOLD", "FAIL"}:
            self.requires_hold = True
        return self
