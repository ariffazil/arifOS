"""
arifOS Mind + Synthesis Schemas — 333_MIND, 444r_REPLY, 222_FETCH
══════════════════════════════════════════════════════════════════════════════

Phase 2 Civilization Intelligence — MindOutput for arif_mind_reason.

MindOutput must include:
- AxiomsUsed: explicit constitutional grounding per reasoning step
- ReasoningTrace: step-by-step derivation with confidence trajectory
- AnomalousContrast: ToAC detection for manipulation / wrong abstraction
- ThermodynamicState: energy cost of reasoning
- ToAC embedded for self-correction

DITEMPA BUKAN DIBERI — Forged, Not Given
"""
from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field
from typing import Any

from arifosmcp.schemas.verdict import ThermodynamicState


# ═══════════════════════════════════════════════════════════════════════════════
# MIND REASONING ENUMS
# ═══════════════════════════════════════════════════════════════════════════════

class ReasoningMode(str, Enum):
    """How is the mind reasoning?"""
    INDUCTIVE = "inductive"        # Specific → General
    DEDUCTIVE = "deductive"        # General → Specific
    ABDUCTIVE = "abductive"        # Effect → Cause
    ANALOGICAL = "analogical"      # Similarity transfer
    CAUSAL = "causal"             # Cause → Effect
    COUNTERFACTUAL = "counterfactual"  # What if not?


class AxiomSource(str, Enum):
    """Where did the axiom come from?"""
    CONSTITUTION = "constitution"      # F1-F13
    EMPIRICAL = "empirical"           # Observed data
    DERIVED = "derived"               # Inferred from other axioms
    HEURISTIC = "heuristic"           # Learned pattern
    AUTHORITY = "authority"            # Trusted external source


class ContrastType(str, Enum):
    """Type of anomalous contrast detected."""
    EXPECTED_V_OBSERVED = "expected_vs_observed"
    CLAIMED_V_VERIFIED = "claimed_vs_verified"
    SHORT_TERM_V_ENTROPY = "shortterm_vs_entropy"
    LOCAL_V_CIVILIZATIONAL = "local_vs_civilizational"
    MODEL_V_REALITY = "model_vs_reality"
    NONE = "none"


# ═══════════════════════════════════════════════════════════════════════════════
# AXIOM USAGE — Explicit constitutional grounding per reasoning step
# ═══════════════════════════════════════════════════════════════════════════════

class AxiomUsage(BaseModel):
    """
    Tracks which axiom was used at which reasoning step.
    Prevents implicit self-modification or invisible drift.
    """
    axiom_id: str = Field(description="Identifier e.g. 'F01_AMANAH', 'F08_GENIUS'")
    axiom_text: str = Field(description="Full axiom text")
    source: AxiomSource = Field(description="Where the axiom originates")
    applicability: str = Field(
        description="Why this axiom applies to this reasoning"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence that axiom was correctly applied"
    )
    step: int = Field(ge=1, description="Which reasoning step this axiom grounded")


class AxiomsUsed(BaseModel):
    """
    Collection of all axioms used in a single reasoning session.
    Makes reasoning traceable to constitutional grounding.
    """
    axioms: list[AxiomUsage] = Field(
        default_factory=list,
        description="All axioms used in this reasoning"
    )
    dominant_axiom: str | None = Field(
        default=None,
        description="Primary axiom driving the conclusion"
    )
    axiom_diversity: float = Field(
        ge=0.0, le=1.0,
        description="Ratio of unique axioms to reasoning steps (higher = more grounded)"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# REASONING STEP — Individual reasoning iteration
# ═══════════════════════════════════════════════════════════════════════════════

class ReasoningStep(BaseModel):
    """Single step in the reasoning trace."""
    step: int = Field(ge=1, description="Step number")
    reasoning_mode: ReasoningMode = Field(description="Type of reasoning used")
    premise: str = Field(description="What was the starting premise?")
    derivation: str = Field(description="How was the conclusion derived?")
    conclusion: str = Field(description="What was concluded at this step")
    confidence_before: float = Field(ge=0.0, le=1.0)
    confidence_after: float = Field(ge=0.0, le=1.0)
    confidence_delta: float = Field(description="Improvement (can be negative)")
    axiom_used: str | None = Field(
        default=None,
        description="Axiom ID that grounded this step (None if heuristic)"
    )
    landauer_cost_eV: float | None = Field(
        default=None,
        description="Thermodynamic cost in electron volts"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# REASONING TRACE — Full step-by-step derivation
# ═══════════════════════════════════════════════════════════════════════════════

class ReasoningTrace(BaseModel):
    """Complete reasoning process with step-by-step traceability."""
    steps: list[ReasoningStep] = Field(
        default_factory=list,
        description="All reasoning steps in order"
    )
    total_steps: int = Field(ge=0)
    reasoning_mode: ReasoningMode = Field(
        default=ReasoningMode.INDUCTIVE,
        description="Primary reasoning mode used"
    )
    conclusion: str | None = Field(
        default=None,
        description="Final conclusion after all steps"
    )
    final_confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence after all steps"
    )
    confidence_trajectory: list[float] = Field(
        default_factory=list,
        description="Confidence at each step for visualization"
    )
    # Quality assessment
    reasoning_depth: str = Field(
        default="shallow",
        description="'shallow' | 'adequate' | 'deep' | 'exhaustive'"
    )
    coherence_score: float = Field(
        ge=0.0, le=1.0,
        description="Internal consistency of the reasoning"
    )
    total_landauer_cost_eV: float = Field(
        default=0.0,
        description="Total thermodynamic cost"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ANOMALOUS CONTRAST — ToAC detection for 333_MIND
# ═══════════════════════════════════════════════════════════════════════════════

class MindAnomalousContrast(BaseModel):
    """
    ToAC detection for Mind reasoning.
    Detects when reasoning pattern diverges from expected norm.
    Prevents: clever but misaligned reasoning, pattern hallucination.

    Embedded in: 333_MIND MindOutput, 888_JUDGE VerdictOutput
    """
    baseline_reasoning_pattern: str = Field(
        default="normal_reasoning",
        description="What normal reasoning looks like for this query type"
    )
    observed_deviation: str = Field(
        default="none",
        description="How observed reasoning diverged from baseline"
    )
    magnitude: float = Field(
        default=0.0,
        ge=0.0, le=1.0,
        description="Normalized deviation (0=none, 1=maximum)"
    )
    confidence: float = Field(
        default=0.95,
        ge=0.0, le=1.0
    )
    contrast_type: ContrastType = Field(
        default=ContrastType.NONE,
        description="Classification of the contrast type"
    )
    manipulation_signal: bool = Field(
        default=False,
        description="Does this suggest intentional manipulation (F09)?"
    )
    anti_hantu_score: float = Field(
        ge=0.0, le=1.0,
        default=0.0,
        description="Likelihood manipulation detected"
    )
    resolution_strategy: str | None = Field(
        default=None,
        description="How the system resolved the contrast"
    )
    resolution_confidence: float | None = Field(
        ge=0.0, le=1.0,
        default=None,
        description="Confidence in resolution"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MIND OUTPUT — PRIMARY OUTPUT FOR arif_mind_reason (333_MIND)
# ═══════════════════════════════════════════════════════════════════════════════

class MindOutput(BaseModel):
    """
    Full output for arif_mind_reason (333_MIND — AGI layer for reasoning).

    Every field affects reasoning behavior:
    - axioms_used: grounds reasoning in constitution, prevents drift
    - reasoning_trace: makes derivation replay-auditable
    - anomalous_contrast: detects manipulation / wrong abstraction
    - thermodynamic_state: tracks energy cost of reasoning
    - ToAC_self_correction: enables self-correction before output

    Stage: 333_MIND (AGI layer — tactical execution)
    Pillar: Constitutional grounding + ToAC + Thermodynamic
    """
    status: str = "OK"
    tool: str = "arif_mind_reason"

    # Core result
    result: dict[str, Any] = Field(default_factory=dict)
    verdict: str = Field(default="CLAIM", description="'CLAIM' | 'PLAUSIBLE' | 'HOLD' | 'VOID'")

    # Constitutional grounding
    axioms_used: AxiomsUsed = Field(
        default_factory=AxiomsUsed,
        description="All axioms used to ground this reasoning"
    )

    # Reasoning traceability
    reasoning_trace: ReasoningTrace = Field(
        default_factory=ReasoningTrace,
        description="Step-by-step derivation with confidence trajectory"
    )

    # ToAC — manipulation / wrong abstraction detection
    anomalous_contrast: MindAnomalousContrast = Field(
        default_factory=MindAnomalousContrast,
        description="Anomalous contrast detection (ToAC)"
    )

    # Thermodynamic cost
    thermodynamic_state: ThermodynamicState = Field(
        default_factory=ThermodynamicState,
        description="Energy and entropy tracking for this reasoning"
    )

    # ToAC self-correction (result of contrast detection)
    toac_self_correction: str | None = Field(
        default=None,
        description="If contrast detected: what correction was applied?"
    )

    # Metadata
    meta: dict[str, Any] = Field(default_factory=dict)
    delta_S: float = Field(default=0.0)
    timestamp: str | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# BACKWARD-COMPATIBLE ENVELOPES
# ═══════════════════════════════════════════════════════════════════════════════

class Synthesis(BaseModel):
    """Backward-compatible synthesis envelope."""
    status: str = "OK"
    tool: str = "arif_mind_reason"
    result: dict[str, Any] = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: str | None = None


class ReplyBlock(BaseModel):
    """Reply envelope for arif_reply_compose."""
    status: str = "OK"
    tool: str = "arif_reply_compose"
    result: dict[str, Any] = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: str | None = None


class EvidenceBlock(BaseModel):
    """Evidence envelope for arif_evidence_fetch."""
    status: str = "OK"
    tool: str = "arif_evidence_fetch"
    result: dict[str, Any] = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: str | None = None
