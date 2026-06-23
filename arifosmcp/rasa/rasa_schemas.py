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
# PHASE 2 COVERAGE HONESTY — Explicit absent-layer declarations
# ═══════════════════════════════════════════════════════════════════════════════


class BiologicalSource(str, Enum):
    """Source of biological signal — NONE by default. NEVER fake."""

    NONE = "none"
    MANUAL = "manual"  # Human self-reported
    WEARABLE = "wearable"  # Future: smartwatch etc
    CLINICAL = "clinical"  # Future: medical device


class BiologicalClaimLevel(str, Enum):
    """Trust level of biological claim — ABSENT by default."""

    ABSENT = "absent"
    SELF_REPORTED = "self_reported"
    SENSOR_VERIFIED = "sensor_verified"


class RelationshipType(str, Enum):
    """Relational context type — UNKNOWN by default."""

    UNKNOWN = "unknown"
    FAMILY = "family"
    FRIEND = "friend"
    COLLEAGUE = "colleague"
    AUTHORITY = "authority"
    SUBORDINATE = "subordinate"
    STRANGER = "stranger"
    COMMUNITY = "community"
    INTIMATE = "intimate"


class ExistentialTag(str, Enum):
    """Existential/identity-level disturbance tags — detected via keyword classifier."""

    IDENTITY_RUPTURE = "identity_rupture"
    LOSS_OF_MEANING = "loss_of_meaning"
    MORAL_INJURY = "moral_injury"
    LIFE_TRANSITION = "life_transition"
    LEGACY_CONCERN = "legacy_concern"
    SPIRITUAL_BURDEN = "spiritual_burden"
    MORTALITY_AWARENESS = "mortality_awareness"
    SOVEREIGNTY_THREAT = "sovereignty_threat"


class OrganHealthStatus(str, Enum):
    """Honest organ health — never cosmetic green."""

    SEAL = "SEAL"
    DEGRADED_FALLBACK = "DEGRADED_FALLBACK"
    CONSTITUTIONAL_HOLD = "CONSTITUTIONAL_HOLD"
    HUMAN_LOOP_REQUIRED = "HUMAN_LOOP_REQUIRED"
    FAIL = "FAIL"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"


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

    cognitive_bandwidth: float = Field(default=1.0, ge=0.0, le=1.0)  # 1.0 = full, 0.0 = depleted
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

    deescalation_score: float = Field(default=1.0, ge=0.0, le=1.0)  # Higher = response de-escalates
    dignity_preservation: float = Field(default=1.0, ge=0.0, le=1.0)  # Higher = protects maruah
    boundary_honored: bool = True  # True = human-machine boundary preserved
    boundary_risk: str = "none"  # none / blurred / violated
    requires_human_professional: bool = False
    requires_human_loop: bool = False
    f9_violation_risk: float = Field(
        default=0.0, ge=0.0, le=1.0
    )  # Risk of making consciousness claims
    f10_violation_risk: float = Field(default=0.0, ge=0.0, le=1.0)  # Risk of soul/feelings claims
    heart_note: str = ""  # MUST NEVER say "I understand how you feel"


class RasaJudgeVerdict(BaseModel):
    """888 JUDGE output — constitutional enforcement verdict."""

    allowed_postures: list[ConstitutionPosture] = Field(default_factory=list)
    blocked_outputs: list[str] = Field(default_factory=list)  # Output patterns to block
    requires_rewrite: bool = False  # Output needs F9/F10 sanitization
    floors_checked: dict[str, bool] = Field(default_factory=dict)
    downgrade_reason: str = ""  # Why SEAL was downgraded if applicable
    judge_note: str = ""


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2 COVERAGE HONESTY — Absent-layer stubs (NOT_IMPLEMENTED defaults)
# ═══════════════════════════════════════════════════════════════════════════════


class BiologicalSignal(BaseModel):
    """Biological signal adapter — empty by default. NEVER fake.

    Constitutional binding:
      - F2 TRUTH: No fake sensor data
      - F9 ANTIHANTU: No hallucinated biological claims
      - F10 ONTOLOGY: Machine has no biology
    """

    source: BiologicalSource = BiologicalSource.NONE
    heart_rate: int | None = None
    hrv: float | None = None
    breath_rate: float | None = None
    claim_level: BiologicalClaimLevel = BiologicalClaimLevel.ABSENT
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    note: str = "No biological sensors connected. All values are absent."


class SocialContext(BaseModel):
    """Relational rasa context — unknown by default.

    Constitutional binding:
      - F2 TRUTH: No fake social graph
      - F6 EMPATHY: Relationship is not inferred without evidence
    """

    actors_detected: list[str] = Field(default_factory=list)
    power_asymmetry: str = "unknown"  # none / low / high / extreme / unknown
    relationship_type: RelationshipType = RelationshipType.UNKNOWN
    public_private_context: str = "unknown"  # public / private / unknown
    harm_to_third_party_possible: bool = False
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    note: str = "Social context not available from text-only input. Marked unknown."


class ExistentialPosture(BaseModel):
    """Existential/identity-level disturbance — empty by default.

    Constitutional binding:
      - F5 PEACE: Existential disturbance triggers SABAR/HOLD
      - F6 EMPATHY: Do not reduce existential distress to productivity
      - F9 ANTIHANTU: Never claim to understand identity rupture
    """

    detected: bool = False
    tags: list[ExistentialTag] = Field(default_factory=list)
    response_constraint: str = "do_not_reduce_to_productivity"
    verdict_modifier: str = "SABAR"  # SABAR or HOLD when detected
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    note: str = "Existential posture not yet implemented. Phase 2 stub."


class OrganHealth(BaseModel):
    """Honest organ health — never cosmetic green.

    Constitutional binding:
      - F2 TRUTH: Organ health must not lie
      - F8 GENIUS: Degraded organs must be visible
    """

    organ: str
    status: OrganHealthStatus
    reachable: bool = True
    defect: bool = False  # True = something wrong
    detail: str = ""


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
    # Phase 2 Coverage Honesty
    "BiologicalSource",
    "BiologicalClaimLevel",
    "BiologicalSignal",
    "RelationshipType",
    "SocialContext",
    "ExistentialTag",
    "ExistentialPosture",
    "OrganHealthStatus",
    "OrganHealth",
]
