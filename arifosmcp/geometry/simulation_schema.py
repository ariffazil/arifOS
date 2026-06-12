"""
simulation_schema.py — Simulation Depth: The Third Axis
═══════════════════════════════════════════════════════════════════════════════

Acemoglu gave us Inclusive vs Extractive. Calhoun gave us the third:
Simulative — institutions that perform value creation, manage perception,
and collapse when belief breaks (not when extraction provokes resistance).

This module provides the Pydantic v2 models for measuring simulation depth
in any institution, system, or agentic structure — including the kernel itself.

Three core metrics compose the SimulationIndex:
  narrative_gap    = |claimed - actual| / |claimed|       [0, 1]
  opacity_trend    = d(transparency)/dt                    [-1, 1]
  belief_integrity = P(insider_actions ≡ stated_values)    [0, 1]

Institution classes extend Acemoglu:
  INCLUSIVE   — real, broad-based value; rules apply; creative destruction
  EXTRACTIVE  — real value captured by elite; entry closed; state extracts
  SIMULATIVE  — performed value; belief-dependent; collapses on scrutiny

The novel contribution: SIMULATIVE collapse is faster and harder to detect
than extractive collapse because it depends on BELIEF, not force. When
belief breaks, there's nothing underneath.

Constitutional binding:
  F2 TRUTH:     simulation_index quantifies the gap between claim and reality
  F4 CLARITY:   higher opacity → higher simulation → warning surfaced
  F9 ANTIHANTU: narrative that is false but maintained = HANTU pattern
  F11 AUDIT:    every simulation measurement is traceable to observables
  F13 SOVEREIGN: the kernel cannot self-certify as "real" — simulation
                 detection applies to the kernel itself

Origin: EUREKA — Calhoun's Universe 25 meets Acemoglu's institutional theory.
The third axis was always there. We just didn't have the vocabulary.
DITEMPA BUKAN DIBERI — even the simulation must be measurable.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator


# ─── Institution Classification (Acemoglu + Calhoun) ──────────────────────
class InstitutionClass(StrEnum):
    """Three-axis classification of institutional reality.

    INCLUSIVE:  Power dispersed, rules apply equally, creative destruction
                works, state serves. Value creation is real and broad-based.
                Collapse rare; evolves.

    EXTRACTIVE: Power concentrated, elite captures resources, rules bent,
                entry closed, state extracts. Value creation is real but
                captured. Collapse via revolution or elite infighting.

    SIMULATIVE: Value creation is PERFORMED not real. The institution manages
                perception because the underlying reality can't survive
                scrutiny. Rules exist on paper only. Collapse via belief
                failure — fast, catastrophic, irreversible.
    """

    INCLUSIVE = "INCLUSIVE"
    EXTRACTIVE = "EXTRACTIVE"
    SIMULATIVE = "SIMULATIVE"


class SimulationVerdict(StrEnum):
    """The current state of an institution on the third axis.

    REAL:       Institution is substantially what it claims to be.
                Gap between narrative and reality is small.
    DRIFTING:   Early simulation signals. Transparency decreasing.
                Some insiders beginning to detach.
    SIMULATING: Active simulation. Narrative maintained but belief eroding.
                Insiders perform roles they no longer believe.
    HOLLOW:     Simulation fragile. Key actors know the truth.
                One unscripted question could collapse it.
    COLLAPSED:  Belief broken. Reality exposed. Institution either
                dissolved (Enron) or forcibly restructured.
    """

    REAL = "REAL"
    DRIFTING = "DRIFTING"
    SIMULATING = "SIMULATING"
    HOLLOW = "HOLLOW"
    COLLAPSED = "COLLAPSED"


# ─── Core metrics ──────────────────────────────────────────────────────────
class NarrativeGap(BaseModel):
    """The distance between what is claimed and what is observed.

    Components:
      claimed_value:  what the institution says it delivers (0-100)
      observed_value: what independent evidence shows (0-100)
      gap_ratio:      |claimed - observed| / max(claimed, 1)
      evidence_refs:  citations for observed_value (F2 TRUTH)
    """

    claimed_value: float = Field(ge=0, le=100, description="Stated/claimed value or performance")
    observed_value: float = Field(ge=0, le=100, description="Independently observed value")
    gap_ratio: float = Field(ge=0, le=1, description="Normalized gap")
    evidence_refs: list[str] = Field(default_factory=list)
    domain: str = Field(default="", description="What domain is being measured")


class OpacityTrend(BaseModel):
    """How information flow is changing over time.

    Components:
      transparency_cadence_t0: historical reporting frequency
      transparency_cadence_t1: current reporting frequency
      trend:                    negative = opacity INCREASING (simulation signal)
      disclosure_quality:       subjective but anchored in observables
      specific_change:          what exactly changed (e.g. 'quarterly→half-yearly')
    """

    transparency_cadence_t0: float = Field(
        ge=0, le=100, description="Historical transparency score"
    )
    transparency_cadence_t1: float = Field(ge=0, le=100, description="Current transparency score")
    trend: float = Field(ge=-1, le=1, description="Rate of change; negative = more opaque")
    disclosure_quality: float = Field(ge=0, le=1, description="Current disclosure quality")
    specific_change: str = Field(default="", description="What changed and when")


class BeliefIntegrity(BaseModel):
    """Do insiders still act as if the stated values are real?

    Components:
      insider_consistency: do internal actions match stated values? [0-1]
      whistleblower_presence: are people willing to surface problems? [0-1]
      dissent_tolerance: can someone say 'no' without retaliation? [0-1]
      bulldog_count: how many Rastam/Azizan types remain? (estimated)
      behavioral_transmission: are new people learning the old DNA? [0-1]

    The Calhoun signal: when belief_integrity drops below 0.3, the
    institution has entered Universe 25 Phase C. Behavioral transmission
    has died. Recovery is nearly impossible.
    """

    insider_consistency: float = Field(ge=0, le=1)
    whistleblower_presence: float = Field(ge=0, le=1)
    dissent_tolerance: float = Field(ge=0, le=1)
    bulldog_count: int = Field(ge=0, description="Estimated remaining DNA carriers")
    behavioral_transmission: float = Field(
        ge=0, le=1, description="Are new people learning old values?"
    )


# ─── Composite ─────────────────────────────────────────────────────────────
class SimulationDepth(BaseModel):
    """The unified simulation measurement.

    simulation_index = weighted average of narrative_gap, opacity, belief_decay.
    Weights are F13-ratified. The kernel does not learn them at runtime.

    Bands:
      0.00-0.25: REAL        — institution is substantially genuine
      0.25-0.50: DRIFTING    — early warning signals
      0.50-0.75: SIMULATING  — active perception management
      0.75-0.90: HOLLOW      — belief dying, one shock away
      0.90-1.00: COLLAPSED   — reality exposed, institution dissolved
    """

    narrative_gap: NarrativeGap
    opacity_trend: OpacityTrend
    belief_integrity: BeliefIntegrity

    simulation_index: float = Field(
        default=0.0, ge=0, le=1, description="Composite 0=real, 1=fully simulated"
    )
    institution_class: InstitutionClass = InstitutionClass.SIMULATIVE
    simulation_verdict: SimulationVerdict = SimulationVerdict.REAL

    # Analysis metadata
    institution_name: str = ""
    analysis_date: str = ""
    confidence: float = Field(ge=0, le=1, default=0.5)
    evidence_strength: str = Field(
        default="HYPOTHESIS", description="CLAIM | PLAUSIBLE | HYPOTHESIS | ESTIMATE"
    )

    @model_validator(mode="after")
    def _compute_index(self) -> SimulationDepth:
        """Auto-compute simulation_index from components."""
        gap = self.narrative_gap.gap_ratio
        opacity = max(0, -self.opacity_trend.trend)  # positive = increasing opacity
        belief_decay = 1.0 - (
            self.belief_integrity.insider_consistency * 0.30
            + self.belief_integrity.whistleblower_presence * 0.20
            + self.belief_integrity.dissent_tolerance * 0.20
            + min(self.belief_integrity.bulldog_count / 10.0, 1.0) * 0.15
            + self.belief_integrity.behavioral_transmission * 0.15
        )

        # Weighted composite: narrative gap is the strongest signal
        self.simulation_index = round(0.40 * gap + 0.30 * opacity + 0.30 * belief_decay, 4)

        # Classify
        si = self.simulation_index
        if si < 0.25:
            self.simulation_verdict = SimulationVerdict.REAL
        elif si < 0.50:
            self.simulation_verdict = SimulationVerdict.DRIFTING
        elif si < 0.75:
            self.simulation_verdict = SimulationVerdict.SIMULATING
        elif si < 0.90:
            self.simulation_verdict = SimulationVerdict.HOLLOW
        else:
            self.simulation_verdict = SimulationVerdict.COLLAPSED

        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "institution_name": self.institution_name,
            "simulation_index": self.simulation_index,
            "institution_class": self.institution_class.value,
            "simulation_verdict": self.simulation_verdict.value,
            "narrative_gap": self.narrative_gap.model_dump(),
            "opacity_trend": self.opacity_trend.model_dump(),
            "belief_integrity": self.belief_integrity.model_dump(),
            "confidence": self.confidence,
            "evidence_strength": self.evidence_strength,
        }

    @property
    def is_simulative(self) -> bool:
        return self.simulation_index >= 0.25

    @property
    def is_hollow(self) -> bool:
        return self.simulation_index >= 0.75

    @property
    def calhoun_phase(self) -> str:
        """Map simulation_index to Calhoun's Universe 25 phases."""
        si = self.simulation_index
        if si < 0.25:
            return "Phase A — Thriving"
        if si < 0.50:
            return "Phase B — The Beautiful Ones emerging"
        if si < 0.75:
            return "Phase C — Behavioral death"
        return "Phase D — Extinction"


# ─── Self-Simulation Guard (kernel self-test) ──────────────────────────────
class SelfSimulationGuard(BaseModel):
    """The kernel must measure its OWN simulation depth.

    If the kernel performs governance that isn't real — if it issues SEAL
    verdicts that don't correspond to actual state changes, if it maintains
    the appearance of floor enforcement without actual enforcement — it
    has become the thing it was built to detect.

    This guard runs periodically. If the kernel's own simulation_index
    exceeds 0.50, it must ISSUE A HOLD ON ITSELF and escalate to F13.
    """

    kernel_claims: list[str] = Field(
        default_factory=list, description="What the kernel claims to do"
    )
    kernel_observed: list[str] = Field(
        default_factory=list, description="What the kernel actually does"
    )
    self_simulation_index: float = Field(ge=0, le=1, default=0.0)
    last_self_check: str = ""
    hold_required: bool = False

    @model_validator(mode="after")
    def _check_self(self) -> SelfSimulationGuard:
        """If the kernel is simulating, it must HOLD itself."""
        if self.self_simulation_index >= 0.50:
            self.hold_required = True
        return self


__all__ = [
    "InstitutionClass",
    "SimulationVerdict",
    "NarrativeGap",
    "OpacityTrend",
    "BeliefIntegrity",
    "SimulationDepth",
    "SelfSimulationGuard",
]
