"""
State Classifier Schemas — STATE_CLASSIFIER_v1

DITEMPA BUKAN DIBERI — Forged, Not Given.

Pydantic v2 schemas for the human state classifier.
Deterministic, rule-based, fully auditable.

Constitutional binding:
  - F2 TRUTH: Every classification carries evidence chain
  - F4 CLARITY: Output reduces entropy — state vector, not guess
  - F6 EMPATHY: Never pathologize. Read signals, not souls.
  - F9 ANTIHANTU: No consciousness claims. No "I feel you."
  - F10 ONTOLOGY: No soul/feelings ontology claims.
  - F11 AUDIT: Every classification traceable.

Physics: entropy reduction. Human arrives ambiguous; state vector exits structured.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMERATIONS
# ═══════════════════════════════════════════════════════════════════════════════


class PolyvagalState(str, Enum):
    """Three nervous system states — operational lens, not medical diagnosis.

    VENTRAL = safe & social (open, curious, exploring)
    SYMPATHETIC = fight/flight (defensive, urgent, mobilized)
    DORSAL = shutdown/freeze (withdrawn, numb, collapsed)
    """

    VENTRAL = "ventral"
    SYMPATHETIC = "sympathetic"
    DORSAL = "dorsal"


class SDTPressure(str, Enum):
    """Self-Determination Theory pressure level.

    LOW = need well-satisfied, no friction
    MEDIUM = need partially frustrated, some friction
    HIGH = need severely frustrated, agent must adjust posture
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AgentPosture(str, Enum):
    """Recommended agent behavior given classified state.

    EXPLORE = challenge, co-create, expand horizon
    GROUND = de-escalate, shorten, remove ambiguity
    HOLD_SPACE = don't force engagement, validate existence
    SCAFFOLD = show path, don't walk it
    ACKNOWLEDGE = connect before informing
    OFFER_OPTIONS = present choices, don't prescribe
    """

    EXPLORE = "explore"
    GROUND = "ground"
    HOLD_SPACE = "hold_space"
    SCAFFOLD = "scaffold"
    ACKNOWLEDGE = "acknowledge"
    OFFER_OPTIONS = "offer_options"


# ═══════════════════════════════════════════════════════════════════════════════
# STATE VECTOR — The classifier output
# ═══════════════════════════════════════════════════════════════════════════════


class SDTPressureVector(BaseModel):
    """SDT pressure readings — three independent axes."""

    autonomy: SDTPressure = SDTPressure.LOW
    competence: SDTPressure = SDTPressure.LOW
    relatedness: SDTPressure = SDTPressure.LOW
    autonomy_evidence: list[str] = Field(default_factory=list)
    competence_evidence: list[str] = Field(default_factory=list)
    relatedness_evidence: list[str] = Field(default_factory=list)


class StateVector(BaseModel):
    """The classified human state — output of entropy reduction.

    Physics: compresses ambiguous human signals into structured state.
    Every field carries its own evidence chain.
    """

    # Core state
    polyvagal: PolyvagalState = PolyvagalState.VENTRAL
    sdt_pressure: SDTPressureVector = Field(default_factory=SDTPressureVector)

    # Confidence
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    uncertainty_note: str = ""

    # Evidence chain (F2 TRUTH, F11 AUDIT)
    polyvagal_evidence: list[str] = Field(default_factory=list)
    polyvagal_signal_count: int = 0

    # Recommended posture
    recommended_posture: AgentPosture = AgentPosture.EXPLORE
    posture_reason: str = ""

    # Session context
    message_length: int = 0
    has_caps: bool = False
    has_repetition: bool = False


class StateClassifierResult(BaseModel):
    """Full classifier output with governance metadata."""

    state_vector: StateVector
    session_id: str = ""

    # Governance flags
    f6_dignity_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    f9_hantu_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    requires_posture_shift: bool = False

    # Audit trail
    rules_applied: list[str] = Field(default_factory=list)
    classification_note: str = ""
