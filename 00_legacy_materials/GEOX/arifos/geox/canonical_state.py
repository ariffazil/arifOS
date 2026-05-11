"""
GEOX Canonical State Schemas — DITEMPA BUKAN DIBERI

GEOX owns the visual semantics, not the LLM.
LLM handles intent and orchestration; GEOX produces deterministic state.

Tri-App Architecture: Map + Cross Section + Seismic Section

Canonical state objects:
- GeoXIntent: Normalized user intent
- GeoXAssetContext: Target asset and spatial context
- GeoXDisplayState: Viewer state (viewport, layers, axes, legend)
- GeoXAnalysisState: Observations, interpretations, uncertainty
- GeoXAuditState: Hold status, scope flags, traceability
- GeoXUiState: UI mode, warnings, badges
- GeoXCrossSectionState: Geologic cross section (INTERPRETED)
- GeoXSeismicSectionState: Seismic section (OBSERVATIONAL)

Tool IO contract pattern:
- Input: typed intent or state delta
- Output: success, state_delta, structuredContent, text_summary, warnings, hold_status
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class IntentType(str, Enum):
    OPEN_MAP_CONTEXT = "open_map_context"
    OPEN_CROSS_SECTION = "open_cross_section"
    OPEN_SEISMIC_SECTION = "open_seismic_section"
    TOGGLE_OVERLAY = "toggle_overlay"
    ANALYZE_ROI = "analyze_roi"
    COMPARE_CROSS_AND_SEISMIC = "compare_cross_and_seismic"
    EXPORT_SNAPSHOT = "export_snapshot"
    SUMMARIZE_INTERPRETATION = "summarize_interpretation"
    QUERY_MEMORY = "query_memory"
    EVALUATE_PROSPECT = "evaluate_prospect"


class AppMode(str, Enum):
    MAP = "map"
    CROSS_SECTION = "cross_section"
    SEISMIC_SECTION = "seismic_section"
    COMPARE = "compare"


class LayerType(str, Enum):
    SEISMIC = "seismic"
    FAULT = "fault"
    HORIZON = "horizon"
    WELL_LOG = "well_log"
    FORMATION = "formation"
    TOPOGRAPHY = "topography"
    ATTRIBUTE = "attribute"
    INTERPRETATION = "interpretation"
    UNCERTAINTY = "uncertainty"
    WELL_TOPS = "well_tops"
    UNIT_POLYGON = "unit_polygon"


class Verdict(str, Enum):
    SEAL = "SEAL"
    PARTIAL = "PARTIAL"
    SABAR = "SABAR"
    VOID = "VOID"


class HoldStatus(str, Enum):
    CLEAR = "CLEAR"
    HOLD_888 = "888_HOLD"
    HOLD_F13_SOVEREIGN = "F13_SOVEREIGN"


class CrossSectionState(str, Enum):
    IDLE = "idle"
    LOADING_PROFILE = "loading_profile"
    PROFILE_DEFINED = "profile_defined"
    MODEL_BUILDING = "model_building"
    READY_CLEAN = "ready_clean"
    READY_WARN = "ready_warn"
    WELL_SELECTED = "well_selected"
    FAULT_SELECTED = "fault_selected"
    UNCERTAINTY_VISIBLE = "uncertainty_visible"
    COMPARE_WITH_SEISMIC = "compare_with_seismic"
    EXPORT_READY = "export_ready"
    HOLD = "hold"


class GeoXIntent(BaseModel):
    """Normalized user intent object. LLM produces only this; never final geology."""

    intent_id: str = Field(default_factory=lambda: str(uuid4()))
    intent_type: IntentType = Field(..., description="Intent class")
    natural_language_query: str = Field(..., description="Original user query")
    target_ref: str | None = Field(None, description="Asset or feature reference")
    action: str | None = Field(None, description="Requested action")
    requested_layers: list[LayerType] = Field(default_factory=list)
    requested_measurements: list[str] = Field(default_factory=list)
    constraints: dict[str, Any] = Field(default_factory=dict)
    requester_id: str = Field(..., description="Requesting user or system ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"json_schema_extra": {"title": "GeoXIntent"}}


class CoordinateBounds(BaseModel):
    """Spatial bounding box."""

    min_lat: float = Field(..., ge=-90, le=90)
    max_lat: float = Field(..., ge=-90, le=90)
    min_lon: float = Field(..., ge=-180, le=180)
    max_lon: float = Field(..., ge=-180, le=180)


class GeoXAssetContext(BaseModel):
    """Asset and spatial context for a geological feature."""

    asset_id: str | None = Field(None, description="Unique asset identifier")
    asset_type: str = Field(..., description="seismic_2d, seismic_3d, well_log, map")
    basin: str = Field(..., description="Sedimentary basin name")
    line_name: str | None = Field(None, description="Seismic line identifier")
    inline: int | None = Field(None, description="Inline number for 3D seismic")
    crossline: int | None = Field(None, description="Crossline number for 3D seismic")
    depth_range_m: tuple[float, float] | None = Field(None)
    time_range_ms: tuple[float, float] | None = Field(None)
    spatial_bounds: CoordinateBounds | None = Field(None)
    vertical_unit: str = Field(default="meters")
    horizontal_scale: float | None = Field(None)
    vertical_scale: float | None = Field(None)

    model_config = {"json_schema_extra": {"title": "GeoXAssetContext"}}


class Viewport(BaseModel):
    """2D viewport for seismic section."""

    x_min: float = 0.0
    x_max: float = 1.0
    y_min: float = 0.0
    y_max: float = 1.0


class AxisDefinition(BaseModel):
    """Axis definition for display."""

    label: str = Field(..., description="Axis label")
    unit: str = Field(..., description="Physical unit")
    scale: str = Field(default="linear")
    min_value: float | None = None
    max_value: float | None = None


class LegendEntry(BaseModel):
    """Legend entry for overlay."""

    label: str
    color: str = Field(..., pattern="^#[0-9A-Fa-f]{6}$")
    opacity: float = Field(default=1.0, ge=0.0, le=1.0)


class LayerState(BaseModel):
    """State of a single display layer."""

    layer_type: LayerType
    visible: bool = True
    opacity: float = Field(default=1.0, ge=0.0, le=1.0)
    color_map: str | None = None
    thresholds: dict[str, float] = Field(default_factory=dict)


class GeoXDisplayState(BaseModel):
    """Canonical visualization state. GEOX produces this deterministically; UI renders it."""

    display_id: str = Field(default_factory=lambda: str(uuid4()))
    asset_context: GeoXAssetContext | None = None
    viewport: Viewport = Field(default_factory=Viewport)
    x_axis: AxisDefinition | None = None
    y_axis: AxisDefinition | None = None
    layers: list[LayerState] = Field(default_factory=list)
    legends: list[LegendEntry] = Field(default_factory=list)
    badges: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    ui_mode: str = Field(default="section")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"json_schema_extra": {"title": "GeoXDisplayState"}}


class Observation(BaseModel):
    """A single geological observation."""

    observation_id: str = Field(default_factory=lambda: str(uuid4()))
    feature_type: str = Field(..., description="fault, horizon, facies, anomaly...")
    location: str = Field(..., description="Inline/crossline or lat/lon reference")
    description: str = Field(..., description="What was observed")
    confidence: float = Field(..., ge=0.0, le=1.0)
    uncertainty: float = Field(..., ge=0.0, le=1.0)
    evidence_sources: list[str] = Field(default_factory=list)


class Interpretation(BaseModel):
    """Geological interpretation."""

    interpretation_id: str = Field(default_factory=lambda: str(uuid4()))
    observation_ids: list[str] = Field(default_factory=list)
    claim: str = Field(..., description="Geological claim")
    confidence: float = Field(..., ge=0.0, le=1.0)
    alternatives: list[str] = Field(default_factory=list)
    provenance: str = Field(..., description="Source of interpretation")


class GeoXAnalysisState(BaseModel):
    """Canonical analysis state with observations, interpretations, counter-hypotheses."""

    analysis_id: str = Field(default_factory=lambda: str(uuid4()))
    display_state: GeoXDisplayState | None = None
    observations: list[Observation] = Field(default_factory=list)
    interpretations: list[Interpretation] = Field(default_factory=list)
    counter_hypotheses: list[str] = Field(default_factory=list)
    uncertainty_band: tuple[float, float] = Field(default=(0.03, 0.15))
    roi_results: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"json_schema_extra": {"title": "GeoXAnalysisState"}}


class FloorStatus(BaseModel):
    """Status of a single constitutional floor."""

    floor_id: str = Field(..., description="F1, F2, F4, F7, F9, F11, F13")
    passed: bool = Field(...)
    details: str | None = Field(None)
    confidence: float | None = Field(None, ge=0.0, le=1.0)


class GeoXAuditState(BaseModel):
    """Canonical audit state with hold status, scope flags, traceability."""

    audit_id: str = Field(default_factory=lambda: str(uuid4()))
    analysis_state: GeoXAnalysisState | None = None
    hold_status: HoldStatus = Field(default=HoldStatus.CLEAR)
    scope_flags: list[str] = Field(default_factory=list)
    floor_compliance: list[FloorStatus] = Field(default_factory=list)
    metadata_completeness: float = Field(default=1.0, ge=0.0, le=1.0)
    traceability: list[str] = Field(default_factory=list)
    human_signoff_required: bool = False
    human_signoff_by: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"json_schema_extra": {"title": "GeoXAuditState"}}


class GeoXUiState(BaseModel):
    """Combined UI state for rendering. This is what UI layers consume."""

    ui_state_id: str = Field(default_factory=lambda: str(uuid4()))
    intent: GeoXIntent | None = None
    display_state: GeoXDisplayState | None = None
    analysis_state: GeoXAnalysisState | None = None
    audit_state: GeoXAuditState | None = None
    text_summary: str = Field(default="")
    artifact_links: dict[str, str] = Field(default_factory=dict)
    success: bool = True
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"json_schema_extra": {"title": "GeoXUiState"}}


class ProfilePoint(BaseModel):
    """A point along a cross-section profile."""

    distance_km: float = Field(..., description="Distance along profile in km")
    elevation_m: float = Field(..., description="Elevation in meters (positive up)")
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)


class WellColumn(BaseModel):
    """Well/borehole data on cross section."""

    well_id: str
    well_name: str
    profile_distance_km: float = Field(..., description="Distance along profile")
    ground_elevation_m: float
    total_depth_m: float
    formation_tops: list[dict[str, Any]] = Field(default_factory=list)
    is_observed: bool = Field(True, description="True if real data, False if inferred")


class FaultTrace(BaseModel):
    """Fault trace on cross section."""

    fault_id: str
    fault_name: str | None = None
    trace_points: list[ProfilePoint] = Field(..., description="Fault trace points")
    dip_degrees: float | None = Field(None, description="Apparent dip if known")
    throw_m: float | None = Field(None, description="Measured throw if known")
    is_observed: bool = Field(
        True, description="True if from seismic, False if inferred"
    )


class UnitPolygon(BaseModel):
    """Geological unit polygon on cross section."""

    unit_id: str
    unit_name: str
    formation_age: str | None = Field(None, description="e.g., 'Miocene', 'Cretaceous'")
    lithology: str | None = Field(None, description="e.g., 'sandstone', 'shale'")
    polygon_coords: list[ProfilePoint] = Field(..., description="Unit boundary points")
    color: str = Field(default="#808080", pattern="^#[0-9A-Fa-f]{6}$")
    is_observed: bool = Field(
        True, description="True if well-control, False if interpolated"
    )


class UncertaintyZone(BaseModel):
    """Region of uncertain interpretation on cross section."""

    zone_id: str
    start_distance_km: float
    end_distance_km: float
    top_depth_m: float | None = None
    bottom_depth_m: float | None = None
    uncertainty_type: str = Field(
        ...,
        description="lateral_continuity, thickness, correlation, pinchout, fault_geometry",
    )
    confidence: float = Field(..., ge=0.0, le=1.0)
    explanation: str = Field(..., description="Why this zone is uncertain")


class GeoXCrossSectionState(BaseModel):
    """
    Canonical geologic cross-section state.

    Geologic cross sections are INTERPRETED earth model products.
    Seismic sections are OBSERVATIONAL images.
    Never confuse them — different confidence semantics.
    """

    profile_id: str = Field(default_factory=lambda: str(uuid4()))
    profile_name: str = Field(..., description="Profile line name")
    profile_points: list[ProfilePoint] = Field(default_factory=list)
    total_length_km: float = Field(..., description="Total profile length")
    wells: list[WellColumn] = Field(default_factory=list)
    faults: list[FaultTrace] = Field(default_factory=list)
    units: list[UnitPolygon] = Field(default_factory=list)
    uncertainty_zones: list[UncertaintyZone] = Field(default_factory=list)
    topography_profile: list[ProfilePoint] = Field(default_factory=list)
    cross_section_state: CrossSectionState = Field(default=CrossSectionState.IDLE)
    vertical_exaggeration: float = Field(default=1.0)
    datum_elevation_m: float = Field(default=0.0)
    show_uncertainty: bool = False
    show_wells: bool = True
    show_faults: bool = True
    structural_style: str | None = Field(
        None, description="e.g., 'thrust', 'normal', 'strike-slip'"
    )
    stratigraphic_continuity: str | None = Field(
        None, description="continuous, discontinuous, pinchout"
    )
    data_density: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Fraction with direct well control"
    )
    interpretation_notes: list[str] = Field(default_factory=list)
    linked_seismic_section_id: str | None = Field(None)
    sync_cursor_distance_km: float | None = Field(None)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"json_schema_extra": {"title": "GeoXCrossSectionState"}}


class GeoXSeismicSectionState(BaseModel):
    """
    Canonical seismic section state.

    Seismic sections are OBSERVATIONAL sensor products.
    Different from geologic cross sections which are INTERPRETED.
    """

    section_id: str = Field(default_factory=lambda: str(uuid4()))
    section_name: str = Field(..., description="Seismic line name")
    asset_context: GeoXAssetContext | None = None
    detected_reflectors: list[dict[str, Any]] = Field(default_factory=list)
    detected_faults: list[dict[str, Any]] = Field(default_factory=list)
    segmented_facies: list[dict[str, Any]] = Field(default_factory=list)
    image_quality: str = Field(default="unknown", description="good, fair, poor")
    polarity: str = Field(
        default="unknown", description="SEG_normal, SEG_reverse, unknown"
    )
    stretch_artifacts: bool = False
    linked_cross_section_id: str | None = Field(None)
    well_tie_points: list[dict[str, Any]] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"json_schema_extra": {"title": "GeoXSeismicSectionState"}}


class GeoXTriAppState(BaseModel):
    """Container for all three GEOX app states. Map + Cross Section + Seismic Section."""

    active_app: AppMode = Field(default=AppMode.MAP)
    map_state: GeoXDisplayState | None = None
    cross_section_state: GeoXCrossSectionState | None = None
    seismic_section_state: GeoXSeismicSectionState | None = None
    selected_profile_line: str | None = Field(None)
    spatial_bounds: CoordinateBounds | None = Field(None)
    compare_mode_active: bool = False
    compare_cursor_distance_km: float | None = Field(None)

    model_config = {"json_schema_extra": {"title": "GeoXTriAppState"}}


class CrossSectionHoldTriggers(BaseModel):
    """888 HOLD triggers specific to cross-section interpretation."""

    borehole_spacing_too_wide: bool = Field(
        default=False,
        description="Boreholes > 10km apart — continuity claims unreliable",
    )
    unit_correlation_confidence_low: bool = Field(
        default=False, description="Unit correlation confidence < 0.6"
    )
    vertical_exaggeration_undisclosed: bool = Field(
        default=False, description="VE > 2x but not shown to user"
    )
    fault_geometry_inferred: bool = Field(
        default=False, description="Fault geometry not seismic-constrained"
    )
    uncertain_pinchout_present: bool = Field(
        default=False, description="Pinchout or truncation in interpreted zone"
    )
    no_well_control_in_interval: bool = Field(
        default=False, description="Interval of interest has zero well control"
    )

    def any_hold_active(self) -> bool:
        return any(
            [
                self.borehole_spacing_too_wide,
                self.unit_correlation_confidence_low,
                self.vertical_exaggeration_undisclosed,
                self.fault_geometry_inferred,
                self.uncertain_pinchout_present,
                self.no_well_control_in_interval,
            ]
        )


class ToolOutputEnvelope(BaseModel):
    """Standard tool output envelope. Every GEOX tool follows this contract."""

    success: bool = True
    state_delta: dict[str, Any] = Field(default_factory=dict)
    structuredContent: dict[str, Any] = Field(default_factory=dict)
    text_summary: str = Field(default="")
    warnings: list[str] = Field(default_factory=list)
    hold_status: HoldStatus = Field(default=HoldStatus.CLEAR)
    tool_name: str = Field(...)
    execution_time_ms: float | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"json_schema_extra": {"title": "ToolOutputEnvelope"}}


def export_canonical_schemas() -> dict[str, Any]:
    """Export all canonical state schemas as JSON Schema dicts."""

    models: list[type[BaseModel]] = [
        GeoXIntent,
        GeoXAssetContext,
        GeoXDisplayState,
        GeoXAnalysisState,
        GeoXAuditState,
        GeoXUiState,
        GeoXCrossSectionState,
        GeoXSeismicSectionState,
        GeoXTriAppState,
        CrossSectionHoldTriggers,
        ToolOutputEnvelope,
    ]
    return {m.__name__: m.model_json_schema() for m in models}
