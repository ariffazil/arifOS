"""
arifOS L2 Exploration Substrate — Canonical Schemas (v2026.06.21)
=================================================================

Pydantic models for the arif_explore tool — one kernel, six modes.
Sense-extend (111): governed, read-only, constitutional.

States:  INIT → PLAN → STEP → UPDATE → CHECK → REFLECT → SEAL
Modes:  navigator | prospector | driller | mapper | surveyor | scout | auto

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ── Mode Enum ─────────────────────────────────────────────────


class ExploreMode(str, Enum):
    """Six exploration strategies + eureka + auto."""

    NAVIGATOR = "navigator"
    PROSPECTOR = "prospector"
    DRILLER = "driller"
    MAPPER = "mapper"
    SURVEYOR = "surveyor"
    SCOUT = "scout"
    EUREKA = "eureka"
    AUTO = "auto"


# ── Seed Sub-models ───────────────────────────────────────────


class SeedURL(BaseModel):
    url: str
    allowed_domains: list[str] = Field(default_factory=list)
    blocked_domains: list[str] = Field(default_factory=list)


class SeedPath(BaseModel):
    path: str
    include_patterns: list[str] = Field(default_factory=lambda: ["*"])
    exclude_patterns: list[str] = Field(default_factory=list)


class SeedAPI(BaseModel):
    base_url: str
    auth: dict = Field(default_factory=dict)
    openapi_url: Optional[str] = None


class Seed(BaseModel):
    url: Optional[SeedURL] = None
    path: Optional[SeedPath] = None
    api: Optional[SeedAPI] = None
    entity: Optional[str] = None
    question: Optional[str] = None


# ── Limits ────────────────────────────────────────────────────


class Limits(BaseModel):
    max_depth: int = Field(default=4, ge=1, le=10)
    max_steps: int = Field(default=64, ge=1, le=256)
    time_budget_s: int = Field(default=60, ge=5, le=600)


# ── Telemetry ─────────────────────────────────────────────────


class TelemetryContext(BaseModel):
    trace_id: str
    organ_context: list[str] = Field(default_factory=list)


# ── Request ───────────────────────────────────────────────────


class ExploreRequest(BaseModel):
    goal: str
    mode: ExploreMode = ExploreMode.AUTO
    seed: Seed = Field(default_factory=Seed)
    limits: Limits = Field(default_factory=Limits)
    telemetry: TelemetryContext


# ── Graph ─────────────────────────────────────────────────────


class GraphNode(BaseModel):
    node_id: str
    mode: ExploreMode
    label: str
    content_hash: str
    evidence: str = ""
    meta: dict = Field(default_factory=dict)


class GraphEdge(BaseModel):
    from_id: str
    to_id: str
    relation: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class ExplorationGraph(BaseModel):
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)


# ── Findings ──────────────────────────────────────────────────


class Finding(BaseModel):
    id: str
    summary: str
    confidence: float = Field(ge=0.0, le=1.0)
    sources: list[str] = Field(default_factory=list)


# ── Verdict ───────────────────────────────────────────────────


class Saturation(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class NextMove(BaseModel):
    mode: ExploreMode
    goal: str
    reason: str


class Verdict(BaseModel):
    saturation: Saturation
    next_moves: list[NextMove] = Field(default_factory=list)


# ── Metrics ───────────────────────────────────────────────────


class ExploreMetrics(BaseModel):
    steps: int = 0
    depth: int = 0
    coverage: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


# ── Response ──────────────────────────────────────────────────


class ExploreStatus(str, Enum):
    OK = "ok"
    PARTIAL = "partial"
    FAILED = "failed"


class ExploreResponse(BaseModel):
    status: ExploreStatus
    exploration_graph: ExplorationGraph = Field(default_factory=ExplorationGraph)
    findings: list[Finding] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    metrics: ExploreMetrics = Field(default_factory=ExploreMetrics)
    verdict: Verdict = Field(default_factory=Verdict)


__all__ = [
    "ExploreMode",
    "SeedURL",
    "SeedPath",
    "SeedAPI",
    "Seed",
    "Limits",
    "TelemetryContext",
    "ExploreRequest",
    "GraphNode",
    "GraphEdge",
    "ExplorationGraph",
    "Finding",
    "Saturation",
    "NextMove",
    "Verdict",
    "ExploreMetrics",
    "ExploreStatus",
    "ExploreResponse",
]
