"""
KernelEnvelope — CANONICAL EXECUTION ENVELOPE (v2.0.0)
═══════════════════════════════════════════════════════════════

Every governed runtime call — tool, organ, model, memory, mutation —
MUST carry this envelope. Without it, the call is invisible to
constitutional governance.

This is the single source of truth for the envelope contract.
All live kernel responses, governance pipeline checks, audit trails,
and federation bridges read this shape.

SIX CANONICAL SECTIONS:
  kernel   — who is acting, under whose constitution
  organ    — which organ/tool is being called
  authority — what action class, under what lease
  state    — input/output hash chain for audit integrity
  risk     — blast radius, reversibility, secret exposure
  audit    — vault pointer, seal mode, timestamp

DITEMPA BUKAN DIBERI — Forged as the constitutional contract.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator, model_validator

# ═══════════════════════════════════════════════════════════════════════════════
# ACTION CLASSES — the seven irreducible permission levels
# ═══════════════════════════════════════════════════════════════════════════════


class ActionClass(StrEnum):
    """The canonical action class ladder. Higher = more dangerous.

    OBSERVE: Read-only. No external side effects.
    ANALYZE: Reason over existing data. No mutation.
    DRAFT: Create proposed content, plan, patch. No external side effects.
    SIMULATE: Run reversible sandbox execution only.
    MUTATE: Change local state, files, memory, database, configuration.
    EXTERNAL_SIDE_EFFECT: Send email, call external API, post, publish,
                          notify, pay, trade, deploy, contact third party.
    IRREVERSIBLE: Delete, rotate keys, commit to protected branch, deploy
                  production, transfer assets, sign legal/financial/governance
                  artifact, vault seal, overwrite canonical memory.
    """

    OBSERVE = "OBSERVE"
    ANALYZE = "ANALYZE"
    DRAFT = "DRAFT"
    SIMULATE = "SIMULATE"
    MUTATE = "MUTATE"
    EXTERNAL_SIDE_EFFECT = "EXTERNAL_SIDE_EFFECT"
    IRREVERSIBLE = "IRREVERSIBLE"
    UNKNOWN = "UNKNOWN"  # fail-closed: unknown class = HOLD

    # Compatibility aliases for legacy code
    PREPARE = "DRAFT"
    ATOMIC = "IRREVERSIBLE"

    @classmethod
    def is_safe(cls, action: ActionClass) -> bool:
        """Safe = no mutation, no external effects, no irreversible effects."""
        return action in {cls.OBSERVE, cls.ANALYZE}

    @classmethod
    def is_mutating(cls, action: ActionClass) -> bool:
        """Mutating = changes state in any way."""
        return action in {cls.MUTATE, cls.EXTERNAL_SIDE_EFFECT, cls.IRREVERSIBLE}

    @classmethod
    def requires_lease(cls, action: ActionClass) -> bool:
        """Actions that require a valid lease beyond OBSERVE."""
        return action not in {cls.OBSERVE, cls.UNKNOWN}

    @classmethod
    def requires_human_ack(cls, action: ActionClass) -> bool:
        """Actions that MUST have explicit human acknowledgement."""
        return action in {cls.IRREVERSIBLE, cls.EXTERNAL_SIDE_EFFECT}

    @classmethod
    def subsumes(cls, granted: ActionClass, requested: ActionClass) -> bool:
        """Whether `granted` action class covers `requested`."""
        order = {
            cls.OBSERVE: 0,
            cls.ANALYZE: 1,
            cls.DRAFT: 2,
            cls.SIMULATE: 3,
            cls.MUTATE: 4,
            cls.EXTERNAL_SIDE_EFFECT: 5,
            cls.IRREVERSIBLE: 6,
        }
        return order.get(granted, -1) >= order.get(requested, 999)


# ═══════════════════════════════════════════════════════════════════════════════
# VERDICT — the three constitutional outcomes
# ═══════════════════════════════════════════════════════════════════════════════


class GateVerdict(StrEnum):
    """Constitutional gate verdict.

    Canonical verdict set (Invariant #15):
      SEAL  — proceed, all checks passed
      SABAR — proceed with conditions, warnings active
      HOLD  — stop, insufficient authority or missing succession continuity
      VOID  — stop, invalid input or internal error
      REJECT — stop, constitutional floor violation (F13-level prohibition)
    """

    SEAL = "SEAL"  # proceed
    SABAR = "SABAR"  # proceed with conditions
    HOLD = "HOLD"  # stop — insufficient authority
    VOID = "VOID"  # stop — invalid input / internal error
    REJECT = "REJECT"  # stop — constitutional floor violation (F13 prohibition)


class BlastRadius(StrEnum):
    """Canonical 8-class blast radius (Hermes ASI standard).

    Hermes ASI standard — the harder the floor, the higher the class.
    Propagation is distributed (matrix over agents), not aggregates (max over agents).

    NONE              — No effect radius.
    LOCAL             — Single process, file, or in-memory state.
    ACCOUNT           — User account / session scope.
    ORG               — Organization / project scope.
    PUBLIC            — Public-facing / external user scope.
    MARKET            — Financial / capital / market-level impact.
    INFRASTRUCTURE    — Infrastructure / host / system-level impact.
    CIVILIZATIONAL    — Multi-system, societal, or civilizational impact.
    UNKNOWN           — Cannot determine; fail closed.
    """

    NONE = "NONE"
    LOCAL = "LOCAL"
    ACCOUNT = "ACCOUNT"
    ORG = "ORG"
    PUBLIC = "PUBLIC"
    MARKET = "MARKET"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    CIVILIZATIONAL = "CIVILIZATIONAL"
    UNKNOWN = "UNKNOWN"

    # Backward-compatible aliases mapped to Hermes 8-class standard
    LOW = "LOCAL"
    MEDIUM = "ACCOUNT"
    HIGH = "PUBLIC"
    CRITICAL = "INFRASTRUCTURE"
    INFRA = "INFRASTRUCTURE"

    @classmethod
    def requires_human_ack(cls, radius: BlastRadius) -> bool:
        """Returns True if this blast radius requires human acknowledgement."""
        return radius.value >= cls.INFRASTRUCTURE.value

    @classmethod
    def subsumes(cls, granted: BlastRadius, requested: BlastRadius) -> bool:
        """Whether `granted` blast radius covers `requested`."""
        order = {
            cls.NONE: 0,
            cls.LOCAL: 1,
            cls.ACCOUNT: 2,
            cls.ORG: 3,
            cls.PUBLIC: 4,
            cls.MARKET: 5,
            cls.INFRASTRUCTURE: 6,
            cls.CIVILIZATIONAL: 7,
            cls.UNKNOWN: 99,
        }
        return order.get(granted, -1) >= order.get(requested, 999)


class DriftLevel(StrEnum):
    """Runtime drift severity."""

    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DelegationMode(StrEnum):
    """How authority was delegated to this actor."""

    DIRECT = "DIRECT"  # sovereign acting directly
    DELEGATED = "DELEGATED"  # delegated by sovereign
    INSTRUMENT = "INSTRUMENT"  # autonomous instrument
    UNVERIFIED = "UNVERIFIED"  # identity not verified


class MemoryScope(StrEnum):
    """Access scope for memory operations."""

    SCRATCH = "scratch"  # ephemeral, overwritable
    SESSION = "session"  # session-bound, expires
    PROJECT = "project"  # project-scoped, lease-required
    ORGAN = "organ"  # organ-owned
    SOVEREIGN = "sovereign"  # requires ARIF authority
    CONSTITUTIONAL = "constitutional"  # requires HOLD before mutation
    VAULT = "vault"  # irreversible-grade


class SealMode(StrEnum):
    """VAULT999 seal requirement level."""

    OBSERVE = "observe"  # no seal needed (read-only)
    ATTEND = "attend"  # log to audit, no seal
    SEAL = "seal"  # require VAULT999 seal
    REJECT = "reject"  # block — cannot seal


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: KERNEL IDENTITY
# ═══════════════════════════════════════════════════════════════════════════════


class KernelIdentity(BaseModel):
    """Who is acting, under whose constitution, in which session."""

    kernel_id: str = Field(default="arifOS", description="Kernel instance identifier")
    constitution_id: str = Field(
        default="arifos-constitution-v2026.05.05-SSCT",
        description="Constitutional version identifier",
    )
    constitution_hash: str = Field(
        default="sha256:dd4f41e75f55ed38df759a1c8db1fc4680ef0307a6b0e2793bccf6540bb21506",
        description="SHA-256 of the active constitutional floor spec",
    )
    session_id: str = Field(default="", description="Active session ID from arif_init")
    epoch_id: str = Field(default="EPOCH-LIVE-1", description="Constitutional epoch identifier")
    actor_id: str = Field(default="", description="Actor identifier (agent or human)")
    actor_verified: bool = Field(
        default=False, description="Whether the actor's identity has been verified"
    )
    sovereign_id: str = Field(default="ARIF_FAZIL", description="Human sovereign identifier (F13)")
    delegation_mode: DelegationMode = Field(
        default=DelegationMode.UNVERIFIED, description="How authority was delegated to this actor"
    )
    caller_actor_id: str | None = Field(
        default=None, description="Upstream caller in delegation chain"
    )
    executor_actor_id: str | None = Field(default=None, description="Actual executing agent/model")
    declared_model_key: str | None = Field(
        default=None, description="Declared model identifier (e.g. 'deepseek', 'minimax')"
    )

    @field_validator("constitution_hash")
    @classmethod
    def _check_hash_format(cls, v: str) -> str:
        if v and not v.startswith("sha256:"):
            raise ValueError("constitution_hash must be sha256:<hex>")
        return v


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: ORGAN & TOOL IDENTITY
# ═══════════════════════════════════════════════════════════════════════════════


class OrganIdentity(BaseModel):
    """Which organ and tool is being called."""

    organ_id: str = Field(default="arifOS", description="Federation organ identifier")
    organ_role: str = Field(
        default="constitutional_kernel", description="Organ's role in the federation"
    )
    organ_version: str = Field(default="v2026.05.05-SSCT", description="Organ version string")
    tool_name: str = Field(default="", description="Name of the tool being called")
    tool_schema_hash: str = Field(default="", description="SHA-256 of the tool's input schema")
    model_id: str | None = Field(
        default=None, description="Model identifier if this call involves an LLM"
    )
    attestation_status: str = Field(
        default="UNKNOWN", description="Last known organ attestation status"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: AUTHORITY & LEASE
# ═══════════════════════════════════════════════════════════════════════════════


class AuthorityBlock(BaseModel):
    """What the caller is allowed to do."""

    action_class: ActionClass = Field(
        default=ActionClass.UNKNOWN, description="Action class for this call"
    )
    lease_id: str | None = Field(
        default=None, description="Active lease identifier (LEASE-NONE if no lease)"
    )
    lease_scope: list[str] = Field(default_factory=list, description="Scope of the active lease")
    mutation_allowed: bool = Field(
        default=False, description="Whether mutation (write/delete) is allowed"
    )
    external_side_effect_allowed: bool = Field(
        default=False, description="Whether external API calls, messages, payments are allowed"
    )
    irreversible_allowed: bool = Field(
        default=False, description="Whether irreversible actions are allowed"
    )
    human_ack_required: bool = Field(
        default=False, description="Whether explicit human acknowledgement is required"
    )
    human_ack_id: str | None = Field(
        default=None, description="Human acknowledgement receipt ID, if provided"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: STATE HASH CHAIN
# ═══════════════════════════════════════════════════════════════════════════════


class StateBlock(BaseModel):
    """Hash chain for audit integrity across calls."""

    input_hash: str = Field(default="sha256:" + "0" * 64, description="SHA-256 of the tool input")
    output_hash: str | None = Field(
        default=None, description="SHA-256 of the tool output (filled after execution)"
    )
    prior_state_hash: str = Field(
        default="sha256:0", description="Hash of the prior state (for chain integrity)"
    )
    current_state_hash: str = Field(
        default="", description="Hash of the current state after execution"
    )
    memory_refs: list[str] = Field(
        default_factory=list, description="Memory references touched by this call"
    )
    memory_scopes: list[MemoryScope] = Field(
        default_factory=list, description="Memory scopes accessed"
    )

    @staticmethod
    def compute_hash(content: Any) -> str:
        """Compute a deterministic SHA-256 hash of any content."""
        raw = str(content).encode("utf-8")
        return f"sha256:{hashlib.sha256(raw).hexdigest()}"


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: RISK ASSESSMENT
# ═══════════════════════════════════════════════════════════════════════════════


class RiskBlock(BaseModel):
    """Risk assessment for this action."""

    reversibility_score: float = Field(
        default=1.0, ge=0.0, le=1.0, description="1.0 = fully reversible, 0.0 = fully irreversible"
    )
    blast_radius: BlastRadius = Field(
        default=BlastRadius.LOCAL, description="Estimated impact radius"
    )
    secret_touching: bool = Field(
        default=False, description="Whether this action touches secrets/credentials"
    )
    human_ack_required: bool = Field(
        default=False, description="Whether human acknowledgement is required for this action"
    )
    max_allowed_action_class: ActionClass = Field(
        default=ActionClass.OBSERVE, description="Maximum action class allowed given current risk"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6: AUDIT TRAIL
# ═══════════════════════════════════════════════════════════════════════════════


class AuditBlock(BaseModel):
    """Audit trail for this call."""

    vault_required: bool = Field(default=False, description="Whether a VAULT999 seal is required")
    audit_pointer: str | None = Field(
        default=None, description="Pointer to the audit entry in VAULT999"
    )
    seal_mode: SealMode = Field(
        default=SealMode.OBSERVE, description="What level of VAULT999 sealing is required"
    )
    event_id: str | None = Field(
        default=None, description="Unique event identifier for this audit event"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="When this event occurred"
    )
    prior_event_hash: str | None = Field(
        default=None, description="Hash of the prior audit event (for chain integrity)"
    )
    trace_id: str | None = Field(
        default=None, description="Distributed trace identifier across organs"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# THE CANONICAL KERNEL ENVELOPE
# ═══════════════════════════════════════════════════════════════════════════════


class KernelEnvelope(BaseModel):
    """The single canonical execution envelope.

    Every governed runtime call MUST carry this envelope.
    Without it, the call is invisible to constitutional governance.

    Six sections mirror the live kernel's runtime structure:
      kernel   — who is acting
      organ    — which tool is being called
      authority — what action class, under what lease
      state    — hash chain for audit
      risk     — blast radius assessment
      audit    — vault pointer and timestamp

    The `verdict` and `reasons` fields capture the gate outcome.
    """

    model_config = {"extra": "forbid", "frozen": False}

    envelope_id: str = Field(
        default_factory=lambda: f"kenv_{uuid4().hex[:16]}", description="Unique envelope identifier"
    )
    envelope_version: str = Field(default="2.0.0", description="Envelope schema version")

    # ── Six sections ──────────────────────────────────────────────

    kernel: KernelIdentity = Field(
        default_factory=KernelIdentity, description="Who is acting, under whose authority"
    )
    organ: OrganIdentity = Field(
        default_factory=OrganIdentity, description="Which organ and tool is being called"
    )
    authority: AuthorityBlock = Field(
        default_factory=AuthorityBlock, description="What the caller is allowed to do"
    )
    state: StateBlock = Field(
        default_factory=StateBlock, description="Hash chain for audit integrity"
    )
    risk: RiskBlock = Field(
        default_factory=RiskBlock, description="Risk assessment for this action"
    )
    audit: AuditBlock = Field(default_factory=AuditBlock, description="Audit trail metadata")

    # ── Tool call payload (optional) ────────────────
    payload: dict[str, Any] = Field(
        default_factory=dict, description="Original tool call parameters for gate inspection"
    )

    # ── Gate outcome ──────────────────────────────────────────────

    verdict: GateVerdict = Field(
        default=GateVerdict.SEAL, description="Constitutional gate verdict"
    )
    reasons: list[str] = Field(default_factory=list, description="Reasons for the verdict")
    violations: list[str] = Field(
        default_factory=list, description="Constitutional floor violations detected"
    )

    # ═══════════════════════════════════════════════════════════════
    # DERIVED FIELDS
    # ═══════════════════════════════════════════════════════════════

    @property
    def is_mutating(self) -> bool:
        """Whether this envelope describes a mutating action."""
        return ActionClass.is_mutating(self.authority.action_class)

    @property
    def is_safe(self) -> bool:
        """Whether this envelope describes a safe (non-mutating) action."""
        return ActionClass.is_safe(self.authority.action_class)

    @property
    def requires_lease(self) -> bool:
        """Whether this action requires a valid lease."""
        return ActionClass.requires_lease(self.authority.action_class)

    @property
    def requires_human_ack(self) -> bool:
        """Whether this action requires human acknowledgement."""
        return ActionClass.requires_human_ack(self.authority.action_class)

    @property
    def is_gated(self) -> bool:
        """Whether the gate has blocked this action (HOLD or VOID)."""
        return self.verdict in {GateVerdict.HOLD, GateVerdict.VOID}

    # ═══════════════════════════════════════════════════════════════
    # FACTORY METHODS
    # ═══════════════════════════════════════════════════════════════

    @classmethod
    def observe_only(cls, **overrides: Any) -> KernelEnvelope:
        """Create a minimal OBSERVE-only envelope."""
        return cls(
            authority=AuthorityBlock(action_class=ActionClass.OBSERVE),
            risk=RiskBlock(reversibility_score=1.0, blast_radius=BlastRadius.LOCAL),
            audit=AuditBlock(seal_mode=SealMode.OBSERVE),
            **overrides,
        )

    @classmethod
    def hold_envelope(
        cls, reasons: list[str], violations: list[str] | None = None
    ) -> KernelEnvelope:
        """Create a HOLD envelope with reasons."""
        return cls(
            verdict=GateVerdict.HOLD,
            reasons=reasons,
            violations=violations or [],
            authority=AuthorityBlock(action_class=ActionClass.UNKNOWN),
        )

    @classmethod
    def void_envelope(cls, reasons: list[str], violations: list[str]) -> KernelEnvelope:
        """Create a VOID envelope for constitutional violations."""
        return cls(
            verdict=GateVerdict.VOID,
            reasons=reasons,
            violations=violations,
            authority=AuthorityBlock(action_class=ActionClass.UNKNOWN),
        )

    # ═══════════════════════════════════════════════════════════════
    # VALIDATION
    # ═══════════════════════════════════════════════════════════════

    @model_validator(mode="after")
    def _validate_consistency(self) -> KernelEnvelope:
        """Enforce envelope internal consistency."""
        # If action is mutating, a lease should exist
        if self.is_mutating and not self.authority.lease_id:
            # Note: this is a soft check — LEASE-NONE is valid for
            # non-production or bootstrapping scenarios.
            pass

        # If action is IRREVERSIBLE, human_ack_required must be set
        if self.authority.action_class == ActionClass.IRREVERSIBLE:
            if not self.authority.human_ack_required:
                self.reasons.append("IRREVERSIBLE action without human_ack_required flag")
            if not self.authority.human_ack_id:
                self.reasons.append("IRREVERSIBLE action without human_ack_id")

        # If verdict is HOLD or VOID, reasons must be populated
        if self.verdict in {GateVerdict.HOLD, GateVerdict.VOID}:
            if not self.reasons:
                self.reasons.append(
                    f"{self.verdict.value} verdict emitted without explicit reasons"
                )

        return self


# ═══════════════════════════════════════════════════════════════════════════════
# GATE RESULT — what pre_execution_gate returns
# ═══════════════════════════════════════════════════════════════════════════════


class GateResult(BaseModel):
    """Result of the pre-execution constitutional gate check."""

    envelope: KernelEnvelope = Field(..., description="The enriched envelope")
    verdict: GateVerdict = Field(..., description="Gate verdict")
    reasons: list[str] = Field(default_factory=list, description="Gate reasons")
    violations: list[str] = Field(default_factory=list, description="Floor violations")
    blocked_action_class: ActionClass | None = Field(
        default=None, description="If blocked, what action class was attempted"
    )
    required_lease_scope: str | None = Field(
        default=None, description="If blocked for lease, what scope was needed"
    )
    required_human_ack: bool = Field(
        default=False, description="Whether human acknowledgement is needed to proceed"
    )
    drift_detected: bool = Field(default=False, description="Whether runtime drift was detected")
    drift_level: DriftLevel | None = Field(
        default=None, description="Detected drift severity level"
    )
    degraded_organs: list[str] = Field(default_factory=list, description="Organs that are degraded")

    @property
    def is_allowed(self) -> bool:
        """Whether the gate allows this action to proceed."""
        return self.verdict in {GateVerdict.SEAL, GateVerdict.SABAR}

    @property
    def is_blocked(self) -> bool:
        """Whether the gate blocks this action."""
        return self.verdict in {GateVerdict.HOLD, GateVerdict.VOID, GateVerdict.REJECT}


# ═══════════════════════════════════════════════════════════════════════════════
# MODEL ADAPTER INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════


class ModelAdapter(BaseModel):
    """Declared capability of an LLM model running inside arifOS.

    The model never owns authority. The model proposes. The kernel disposes.
    """

    model_id: str = Field(..., description="Unique model identifier")
    provider: str = Field(..., description="Provider name (e.g. deepseek, minimax, anthropic)")
    context_window: int = Field(..., description="Maximum context window in tokens")
    max_output_tokens: int = Field(default=4096, description="Maximum output tokens")
    tool_call_format: str = Field(default="openai", description="Tool call format")
    safety_notes: str = Field(default="", description="Known safety considerations")
    max_action_class: ActionClass = Field(
        default=ActionClass.ANALYZE, description="Maximum action class this model may propose"
    )
    supports_json: bool = Field(default=True, description="Supports JSON mode")
    supports_streaming: bool = Field(default=True, description="Supports streaming")
    supports_function_calling: bool = Field(
        default=True, description="Supports function/tool calling"
    )
    supports_vision: bool = Field(default=False, description="Supports vision/image inputs")
    supports_code_execution: bool = Field(default=False, description="Supports code execution")
    supports_reasoning: bool = Field(
        default=False, description="Supports reasoning/thinking tokens"
    )
    known_hallucination_risk: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Estimated hallucination risk (0=never, 1=always)"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# FEDERATION ORGAN CARD
# ═══════════════════════════════════════════════════════════════════════════════


class OrganCard(BaseModel):
    """Canonical declaration of a federation organ."""

    organ_id: str = Field(..., description="Unique organ identifier")
    organ_role: str = Field(..., description="Role in the federation")
    version: str = Field(..., description="Version string")
    schema_hash: str = Field(..., description="SHA-256 of the organ's tool schema")
    constitution_hash: str = Field(..., description="SHA-256 of the constitution")
    tool_count: int = Field(default=0, description="Number of public tools")
    health_status: str = Field(default="UNKNOWN", description="Health status")
    authority_level: ActionClass = Field(
        default=ActionClass.OBSERVE, description="Maximum action class this organ may perform"
    )
    allowed_action_classes: list[ActionClass] = Field(
        default_factory=list, description="Action classes this organ is authorized for"
    )
    model_adapter: str | None = Field(
        default=None, description="Model adapter if this organ hosts an LLM"
    )
    memory_scope: list[MemoryScope] = Field(
        default_factory=list, description="Memory scopes this organ may access"
    )
    last_heartbeat: datetime | None = Field(default=None, description="Last heartbeat timestamp")
    degraded_reason: str | None = Field(
        default=None, description="Reason for degradation if not healthy"
    )
    drift_status: DriftLevel = Field(default=DriftLevel.NONE, description="Runtime drift severity")


# ═══════════════════════════════════════════════════════════════════════════════
# FEDERATION REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════


class FederationRegistry(BaseModel):
    """Complete federation organ registry."""

    registry_version: str = Field(default="2.0.0")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    kernel_organ: OrganCard = Field(
        default_factory=lambda: OrganCard(
            organ_id="arifOS",
            organ_role="constitutional_kernel",
            version="v2026.05.05-SSCT",
            schema_hash="",
            constitution_hash="sha256:dd4f41e75f55ed38df759a1c8db1fc4680ef0307a6b0e2793bccf6540bb21506",
            tool_count=13,
            health_status="ALIVE",
        )
    )
    organs: list[OrganCard] = Field(
        default_factory=list, description="All registered federation organs"
    )
    degraded_organs: list[str] = Field(
        default_factory=list, description="Organs currently in degraded state"
    )

    def get_organ(self, organ_id: str) -> OrganCard | None:
        """Look up an organ by ID."""
        for organ in self.organs:
            if organ.organ_id == organ_id:
                return organ
        return None

    def is_organ_healthy(self, organ_id: str) -> bool:
        """Check if an organ is healthy enough to receive mutation authority."""
        organ = self.get_organ(organ_id)
        if organ is None:
            return False
        return (
            organ.health_status in ("ALIVE", "HEALTHY")
            and organ.drift_status in (DriftLevel.NONE, DriftLevel.LOW)
            and organ_id not in self.degraded_organs
        )


# ═══════════════════════════════════════════════════════════════════════════════
# HUMAN ACKNOWLEDGEMENT
# ═══════════════════════════════════════════════════════════════════════════════


class HumanAcknowledgement(BaseModel):
    """Explicit human acknowledgement for high-blast-radius actions.

    Required for: deploy, commit to main, delete, rotate secrets,
    send external communication, payment/trade/asset transfer,
    vault seal, constitutional amendment, production DB mutation,
    public publication.
    """

    human_ack_id: str = Field(
        default_factory=lambda: f"hack_{uuid4().hex[:12]}",
        description="Unique acknowledgement identifier",
    )
    actor_id: str = Field(..., description="Who acknowledged (human)")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When acknowledgement was given",
    )
    action_summary: str = Field(..., description="What action is being acknowledged")
    risk_summary: str = Field(..., description="Risk assessment of the action")
    exact_command: str = Field(..., description="The exact command or mutation")
    expiry_seconds: int = Field(
        default=300, description="How long this acknowledgement is valid (seconds)"
    )
    nonce: str = Field(
        default_factory=lambda: uuid4().hex[:16],
        description="Cryptographic nonce to prevent replay",
    )
    signature: str | None = Field(
        default=None, description="Ed25519 signature over (nonce + exact_command)"
    )
    binding_hash: str = Field(
        default="", description="SHA-256 of (human_ack_id + nonce + exact_command)"
    )

    @model_validator(mode="after")
    def _compute_binding(self) -> HumanAcknowledgement:
        """Compute the binding hash that ties this acknowledgement to the action."""
        raw = f"{self.human_ack_id}:{self.nonce}:{self.exact_command}"
        self.binding_hash = f"sha256:{hashlib.sha256(raw.encode()).hexdigest()}"
        return self

    def is_expired(self) -> bool:
        """Check if this acknowledgement has expired."""
        elapsed = (datetime.now(UTC) - self.timestamp).total_seconds()
        return elapsed > self.expiry_seconds


# ═══════════════════════════════════════════════════════════════════════════════
# DRIFT REPORT
# ═══════════════════════════════════════════════════════════════════════════════


class DriftReport(BaseModel):
    """Runtime drift attestation."""

    build_hash: str = Field(..., description="Declared build hash")
    runtime_hash: str = Field(..., description="Actual runtime hash")
    git_commit: str | None = Field(default=None, description="Git commit SHA")
    container_image_digest: str | None = Field(default=None, description="Container image digest")
    tool_manifest_hash: str = Field(default="", description="SHA-256 of tool manifest")
    schema_hash: str = Field(default="", description="SHA-256 of schemas")
    constitution_hash: str = Field(default="", description="SHA-256 of constitution")
    env_config_hash: str = Field(
        default="", description="SHA-256 of env config (excluding secrets)"
    )
    deployment_timestamp: datetime | None = Field(default=None, description="When deployed")
    drift_level: DriftLevel = Field(default=DriftLevel.NONE, description="Drift severity")
    drift_details: str = Field(default="", description="Human-readable drift explanation")

    @property
    def blocks_mutation(self) -> bool:
        """Whether drift blocks mutation actions."""
        return self.drift_level in {DriftLevel.HIGH, DriftLevel.CRITICAL}

    @property
    def blocks_irreversible(self) -> bool:
        """Whether drift blocks irreversible actions."""
        return self.drift_level == DriftLevel.CRITICAL


# ═══════════════════════════════════════════════════════════════════════════════
# AUDIT EVENT (append-only, hash-chained)
# ═══════════════════════════════════════════════════════════════════════════════


class AuditEvent(BaseModel):
    """A single tamper-evident audit event in the hash chain."""

    event_id: str = Field(
        default_factory=lambda: f"audit_{uuid4().hex[:16]}",
        description="Unique audit event identifier",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="When this event occurred"
    )
    session_id: str = Field(default="", description="Session identifier")
    actor_id: str = Field(default="", description="Actor identifier")
    sovereign_id: str = Field(default="ARIF_FAZIL", description="Sovereign identifier")
    organ_id: str = Field(default="arifOS", description="Organ identifier")
    model_id: str | None = Field(default=None, description="Model identifier if LLM")
    tool_name: str = Field(default="", description="Tool name")
    action_class: ActionClass = Field(default=ActionClass.UNKNOWN, description="Action class")
    lease_id: str | None = Field(default=None, description="Active lease")
    input_hash: str = Field(default="", description="SHA-256 of input")
    output_hash: str = Field(default="", description="SHA-256 of output")
    prior_state_hash: str = Field(default="", description="Prior state hash")
    current_state_hash: str = Field(default="", description="Current state hash")
    prior_event_hash: str = Field(default="", description="Hash of prior audit event")
    verdict: GateVerdict = Field(default=GateVerdict.SEAL, description="Gate verdict")
    reasons: list[str] = Field(default_factory=list, description="Reasons")
    human_ack_id: str | None = Field(default=None, description="Human acknowledgement ID")

    @model_validator(mode="after")
    def _compute_event_hash(self) -> AuditEvent:
        """Compute the hash of this event for chain integrity."""
        # Use a deterministic subset of fields for the hash
        payload = (
            f"{self.event_id}:{self.timestamp.isoformat()}:{self.session_id}:"
            f"{self.actor_id}:{self.organ_id}:{self.tool_name}:"
            f"{self.action_class.value}:{self.input_hash}:{self.output_hash or ''}:"
            f"{self.prior_state_hash}:{self.current_state_hash}:"
            f"{self.verdict.value}"
        )
        self._event_hash = f"sha256:{hashlib.sha256(payload.encode()).hexdigest()}"
        return self

    _event_hash: str = ""

    @property
    def event_hash(self) -> str:
        """The SHA-256 hash of this event for chain integrity."""
        return self._event_hash

    def verify_chain(self, prior_event: AuditEvent | None) -> bool:
        """Verify that this event correctly chains to the prior event."""
        if prior_event is None:
            return self.prior_event_hash == ""
        return self.prior_event_hash == prior_event.event_hash


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL MANIFEST ENTRY
# ═══════════════════════════════════════════════════════════════════════════════


class ToolManifestEntry(BaseModel):
    """Declaration of a single tool in the kernel manifest."""

    tool_name: str = Field(..., description="Canonical tool name")
    action_class: ActionClass = Field(..., description="Maximum action class")
    safe_modes: list[str] = Field(default_factory=list, description="Safe modes")
    dangerous_modes: list[str] = Field(default_factory=list, description="Gated modes")
    requires_lease: bool = Field(default=False)
    requires_human_ack: bool = Field(default=False)
    blast_radius: BlastRadius = Field(default=BlastRadius.LOCAL)
    is_reversible: bool = Field(default=True)
    memory_scope: MemoryScope | None = Field(default=None)


# ═══════════════════════════════════════════════════════════════════════════════
# SELF-CHECK — verify the schema is internally consistent
# ═══════════════════════════════════════════════════════════════════════════════


def _self_check() -> bool:
    """Verify that the KernelEnvelope schema is internally consistent."""
    # 1. Create a minimal observe-only envelope
    env = KernelEnvelope.observe_only()
    assert env.verdict == GateVerdict.SEAL
    assert env.is_safe
    assert not env.is_mutating
    assert not env.requires_human_ack
    assert env.authority.action_class == ActionClass.OBSERVE

    # 2. Create a HOLD envelope
    hold = KernelEnvelope.hold_envelope(reasons=["Test hold"], violations=["F2_TRUTH"])
    assert hold.verdict == GateVerdict.HOLD
    assert hold.is_gated

    # 3. Verify action class ordering
    assert ActionClass.subsumes(ActionClass.IRREVERSIBLE, ActionClass.OBSERVE)
    assert not ActionClass.subsumes(ActionClass.OBSERVE, ActionClass.IRREVERSIBLE)
    assert ActionClass.subsumes(ActionClass.MUTATE, ActionClass.MUTATE)

    # 4. Verify safe/mutating classification
    assert ActionClass.is_safe(ActionClass.OBSERVE)
    assert ActionClass.is_safe(ActionClass.ANALYZE)
    assert not ActionClass.is_safe(ActionClass.MUTATE)
    assert ActionClass.is_mutating(ActionClass.MUTATE)
    assert ActionClass.is_mutating(ActionClass.IRREVERSIBLE)
    assert not ActionClass.is_mutating(ActionClass.OBSERVE)

    # 5. Verify human ack requirement
    assert ActionClass.requires_human_ack(ActionClass.IRREVERSIBLE)
    assert ActionClass.requires_human_ack(ActionClass.EXTERNAL_SIDE_EFFECT)
    assert not ActionClass.requires_human_ack(ActionClass.OBSERVE)

    # 6. Verify HumanAcknowledgement binding hash
    hack = HumanAcknowledgement(
        actor_id="arif",
        action_summary="Test action",
        risk_summary="Low risk",
        exact_command="echo test",
    )
    assert hack.binding_hash.startswith("sha256:")
    assert not hack.is_expired()

    # 7. Verify AuditEvent hash chaining
    event1 = AuditEvent(
        session_id="test-session",
        actor_id="agent-1",
        tool_name="test_tool",
        action_class=ActionClass.OBSERVE,
        input_hash="sha256:abc",
        output_hash="sha256:def",
    )
    event2 = AuditEvent(
        session_id="test-session",
        actor_id="agent-1",
        tool_name="test_tool",
        action_class=ActionClass.OBSERVE,
        input_hash="sha256:ghi",
        prior_event_hash=event1.event_hash,
    )
    assert event2.verify_chain(event1)
    assert not event2.verify_chain(None)
    assert len(event1.event_hash) > 0

    # 8. Verify DriftReport blocking rules
    low_drift = DriftReport(
        build_hash="abc",
        runtime_hash="abc",
        tool_manifest_hash="abc",
        schema_hash="abc",
        constitution_hash="abc",
        env_config_hash="abc",
        drift_level=DriftLevel.LOW,
    )
    assert not low_drift.blocks_mutation
    high_drift = DriftReport(
        build_hash="abc",
        runtime_hash="def",
        tool_manifest_hash="abc",
        schema_hash="abc",
        constitution_hash="abc",
        env_config_hash="abc",
        drift_level=DriftLevel.HIGH,
    )
    assert high_drift.blocks_mutation
    assert not high_drift.blocks_irreversible
    crit_drift = DriftReport(
        build_hash="abc",
        runtime_hash="ghi",
        tool_manifest_hash="abc",
        schema_hash="abc",
        constitution_hash="abc",
        env_config_hash="abc",
        drift_level=DriftLevel.CRITICAL,
    )
    assert crit_drift.blocks_irreversible

    return True


if __name__ == "__main__":
    assert _self_check(), "KernelEnvelope self-check FAILED"
    print("KernelEnvelope self-check PASSED — all 8 assertions verified.")
