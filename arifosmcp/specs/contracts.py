"""
arifOS MCP Context Contracts
═══════════════════════════════════════════════════════════════════════════════

Shared JSON schemas for tools, resources, and prompts.
These contracts ensure type safety and consistency across the MCP surface.

Contract categories:
- Identity: SessionAnchor, ToolAuthContext
- Telemetry: TelemetryEnvelope, ConstitutionalHealthView
- Evidence: EvidenceBundle, WitnessTriple
- Verdict: VerdictRecord, VerdictCode
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


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
    Root identity contract for all arifOS sessions.
    
    Every session begins with an anchor that binds:
    - A unique session identity
    - The actor's claimed and verified identity
    - Authority level and scope
    - Constitutional telemetry seed
    """
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "session_id": "sess_arifos_abc123",
            "epoch": "2026-04-06",
            "declared_actor_id": "user@example.com",
            "verified_actor_id": "user@example.com",
            "canonical_actor_id": "user@example.com",
            "state": "anchored",
            "authority_level": "operator",
            "trinity_seed": "PSI",
            "baseline_tau": 1.0,
            "baseline_omega": 0.05
        }
    })
    
    session_id: str = Field(..., description="Unique session identifier")
    epoch: str = Field(default="2026-04-06", description="Governance epoch")
    
    # Identity layers
    declared_actor_id: str | None = Field(None, description="Self-claimed identity")
    verified_actor_id: str | None = Field(None, description="Cryptographically verified identity")
    canonical_actor_id: str = Field(default="anonymous", description="Resolved effective identity")
    
    # State and authority
    state: SessionState = Field(default=SessionState.ANONYMOUS)
    authority_level: Literal["anonymous", "claimed", "user", "agent", "operator", "sovereign"] = Field(
        default="anonymous"
    )
    
    # Trinity alignment
    trinity_seed: TrinityAspect = Field(default=TrinityAspect.PSI)
    
    # Telemetry baseline (established at anchor time)
    baseline_tau: float = Field(default=1.0, ge=0.0, le=1.0, description="Truth baseline")
    baseline_omega: float = Field(default=0.05, ge=0.0, le=1.0, description="Humility baseline")


class ToolAuthContext(BaseModel):
    """
    Authentication context for restricted tool access.
    
    Required for tools that:
    - Access governed memory (engineering_memory)
    - Seal vault entries (vault_ledger)
    - Execute VPS tasks (code_engine)
    """
    actor_id: str = Field(..., description="Verified actor identity")
    session_id: str = Field(..., description="Bound session")
    approval_scope: list[str] = Field(default_factory=list, description="Granted tool scopes")
    human_approval_persisted: bool = Field(default=False, description="F13 human override")
    proof_timestamp: str | None = Field(None, description="ISO 8601 of proof generation")
    
    @field_validator('approval_scope')
    @classmethod
    def validate_scope(cls, v: list[str]) -> list[str]:
        valid_prefixes = ('arifos_kernel:', 'engineering_memory:', 'vault_ledger:', 'code_engine:', '*')
        for scope in v:
            if not any(scope.startswith(p) or scope == p.rstrip(':') for p in valid_prefixes):
                raise ValueError(f"Invalid scope: {scope}")
        return v


# ═══════════════════════════════════════════════════════════════════════════════
# TELEMETRY CONTRACTS
# ═══════════════════════════════════════════════════════════════════════════════

class WitnessTriple(BaseModel):
    """
    The three-witness attestation model.
    
    Constitutional truth requires convergence of:
    - human: Human judgment or oversight
    - ai: AI reasoning and synthesis
    - earth: Observable reality and facts
    """
    human: float = Field(default=1.0, ge=0.0, le=1.0, description="Human witness confidence")
    ai: float = Field(default=0.0, ge=0.0, le=1.0, description="AI witness confidence")
    earth: float = Field(default=0.0, ge=0.0, le=1.0, description="Earth witness confidence")
    
    @property
    def coherence(self) -> float:
        """Geometric mean of witness confidences."""
        import math
        return math.pow(self.human * self.ai * self.earth, 1/3) if all([self.human, self.ai, self.earth]) else 0.0


class TelemetryEnvelope(BaseModel):
    """
    Standard telemetry packet for all arifOS operations.
    
    These six canonical metrics govern all constitutional evaluation:
    - tau_truth: Truth alignment (0-1)
    - omega_0: Humility/uncertainty level (0-1)
    - delta_s: Entropy change (-1 to +1)
    - peace2: Conflict resolution ratio (>1 is peaceful)
    - kappa_r: Reality grounding (0-1)
    - tri_witness: Triple witness coherence (0-1)
    """
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "session_id": "sess_abc123",
            "epoch": "2026-04-06",
            "timestamp": "2026-04-06T10:30:00Z",
            "tau_truth": 0.995,
            "omega_0": 0.04,
            "delta_s": -0.35,
            "peace2": 1.08,
            "kappa_r": 0.97,
            "tri_witness": 0.95,
            "psi_le": 1.09,
            "verdict_hint": "SEAL"
        }
    })
    
    session_id: str = Field(..., description="Source session")
    epoch: str = Field(default="2026-04-06", description="Governance epoch")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    
    # Six canonical constitutional metrics
    tau_truth: float = Field(default=0.95, ge=0.0, le=1.0, description="F2: Truth alignment")
    omega_0: float = Field(default=0.05, ge=0.0, le=1.0, description="F7: Humility level")
    delta_s: float = Field(default=0.0, ge=-1.0, le=1.0, description="F4: Entropy delta")
    peace2: float = Field(default=1.0, ge=0.0, description="F6: Conflict resolution")
    kappa_r: float = Field(default=0.9, ge=0.0, le=1.0, description="F3: Reality grounding")
    tri_witness: float = Field(default=0.0, ge=0.0, le=1.0, description="F9: Witness coherence")
    
    # Derived
    psi_le: float | None = Field(None, description="Life/entropy index (computed)")
    verdict_hint: VerdictCode = Field(default=VerdictCode.SABAR, description="Suggested verdict")


class ConstitutionalHealthView(BaseModel):
    """
    Human-readable constitutional health snapshot.
    
    Used by ChatGPT widget and dashboard UIs.
    """
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "session_id": "sess_abc123",
            "timestamp": "2026-04-06T10:30:00Z",
            "truth_score": 0.995,
            "humility_level": 0.04,
            "entropy_delta": -0.35,
            "harmony_ratio": 1.08,
            "reality_index": 0.97,
            "witness_strength": 0.95,
            "verdict": "SEAL",
            "verdict_label": "Aligned",
            "attestation": {"jurors": 5, "quorum": 3, "sealed": True}
        }
    })
    
    session_id: str
    timestamp: str
    
    # Floor scores (human labels)
    truth_score: float = Field(..., ge=0.0, le=1.0, description="tau_truth")
    humility_level: float = Field(..., ge=0.0, le=1.0, description="omega_0")
    entropy_delta: float = Field(..., ge=-1.0, le=1.0, description="delta_s")
    harmony_ratio: float = Field(..., ge=0.0, description="peace2")
    reality_index: float = Field(..., ge=0.0, le=1.0, description="kappa_r")
    witness_strength: float = Field(..., ge=0.0, le=1.0, description="tri_witness")
    
    # Verdict
    verdict: VerdictCode
    verdict_label: str = Field(..., description="Human-readable verdict")
    
    # BLS attestation (if available)
    attestation: dict[str, Any] | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# EVIDENCE CONTRACTS
# ═══════════════════════════════════════════════════════════════════════════════

class EvidenceBundle(BaseModel):
    """
    Standard evidence container for multi-agent handoffs.
    
    Ensures continuity when passing context between:
    - Different tools
    - Different agents
    - Different sessions
    """
    bundle_id: str = Field(..., description="Unique evidence bundle ID")
    source_session: str = Field(..., description="Originating session")
    source_tool: str = Field(..., description="Tool that produced this evidence")
    timestamp: str = Field(..., description="ISO 8601 creation time")
    
    # Content
    evidence_type: Literal["synthesis", "critique", "verification", "observation", "judgment"] = Field(
        default="observation"
    )
    content: str = Field(..., max_length=100000, description="Evidence payload")
    content_hash: str | None = Field(None, description="SHA-256 of content")
    
    # Constitutional context
    telemetry_at_capture: TelemetryEnvelope | None = None
    witness_at_capture: WitnessTriple | None = None
    
    # Chain
    parent_bundle_id: str | None = Field(None, description="Previous bundle in chain")
    child_bundle_ids: list[str] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════════
# VERDICT CONTRACTS
# ═══════════════════════════════════════════════════════════════════════════════

class VerdictRecord(BaseModel):
    """
    Immutable vault record for constitutional decisions.
    
    Sealed with BLS signatures and stored in Vault999.
    """
    record_id: str = Field(..., description="Unique record identifier")
    session_id: str = Field(..., description="Source session")
    timestamp: str = Field(..., description="ISO 8601 seal time")
    
    # Decision
    verdict: VerdictCode
    candidate_action: str = Field(..., max_length=10000, description="What was evaluated")
    risk_tier: RiskTier
    
    # Constitutional basis
    floors_checked: list[str] = Field(default_factory=list)
    floors_failed: list[str] = Field(default_factory=list)
    telemetry_at_verdict: TelemetryEnvelope
    
    # Attestation
    juror_signatures: list[dict[str, Any]] = Field(default_factory=list)
    aggregate_signature: str | None = None
    seal_status: Literal["PENDING", "SEALED", "VERIFIED", "MIGRATED"] = "PENDING"
    
    # Audit
    human_override: bool = False
    override_reason: str | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL INPUT CONTRACTS
# ═══════════════════════════════════════════════════════════════════════════════

class JudgeVerdictInput(BaseModel):
    """Input schema for judge_verdict tool."""
    candidate_action: str = Field(..., description="The proposed action to evaluate")
    risk_tier: RiskTier = Field(default=RiskTier.MEDIUM)
    telemetry: TelemetryEnvelope | None = None
    context: str | None = Field(None, description="Additional evaluation context")
    session_id: str | None = None


class InitSessionInput(BaseModel):
    """Input schema for init_session_anchor tool."""
    actor_id: str | None = Field(None, description="Identity claim")
    intent: str | None = Field(None, description="Purpose of session")
    session_class: Literal["query", "execute", "elevated", "sovereign"] = Field(default="execute")
    human_approval: bool = False


class SenseRealityInput(BaseModel):
    """Input schema for sense_reality tool."""
    query: str = Field(..., description="What to search/verify")
    operation: Literal["search", "ingest", "compass", "atlas", "time"] = Field(default="search")
    top_k: int = Field(default=5, ge=1, le=20)
    session_id: str | None = None


class RouteExecutionInput(BaseModel):
    """Input schema for route_execution tool."""
    query: str = Field(..., description="User request to route")
    intent_type: Literal["ask", "audit", "design", "decide", "analyze", "execute"] = Field(
        default="ask"
    )
    max_steps: int = Field(default=13, ge=1, le=50)
    session_id: str | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def make_telemetry_seed(session_id: str) -> TelemetryEnvelope:
    """Generate a fresh telemetry seed for a new session."""
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
    """
    Compute psi_LE (Life/Entropy index).
    
    Higher values indicate more life-like (low entropy, high truth, high peace).
    """
    import math
    # Normalize components
    truth_component = telemetry.tau_truth
    entropy_component = 1 - abs(telemetry.delta_s)  # Low entropy change is good
    peace_component = min(telemetry.peace2 / 2.0, 1.0)  # Cap at 2.0
    
    # Geometric mean with witness weight
    witness_weight = telemetry.tri_witness if telemetry.tri_witness > 0 else 0.5
    
    psi = math.pow(truth_component * entropy_component * peace_component * witness_weight, 0.25)
    return round(psi + 1.0, 3)  # Scale to 1.0-2.0 range


__all__ = [
    # Enums
    "VerdictCode",
    "RiskTier", 
    "SessionState",
    "TrinityAspect",
    # Identity
    "SessionAnchor",
    "ToolAuthContext",
    # Telemetry
    "WitnessTriple",
    "TelemetryEnvelope",
    "ConstitutionalHealthView",
    # Evidence
    "EvidenceBundle",
    # Verdict
    "VerdictRecord",
    # Tool inputs
    "JudgeVerdictInput",
    "InitSessionInput",
    "SenseRealityInput",
    "RouteExecutionInput",
    # Utils
    "make_telemetry_seed",
    "compute_psi_le",
]
