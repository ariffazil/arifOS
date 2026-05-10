"""
Runtime Pydantic Models
══════════════════════════════════════════════════════════════════════════════════════

Single source of truth for all runtime type definitions.
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field

# ═══════════════════════════════════════════════════════════════════════════════
# ENUMERATIONS
# ═══════════════════════════════════════════════════════════════════════════════


class ExecutionState(str, Enum):
    """Canonical execution pipeline states (formal state machine)."""

    OBSERVE = "OBSERVE"
    ANALYZE = "ANALYZE"
    SIMULATE = "SIMULATE"
    AWAIT_APPROVAL = "AWAIT_APPROVAL"
    EXECUTE = "EXECUTE"
    VERIFY = "VERIFY"
    SEAL = "SEAL"


class ClaimStatus(str, Enum):
    ANONYMOUS = "anonymous"
    CLAIMED = "claimed"
    VERIFIED = "verified"
    DENIED = "denied"


class AuthorityLevel(str, Enum):
    ANONYMOUS = "anonymous"
    OPERATOR = "operator"
    SOVEREIGN = "sovereign"
    GOVERNOR = "governor"
    AUDITOR = "auditor"
    ARIF = "arif"


class RuntimeStatus(str, Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"
    HOLD = "HOLD"
    DRY_RUN = "DRY_RUN"
    DEGRADED = "DEGRADED"
    SABAR = "SABAR"
    UNKNOWN = "UNKNOWN"


class Stage(str, Enum):
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


class ExecutionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    TIMEOUT = "TIMEOUT"
    DRY_RUN = "DRY_RUN"
    DEGRADED = "DEGRADED"


class GovernanceStatus(str, Enum):
    PAUSE = "PAUSE"
    ACTIVE = "ACTIVE"
    SEALED = "SEALED"
    OVERRIDE = "OVERRIDE"


class ContinuationStatus(str, Enum):
    READY = "READY"
    WAITING = "WAITING"
    TERMINATED = "TERMINATED"


class ArtifactStatus(str, Enum):
    NONE = "NONE"
    PENDING = "PENDING"
    READY = "READY"
    SEALED = "SEALED"
    FAILED = "FAILED"


class VerdictScope(str, Enum):
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


class Verdict(BaseModel):
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


class SacredStage(str, Enum):
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
    model_config = ConfigDict(populate_by_name=True)

    actor_id: str = "anonymous"
    level: AuthorityLevel = AuthorityLevel.ANONYMOUS
    claim_status: ClaimStatus = ClaimStatus.ANONYMOUS
    human_required: bool = False
    approval_scope: list[str] = Field(default_factory=list)
    auth_state: str = "unverified"


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

    verdict: Verdict | str | None = None
    status: RuntimeStatus = RuntimeStatus.SUCCESS
    authority: CanonicalAuthority | None = None

    allowed_next_tools: list[str] = Field(default_factory=list)
    transitions: list[dict[str, Any]] = Field(default_factory=list)
    operator_summary: dict[str, Any] = Field(default_factory=dict)
    state: dict[str, Any] = Field(default_factory=dict)
    handoff: dict[str, Any] = Field(default_factory=dict)
    payload: dict[str, Any] = Field(default_factory=dict)
    diagnostics: dict[str, Any] = Field(default_factory=dict)
    errors: list[CanonicalError] = Field(default_factory=list)
    contract_version: str = "0.1.0"


class VerdictCode(str, Enum):
    SEAL = "SEAL"
    SABAR = "SABAR"
    PARTIAL = "PARTIAL"
    VOID = "VOID"


class TelemetryMetrics(BaseModel):
    ds: float = 0.0
    confidence: float = 0.85
    G_star: float = 0.0


class TelemetryBasis(BaseModel):
    source: str | None = None
    mode: str | None = None


class TripleWitness(BaseModel):
    human: float = 0.0
    ai: float = 0.0
    earth: float = 0.0


class TelemetryVitals(BaseModel):
    metrics: TelemetryMetrics
    basis: TelemetryBasis = Field(default_factory=TelemetryBasis)
    witness: TripleWitness = Field(default_factory=TripleWitness)


class CanonicalMetrics(BaseModel):
    telemetry: TelemetryMetrics = Field(default_factory=TelemetryMetrics)


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
