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


# ── Replay Receipt ─────────────────────────────────────────────


class ReplayStep(BaseModel):
    """Single step in an exploration trace for replay verification."""

    step_index: int
    mode: ExploreMode
    action: str = Field(description="What the step did: sense|step|update|check|reflect")
    input_nodes: int = Field(default=0, ge=0)
    output_nodes: int = Field(default=0, ge=0)
    findings_delta: int = Field(default=0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    duration_s: float = Field(default=0.0, ge=0.0)
    timestamp: str = Field(default="", description="ISO8601 utcnow at step start")


class ReplayReceipt(BaseModel):
    """
    Traceable, HMAC-ready receipt for ExploreResponse.

    Provides replay verification: given the same seed + goal + mode,
    can we reproduce the same result_hash? If receipt_hash matches
    on replay, the exploration is deterministic-verifiable.

    Fields:
        trace_id:       Unique identifier for this exploration session.
        steps:          Ordered list of ReplayStep records.
        result_hash:    SHA-256 of (goal + mode + sorted(findings) + graph_hash).
        receipt_hash:  SHA-256 of (trace_id + result_hash + step_hashes).
        verified:       Whether receipt_hash was independently recomputed.
        explorer_tag:   Identity of the explorer (actor_id or agent class).
        epistemic_tag:  OBS/DER/INT/SPEC — base evidence grade for the exploration.
    """

    trace_id: str
    steps: list[ReplayStep] = Field(default_factory=list)
    result_hash: str = Field(default="", description="SHA-256 of exploration result")
    receipt_hash: str = Field(default="", description="SHA-256 of full trace")
    verified: bool = Field(default=False)
    explorer_tag: str = Field(
        default="arif_explore", description="Identity that ran the exploration"
    )
    epistemic_tag: str = Field(
        default="DER",
        description="Evidence grade: OBS (direct) | DER (computed) | INT (interpreted) | SPEC (speculative)",
    )

    def compute_result_hash(
        self,
        goal: str,
        mode: str,
        finding_summaries: list[str],
        node_hashes: list[str],
    ) -> str:
        """Compute SHA-256 result_hash from exploration outputs."""
        import hashlib

        payload = (
            f"{goal}|{mode}|"
            + "|".join(sorted(finding_summaries))
            + "|"
            + "|".join(sorted(node_hashes))
        )
        return hashlib.sha256(payload.encode()).hexdigest()

    def compute_receipt_hash(self) -> str:
        """Compute SHA-256 receipt_hash from trace + result_hash."""
        import hashlib

        step_hashes = "|".join(
            hashlib.sha256(f"{s.step_index}{s.mode.value}{s.action}".encode()).hexdigest()
            for s in self.steps
        )
        payload = f"{self.trace_id}|{self.result_hash}|{step_hashes}"
        return hashlib.sha256(payload.encode()).hexdigest()


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
    replay_receipt: ReplayReceipt | None = Field(
        default=None,
        description="Traceable replay receipt with result_hash + receipt_hash for verification",
    )


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
    "ReplayReceipt",
    "ReplayStep",
]
