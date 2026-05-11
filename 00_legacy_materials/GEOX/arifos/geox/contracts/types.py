"""
GEOX Type Contracts — Pydantic models for tool inputs/outputs.
Transport-agnostic definitions used across all host adapters.
DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════════════════════════
# Base Types
# ═══════════════════════════════════════════════════════════════════════════════


class GeoXStatus(str, Enum):
    """Canonical status values for GEOX operations."""

    SEAL = "SEAL"
    SABAR = "SABAR"
    VOID = "VOID"
    PARTIAL = "PARTIAL"
    HOLD = "888_HOLD"
    UNAVAILABLE = "UNAVAILABLE"


class FloorVerdicts(BaseModel):
    """Constitutional floor check results."""

    f1_amanah: bool = True
    f2_truth: bool = True
    f3_tri_witness: bool = True
    f4_clarity: bool = True
    f5_peace: bool = True
    f6_empathy: bool = True
    f7_humility: bool = True
    f8_genius: bool = True
    f9_anti_hantu: bool = True
    f10_ontology: bool = True
    f11_authority: bool = True
    f12_injection: bool = True
    f13_sovereign: bool = True


class ProvenanceTag(str, Enum):
    """Data provenance classification."""

    MEASURED = "MEASURED"
    DERIVED = "DERIVED"
    POLICY = "POLICY"
    INTERPRETED = "INTERPRETED"


class GeoXResult(BaseModel):
    """Base result structure for all GEOX operations."""

    status: GeoXStatus
    timestamp: datetime
    seal: str = "DITEMPA BUKAN DIBERI"
    geox_version: str = "0.5.0"
    floor_verdicts: FloorVerdicts = Field(default_factory=FloorVerdicts)
    provenance_tag: ProvenanceTag = ProvenanceTag.DERIVED

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# ═══════════════════════════════════════════════════════════════════════════════
# Petrophysics Types
# ═══════════════════════════════════════════════════════════════════════════════


class SwModel(str, Enum):
    """Water saturation calculation models."""

    ARCHIE = "archie"
    SIMANDOUX = "simandoux"
    INDONESIA = "indonesia"


class SwStats(BaseModel):
    """Monte Carlo statistics for Sw calculation."""

    p10: float
    p50: float
    p90: float
    mean: float
    std: float
    min: float
    max: float


class SwCalculationResult(GeoXResult):
    """Result from water saturation calculation."""

    model: SwModel
    nominal_sw: float
    stats: SwStats | None = None
    hold_triggers: list[str] = Field(default_factory=list)
    requires_hold: bool = False


class SwModelAdmissibilityResult(GeoXResult):
    """Result from Sw model selection/admissibility check."""

    well_id: str
    recommended_model: str
    admissible_models: list[str]
    inadmissible_models: dict[str, list[str]]
    requires_hold: bool
    hold_reasons: list[str]
    confidence: float


class PetrophysicsResult(GeoXResult):
    """Full petrophysics calculation result."""

    well_id: str
    sw_model_used: SwModel
    sw_nominal: float
    sw_p10: float | None = None
    sw_p50: float | None = None
    sw_p90: float | None = None
    sw_std: float | None = None
    phi_effective: float
    vcl: float
    bvw: float
    uncertainty: float
    hold_triggers: list[str] = Field(default_factory=list)
    requires_hold: bool = False
    audit_id: str


class CutoffValidationResult(GeoXResult):
    """Cutoff policy validation result."""

    well_id: str
    policy_id: str
    policy_basis: str
    is_net_reservoir: bool
    is_net_pay: bool
    passed_rt_cutoff: bool | None = None
    phi_pass: bool
    sw_pass: bool
    vcl_pass: bool
    phi_tested: float
    sw_tested: float
    vcl_tested: float
    rt_tested: float | None = None
    cutoffs: dict[str, float | None]
    violations: list[str] = Field(default_factory=list)
    requires_hold: bool = False
    audit_id: str


class PetrophysicsHoldResult(GeoXResult):
    """888_HOLD result for constitutional violations."""

    well_id: str
    hold_id: str
    triggered_by: str
    violated_floors: list[str]
    violations: list[str]
    remediation: list[str]
    severity: Literal["block", "warn", "info"]
    requires_human_signoff: bool = True


# ═══════════════════════════════════════════════════════════════════════════════
# Seismic Types
# ═══════════════════════════════════════════════════════════════════════════════


class SeismicView(BaseModel):
    """Individual seismic view metadata."""

    view_id: str
    mode: str
    source: str
    note: str


class SeismicLineResult(GeoXResult):
    """Result from seismic line loading."""

    line_id: str
    survey_path: str
    views: list[SeismicView]
    ignition_status: str = "IGNITED"


class StructuralCandidate(BaseModel):
    """Structural model candidate."""

    candidate_id: str
    confidence: float
    model_type: str
    parameters: dict[str, Any]


class StructuralCandidatesResult(GeoXResult):
    """Result from structural candidate generation."""

    line_id: str
    candidates: list[StructuralCandidate]
    count: int
    verdict: str = "QUALIFY"
    confidence: float = 0.12


# ═══════════════════════════════════════════════════════════════════════════════
# Evaluation Types
# ═══════════════════════════════════════════════════════════════════════════════


class ProspectEvaluationResult(GeoXResult):
    """Result from prospect evaluation."""

    prospect_id: str
    interpretation_id: str
    verdict: str
    confidence: float
    reason: str


class FeasibilityResult(GeoXResult):
    """Result from feasibility check."""

    plan_id: str
    constraints: list[str]
    verdict: str
    grounding_confidence: float


class GeospatialVerificationResult(GeoXResult):
    """Result from geospatial verification."""

    lat: float
    lon: float
    radius_m: float
    geological_province: str
    jurisdiction: str
    verdict: str
    crs: str = "WGS84"


# ═══════════════════════════════════════════════════════════════════════════════
# Memory Types
# ═══════════════════════════════════════════════════════════════════════════════


class MemoryEntry(BaseModel):
    """Single memory entry."""

    entry_id: str
    query_match_score: float
    content: dict[str, Any]
    basin: str | None = None


class MemoryQueryResult(GeoXResult):
    """Result from memory query."""

    query: str
    basin_filter: str | None = None
    results: list[MemoryEntry]
    count: int
    memory_backend: str


# ═══════════════════════════════════════════════════════════════════════════════
# Health Types
# ═══════════════════════════════════════════════════════════════════════════════


class HealthResult(GeoXResult):
    """Server health check result."""

    ok: bool = True
    service: str = "geox-earth-witness"
    fastmcp_version: str = ""
    prefab_ui: bool = False
    seismic_engine: bool = False
    constitutional_floors: list[str] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════════
# App Intent Types (for MCP Apps)
# ═══════════════════════════════════════════════════════════════════════════════


class AppIntent(BaseModel):
    """Intent to launch a GEOX App."""

    app_id: str
    action: Literal["open", "update", "close", "focus"]
    params: dict[str, Any] = Field(default_factory=dict)
    preferred_mode: Literal["inline", "external"] = "inline"
    session_token: str | None = None
