"""
arifOS Metabolic Output Schemas — 444_METABOLIZE
═══════════════════════════════════════════════════════════════════════════════════

Governed Witness Metabolism Architecture (Arif Eureka 2026-05-16)
─────────────────────────────────────────────────────────────────────

Intelligence is not answer generation.
Intelligence is governed witness metabolism.

LLM generates language.
MCP gives access to tools.
Memory stores state.
Governance constrains action.

The loop:
  witness → decode → contrast → meaning → constraint → model update → judgment

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# ═══════════════════════════════════════════════════════════════════════════════
# METABOLIC ENUMS
# ═══════════════════════════════════════════════════════════════════════════════


class ClaimState(StrEnum):
    """Where does this claim sit in the evidence lifecycle?

    Maps directly to Eureka 10 metabolic output contract.
    """

    OBSERVED = "OBSERVED"  # Raw witness received — not yet interpreted
    HYPOTHESIS = "HYPOTHESIS"  # Anomaly detected, meaning proposed
    QUALIFIED = "QUALIFIED"  # Meaning tested, constraints checked
    VERIFIED = "VERIFIED"  # Cross-witness confirmed
    SEALED = "SEALED"  # Irreversible — human ratified + vault entry
    HOLD = "HOLD"  # Governance pause — requires 888_JUDGE


class WitnessType(StrEnum):
    """What category of evidence is this witness?

    Eureka 1: Reality is never directly held. Maps are not Earth.
    """

    MAP = "map"
    SEISMIC = "seismic"
    FILING = "filing"
    REPORT = "report"
    IMAGE = "image"
    LOG = "log"
    TESTIMONY = "testimony"
    SENSOR = "sensor"
    DOCUMENT = "document"
    SIGNAL = "signal"


class ModelTarget(StrEnum):
    """Which domain model does this witness update?

    Eureka 4: GEOX → LargeEarthModel
              WEALTH → LargeWealthModel / LargeInstitutionModel
              WELL → LargeBodyModel
    """

    EARTH = "Earth"
    WEALTH = "Wealth"
    INSTITUTION = "Institution"
    BODY = "Body"
    CASE = "Case"
    SYSTEM = "System"


class OrganType(StrEnum):
    """Which organ processes this witness."""

    GEOX = "GEOX"  # Earth metabolism
    WEALTH = "WEALTH"  # Capital/institution metabolism
    WELL = "WELL"  # Body/human-readiness metabolism
    INSTX = "INSTX"  # Institution model (forge as WEALTH mode first)
    ARIFOS = "arifOS"  # Constitutional kernel + routing


class ContrastSeverity(StrEnum):
    """How significant is the anomalous contrast?"""

    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AbstractionUse(StrEnum):
    """How can an abstraction be safely used?"""

    HEURISTIC = "heuristic"  # Starting point for investigation only
    HYPOTHESIS = "hypothesis"  # Testable claim under development
    VERIFIED_MODEL = "verified_model"  # Physically/logically confirmed


# ═══════════════════════════════════════════════════════════════════════════════
# UNIVERSAL CONFIDENCE POLICY — Eureka 10 §7
# Shared confidence language across ALL organs (GEOX, WEALTH, WELL, arifOS)
# ═══════════════════════════════════════════════════════════════════════════════


class ConfidenceLevel(StrEnum):
    """
    Shared confidence language across all organs.

    Eureka 10 §7: One shared confidence policy.

    Rules:
      No evidence       → UNKNOWN / HOLD
      Weak evidence     → HYPOTHESIS
      Cross-checked    → QUALIFIED
      Primary-source   → VERIFIED
      Human authority  → SEALED
    """

    UNKNOWN = "UNKNOWN"  # No evidence at all — cannot proceed
    LOW = "LOW"  # Anecdotal or single-source evidence
    MODERATE = "MODERATE"  # Multiple sources, some constraints checked
    HIGH = "HIGH"  # Cross-validated, constraints pass
    VERIFIED = "VERIFIED"  # Primary-source confirmed
    SEALED = "SEALED"  # Human ratified + vault entry (irreversible)


class WitnessStatus(StrEnum):
    """
    Lifecycle stage of a witness through the metabolic pipeline.

    Eureka 10 §1: Universal witness schema.
    """

    RAW = "RAW"  # Received but not decoded
    DECODED = "DECODED"  # Entity extracted
    INTERPRETED = "INTERPRETED"  # Meaning assigned
    VERIFIED = "VERIFIED"  # Cross-confirmed
    CONTESTED = "CONTESTED"  # Contradicting evidence found


class StalenessRisk(StrEnum):
    """How likely is this evidence to be stale?"""

    LOW = "LOW"  # Static evidence (legal structure, geology)
    MODERATE = "MODERATE"  # Slowly changing (company filings, reserves)
    HIGH = "HIGH"  # Rapidly changing (market prices, health metrics)


# ═══════════════════════════════════════════════════════════════════════════════
# WITNESS LAYER — Raw evidence ingestion
# ═══════════════════════════════════════════════════════════════════════════════


class Witness(BaseModel):
    """A single piece of evidence — ingested, classified, not yet interpreted.

    Eureka 1: Reality is never directly held. Maps are not Earth.
    Seismic is not Earth. Financial reports are not institutions.
    They are witnesses.
    """

    witness_id: str = Field(description="Unique identifier for this witness")
    witness_type: WitnessType = Field(description="Category of evidence")
    source_uri: str = Field(default="", description="Where this evidence came from")
    raw_content: Any = Field(default=None, description="Raw evidence payload")
    ingested_at: str = Field(description="UTC timestamp of ingestion")
    session_id: str | None = Field(default=None, description="Session binding")
    provenance: str = Field(
        default="", description="Origin chain: who observed, how transmitted, any transforms"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# DECODED ENTITY LAYER — What the witness contains
# ═══════════════════════════════════════════════════════════════════════════════


class DecodedEntity(BaseModel):
    """A discrete object extracted from the witness.

    Eureka 2: The LLM should not just reply. It should process witnesses.
    ingest → decode → digest → encode → contextualize → verify → update memory
    """

    entity_id: str = Field(description="Unique decoded entity ID")
    entity_type: str = Field(description="Type: horizon, fault, anomaly, filing, ratio...")
    detected_at_depth: str | None = Field(
        default=None, description="Depth reference: MD, TVD, TVDSS — or temporal for non-spatial"
    )
    detected_value: Any = Field(default=None, description="The measured/detected value")
    detection_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence in detection (separate from meaning confidence!)",
    )
    perception_class: str = Field(
        default="MEASURED", description="MEASURED | DERIVED | DISPLAY | CORROBORATED | HYPOTHESIS"
    )
    evidence_tag: str = Field(
        default="UNKNOWN",
        description="EVIDENCE_DIRECT | EVIDENCE_MULTI_ZONE | INTERPRET_FROM_LITHOLOGY...",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ANOMALOUS CONTRAST LAYER — What differs from expectation
# ═══════════════════════════════════════════════════════════════════════════════


class AnomalousContrast(BaseModel):
    """A deviation from expected background.

    Eureka 3: Contrast is the birth of hypothesis.
    A hypothesis begins when something differs from expected background.

    In GEOX:    bright spot ≠ gas automatically
    In WEALTH:  profit decline + high dividend + debt rise ≠ fraud automatically
    In governance: UK incorporation + public silence ≠ illegality automatically
    """

    contrast_id: str = Field(description="Unique contrast ID, e.g. AC-001")
    contrast_domain: Literal["earth", "wealth", "institution", "health", "law", "system"] = Field(
        description="Which domain context"
    )
    background_expectation: str = Field(description="What the model expected before this witness")
    observed_deviation: str = Field(description="What was actually observed that differs")
    candidate_causes: list[str] = Field(
        default_factory=list, description="Possible explanations for the contrast"
    )
    false_positive_risks: list[str] = Field(
        default_factory=list, description="Known ways this contrast could be spurious"
    )
    required_verification: list[str] = Field(
        default_factory=list, description="What tests are needed before treating as real"
    )
    severity: ContrastSeverity = Field(default=ContrastSeverity.MODERATE)


# ═══════════════════════════════════════════════════════════════════════════════
# MEANING LAYER — What could this actually mean?
# ═══════════════════════════════════════════════════════════════════════════════


class CandidateMeaning(BaseModel):
    """Possible interpretations of a decoded entity.

    Eureka 6: Meaning is harder than perception.
    Horizon picking is not the highest intelligence.
    The harder question is: What does this horizon mean?

    NEVER allow: detected=true → meaning=proven
    """

    meaning_id: str = Field(description="Unique meaning ID")
    decoded_entity_id: str = Field(description="Which entity this meaning applies to")
    possible_meanings: list[str] = Field(
        default_factory=list, description="Differential interpretations — never just one"
    )
    primary_interpretation: str = Field(
        default="", description="Most likely meaning given current evidence"
    )
    meaning_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence in primary interpretation (separate from detection!)",
    )
    meaning_confidence_band: tuple[float, float] = Field(
        default=(0.0, 1.0), description="L07 HUMILITY: uncertainty range for this meaning claim"
    )
    tests_needed_before_claim: list[str] = Field(
        default_factory=list, description="What evidence would confirm or deny this interpretation"
    )
    ruling_out: list[str] = Field(
        default_factory=list, description="What other interpretations have been ruled out and why"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRAINT LAYER — Rules, physics, law, ethics
# ═══════════════════════════════════════════════════════════════════════════════


class ConstraintCheck(BaseModel):
    """A single constraint verified against the candidate meaning.

    Eureka 7: Abstraction without guard becomes hallucination.
    Institutional fault, capital pressure, governance leakage —
    useful abstractions but must be converted into testable claims.
    """

    constraint_id: str = Field(description="Which constraint was checked")
    constraint_type: str = Field(description="physics | law | ethics | financial | constitutional")
    rule_invoked: str = Field(description="Which rule or law is being applied")
    check_passed: bool = Field(
        default=False, description="Did the candidate meaning pass this constraint?"
    )
    failure_reason: str = Field(default="", description="If check failed, why")
    evidence_required: list[str] = Field(
        default_factory=list, description="What evidence was used to verify this constraint"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MODEL UPDATE LAYER — Before and after state
# ═══════════════════════════════════════════════════════════════════════════════


class ModelUpdate(BaseModel):
    """A proposed update to a Large Domain Model.

    Eureka 4: The true object is not the output; it is the model.
    GEOX should not produce "a map." It should update a Large Earth Model.
    WEALTH should not produce "a ratio." It should update a Large Capital Model.
    WELL should not produce "a health answer." It should update a Large Body Model.

    This is the real memory — not the output, but the updated state.
    """

    model_id: str = Field(description="Which model is being updated")
    model_type: Literal[
        "LargeEarthModel",
        "LargeWealthModel",
        "LargeInstitutionModel",
        "LargeBodyModel",
        "LargeSystemModel",
    ] = Field(description="Domain model classification")
    state_before: dict[str, Any] = Field(
        default_factory=dict, description="Model state before this witness was applied"
    )
    incoming_witnesses: list[str] = Field(
        default_factory=list, description="Which witness IDs contributed to this update"
    )
    proposed_updates: list[dict[str, Any]] = Field(
        default_factory=list, description="Specific field-level changes proposed to the model"
    )
    constraints_checked: list[str] = Field(
        default_factory=list, description="Which constraints were verified before accepting update"
    )
    state_after: dict[str, Any] = Field(
        default_factory=dict, description="Model state after this witness was applied"
    )
    confidence_delta: float = Field(
        default=0.0, description="Change in model confidence from this update"
    )
    audit_receipt: str = Field(default="", description="VAULT999 reference for this model update")


# ═══════════════════════════════════════════════════════════════════════════════
# ABSTRACTION GUARD LAYER — Preventing metaphor → hallucination
# ═══════════════════════════════════════════════════════════════════════════════


class AbstractionGuard(BaseModel):
    """Guard against metaphor being used as proof.

    Eureka 7: Analogy is powerful but dangerous.
    Example: institutional fault, capital pressure, governance leakage.
    These are useful abstractions but must be testable claims.

    metaphor → literal claim → evidence needed → allowed status
    """

    metaphor: str = Field(description="The figurative language or abstraction being guarded")
    literal_claim: str = Field(description="What the metaphor translates to as a testable claim")
    evidence_required: list[str] = Field(
        default_factory=list, description="What evidence is needed to support this claim"
    )
    allowed_use: AbstractionUse = Field(
        default=AbstractionUse.HEURISTIC,
        description="How this abstraction can legitimately be used",
    )
    misuse_risk: str = Field(
        default="", description="Known risks if this metaphor is over-extended"
    )
    violations: list[str] = Field(
        default_factory=list, description="If metaphor was misused as proof, what was violated"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# UNCERTAINTY LAYER — L07 HUMILITY
# ═══════════════════════════════════════════════════════════════════════════════


class UncertaintyBand(BaseModel):
    """Uncertainty quantification for this metabolic output.

    L07 HUMILITY: Confidence must be labeled honestly.
    No fake certainty.
    """

    omega_0: float = Field(default=0.05, ge=0.0, le=1.0, description="Base uncertainty (Ω₀)")
    uncertainty_range: tuple[float, float] = Field(
        default=(0.0, 1.0), description="Honest range of confidence"
    )
    major_unknowns: list[str] = Field(
        default_factory=list, description="What key variables are unconstrained"
    )
    key_missing_evidence: list[str] = Field(
        default_factory=list, description="What evidence would most reduce uncertainty"
    )
    claim_too_certain_flag: bool = Field(
        default=False, description="Was the model tempted to overclaim? Flag for human review."
    )


# ═══════════════════════════════════════════════════════════════════════════════
# EVIDENCE FRESHNESS — Eureka 10 §8
# Evidence expiry and staleness tracking
# ═══════════════════════════════════════════════════════════════════════════════


class EvidenceFreshness(BaseModel):
    """
    Evidence freshness tracking — prevents stale intelligence from guiding action.

    Eureka 10 §8: Evidence freshness and decay.
    Some evidence has a short half-life:
      market prices, health metrics, company registry status, production numbers.

    The system must track when evidence was collected and when it expires.
    """

    as_of: str = Field(description="UTC timestamp when evidence was collected")
    expires_after_seconds: int | None = Field(
        default=None, description="Seconds after which this evidence is considered stale"
    )
    staleness_risk: StalenessRisk = Field(
        default=StalenessRisk.MODERATE, description="Likely rate of evidence decay"
    )
    requires_refresh: bool = Field(
        default=False, description="Should this evidence be re-fetched before use?"
    )
    refresh_recommendation: str = Field(
        default="", description="Human-readable recommendation for refresh"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CROSS-ORGAN HANDOFF — Eureka 10 §4
# Formal handoff contract between organs
# ═══════════════════════════════════════════════════════════════════════════════


class CrossOrganHandoff(BaseModel):
    """
    Formal handoff packet when one organ passes work to another.

    Eureka 10 §4: Cross-organ handoff contract.

    Example chain:
      GEOX (finds resource significance)
        → WEALTH (evaluates capital consequence)
        → WELL (checks Arif readiness)
        → arifOS (judges route)
        → VAULT (seals)

    Every organ output should declare: where should this go next?
    """

    next_best_organ: OrganType = Field(description="Which organ should receive this output next")
    handoff_reason: str = Field(
        default="", description="Why this organ? What can it add that this organ cannot?"
    )
    handoff_payload: dict[str, Any] = Field(
        default_factory=dict, description="Structured data to pass to the next organ"
    )
    blocked_organs: list[OrganType] = Field(
        default_factory=list,
        description="Which organs should NOT receive this (conflict, capture risk)",
    )
    blocked_reason: str = Field(default="", description="Why each blocked organ was excluded")
    confidence_at_handoff: ConfidenceLevel = Field(
        default=ConfidenceLevel.MODERATE, description="Confidence level at handoff"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ORGAN CONFLICT — Eureka 10 §9
# Detects when organs disagree
# ═══════════════════════════════════════════════════════════════════════════════


class OrganConflict(BaseModel):
    """
    Record of a conflict between organ conclusions.

    Eureka 10 §9: Conflict scanner.

    Example:
      GEOX:  asset is technically strategic
      WEALTH: deal structure is economically defensible
      arifOS: governance transparency is insufficient
      WELL:   public action readiness is low

    Result: PARTIAL / HOLD — not a forced conclusion.
    """

    conflict_id: str = Field(description="Unique conflict identifier")
    organ_a: OrganType = Field(description="First organ in conflict")
    organ_a_conclusion: str = Field(description="What organ A concluded")
    organ_b: OrganType = Field(description="Second organ in conflict")
    organ_b_conclusion: str = Field(description="What organ B concluded")
    conflict_domain: str = Field(
        default="", description="earth | wealth | governance | health | law | system"
    )
    resolution_status: Literal["OPEN", "PARTIAL", "RESOLVED", "ESCALATED"] = Field(
        default="OPEN", description="Current resolution state"
    )
    partial_flag: bool = Field(
        default=False, description="True if this conflict means output should be PARTIAL not FORCED"
    )
    recommended_action: str = Field(
        default="", description="What should happen given this conflict"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# METABOLIC OUTPUT — The universal contract
# ═══════════════════════════════════════════════════════════════════════════════


class MetabolicOutput(BaseModel):
    """
    Universal metabolic output contract for all organs.

    Eureka 10: Forge this into the MCP system.

    This is the loop closer — the thing that was missing.

    witness → meaning → verification → model update → judgment

    Every organ (GEOX, WEALTH, WELL, arifOS) should output this structure.
    It captures:
      - What evidence was ingested
      - What it means (with alternatives)
      - What anomalies were found
      - What constraints were checked
      - How the model changed (before → after)
      - What remains unknown
      - What the human must judge before action
    """

    # ── Identity ──────────────────────────────────────────────────────────────
    organ: OrganType = Field(description="Which organ produced this output")
    tool_name: str = Field(default="", description="Which MCP tool generated this output")
    session_id: str | None = Field(default=None)

    # ── Witness layer ──────────────────────────────────────────────────────────
    witnesses_ingested: list[Witness] = Field(
        default_factory=list, description="Raw evidence received in this metabolic cycle"
    )
    witness_type: WitnessType | None = Field(default=None, description="Primary witness category")
    witness_status: WitnessStatus = Field(
        default=WitnessStatus.RAW,
        description="Lifecycle stage: RAW → DECODED → INTERPRETED → VERIFIED → CONTESTED",
    )

    # ── Decoded layer ─────────────────────────────────────────────────────────
    decoded_entities: list[DecodedEntity] = Field(
        default_factory=list, description="Objects extracted from witnesses"
    )

    # ── Contrast layer ────────────────────────────────────────────────────────
    anomalous_contrasts: list[AnomalousContrast] = Field(
        default_factory=list, description="Deviations from expected background"
    )

    # ── Meaning layer ─────────────────────────────────────────────────────────
    candidate_meanings: list[CandidateMeaning] = Field(
        default_factory=list, description="Possible interpretations (never a single claim)"
    )

    # ── Constraint layer ──────────────────────────────────────────────────────
    constraints_checked: list[ConstraintCheck] = Field(
        default_factory=list, description="Rules, physics, law, ethics verified"
    )

    # ── Model update layer ────────────────────────────────────────────────────
    model_updates: list[ModelUpdate] = Field(
        default_factory=list, description="Proposed state changes to domain models"
    )
    model_target: ModelTarget | None = Field(
        default=None, description="Which domain model was updated"
    )

    # ── Abstraction guard ─────────────────────────────────────────────────────
    abstraction_guard: AbstractionGuard | None = Field(
        default=None, description="If metaphors were used, guard against hallucination"
    )

    # ── Uncertainty ────────────────────────────────────────────────────────────
    uncertainty: UncertaintyBand = Field(
        default_factory=UncertaintyBand, description="Honest uncertainty quantification (L07)"
    )

    # ── Evidence freshness ────────────────────────────────────────────────────
    evidence_freshness: EvidenceFreshness | None = Field(
        default=None, description="Evidence expiry and staleness tracking (Eureka 10 §8)"
    )

    # ── Required next steps ────────────────────────────────────────────────────
    required_next_tests: list[str] = Field(
        default_factory=list, description="What tests would most improve confidence"
    )
    next_best_tool: str = Field(
        default="", description="Which tool should be called next to advance understanding"
    )

    # ── Cross-organ handoff ───────────────────────────────────────────────────
    cross_organ_handoff: CrossOrganHandoff | None = Field(
        default=None,
        description="Formal handoff packet to next organ (Eureka 10 §4)",
    )

    # ── Claim state ────────────────────────────────────────────────────────────
    claim_state: ClaimState = Field(
        default=ClaimState.HYPOTHESIS, description="Where does this sit in the evidence lifecycle?"
    )

    # ── Conflict flags ─────────────────────────────────────────────────────────
    conflict_flags: list[OrganConflict] = Field(
        default_factory=list,
        description="Detected disagreements between organ conclusions (Eureka 10 §9)",
    )

    # ── Confidence level (shared policy) ───────────────────────────────────────
    confidence_level: ConfidenceLevel = Field(
        default=ConfidenceLevel.MODERATE,
        description=(
            "Shared confidence language: UNKNOWN/LOW/MODERATE/HIGH/VERIFIED/SEALED (Eureka 10 §7)"
        ),
    )

    # ── Audit ─────────────────────────────────────────────────────────────────
    audit_receipt: str = Field(
        default="", description="VAULT999 reference for this metabolic cycle"
    )

    # ── SOVEREIGNTY BOUNDARY (Eureka 8) ───────────────────────────────────────
    # AI proposes. Tools compute. Memory records. Constraints guard. Arif judges.
    #
    # Every output must contain this — especially for:
    #   public disclosure, employment action, financial allocation,
    #   health decision, legal escalation, irreversible deployment
    recommendation_only: bool = Field(
        default=True, description="AI proposes only — has not been ratified by human"
    )
    execution_authorized: bool = Field(
        default=False, description="Has a human authorized execution? False until L13 ratification."
    )
    human_final_authority: str = Field(
        default="Arif", description="Who has final say on this output?"
    )
    requires_888_judge: bool = Field(
        default=False, description="Does this output require 888_JUDGE before action?"
    )

    # ── Provenance ─────────────────────────────────────────────────────────────
    timestamp_utc: str = Field(description="UTC timestamp of this output")
    constitution_hash: str = Field(
        default="", description="Constitutional law version this output was generated under"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "Governed Witness Metabolism Output — "
                "Intelligence is not answer generation. "
                "Intelligence is governed witness metabolism. "
                "DITEMPA BUKAN DIBERI"
            )
        }
    )


# ═══════════════════════════════════════════════════════════════════════════════
# METABOLIC CYCLE — Full witness → judgment loop record
# ═══════════════════════════════════════════════════════════════════════════════


class MetabolicCycle(BaseModel):
    """
    Complete record of one full metabolic cycle.

    Useful for auditing and for continuing interrupted sessions.
    """

    cycle_id: str = Field(description="Unique cycle identifier")
    organ: OrganType
    session_id: str | None = None

    # Steps in order
    witness_ingest: list[Witness] = Field(default_factory=list)
    visual_decode: list[DecodedEntity] = Field(default_factory=list)
    anomalous_contrast: list[AnomalousContrast] = Field(default_factory=list)
    meaning_generate: list[CandidateMeaning] = Field(default_factory=list)
    constraint_verify: list[ConstraintCheck] = Field(default_factory=list)
    model_update: list[ModelUpdate] = Field(default_factory=list)

    # Final state
    final_output: MetabolicOutput | None = None
    claim_state: ClaimState = ClaimState.HYPOTHESIS

    # Sovereignty
    recommendation_only: bool = True
    execution_authorized: bool = False
    human_final_authority: str = "Arif"
    requires_888_judge: bool = False

    # Audit
    timestamp_utc: str = ""
    total_steps: int = 0
