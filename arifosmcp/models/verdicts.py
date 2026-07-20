"""
arifOS v2.0 — Canonical Verdict Enumerations (v1.0 ratified 2026-07-07)
═══════════════════════════════════════════════════════════════════════════
Defines the FIVE primary seals (SEAL, HOLD, SABAR, PARTIAL, VOID), the 14 canonical
qualified substates, the 13 constitutional floors, and the metabolic telemetry schemas.

5-state monotonic lattice (canon):
    VOID > HOLD > SABAR > PARTIAL > SEAL
    (most restrictive ─────────► least restrictive)

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE · canon anchored at /root/A-FORGE/proto/verdict/
"""

from __future__ import annotations

from enum import Enum, StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class SealType(StrEnum):
    """
    The SEVEN canonical seals of arifOS v2.0 (v1.0 ratified 2026-07-07, extended 2026-07-11).
    Only SEAL allows progression to Tier 05 (Execution).
    Monotonicity ordering: VOID > HOLD_888 > HOLD > SABAR > PARTIAL > PROVISIONAL > SEAL.

    PROVISIONAL and HOLD_888 were added 2026-07-11 during Phase 1 Verdict Unification
    (APEX Refactor Directive). They were previously defined only in runtime/model.py
    VerdictEnvelope and runtime/tools.py (dead enum). Now canonical.
    """

    VOID = "VOID"  # HARD floor violation — blocked permanently (rank 6)
    HOLD_888 = "HOLD_888"  # 888_HOLD — immediate sovereign escalation (rank 5)
    HOLD = "HOLD"  # Human veto/review required (rank 4)
    SABAR = "SABAR"  # SOFT caution — wait, retry allowed (rank 3)
    PARTIAL = "PARTIAL"  # DERIVED warning — proceed with cooling (rank 2)
    PROVISIONAL = "PROVISIONAL"  # Contract variant — interim state (rank 1)
    SEAL = "SEAL"  # all floors pass; W³ ≥ 0.95 — proceed (rank 0)


class VerdictState(StrEnum):
    """
    Detailed verdict states within the canonical seals.
    """

    # SEAL substates
    SEAL_CANONICAL = "SEAL_CANONICAL"  # High confidence, full compliance
    SEAL_QUALIFIED = "SEAL_QUALIFIED"  # Compliant with noted assumptions

    # HOLD substates
    HOLD_888 = "HOLD_888"  # Human Architect intervention required
    HOLD_UNCERTAINTY = "HOLD_UNCERTAINTY"  # Ωₒᵣₜₕₒ < 0.95 or Peace² < 0.70
    HOLD_TEMPORAL = "HOLD_TEMPORAL"  # Waiting for data vintage refresh

    # VOID substates
    VOID_BREACH = "VOID_BREACH"  # Constitutional Floor violation
    VOID_HANTU = "VOID_HANTU"  # Shadow arifOS / Narrative Laundering
    VOID_IRREVERSIBLE = "VOID_IRREVERSIBLE"  # Irreversible action without W³

    # SABAR substates
    SABAR_EPISTEMIC = "SABAR_EPISTEMIC"  # Waiting for grounded truth
    SABAR_GEOPOLITICAL = "SABAR_GEOPOLITICAL"  # Waiting for external stability

    # PARTIAL substates (v1.0 ratified 2026-07-07)
    PARTIAL_DERIVED = "PARTIAL_DERIVED"  # derived floor warns, proceed with cooling
    PARTIAL_REVERSIBILITY = "PARTIAL_REVERSIBILITY"  # reversibility ambiguous, monitor


class FloorState(StrEnum):
    """
    Metabolic states for each of the 13 floors.
    """

    INACTIVE = "INACTIVE"
    ACTIVE = "ACTIVE"
    COMPLETE = "COMPLETE"
    HOLD = "HOLD"
    VOID = "VOID"


class FloorName(StrEnum):
    """
    The 13 canonical floors of arifOS v2.0.
    Ordered by the Gödel-Locked Cognitive Stack.
    """

    F1_REVERSIBILITY = "F1_REVERSIBILITY"  # κᵣ — Can we undo this?
    F2_TRUTH = "F2_TRUTH"  # Λ2 — Physical grounding
    F3_TRI_WITNESS = "F3_TRI_WITNESS"  # W³ — human · ai · earth (H·A·E geometric mean, Nash 1950)
    F4_CLARITY = "F4_CLARITY"  # ΔS — Entropy reduction
    F5_ORTHOGONALITY = "F5_ORTHOGONALITY"  # Ω — Lane independence
    F6_MARUAH = "F6_MARUAH"  # Peace² — Human dignity
    F7_HUMILITY = "F7_HUMILITY"  # κ_H — Uncertainty declared
    F8_LOGIC = "F8_LOGIC"  # Internal consistency
    F9_ANTI_HANTU = "F9_ANTI_HANTU"  # Shadow detection
    L10_AMANAH = "L10_AMANAH"  # Fiduciary duty
    L11_IDENTITY = "L11_IDENTITY"  # Session anchoring
    L12_CONTINUITY = "L12_CONTINUITY"  # Passive monitoring
    L13_SOVEREIGNTY = "L13_SOVEREIGNTY"  # Human Architect Veto


class PipelineStage(int, Enum):
    """
    The 000→999 metabolic stages of arifOS v2.0.
    """

    S000_INIT = 0
    S111_OBSERVE = 111
    S222_EVIDENCE = 222
    S333_REASON = 333
    S444_CRITIQUE = 444
    S555_ROUTE = 555
    S666_FORGE = 666
    S777_MEASURE = 777
    S888_JUDGE = 888
    S999_SEAL = 999


class ConstitutionalThresholds(BaseModel):
    """
    Numerical thresholds for v2.0 metabolic gates.
    """

    omega_min: float = 0.95  # Ω Orthogonality
    peace2_floor: float = 0.70  # Ethical Stability
    w3_min: float = 0.95  # Tri-Witness Consensus
    delta_s_ceiling: float = 0.20  # Entropy Limit
    kappa_r_phys_floor: float = 0.40  # Reversibility Floor
    kappa_h_low: float = 0.03  # Humility Band Min
    kappa_h_high: float = 0.15  # Humility Band Max


class FloorMetrics(BaseModel):
    """
    Metrics for a single floor execution.
    """

    floor_number: int = Field(..., ge=1, le=13)
    floor_name: FloorName = Field(...)
    state: FloorState = Field(default=FloorState.INACTIVE)
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    violation: str | None = None

    @field_validator("floor_number")
    @classmethod
    def validate_floor(cls, v: int) -> int:
        if not 1 <= v <= 13:
            raise ValueError(f"Floor must be 1-13, got {v}")
        return v


class KernelMetrics(BaseModel):
    """
    Unified Telemetry from 13-floor kernel execution.
    """

    omega_ortho: float = Field(default=1.0, ge=0.0, le=1.0)
    delta_s: float = Field(default=0.0)
    peace2: float = Field(default=1.0)
    kappa_r: float = Field(default=1.0)
    w3: float = Field(default=1.0, ge=0.0, le=1.0)
    shadow_score: float = Field(default=0.0, ge=0.0, le=1.0)

    witness_vector: dict[str, float] = Field(
        default_factory=lambda: {"human": 1.0, "ai": 1.0, "earth": 1.0, "system": 1.0}
    )

    floors_passed: list[FloorName] = Field(default_factory=list)
    floors_violated: list[FloorName] = Field(default_factory=list)

    overall_confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class VerdictResult(BaseModel):
    """
    Complete arifOS v2.0 verdict result.
    """

    epoch: str = "2026.4.16-CANONICAL"
    session_id: str
    verdict: SealType = Field(default=SealType.HOLD)
    state: VerdictState = Field(default=VerdictState.HOLD_888)
    metrics: KernelMetrics = Field(default_factory=KernelMetrics)
    explanation: str = Field(default="")
    recommendations: list[str] = Field(default_factory=list)

    def is_sealed(self) -> bool:
        """Check if execution is authorized."""
        return self.verdict == SealType.SEAL

    def is_void(self) -> bool:
        """Check if constitution is breached."""
        return self.verdict == SealType.VOID


# ═══════════════════════════════════════════════════════════════════════════════
# QQQ RECOMMENDATION ENVELOPE (v1.0 — 2026-07-14)
# ═══════════════════════════════════════════════════════════════════════════════
# QQQ Recommendation Doctrine: operational protocol expressing F2+F4+F7.
# Every RECOMMENDATION/DECISION/VERDICT must carry this envelope.
# Doctrine: /root/AAA/governance/QQQ_RECOMMENDATION_PROTOCOL.md
# ═══════════════════════════════════════════════════════════════════════════════


class PathOption(BaseModel):
    """A single path in the QQQ option space (Q1 layer).

    Every path must carry: name, description, category, and Q2 metrics.
    Minimum 5 paths per envelope. NULL and INVERSE are mandatory.
    """

    path_id: str = Field(description="Unique path identifier (e.g., P1, P2)")
    name: str = Field(description="Short name for the path")
    description: str = Field(description="One-line description of what this path does")
    category: str = Field(
        description="Path category: CONSERVATIVE | AGGRESSIVE | NULL | INVERSE | LATERAL"
    )

    # Q2 metrics — all required
    blast_radius: int = Field(
        ge=0,
        le=5,
        description="BR-0..5. How many systems/organs are affected? 0=none, 5=federation-wide",
    )
    reversibility: int = Field(
        ge=0,
        le=5,
        description="REV-0..5. How reversible is this path? 0=irreversible, 5=fully reversible",
    )
    time_cost: str = Field(description="Estimated time with units (e.g., '~15min', '~2hr', '0min')")
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence in outcome (0.0-1.0). Must have evidence basis."
    )
    prior_art: str = Field(description="Prior-art availability: STRONG | WEAK | NONE")


class QuantumAnalysis(BaseModel):
    """Q3 quantum analysis — second-order effects (Q3 layer).

    Every recommendation must answer all four quantum questions.
    These surface effects not visible in local reasoning.
    """

    precedent_effect: str = Field(
        description="If this path becomes canonical, what future decisions does it force?"
    )
    interference_effect: str = Field(
        description="What other organs/agents/sessions get affected that are not obvious?"
    )
    superposition_effect: str = Field(
        description="Are we collapsing options that should have stayed open?"
    )
    observer_effect: str = Field(
        description="How does the act of choosing change the choice space itself?"
    )


class RecommendationEnvelope(BaseModel):
    """QQQ Recommendation Envelope v1.0.

    Every RECOMMENDATION/DECISION/VERDICT must carry this envelope.
    Missing any section → qqq_compliance = INADMISSIBLE-Q*.

    This is NOT a new constitutional floor. It is jurisprudence —
    the operational protocol that enforces F2 TRUTH + F4 CLARITY + F7 HUMILITY
    on recommendations.

    Doctrine: /root/AAA/governance/QQQ_RECOMMENDATION_PROTOCOL.md
    """

    # Q1 — Qualitative: option space
    paths: list[PathOption] = Field(
        min_length=5, description="Minimum 5 paths. Must include NULL and INVERSE categories."
    )

    # Q2 — Quantitative: dominance analysis
    dominance_analysis: list[str] = Field(
        default_factory=list, description="Which paths dominate on which metrics"
    )

    # Q3 — Quantum: second-order effects
    quantum: QuantumAnalysis = Field(
        description="Four quantum questions: precedent, interference, superposition, observer"
    )

    # Verdict
    recommended_path_id: str = Field(
        description="Which path is recommended (must match a path_id in paths)"
    )
    reasoning_trace: list[str] = Field(
        default_factory=list, description="Q1 → Q2 → Q3 → verdict reasoning chain"
    )
    refusal_surface: list[str] = Field(
        default_factory=list, description="What this recommendation refuses to do"
    )
    sovereign_gate_required: bool = Field(
        default=False, description="Does this recommendation require F13 approval?"
    )

    # Compliance
    qqq_compliance: str = Field(
        default="COMPLETE",
        description="COMPLETE | INADMISSIBLE-Q1 | INADMISSIBLE-Q2 | INADMISSIBLE-Q3",
    )

    # Identity
    human_final_authority: str = Field(
        default="Arif", description="Who has final say. Always 'Arif' — F13 veto is absolute."
    )

    @field_validator("paths")
    @classmethod
    def validate_mandatory_categories(cls, v: list[PathOption]) -> list[PathOption]:
        """Q1 rule: NULL and INVERSE categories must be present."""
        categories = {p.category for p in v}
        if "NULL" not in categories:
            raise ValueError("Q1 violation: NULL path is mandatory (do-nothing option)")
        if "INVERSE" not in categories:
            raise ValueError("Q1 violation: INVERSE path is mandatory (do-opposite option)")
        return v

    @field_validator("recommended_path_id")
    @classmethod
    def validate_recommended_path_exists(cls, v: str, info) -> str:
        """Verdict must reference a valid path_id."""
        paths = info.data.get("paths", [])
        if paths and v not in {p.path_id for p in paths}:
            raise ValueError(f"recommended_path_id '{v}' not found in paths")
        return v

    def to_receipt(self) -> dict[str, Any]:
        """Convert to VAULT999 receipt dict.

        Returns structured data (not JSON blob) for VAULT999 sealing.
        Queryable by path_id, category, decision_reason.

        This is the historical value of QQQ: past recommendations become
        the prior-art corpus for future Q2 confidence scoring.
        """
        from datetime import UTC, datetime

        recommended_path = next(
            (p for p in self.paths if p.path_id == self.recommended_path_id),
            None,
        )

        return {
            "receipt_type": "QQQ_RECOMMENDATION",
            "version": "1.0",
            "sealed_at": datetime.now(UTC).isoformat(),
            "paths": [
                {
                    "path_id": p.path_id,
                    "name": p.name,
                    "category": p.category,
                    "blast_radius": p.blast_radius,
                    "reversibility": p.reversibility,
                    "time_cost": p.time_cost,
                    "confidence": p.confidence,
                    "prior_art": p.prior_art,
                }
                for p in self.paths
            ],
            "recommended_path_id": self.recommended_path_id,
            "recommended_path_name": recommended_path.name if recommended_path else None,
            "decision_reason": (
                f"Recommended {self.recommended_path_id}: " + "; ".join(self.reasoning_trace)
                if self.reasoning_trace
                else "No reasoning trace provided"
            ),
            "quantum_analysis": {
                "precedent_effect": self.quantum.precedent_effect,
                "interference_effect": self.quantum.interference_effect,
                "superposition_effect": self.quantum.superposition_effect,
                "observer_effect": self.quantum.observer_effect,
            },
            "qqq_compliance": self.qqq_compliance,
            "refusal_surface": self.refusal_surface,
            "sovereign_gate_required": self.sovereign_gate_required,
            "human_final_authority": self.human_final_authority,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL ALIAS — single import path for all runtime code
# ═══════════════════════════════════════════════════════════════════════════════
# All runtime modules import:
#   from arifosmcp.models.verdicts import Verdict, RuntimeStatus
# No module may define its own Verdict class locally.
# ═══════════════════════════════════════════════════════════════════════════════

Verdict = SealType
"""Canonical governance verdict. Alias for SealType.
Constitutional ordering: VOID > HOLD > SABAR > SEAL"""


# ═══════════════════════════════════════════════════════════════════════════════
# TRANSPORT STATUS — execution plumbing, NOT governance
# ═══════════════════════════════════════════════════════════════════════════════
# Governance = constitutional law (Verdict: SEAL/HOLD/SABAR/VOID)
# Transport  = execution plumbing (RuntimeStatus: SUCCESS/ERROR/TIMEOUT/RETRY)
# These are NEVER mixed. A tool returns a RuntimeStatus and may carry a Verdict.
# ═══════════════════════════════════════════════════════════════════════════════


class RuntimeStatus(StrEnum):
    """Transport status — execution plumbing, not constitutional governance.

    This is what a tool returns to indicate execution outcome.
    Governance verdicts (SEAL/HOLD/SABAR/VOID) travel in the payload, NOT as status.
    """

    SUCCESS = "SUCCESS"  # Tool executed normally
    ERROR = "ERROR"  # Tool encountered an error
    TIMEOUT = "TIMEOUT"  # Tool exceeded its time budget
    RETRY = "RETRY"  # Transient failure — caller should retry
    HOLD = "HOLD"  # Tool blocked by constitutional gate (NOT governance verdict — transport block)


# ═══════════════════════════════════════════════════════════════════════════════
# MONOTONICITY (v1.0 — ratified 2026-07-07, 5-state lattice)
# ═══════════════════════════════════════════════════════════════════════════════
# VOID > HOLD > SABAR > PARTIAL > SEAL
# - VOID overrides everything — irreversible constitutional breach
# - HOLD overrides SABAR + PARTIAL + SEAL — human veto
# - SABAR overrides PARTIAL + SEAL — conditional proceed
# - PARTIAL overrides SEAL — derived warning, proceed cooling
# - SEAL is the lowest authority — proceed only if no higher verdict blocks
#
# Every merge point in the system must respect this ordering:
# - arif_judge verdict merge
# - arif_memory floor aggregation
# - arif_forge execution gates
# - 888_HOLD conflict routing
# - JITU contradiction detection (δ ≥ 0.50 → HOLD)
# ═══════════════════════════════════════════════════════════════════════════════


VERDICT_ORDER: dict[str, int] = {
    # v1.0 ratified 2026-07-07 — 5-state lattice (added PARTIAL between SABAR and SEAL)
    # Higher number = higher authority (more restrictive)
    # VOID (4) > HOLD (3) > SABAR (2) > PARTIAL (1) > SEAL (0)
    "SEAL": 0,
    "PARTIAL": 1,
    "SABAR": 2,
    "HOLD": 3,
    "VOID": 4,
}


def enforce_verdict_monotonicity(v: Verdict | str) -> int:
    """Return the constitutional weight of a verdict (v1.0 — 5-state lattice, 2026-07-07).

    Higher weight = higher authority.
    Use this to enforce that a HOLD cannot be downgraded to SEAL,
    and VOID cannot be overridden by any other verdict.

    Args:
        v: Verdict as SealType enum or string ("SEAL", "PARTIAL", "HOLD", "SABAR", "VOID")

    Returns:
        Integer weight: SEAL=0, PARTIAL=1, SABAR=2, HOLD=3, VOID=4

    Raises:
        ValueError: If the verdict string is not a canonical verdict
    """
    key = v.value if isinstance(v, Verdict) else str(v).upper()
    if key not in VERDICT_ORDER:
        raise ValueError(
            f"Unknown verdict '{v}'. Canonical verdicts: SEAL, PARTIAL, HOLD, SABAR, VOID. "
            "RuntimeStatus values (SUCCESS/ERROR/TIMEOUT/RETRY) are transport only."
        )
    return VERDICT_ORDER[key]


def merge_verdicts(v1: Verdict | str, v2: Verdict | str) -> Verdict:
    """Merge two verdicts — the higher weight wins (v1.0 — 5-state lattice).

    At every merge point in the system, call this to enforce monotonicity.
    A HOLD from any gate cannot be downgraded by a later SEAL.
    PARTIAL merges into SABAR weight class (weight=2 in this 5-state impl).
    """
    w1 = enforce_verdict_monotonicity(v1)
    w2 = enforce_verdict_monotonicity(v2)
    wmax = max(w1, w2)
    if wmax >= 4:
        return Verdict(SealType.VOID)
    if wmax >= 3:
        return Verdict(SealType.HOLD)
    if wmax >= 2:
        return Verdict(SealType.SABAR)
    if wmax >= 1:
        return Verdict(SealType.PARTIAL)
    return Verdict(SealType.SEAL)


def is_verdict_allowed(v: Verdict | str) -> bool:
    """Check if a verdict allows progression (v1.0 — 5-state lattice).

    Progression allowed for: SEAL, PARTIAL, SABAR (proceed with caveats).
    Blocked for: HOLD (paused), VOID (constitutional breach).
    """
    weight = enforce_verdict_monotonicity(v)
    return weight <= 2  # SEAL=0, PARTIAL=1, SABAR=2 — all three allow action with semantics
