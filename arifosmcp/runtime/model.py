"""
Runtime Pydantic Models
══════════════════════════════════════════════════════════════════════════════════════

Single source of truth for all runtime type definitions.
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field

# ═══════════════════════════════════════════════════════════════════════════════
# ENUMERATIONS
# ═══════════════════════════════════════════════════════════════════════════════


class ExecutionState(StrEnum):
    """Canonical execution pipeline states (formal state machine)."""

    OBSERVE = "OBSERVE"
    ANALYZE = "ANALYZE"
    SIMULATE = "SIMULATE"
    AWAIT_APPROVAL = "AWAIT_APPROVAL"
    EXECUTE = "EXECUTE"
    VERIFY = "VERIFY"
    SEAL = "SEAL"


class ActionRiskTier(StrEnum):
    """Constitutional risk classification for tool actions."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ── Backward-compatible alias ──────────────────────────────────────────


class ClaimStatus(StrEnum):
    ANONYMOUS = "anonymous"
    CLAIMED = "claimed"
    VERIFIED = "verified"
    DENIED = "denied"


class AuthorityLevel(StrEnum):
    ANONYMOUS = "anonymous"
    OPERATOR = "operator"
    SOVEREIGN = "sovereign"
    GOVERNOR = "governor"
    AUDITOR = "auditor"
    ARIF = "arif"


# RuntimeStatus is now canonical — imported from models/verdicts.
# Backward-compat alias for files importing Verdict from model (DEPRECATED — use models/verdicts directly)
from arifosmcp.models.verdicts import RuntimeStatus, Verdict

# Legacy local extensions (not in canonical RuntimeStatus):
LEGACY_RS_DRY_RUN = "DRY_RUN"  # Model-only: simulation/dry-run mode
LEGACY_RS_DEGRADED = "DEGRADED"  # Model-only: degraded capability
LEGACY_RS_UNKNOWN = "UNKNOWN"  # Model-only: uninitialized state
# Note: SABAR was removed — it is a governance Verdict, not a RuntimeStatus.
# Use Verdict.SABAR for governance holds, RuntimeStatus.SUCCESS for transport success.


class Stage(StrEnum):
    INIT = "000"
    INIT_000 = "000"
    SENSE = "111"
    SENSE_111 = "111"
    FETCH = "222"
    REALITY_222 = "222"
    MIND = "333"
    MIND_333 = "333"
    KERNEL = "444"
    ROUTER_444 = "444"
    REPLY = "444r"
    MEMORY = "555"
    MEMORY_555 = "555"
    HEART = "666"
    HEART_666 = "666"
    CRITIQUE_666 = "666c"
    GATEWAY = "666g"
    OPS = "777"
    FORGE_777 = "777"
    JUDGE = "888"
    JUDGE_888 = "888"
    FORGE = "010"
    VAULT = "999"
    VAULT_999 = "999"


class ExecutionStatus(StrEnum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    ERROR = "ERROR"  # Contract variant
    TIMEOUT = "TIMEOUT"
    DRY_RUN = "DRY_RUN"
    PARTIAL = "PARTIAL"  # Contract variant
    DEGRADED = "DEGRADED"


class GovernanceStatus(StrEnum):
    PAUSE = "PAUSE"
    ACTIVE = "ACTIVE"
    SEALED = "SEALED"
    OVERRIDE = "OVERRIDE"
    APPROVED = "APPROVED"  # Contract variant: maps from SEAL
    PARTIAL = "PARTIAL"  # Contract variant
    HOLD = "HOLD"  # Contract variant: awaiting human (L13)
    VOID = "VOID"  # Contract variant: forbidden/blocked
    PROVISIONAL = "PROVISIONAL"  # Contract variant


class ContinuationStatus(StrEnum):
    READY = "READY"
    WAITING = "WAITING"
    TERMINATED = "TERMINATED"
    HOLD = "HOLD"  # Contract variant
    BLOCKED = "BLOCKED"  # Contract variant
    CLARIFY_FIRST = "CLARIFY_FIRST"  # Contract variant


class ArtifactStatus(StrEnum):
    NONE = "NONE"
    PENDING = "PENDING"
    READY = "READY"
    SEALED = "SEALED"
    FAILED = "FAILED"
    USABLE = "USABLE"  # Contract variant: complete, can be used
    STAGED = "STAGED"  # Contract variant: prepared but not committed
    REJECTED = "REJECTED"  # Contract variant: failed validation
    EMPTY = "EMPTY"  # Contract variant: no output produced


class VerdictScope(StrEnum):
    """Scope of verdict authority."""

    SELF = "self"  # Self-judgment only
    LOCAL = "local"  # Tool-level
    SESSION = "session"  # Session-level
    GLOBAL = "global"  # System-wide


# ═══════════════════════════════════════════════════════════════════════════════
# PYDANTIC MODELS
# ═══════════════════════════════════════════════════════════════════════════════


class DeltaOmegaPsi(BaseModel):
    delta: float = Field(..., ge=0.0, le=1.0, description="Δ — Entropy reduction score.")
    omega: float = Field(..., ge=0.0, le=1.0, description="Ω — Human impact load.")
    psi: float = Field(..., ge=0.0, le=1.0, description="Ψ — Paradox score.")


class ToolRequest(BaseModel):
    tool: str
    params: dict[str, Any] = Field(default_factory=dict)
    session_id: str | None = None
    actor_id: str | None = None


class ToolResponse(BaseModel):
    tool: str
    status: str
    result: dict[str, Any] = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)
    omega_0: float = 0.0


class VerdictEnvelope(BaseModel):
    """Structured verdict envelope — NOT a governance verdict.

    This is a data container for verdict metadata (code, floor, reason).
    For the canonical governance verdict (SEAL/HOLD/SABAR/VOID), use:
        from arifosmcp.models.verdicts import Verdict
    """

    code: str
    floor: str | None = None
    reason: str = ""
    authorized_by: str | None = None
    SEAL: ClassVar[str] = "SEAL"
    PROVISIONAL: ClassVar[str] = "PROVISIONAL"
    ALIVE: ClassVar[str] = "ALIVE"
    SABAR: ClassVar[str] = "SABAR"
    PARTIAL: ClassVar[str] = "PARTIAL"
    HOLD: ClassVar[str] = "HOLD"
    HOLD_888: ClassVar[str] = "HOLD_888"
    DEGRADED: ClassVar[str] = "DEGRADED"
    VOID: ClassVar[str] = "VOID"


# Verdict = VerdictEnvelope REMOVED (2026-07-11 Phase 1: verdict unification)
# 20+ files imported Verdict from here and got VerdictEnvelope (Pydantic model) instead
# of the canonical SealType enum. Use: from arifosmcp.models.verdicts import Verdict
# VerdictEnvelope remains available for code that needs the Pydantic model directly.


class SacredStage(StrEnum):
    INIT_ANCHOR = "init_anchor"
    AGI_REASON = "agi_reason"
    AGI_REFLECT = "agi_reflect"
    ASI_SIMULATE = "asi_simulate"
    ASI_CRITIQUE = "asi_critique"
    AGI_ASI_FORGE = "agi_asi_forge"
    APEX_JUDGE = "apex_judge"
    VAULT_SEAL = "vault_seal"


class SessionState(BaseModel):
    session_id: str
    actor_id: str | None = None
    stage: str = "000"
    lane: str = "AGI"
    floors_ok: list[str] = Field(default_factory=list)
    floors_fail: list[str] = Field(default_factory=list)
    entropy_delta: float = 0.0
    sealed: bool = False


class CallerContext(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    actor_id: str = "anonymous"
    authority_level: AuthorityLevel = AuthorityLevel.ANONYMOUS
    claim_status: ClaimStatus = ClaimStatus.ANONYMOUS
    human_required: bool = False
    approval_scope: list[str] = Field(default_factory=list)
    auth_state: str = "unverified"


class CanonicalAuthority(BaseModel):
    """
    DEPRECATED 2026-07-12 — superseded by ``AuthorityState`` (see below; mirrors
    ``/schemas/authority-state.schema.json``).

    Retained for one compat cycle as a derived view. Do NOT write new fields here.
    Existing parallel legacy fields (``actor_verified``, ``identity_verified``,
    ``authority_level``, ``human_authority``, ``runtime_authority``) must derive
    from ``AuthorityState`` rather than be computed independently.

    Reference: ``forge_work/2026-07-12/KERNEL-INTELLIGENCE-HARDENING-CYCLE-PHASE-A.md``
    §1 (WS1, Phase B, step 1.2). Removal target: 2026-08-09 (one compat cycle).
    """

    model_config = ConfigDict(populate_by_name=True)

    actor_id: str = "anonymous"
    level: AuthorityLevel = AuthorityLevel.ANONYMOUS
    claim_status: ClaimStatus = ClaimStatus.ANONYMOUS
    human_required: bool = False
    approval_scope: list[str] = Field(default_factory=list)
    auth_state: str = "unverified"


# ═══════════════════════════════════════════════════════════════════════════════
# AUTHORITY STATE — WS1 (KERNEL HARDENING CYCLE PHASE A)
# ═══════════════════════════════════════════════════════════════════════════════
# Single source of truth for "who is acting and what may they do."
# Replaces parallel legacy fields: actor_verified, identity_verified,
# authority_level, human_authority, runtime_authority.
# Schema mirror: /root/arifOS/schemas/authority-state.schema.json
# Forged 2026-07-12 under F13 SOVEREIGN directive.
# ═══════════════════════════════════════════════════════════════════════════════


class AuthorityActor(BaseModel):
    """Identity layer of an ``AuthorityState`` snapshot (WS1 spec §1.1)."""

    claimed_id: str = "anonymous"
    verified: bool = False
    # P0 FIX 2026-09-04 (FI-008, F13 "auto go"): canonical key fingerprint
    # ("ed25519:sha256:<hex16>") of the public key that VERIFIED the actor's
    # signature. bind_authority_state matches this against SOVEREIGN_KEY_IDS
    # (SECURITY P0 2026-07-12). Without it, verified=True alone only ever
    # reaches OPERATOR/OBSERVER_MUTATE — the LIMITED_MUTATE bug.
    verified_key_id: str | None = None
    verification_method: Literal[
        "none", "session", "signature", "oauth", "hardware", "f13_sovereign",
        # T3 grant 2026-08-07 by 888 SOVEREIGN: DPoP proof + DID registry match.
        # Cryptographically strong: Ed25519 signature over nonce+method+url+ath,
        # bound to a registered DID via JWK thumbprint.
        "dpop+registry",
    ] = "none"


class AuthoritySeals(BaseModel):
    """Namespaced seal states (WS1 spec §1.1). Each is independent."""

    kernel_seal_awareness: Literal["ACTIVE", "INACTIVE", "STALE"] = "INACTIVE"
    domain_seal_validity: Literal["ACTIVE", "INACTIVE", "STALE"] = "INACTIVE"
    judge_seal_authorization: Literal["ACTIVE", "INACTIVE", "STALE", "REVOKED"] = "INACTIVE"
    vault999_seal_record: Literal["ACTIVE", "INACTIVE", "STALE"] = "INACTIVE"
    public_seal_readiness: Literal["ACTIVE", "INACTIVE", "STALE"] = "INACTIVE"


class AuthorityForgeGate(BaseModel):
    """The state of the A-FORGE gate (WS1 spec §1.1). ``enabled=false`` means
    A-FORGE is disabled regardless of any other signal."""

    enabled: bool = False
    reversibility_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    blockers: list[str] = Field(default_factory=list)


class AuthorityPublicPosture(BaseModel):
    """Receipt-bound public view. ``service_health`` (liveness) is deliberately
    separated from ``execution_readiness`` (gate state)."""

    service_health: Literal["green", "yellow", "red", "unknown"] = "unknown"
    execution_readiness: Literal["ready", "held", "void", "unknown"] = "unknown"
    human_visible_summary: str | None = None


class AuthorityState(BaseModel):
    """
    Canonical authority posture — single source of truth for "who is acting and
    what may they do." Mirrors
    ``/root/arifOS/schemas/authority-state.schema.json`` (WS1 spec §1.1).

    Forged 2026-07-12 under F13 SOVEREIGN directive.

    Replaces the legacy parallel-write pattern where ``actor_verified``,
    ``identity_verified``, ``authority_level``, ``human_authority``, and
    ``runtime_authority`` were each computed by independent code paths and
    could disagree (the ``MEDIUM-vs-OBSERVE_ONLY`` split documented in
    ``KERNEL-INTELLIGENCE-HARDENING-CYCLE-PHASE-A.md`` §1.1).

    Acceptance: every ``arif_init`` response must carry exactly one
    ``AuthorityState`` instance. Legacy fields may be derived from it for one
    compat cycle only — never computed independently.
    """

    model_config = ConfigDict(populate_by_name=True)

    state_id: str = Field(
        default="as_pending",
        pattern=r"^as(_pending|_[0-9]{4}_[0-9]{2}_[0-9]{2}_[0-9]{6})$",
        description="Globally unique authority-state identifier (date-based).",
    )
    snapshot_at: str = Field(
        default="1970-01-01T00:00:00Z",
        description="When this state was captured (ISO 8601 UTC).",
    )
    actor: AuthorityActor = Field(default_factory=AuthorityActor)
    context_verdict: Literal["STABLE", "DEGRADED_CONTEXT", "UNKNOWN"] = "UNKNOWN"
    seals: AuthoritySeals = Field(default_factory=AuthoritySeals)
    execution_authority: Literal["HOLD", "SEAL_AUTHORIZED", "VOID"] = "HOLD"
    apex_approval: Literal["ABSENT", "PRESENT", "REJECTED"] = "ABSENT"
    active_holds: list[str] = Field(default_factory=list)
    active_missions: list[str] = Field(default_factory=list)
    forge_gate: AuthorityForgeGate = Field(default_factory=AuthorityForgeGate)
    public_posture: AuthorityPublicPosture = Field(default_factory=AuthorityPublicPosture)
    non_overclaim_check: Literal["passed", "failed"] = "failed"

    def is_sealed(self) -> bool:
        """Top-level verdict for downstream actuators: any unauthorized mutation
        must check this before acting."""
        return self.execution_authority == "SEAL_AUTHORIZED"

    def is_held(self) -> bool:
        return self.execution_authority == "HOLD" or len(self.active_holds) > 0


class IdentityContext(BaseModel):
    actor_id: str = "anonymous"
    authority_level: AuthorityLevel = AuthorityLevel.ANONYMOUS
    session_id: str | None = None
    intent: str | None = None
    seals: list[str] = Field(default_factory=list)


class ContinuityState(BaseModel):
    contract_version: str = "0.1.0"
    continuity_version: int = 0
    previous_tool: str | None = None
    current_tool: str | None = None
    max_risk_tier: str = "low"


class Artifact(BaseModel):
    artifact_id: str | None = None
    artifact_type: str | None = None
    content: Any = None
    sealed: bool = False


class CanonicalError(BaseModel):
    code: str
    message: str
    stage: str | None = None


class PNSSignal(BaseModel):
    source: str
    status: str | None = None
    score: float | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class PNSContext(BaseModel):
    shield: PNSSignal | None = None
    search: PNSSignal | None = None
    vision: PNSSignal | None = None
    health: PNSSignal | None = None


class TelemetryMetrics(BaseModel):
    ds: float = 0.0
    confidence: float = 0.85
    G_star: float = 0.0
    peace2: float = 1.0
    omega_ortho: float = 1.0
    shadow: float = 0.0
    kappa_r: float | None = None
    echo_debt: float = 0.1
    psi_le: float = 0.0
    verdict: str = "ALIVE"


class TelemetryBasis(BaseModel):
    source: str | None = None
    mode: str | None = None


class TripleWitness(BaseModel):
    human: float = 0.0
    ai: float = 0.0
    earth: float = 0.0


class CanonicalMetrics(BaseModel):
    telemetry: TelemetryMetrics = Field(default_factory=TelemetryMetrics)
    witness: TripleWitness = Field(default_factory=TripleWitness)
    basis: TelemetryBasis = Field(default_factory=TelemetryBasis)


class RuntimeEnvelope(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    ok: bool = True
    tool: str
    version: str = "2.0.0"

    execution_status: ExecutionStatus = ExecutionStatus.SUCCESS
    governance_status: GovernanceStatus = GovernanceStatus.PAUSE
    continuation_status: ContinuationStatus = ContinuationStatus.READY

    primary_artifact: Artifact | None = None
    artifact_state: ArtifactStatus = ArtifactStatus.NONE

    identity: IdentityContext | None = None
    continuity: ContinuityState | None = None

    canonical_tool_name: str | None = None
    risk_class: str = "LOW"
    requires_auth: bool = False
    requires_human: bool = False
    recoverable: bool = True
    next_action: dict[str, Any] | None = None

    stage: str | None = "000"
    lane: str = "AGI"
    session_id: str | None = None
    actor_id: str | None = None
    # Patched 2026-07-14 (FEDERATION-ALIGN audit Step 3): was missing,
    # causing RuntimeEnvelope "object has no field platform_context"
    # when __main__.py:160 set result.platform_context = "stdio" and
    # output_formatter.py:63,471 read envelope.platform_context.
    platform_context: str | None = None

    verdict: Verdict | str | None = None
    status: RuntimeStatus = RuntimeStatus.SUCCESS
    authority: CanonicalAuthority | None = None

    # ── Spine P0: SCT continuity echo ───────────────────────────────────────
    # authority is reserved for CanonicalAuthority; authority_band holds the
    # string band from resolved SCT standing to avoid type collision.
    session_token: str | None = None
    standing_source: str | None = None
    apex_scalars: dict[str, Any] | None = None
    authority_band: str | None = None
    actor_verified: bool | None = None
    authority_delta: dict[str, Any] | None = None

    allowed_next_tools: list[str] = Field(default_factory=list)
    transitions: list[dict[str, Any]] = Field(default_factory=list)
    operator_summary: dict[str, Any] = Field(default_factory=dict)
    state: dict[str, Any] = Field(default_factory=dict)
    handoff: dict[str, Any] = Field(default_factory=dict)
    payload: dict[str, Any] = Field(default_factory=dict)
    diagnostics: dict[str, Any] = Field(default_factory=dict)
    errors: list[CanonicalError] = Field(default_factory=list)
    contract_version: str = "0.1.0"

    # Metabolic Attributes (DITEMPA)
    metrics: CanonicalMetrics = Field(default_factory=CanonicalMetrics)
    detail: str | None = None
    hint: str | None = None

    def to_dict(self, compact: bool = False) -> dict[str, Any]:
        """Convert to dict, optionally removing empty fields."""
        data = self.model_dump(mode="json")
        if compact:
            return {k: v for k, v in data.items() if v not in (None, [], {})}
        return data


from arifosmcp.models.verdicts import Verdict as VerdictCode

# VerdictCode is now canonical Verdict — imported from models/verdicts.
# PARTIAL is not a governance verdict. Use VerdictState.SABAR_EPISTEMIC
# for partial qualification, or RuntimeStatus for transport partial status.
LEGACY_VC_PARTIAL = VerdictCode.SABAR  # Best mapping: SABAR as "partial proceed"


class PhilosophyState(BaseModel):
    confidence_cap: float = 1.0
    posture: str = "SEAL"


class ArifOSError(BaseModel):
    code: str
    message: str
    type: str | None = None
    source: str | None = None
    stage: str | None = None
    recoverable: bool = True
    required_next_tool: str | None = None
    required_fields: list[str] | None = None
    example_next_call: dict[str, Any] | None = None
    remediation: dict[str, Any] | None = None
