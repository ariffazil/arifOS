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

from enum import Enum, StrEnum

from pydantic import BaseModel, Field, field_validator


class SealType(StrEnum):
    """
    The FIVE canonical seals of arifOS v2.0 (v1.0 ratified 2026-07-07).
    Only SEAL allows progression to Tier 05 (Execution).
    Monotonicity ordering: VOID > HOLD > SABAR > PARTIAL > SEAL.
    """

    VOID = "VOID"  # HARD floor violation — blocked permanently (rank 4)
    HOLD = "HOLD"  # 888_HOLD — human veto/review required (rank 3)
    SABAR = "SABAR"  # SOFT caution — wait, retry allowed (rank 2)
    PARTIAL = "PARTIAL"  # DERIVED warning — proceed with cooling (rank 1)
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
