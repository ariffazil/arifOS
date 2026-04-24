"""
Verdict and seal output schemas — 888_JUDGE, 999_VAULT, 666_HEART
══════════════════════════════════════════════════════════════════════════

Phase 2 Civilization Intelligence: Full structural upgrade.

888_JUDGE VerdictOutput must include:
- ToAC (Theory of Anomalous Contrast) for manipulation detection
- ThermodynamicState for entropy awareness
- DecisionCollapse for probabilistic state resolution
- GrowthParadox for scale risk detection
- AKAL for present energy awareness
- AmanahProof for ethical stewardship validation
- FloorComplianceProof for constitutional enforcement
- CivilizationalAnchor for philosophy-stabilized reasoning

DITEMPA BUKAN DIBERI — Forged, Not Given
"""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from arifosmcp.schemas.cognition import UncertaintyGeometry
from arifosmcp.schemas.forge import IrreversibilityBond, ConstitutionalCompliance
from arifosmcp.schemas.lineage import JudgeSealContract


# ═══════════════════════════════════════════════════════════════════════════════
# VERDICT CODES
# ═══════════════════════════════════════════════════════════════════════════════

class VerdictCode(str, Enum):
    SEAL = "SEAL"       # Approved — proceed
    SABAR = "SABAR"      # Wait — under review
    VOID = "VOID"       # Rejected — constitutional breach
    HOLD = "HOLD"       # Paused — manual review required


# ═══════════════════════════════════════════════════════════════════════════════
# TOAC — THEORY OF ANOMALOUS CONTRAST
# ═══════════════════════════════════════════════════════════════════════════════

class AnomalousContrast(BaseModel):
    """
    Detects contrast between expected vs observed, claimed vs verified.

    ToAC Principle: Intelligence = ability to detect and resolve contrast.

    Embeds in: 333_MIND, 888_JUDGE, 999_VAULT
    """
    # Baseline expectation
    baseline_model: str = Field(description="What the system expected before evidence")

    # What actually happened
    observed_deviation: str = Field(description="How reality diverged from expectation")

    # Magnitude
    magnitude: float = Field(
        ge=0.0, le=1.0,
        description="Normalized deviation strength (0=none, 1=maximum)"
    )

    # Confidence in detection
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence that deviation is real, not noise"
    )

    # Contrast type classification
    contrast_type: str = Field(
        description="'expected_vs_observed' | 'claimed_vs_verified' | 'shortterm_vs_entropy' | 'local_vs_civilizational'"
    )

    # Resolution
    resolution_strategy: str | None = Field(
        default=None,
        description="How the system resolved the contrast"
    )
    resolution_confidence: float | None = Field(
        default=None, ge=0.0, le=1.0,
        description="Confidence in resolution strategy"
    )

    # Manipulation detection
    manipulation_signal: bool = Field(
        default=False,
        description="Does contrast suggest intentional manipulation (F09)?"
    )
    anti_hantu_score: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Likelihood of hantu (manipulation) detected"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# THERMODYNAMIC STATE
# ═══════════════════════════════════════════════════════════════════════════════

class ThermodynamicState(BaseModel):
    """
    Energy, entropy, and reversibility tracking.

    Intelligence evolves through thermodynamic → informational → strategic → quantum layers.
    This schema captures Layer 1 (thermodynamic) for all major decisions.
    """
    # Energy cost
    energy_estimate: float | None = Field(
        default=None,
        description="Estimated energy cost in joules"
    )

    # Entropy change
    delta_S: float = Field(
        default=0.0,
        description="Entropy change from this action (positive = disorder)"
    )

    # Direction
    entropy_direction: str = Field(
        default="unknown",
        description="'increasing' | 'decreasing' | 'stable' | 'unknown'"
    )

    # Reversibility
    irreversibility: bool = Field(
        default=False,
        description="Is this action thermodynamically irreversible?"
    )
    reversibility_cost: float | None = Field(
        default=None,
        description="Energy cost to reverse (if reversible)"
    )
    reversal_window_seconds: float | None = Field(
        default=None,
        description="Time window for safe reversal (if applicable)"
    )

    # Landauer compliance
    landauer_cost_eV: float | None = Field(
        default=None,
        description="Minimum thermodynamic cost (kT * ln 2) in electron volts"
    )

    # Quantum layer indicator
    decision_collapse_triggered: bool = Field(
        default=False,
        description="Did probabilistic state collapse occur at decision point?"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# DECISION COLLAPSE — QUANTUM INTELLIGENCE LAYER
# ═══════════════════════════════════════════════════════════════════════════════

class DecisionCollapse(BaseModel):
    """
    Probabilistic state collapse under constraint.

    Quantum intelligence layer: multi-distribution → single verdict.
    Tracks prior → posterior transformation.
    """
    # Prior state
    prior_distribution: dict[str, float] = Field(
        default_factory=dict,
        description="Probability distribution before decision (e.g., {'SEAL': 0.3, 'SABAR': 0.5, 'VOID': 0.2})"
    )

    # Posterior state
    posterior_distribution: dict[str, float] = Field(
        default_factory=dict,
        description="Probability distribution after decision"
    )

    # Collapse mechanism
    collapse_trigger: str = Field(
        description="What triggered collapse: 'threshold' | 'evidence' | 'override' | 'timeout'"
    )

    # Post-collapse
    residual_uncertainty: float = Field(
        ge=0.0, le=1.0,
        description="Uncertainty remaining after collapse (0=certain, 1=maximum)"
    )

    # Confidence shift
    confidence_shift: float = Field(
        default=0.0,
        description="Change in confidence from prior to posterior"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# GROWTH PARADOX
# ═══════════════════════════════════════════════════════════════════════════════

class GrowthParadox(BaseModel):
    """
    Detects when scale increases faster than stability.

    Paradox of Growth Principle: Growth increases entropy unless structured by constraint.

    Mandatory in: 777_OPS, 888_JUDGE, 444_KERNEL
    """
    # Scale
    scaling_factor: float = Field(
        default=1.0,
        ge=0.0,
        description="Growth multiplier (1.0 = no growth, 2.0 = 2x)"
    )

    # Stability
    stability_margin: float = Field(
        ge=0.0, le=1.0,
        description="Margin before instability (0=no margin, 1=maximum margin)"
    )

    # Systemic risk
    systemic_risk: float = Field(
        ge=0.0, le=1.0,
        description="Likelihood that scaling creates system-wide instability"
    )

    # Fragility
    fragility_index: float = Field(
        ge=0.0, le=1.0,
        description="Structural fragility under scaling (0=robust, 1=brittle)"
    )

    # Paradox detection
    paradox_detected: bool = Field(
        default=False,
        description="Is growth paradox active (scaling > stability)?"
    )
    paradox_mitigation: str | None = Field(
        default=None,
        description="Strategy to resolve paradox if detected"
    )

    # Efficiency vs fragility
    efficiency_fragility_tradeoff: float = Field(
        default=0.5, ge=0.0, le=1.0,
        description="Balance: 0=maximum efficiency, 1=maximum stability"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# AKAL — PRESENT ENERGY AWARENESS
# ═══════════════════════════════════════════════════════════════════════════════

class AkalState(BaseModel):
    """
    Present-state awareness of system energy and capacity.

    AKAL = Present Energy Awareness (Sikh philosophy of current consciousness).

    Every decision must track current system state, not hypothetical future.
    """
    # Present energy
    present_energy: float = Field(
        ge=0.0,
        description="Available cognitive energy now (arbitrary units)"
    )
    present_energy_ratio: float = Field(
        ge=0.0, le=1.0,
        description="Energy as ratio of maximum capacity"
    )

    # Cognitive load
    cognitive_load: float = Field(
        ge=0.0, le=1.0,
        description="Current load as ratio of capacity (0=idle, 1=fully loaded)"
    )

    # System capacity
    system_capacity: float = Field(
        description="Maximum cognitive capacity available"
    )
    capacity_utilized: float = Field(
        ge=0.0, le=1.0,
        description="Percentage of capacity currently in use"
    )

    # Alignment state
    alignment_state: str = Field(
        default="stable",
        description="'stable' | 'strained' | 'critical' | 'overload'"
    )

    # Energy trajectory
    energy_trend: str = Field(
        default="stable",
        description="'increasing' | 'stable' | 'decreasing' | 'depleted'"
    )
    projected_depletion_seconds: float | None = Field(
        default=None,
        description="Estimated seconds until energy depletion (if decreasing)"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# AMANAH GENIUS — ETHICAL STEWARDSHIP + STRUCTURAL ELEGANCE
# ═══════════════════════════════════════════════════════════════════════════════

class AmanahProof(BaseModel):
    """
    Trust stewardship (Amanah) + Structural elegance (Genius).

    AmanahPrinciple: Every action is accountable.
    GeniusPrinciple: Elegance under constraint, not brute force.

    Mandatory in: 888_JUDGE, 999_VAULT, 010_FORGE
    """
    # Floor compliance
    floors_checked: list[str] = Field(
        default_factory=list,
        description="F1-F13 floors evaluated for this action"
    )
    floors_passed: list[str] = Field(
        default_factory=list,
        description="Floors that passed"
    )
    floors_failed: list[str] = Field(
        default_factory=list,
        description="Floors that blocked or required override"
    )

    # Violations
    violations: list[str] = Field(
        default_factory=list,
        description="Specific floor breaches detected"
    )
    violation_mitigation: list[str] = Field(
        default_factory=list,
        description="How each violation was addressed or acknowledged"
    )

    # Override
    override_acknowledged: bool = Field(
        default=False,
        description="Did sovereign (F13) override any floor?"
    )
    override_reason: str | None = Field(
        default=None,
        description="Why sovereign chose to override"
    )
    override_authorizer: str | None = Field(
        default=None,
        description="Who authorized the override (must be sovereign)"
    )

    # Genius score
    genius_score: float = Field(
        ge=0.0, le=1.0,
        description="Structural elegance: 0=brute force, 1=minimal path with maximum effect"
    )
    genius_rationale: str | None = Field(
        default=None,
        description="Why this is the genius (elegant) path"
    )

    # Minimal entropy path
    entropy_minimal: bool = Field(
        default=True,
        description="Is this the minimum entropy path to achieve the goal?"
    )
    entropy_alternatives_considered: int = Field(
        default=0,
        ge=0,
        description="How many alternative paths were evaluated for entropy comparison"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# FLOOR COMPLIANCE PROOF
# ═══════════════════════════════════════════════════════════════════════════════

class FloorComplianceProof(BaseModel):
    """
    Constitutional floor enforcement proof.

    F1-F13 are structural axioms, not post-processing.
    This proof shows each floor was evaluated and its result.
    """
    # Invocations
    floors_invoked: list[str] = Field(
        default_factory=list,
        description="Which F1-F13 were relevant to this decision"
    )

    # Per-floor results
    floor_results: dict[str, str] = Field(
        default_factory=dict,
        description="Per-floor result: 'PASS' | 'FAIL' | 'OVERRIDE' | 'N/A'"
    )

    # Failed floors
    failed_floors: list[str] = Field(
        default_factory=list,
        description="Floors that returned HOLD or VOID"
    )
    failed_floor_reasons: dict[str, str] = Field(
        default_factory=dict,
        description="Why each failed floor failed"
    )

    # Blocking
    blocking_floor: str | None = Field(
        default=None,
        description="Which floor caused VOID/HOLD if any"
    )

    # F13 Sovereign
    f13_invoked: bool = Field(
        default=False,
        description="Was F13 (sovereign veto) triggered?"
    )
    f13_veto_triggered: bool = Field(
        default=False,
        description="Did sovereign actually exercise veto?"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# DISSENT REASONING — STRUCTURED OPPOSING VIEW
# ═══════════════════════════════════════════════════════════════════════════════

class DissentReasoning(BaseModel):
    """
    Structured dissent: tracks opposing arguments.

    Civilization intelligence requires the AI to argue against itself.
    If there is no dissent tracked, the reasoning is shallow.
    """
    # Dissent present?
    dissent_raised: bool = Field(
        default=False,
        description="Was formal dissent raised during deliberation?"
    )

    # Dissenting position
    dissent_position: str | None = Field(
        default=None,
        description="What did the dissenting argument claim?"
    )
    dissent_strength: float = Field(
        ge=0.0, le=1.0,
        default=0.0,
        description="How compelling was the dissent (0=weak, 1=overwhelming)"
    )

    # Why dissent was overruled
    dissent_overruled: bool = Field(
        default=False,
        description="Was dissent formally overruled?"
    )
    overruling_rationale: str | None = Field(
        default=None,
        description="Why dissent was not adopted as the verdict"
    )

    # Alternative verdicts considered
    alternative_verdicts: list[str] = Field(
        default_factory=list,
        description="Other verdict options that were considered"
    )
    alternative_dismissed: list[str] = Field(
        default_factory=list,
        description="Why each alternative was dismissed"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CIVILIZATIONAL ANCHOR — PHILOSOPHY-STABILIZED REASONING
# ═══════════════════════════════════════════════════════════════════════════════

class CivilizationalAnchor(BaseModel):
    """
    Philosophy-stabilized reasoning anchor.

    Embeds structured civilizational principle to stabilize decisions.
    NOT decorative — must be relevant to the decision.
    """
    quote: str = Field(
        max_length=90,
        description="Short quote (≤90 chars) that anchors this decision"
    )
    author: str = Field(description="Who said it")
    principle: str = Field(description="Core principle being applied")
    dimension: str = Field(
        description="'entropy' | 'ethics' | 'uncertainty' | 'growth' | 'identity' | 'governance'"
    )
    stage_relevance: str = Field(
        description="Which 13-stage tool this anchor stabilizes"
    )

    # Selection justification
    selection_rationale: str | None = Field(
        default=None,
        description="Why this anchor was selected for this specific decision"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# VERDICT OUTPUT — 888_JUDGE FULL CIVILIZATION INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════════════════

class VerdictOutput(BaseModel):
    """
    Full civilization intelligence output for 888_JUDGE.

    This is where sovereign judgment crystallizes.
    Every field must affect the reasoning behavior.

    VerdictOutput is the primary output for arif_judge_deliberate.
    """
    # Standard
    status: str = "OK"
    tool: str = "arif_judge_deliberate"

    # Core verdict
    verdict: VerdictCode = Field(description="SEAL | SABAR | VOID | HOLD")
    candidate: str | None = Field(default=None, description="What was judged")

    # Reasoning result
    result: dict[str, Any] = Field(default_factory=dict)

    # ── TOAC Layer ──
    anomalous_contrast: AnomalousContrast | None = Field(
        default=None,
        description="Contrast detection for manipulation/deception identification"
    )

    # ── Thermodynamic Layer ──
    thermodynamic_state: ThermodynamicState | None = Field(
        default=None,
        description="Energy cost, entropy change, reversibility tracking"
    )

    # ── Quantum Layer ──
    decision_collapse: DecisionCollapse | None = Field(
        default=None,
        description="Prior → posterior probability collapse"
    )

    # ── Growth Layer ──
    growth_paradox: GrowthParadox | None = Field(
        default=None,
        description="Scale risk detection"
    )

    # ── AKAL Layer ──
    akal_state: AkalState | None = Field(
        default=None,
        description="Present energy awareness and system capacity"
    )

    # ── Floor Compliance ──
    floor_compliance: FloorComplianceProof = Field(
        default_factory=FloorComplianceProof,
        description="Constitutional floor enforcement proof"
    )

    # ── Amanah Genius ──
    amanah_proof: AmanahProof = Field(
        default_factory=AmanahProof,
        description="Ethical stewardship + structural elegance proof"
    )

    # ── Dissent ──
    dissent: DissentReasoning = Field(
        default_factory=DissentReasoning,
        description="Structured opposing arguments"
    )

    # ── Civilizational Anchor ──
    civilizational_anchor: CivilizationalAnchor | None = Field(
        default=None,
        description="Philosophy-stabilized reasoning anchor"
    )

    # ── Uncertainty (structured epistemic discipline) ──
    epistemic_state: UncertaintyGeometry = Field(
        default_factory=UncertaintyGeometry,
        description="Structured uncertainty geometry — not just confidence number"
    )

    judge_contract: JudgeSealContract | None = Field(
        default=None,
        description="Structured judge packet for downstream irreversible lineage checks",
    )

    # Metadata
    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: str | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# BACKWARD-COMPATIBLE ENVELOPES
# ═══════════════════════════════════════════════════════════════════════════════

class _VerdictEnvelope(BaseModel):
    status: str = "OK"
    tool: str = ""
    result: dict[str, Any] = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: str | None = None


class Verdict(_VerdictEnvelope):
    """Backward-compatible verdict envelope."""
    tool: str = "arif_judge_deliberate"


class CritiqueReport(_VerdictEnvelope):
    """Heart output envelope."""
    tool: str = "arif_heart_critique"


class SealReceipt(_VerdictEnvelope):
    """Vault output envelope."""
    tool: str = "arif_vault_seal"


class VerdictReport(Verdict):
    """Backward-compatible verdict report alias."""


# ═══════════════════════════════════════════════════════════════════════════════
# 999_VAULT — SEAL OUTPUT (IrreversibilityBond, EntropyDelta, EpistemicSnapshot)
# ═══════════════════════════════════════════════════════════════════════════════

class EntropyDelta(BaseModel):
    """Thermodynamic entropy change from this seal."""
    delta_S: float = Field(default=0.0, description="Entropy change in J/K")
    entropy_direction: str = Field(default="stable", description="'increasing' | 'stable' | 'decreasing'")
    irreversibility: bool = Field(default=False, description="Can this be reversed?")
    landauer_cost_joules: float | None = Field(default=None)


class EpistemicSnapshot(BaseModel):
    """State of knowledge at time of sealing."""
    omega_ortho: float = Field(default=0.0, ge=0.0, le=1.0, description="Orthogonal coherence")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    data_gaps: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    confidence_sources: list[str] = Field(default_factory=list)


class SealOutput(BaseModel):
    """
    Full output for arif_vault_seal (999_VAULT).

    Every field affects behavior:
    - irreversibility_bond: determines if seal is allowed
    - entropy_delta: tracks thermodynamic cost of sealing
    - epistemic_snapshot: captures knowledge state at seal time
    - ack_irreversible_required: F01 amanah enforcement

    Pillar: Thermodynamic + AKAL + Amanah Genius
    """
    status: str = "OK"
    tool: str = "arif_vault_seal"

    # Irreversibility
    irreversibility_bond: IrreversibilityBond = Field(
        default_factory=IrreversibilityBond,
        description="Thermodynamic irreversibility of this seal"
    )
    entropy_delta: EntropyDelta = Field(
        default_factory=EntropyDelta,
        description="Entropy accounting for this seal"
    )

    # Ledger entry
    result: dict[str, Any] = Field(default_factory=dict)
    entry_id: str | None = None
    ledger_size: int = 0

    # Constitutional compliance
    constitutional_compliance: ConstitutionalCompliance = Field(
        default_factory=ConstitutionalCompliance,
        description="F1-F13 floor compliance"
    )

    # Epistemic state at seal time
    epistemic_snapshot: EpistemicSnapshot = Field(
        default_factory=EpistemicSnapshot,
        description="Knowledge state when seal was made"
    )

    judge_contract: JudgeSealContract | None = Field(
        default=None,
        description="Judge packet that authorized this seal",
    )

    # Acknowledgment
    ack_irreversible_received: bool = Field(default=False)
    actor_id: str | None = None

    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: str | None = None
