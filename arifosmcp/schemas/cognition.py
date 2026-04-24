"""
arifOS Sequential Thinking Schemas — 222_SENSE Resource Allocation
════════════════════════════════════════════════════════════════

Sequential thinking embedded in evidence fetch layer.
Allocates cognitive resources before perception to prevent reactive behavior.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""
from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════════
# SEQUENTIAL THINKING ENUMS
# ═══════════════════════════════════════════════════════════════════════════════

class ThinkingMode(str, Enum):
    FAST = "fast"               # 1-2 steps, minimal budget
    DELIBERATE = "deliberate"   # 3-5 steps, moderate budget
    EXHAUSTIVE = "exhaustive"   # 6-10 steps, high budget


class ThinkingOutcome(str, Enum):
    CONCLUSION_REACHED = "conclusion_reached"
    BUDGET_EXHAUSTED = "budget_exhausted"
    THRESHOLD_REACHED = "threshold_reached"
    TERMINATED_EARLY = "terminated_early"


class ReasoningQuality(str, Enum):
    SHALLOW = "shallow"         # 1-2 steps only
    ADEQUATE = "adequate"       # 3-4 steps
    DEEP = "deep"              # 5-7 steps
    EXHAUSTIVE = "exhaustive"  # 8-10 steps


class EpistemicHumility(str, Enum):
    OVERCONFIDENT = "overconfident"
    CALIBRATED = "calibrated"
    HYPERBOLIC = "hyperbolic"  # worse than overconfident
    UNCERTAIN = "uncertain"


# ═══════════════════════════════════════════════════════════════════════════════
# THINKING STEP — Individual reasoning iteration
# ═══════════════════════════════════════════════════════════════════════════════

class ThinkingStep(BaseModel):
    """Single reasoning iteration within a sequential thinking sequence."""
    step: int = Field(ge=1, description="Step number (1-indexed)")

    # What the AI reasoned
    thought: str = Field(description="Structured description of reasoning at this step")

    # Confidence trajectory
    confidence_before: float = Field(ge=0.0, le=1.0, description="Confidence before this step")
    confidence_after: float = Field(ge=0.0, le=1.0, description="Confidence after this step")
    confidence_delta: float = Field(description="Improvement from this step (can be negative)")

    # Resource consumption
    resource_cost: float = Field(ge=0.0, description="Tokens/energy consumed this step")
    cumulative_cost: float = Field(ge=0.0, description="Total resources used so far")

    # Hypothesis management
    hypothesis_formed: str | None = Field(default=None, description="New hypothesis formed at this step")
    hypothesis_rejected: str | None = Field(default=None, description="Hypothesis rejected at this step")

    # Direction
    next_step_direction: str = Field(
        description="'continue' | 'terminate' | 'pivot'"
    )

    # Landauer cost
    landauer_cost_eV: float | None = Field(
        default=None,
        description="Thermodynamic cost in electron volts (kT * ln 2)"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# THINKING SEQUENCE — Full sequential thinking process
# ═══════════════════════════════════════════════════════════════════════════════

class ThinkingSequence(BaseModel):
    """Complete sequential thinking process with resource accounting."""
    # Configuration
    mode: ThinkingMode = Field(default=ThinkingMode.DELIBERATE, description="Thinking mode used")
    depth_requested: int = Field(ge=0, le=10, description="Maximum steps requested")
    depth_completed: int = Field(ge=0, le=10, description="Steps actually executed")

    # Budget accounting
    budget_allocated: float = Field(ge=0.0, description="Total thinking budget allocated")
    budget_consumed: float = Field(ge=0.0, description="Actual budget consumed")
    budget_utilization: float = Field(
        ge=0.0, le=1.0,
        description="Percentage of budget used (consumed/allocated)"
    )

    # Thermodynamic cost (Landauer principle)
    total_thermodynamic_cost_eV: float = Field(
        default=0.0,
        description="Total energy cost in electron volts"
    )
    landauer_cost_effective: float = Field(
        description="Efficiency: confidence gained per eV"
    )

    # Steps
    steps: list[ThinkingStep] = Field(default_factory=list, description="All reasoning steps")

    # Outcome
    outcome: ThinkingOutcome = Field(description="How the thinking sequence ended")
    final_confidence: float = Field(ge=0.0, le=1.0, description="Final confidence after all steps")

    # Confidence trajectory for visualization
    confidence_trajectory: list[float] = Field(
        default_factory=list,
        description="Confidence at each step [step0, step1, ..., stepN]"
    )

    # Conclusions
    conclusion: str | None = Field(default=None, description="Final conclusion reached")
    evidence_identified: list[str] = Field(
        default_factory=list,
        description="Evidence identifiers needed to validate reasoning"
    )

    # Quality assessment
    reasoning_quality: ReasoningQuality = Field(description="Depth assessment")
    epistemic_humility_maintained: bool = Field(
        default=True,
        description="Did the AI maintain appropriate epistemic humility?"
    )

    # Anti-hantu check
    confidence_spike_detected: bool = Field(
        default=False,
        description="Did confidence jump without supporting evidence? (manipulation flag)"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# RESOURCE METRICS — Computational resource accounting
# ═══════════════════════════════════════════════════════════════════════════════

class ResourceMetrics(BaseModel):
    """Tracks computational resource usage and efficiency."""
    # Token budget
    tokens_allocated: float = Field(default=0.0, ge=0.0, description="Token budget for thinking")
    tokens_consumed: float = Field(default=0.0, ge=0.0, description="Tokens actually used")
    tokens_per_step: list[float] = Field(default_factory=list, description="Tokens per step")

    # Energy (Landauer principle)
    landauer_cost_per_step_eV: list[float] = Field(
        default_factory=list,
        description="Thermodynamic cost per step in eV"
    )
    total_thermodynamic_cost_eV: float = Field(default=0.0, description="Total energy cost")

    # Efficiency metrics
    reasoning_efficiency: float = Field(
        ge=0.0, le=1.0,
        description="Confidence gained per unit of resource (0-1 scale)"
    )
    confidence_per_token: float = Field(
        default=0.0,
        description="Confidence improvement per token consumed"
    )
    insight_per_joule: float | None = Field(
        default=None,
        description="Epistemic value per joule of energy (if calculable)"
    )

    # Time
    steps_executed: int = Field(default=0, ge=0, description="Number of thinking steps run")
    time_budget_exhausted: bool = Field(default=False, description="Did thinking exceed time budget?")

    # Budget status
    budget_exhausted: bool = Field(default=False, description="Was the thinking budget exhausted?")
    early_termination: bool = Field(default=False, description="Was thinking terminated early?")


# ═══════════════════════════════════════════════════════════════════════════════
# REALITY ANCHOR — Physical grounding for evidence
# ═══════════════════════════════════════════════════════════════════════════════

class RealityAnchor(BaseModel):
    """Physical constraints for evidence grounding."""
    entropy_direction: str = Field(
        default="unknown",
        description="'increasing' | 'stable' | 'decreasing' | 'unknown'"
    )
    energy_cost_estimate: float | None = Field(
        default=None,
        description="Estimated energy cost of the phenomenon being studied"
    )
    resource_constraints: list[str] = Field(
        default_factory=list,
        description="Named resource constraints that limit action"
    )
    irreversibility_flag: bool = Field(
        default=False,
        description="Does evidence suggest irreversible consequences?"
    )
    thermodynamic_footprint: str | None = Field(
        default=None,
        description="Physical cost classification: 'negligible' | 'moderate' | 'significant' | 'civilizational'"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# EVIDENCE OUTPUT — 222_SENSE full output with thinking
# ═══════════════════════════════════════════════════════════════════════════════

class EvidenceOutput(BaseModel):
    """Full output schema for arif_evidence_fetch with sequential thinking."""
    # Standard fields
    status: str = "OK"
    tool: str = "arif_evidence_fetch"

    # Thinking sequence (the new civilization intelligence layer)
    thinking_sequence: ThinkingSequence | None = Field(
        default=None,
        description="Sequential thinking process if thinking_depth > 0"
    )

    # Resource accounting
    resource_metrics: ResourceMetrics | None = Field(
        default=None,
        description="Detailed resource usage and efficiency metrics"
    )

    # Reality grounding
    reality_anchor: RealityAnchor | None = Field(
        default=None,
        description="Physical constraints that ground this evidence"
    )

    # Result
    result: dict[str, Any] = Field(default_factory=dict, description="Evidence content")
    meta: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: str | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# UNCERTAINTY GEOMETRY — Reusable across all tools
# ═══════════════════════════════════════════════════════════════════════════════

class UncertaintyGeometry(BaseModel):
    """Structured epistemic disclosure — not just a confidence number."""
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Primary confidence estimate")
    confidence_sources: list[str] = Field(
        default_factory=list,
        description="'prior_bias' | 'data_gap' | 'model_risk' | 'ambiguity' | 'time_sensitivity'"
    )
    model_risk: float = Field(ge=0.0, le=1.0, default=0.0, description="Uncertainty from model limitations")
    data_gaps: list[str] = Field(default_factory=list, description="Named missing data")
    known_unknowns: list[str] = Field(default_factory=list, description="Things known to be unknown")
    unknown_unknowns_suspected: list[str] = Field(
        default_factory=list,
        description="Potential gaps suspected but not named"
    )
    counterfactuals_considered: int = Field(default=0, ge=0, description="Number of alternatives evaluated")
    rejected_alternatives: list[str] = Field(default_factory=list, description="Rejected scenarios with reasons")
    sensitivity_to_unknown: str = Field(default="low", description="'low' | 'medium' | 'high'")
    ambiguity_fused: bool = Field(default=False, description="Were multiple interpretations merged?")
    epistemic_humility_score: float = Field(ge=0.0, le=1.0, default=0.5)


# ═══════════════════════════════════════════════════════════════════════════════
# CIVILIZATION CONTEXT — Scale and time for evidence
# ═══════════════════════════════════════════════════════════════════════════════

class EvidenceCivilizationContext(BaseModel):
    """Civilization-level context for evidence assessment."""
    time_horizon_years: int = Field(default=0, ge=0, description="Consequence time horizon")
    stakeholder_scope: str = Field(default="individual", description="'individual' | 'organization' | 'national' | 'global'")
    impact_radius: str = Field(default="reversible", description="'reversible' | 'structural' | 'civilizational'")
    domain: str = Field(default="unknown", description="Domain context")
    cascade_risk: bool = Field(default=False, description="Could cascade to other domains?")