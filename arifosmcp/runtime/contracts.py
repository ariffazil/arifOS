"""
arifOS MCP Context Contracts
═══════════════════════════════════════════════════════════════════════════════

Shared JSON schemas for tools, resources, and prompts.
These contracts ensure type safety and consistency across the MCP surface.

Aligned with SPEC.md: Functional naming, canonical fields, and strict typing.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field as dataclass_field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

# ═══════════════════════════════════════════════════════════════════════════════
# ENUMERATIONS
# ═══════════════════════════════════════════════════════════════════════════════

class VerdictCode(str, Enum):
    """Canonical constitutional verdict codes."""
    SEAL = "SEAL"       # Approved, attested
    PARTIAL = "PARTIAL" # Approved with reservations
    VOID = "VOID"       # Rejected, failed floors
    SABAR = "SABAR"     # Pending, needs more info
    HOLD = "888_HOLD"   # High-risk, requires human


class RiskTier(str, Enum):
    """Risk classification tiers."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @classmethod
    def _missing_(cls, value: object) -> RiskTier | None:
        if isinstance(value, str) and value.lower() == "sovereign":
            return cls.CRITICAL
        return None


class SessionState(str, Enum):
    """Session lifecycle states."""
    ANONYMOUS = "anonymous"
    CLAIMED = "claimed"
    ANCHORED = "anchored"
    VERIFIED = "verified"
    SCOPED = "scoped"
    APPROVED = "approved"


class TrinityAspect(str, Enum):
    """The three governing principles."""
    PSI = "PSI"      # Will, identity, sovereignty
    DELTA = "DELTA"  # Change, reason, action
    OMEGA = "OMEGA"  # End state, empathy, memory


# ═══════════════════════════════════════════════════════════════════════════════
# IDENTITY CONTRACTS
# ═══════════════════════════════════════════════════════════════════════════════

class SessionAnchor(BaseModel):
    """
    SessionAnchor — Established by init_session_anchor.
    Used by: init_session_anchor, session resources, prompts.
    """
    session_id: str = Field(..., description="Unique session identifier (UUID)")
    actor_id: str = Field(..., description="Human sovereign or agent identity")
    declared_name: str | None = Field(None, description="Optional display name")
    intent: str | None = Field(None, description="Session purpose statement")
    token: str | None = Field(None, description="Short-lived session token")
    created_at: str | None = Field(None, description="ISO 8601 creation time")
    expires_at: str | None = Field(None, description="ISO 8601 expiration time")
    epoch: str = Field(default="2026-04-06", description="Governance epoch")
    state: SessionState = Field(default=SessionState.ANONYMOUS)


class ToolAuthContext(BaseModel):
    """
    ToolAuthContext — Restricted tool authorization.
    Used by: restricted tools (memory, vault, VPS execution).
    """
    session_id: str = Field(..., description="Bound session ID")
    token: str = Field(..., description="Session token")
    actor_id: str = Field(..., description="Verified actor identity")
    access_class: Literal["public", "authenticated", "sovereign"] = Field(default="authenticated")
    scopes: list[str] = Field(default_factory=list, description="Granted capability scopes")
    human_approval_persisted: bool = Field(default=False, description="F13 human override")


# ═══════════════════════════════════════════════════════════════════════════════
# TELEMETRY CONTRACTS
# ═══════════════════════════════════════════════════════════════════════════════

class WitnessTriple(BaseModel):
    """
    The three-witness attestation model.
    """
    human: float = Field(default=1.0, ge=0.0, le=1.0)
    ai: float = Field(default=0.0, ge=0.0, le=1.0)
    earth: float = Field(default=0.0, ge=0.0, le=1.0)


class TelemetryEnvelope(BaseModel):
    """
    TelemetryEnvelope — Standard telemetry packet for all arifOS operations.
    """
    session_id: str = Field(..., description="Source session")
    epoch: str = Field(default="2026-04-06", description="Governance epoch")
    timestamp: str | None = Field(None, description="ISO 8601 timestamp")
    
    # Six canonical constitutional metrics
    tau_truth: float = Field(default=0.95, ge=0.0, le=1.0, description="F2: Truth alignment")
    omega_0: float = Field(default=0.05, ge=0.0, description="F7: Humility level")
    delta_s: float = Field(default=0.0, description="F4: Entropy delta")
    peace2: float = Field(default=1.0, ge=0.0, description="F5: Peace² factor")
    kappa_r: float = Field(default=0.9, ge=0.0, le=1.0, description="F6: Empathy/Care level")
    tri_witness: float = Field(default=0.0, ge=0.0, le=1.0, description="F3: Witness coherence")
    
    # Derived
    psi_le: float | None = Field(None, description="Ψ Life-Energy index")
    verdict_hint: VerdictCode | None = Field(None, description="Indicative verdict")


class ConstitutionalHealthView(BaseModel):
    """
    ConstitutionalHealthView — Dashboard view.
    Used by: ChatGPT render path and widget.
    """
    session_id: str
    status: str = Field(..., description="HEALTHY, DEGRADED, CRITICAL, or VOID")
    floors_active: int = Field(default=13, ge=0, le=13)
    telemetry: TelemetryEnvelope | None = None
    recent_verdicts: list[Any] = Field(default_factory=list)
    widget_uri: str | None = Field(None, description="Widget render URI")


# ═══════════════════════════════════════════════════════════════════════════════
# VERDICT CONTRACTS
# ═══════════════════════════════════════════════════════════════════════════════

class VerdictRecord(BaseModel):
    """
    VerdictRecord — Immutable vault record for constitutional decisions.
    """
    record_id: str = Field(..., description="Unique record identifier")
    session_id: str = Field(..., description="Source session")
    timestamp: str = Field(..., description="ISO 8601 seal time")
    verdict: VerdictCode
    candidate_action: str = Field(..., description="What was evaluated")
    risk_tier: RiskTier
    floors_checked: list[str] = Field(default_factory=list)
    floors_failed: list[str] = Field(default_factory=list)
    telemetry_at_verdict: TelemetryEnvelope
    bls_aggregate_signature: str | None = Field(None, description="BLS12-381 hex signature")
    seal_status: str = Field(default="PENDING")


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL INPUT CONTRACTS
# ═══════════════════════════════════════════════════════════════════════════════

class InitSessionAnchorInput(BaseModel):
    actor_id: str = Field(..., description="Identity claim (human or agent)")
    intent: str = Field(..., description="Session purpose statement")
    declared_name: str | None = Field(None, description="Optional display name")


class JudgeVerdictInput(BaseModel):
    candidate_action: str = Field(..., description="The action to evaluate")
    risk_tier: RiskTier = Field(default=RiskTier.MEDIUM)
    telemetry: TelemetryEnvelope | None = None


class SenseRealityInput(BaseModel):
    query: str = Field(..., description="What to verify in physical reality")
    operation: Literal["search", "ingest", "compass", "atlas", "time"] = Field(default="search")


class ReasonSynthesisInput(BaseModel):
    query: str = Field(..., description="Reasoning task or synthesis target")
    context: str | None = Field(None, description="Additional context or evidence")


class CritiqueSafetyInput(BaseModel):
    content: str = Field(..., description="Content or proposal to critique")
    mode: Literal["critique", "simulate"] = Field(default="critique")


class LoadMemoryContextInput(BaseModel):
    query: str = Field(..., description="Memory search query")
    project_id: str = Field(default="default")


class EstimateOpsInput(BaseModel):
    action_description: str = Field(..., description="Planned action to estimate")


class RouteExecutionInput(BaseModel):
    query: str = Field(..., description="User request to route")


# ═══════════════════════════════════════════════════════════════════════════════
# BACKWARD COMPATIBILITY MAPPINGS
# ═══════════════════════════════════════════════════════════════════════════════

AAA_CANONICAL_TOOLS = [
    "init_session_anchor",
    "get_tool_registry",
    "sense_reality",
    "reason_synthesis",
    "critique_safety",
    "route_execution",
    "load_memory_context",
    "estimate_ops",
    "judge_verdict",
    "record_vault_entry",
    "execute_vps_task",
]

AAA_PUBLIC_TOOLS = [
    "arifos_init",
    "arifos_sense",
    "arifos_mind",
    "arifos_kernel",
    "arifos_heart",
    "arifos_ops",
    "arifos_judge",
    "arifos_memory",
    "arifos_vault",
    "arifos_forge",
    "arifos_gateway",
]

AAA_TOOL_ALIASES = {
    "init_anchor": "arifos.init",
    "arifos_kernel": "arifos.kernel",
    "arifos_route": "arifos.kernel",
    "apex_soul": "arifos.judge",
    "apex_judge": "arifos.judge",
    "vault_ledger": "arifos.vault",
    "agi_mind": "arifos.mind",
    "asi_heart": "arifos.heart",
    "engineering_memory": "arifos.memory",
    "physics_reality": "arifos.sense",
    "math_estimator": "arifos.ops",
    "architect_registry": "arifos.init",  # Merged into init
    # v2 underscored aliases
    "arifos_init": "arifos_init",
    "arifos_kernel": "arifos_kernel",
    "arifos_route": "arifos_kernel",
    "arifos_sense": "arifos_sense",
    "arifos_mind": "arifos_mind",
    "arifos_heart": "arifos_heart",
    "arifos_ops": "arifos_ops",
    "arifos_judge": "arifos_judge",
    "arifos_memory": "arifos_memory",
    "arifos_vault": "arifos_vault",
    "arifos_forge": "arifos_forge",
    "arifos_gateway": "arifos_gateway",
    "arifos_health": "arifos_health",
}

AAA_TOOL_STAGE_MAP = {
    "init_session_anchor": "000_INIT",
    "get_tool_registry": "M-4_ARCH",
    "sense_reality": "111_SENSE",
    "reason_synthesis": "333_MIND",
    "critique_safety": "666_HEART",
    "route_execution": "444_ROUTER",
    "load_memory_context": "555_MEMORY",
    "estimate_ops": "444_ROUTER",
    "judge_verdict": "888_JUDGE",
    "record_vault_entry": "999_VAULT",
    "execute_vps_task": "M-3_EXEC",
    # v2 underscored names
    "arifos_init": "000_INIT",
    "arifos_sense": "111_SENSE",
    "arifos_mind": "333_MIND",
    "arifos_kernel": "444_ROUTER",
    "arifos_heart": "666_HEART",
    "arifos_ops": "777_OPS",
    "arifos_judge": "888_JUDGE",
    "arifos_memory": "555_MEMORY",
    "arifos_vault": "999_VAULT",
    "arifos_forge": "010_FORGE",
    "arifos_gateway": "888_OMEGA",
    "arifos_health": "111_SENSE",
}

TRINITY_BY_TOOL = {
    "init_session_anchor": "PSI Ψ",
    "get_tool_registry": "DELTA Δ",
    "sense_reality": "DELTA Δ",
    "reason_synthesis": "DELTA Δ",
    "critique_safety": "OMEGA Ω",
    "route_execution": "DELTA/PSI",
    "load_memory_context": "OMEGA Ω",
    "estimate_ops": "DELTA Δ",
    "judge_verdict": "PSI Ψ",
    "record_vault_entry": "PSI Ψ",
    "execute_vps_task": "ALL",
    # v2 underscored names
    "arifos_init": "PSI Ψ",
    "arifos_sense": "DELTA Δ",
    "arifos_mind": "DELTA Δ",
    "arifos_kernel": "DELTA/PSI",
    "arifos_heart": "OMEGA Ω",
    "arifos_ops": "DELTA Δ",
    "arifos_judge": "PSI Ψ",
    "arifos_memory": "OMEGA Ω",
    "arifos_vault": "PSI Ψ",
    "arifos_forge": "DELTA Δ",
    "arifos_gateway": "OMEGA Ω",
    "arifos_health": "DELTA Δ",
}

AAA_TOOL_LAW_BINDINGS = {
    "init_session_anchor": ["F11", "F12", "F13"],
    "get_tool_registry": ["F10", "F11"],
    "sense_reality": ["F2", "F3", "F10"],
    "reason_synthesis": ["F2", "F4", "F7", "F8"],
    "critique_safety": ["F5", "F6", "F9"],
    "route_execution": ["F4", "F11"],
    "load_memory_context": ["F2", "F10", "F11"],
    "estimate_ops": ["F4", "F5"],
    "judge_verdict": ["F1", "F2", "F3", "F9", "F10", "F12", "F13"],
    "record_vault_entry": ["F1", "F13"],
    "execute_vps_task": ["F1", "F2", "F7", "F13"],
    # v2 underscored names
    "arifos_init": ["F11", "F12", "F13"],
    "arifos_sense": ["F2", "F3", "F4", "F10"],
    "arifos_mind": ["F2", "F4", "F7", "F8"],
    "arifos_kernel": ["F4", "F11"],
    "arifos_heart": ["F5", "F6", "F9"],
    "arifos_ops": ["F4", "F5"],
    "arifos_judge": ["F1", "F2", "F3", "F9", "F10", "F12", "F13"],
    "arifos_memory": ["F2", "F10", "F11"],
    "arifos_vault": ["F1", "F13"],
    "arifos_forge": ["F1", "F2", "F7", "F13"],
    "arifos_gateway": ["F3", "F4", "F9", "F11", "F13"],
    "arifos_health": ["F4", "F12"],
}

# Executable contract metadata
DOMAIN_PAYLOAD_GATES = {
    "arifos_init": {"required": ["actor_id", "intent"]},
    "arifos_sense": {"required": ["query"]},
    "arifos_mind": {"required": ["query"]},
    "arifos_kernel": {"required": ["query"]},
    "arifos_heart": {"required": ["query"]},
    "arifos_ops": {"required": ["query"]},
    "arifos_judge": {"required": ["query", "risk_tier"]},
    "arifos_memory": {"required": ["query"]},
    "arifos_vault": {"required": ["verdict"]},
    "arifos_forge": {"required": ["action", "payload", "session_id", "judge_verdict", "judge_g_star", "judge_state_hash"]},
    "arifos_gateway": {"required": ["session_id"]},
    "arifos_health": {"required": []},
}
LAW_13_CATALOG = {
    "F1": "Reversibility before irreversible action",
    "F2": "Truth over fabrication",
    "F3": "Tri-witness grounding",
    "F4": "Entropy discipline",
    "F5": "Safety and stability",
    "F6": "Care and dignity",
    "F7": "Humility under uncertainty",
    "F8": "Governance integrity",
    "F9": "Anti-deception / anti-hantu",
    "F10": "Boundary integrity",
    "F11": "Audit continuity",
    "F12": "Injection defense",
    "F13": "Sovereign ratification",
}
READ_ONLY_TOOLS = ["arifos_sense", "arifos_mind", "arifos_kernel", "arifos_ops", "arifos_gateway", "arifos_health"]
REQUIRES_SESSION = [
    "arifos_sense",
    "arifos_mind",
    "arifos_kernel",
    "arifos_heart",
    "arifos_ops",
    "arifos_judge",
    "arifos_memory",
    "arifos_vault",
    "arifos_forge",
    "arifos_gateway",
    "arifos_health",
]
TOOL_MODES = {
    "arifos_init": {"init", "refresh", "state", "status", "probe", "revoke"},
    "arifos_sense": {"governed", "search", "ingest", "compass", "atlas", "time"},
    "arifos_mind": {"reason", "sequential", "step", "branch", "merge", "review", "reflect"},
    "arifos_kernel": {"kernel", "status"},
    "arifos_heart": {"critique", "simulate"},
    "arifos_ops": {"cost", "health", "vitals", "entropy"},
    "arifos_judge": {"judge"},
    "arifos_memory": {"vector_query", "vector_store", "engineer", "query"},
    "arifos_vault": {"seal"},
    "arifos_forge": {"execute"},
    "arifos_gateway": {"guard", "audit", "correlate"},
    "arifos_health": {"health"},
}

# Runtime helper contracts
class ToolStatus(str, Enum):
    OK = "OK"
    WARNING = "WARNING"
    HOLD = "HOLD"
    SABAR = "SABAR"
    ERROR = "ERROR"
    VOID = "VOID"


OutputPolicy = Literal["redact", "mask", "raw"]
VerdictScope = Literal["session", "global", "resource"]


class HumanDecisionMarker(str, Enum):
    MACHINE_RECOMMENDATION_ONLY = "machine_recommendation_only"
    HUMAN_APPROVAL_BOUND = "human_approval_bound"
    HUMAN_CONFIRMATION_REQUIRED = "human_confirmation_required"
    ESCALATED = "escalated"
    SEALED = "sealed"


class SessionClass(str, Enum):
    OBSERVE = "observe"
    ADVISE = "advise"
    EXECUTE = "execute"
    SOVEREIGN = "sovereign"
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"


@dataclass
class TraceContext:
    stage: str
    session_id: str
    trace_id: str = dataclass_field(default_factory=lambda: f"trace-{uuid4().hex[:12]}")
    parent_trace_id: str | None = None
    policy_version: str = "v2026.04"
    timestamp: str = dataclass_field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def stage_id(self) -> str:
        return self.stage


@dataclass
class EntropyBudget:
    ambiguity_score: float = 0.0
    delta_s: float = 0.0
    confidence: float = 1.0
    assumptions: list[str] = dataclass_field(default_factory=list)
    blast_radius: str = "minimal"
    contradictions: int = 0

    @property
    def is_stable(self) -> bool:
        return self.delta_s <= 0.0 and self.confidence >= 0.6

    @property
    def assumptions_made(self) -> list[str]:
        return self.assumptions

    @property
    def blast_radius_estimate(self) -> str:
        return self.blast_radius


class ToolEnvelope(BaseModel):
    status: ToolStatus
    tool: str
    session_id: str
    risk_tier: RiskTier = RiskTier.MEDIUM
    confidence: float = 1.0
    trace: TraceContext | None = None
    entropy: EntropyBudget | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    authority: Any = None
    caller_state: str | None = None
    auth_context: dict[str, Any] | None = None
    allowed_next_tools: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")

    @property
    def inputs_hash(self) -> str:
        payload = {
            "tool": self.tool,
            "session_id": self.session_id,
            "risk_tier": self.risk_tier.value if isinstance(self.risk_tier, Enum) else self.risk_tier,
        }
        return f"sha256:{hash(str(payload)) & 0xffffffff:08x}"

    @property
    def outputs_hash(self) -> str:
        return f"sha256:{hash(str(self.payload)) & 0xffffffff:08x}"

    @property
    def human_decision(self) -> HumanDecisionMarker:
        explicit = self.__pydantic_extra__.get("human_decision") if self.__pydantic_extra__ else None
        if explicit is not None:
            return explicit
        if self.status in {ToolStatus.HOLD, ToolStatus.VOID}:
            return HumanDecisionMarker.HUMAN_CONFIRMATION_REQUIRED
        if self.risk_tier in {RiskTier.HIGH, RiskTier.CRITICAL}:
            return HumanDecisionMarker.HUMAN_APPROVAL_BOUND
        return HumanDecisionMarker.MACHINE_RECOMMENDATION_ONLY

    @property
    def requires_human(self) -> bool:
        return self.human_decision in {
            HumanDecisionMarker.HUMAN_APPROVAL_BOUND,
            HumanDecisionMarker.HUMAN_CONFIRMATION_REQUIRED,
            HumanDecisionMarker.ESCALATED,
        }


@dataclass
class ValidationResult:
    valid: bool
    reason: str = ""
    stage: str = "FAIL_CLOSED"

    def to_envelope(
        self,
        tool: str,
        session_id: str,
        trace: TraceContext | None = None,
    ) -> ToolEnvelope:
        return ToolEnvelope(
            status=ToolStatus.ERROR,
            tool=tool,
            session_id=session_id,
            trace=trace,
            confidence=0.0,
            payload={"error": self.reason, "valid": self.valid},
        )

# Utils
def make_telemetry_seed(session_id: str) -> TelemetryEnvelope:
    """Generate a fresh telemetry seed."""
    from datetime import datetime, timezone
    return TelemetryEnvelope(
        session_id=session_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        tau_truth=1.0,
        omega_0=0.05,
        delta_s=0.0,
        peace2=1.0,
        kappa_r=0.9,
        tri_witness=0.0,
        verdict_hint=VerdictCode.SABAR
    )


def compute_psi_le(telemetry: TelemetryEnvelope) -> float:
    """Compute life-energy index."""
    import math
    truth = telemetry.tau_truth
    entropy = 1 - abs(telemetry.delta_s)
    peace = min(telemetry.peace2 / 2.0, 1.0)
    witness = telemetry.tri_witness if telemetry.tri_witness > 0 else 0.5
    psi = math.pow(truth * entropy * peace * witness, 0.25)
    return round(psi + 1.0, 3)


def calculate_entropy_budget(
    ambiguity_score: float = 0.0,
    delta_s: float | None = None,
    confidence: float = 1.0,
    assumptions: list[str] | None = None,
    blast_radius: str = "minimal",
    *args: Any,
    **kwargs: Any,
) -> EntropyBudget:
    if not isinstance(assumptions, list):
        assumptions = []
    if isinstance(confidence, (int, float)) and confidence > 1.0:
        confidence = max(0.1, min(1.0, 1.0 - float(ambiguity_score)))
    elif confidence is None:
        confidence = max(0.1, min(1.0, 1.0 - float(ambiguity_score)))
    elif kwargs.get("confidence") is None and float(confidence) == 1.0:
        confidence = max(0.1, min(1.0, 1.0 - float(ambiguity_score)))
    if delta_s is None:
        delta_s = kwargs.get("delta_s")
    if delta_s is None:
        delta_s = max(-1.0, min(1.0, float(ambiguity_score) - float(confidence)))
    assumptions = list(assumptions or kwargs.get("assumptions") or [])
    blast_radius = str(kwargs.get("blast_radius", blast_radius))
    return EntropyBudget(
        ambiguity_score=float(ambiguity_score),
        delta_s=float(delta_s),
        confidence=float(confidence),
        assumptions=assumptions,
        blast_radius=blast_radius,
        contradictions=int(kwargs.get("contradictions", 0)),
    )


def check_domain_gate(tool_name: str, payload: dict[str, Any] | None = None) -> bool:
    gate = DOMAIN_PAYLOAD_GATES.get(tool_name, {})
    required = gate.get("required", [])
    payload = payload or {}
    return all(key in payload for key in required)


def determine_human_marker(risk_tier: RiskTier | str, human_approval: bool = False) -> str | None:
    tier = risk_tier.value if isinstance(risk_tier, RiskTier) else str(risk_tier).lower()
    if human_approval:
        return "HUMAN_APPROVED"
    if tier in {"high", "critical"}:
        return "HUMAN_REQUIRED"
    return None


def generate_trace_context(stage: str, session_id: str, parent_trace_id: str | None = None) -> TraceContext:
    return TraceContext(
        stage=stage,
        session_id=session_id,
        parent_trace_id=parent_trace_id or stage,
    )


def public_tool_input_contracts() -> dict[str, Any]:
    from arifosmcp.runtime.tool_specs import PUBLIC_TOOL_SPECS

    contracts: dict[str, Any] = {}
    for spec in PUBLIC_TOOL_SPECS:
        contracts[spec.name] = spec.input_schema
    return contracts


def require_session(fn):
    return fn


def validate_fail_closed(*args: Any, **kwargs: Any) -> ValidationResult:
    tool = str(kwargs.get("tool", "unknown"))
    risk_tier = kwargs.get("risk_tier", RiskTier.MEDIUM)
    try:
        RiskTier(risk_tier.lower() if isinstance(risk_tier, str) else risk_tier.value)
    except Exception:
        return ValidationResult(valid=False, reason=f"Invalid risk_tier for {tool}")
    return ValidationResult(valid=True)


def verify_contract(*args: Any, **kwargs: Any) -> dict[str, Any]:
    public_tools = set(AAA_PUBLIC_TOOLS)
    checks = {
        "stage_map_complete": public_tools.issubset(AAA_TOOL_STAGE_MAP.keys()),
        "trinity_map_complete": public_tools.issubset(TRINITY_BY_TOOL.keys()),
        "law_bindings_complete": public_tools.issubset(AAA_TOOL_LAW_BINDINGS.keys()),
        "tool_modes_complete": public_tools.issubset(TOOL_MODES.keys()),
        "session_requirements_cover_public_non_init": public_tools.difference({"arifos_init"}).issubset(REQUIRES_SESSION),
    }
    missing = {
        "stage": sorted(public_tools.difference(AAA_TOOL_STAGE_MAP.keys())),
        "trinity": sorted(public_tools.difference(TRINITY_BY_TOOL.keys())),
        "law": sorted(public_tools.difference(AAA_TOOL_LAW_BINDINGS.keys())),
        "modes": sorted(public_tools.difference(TOOL_MODES.keys())),
    }
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "public_tools": sorted(public_tools),
        "missing": missing,
    }

class EvidenceBundle(BaseModel):
    bundle_id: str
    session_id: str
    sources: list[dict[str, Any]] = []

__all__ = [
    "VerdictCode", "RiskTier", "SessionState", "TrinityAspect",
    "SessionAnchor", "ToolAuthContext", "WitnessTriple", 
    "TelemetryEnvelope", "ConstitutionalHealthView", "VerdictRecord",
    "InitSessionAnchorInput", "JudgeVerdictInput", "SenseRealityInput",
    "ReasonSynthesisInput", "CritiqueSafetyInput", "LoadMemoryContextInput",
    "EstimateOpsInput", "RouteExecutionInput",
    "AAA_CANONICAL_TOOLS", "AAA_PUBLIC_TOOLS", "AAA_TOOL_ALIASES",
    "AAA_TOOL_STAGE_MAP", "TRINITY_BY_TOOL", "AAA_TOOL_LAW_BINDINGS",
    "DOMAIN_PAYLOAD_GATES", "LAW_13_CATALOG", "READ_ONLY_TOOLS", "REQUIRES_SESSION", "TOOL_MODES",
    "ToolEnvelope", "ToolStatus", "OutputPolicy", "VerdictScope", "HumanDecisionMarker", 
    "SessionClass", "TraceContext", "EntropyBudget",
    "make_telemetry_seed", "compute_psi_le", "calculate_entropy_budget", "check_domain_gate",
    "determine_human_marker", "generate_trace_context", "public_tool_input_contracts",
    "require_session", "validate_fail_closed", "verify_contract", "EvidenceBundle"
]
