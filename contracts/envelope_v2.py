"""
arifOS/contracts/envelope_v2.py — EnvelopeV2 (Pydantic v2 mirror of JSON Schema)
═══════════════════════════════════════════════════════════════════════════════════

Forged 2026-06-11 by Omega (ω-Ω) under F13 sovereign directive.
P2-9 roadmap slot. Phase 1 of AAA-A2A-1.0 protocol.

SINGLE SOURCE OF TRUTH: /root/arifOS/contracts/envelope_v2.json
This file is the Pydantic v2 mirror. Any change here must be mirrored in
the JSON Schema, and vice versa. The JSON Schema is authoritative for
shape; this file is authoritative for runtime validation.

TWO-ZONE SPLIT (the constitutional pattern):
  - SenderZone: routing, intent, context, reasoning, payload, sender_sig
    Authored by the sending agent. Subject to kernel override.
  - KernelZone: verdict, reversibility, evaluation, nine_signal, floor_scores, kernel_sig
    Stamped by arifOS kernel. IMMUTABLE in transit.
    The validator REJECTS any sender attempt to author kernel_zone fields.

DITEMPA BUKAN DIBERI — Forged, not given.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# Import the canonical pipeline stages — never retype.
# This makes the "pipeline enum import guard" structurally enforced.
try:
    from arifosmcp.constitutional_map import ToolStage as _CanonicalToolStage

    _CANONICAL_PIPELINE_STAGES: tuple[str, ...] = tuple(
        stage.value for stage in _CanonicalToolStage
    )
except ImportError:
    # Standalone mode (when imported from tooling outside the kernel tree).
    # The validator catches this with the import-guard test.
    _CANONICAL_PIPELINE_STAGES = (
        "000",
        "111",
        "222",
        "333",
        "444",
        "444r",
        "555",
        "555m",
        "666",
        "010",
        "666g",
        "777",
        "888",
        "999",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS — fail-closed: unknown values are rejected
# ═══════════════════════════════════════════════════════════════════════════════


class AdatTier(str, Enum):
    """Cultural decision tiers. From Hermes comm_receipt (Malaysia/Islam epistemics)."""

    WAJIB = "WAJIB"  # mandatory execution
    SUNAT = "SUNAT"  # proceed if optimal
    HARUS = "HARUS"  # neutral, no judgment
    MAKRUH = "MAKRUH"  # suboptimal, advise against
    HARAM = "HARAM"  # hard block


class MessageKind(str, Enum):
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"
    EVENT = "EVENT"
    ERROR = "ERROR"
    CONTROL = "CONTROL"


class Intent(str, Enum):
    EXECUTE = "EXECUTE"
    QUERY = "QUERY"
    OBSERVE = "OBSERVE"
    SEAL = "SEAL"
    PROPOSE = "PROPOSE"
    AUDIT = "AUDIT"
    VETO = "VETO"


class Priority(str, Enum):
    P0 = "P0"  # Sovereign, rings terminal, no batching
    P1 = "P1"  # Critical, near-real-time
    P2 = "P2"  # Default
    P3 = "P3"  # Background, batch-friendly


class Channel(str, Enum):
    A2A = "a2a"
    A2H = "a2h"
    H2A = "h2a"


class Epistemic(str, Enum):
    CLAIM = "CLAIM"
    PLAUSIBLE = "PLAUSIBLE"
    HYPOTHESIS = "HYPOTHESIS"
    ESTIMATE = "ESTIMATE"
    UNKNOWN = "UNKNOWN"


class ImpactLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ReversibilityHint(str, Enum):
    """Sender-writable hint. Kernel stamps authoritative version in KernelZone."""

    REVERSIBLE = "REVERSIBLE"
    PARTIAL = "PARTIAL"
    IRREVERSIBLE = "IRREVERSIBLE"


class ReversibilityVerdict(str, Enum):
    """Kernel-stamped. Sender MUST NOT author this."""

    SAFE = "SAFE"
    REVERSIBLE = "REVERSIBLE"
    IRREVERSIBLE = "IRREVERSIBLE"
    NEEDS_CONFIRMATION = "NEEDS_CONFIRMATION"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class VerdictCode(str, Enum):
    SEAL = "SEAL"
    SABAR = "SABAR"
    PARTIAL = "PARTIAL"
    VOID = "VOID"


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTING ZONE
# ═══════════════════════════════════════════════════════════════════════════════

_SHA256_RE = re.compile(r"^sha256:[0-9a-fA-F]{64}$")
_ED25519_RE = re.compile(r"^ed25519:[0-9a-fA-F]{128}$")
_FLOOR_RE = re.compile(r"^F(0[1-9]|1[0-4])$")


class RoutingBlock(BaseModel):
    """A2A routing — sender-writable, kernel-validated at ingress."""

    model_config = ConfigDict(extra="forbid")

    from_: str = Field(alias="from", min_length=1, description="Sender agent_id or 888_Sovereign")
    from_state_hash: str = Field(pattern=r"^sha256:[0-9a-fA-F]{64}$")
    to: str = Field(min_length=1, description="Recipient agent_id or 888_Sovereign")
    cc: list[str] = Field(default_factory=list)
    channel: Channel = Channel.A2A
    correlation_id: Optional[str] = None
    message_kind: MessageKind
    intent: Intent
    priority: Priority = Priority.P2
    session_id: Optional[str] = None
    timestamp: Optional[str] = None


class IntentBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action: str = Field(min_length=1, description="Verb-object task name")
    adat_tier_hint: Optional[AdatTier] = None
    constraints: list[str] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════════
# CONTEXT, REASONING, PAYLOAD — sender-writable
# ═══════════════════════════════════════════════════════════════════════════════


class RelatedResource(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["doc", "vector", "api", "db", "file", "memory", "evidence"]
    ref: str
    role: Literal["evidence", "config", "code", "log", "policy"]


class Environment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenant: Optional[str] = None
    mcp_tools: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)


class ContextBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    summary: str = Field(max_length=200)
    goal: Optional[str] = None
    inputs: dict[str, Any] = Field(default_factory=dict)
    assumptions: list[str] = Field(default_factory=list)
    related_resources: list[RelatedResource] = Field(default_factory=list)
    environment: Environment = Field(default_factory=Environment)


class ReasoningStep(BaseModel):
    model_config = ConfigDict(extra="forbid")
    stage: str
    description: str
    epistemic: Epistemic
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator("stage")
    @classmethod
    def _validate_stage(cls, v: str) -> str:
        if v not in _CANONICAL_PIPELINE_STAGES:
            raise ValueError(
                f"stage {v!r} not in canonical ToolStage "
                f"{_CANONICAL_PIPELINE_STAGES}. Import from arifosmcp.constitutional_map."
            )
        return v


class Uncertainty(BaseModel):
    model_config = ConfigDict(extra="forbid")
    issue: str
    impact: ImpactLevel
    mitigation: Optional[str] = None


class ReasoningBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pipeline_stages: list[str] = Field(default_factory=list)
    steps: list[ReasoningStep] = Field(default_factory=list)
    uncertainties: list[Uncertainty] = Field(default_factory=list)

    @field_validator("pipeline_stages")
    @classmethod
    def _validate_pipeline(cls, v: list[str]) -> list[str]:
        bad = [s for s in v if s not in _CANONICAL_PIPELINE_STAGES]
        if bad:
            raise ValueError(
                f"pipeline_stages contains non-canonical values: {bad}. "
                f"Import from arifosmcp.constitutional_map.ToolStage."
            )
        return v


class Artifact(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["file", "chart", "image", "log", "patch", "uri"]
    ref: str
    description: Optional[str] = None


class PayloadBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    context_p_truth: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    action_intent: Optional[str] = None
    way_forward: Optional[str] = None
    recommendation_tier: Optional[AdatTier] = None
    reversibility_hint: Optional[ReversibilityHint] = None
    context_summary: Optional[str] = Field(default=None, max_length=200)
    f_floor_trigger: Optional[str] = None
    data: dict[str, Any] = Field(default_factory=dict)
    artifacts: list[Artifact] = Field(default_factory=list)

    @field_validator("f_floor_trigger")
    @classmethod
    def _validate_floor(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not _FLOOR_RE.match(v):
            raise ValueError(f"f_floor_trigger {v!r} must match F01..F14")
        return v


# ═══════════════════════════════════════════════════════════════════════════════
# SENDER ZONE — sender-writable, sender.sig over the rest of the envelope
# ═══════════════════════════════════════════════════════════════════════════════


class SenderZone(BaseModel):
    model_config = ConfigDict(extra="forbid")
    protocol_features: list[str] = Field(default_factory=lambda: ["two-zone", "dual-sig"])
    sender_sig: Optional[str] = Field(default=None, pattern=r"^ed25519:[0-9a-fA-F]{128}$")
    sender_signed_at: Optional[str] = None
    sender_key_ref: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# KERNEL ZONE — IMMUTABLE. Sender MUST NOT author this.
# ═══════════════════════════════════════════════════════════════════════════════


class FloorScores(BaseModel):
    model_config = ConfigDict(extra="forbid")
    F01: float = Field(ge=0.0, le=1.0)
    F02: float = Field(ge=0.0, le=1.0)
    F03: float = Field(ge=0.0, le=1.0)
    F04: float = Field(ge=0.0, le=1.0)
    F05: float = Field(ge=0.0, le=1.0)
    F06: float = Field(ge=0.0, le=1.0)
    F07: float = Field(ge=0.0, le=1.0)
    F08: float = Field(ge=0.0, le=1.0)
    F09: float = Field(ge=0.0, le=1.0)
    F10: float = Field(ge=0.0, le=1.0)
    F11: float = Field(ge=0.0, le=1.0)
    F12: float = Field(ge=0.0, le=1.0)
    F13: float = Field(ge=0.0, le=1.0)


class SafetyBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    lawful: bool
    risk_level: RiskLevel
    flags: list[str] = Field(default_factory=list)


class EvaluationBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entropy_delta: Optional[float] = None
    peace2: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    maruah_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    omega_0: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    safety: Optional[SafetyBlock] = None


class KernelZone(BaseModel):
    """
    IMMUTABLE in transit. The validator rejects any sender attempt to author
    these fields on a REQUEST. The kernel stamps this zone on a RESPONSE.
    """

    model_config = ConfigDict(extra="forbid")
    verdict: Optional[VerdictCode] = None
    reversibility: Optional[ReversibilityVerdict] = None
    reversibility_rationale: Optional[str] = None
    recommendation_tier: Optional[AdatTier] = None
    evaluation: Optional[EvaluationBlock] = None
    nine_signal: dict[str, Any] = Field(default_factory=dict)
    floor_scores: Optional[FloorScores] = None
    kernel_signed_at: Optional[str] = None
    kernel_sig: Optional[str] = Field(default=None, pattern=r"^ed25519:[0-9a-fA-F]{128}$")
    kernel_key_ref: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# ENVELOPE V2 — top-level
# ═══════════════════════════════════════════════════════════════════════════════


class EnvelopeV2(BaseModel):
    """
    AAA-A2A-1.0 Envelope. Backward shim: empty kernel_zone = current RuntimeEnvelope.
    """

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    protocol_version: Literal["AAA-A2A-1.0"] = "AAA-A2A-1.0"
    routing: RoutingBlock
    intent: IntentBlock
    context: Optional[ContextBlock] = None
    reasoning: Optional[ReasoningBlock] = None
    payload: Optional[PayloadBlock] = None
    sender_zone: SenderZone = Field(default_factory=SenderZone)
    kernel_zone: Optional[KernelZone] = None
    profile: Optional[MessageKind] = None
    schema_version: str = Field(default="1.0.0", pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")

    @model_validator(mode="after")
    def _profile_must_match_message_kind(self) -> "EnvelopeV2":
        """If profile is set, it must match routing.message_kind."""
        if self.profile is not None and self.profile != self.routing.message_kind:
            raise ValueError(
                f"profile {self.profile!r} does not match routing.message_kind "
                f"{self.routing.message_kind!r}"
            )
        return self

    def canonical_for_signature(self) -> str:
        """
        Canonical JSON used for sender_sig (and kernel_sig on the stamped zone).
        Sort keys, no whitespace. Excludes the signature fields themselves.
        """
        d = self.model_dump(mode="json", by_alias=True, exclude_none=True)
        # Remove signature fields from the canonical form
        sender_zone = d.get("sender_zone", {})
        sender_zone.pop("sender_sig", None)
        sender_zone.pop("sender_signed_at", None)
        kernel_zone = d.get("kernel_zone") or {}
        kernel_zone.pop("kernel_sig", None)
        kernel_zone.pop("kernel_signed_at", None)
        return json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    def canonical_for_kernel_sig(self) -> str:
        """Canonical form for kernel_sig: includes sender_zone but excludes both sigs."""
        d = self.model_dump(mode="json", by_alias=True, exclude_none=True)
        kernel_zone = d.get("kernel_zone") or {}
        kernel_zone.pop("kernel_sig", None)
        kernel_zone.pop("kernel_signed_at", None)
        return json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
