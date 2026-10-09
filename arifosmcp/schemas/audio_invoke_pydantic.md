# audio.invoke — Pydantic v2 Interfaces

> These mirror the JSON Schema Draft 2020-12 definitions in
> `arifosmcp/schemas/audio_invoke_*.schema.json`.
> The JSON Schema files are authoritative; these are developer conveniences.

```python
"""
arifOS — audio.invoke Pydantic v2 interfaces.
Provider-neutral MCP tool for governed audio analysis.
Generated from JSON Schema Draft 2020-12 (authoritative).
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ── Enums ────────────────────────────────────────────────────────────────────

class AudioMIME(str, Enum):
    WAV = "audio/wav"
    MP3 = "audio/mpeg"
    OGG = "audio/ogg"
    OPUS = "audio/opus"
    FLAC = "audio/flac"
    AAC = "audio/aac"
    M4A = "audio/mp4"
    WEBM_AUDIO = "audio/webm"
    X_M4A = "audio/x-m4a"
    MP4_VIDEO = "video/mp4"
    WEBM_VIDEO = "video/webm"
    QUICKTIME = "video/quicktime"
    MATROSKA = "video/x-matroska"


class AudioTask(str, Enum):
    TRANSCRIBE = "transcribe"
    CLASSIFY = "classify"
    DIARIZE = "diarize"
    DETECT_EVENTS = "detect_events"
    REASON = "reason"
    SUMMARIZE = "summarize"
    TRANSLATE = "translate"
    # v2 only:
    COMPARE = "compare"
    QUALITY_ASSESS = "quality_assess"


class RiskTier(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class OutputMode(str, Enum):
    FULL = "full"
    SUMMARY = "summary"
    SEGMENTS_ONLY = "segments_only"
    STRUCTURED_ONLY = "structured_only"
    # v2 only:
    STREAMING = "streaming"


class Verdict(str, Enum):
    CLAIM = "CLAIM"
    PLAUSIBLE = "PLAUSIBLE"
    HYPOTHESIS = "HYPOTHESIS"
    ESTIMATE = "ESTIMATE"
    UNKNOWN = "UNKNOWN"


class ResponseStatus(str, Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    ERROR = "error"
    HELD = "held"


class DataClassification(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"


class ArtifactRole(str, Enum):
    """v2 only."""
    PRIMARY = "primary"
    REFERENCE = "reference"
    BACKGROUND = "background"
    COMPARISON = "comparison"


class EventRating(str, Enum):
    """v2 only."""
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    UNUSABLE = "unusable"


class ErrorCode(str, Enum):
    INVALID_ARTIFACT = "invalid_artifact"
    UNSUPPORTED_MEDIA = "unsupported_media"
    ACCESS_DENIED = "access_denied"
    CONSENT_REQUIRED = "consent_required"
    CLASSIFICATION_BLOCKED = "classification_blocked"
    DURATION_EXCEEDED = "duration_exceeded"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    CAPABILITY_MISMATCH = "capability_mismatch"
    BUDGET_EXCEEDED = "budget_exceeded"
    LOW_CONFIDENCE = "low_confidence"
    POLICY_HOLD = "policy_hold"
    INTERNAL_ERROR = "internal_error"


# ── Input Models ─────────────────────────────────────────────────────────────

class TimeRange(BaseModel):
    start_ms: int = Field(ge=0, description="Start offset in milliseconds (inclusive).")
    end_ms: int = Field(ge=0, description="End offset in milliseconds (exclusive).")


class ArtifactRef(BaseModel):
    uri: str
    expected_mime_type: AudioMIME
    sha256: str | None = Field(
        default=None,
        pattern=r"^[a-fA-F0-9]{64}$",
        description="Optional SHA-256 hex digest.",
    )
    time_range: TimeRange | None = None
    channel_selector: str | list[int] | None = Field(
        default=None,
        description="'all', 'mono_mix', or list of zero-based channel indices.",
    )
    role_hint: ArtifactRole | None = Field(
        default=None,
        description="v2 only — artifact's role in multi-artifact fusion.",
    )


class AudioConstraints(BaseModel):
    max_cost_usd: float | None = Field(default=None, gt=0)
    max_latency_ms: int | None = Field(default=None, gt=0)
    external_provider: str | None = Field(
        default=None,
        description="Force a specific provider. Omit for automatic SOT routing.",
    )
    retain_transcript: bool = False
    redact_sensitive: bool = False
    # v2 only:
    confidence_floor: float | None = Field(default=None, ge=0, le=0.90)
    provider_fallback_chain: list[str] | None = None


class AudioInvokeInput(BaseModel):
    artifact_refs: list[ArtifactRef] = Field(min_length=1, max_length=10)
    task: AudioTask
    language_hint: str | None = Field(default=None, max_length=20)
    target_language: str | None = Field(default=None, max_length=20)
    output_mode: OutputMode = OutputMode.FULL
    risk_tier: RiskTier = RiskTier.MEDIUM
    constraints: AudioConstraints | None = None
    trace_id: str | None = Field(default=None, pattern=r"^[a-fA-F0-9]{32}$")
    dry_run: bool = False


# ── Output Models ────────────────────────────────────────────────────────────

class TranscriptSegment(BaseModel):
    start_ms: int = Field(ge=0)
    end_ms: int = Field(ge=0)
    text: str
    speaker: str | None = None
    asr_confidence: float | None = Field(default=None, ge=0, le=1)
    language: str | None = None
    artifact_index: int | None = Field(
        default=None, ge=0, description="v2 only."
    )


class DiarizationSegment(BaseModel):
    speaker: str = Field(pattern=r"^SPEAKER_[0-9]{2}$")
    start_ms: int = Field(ge=0)
    end_ms: int = Field(ge=0)
    artifact_index: int | None = Field(default=None, ge=0, description="v2 only.")


class AcousticEvent(BaseModel):
    event_type: str
    start_ms: int = Field(ge=0)
    end_ms: int | None = Field(default=None, ge=0)
    confidence: float = Field(ge=0, le=1)


class Interpretation(BaseModel):
    claim: str
    confidence_band: tuple[float, float] = Field(
        min_length=2, max_length=2,
        description="[lower, upper]. Upper capped at 0.90 per F7 HUMILITY.",
    )
    alternatives: list[str] | None = None


class ProvenanceTimestamps(BaseModel):
    received_utc: datetime
    started_utc: datetime | None = None
    completed_utc: datetime


class ProvenanceDuration(BaseModel):
    preflight_ms: int = Field(ge=0)
    routing_ms: int = Field(ge=0)
    processing_ms: int = Field(ge=0)
    total_ms: int = Field(ge=0)


class ProvenanceCost(BaseModel):
    currency: str = "USD"
    total: float = Field(ge=0)
    breakdown: dict[str, float] | None = None


class Provenance(BaseModel):
    hash: str = Field(pattern=r"^[a-fA-F0-9]{64}$")
    route: list[str]
    model: str | None = None
    version: str | None = None
    prompt_profile: str | None = None
    timestamps: ProvenanceTimestamps
    duration: ProvenanceDuration
    cost: ProvenanceCost | None = None


class PolicyOutcome(BaseModel):
    consent_verified: bool | None = None
    classification: DataClassification | None = None
    egress_approved: bool | None = None
    redactions_applied: int = Field(default=0, ge=0)
    human_review_required: bool = False


class TypedError(BaseModel):
    code: ErrorCode
    message: str
    detail: dict[str, Any] | None = None


# v2 fusion models

class CrossArtifactCorrelation(BaseModel):
    """v2 only."""
    artifact_indices: list[int]
    correlation_type: str
    description: str
    confidence: float = Field(ge=0, le=1)


class QualityComparison(BaseModel):
    """v2 only."""
    artifact_index: int
    snr_db: float
    clarity_score: float = Field(ge=0, le=1)
    rating: EventRating


class FusionEvidence(BaseModel):
    """v2 only."""
    cross_artifact_correlations: list[CrossArtifactCorrelation] | None = None
    quality_comparison: list[QualityComparison] | None = None


class QualityMetrics(BaseModel):
    """v2 only."""
    overall_snr_db: float | None = None
    overall_clarity: float | None = Field(default=None, ge=0, le=1)
    voice_activity_ratio: float | None = Field(default=None, ge=0, le=1)
    speaker_count_estimated: int | None = Field(default=None, ge=1)


class StreamingMetadata(BaseModel):
    """v2 only."""
    stream_id: str
    total_chunks: int = Field(ge=0)
    chunks_emitted: int = Field(ge=0)
    complete: bool


class AudioInvokeOutput(BaseModel):
    request_id: str
    status: ResponseStatus
    verdict: Verdict
    answer: str | None = None
    audio_observations: list[str] | None = None
    transcript_segments: list[TranscriptSegment] | None = None
    diarization_segments: list[DiarizationSegment] | None = None
    acoustic_events: list[AcousticEvent] | None = None
    interpretations: list[Interpretation] | None = None
    confidence_band: tuple[float, float] | None = None
    limitations: list[str] | None = None
    structured_data: dict[str, Any] | None = None
    provenance: Provenance | None = None
    policy: PolicyOutcome | None = None
    errors: list[TypedError] | None = None
    # v2 only:
    fusion_evidence: FusionEvidence | None = None
    quality_metrics: QualityMetrics | None = None
    streaming_metadata: StreamingMetadata | None = None
```
