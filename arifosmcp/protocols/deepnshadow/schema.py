"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  arifOS — DeepnShadow Schemas                                                ║
║  Behavioural evidence → pattern → hypothesis → scar-vector → safe action     ║
║  SOT: Canonical type system for governed human-pattern inference.            ║
║  Version: DS-111..DS-999 (encode → decode → metabolize)                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class EvidenceStrength(str, Enum):
    """F02 TRUTH banding for behavioural observations."""

    SINGLE = "single"
    REPEATED = "repeated"
    CORROBORATED = "corroborated"


class EvidenceClass(str, Enum):
    """DS-222 Evidence Quality Gate — granular confidence class.

    E0 = feeling only
    E1 = single observation
    E2 = repeated observation
    E3 = documented message / meeting note
    E4 = multiple witnesses / artifacts
    E5 = confirmed by person directly
    """

    E0_FEELING = "E0"
    E1_SINGLE = "E1"
    E2_REPEATED = "E2"
    E3_DOCUMENTED = "E3"
    E4_CORROBORATED = "E4"
    E5_CONFIRMED = "E5"


class InferenceMode(str, Enum):
    """DS prompt engine mode — who is being mapped."""

    MIRROR = "mirror"  # Arif's own shadow
    OTHER = "other"  # Another individual
    TEAM = "team"  # Organizational / team pattern


class DignityStatus(str, Enum):
    """F05 PEACE / F06 EMPATHY enforcement state."""

    SAFE = "safe"
    GUARDED = "guarded"
    HOLD = "hold"


class EmotionalCharge(str, Enum):
    """DS-777: raw charge before metabolism."""

    ANGER = "anger"
    SHAME = "shame"
    SUSPICION = "suspicion"
    CONFUSION = "confusion"
    HURT = "hurt"
    FEAR = "fear"
    GRIEF = "grief"
    LOW = "low"
    NEUTRAL = "neutral"


class BehaviourObservation(BaseModel):
    """Layer 1: SENSE / DS-111 — capture behaviour, not story.

    Every observation must be observable, timestamped, and separated
    from interpretation. No diagnostic language at this layer.
    """

    observation_id: str = Field(..., description="UUID for this observation")
    session_id: str = Field(..., description="Governing session")
    actor_id: str | None = Field(
        default=None, description="Subject of observation (hashed/pseudonym)"
    )
    description: str = Field(..., description="Observable behaviour, no judgment")
    context: str | None = Field(default=None, description="Situational context")
    source: str = Field(
        default="human_report",
        description="sense, memory, human_report, a2a, meeting_note, document",
    )
    observed_at: datetime = Field(default_factory=datetime.utcnow)
    evidence_strength: EvidenceStrength = Field(default=EvidenceStrength.SINGLE)
    evidence_class: EvidenceClass = Field(default=EvidenceClass.E1_SINGLE)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("description")
    @classmethod
    def _no_diagnostic_language(cls, v: str) -> str:
        banned = ["is insecure", "is narcissistic", "is toxic", "has trauma", "is projecting"]
        lower = v.lower()
        for phrase in banned:
            if phrase in lower:
                raise ValueError(
                    f"F05 dignity violation: observation contains diagnostic language '{phrase}'"
                )
        return v


class PatternRecurrence(BaseModel):
    """Layer 2: MEMORY — detect recurrence without overreading.

    A pattern is not a diagnosis. It is a statistical clustering
    of observations across time and context.
    """

    pattern_id: str = Field(..., description="UUID for this pattern")
    observation_ids: list[str] = Field(default_factory=list)
    recurrence_count: int = Field(..., ge=2, description="Must be ≥ 2 to qualify as pattern")
    time_window_days: int = Field(..., description="Span of observation window")
    trigger_contexts: list[str] = Field(default_factory=list)
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Pattern confidence from recurrence density"
    )


class AlternativeExplanation(BaseModel):
    """DS-333 mandatory alternative — prevents ego-confirmation."""

    explanation_id: str = Field(..., description="UUID")
    hypothesis_id: str = Field(..., description="Linked hypothesis")
    explanation_text: str = Field(
        ..., description="Non-shadow explanation, e.g., workload pressure"
    )
    likelihood: str = Field(default="possible", description="possible / probable / unlikely")


class ShadowHypothesis(BaseModel):
    """Layer 3: MIND / DS-333 — generate hypotheses, not truths.

    Every shadow hypothesis must be labelled as such.
    Confidence must be uncertainty-banded (F02 / F07).
    Alternative explanations are mandatory.
    """

    hypothesis_id: str = Field(..., description="UUID")
    pattern_id: str = Field(..., description="Linked pattern")
    hypothesis_text: str = Field(
        ..., description="e.g., 'Control behaviour increases under uncertainty'"
    )
    trigger_vector: str | None = Field(
        default=None, description="What appears to trigger the pattern"
    )
    confidence: float = Field(..., ge=0.0, le=1.0)
    uncertainty_band: str = Field(default="medium", description="low / medium / high")
    is_dignity_safe: bool = Field(default=True)
    dignity_status: DignityStatus = Field(default=DignityStatus.SAFE)
    alternative_explanations: list[AlternativeExplanation] = Field(default_factory=list)

    @field_validator("hypothesis_text")
    @classmethod
    def _hypothesis_not_truth(cls, v: str) -> str:
        truth_claims = ["is", "has", "because", "due to"]
        if any(v.lower().startswith(t) for t in truth_claims):
            raise ValueError(
                "Hypothesis must not be phrased as truth claim. Use 'suggests', 'may indicate', 'pattern consistent with'"
            )
        return v


class ScarVector(BaseModel):
    """Layer 4: WELL / DS-555 — scar-risk boundary, not diagnosis.

    A scar-vector is a protected-zone inference. It must never
    be presented as confirmed trauma. It is a structural hypothesis
    about what the person may be protecting.
    """

    vector_id: str = Field(..., description="UUID")
    hypothesis_id: str = Field(..., description="Linked hypothesis")
    protected_zone: str = Field(
        ..., description="e.g., 'authority / competence / shame / abandonment'"
    )
    confidence: float = Field(..., ge=0.0, le=1.0)
    boundary_type: str = Field(
        default="unknown", description="e.g., control-seeking, withdrawal, externalisation"
    )
    safe_action_hint: str | None = Field(
        default=None, description="How to interact without triggering the boundary"
    )


class ProjectionMirror(BaseModel):
    """DS-444 — Projection differential.

    Asks: 'How much of this read is about Arif's own scar reacting?'
    This does not invalidate the read. It purifies it.
    """

    mirror_id: str = Field(..., description="UUID")
    hypothesis_id: str = Field(..., description="Linked hypothesis")
    arif_trigger_match: str | None = Field(
        default=None, description="Which of Arif's scar-vectors may be resonating"
    )
    resonance_score: float = Field(
        ..., ge=0.0, le=1.0, description="0 = pure observation, 1 = likely projection"
    )
    reflection_text: str = Field(
        ...,
        description="e.g., 'Arif may be reacting strongly because false authority is a scar trigger'",
    )
    safe_self_action: str | None = Field(
        default=None, description="What Arif should do to reduce projection bias"
    )


class SafeAction(BaseModel):
    """Layer 5: REPLY / FORGE — dignity-preserving action.

    No shadow map may be used as accusation.
    The only valid output of DeepnShadow is safer behaviour
    from the observer (Arif), not a label on the observed.
    """

    action_text: str = Field(..., description="What Arif should do or say")
    avoids_trigger: str | None = Field(default=None, description="What to avoid")
    preserves_dignity: bool = Field(default=True)
    escalation_path: str | None = Field(
        default=None, description="If HOLD, route to human deliberation"
    )


class MetabolizedAction(BaseModel):
    """DS-777 — explicit emotional metabolism.

    Converts raw charge into governed action.
    Before: anger → After: boundary.
    Before: shame → After: workflow container.
    """

    metabolize_id: str = Field(..., description="UUID")
    action: SafeAction = Field(..., description="The dignity-safe action")
    raw_charge: EmotionalCharge = Field(..., description="Emotion before metabolism")
    metabolized_charge: str = Field(
        ..., description="Emotion after metabolism, e.g., 'clean signal'"
    )
    arif_scar_link: str | None = Field(
        default=None, description="Which Arif scar-vector this touches"
    )


class TeamShadowPattern(BaseModel):
    """DS-333 TEAM mode — organizational geology.

    Maps team-level behaviour to possible systemic shadows.
    """

    team_pattern_id: str = Field(..., description="UUID")
    team_name: str | None = Field(default=None, description="Team or org unit")
    observed_behaviours: list[str] = Field(default_factory=list)
    systemic_shadow: str | None = Field(default=None, description="e.g., 'fear of accountability'")
    alternative_systemic_cause: str | None = Field(
        default=None, description="e.g., 'management pressure'"
    )
    safe_org_action: str | None = Field(default=None, description="What leadership should do")


class RedactedVaultEntry(BaseModel):
    """DS-999 — privacy-preserving vault record.

    Stores patterns and safe responses, not accusations.
    Actor_id is redacted or role-based.
    """

    entry_id: str = Field(..., description="UUID")
    session_id: str = Field(..., description="Governing session")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    mode: InferenceMode = Field(default=InferenceMode.OTHER)
    role_tag: str | None = Field(default=None, description="e.g., 'colleague', 'manager', 'self'")
    pattern_summary: str = Field(..., description="Redacted pattern description")
    safe_response: str | None = Field(default=None, description="What was done")
    outcome: str | None = Field(default=None, description="What happened next")
    dignity_status: DignityStatus = Field(default=DignityStatus.SAFE)


class DeepnShadowReport(BaseModel):
    """Terminal output of the DeepnShadow pipeline.

    Governed by F02 (truth), F05 (peace), F06 (empathy),
    F07 (humility), F09 (antihantu), F13 (sovereign).
    """

    report_id: str = Field(..., description="UUID")
    session_id: str = Field(..., description="Governing session")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    mode: InferenceMode = Field(default=InferenceMode.OTHER)
    observations: list[BehaviourObservation] = Field(default_factory=list)
    patterns: list[PatternRecurrence] = Field(default_factory=list)
    hypotheses: list[ShadowHypothesis] = Field(default_factory=list)
    alternative_explanations: list[AlternativeExplanation] = Field(default_factory=list)
    projection_mirrors: list[ProjectionMirror] = Field(default_factory=list)
    scar_vectors: list[ScarVector] = Field(default_factory=list)
    safe_actions: list[SafeAction] = Field(default_factory=list)
    metabolized_actions: list[MetabolizedAction] = Field(default_factory=list)
    team_patterns: list[TeamShadowPattern] = Field(default_factory=list)
    overall_dignity_status: DignityStatus = Field(default=DignityStatus.SAFE)
    overall_confidence: float = Field(..., ge=0.0, le=1.0)
    verdict: str = Field(default="SABAR", description="SEAL / SABAR / HOLD / VOID")
    constitutional_notes: list[str] = Field(default_factory=list)

    def to_vault_line(self) -> dict[str, Any]:
        """Append-only serialization for VAULT999 shadow journal.

        Strips identifiable actor_id if present to preserve privacy.
        """
        return {
            "report_id": self.report_id,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "mode": self.mode.value,
            "observation_count": len(self.observations),
            "pattern_count": len(self.patterns),
            "hypothesis_count": len(self.hypotheses),
            "alternative_count": len(self.alternative_explanations),
            "projection_mirror_count": len(self.projection_mirrors),
            "scar_vector_count": len(self.scar_vectors),
            "safe_action_count": len(self.safe_actions),
            "metabolized_action_count": len(self.metabolized_actions),
            "team_pattern_count": len(self.team_patterns),
            "overall_dignity_status": self.overall_dignity_status.value,
            "overall_confidence": self.overall_confidence,
            "verdict": self.verdict,
            "constitutional_notes": self.constitutional_notes,
        }
