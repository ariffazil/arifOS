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

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from arifosmcp.schemas.cognition import UncertaintyGeometry
from arifosmcp.schemas.forge import ConstitutionalCompliance, IrreversibilityBond
from arifosmcp.schemas.lineage import JudgeSealContract

# ═══════════════════════════════════════════════════════════════════════════════
# VERDICT CODES
# ═══════════════════════════════════════════════════════════════════════════════


class VerdictCode(StrEnum):
    SEAL = "SEAL"  # Approved — proceed
    SABAR = "SABAR"  # Wait — under review
    VOID = "VOID"  # Rejected — constitutional breach
    HOLD = "HOLD"  # Paused — manual review required
    PARADOX_HOLD = "PARADOX_HOLD"  # Two truths conflict — both verified, both preserved


# ═══════════════════════════════════════════════════════════════════════════════
# TOAC — THEORY OF ANOMALOUS CONTRAST
# ═══════════════════════════════════════════════════════════════════════════════


class AnomalousContrast(BaseModel):
    """
    Detects contrast between expected vs observed, claimed vs verified.

    ToAC Principle: Intelligence = ability to detect and resolve contrast.

    Core equation: AC_Risk = U_phys × D_transform × B_cog
      U_phys ∈ [0,1] — Physical model uncertainty
      D_transform ∈ [1,3] — Processing chain distortion
      B_cog ∈ [0,1] — Cognitive bias exposure

    Verdict thresholds:
      < 0.15 → SEAL
      0.15–0.34 → SABAR
      0.35–0.59 → HOLD
      ≥ 0.60 → VOID

    Embeds in: 333_MIND, 888_JUDGE, 999_VAULT
    """

    # Baseline expectation
    baseline_model: str = Field(description="What the system expected before evidence")

    # What actually happened
    observed_deviation: str = Field(description="How reality diverged from expectation")

    # ── ToAC component factors ───────────────────────────────────────
    u_phys: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="AC_Risk factor: Physical model uncertainty (0=perfect model, 1=no model)",
    )
    d_transform: float = Field(
        default=1.0,
        ge=1.0,
        le=3.0,
        description="AC_Risk factor: Processing chain distortion (1=direct, 3=highly transformed)",
    )
    b_cog: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="AC_Risk factor: Cognitive bias exposure (0=none, 1=max bias)",
    )

    # ── Computed AC_Risk (via model_validator) ──────────────────────
    magnitude: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
        description="AC_Risk = U_phys × D_transform × B_cog (computed via model_validator)",
    )

    # Confidence in detection
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence that deviation is real, not noise"
    )

    # Contrast type classification
    contrast_type: Literal[
        "expected_vs_observed",
        "claimed_vs_verified",
        "shortterm_vs_entropy",
        "local_vs_civilizational",
    ] = Field(description="Canonical contrast classification")

    # ── model_validator: compute AC_Risk = U_phys × D_transform × B_cog ──
    @model_validator(mode="after")
    def compute_ac_risk(self) -> AnomalousContrast:
        """Compute AC_Risk from component factors and set magnitude."""
        self.magnitude = round(self.u_phys * self.d_transform * self.b_cog / 3.0, 4)
        # Bound to [0, 1] — D_transform ∈ [1,3] so raw product can exceed 1
        self.magnitude = min(self.magnitude, 1.0)
        return self

    @property
    def ac_risk_verdict(self) -> str:
        """Return the verdict band for the current AC_Risk magnitude."""
        if self.magnitude < 0.15:
            return "SEAL"
        elif self.magnitude < 0.35:
            return "SABAR"
        elif self.magnitude < 0.60:
            return "HOLD"
        return "VOID"

    # Resolution
    resolution_strategy: str | None = Field(
        default=None, description="How the system resolved the contrast"
    )
    resolution_confidence: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Confidence in resolution strategy"
    )

    # Manipulation detection
    manipulation_signal: bool = Field(
        default=False,
        description="Does contrast suggest intentional manipulation (L09)?",
    )
    anti_hantu_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Likelihood of hantu (manipulation) detected",
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
        default=None, description="Estimated energy cost in joules"
    )

    # Entropy change
    delta_s: float = Field(  # N815: snake_case
        default=0.0, description="Entropy change from this action (positive = disorder)"
    )

    # Direction
    entropy_direction: Literal["increasing", "decreasing", "stable", "unknown"] = Field(
        default="unknown",
        description="Canonical entropy direction",
    )

    # Reversibility
    irreversibility: bool = Field(
        default=False, description="Is this action thermodynamically irreversible?"
    )
    reversibility_cost: float | None = Field(
        default=None, description="Energy cost to reverse (if reversible)"
    )
    reversal_window_seconds: float | None = Field(
        default=None, description="Time window for safe reversal (if applicable)"
    )

    # Landauer compliance
    landauer_cost_ev: float | None = Field(  # N815: snake_case
        default=None,
        description="Minimum thermodynamic cost (kT * ln 2) in electron volts",
    )

    # Quantum layer indicator
    decision_collapse_triggered: bool = Field(
        default=False,
        description="Did probabilistic state collapse occur at decision point?",
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
        description=(
            "Probability distribution before decision "
            "(e.g., {'SEAL': 0.3, 'SABAR': 0.5, 'VOID': 0.2})"
        ),
    )

    # Posterior state
    posterior_distribution: dict[str, float] = Field(
        default_factory=dict, description="Probability distribution after decision"
    )

    # Collapse mechanism
    collapse_trigger: Literal["threshold", "evidence", "override", "timeout"] = Field(
        description="What triggered the decision collapse"
    )

    # Post-collapse
    residual_uncertainty: float = Field(
        ge=0.0,
        le=1.0,
        description="Uncertainty remaining after collapse (0=certain, 1=maximum)",
    )

    # Confidence shift
    confidence_shift: float = Field(
        default=0.0, description="Change in confidence from prior to posterior"
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
        default=1.0, ge=0.0, description="Growth multiplier (1.0 = no growth, 2.0 = 2x)"
    )

    # Stability
    stability_margin: float = Field(
        ge=0.0,
        le=1.0,
        description="Margin before instability (0=no margin, 1=maximum margin)",
    )

    # Systemic risk
    systemic_risk: float = Field(
        ge=0.0,
        le=1.0,
        description="Likelihood that scaling creates system-wide instability",
    )

    # Fragility
    fragility_index: float = Field(
        ge=0.0,
        le=1.0,
        description="Structural fragility under scaling (0=robust, 1=brittle)",
    )

    # Paradox detection
    paradox_detected: bool = Field(
        default=False, description="Is growth paradox active (scaling > stability)?"
    )
    paradox_mitigation: str | None = Field(
        default=None, description="Strategy to resolve paradox if detected"
    )

    # Efficiency vs fragility
    efficiency_fragility_tradeoff: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Balance: 0=maximum efficiency, 1=maximum stability",
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
        ge=0.0, description="Available cognitive energy now (arbitrary units)"
    )
    present_energy_ratio: float = Field(
        ge=0.0, le=1.0, description="Energy as ratio of maximum capacity"
    )

    # Cognitive load
    cognitive_load: float = Field(
        ge=0.0,
        le=1.0,
        description="Current load as ratio of capacity (0=idle, 1=fully loaded)",
    )

    # System capacity
    system_capacity: float = Field(description="Maximum cognitive capacity available")
    capacity_utilized: float = Field(
        ge=0.0, le=1.0, description="Percentage of capacity currently in use"
    )

    # Alignment state
    alignment_state: str = Field(
        default="stable", description="'stable' | 'strained' | 'critical' | 'overload'"
    )

    # Energy trajectory
    energy_trend: str = Field(
        default="stable",
        description="'increasing' | 'stable' | 'decreasing' | 'depleted'",
    )
    projected_depletion_seconds: float | None = Field(
        default=None,
        description="Estimated seconds until energy depletion (if decreasing)",
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
        default_factory=list, description="F1-L13 floors evaluated for this action"
    )
    floors_passed: list[str] = Field(default_factory=list, description="Floors that passed")
    floors_failed: list[str] = Field(
        default_factory=list, description="Floors that blocked or required override"
    )

    # Violations
    violations: list[str] = Field(
        default_factory=list, description="Specific floor breaches detected"
    )
    violation_mitigation: list[str] = Field(
        default_factory=list,
        description="How each violation was addressed or acknowledged",
    )

    # Override
    override_acknowledged: bool = Field(
        default=False, description="Did sovereign (L13) override any floor?"
    )
    override_reason: str | None = Field(default=None, description="Why sovereign chose to override")
    override_authorizer: str | None = Field(
        default=None, description="Who authorized the override (must be sovereign)"
    )

    # Genius score
    genius_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Structural elegance: 0=brute force, 1=minimal path with maximum effect",
    )
    genius_rationale: str | None = Field(
        default=None, description="Why this is the genius (elegant) path"
    )

    # Minimal entropy path
    entropy_minimal: bool = Field(
        default=True,
        description="Is this the minimum entropy path to achieve the goal?",
    )
    entropy_alternatives_considered: int = Field(
        default=0,
        ge=0,
        description="How many alternative paths were evaluated for entropy comparison",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# FLOOR COMPLIANCE PROOF
# ═══════════════════════════════════════════════════════════════════════════════


class FloorComplianceProof(BaseModel):
    """
    Constitutional floor enforcement proof.

    F1-L13 are structural axioms, not post-processing.
    This proof shows each floor was evaluated and its result.
    """

    # Invocations
    floors_invoked: list[str] = Field(
        default_factory=list, description="Which F1-L13 were relevant to this decision"
    )

    # Per-floor results
    law_results: dict[str, str] = Field(
        default_factory=dict,
        description="Per-floor result: 'PASS' | 'FAIL' | 'OVERRIDE' | 'N/A'",
    )

    # Failed floors
    violated_laws: list[str] = Field(
        default_factory=list, description="Floors that returned HOLD or VOID"
    )
    failed_floor_reasons: dict[str, str] = Field(
        default_factory=dict, description="Why each failed floor failed"
    )

    # Blocking
    blocking_floor: str | None = Field(
        default=None, description="Which floor caused VOID/HOLD if any"
    )

    # L13 Sovereign
    f13_invoked: bool = Field(default=False, description="Was L13 (sovereign veto) triggered?")
    f13_veto_triggered: bool = Field(
        default=False, description="Did sovereign actually exercise veto?"
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
        default=False, description="Was formal dissent raised during deliberation?"
    )

    # Dissenting position
    dissent_position: str | None = Field(
        default=None, description="What did the dissenting argument claim?"
    )
    dissent_strength: float = Field(
        ge=0.0,
        le=1.0,
        default=0.0,
        description="How compelling was the dissent (0=weak, 1=overwhelming)",
    )

    # Why dissent was overruled
    dissent_overruled: bool = Field(default=False, description="Was dissent formally overruled?")
    overruling_rationale: str | None = Field(
        default=None, description="Why dissent was not adopted as the verdict"
    )

    # Alternative verdicts considered
    alternative_verdicts: list[str] = Field(
        default_factory=list, description="Other verdict options that were considered"
    )
    alternative_dismissed: list[str] = Field(
        default_factory=list, description="Why each alternative was dismissed"
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
        max_length=90, description="Short quote (≤90 chars) that anchors this decision"
    )
    author: str = Field(description="Who said it")
    principle: str = Field(description="Core principle being applied")
    dimension: str = Field(
        description="'entropy' | 'ethics' | 'uncertainty' | 'growth' | 'identity' | 'governance'"
    )
    stage_relevance: str = Field(description="Which 13-stage tool this anchor stabilizes")

    # Selection justification
    selection_rationale: str | None = Field(
        default=None,
        description="Why this anchor was selected for this specific decision",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# DEGRADED MODE — RUNTIME DEGRADE STATES
# ═══════════════════════════════════════════════════════════════════════════════


class DegradedMode(StrEnum):
    """Runtime degradation state when policy or approval is unavailable."""

    FULL = "full"  # Normal operation
    OBSERVE_ONLY = "observe_only"  # Downshifted to read-only
    DENY = "deny"  # Default deny — all mutations blocked
    CIRCUIT_OPEN = "circuit_open"  # Circuit breaker tripped


class CircuitBreaker(BaseModel):
    """Circuit breaker state for fault-tolerant degradation."""

    open: bool = Field(default=False, description="Is the circuit open?")
    reason: str | None = Field(default=None, description="Why the circuit opened")
    half_open_attempts: int = Field(default=0, ge=0, description="Attempts made in half-open state")
    last_failure: str | None = Field(
        default=None, description="Timestamp or reason of last failure"
    )
    consecutive_failures: int = Field(default=0, ge=0, description="Failures before circuit opened")


# ═══════════════════════════════════════════════════════════════════════════════
# APPROVAL REQUIRED — DURABLE APPROVAL OBJECT
# ═══════════════════════════════════════════════════════════════════════════════


class ApprovalRequired(BaseModel):
    """
    Durable approval object for high-impact actions.

    NOT an ad-hoc UI prompt — this is a structured, traceable, expirable
    approval record that links to evidence and can be replayed.
    """

    subject: str = Field(description="Who or what needs approval")
    action: str = Field(description="What action is being requested")
    scope: list[str] = Field(default_factory=list, description="Scoped boundaries of the action")
    expires_at: datetime | None = Field(default=None, description="When this approval expires")
    evidence_link: str | None = Field(
        default=None, description="Link to evidence that triggered the approval request"
    )
    resolution_status: str = Field(
        default="pending",
        description="pending | approved | declined | modified | expired | superseded",
    )
    resolved_by: str | None = Field(default=None, description="Who resolved the approval")
    resolution_reason: str | None = Field(default=None, description="Why it was resolved this way")
    resolution_timestamp: datetime | None = Field(default=None, description="When it was resolved")


# ═══════════════════════════════════════════════════════════════════════════════
# VERDICT OUTPUT — 888_JUDGE FULL CIVILIZATION INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════════════════


class VerdictOutput(BaseModel):
    """
    Full civilization intelligence output for 888_JUDGE.

    This is where sovereign judgment crystallizes.
    Every field must affect the reasoning behavior.

    VerdictOutput is the primary output for arif_judge.
    """

    # Standard
    status: str = "OK"
    tool: str = "arif_judge"

    # Core verdict
    verdict: VerdictCode = Field(description="SEAL | SABAR | VOID | HOLD")
    candidate: str | None = Field(default=None, description="What was judged")

    # Reasoning result
    result: dict[str, Any] = Field(default_factory=dict)

    # Nine-Signal compliance (F2 addendum)
    reasons: list[str] = Field(
        default_factory=list,
        description="Constitutional rationale for the verdict",
    )
    next_safe_action: str | None = Field(
        default=None,
        description="Recommended next step to resolve a HOLD or SABAR",
    )

    # ── TOAC Layer ──
    anomalous_contrast: AnomalousContrast | None = Field(
        default=None,
        description="Contrast detection for manipulation/deception identification",
    )

    # ── Thermodynamic Layer ──
    thermodynamic_state: ThermodynamicState | None = Field(
        default=None, description="Energy cost, entropy change, reversibility tracking"
    )

    # ── Quantum Layer ──
    decision_collapse: DecisionCollapse | None = Field(
        default=None, description="Prior → posterior probability collapse"
    )

    # ── Growth Layer ──
    growth_paradox: GrowthParadox | None = Field(default=None, description="Scale risk detection")

    # ── AKAL Layer ──
    akal_state: AkalState | None = Field(
        default=None, description="Present energy awareness and system capacity"
    )

    # ── Floor Compliance ──
    floor_compliance: FloorComplianceProof = Field(
        default_factory=FloorComplianceProof,
        description="Constitutional floor enforcement proof",
    )

    # ── Amanah Genius ──
    amanah_proof: AmanahProof = Field(
        default_factory=AmanahProof,
        description="Ethical stewardship + structural elegance proof",
    )

    # ── Dissent ──
    dissent: DissentReasoning = Field(
        default_factory=DissentReasoning, description="Structured opposing arguments"
    )

    # ── Civilizational Anchor ──
    civilizational_anchor: CivilizationalAnchor | None = Field(
        default=None, description="Philosophy-stabilized reasoning anchor"
    )

    # ── Uncertainty (structured epistemic discipline) ──
    epistemic_state: UncertaintyGeometry = Field(
        default_factory=UncertaintyGeometry,
        description="Structured uncertainty geometry — not just confidence number",
    )

    judge_contract: JudgeSealContract | None = Field(
        default=None,
        description="Structured judge packet for downstream irreversible lineage checks",
    )

    # ── Post-AGI WEALTH verification governance (Phase 2) ─────────────────────
    # F2 truth declaration and confidence note — propagated from WealthGovernance
    # at judgment time. Not optional: every SEAL/HOLD/VOID must declare its band.
    truth_band: str | None = Field(
        default=None,
        description="F2 truth: CERTAIN | HIGH_CONF | PLAUSIBLE | SPECULATIVE | UNKNOWN",
    )
    confidence_note: str | None = Field(
        default=None,
        description="F2 human-readable confidence declaration at judgment time",
    )

    # ── Reversibility State (CRP v1.0) ──────────────────────────────────────
    reversibility_state: dict[str, Any] = Field(
        default_factory=lambda: {
            "state": "REVERSIBLE",
            "requires_human_seal": False,
            "external_effect": False,
            "vault_committed": False,
        },
        description="Structured reversibility tracking per CRP v1.0",
    )

    # ── Seal State ──────────────────────────────────────────────────────────
    seal_state: dict[str, Any] = Field(
        default_factory=lambda: {
            "semantic_seal": False,
            "procedural_seal": False,
            "cryptographic_seal": False,
            "vault_committed": False,
            "human_approved": False,
        },
        description="Explicit seal semantics for the judgment",
    )

    # Metadata
    meta: dict[str, Any] = Field(default_factory=dict)

    # ── F-WEB Evidence Sufficiency (Blueprint §9) ─────────────────────────────
    # Deterministic max evidence level computed from receipt fields — NOT LLM-claimed
    max_evidence_level: str | None = Field(
        default=None,
        description="L0–L5. Deterministically computed from evidence receipt fields.",
    )
    sufficiency_verdict: str | None = Field(
        default=None,
        description="SEAL | HOLD | VOID. Result of comparing claimed vs max level.",
    )
    sufficiency_reason: str | None = Field(
        default=None,
        description="Human-readable reason when sufficiency check fails.",
    )
    injection_detected: bool = Field(
        default=False,
        description="True if indirect prompt injection detected in evidence.",
    )
    invariants_checked: list[str] = Field(
        default_factory=list,
        description=(
            "List of constitutional invariants tested during this verdict "
            "(e.g., L01_reversibility, L11_identity, L13_sovereign). "
            "Proves WHY the verdict was reached, not just WHAT."
        ),
    )

    # ── Sovereignty Boundary (Eureka 8 — from metabolize internal) ──────────────────
    # AI proposes. Tools compute. Memory records. Constraints guard. Arif judges.
    # These flags are set TRUE only when Arif has ratified the action.
    recommendation_only: bool = Field(
        default=True,
        description="AI proposes only. Has not been ratified by human. True until L13 sign-off.",
    )
    execution_authorized: bool = Field(
        default=False,
        description="Has a human authorized execution? False until L13 SOVEREIGN sign-off.",
    )
    human_final_authority: str = Field(
        default="Arif",
        description="Who has final say on this verdict? Always 'Arif' — L13 veto is absolute.",
    )
    requires_888_judge: bool = Field(
        default=False,
        description="Does this candidate require 888_JUDGE re-review before action?",
    )

    # ── v3.1 Degrade Modes (ChatGPT Deep Research integration) ──────────────
    # If policy decision is unavailable → default deny.
    # If approval service is unavailable → downshift actionable tools to observe-only.
    # If model/tool registry lacks valid attestation → refuse activation.
    degraded_mode: DegradedMode = Field(
        default=DegradedMode.FULL,
        description="Runtime degradation state: full | observe_only | deny | circuit_open",
    )
    circuit_breaker: CircuitBreaker = Field(
        default_factory=CircuitBreaker,
        description="Circuit breaker state for fault-tolerant degradation",
    )

    # ── v3.1 Durable Approval Object (ChatGPT Deep Research integration) ────
    # Structured approval record with subject, action, scope, expiration,
    # evidence link, and resolution status. Replaces ad-hoc UI prompts.
    approval_required: ApprovalRequired | None = Field(
        default=None,
        description="Durable approval object if the verdict requires human sign-off",
    )

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

    tool: str = "arif_judge"


class CritiqueReport(_VerdictEnvelope):
    """Heart output envelope."""

    tool: str = "arif_critique"


class SealReceipt(_VerdictEnvelope):
    """Vault output envelope."""

    tool: str = "arif_seal"


class VerdictReport(Verdict):
    """Backward-compatible verdict report alias."""


# ═══════════════════════════════════════════════════════════════════════════════
# 999_VAULT — SEAL OUTPUT (IrreversibilityBond, EntropyDelta, EpistemicSnapshot)
# ═══════════════════════════════════════════════════════════════════════════════


class EntropyDelta(BaseModel):
    """Thermodynamic entropy change from this seal."""

    delta_s: float = Field(default=0.0, description="Entropy change in J/K")  # N815
    entropy_direction: Literal["increasing", "stable", "decreasing"] = Field(
        default="stable", description="Canonical entropy direction for seal"
    )
    irreversibility: bool = Field(default=False, description="Can this be reversed?")
    landauer_cost_joules: float | None = Field(default=None)


class EpistemicSnapshot(BaseModel):
    """State of knowledge at time of sealing."""

    omega_ortho: float = Field(default=0.0, ge=0.0, le=1.0, description="Orthogonal coherence")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    data_gaps: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    confidence_sources: list[str] = Field(default_factory=list)


class AttributionLink(BaseModel):
    """A single link in the attribution chain."""

    source_seal_hash: str  # SHA-256 of the prior seal being cited
    source_agent: str  # e.g. "geox", "wealth", "omega-forge-agent"
    source_session_id: str
    citation_type: Literal["EVIDENCE", "DECISION", "METHOD", "DATA"]
    cited_at: datetime = Field(default_factory=datetime.utcnow)


class AttributionChain(BaseModel):
    """Full provenance chain for a sealed verdict."""

    links: list[AttributionLink] = Field(default_factory=list)
    chain_integrity: Literal["INTACT", "UNCONFORMITY_DETECTED", "UNVERIFIED"] = "UNVERIFIED"
    unconformity_at: int | None = None  # index where chain broke
    unconformity_reason: str | None = None

    @model_validator(mode="after")
    def detect_unconformity(self) -> AttributionChain:
        """Scan chain for missing links — geological unconformity detection."""
        if not self.links:
            self.chain_integrity = "UNVERIFIED"
            return self
        for i, link in enumerate(self.links):
            if not link.source_seal_hash:
                self.chain_integrity = "UNCONFORMITY_DETECTED"
                self.unconformity_at = i
                self.unconformity_reason = (
                    f"Missing seal hash at link {i} ({link.citation_type} from {link.source_agent})"
                )
                return self
        self.chain_integrity = "INTACT"
        return self


class SealOutput(BaseModel):
    """
    Full output for arif_seal (999_VAULT).

    Every field affects behavior:
    - irreversibility_bond: determines if seal is allowed
    - entropy_delta: tracks thermodynamic cost of sealing
    - epistemic_snapshot: captures knowledge state at seal time
    - ack_irreversible_required: L01 amanah enforcement

    Pillar: Thermodynamic + AKAL + Amanah Genius
    """

    status: str = "OK"
    tool: str = "arif_seal"

    # Core verdict
    verdict: VerdictCode = Field(default=VerdictCode.SEAL)

    # Nine-Signal compliance (F2 addendum)
    reasons: list[str] = Field(
        default_factory=list,
        description="Constitutional rationale for the seal status",
    )
    next_safe_action: str | None = Field(
        default=None,
        description="Recommended next step to resolve a HOLD",
    )

    # Irreversibility
    irreversibility_bond: IrreversibilityBond = Field(
        default_factory=IrreversibilityBond,
        description="Thermodynamic irreversibility of this seal",
    )
    entropy_delta: EntropyDelta = Field(
        default_factory=EntropyDelta, description="Entropy accounting for this seal"
    )

    # Ledger entry
    result: dict[str, Any] = Field(default_factory=dict)
    entry_id: str | None = None
    ledger_size: int = 0
    chain_hash: str | None = None
    permanence_flag: bool = False

    # Constitutional compliance
    constitutional_compliance: ConstitutionalCompliance = Field(
        default_factory=ConstitutionalCompliance, description="F1-L13 floor compliance"
    )

    # Epistemic state at seal time
    epistemic_snapshot: EpistemicSnapshot = Field(
        default_factory=EpistemicSnapshot,
        description="Knowledge state when seal was made",
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
    mode: str | None = None
    seal_data: dict[str, Any] | None = None

    # ── Post-AGI WEALTH verification governance (Phase 2) ─────────────────────
    # Captured at decision time, stored in ledger for drift analysis / post-mortems
    delta_m: float | None = Field(
        default=None,
        description=(
            "Measurability Gap: share of tasks AI can execute minus share humans can verify"
        ),
    )
    svs: float | None = Field(
        default=None,
        description=(
            "Safe Verifiable Share: fraction of AI output safely underwritable at acceptable cost"
        ),
    )
    entropy_band: Literal["LOW", "MEDIUM", "HIGH", "EXTREME"] | None = Field(
        default=None,
        description="Entropy classification at seal time",
    )
    liability_owner: str | None = Field(
        default=None,
        description="Human or institution who bears downside accountability — no owner = no SEAL",
    )
    verification_bottlenecks: list[str] = Field(
        default_factory=list,
        description="Top verification bottlenecks at decision time",
    )
    wealth_final_score: float | None = Field(
        default=None,
        description="WEALTH constitutional score: multi-axis reward/risk/verifiability composite",
    )
    wealth_recommendation: Literal["SEAL_CANDIDATE", "HOLD_CANDIDATE", "VOID_CANDIDATE"] | None = (
        Field(
            default=None,
            description="WEALTH score recommendation",
        )
    )
    truth_band: Literal["CERTAIN", "HIGH_CONF", "PLAUSIBLE", "SPECULATIVE", "UNKNOWN"] | None = (
        Field(
            default=None,
            description="F2 truth band at seal time",
        )
    )
    confidence_note: str | None = Field(
        default=None,
        description="F2 human-readable confidence declaration at seal time",
    )

    # ── Constitutional Doctrine (F9 Anti-Hallucination: witness, not authority) ──
    # This field is a CODED CONSTANT. It is never LLM-generated.
    # The motto is proof-of-origin, not proof-of-truth.
    # It does NOT affect verdict, status, floor pass/fail, or execution.
    doctrine: dict | None = Field(
        default=None,
        description="arifOS constitutional doctrine motto. "
        "seal_motto: fixed coded string. "
        "llm_generated: always false. "
        "source: 'arifOS constitutional doctrine'. "
        "Authority remains with the constitution and human sovereign.",
    )

    # ── EUREKA 2: Attribution Chain (Geological Unconformity Detector) ─────────
    attribution_chain: AttributionChain | None = Field(
        default=None,
        description="Provenance chain for this seal. "
        "UNCONFORMITY_DETECTED means a cited source has no traceable origin "
        "— the geological equivalent of a missing layer in the stratigraphic column. "
        "Named after Arif's Layang-Layang scar: work existed, truth was correct, "
        "but attribution was erased.",
    )
