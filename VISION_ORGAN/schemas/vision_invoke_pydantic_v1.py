"""
vision.invoke — Pydantic Interfaces (v1.0.0)
Provider-neutral MCP tool for visual perception.

These interfaces validate both inbound requests and outbound responses
against the JSON Schema Draft 2020-12 contracts.

DO NOT import external vision providers here. Routing is the router's concern.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, Any, Literal, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

# ─── Enums ───────────────────────────────────────────────────────────────


class Task(str, Enum):
    """Canonical task taxonomy — drives model selection and prompt routing."""
    CAPTION = "caption"
    DESCRIBE = "describe"
    DETECT = "detect"
    OCR = "ocr"
    EXTRACT_STRUCTURED = "extract_structured"
    COMPARE = "compare"
    VERIFY = "verify"
    CLASSIFY = "classify"
    SEGMENT = "segment"
    MEASURE = "measure"
    TRANSCRIBE_VISUAL = "transcribe_visual"
    QA = "qa"
    CUSTOM = "custom"


class OutputMode(str, Enum):
    TEXT = "text"
    STRUCTURED = "structured"
    BOTH = "both"


class RiskTier(str, Enum):
    TRIVIAL = "trivial"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ClassificationLevel(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"
    SOVEREIGN = "sovereign"


class VerdictTag(str, Enum):
    """Epistemic classification of the primary answer."""
    CLAIM = "CLAIM"
    PLAUSIBLE = "PLAUSIBLE"
    HYPOTHESIS = "HYPOTHESIS"
    ESTIMATE = "ESTIMATE"
    UNKNOWN = "UNKNOWN"


class ResponseStatus(str, Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    REJECTED = "rejected"
    FAILED = "failed"
    POLICY_HOLD = "policy_hold"
    HUMAN_REVIEW_REQUIRED = "human_review_required"


class ObservationLabel(str, Enum):
    OBS = "OBS"
    DER = "DER"
    META = "META"


class FormatHint(str, Enum):
    TABLE = "table"
    LIST = "list"
    KEY_VALUE = "key_value"
    GRAPH = "graph"
    GEOJSON = "geojson"


class PolicyAction(str, Enum):
    BLOCKED = "blocked"
    REDACTED = "redacted"
    LOGGED = "logged"
    WARNED = "warned"


# ─── Error Code (authoritative list) ─────────────────────────────────────


class ErrorCode(str, Enum):
    INVALID_ARTIFACT = "invalid_artifact"
    UNSUPPORTED_MEDIA = "unsupported_media"
    ACCESS_DENIED = "access_denied"
    CLASSIFICATION_BLOCKED = "classification_blocked"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    CAPABILITY_MISMATCH = "capability_mismatch"
    BUDGET_EXCEEDED = "budget_exceeded"
    LOW_CONFIDENCE = "low_confidence"
    POLICY_HOLD = "policy_hold"
    INTERNAL_ERROR = "internal_error"


# ─── Input Models ────────────────────────────────────────────────────────


class ArtifactById(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(..., min_length=1, max_length=256,
                    description="Federated artifact ID (e.g. fed://artifact/sha256:abc123)")
    expected_mime: Optional[str] = Field(None, description="Expected MIME type for preflight check")


class ArtifactByUri(BaseModel):
    model_config = ConfigDict(extra="forbid")
    uri: str = Field(..., description="Resolvable URI: file://, https://, data:URL, ipfs://, ui://")
    expected_mime: Optional[str] = Field(None, description="Expected MIME type for preflight check")


class InlineData(BaseModel):
    model_config = ConfigDict(extra="forbid")
    media_type: str = Field(..., description="MIME type of the inline data")
    data: str = Field(..., description="Base64-encoded bytes")


class ArtifactByInline(BaseModel):
    model_config = ConfigDict(extra="forbid")
    inline_data: InlineData


class ArtifactOneOf(BaseModel):
    """Wrapper to enforce oneOf semantics via model_validator."""
    id_based: Optional[ArtifactById] = None
    uri_based: Optional[ArtifactByUri] = None
    inline_based: Optional[ArtifactByInline] = None

    @model_validator(mode="after")
    def exactly_one(self) -> "ArtifactOneOf":
        sources = [self.id_based, self.uri_based, self.inline_based]
        provided = sum(1 for s in sources if s is not None)
        if provided != 1:
            raise ValueError("Exactly one of id, uri, or inline_data must be provided")
        return self

    @property
    def artifact_ref(self) -> ArtifactById | ArtifactByUri | ArtifactByInline:
        return self.id_based or self.uri_based or self.inline_based  # type: ignore[return-value]


class Region(BaseModel):
    model_config = ConfigDict(extra="forbid")
    x: float
    y: float
    width: float = Field(..., gt=0)
    height: float = Field(..., gt=0)


class Selector(BaseModel):
    model_config = ConfigDict(extra="forbid")
    page: Optional[int] = Field(None, ge=1, description="1-based page number")
    frame: Optional[int] = Field(None, ge=0, description="Frame index for video/animated GIF")
    region: Optional[Region] = None
    timestamp_s: Optional[float] = Field(None, ge=0, description="Video frame at this timestamp (seconds)")


class PolicyConstraints(BaseModel):
    model_config = ConfigDict(extra="forbid")
    classification_level: ClassificationLevel = ClassificationLevel.PUBLIC
    egress_prohibited: bool = False
    redact_exif: bool = True
    prompt_injection_guard: bool = True
    max_cost_usd: Optional[float] = Field(None, ge=0)
    human_review_required: bool = False


class StructuredOutputProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Optional[dict[str, Any]] = Field(None, alias="schema",
                                               description="JSON Schema Draft 2020-12 for structured output")
    required_fields: Optional[list[str]] = Field(None, min_length=1)
    format_hint: Optional[FormatHint] = None


class TraceContext(BaseModel):
    model_config = ConfigDict(extra="forbid")
    correlation_id: Optional[str] = None
    span_id: Optional[str] = None
    session_id: Optional[str] = None
    requester_agent: Optional[str] = None


class VisionInvokeRequest(BaseModel):
    """
    vision.invoke — Provider-Neutral MCP Tool Input (v1.0.0)

    The single entrypoint for all visual-perception requests.
    Callers never name a model, adapter, or endpoint.
    """
    model_config = ConfigDict(extra="forbid")

    artifact: ArtifactOneOf
    task: Task
    question: str = Field(..., min_length=1, max_length=8192)
    selector: Optional[Selector] = None
    output_mode: OutputMode = OutputMode.TEXT
    risk_tier: RiskTier = RiskTier.LOW
    policy: Optional[PolicyConstraints] = None
    structured_output_profile: Optional[StructuredOutputProfile] = None
    trace: Optional[TraceContext] = None

    def artifact_hash(self) -> Optional[str]:
        """Return SHA-256 of artifact bytes if inline, None otherwise (intake computes for id/uri)."""
        if self.artifact.inline_based:
            return hashlib.sha256(
                self.artifact.inline_based.inline_data.data.encode()
            ).hexdigest()
        return None


# ─── Output Models ───────────────────────────────────────────────────────


class ObservationRegion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None


class Observation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    label: ObservationLabel
    content: str = Field(..., min_length=1)
    source_region: Optional[ObservationRegion] = None
    confidence: Optional[float] = Field(None, ge=0, le=1)


class Interpretation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    claim: str = Field(..., min_length=1)
    confidence_band: ConfidenceBand = Field(..., description="[lower, upper] confidence interval")
    alternatives: list[str] = Field(..., min_length=1)
    reasoning_path: Optional[str] = None


class ConfidenceBand(BaseModel):
    """Enforced 2-tuple with 0 <= lo <= hi <= 1."""
    model_config = ConfigDict(extra="forbid")
    lo: float = Field(..., ge=0, le=1)
    hi: float = Field(..., ge=0, le=1)

    @model_validator(mode="after")
    def lo_le_hi(self) -> "ConfidenceBand":
        if self.lo > self.hi:
            raise ValueError(f"confidence_band lo ({self.lo}) must be <= hi ({self.hi})")
        return self


class ConfidenceBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    overall: float = Field(..., ge=0, le=1)
    band: ConfidenceBand = Field(..., description="[lower, upper] confidence interval")
    per_component: Optional[dict[str, float]] = None


class ModelInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    provider: str
    version: str
    tier: Optional[int] = Field(None, ge=0, le=4)


class Timestamps(BaseModel):
    model_config = ConfigDict(extra="forbid")
    received_at: datetime
    completed_at: datetime
    dispatched_at: Optional[datetime] = None
    model_start_at: Optional[datetime] = None
    model_end_at: Optional[datetime] = None


class Durations(BaseModel):
    model_config = ConfigDict(extra="forbid")
    total: float = Field(..., ge=0)
    intake: Optional[float] = Field(None, ge=0)
    model_inference: Optional[float] = Field(None, ge=0)
    post_processing: Optional[float] = Field(None, ge=0)


class CostInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    usd: Optional[float] = Field(None, ge=0)
    tokens_input: Optional[int] = Field(None, ge=0)
    tokens_output: Optional[int] = Field(None, ge=0)
    quota_source: Optional[str] = None


class Provenance(BaseModel):
    model_config = ConfigDict(extra="forbid")
    artifact_hash: str = Field(..., pattern=r"^[a-f0-9]{64}$",
                                description="SHA-256 of artifact bytes (hex)")
    route: list[str] = Field(..., description="Ordered processing hops")
    model: ModelInfo
    version: Literal["1.0.0"] = "1.0.0"
    prompt_profile: str
    timestamps: Timestamps
    duration_s: Durations
    cost: Optional[CostInfo] = None


class PolicyViolation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rule_id: str
    description: str
    action: PolicyAction


class PolicyOutcomes(BaseModel):
    model_config = ConfigDict(extra="forbid")
    egress_blocked: bool = False
    exif_redacted: bool = False
    prompt_injection_defused: bool = False
    classification_level: Optional[str] = None
    budget_remaining_usd: Optional[float] = None
    policy_violations: list[PolicyViolation] = []


class HumanReview(BaseModel):
    model_config = ConfigDict(extra="forbid")
    required: bool = False
    reason: Optional[str] = None
    ticket_id: Optional[str] = None
    risk_tier: Optional[RiskTier] = None


class MachineError(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: ErrorCode
    message: str
    detail: Optional[str] = None
    retryable: bool = False
    suggestion: Optional[str] = None


class VisionInvokeResponse(BaseModel):
    """
    vision.invoke — Provider-Neutral MCP Tool Output (v1.0.0)

    Separates raw observations from interpreted claims.
    Always includes provenance for auditability.
    """
    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(..., pattern=r"^vis_[a-z0-9_]{8,64}$")
    status: ResponseStatus
    verdict: VerdictTag
    answer: str = Field(..., min_length=1, max_length=16384)
    observations: list[Observation] = []
    interpretations: list[Interpretation] = []
    confidence: Optional[ConfidenceBlock] = None
    limitations: list[str] = []
    structured_data: Optional[dict[str, Any]] = None
    provenance: Provenance
    policy_outcomes: Optional[PolicyOutcomes] = None
    human_review: Optional[HumanReview] = None
    errors: list[MachineError] = []
