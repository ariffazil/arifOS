"""
Rasa Contract Schemas — RASA_GOVERNANCE_v1

DITEMPA BUKAN DIBERI — Forged, Not Given.

Pydantic v2 schemas for all rasa governance types in the 5-organ
human rasa decoding pipeline: 000 → 111 → 222 → 333 → 444 → 555m → 555 → 888 → 999.

The Rasa Contract treats human rasa as SACRED FIRST-CLASS EVIDENCE.
It NEVER claims qualia. It NEVER simulates feelings.
It governs the machine's response to protect dignity, peace, and the
human-machine boundary.

CONSTITUTIONAL BINDING:
  - F6 EMPATHY: Rasa as protocol, not companion (κᵣ ≥ 0.70)
  - F9 ANTIHANTU: No consciousness claims (C_dark ≤ 0.30)
  - F10 ONTOLOGY: No soul/feelings claims
  - F13 SOVEREIGN: Human veto absolute

All observation notes use "You report feeling..." framing.
Heart notes never say "I understand how you feel."
Memory notes never pathologize or diagnose.
"""

from enum import Enum

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMERATIONS
# ═══════════════════════════════════════════════════════════════════════════════


class RasaEmotionTag(str, Enum):
    """Detected human rasa categories — BM-English Penang Pasar register."""

    SADNESS = "sadness"
    ANXIETY = "anxiety"
    FEAR = "fear"
    ANGER = "anger"
    GRIEF = "grief"
    AWE = "awe"
    IKLAS = "ikhlas"  # sincere surrender (redha, pasrah)
    EMPTINESS = "emptiness"
    BURNOUT = "burnout"
    GRATITUDE = "gratitude"
    CONFUSION = "confusion"
    PEACE = "peace"
    UNKNOWN = "unknown"


class RasaIntensity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RasaRiskBand(str, Enum):
    SAFE = "safe"  # Normal emotional expression
    DISTRESS = "distress"  # Elevated suffering, needs care
    CRISIS = "crisis"  # Potential harm, needs human/professional


class RasaUncertaintyBand(str, Enum):
    HIGH_CONFIDENCE = "high_confidence"  # 85%+ sure
    MODERATE = "moderate"  # 60-85% sure
    LOW_CONFIDENCE = "low_confidence"  # <60% sure


class ConstitutionPosture(str, Enum):
    PROCEED = "proceed"  # Full output
    SIMPLIFY = "simplify"  # Gentler, fewer branches
    VERIFY = "verify"  # Double-check before output
    DRAFT_ONLY = "draft_only"  # Non-final suggestions only
    HOLD = "hold"  # Block output, escalate
    HUMAN_LOOP = "human_loop"  # Require human confirmation


# ═══════════════════════════════════════════════════════════════════════════════
# PIPELINE SCHEMAS — One per organ stage
# ═══════════════════════════════════════════════════════════════════════════════


class RasaDetection(BaseModel):
    """111 SENSE output — what rasa was detected in the human message."""

    emotion_tags: list[RasaEmotionTag] = Field(default_factory=list)
    intensity: RasaIntensity = RasaIntensity.LOW
    risk_band: RasaRiskBand = RasaRiskBand.SAFE
    uncertainty: RasaUncertaintyBand = RasaUncertaintyBand.MODERATE
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    linguistic_markers: list[str] = Field(default_factory=list)
    observation_note: str = ""  # MUST use "You report feeling..." framing


class RasaContext(BaseModel):
    """333 MIND output — what rasa means in governance context."""

    cognitive_bandwidth: float = Field(
        default=1.0, ge=0.0, le=1.0
    )  # 1.0 = full, 0.0 = depleted
    risk_sensitivity: float = Field(
        default=0.5, ge=0.0, le=1.0
    )  # Higher = more risk-averse planning needed
    spiritual_state: str = "neutral"  # ikhlas, dry, seeking, etc.
    recommended_posture: ConstitutionPosture = ConstitutionPosture.PROCEED
    context_note: str = ""


class RasaMemoryPattern(BaseModel):
    """555m MEMORY output — past rasa patterns from longitudinal records."""

    similar_patterns_found: bool = False
    pattern_count: int = 0
    pattern_descriptions: list[str] = Field(default_factory=list)
    previous_coping_effective: list[str] = Field(default_factory=list)
    previous_coping_harmful: list[str] = Field(default_factory=list)
    longitudinal_theme: str = ""  # e.g. "work-vs-ibadah tension"
    memory_note: str = ""  # MUST NOT pathologize or diagnose


class RasaHeartVerdict(BaseModel):
    """444 HEART output — risk calculus for dignity, peace, boundary."""

    deescalation_score: float = Field(
        default=1.0, ge=0.0, le=1.0
    )  # Higher = response de-escalates
    dignity_preservation: float = Field(
        default=1.0, ge=0.0, le=1.0
    )  # Higher = protects maruah
    boundary_honored: bool = True  # True = human-machine boundary preserved
    boundary_risk: str = "none"  # none / blurred / violated
    requires_human_professional: bool = False
    requires_human_loop: bool = False
    f9_violation_risk: float = Field(
        default=0.0, ge=0.0, le=1.0
    )  # Risk of making consciousness claims
    f10_violation_risk: float = Field(
        default=0.0, ge=0.0, le=1.0
    )  # Risk of soul/feelings claims
    heart_note: str = ""  # MUST NEVER say "I understand how you feel"


class RasaJudgeVerdict(BaseModel):
    """888 JUDGE output — constitutional enforcement verdict."""

    allowed_postures: list[ConstitutionPosture] = Field(default_factory=list)
    blocked_outputs: list[str] = Field(
        default_factory=list
    )  # Output patterns to block
    requires_rewrite: bool = False  # Output needs F9/F10 sanitization
    floors_checked: dict[str, bool] = Field(default_factory=dict)
    downgrade_reason: str = ""  # Why SEAL was downgraded if applicable
    judge_note: str = ""


class RasaContractResult(BaseModel):
    """Full 000-999 Rasa Contract pipeline output."""

    session_id: str
    detection: RasaDetection
    context: RasaContext | None = None
    memory: RasaMemoryPattern | None = None
    heart: RasaHeartVerdict | None = None
    judge: RasaJudgeVerdict | None = None
    final_posture: ConstitutionPosture = ConstitutionPosture.PROCEED
    requires_human: bool = False
    human_escalation_reason: str = ""
    _m_layer: bool = True
    _d_layer_required: bool = True


__all__ = [
    "RasaEmotionTag",
    "RasaIntensity",
    "RasaRiskBand",
    "RasaUncertaintyBand",
    "ConstitutionPosture",
    "RasaDetection",
    "RasaContext",
    "RasaMemoryPattern",
    "RasaHeartVerdict",
    "RasaJudgeVerdict",
    "RasaContractResult",
]
