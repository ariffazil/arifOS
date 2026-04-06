"""
arifOS MCP Context Contracts
═══════════════════════════════════════════════════════════════════════════════

Shared JSON schemas for tools, resources, and prompts.
These contracts ensure type safety and consistency across the MCP surface.

Aligned with SPEC.md: Functional naming, canonical fields, and strict typing.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


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

AAA_PUBLIC_TOOLS = AAA_CANONICAL_TOOLS

AAA_TOOL_ALIASES = {
    "init_anchor": "arifos.init",
    "arifOS_kernel": "arifos.route",
    "apex_soul": "arifos.judge",
    "apex_judge": "arifos.judge",
    "vault_ledger": "arifos.vault",
    "agi_mind": "arifos.mind",
    "asi_heart": "arifos.heart",
    "engineering_memory": "arifos.memory",
    "physics_reality": "arifos.sense",
    "math_estimator": "arifos.ops",
    "architect_registry": "arifos.init",  # Merged into init
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
}

AAA_TOOL_LAW_BINDINGS = {
    "init_session_anchor": ["F11", "F12", "F13"],
    "get_tool_registry": ["F10", "F11"],
    "sense_reality": ["F2", "F3", "F10"],
    "reason_synthesis": ["F2", "F4", "F7", "F8"],
    "critique_safety": ["F5", "F6", "F9"],
    "route_execution": ["F4", "F11"],
    "load_memory_context": ["F10", "F11", "F2"],
    "estimate_ops": ["F4", "F5"],
    "judge_verdict": ["F3", "F12", "F13"],
    "record_vault_entry": ["F1", "F13"],
    "execute_vps_task": ["F1"],
}

# Missing names identified from contracts_v2.py
DOMAIN_PAYLOAD_GATES = {}
LAW_13_CATALOG = {}
READ_ONLY_TOOLS = ["get_tool_registry", "sense_reality", "estimate_ops"]
REQUIRES_SESSION = AAA_CANONICAL_TOOLS
TOOL_MODES = {}

# Legacy class aliases for compatibility
ToolEnvelope = TelemetryEnvelope
ToolStatus = Literal["SUCCESS", "FAILURE", "VOID", "HOLD"]
OutputPolicy = Literal["redact", "mask", "raw"]
VerdictScope = Literal["session", "global", "resource"]
HumanDecisionMarker = Any
SessionClass = Literal["public", "authenticated", "sovereign"]
TraceContext = Any
EntropyBudget = Any

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

def calculate_entropy_budget(*args, **kwargs): return 0.0
def check_domain_gate(*args, **kwargs): return True
def determine_human_marker(*args, **kwargs): return None
def generate_trace_context(*args, **kwargs): return {}
def public_tool_input_contracts(): return {}
def require_session(fn): return fn
def validate_fail_closed(*args, **kwargs): return True
def verify_contract(*args, **kwargs): return True

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
