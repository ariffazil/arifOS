"""
Runtime Pydantic Models
══════════════════════════════════════════════════════════════════════════════════════

Single source of truth for all runtime type definitions.
DITEMPA BUKAN DIBERI.
"""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ═══════════════════════════════════════════════════════════════════════════════
# ENUMERATIONS
# ═══════════════════════════════════════════════════════════════════════════════


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
    SENSE = "111"
    FETCH = "222"
    MIND = "333"
    KERNEL = "444"
    REPLY = "444r"
    MEMORY = "555"
    HEART = "666"
    GATEWAY = "666g"
    OPS = "777"
    JUDGE = "888"
    FORGE = "010"
    VAULT = "999"


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
    SELF = "self"          # Self-judgment only
    LOCAL = "local"        # Tool-level
    SESSION = "session"    # Session-level
    GLOBAL = "global"      # System-wide


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

    verdict: Verdict | None = None
    status: RuntimeStatus = RuntimeStatus.SUCCESS
    authority: CanonicalAuthority | None = None

    allowed_next_tools: list[str] = Field(default_factory=list)
    transitions: list[dict[str, Any]] = Field(default_factory=list)
    operator_summary: dict[str, Any] = Field(default_factory=dict)
    state: dict[str, Any] = Field(default_factory=dict)
    handoff: dict[str, Any] = Field(default_factory=dict)
    payload: dict[str, Any] = Field(default_factory=dict)
    diagnostics: dict[str, Any] = Field(default_factory=dict)
    contract_version: str = "0.1.0"


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
