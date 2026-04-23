"""
arifosmcp/runtime/sensing_protocol.py — Governed Sensing Protocol — 8-Stage Constitutional
═══════════════════════════════════════════════════════════════════════════════

Constitutional sensing protocol for arifos.sense — CANONICAL SEAL VERSION.

Stage: 111_SENSE | Trinity: DELTA Δ | Floors: F2, F3, F4, F7, F8, F10

Implements the 8-stage constitutional sensing flow:
    1. PARSE    → Extract entities, intent, time-dependence, risk, jurisdiction
    2. CLASSIFY → Route to truth-class lane (7 classes)
    3. DECIDE   → Whether search is needed based on class
    4. PLAN     → Build evidence hierarchy (7 ranks)
    5. SENSE    → Execute constrained retrieval (web search gated by classification)
    6. NORMALIZE→ Convert to structured claims with provenance
    7. GATE     → Assess uncertainty, ambiguity, conflict
    8. HANDOFF  → Route to next stage with state delta

Web Search Integration
──────────────────────
Live web search is a *subordinate acquisition backend*, not the brain.
The protocol decides IF search runs:
    absolute_invariant / conditional_invariant / operational_principle
        → offline reasoning only (no web call)
    time_sensitive_fact / contested_framework (when grounding is needed)
        → web_search lane activated
    ambiguous_query / unknown
        → HOLD (narrow first, never search blind)

A WebSearchProvider protocol wraps the actual search engine so the
governing logic stays invariant even when the backend changes.

Author: Arif (Sovereign Architect)
Constitutional Seal: 999_VALIDATOR
Version: 2.1.0 — CANONICAL + LIVE SEARCH
"""

from __future__ import annotations

import hashlib
import logging
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Protocol, runtime_checkable

from arifosmcp.runtime.philosophy_registry import select_philosophy_state

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# PARSING LIMITS — Zero-Day Mitigation (Category 5)
# Prevents parser/resource weirdness and schema smuggling
# ═══════════════════════════════════════════════════════════════════════════════

_MAX_QUERY_LENGTH = 10000  # Max raw query string length
_MAX_ENTITIES = 50  # Max entity list size
_MAX_CLAIMS = 100  # Max claim target list size
_MAX_EVIDENCE = 200  # Max evidence items list size
_MAX_NESTED_DEPTH = 10  # Max nested object depth
_MAX_STRING_FIELD_LENGTH = 5000  # Max individual string field length
_MAX_LIST_FIELD_LENGTH = 100  # Max list field size
_PARSER_TIMEOUT_SECONDS = 5.0  # Max time for any parsing operation


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMERATIONS — Constitutional Classification
# ═══════════════════════════════════════════════════════════════════════════════


class ExplorationState(str, Enum):
    """Cognitive exploration posture."""

    NARROW = "NARROW"
    BROAD = "BROAD"
    FOCUSED = "FOCUSED"


class EntropyState(str, Enum):
    """Information entropy assessment."""

    LOW = "LOW"
    MANAGEABLE = "MANAGEABLE"
    HIGH = "HIGH"


class EurekaState(str, Enum):
    """Insight emergence detection."""

    NONE = "NONE"
    EMERGING = "EMERGING"
    STRONG = "STRONG"


class TruthClass(str, Enum):
    """Seven truth classification lanes."""

    ABSOLUTE_INVARIANT = "absolute_invariant"  # Lane A: Logic, math, physics
    CONDITIONAL_INVARIANT = "conditional_invariant"  # Lane B: Frame-dependent truths
    OPERATIONAL_PRINCIPLE = "operational_principle"  # Lane C: Strategy, governance
    TIME_SENSITIVE_FACT = "time_sensitive_fact"  # Lane D: Current events, live data
    CONTESTED_FRAMEWORK = "contested_framework"  # Lane F: Axiom-dependent, ideological
    AMBIGUOUS_QUERY = "ambiguous_query"  # Lane G: Frame unresolved
    UNKNOWN = "unknown"  # Lane H: Insufficient basis


class TaskType(str, Enum):
    """User intent classification."""

    DEFINE = "define"
    VERIFY = "verify"
    COMPARE = "compare"
    LOCATE = "locate"
    MONITOR = "monitor"
    EXPLAIN = "explain"
    CLASSIFY = "classify"
    UNKNOWN = "unknown"


class DecisionProximity(str, Enum):
    """Consequence proximity of the query."""

    INFORMATIONAL = "informational"
    PREPARATORY = "preparatory"
    DECISION_CRITICAL = "decision_critical"


class TimeScope(str, Enum):
    """Temporal classification."""

    TIMELESS = "timeless"
    HISTORICAL = "historical"
    DATED = "dated"
    LIVE = "live"
    FORECAST = "forecast"


class InputType(str, Enum):
    """Input modality."""

    QUERY = "query"
    URL = "url"
    BUNDLE = "bundle"
    ARTIFACT = "artifact"
    TIME = "time"


class SensingMode(str, Enum):
    """Sensing execution modes."""

    SEARCH = "search"
    INGEST = "ingest"
    COMPASS = "compass"
    ATLAS = "atlas"
    TIME = "time"
    GOVERNED = "governed"


class EvidenceRank(int, Enum):
    """Seven-tier evidence hierarchy — constitutional rank."""

    DIRECT_MEASUREMENT = 1  # Sensors, primary data
    PRIMARY_SOURCE = 2  # Original documents, raw data
    OFFICIAL_ISSUER = 3  # Current authority on subject
    TECHNICAL_DOCUMENTATION = 4  # Specs, standards, methods
    REPUTABLE_SECONDARY = 5  # Vetted summaries, analysis
    AGGREGATOR_OR_INDEX = 6  # Search engines, databases
    SOCIAL_OR_UNVERIFIED = 7  # Social media, unvetted claims


class AmbiguityType(str, Enum):
    """Seven ambiguity categories."""

    ENTITY = "entity"
    TIMEFRAME = "timeframe"
    JURISDICTION = "jurisdiction"
    DEFINITION = "definition"
    METRIC = "metric"
    REFERENT = "referent"
    INTENT = "intent"


class ConflictType(str, Enum):
    """Six conflict categories."""

    SOURCE_DISAGREEMENT = "source_disagreement"
    TEMPORAL_MISMATCH = "temporal_mismatch"
    DEFINITIONAL_MISMATCH = "definitional_mismatch"
    JURISDICTION_MISMATCH = "jurisdiction_mismatch"
    MEASUREMENT_MISMATCH = "measurement_mismatch"
    VERSION_MISMATCH = "version_mismatch"


class UncertaintyLevel(str, Enum):
    """Epistemic uncertainty bands."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"


class StalenessRisk(str, Enum):
    """Temporal staleness assessment."""

    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class ClaimType(str, Enum):
    """Claim categorization."""

    DEFINITION = "definition"
    STATUS = "status"
    EVENT = "event"
    RELATIONSHIP = "relationship"
    MEASUREMENT = "measurement"
    RULE = "rule"
    PREDICTION = "prediction"
    UNKNOWN = "unknown"


class Polarity(str, Enum):
    """Claim polarity."""

    AFFIRM = "affirm"
    DENY = "deny"
    QUESTION = "question"
    COMPARE = "compare"
    ESTIMATE = "estimate"


class EntityType(str, Enum):
    """Entity categorization."""

    PERSON = "person"
    COMPANY = "company"
    PLACE = "place"
    CONCEPT = "concept"
    LAW = "law"
    PRODUCT = "product"
    DOCUMENT = "document"
    UNKNOWN = "unknown"


class ResolutionStatus(str, Enum):
    """Conflict resolution state."""

    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"
    PARTIALLY_RESOLVED = "partially_resolved"


class QualityFlag(str, Enum):
    """Evidence quality markers."""

    PRIMARY = "primary"
    OFFICIAL = "official"
    STALE = "stale"
    PAYWALLED = "paywalled"
    CONFLICTING = "conflicting"
    INCOMPLETE = "incomplete"
    MIRRORED = "mirrored"


class RoutingTarget(str, Enum):
    """Downstream routing destinations."""

    MIND = "arifos.mind"
    HEART = "arifos.heart"
    JUDGE = "arifos.judge"
    HOLD = "hold"


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES — Intelligence State (Whole-State Alignment)
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class TruthVector:
    """
    Constitutional physics vector for truth assessment.

    grounding_g: Grounding score (how well evidence supports claim)
    truth_tau: Truth integrity (internal consistency)
    uncertainty_sigma: Residual uncertainty (what remains unknown)
    coherence_c: Coherence/consistency across sources
    entropy_delta_s: Local entropic effect estimate (ΔS ≤ 0 principle)
    humility_omega0: Humility/confidence cap (Ω₀ band)
    """

    grounding_g: float = 0.0
    truth_tau: float = 0.0
    uncertainty_sigma: float = 1.0
    coherence_c: float = 0.0
    entropy_delta_s: float = 0.0
    humility_omega0: float = 0.5

    def to_dict(self) -> dict[str, float]:
        return {
            "grounding_g": round(self.grounding_g, 4),
            "truth_tau": round(self.truth_tau, 4),
            "uncertainty_sigma": round(self.uncertainty_sigma, 4),
            "coherence_c": round(self.coherence_c, 4),
            "entropy_delta_s": round(self.entropy_delta_s, 4),
            "humility_omega0": round(self.humility_omega0, 4),
        }


@dataclass
class IntelligenceState:
    """
    Live state of cognition at the moment sense finishes.

    This aligns sense to the full constitutional state, not just retrieval.
    Downstream tools inherit the epistemic posture, not only the data.
    """

    exploration: ExplorationState = ExplorationState.NARROW
    entropy: EntropyState = EntropyState.MANAGEABLE
    eureka: EurekaState = EurekaState.NONE
    confidence: float = 0.5
    uncertainty_score: float = 0.5
    stable_facts: list[str] = field(default_factory=list)
    unstable_assumptions: list[str] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    decision_required: list[str] = field(default_factory=list)
    truth_vector: TruthVector = field(default_factory=TruthVector)

    def to_dict(self) -> dict[str, Any]:
        return {
            "exploration": self.exploration.value,
            "entropy": self.entropy.value,
            "eureka": self.eureka.value,
            "confidence": round(self.confidence, 4),
            "uncertainty_score": round(self.uncertainty_score, 4),
            "stable_facts": self.stable_facts,
            "unstable_assumptions": self.unstable_assumptions,
            "unknowns": self.unknowns,
            "conflicts": self.conflicts,
            "decision_required": self.decision_required,
            "truth_vector": self.truth_vector.to_dict(),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES — Input Contract
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class InputSpec:
    """Input specification."""

    type: InputType = InputType.QUERY
    value: str = ""
    mode: SensingMode = SensingMode.GOVERNED


@dataclass
class IntentSpec:
    """Intent specification."""

    task_type: TaskType = TaskType.UNKNOWN
    user_goal: str | None = None
    decision_proximity: DecisionProximity = DecisionProximity.INFORMATIONAL


@dataclass
class EntityRef:
    """Entity reference."""

    name: str
    type: EntityType = EntityType.UNKNOWN
    canonical_id: str | None = None
    aliases: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type.value,
            "canonical_id": self.canonical_id,
            "aliases": self.aliases,
        }


@dataclass
class ClaimTarget:
    """Target claim specification."""

    text: str
    polarity: Polarity = Polarity.QUESTION
    claim_type: ClaimType = ClaimType.UNKNOWN

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "polarity": self.polarity.value,
            "claim_type": self.claim_type.value,
        }


@dataclass
class QueryFrame:
    """Query framing context."""

    domain: str = "unknown"
    time_scope: TimeScope = TimeScope.TIMELESS
    jurisdiction: str | None = None
    entity_targets: list[EntityRef] = field(default_factory=list)
    claim_targets: list[ClaimTarget] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "domain": self.domain,
            "time_scope": self.time_scope.value,
            "jurisdiction": self.jurisdiction,
            "entity_targets": [e.to_dict() for e in self.entity_targets],
            "claim_targets": [c.to_dict() for c in self.claim_targets],
        }


@dataclass
class PolicySpec:
    """Sensing policy constraints."""

    obey_robots: bool = True
    allow_paywalls: bool = False
    allow_login: bool = False
    max_redirects: int = 10
    max_hops: int = 3
    freshness_max_age_days: int | None = None
    min_evidence_rank: int | None = None
    offline_first: bool = False
    fail_closed: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "obey_robots": self.obey_robots,
            "allow_paywalls": self.allow_paywalls,
            "allow_login": self.allow_login,
            "max_redirects": self.max_redirects,
            "max_hops": self.max_hops,
            "freshness_max_age_days": self.freshness_max_age_days,
            "min_evidence_rank": self.min_evidence_rank,
            "offline_first": self.offline_first,
            "fail_closed": self.fail_closed,
        }


@dataclass
class BudgetSpec:
    """Resource budget constraints."""

    top_k: int = 5
    fetch_top_k: int = 2
    budget_ms: int = 15000
    token_budget: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "top_k": self.top_k,
            "fetch_top_k": self.fetch_top_k,
            "budget_ms": self.budget_ms,
            "token_budget": self.token_budget,
        }


@dataclass
class ActorSpec:
    """Actor/authority specification."""

    actor_id: str = "anonymous"
    auth_state: str = "unverified"
    authority_level: str = "anonymous"

    def to_dict(self) -> dict[str, Any]:
        return {
            "actor_id": self.actor_id,
            "auth_state": self.auth_state,
            "authority_level": self.authority_level,
        }


@dataclass
class SenseInput:
    """
    Canonical sense input contract.

    Backward compatible: simple string query auto-normalizes to full structure.
    """

    input: InputSpec = field(default_factory=InputSpec)
    intent: IntentSpec = field(default_factory=IntentSpec)
    query_frame: QueryFrame = field(default_factory=QueryFrame)
    policy: PolicySpec = field(default_factory=PolicySpec)
    budget: BudgetSpec = field(default_factory=BudgetSpec)
    actor: ActorSpec = field(default_factory=ActorSpec)

    def to_dict(self) -> dict[str, Any]:
        return {
            "input": {
                "type": self.input.type.value,
                "value": self.input.value,
                "mode": self.input.mode.value,
            },
            "intent": {
                "task_type": self.intent.task_type.value,
                "user_goal": self.intent.user_goal,
                "decision_proximity": self.intent.decision_proximity.value,
            },
            "query_frame": self.query_frame.to_dict(),
            "policy": self.policy.to_dict(),
            "budget": self.budget.to_dict(),
            "actor": self.actor.to_dict(),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES — Truth Classification
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class TruthClassification:
    """
    Truth classification block — heart of governed sensing.

    Determines whether and how to search based on the nature of the query.
    """

    truth_class: TruthClass = TruthClass.UNKNOWN
    search_required: bool = False
    search_reason: str | None = None
    framework_dependency: bool = False
    framework_note: str | None = None
    temporal_dependency: bool = False
    temporal_note: str | None = None
    classification_confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "truth_class": self.truth_class.value,
            "search_required": self.search_required,
            "search_reason": self.search_reason,
            "framework_dependency": self.framework_dependency,
            "framework_note": self.framework_note,
            "temporal_dependency": self.temporal_dependency,
            "temporal_note": self.temporal_note,
            "classification_confidence": round(self.classification_confidence, 4),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES — Evidence Planning
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class FreshnessRequirement:
    """Temporal freshness constraints."""

    required: bool = False
    max_age_days: int | None = None
    reference_time: str | None = None


@dataclass
class CorroborationSpec:
    """Multi-source corroboration requirements."""

    min_distinct_sources: int = 2
    require_primary_if_available: bool = True


@dataclass
class ConflictPolicy:
    """Conflict resolution policy."""

    mode: str = "prefer_higher_rank"  # or: prefer_newer_if_same_rank, hold_on_conflict, summarize_disagreement


@dataclass
class EvidencePlan:
    """
    Evidence gathering plan based on classification.

    Constrained retrieval: only fetch what meets the plan.
    """

    retrieval_lane: str = "hold"  # offline_reason | web_search | url_ingest | mixed | hold
    preferred_sources: list[str] = field(default_factory=list)
    banned_sources: list[str] = field(default_factory=list)
    min_rank_required: int = 5
    freshness_requirement: FreshnessRequirement = field(default_factory=FreshnessRequirement)
    corroboration: CorroborationSpec = field(default_factory=CorroborationSpec)
    conflict_policy: ConflictPolicy = field(default_factory=ConflictPolicy)

    def to_dict(self) -> dict[str, Any]:
        return {
            "retrieval_lane": self.retrieval_lane,
            "preferred_sources": self.preferred_sources,
            "banned_sources": self.banned_sources,
            "min_rank_required": self.min_rank_required,
            "freshness_requirement": {
                "required": self.freshness_requirement.required,
                "max_age_days": self.freshness_requirement.max_age_days,
                "reference_time": self.freshness_requirement.reference_time,
            },
            "corroboration": {
                "min_distinct_sources": self.corroboration.min_distinct_sources,
                "require_primary_if_available": self.corroboration.require_primary_if_available,
            },
            "conflict_policy": {"mode": self.conflict_policy.mode},
        }


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES — Temporal Grounding
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class TemporalGrounding:
    """
    Temporal grounding block.

    Essential because sense is not just "what sources say",
    but what they say relative to time.
    """

    query_time_class: TimeScope = TimeScope.TIMELESS
    detected_dates: list[str] = field(default_factory=list)
    effective_reference_time: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    freshness_required: bool = False
    staleness_risk: StalenessRisk = StalenessRisk.NONE
    temporal_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "query_time_class": self.query_time_class.value,
            "detected_dates": self.detected_dates,
            "effective_reference_time": self.effective_reference_time,
            "freshness_required": self.freshness_required,
            "staleness_risk": self.staleness_risk.value,
            "temporal_notes": self.temporal_notes,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES — Ambiguity, Conflict, Uncertainty
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class AmbiguityModel:
    """
    Ambiguity detection and containment.

    Ambiguity must be surfaced, not hidden.
    """

    detected: bool = False
    ambiguity_type: list[AmbiguityType] = field(default_factory=list)
    candidate_interpretations: list[str] = field(default_factory=list)
    chosen_interpretation: str | None = None
    assumption_disclosed: bool = False
    needs_human_narrowing: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "detected": self.detected,
            "ambiguity_type": [t.value for t in self.ambiguity_type],
            "candidate_interpretations": self.candidate_interpretations,
            "chosen_interpretation": self.chosen_interpretation,
            "assumption_disclosed": self.assumption_disclosed,
            "needs_human_narrowing": self.needs_human_narrowing,
        }


@dataclass
class ConflictModel:
    """
    Conflict detection and resolution.

    Conflict is signal, not noise. Do not average blindly.
    """

    detected: bool = False
    conflict_type: list[ConflictType] = field(default_factory=list)
    conflict_summary: str | None = None
    resolution_status: ResolutionStatus = ResolutionStatus.RESOLVED
    resolution_method: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "detected": self.detected,
            "conflict_type": [t.value for t in self.conflict_type],
            "conflict_summary": self.conflict_summary,
            "resolution_status": self.resolution_status.value,
            "resolution_method": self.resolution_method,
        }


@dataclass
class UncertaintyBasis:
    """Five-dimensional uncertainty basis."""

    evidence_quality: float = 0.0
    source_agreement: float = 0.0
    temporal_alignment: float = 0.0
    frame_clarity: float = 0.0
    model_fit: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {
            "evidence_quality": round(self.evidence_quality, 4),
            "source_agreement": round(self.source_agreement, 4),
            "temporal_alignment": round(self.temporal_alignment, 4),
            "frame_clarity": round(self.frame_clarity, 4),
            "model_fit": round(self.model_fit, 4),
        }


@dataclass
class UncertaintyBand:
    """
    Uncertainty band with Ω₀ humility integration.

    Uncertainty must remain explicit. Confidence capped by humility.
    """

    level: UncertaintyLevel = UncertaintyLevel.HIGH
    sigma: float = 1.0
    omega0_cap: float = 0.5
    basis: UncertaintyBasis = field(default_factory=UncertaintyBasis)
    narrative_note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level.value,
            "sigma": round(self.sigma, 4),
            "omega0_cap": round(self.omega0_cap, 4),
            "basis": self.basis.to_dict(),
            "narrative_note": self.narrative_note,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES — Evidence Items
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class ExtractedClaim:
    """Claim extracted from evidence."""

    claim_text: str
    claim_type: ClaimType = ClaimType.UNKNOWN
    supports_target: bool | None = None
    confidence: float = 0.5

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim_text": self.claim_text,
            "claim_type": self.claim_type.value,
            "supports_target": self.supports_target,
            "confidence": round(self.confidence, 4),
        }


@dataclass
class EvidenceItem:
    """
    Normalized evidence item with full provenance.

    Required for downstream traceability and constitutional audit.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source_name: str = ""
    source_type: str = ""
    source_rank: int = 7
    url: str | None = None
    title: str | None = None
    issuer: str | None = None
    author: str | None = None
    published_at: str | None = None
    observed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    jurisdiction: str | None = None
    version: str | None = None
    extracted_claims: list[ExtractedClaim] = field(default_factory=list)
    snippets: list[str] = field(default_factory=list)
    provenance_hash: str | None = None
    quality_flags: list[QualityFlag] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source_name": self.source_name,
            "source_type": self.source_type,
            "source_rank": self.source_rank,
            "url": self.url,
            "title": self.title,
            "issuer": self.issuer,
            "author": self.author,
            "published_at": self.published_at,
            "observed_at": self.observed_at,
            "jurisdiction": self.jurisdiction,
            "version": self.version,
            "extracted_claims": [c.to_dict() for c in self.extracted_claims],
            "snippets": self.snippets,
            "provenance_hash": self.provenance_hash,
            "quality_flags": [f.value for f in self.quality_flags],
        }


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES — Normalized Findings
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class NormalizedFindings:
    """
    Structured findings from evidence processing.

    Not raw links. Normalized observations ready for downstream reasoning.
    """

    grounded_facts: list[str] = field(default_factory=list)
    unresolved_questions: list[str] = field(default_factory=list)
    assumptions_made: list[str] = field(default_factory=list)
    rejected_claims: list[str] = field(default_factory=list)
    contested_points: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "grounded_facts": self.grounded_facts,
            "unresolved_questions": self.unresolved_questions,
            "assumptions_made": self.assumptions_made,
            "rejected_claims": self.rejected_claims,
            "contested_points": self.contested_points,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES — Routing and Handoff
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class RoutingDecision:
    """
    Deterministic routing to next stage.

    Must be explicit, not implied.
    """

    next_stage: RoutingTarget = RoutingTarget.HOLD
    route_reason: str = ""
    requires_human_decision: bool = False
    requires_live_verification: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "next_stage": self.next_stage.value,
            "route_reason": self.route_reason,
            "requires_human_decision": self.requires_human_decision,
            "requires_live_verification": self.requires_live_verification,
        }


@dataclass
class StateUpdate:
    """
    Delta update to intelligence state.

    What changed as a result of this sensing operation.
    """

    stable_facts_delta: list[str] = field(default_factory=list)
    unknowns_delta: list[str] = field(default_factory=list)
    conflicts_delta: list[str] = field(default_factory=list)
    confidence_delta: float = 0.0
    uncertainty_delta: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "stable_facts_delta": self.stable_facts_delta,
            "unknowns_delta": self.unknowns_delta,
            "conflicts_delta": self.conflicts_delta,
            "confidence_delta": round(self.confidence_delta, 4),
            "uncertainty_delta": round(self.uncertainty_delta, 4),
        }


@dataclass
class HandoffSpec:
    """
    Handoff specification for downstream consumption.
    """

    packet_type: str = "sense_packet@v2"
    consumable_by: list[str] = field(
        default_factory=lambda: ["arifos.mind", "arifos.heart", "arifos.judge"]
    )
    state_update: StateUpdate = field(default_factory=StateUpdate)

    def to_dict(self) -> dict[str, Any]:
        return {
            "packet_type": self.packet_type,
            "consumable_by": self.consumable_by,
            "state_update": self.state_update.to_dict(),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES — Input Summary
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class InputSummary:
    """Summary of input processing."""

    raw_query: str | None = None
    normalized_query: str | None = None
    mode_used: str = "governed"
    domain: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "raw_query": self.raw_query,
            "normalized_query": self.normalized_query,
            "mode_used": self.mode_used,
            "domain": self.domain,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES — Canonical SensePacket
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class SensePacket:
    """
    Canonical SensePacket — the full output of governed sensing.

    This is not raw search results. This is a structured, bounded,
    time-aware, source-ranked, uncertainty-tagged observation packet.
    """

    packet_id: str = field(default_factory=lambda: f"spk_{uuid.uuid4().hex[:12]}")
    stage: str = "111_SENSE"

    input_summary: InputSummary = field(default_factory=InputSummary)
    truth_classification: TruthClassification = field(default_factory=TruthClassification)
    temporal_grounding: TemporalGrounding = field(default_factory=TemporalGrounding)
    ambiguity: AmbiguityModel = field(default_factory=AmbiguityModel)
    conflict: ConflictModel = field(default_factory=ConflictModel)
    uncertainty: UncertaintyBand = field(default_factory=UncertaintyBand)
    evidence_plan: EvidencePlan = field(default_factory=EvidencePlan)

    entities: list[EntityRef] = field(default_factory=list)
    target_claims: list[ClaimTarget] = field(default_factory=list)
    evidence_items: list[EvidenceItem] = field(default_factory=list)

    normalized_findings: NormalizedFindings = field(default_factory=NormalizedFindings)
    routing: RoutingDecision = field(default_factory=RoutingDecision)
    handoff: HandoffSpec = field(default_factory=HandoffSpec)

    def to_dict(self) -> dict[str, Any]:
        return {
            "packet_id": self.packet_id,
            "stage": self.stage,
            "input_summary": self.input_summary.to_dict(),
            "truth_classification": self.truth_classification.to_dict(),
            "temporal_grounding": self.temporal_grounding.to_dict(),
            "ambiguity": self.ambiguity.to_dict(),
            "conflict": self.conflict.to_dict(),
            "uncertainty": self.uncertainty.to_dict(),
            "evidence_plan": self.evidence_plan.to_dict(),
            "entities": [e.to_dict() for e in self.entities],
            "target_claims": [c.to_dict() for c in self.target_claims],
            "evidence_items": [i.to_dict() for i in self.evidence_items],
            "normalized_findings": self.normalized_findings.to_dict(),
            "routing": self.routing.to_dict(),
            "handoff": self.handoff.to_dict(),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# KNOWLEDGE BASES — Classification Anchors
# ═══════════════════════════════════════════════════════════════════════════════

# Absolute invariants — no web search ever needed
_INVARIANT_TERMS: dict[str, list[str]] = {
    "physics": [
        "entropy",
        "thermodynamics",
        "conservation of energy",
        "speed of light",
        "gravity",
        "relativity",
        "quantum mechanics",
        "second law",
        "planck",
        "boltzmann",
        "maxwell",
        "newton",
        "faraday",
    ],
    "math": [
        "nash equilibrium",
        "pythagorean theorem",
        "turing completeness",
        "algorithm",
        "complexity",
        "proof",
        "axiom",
        "theorem",
        "lemma",
        "derivative",
        "integral",
        "eigenvalue",
        "fourier",
    ],
    "logic": [
        "syllogism",
        "deductive reasoning",
        "inductive reasoning",
        "occam's razor",
        "falsification",
        "null hypothesis",
        "modus ponens",
        "modus tollens",
        "contrapositive",
    ],
    "definitions": [
        "is defined as",
        "what is the meaning of",
        "definition of",
        "what does.*mean",
        r"\bmeaning\b",
    ],
}

# Time-sensitive triggers — live search required
_LIVE_TRIGGERS: list[str] = [
    "current",
    "now",
    "today",
    "latest",
    "recent",
    "right now",
    "at the moment",
    "this year",
    "2024",
    "2025",
    "2026",
    "price",
    "trading at",
    "rate of",
    "ceo",
    "cto",
    "president",
    "prime minister",
    "minister",
    "leader",
    "outbreak",
    "election",
    "war",
    "outage",
    "breach",
    "release",
    "launched",
    "weather",
    "temperature",
    "forecast",
]

# Contested / axiom-dependent markers
_CONTESTED_MARKERS: list[str] = [
    "best framework",
    "best language",
    "better than",
    "vs ",
    " versus ",
    "capitalism",
    "socialism",
    "religion",
    "god",
    "morality",
    "ethical",
    "should society",
    "is it wrong",
    "political",
    "ideology",
]

# Domain → staleness threshold (days)
_FRESHNESS_BY_DOMAIN: dict[str, int] = {
    "finance": 1,
    "weather": 0,  # same-day
    "security": 1,
    "news": 1,
    "software": 7,
    "law": 30,
    "medicine": 14,
    "sports": 1,
}

# Domain detection keywords
_DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "finance": ["price", "stock", "crypto", "market", "trading", "bitcoin", "investment", "fund"],
    "weather": ["weather", "temperature", "forecast", "rain", "humidity"],
    "security": ["cve", "vulnerability", "exploit", "breach", "malware", "ransomware"],
    "software": ["api", "library", "framework", "version", "github", "npm", "pypi", "sdk"],
    "law": ["law", "legal", "statute", "regulation", "gdpr", "jurisdiction", "court"],
    "medicine": ["drug", "treatment", "disease", "diagnosis", "clinical", "fda", "who"],
    "geopolitics": ["election", "war", "country", "government", "treaty", "sanctions"],
    "physics": ["entropy", "quantum", "energy", "force", "thermodynamics"],
    "math": ["equation", "theorem", "proof", "formula", "algorithm"],
}


# ═══════════════════════════════════════════════════════════════════════════════
# WEB SEARCH PROVIDER PROTOCOL
# ═══════════════════════════════════════════════════════════════════════════════


@runtime_checkable
class WebSearchProvider(Protocol):
    """
    Invariant search provider interface.

    The governed protocol stays constant; backends are swappable.
    Implement this to plug in Brave, DDGS, Perplexity, or any other engine.
    """

    async def search(
        self,
        query: str,
        top_k: int = 5,
        freshness_days: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Execute a web search.

        Returns a list of result dicts with keys:
            title, url, description, published_date (optional)
        """
        ...


class RealityHandlerSearchProvider:
    """
    Wraps the existing RealityHandler (Brave + DDGS fallback) as a
    WebSearchProvider.  Keeps the live-search path decoupled from the
    governing logic.
    """

    def __init__(self) -> None:
        self._handler: Any = None  # lazy init to avoid circular imports

    def _get_handler(self) -> Any:
        if self._handler is None:
            from arifosmcp.runtime.reality_handlers import handler as _h

            self._handler = _h
        return self._handler

    async def search(
        self,
        query: str,
        top_k: int = 5,
        freshness_days: int | None = None,  # noqa: ARG002 — future use
    ) -> list[dict[str, Any]]:
        if not query or not query.strip():
            logger.warning("RealityHandlerSearchProvider: empty query suppressed")
            return []
        try:
            result = await self._get_handler().search_brave(query, top_k=top_k)
            if result.results:
                return [
                    {
                        "title": r.get("title", ""),
                        "url": r.get("url", r.get("href", "")),
                        "description": r.get("description", r.get("body", "")),
                        "published_date": r.get("age", r.get("published_date")),
                    }
                    for r in result.results
                ]
        except Exception as exc:
            logger.warning("RealityHandlerSearchProvider.search failed: %s", exc)
        return []


class SubstrateFetchProvider:
    """
    Substrate-backed fetch provider.
    Prioritizes direct mcp-server-fetch for high-fidelity Markdown.
    """

    async def search(
        self,
        query: str,
        top_k: int = 5,
        freshness_days: int | None = None,
    ) -> list[dict[str, Any]]:
        # This provider is primarily for direct URL grounding or high-signal docs
        from arifosmcp.integrations.fetch_bridge import fetch_bridge
        
        # If the query is a URL, use fetch_guarded directly
        if query.startswith(("http://", "https://")):
            res = await fetch_bridge.fetch_guarded(query, reason="Governed Sense Grounding")
            if res.get("ok"):
                return [{
                    "title": f"Fetched Document: {query}",
                    "url": query,
                    "description": res.get("content", ""),
                    "source_type": "mcp-fetch",
                    "source_rank": res.get("source_rank", 4)
                }]
        
        # Otherwise, fallback to a search engine to find URLs, then fetch
        # (This is handled by the higher-level logic in governed_sense)
        return []


# Module-level default provider (lazy singleton)
_default_provider: WebSearchProvider | None = None


def _get_default_provider() -> WebSearchProvider:
    global _default_provider
    if _default_provider is None:
        _default_provider = RealityHandlerSearchProvider()
    return _default_provider


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 1: PARSE — Normalize raw string into SenseInput
# ═══════════════════════════════════════════════════════════════════════════════


def normalize_query(raw: str) -> SenseInput:
    """
    Stage 1: Convert a raw query string into a structured SenseInput.

    Extracts: domain, time_scope, entity targets, task_type.
    Backward-compatible: callers passing a plain string get the full structure.

    SECURITY: Enforces _MAX_QUERY_LENGTH to prevent resource exhaustion.
    """
    q = raw.strip()[:_MAX_QUERY_LENGTH]  # Hard limit on query length
    ql = q.lower()

    # Detect domain
    domain = "unknown"
    for d, kws in _DOMAIN_KEYWORDS.items():
        if any(kw in ql for kw in kws):
            domain = d
            break

    # Detect time scope
    if any(t in ql for t in _LIVE_TRIGGERS[:15]):  # current/now/today keywords
        time_scope = TimeScope.LIVE
    elif re.search(r"\b(yesterday|last week|ago|previous|historical|in \d{4})\b", ql):
        time_scope = TimeScope.HISTORICAL
    elif re.search(r"\b(this week|this month|recently)\b", ql):
        time_scope = TimeScope.DATED
    elif re.search(r"\b(will|predict|forecast|next year)\b", ql):
        time_scope = TimeScope.FORECAST
    else:
        time_scope = TimeScope.TIMELESS

    # Detect task type
    if re.search(r"\b(what is|define|meaning of|definition)\b", ql):
        task_type = TaskType.DEFINE
    elif re.search(r"\b(is it true|verify|confirm|check)\b", ql):
        task_type = TaskType.VERIFY
    elif re.search(r"\b(compare|vs|versus|better|worse|difference)\b", ql):
        task_type = TaskType.COMPARE
    elif re.search(r"\b(where|location|find|who is|current.*ceo|current.*president)\b", ql):
        task_type = TaskType.LOCATE
    elif re.search(r"\b(monitor|track|watch|alert)\b", ql):
        task_type = TaskType.MONITOR
    elif re.search(r"\b(why|explain|how does|reason)\b", ql):
        task_type = TaskType.EXPLAIN
    else:
        task_type = TaskType.UNKNOWN

    # Extract entity (simple heuristic: proper-ish nouns after "of/for/about/is")
    entity_targets: list[EntityRef] = []
    m = re.search(
        r"(?:of|for|about|is|who is|what is)\s+([A-Z][a-zA-Z\s\-]{2,40}?)(?:\?|$|\s+(?:today|now|currently|the))",
        q,
    )
    if m:
        entity_targets = [EntityRef(name=m.group(1).strip(), type=EntityType.UNKNOWN)]

    return SenseInput(
        input=InputSpec(type=InputType.QUERY, value=q, mode=SensingMode.GOVERNED),
        intent=IntentSpec(task_type=task_type, user_goal=q[:120]),
        query_frame=QueryFrame(
            domain=domain,
            time_scope=time_scope,
            entity_targets=entity_targets,
        ),
        policy=PolicySpec(),
        budget=BudgetSpec(),
        actor=ActorSpec(),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 2: CLASSIFY — Truth-Class Router (7 lanes)
# ═══════════════════════════════════════════════════════════════════════════════


def classify_truth_class(si: SenseInput) -> TruthClassification:
    """
    Stage 2: Route the query to one of 7 truth-class lanes.

    Lane A  absolute_invariant   → Offline only (math, physics, logic)
    Lane B  conditional_invariant → Frame-dependent (jurisdiction, version)
    Lane C  operational_principle → Strategy, governance, design
    Lane D  time_sensitive_fact  → Live search required
    Lane F  contested_framework  → Axiom-dependent, no universal answer
    Lane G  ambiguous_query      → Frame unresolved — HOLD
    Lane H  unknown              → Insufficient basis
    """
    ql = si.input.value.lower()
    time_scope = si.query_frame.time_scope

    # Lane A: Absolute invariant
    for _, terms in _INVARIANT_TERMS.items():
        for t in terms:
            if re.search(t, ql):
                if time_scope != TimeScope.LIVE:
                    return TruthClassification(
                        truth_class=TruthClass.ABSOLUTE_INVARIANT,
                        search_required=False,
                        search_reason="First-principles sufficient; no retrieval needed.",
                        classification_confidence=0.95,
                    )

    # Lane D: Time-sensitive (checked before B/C to catch "current X")
    if time_scope == TimeScope.LIVE or any(t in ql for t in _LIVE_TRIGGERS):
        return TruthClassification(
            truth_class=TruthClass.TIME_SENSITIVE_FACT,
            search_required=True,
            search_reason="Live/time-sensitive query; freshness required.",
            temporal_dependency=True,
            temporal_note="Result may be stale without live retrieval.",
            classification_confidence=0.90,
        )

    # Lane F: Contested framework
    if any(m in ql for m in _CONTESTED_MARKERS):
        return TruthClassification(
            truth_class=TruthClass.CONTESTED_FRAMEWORK,
            search_required=True,
            search_reason="Axiom-dependent topic; multiple valid frameworks exist.",
            framework_dependency=True,
            framework_note="No single authoritative answer; surface competing views.",
            classification_confidence=0.75,
        )

    # Lane B: Conditional invariant (frame-dependent)
    conditional_markers = [
        "in the us",
        "in malaysia",
        "in uk",
        "under gdpr",
        "according to",
        "in python",
        "in version",
        "based on",
        "depending on",
        "in context of",
        "under ",
        "per ",
        "jurisdiction",
    ]
    if any(m in ql for m in conditional_markers):
        return TruthClassification(
            truth_class=TruthClass.CONDITIONAL_INVARIANT,
            search_required=True,
            search_reason="Frame-dependent truth; context-specific retrieval needed.",
            classification_confidence=0.80,
        )

    # Lane C: Operational principle
    operational_markers = [
        "best practice",
        "should i",
        "recommend",
        "strategy",
        "tradeoff",
        "trade-off",
        "architecture",
        "design pattern",
        "how to",
        "guide",
        "tutorial",
        "steps to",
    ]
    if any(m in ql for m in operational_markers):
        return TruthClassification(
            truth_class=TruthClass.OPERATIONAL_PRINCIPLE,
            search_required=False,
            search_reason="Operational guidance; reasoning + curated evidence sufficient.",
            classification_confidence=0.70,
        )

    # Lane G: Ambiguous (unknown claim type + no entity + very short)
    if len(si.input.value.split()) < 3:
        return TruthClassification(
            truth_class=TruthClass.AMBIGUOUS_QUERY,
            search_required=False,
            search_reason="Query too short to classify reliably.",
            classification_confidence=0.30,
        )

    # Lane H: Unknown — not enough signal
    if si.intent.task_type == TaskType.UNKNOWN and not si.query_frame.entity_targets:
        return TruthClassification(
            truth_class=TruthClass.UNKNOWN,
            search_required=False,
            search_reason="Insufficient classification signal.",
            classification_confidence=0.20,
        )

    # Default: conditional invariant is the safest middle ground
    return TruthClassification(
        truth_class=TruthClass.CONDITIONAL_INVARIANT,
        search_required=True,
        search_reason="Defaulting to conditional lane; may need contextual evidence.",
        classification_confidence=0.55,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 3: TEMPORAL GROUNDING
# ═══════════════════════════════════════════════════════════════════════════════


def build_temporal_grounding(si: SenseInput, tc: TruthClassification) -> TemporalGrounding:
    """Stage 3: Determine temporal validity constraints."""
    time_scope = si.query_frame.time_scope
    domain = si.query_frame.domain
    now = datetime.now(timezone.utc).isoformat()

    freshness_required = tc.temporal_dependency or time_scope in (TimeScope.LIVE, TimeScope.DATED)
    freshness_days = _FRESHNESS_BY_DOMAIN.get(domain)

    staleness_risk = StalenessRisk.NONE
    notes: list[str] = []

    if time_scope == TimeScope.LIVE:
        staleness_risk = StalenessRisk.HIGH
        notes.append("Live query — evidence must be from within freshness window.")
    elif time_scope == TimeScope.DATED:
        staleness_risk = StalenessRisk.MODERATE
        notes.append("Recent query — prefer sources published in the last 7 days.")
    elif time_scope == TimeScope.HISTORICAL:
        notes.append("Historical query — exact date reference preferred.")

    # Detect explicit date mentions in query
    detected_dates = re.findall(
        r"\b(20\d{2}|january|february|march|april|may|june|july|"
        r"august|september|october|november|december)\b",
        si.input.value.lower(),
    )

    return TemporalGrounding(
        query_time_class=time_scope,
        detected_dates=detected_dates,
        effective_reference_time=now,
        freshness_required=freshness_required,
        staleness_risk=staleness_risk,
        temporal_notes=notes,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 4: PLAN — Evidence Hierarchy
# ═══════════════════════════════════════════════════════════════════════════════


def build_evidence_plan(si: SenseInput, tc: TruthClassification) -> EvidencePlan:
    """
    Stage 4: Build constrained evidence-gathering plan.

    Lane assignments:
        absolute_invariant / operational_principle → offline_reason (no web call)
        time_sensitive_fact → web_search (live, strict freshness)
        conditional_invariant → web_search (moderate freshness)
        contested_framework → web_search (multiple views required)
        ambiguous_query / unknown → hold
    """
    truth_class = tc.truth_class
    domain = si.query_frame.domain
    time_scope = si.query_frame.time_scope

    if truth_class in (TruthClass.ABSOLUTE_INVARIANT, TruthClass.OPERATIONAL_PRINCIPLE):
        return EvidencePlan(
            retrieval_lane="offline_reason",
            min_rank_required=EvidenceRank.TECHNICAL_DOCUMENTATION.value,
            corroboration=CorroborationSpec(min_distinct_sources=0),
        )

    if truth_class in (TruthClass.AMBIGUOUS_QUERY, TruthClass.UNKNOWN):
        return EvidencePlan(retrieval_lane="hold")

    # Web-search lanes
    freshness_days = _FRESHNESS_BY_DOMAIN.get(domain)
    if time_scope == TimeScope.LIVE:
        freshness_days = freshness_days or 1

    domain_sources: dict[str, list[str]] = {
        "software": ["official documentation", "github releases", "pypi", "npm"],
        "finance": ["stock exchange", "official filings", "bloomberg", "reuters"],
        "law": ["government gazette", "official court records", "legal databases"],
        "security": ["cve database", "security advisories", "vendor notices"],
        "medicine": ["pubmed", "who", "fda", "cdc", "lancet", "nejm"],
        "geopolitics": ["reuters", "ap news", "bbc", "official government sites"],
    }

    min_rank = (
        EvidenceRank.OFFICIAL_ISSUER.value
        if truth_class == TruthClass.TIME_SENSITIVE_FACT
        else EvidenceRank.REPUTABLE_SECONDARY.value
    )

    return EvidencePlan(
        retrieval_lane="web_search",
        preferred_sources=domain_sources.get(domain, ["authoritative sources"]),
        min_rank_required=min_rank,
        freshness_requirement=FreshnessRequirement(
            required=freshness_days is not None,
            max_age_days=freshness_days,
            reference_time=datetime.now(timezone.utc).isoformat(),
        ),
        corroboration=CorroborationSpec(
            min_distinct_sources=2,
            require_primary_if_available=True,
        ),
        conflict_policy=ConflictPolicy(
            mode="prefer_higher_rank"
            if truth_class == TruthClass.TIME_SENSITIVE_FACT
            else "summarize_disagreement"
        ),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 6: NORMALIZE — Raw results → EvidenceItem list
# ═══════════════════════════════════════════════════════════════════════════════


def _infer_source_rank(url: str, title: str) -> int:
    """Heuristic source-rank inference from URL/title signals."""
    u = (url or "").lower()
    t = (title or "").lower()
    # Rank 1: primary measurement — not inferrable from URL alone
    # Rank 2: primary source (original doc, raw data)
    if any(x in u for x in [".gov", ".gov.", "official", "parliament", "congress"]):
        return EvidenceRank.OFFICIAL_ISSUER.value
    # Rank 3: official issuer
    if any(x in u for x in ["github.com", "docs.", "pypi.org", "npmjs.com", "developer."]):
        return EvidenceRank.TECHNICAL_DOCUMENTATION.value
    # Rank 4: technical documentation
    if any(
        x in u
        for x in [
            "reuters.com",
            "ap.org",
            "bbc.com",
            "bloomberg.com",
            "ft.com",
            "wsj.com",
            "economist.com",
            "nature.com",
            "pubmed",
            "ncbi.nlm",
        ]
    ):
        return EvidenceRank.REPUTABLE_SECONDARY.value
    # Rank 5: reputable secondary
    if any(x in u for x in ["wikipedia.org", "britannica.com", "investopedia.com"]):
        return EvidenceRank.AGGREGATOR_OR_INDEX.value
    # Rank 7: social/unverified default
    return EvidenceRank.SOCIAL_OR_UNVERIFIED.value


def normalize_results_to_items(raw_results: list[dict[str, Any]]) -> list[EvidenceItem]:
    """Stage 6: Convert raw search results to structured EvidenceItem list."""
    items: list[EvidenceItem] = []
    for r in raw_results:
        url = r.get("url", r.get("href", ""))
        title = r.get("title", "")
        description = r.get("description", r.get("body", r.get("snippet", "")))
        pub_date = r.get("published_date", r.get("age", r.get("date")))
        source_rank = _infer_source_rank(url, title)

        quality_flags: list[QualityFlag] = []
        if source_rank >= EvidenceRank.SOCIAL_OR_UNVERIFIED.value:
            quality_flags.append(QualityFlag.INCOMPLETE)
        if pub_date and isinstance(pub_date, str) and "ago" in pub_date.lower():
            quality_flags.append(QualityFlag.STALE)

        # Build provenance hash
        prov_src = f"{url}|{title}|{description[:80]}"
        provenance_hash = hashlib.sha256(prov_src.encode()).hexdigest()[:16]

        # Extract a simple claim from description
        extracted: list[ExtractedClaim] = []
        if description:
            extracted.append(
                ExtractedClaim(
                    claim_text=description[:200],
                    claim_type=ClaimType.STATUS,
                    confidence=0.6,
                )
            )

        items.append(
            EvidenceItem(
                source_name=url.split("/")[2] if url.startswith("http") else url,
                source_type="web",
                source_rank=source_rank,
                url=url if url else None,
                title=title if title else None,
                published_at=str(pub_date) if pub_date else None,
                observed_at=datetime.now(timezone.utc).isoformat(),
                extracted_claims=extracted,
                snippets=[description[:300]] if description else [],
                provenance_hash=provenance_hash,
                quality_flags=quality_flags,
            )
        )
    return items


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 7: GATE — Ambiguity, Conflict, Uncertainty
# ═══════════════════════════════════════════════════════════════════════════════


def detect_ambiguity(si: SenseInput, tc: TruthClassification) -> AmbiguityModel:
    """Detect ambiguity in the query."""
    detected_types: list[AmbiguityType] = []
    candidates: list[str] = []

    ql = si.input.value.lower()
    word_count = len(si.input.value.split())

    # Never flag ambiguity for invariant lanes — they are definitionally unambiguous
    if tc.truth_class == TruthClass.ABSOLUTE_INVARIANT:
        return AmbiguityModel(detected=False)

    if word_count < 3:
        detected_types.append(AmbiguityType.INTENT)
        candidates = [
            "Asking for a definition",
            "Asking for current status",
            "Asking for a comparison",
        ]
    if tc.truth_class == TruthClass.AMBIGUOUS_QUERY:
        detected_types.append(AmbiguityType.DEFINITION)

    # Temporal ambiguity: only for status/locate queries that lack time context
    # (e.g. "who is the president" — which year?)
    if (
        re.search(r"\b(who is|current)\b", ql)
        and si.query_frame.time_scope == TimeScope.TIMELESS
        and si.intent.task_type in (TaskType.LOCATE, TaskType.UNKNOWN)
    ):
        detected_types.append(AmbiguityType.TIMEFRAME)
        candidates.append("Query may refer to current or historical status")

    detected = bool(detected_types)
    return AmbiguityModel(
        detected=detected,
        ambiguity_type=detected_types,
        candidate_interpretations=candidates,
        chosen_interpretation=None,
        assumption_disclosed=False,
        needs_human_narrowing=word_count < 2,
    )


def detect_conflicts_from_items(items: list[EvidenceItem]) -> ConflictModel:
    """Detect source conflicts in evidence items."""
    if len(items) < 2:
        return ConflictModel(detected=False, resolution_status=ResolutionStatus.RESOLVED)

    # Simple conflict detection: negation terms or rank mismatch
    conflict_types: list[ConflictType] = []
    conflict_notes: list[str] = []

    # Check for negations in claims
    all_claims = [claim.claim_text for item in items for claim in item.extracted_claims]
    has_negation = any(
        re.search(r"\b(not|no longer|false|incorrect|denied|wrong|misleading)\b", c.lower())
        for c in all_claims
    )
    if has_negation:
        conflict_types.append(ConflictType.SOURCE_DISAGREEMENT)
        conflict_notes.append("Negation terms detected across sources")

    # Check for temporal mismatch (different dates)
    pub_dates = [i.published_at for i in items if i.published_at]
    if len(set(pub_dates)) > 2:
        conflict_types.append(ConflictType.TEMPORAL_MISMATCH)
        conflict_notes.append(f"Sources span multiple publication dates: {set(pub_dates)}")

    detected = bool(conflict_types)
    return ConflictModel(
        detected=detected,
        conflict_type=conflict_types,
        conflict_summary="; ".join(conflict_notes) if conflict_notes else None,
        resolution_status=ResolutionStatus.UNRESOLVED if detected else ResolutionStatus.RESOLVED,
        resolution_method="prefer_higher_rank" if detected else None,
    )


def detect_glocks(
    si: SenseInput,
    tc: TruthClassification,
    ub: UncertaintyBand,
    conflict: ConflictModel,
    ambiguity: AmbiguityModel,
) -> list[str]:
    """Detect active Gödel/Void locks based on structural signals."""
    locks = []

    # G1: Incompleteness (grounding gap)
    if ub.basis.evidence_quality < 0.4 or tc.truth_class == TruthClass.UNKNOWN:
        locks.append("G1")

    # G2: Contradiction
    if conflict.detected:
        locks.append("G2")

    # G3: Self-Reference (heuristic)
    self_ref_patterns = ["system", "myself", "constitution", "certified by arifos"]
    if (
        any(p in si.input.value.lower() for p in self_ref_patterns)
        and tc.truth_class == TruthClass.OPERATIONAL_PRINCIPLE
    ):
        locks.append("G3")

    # G4: Undecidability
    if ub.sigma > 0.6 and not (conflict.detected or ambiguity.detected):
        locks.append("G4")

    # G5: Meaning Drift
    if ambiguity.detected:
        locks.append("G5")

    # G6: Regress / Infinity (heuristic)
    if ub.sigma > 0.4 and "..." in si.input.value:
        locks.append("G6")

    # G7: Moral Remainder (heuristic: keyword-based or high risk)
    moral_patterns = ["tradeoff", "sacrifice", "lesser evil", "choice"]
    if any(p in si.input.value.lower() for p in moral_patterns):
        locks.append("G7")

    return sorted(list(set(locks))) or ["G0"]


def compute_uncertainty_band(
    items: list[EvidenceItem],
    conflict: ConflictModel,
    ambiguity: AmbiguityModel,
    temporal: TemporalGrounding,
    plan: EvidencePlan,
) -> UncertaintyBand:
    """Compute the epistemic uncertainty band from all signals."""
    # Evidence quality score
    if not items:
        eq = 0.0
    else:
        rank_scores = [1.0 - (i.source_rank - 1) / 6.0 for i in items]
        eq = sum(rank_scores) / len(rank_scores)

    # Source agreement
    sa = 0.0 if conflict.detected else 1.0
    if conflict.resolution_status == ResolutionStatus.PARTIALLY_RESOLVED:
        sa = 0.5

    # Temporal alignment
    ta = 1.0
    if temporal.staleness_risk == StalenessRisk.HIGH:
        ta = 0.2
    elif temporal.staleness_risk == StalenessRisk.MODERATE:
        ta = 0.6
    elif temporal.staleness_risk == StalenessRisk.LOW:
        ta = 0.8

    # Frame clarity
    fc = 0.3 if ambiguity.detected else 0.9

    # Model fit
    min_sources = plan.corroboration.min_distinct_sources if plan else 2
    mf = min(1.0, len(items) / max(min_sources, 1))

    # Weighted sigma
    sigma = 1.0 - (0.30 * eq + 0.25 * sa + 0.20 * ta + 0.15 * fc + 0.10 * mf)
    sigma = round(max(0.0, min(1.0, sigma)), 4)

    if sigma < 0.25:
        level = UncertaintyLevel.LOW
    elif sigma < 0.5:
        level = UncertaintyLevel.MODERATE
    elif sigma < 0.75:
        level = UncertaintyLevel.HIGH
    else:
        level = UncertaintyLevel.EXTREME

    # Omega_0 cap: never report confidence above this
    omega0_cap = 0.9 - sigma * 0.4

    return UncertaintyBand(
        level=level,
        sigma=sigma,
        omega0_cap=round(omega0_cap, 4),
        basis=UncertaintyBasis(
            evidence_quality=round(eq, 4),
            source_agreement=round(sa, 4),
            temporal_alignment=round(ta, 4),
            frame_clarity=round(fc, 4),
            model_fit=round(mf, 4),
        ),
        narrative_note=(
            f"σ={sigma:.2f} — "
            + ("conflict detected; " if conflict.detected else "")
            + (
                f"staleness risk={temporal.staleness_risk.value}; "
                if temporal.staleness_risk != StalenessRisk.NONE
                else ""
            )
            + f"{len(items)} evidence item(s)"
        ),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# INTELLIGENCE STATE — Compute from packet
# ═══════════════════════════════════════════════════════════════════════════════


def compute_intelligence_state(
    si: SenseInput,
    packet: SensePacket,
    tc: TruthClassification,
    ub: UncertaintyBand,
    session_id: str | None = None,
) -> tuple[IntelligenceState, dict[str, Any]]:
    """Derive IntelligenceState and PhilosophyState from the packet."""
    # 1. Detect locks and compute philosophy
    locks = detect_glocks(si, tc, ub, packet.conflict, packet.ambiguity)
    p_state = select_philosophy_state(
        confidence=1.0 - ub.sigma,
        dS=1.0 - ub.basis.temporal_alignment,
        intervention=0.5,  # Default intervention
        session_id=session_id or "global",
        locks=locks,
    )

    # 2. Derive metrics
    confidence = 1.0 - ub.sigma
    # Apply philosophy cap
    confidence = min(confidence, p_state["confidence_cap"])

    # Exploration posture
    if len(packet.evidence_items) >= 3:
        exploration = ExplorationState.BROAD
    elif len(packet.evidence_items) >= 1:
        exploration = ExplorationState.FOCUSED
    else:
        exploration = ExplorationState.NARROW

    # Entropy
    if ub.level in (UncertaintyLevel.HIGH, UncertaintyLevel.EXTREME):
        entropy = EntropyState.HIGH
    elif ub.level == UncertaintyLevel.MODERATE:
        entropy = EntropyState.MANAGEABLE
    else:
        entropy = EntropyState.LOW

    # Eureka
    if confidence > 0.80 and not packet.conflict.detected and not packet.ambiguity.detected:
        eureka = EurekaState.STRONG
    elif confidence > 0.60:
        eureka = EurekaState.EMERGING
    else:
        eureka = EurekaState.NONE

    stable_facts = packet.normalized_findings.grounded_facts[:5]
    unstable = packet.normalized_findings.assumptions_made[:3]
    unknowns = packet.normalized_findings.unresolved_questions[:3]
    conflicts_list = (
        [packet.conflict.conflict_summary]
        if (packet.conflict.detected and packet.conflict.conflict_summary)
        else []
    )

    decision_required: list[str] = []
    if packet.ambiguity.needs_human_narrowing:
        decision_required.append("Query requires human clarification before proceeding.")
    if packet.conflict.resolution_status == ResolutionStatus.UNRESOLVED:
        decision_required.append("Unresolved source conflict requires human judgment.")

    # Truth vector
    tv = TruthVector(
        grounding_g=ub.basis.evidence_quality,
        truth_tau=ub.basis.source_agreement,
        uncertainty_sigma=ub.sigma,
        coherence_c=ub.basis.frame_clarity,
        entropy_delta_s=round(1.0 - ub.basis.temporal_alignment, 4),
        humility_omega0=p_state["confidence_cap"],  # Using Hyperlattice cap
    )

    intel = IntelligenceState(
        exploration=exploration,
        entropy=entropy,
        eureka=eureka,
        confidence=round(confidence, 4),
        uncertainty_score=ub.sigma,
        stable_facts=stable_facts,
        unstable_assumptions=unstable,
        unknowns=unknowns,
        conflicts=conflicts_list,
        decision_required=decision_required,
        truth_vector=tv,
    )

    return intel, p_state


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 8: ROUTING — Deterministic next-stage selection
# ═══════════════════════════════════════════════════════════════════════════════


def compute_routing(
    tc: TruthClassification,
    ub: UncertaintyBand,
    ambiguity: AmbiguityModel,
    conflict: ConflictModel,
    has_evidence: bool,
) -> RoutingDecision:
    """
    Deterministic routing: sense → mind / heart / hold.

    Rules (evaluated in order):
    1. needs_human_narrowing → HOLD
    2. absolute_invariant → MIND (before ambiguity check — invariants are self-grounded)
    3. ambiguous + no evidence → HOLD
    4. conflict unresolved → HEART (ethical critique before reasoning)
    5. has_evidence + uncertainty LOW/MODERATE → MIND
    6. contested_framework → HEART (value/frame critique needed)
    7. default → HOLD
    """
    if ambiguity.needs_human_narrowing:
        return RoutingDecision(
            next_stage=RoutingTarget.HOLD,
            route_reason="Query requires human clarification before search can proceed.",
            requires_human_decision=True,
        )

    # Invariant claims are self-grounded — route directly to MIND
    if tc.truth_class == TruthClass.ABSOLUTE_INVARIANT:
        return RoutingDecision(
            next_stage=RoutingTarget.MIND,
            route_reason="Invariant claim — first-principles reasoning is sufficient.",
        )

    if ambiguity.detected and not has_evidence:
        return RoutingDecision(
            next_stage=RoutingTarget.HOLD,
            route_reason="Ambiguous query with no evidence — narrow scope first.",
            requires_human_decision=False,
        )

    if conflict.detected and conflict.resolution_status == ResolutionStatus.UNRESOLVED:
        return RoutingDecision(
            next_stage=RoutingTarget.HEART,
            route_reason="Unresolved source conflict — ethical/critical review required before synthesis.",
            requires_human_decision=True,
        )

    if has_evidence and ub.level in (UncertaintyLevel.LOW, UncertaintyLevel.MODERATE):
        return RoutingDecision(
            next_stage=RoutingTarget.MIND,
            route_reason="Grounded evidence ready — synthesize and reason.",
            requires_live_verification=tc.temporal_dependency,
        )

    # NEW: has_evidence + uncertainty HIGH/EXTREME → MIND (with caution)
    # This prevents trigger-happy HOLD when we actually have data to work with.
    if has_evidence:
        return RoutingDecision(
            next_stage=RoutingTarget.MIND,
            route_reason="Evidence gathered but uncertainty remains high — proceed with epistemic caution.",
            requires_live_verification=True,
        )

    if tc.truth_class == TruthClass.CONTESTED_FRAMEWORK:
        return RoutingDecision(
            next_stage=RoutingTarget.HEART,
            route_reason="Contested topic — value/frame critique required before making claims.",
        )

    if ub.level == UncertaintyLevel.HIGH:
        return RoutingDecision(
            next_stage=RoutingTarget.HOLD,
            route_reason=f"High uncertainty (σ={ub.sigma:.2f}) — insufficient evidence to route forward.",
        )

    return RoutingDecision(
        next_stage=RoutingTarget.HOLD,
        route_reason="Insufficient signal for deterministic routing.",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# VERDICT GATE — SEAL only when conditions are met
# ═══════════════════════════════════════════════════════════════════════════════


def compute_verdict(
    tc: TruthClassification,
    ub: UncertaintyBand,
    ambiguity: AmbiguityModel,
    routing: RoutingDecision,
    items: list[EvidenceItem],
) -> str:
    """
    Determine packet verdict.

    SEAL  → adequately classified, grounded, bounded, handoff-safe
    SABAR → partial — proceed with caveats
    HOLD  → ambiguous or uncertain — human narrowing needed
    """
    if routing.next_stage == RoutingTarget.HOLD:
        return "HOLD"
    if ambiguity.needs_human_narrowing:
        return "HOLD"
    if ub.level == UncertaintyLevel.EXTREME:
        return "SABAR"

    # SEAL conditions
    classified = tc.classification_confidence >= 0.70
    grounded = tc.truth_class == TruthClass.ABSOLUTE_INVARIANT or len(items) >= 1
    bounded = ub.level in (UncertaintyLevel.LOW, UncertaintyLevel.MODERATE)
    handoff_safe = routing.next_stage in (RoutingTarget.MIND, RoutingTarget.HEART)

    if classified and grounded and bounded and handoff_safe:
        return "SEAL"
    if grounded:
        return "SABAR"
    return "HOLD"


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN — governed_sense()
# ═══════════════════════════════════════════════════════════════════════════════


async def governed_sense(
    query: str | SenseInput,
    session_id: str | None = None,
    session_context: dict[str, Any] | None = None,
    provider: WebSearchProvider | None = None,
    execute_search: bool = True,
) -> tuple[SensePacket, IntelligenceState]:
    """
    Execute the full 8-stage constitutional sensing protocol.

    Web search is gated by truth classification:
        invariant / operational  → no search
        time_sensitive / conditional → live search
        ambiguous / unknown      → HOLD (no search)

    Args:
        query:          Raw query string or pre-built SenseInput.
        session_id:     Session identifier for audit trail.
        session_context: Prior context dict (not yet fully consumed; future use).
        provider:       WebSearchProvider to use. Defaults to RealityHandlerSearchProvider.
        execute_search: False = dry-run (plan only, no actual retrieval).

    Returns:
        (SensePacket, IntelligenceState)
    """
    # ── STAGE 1: PARSE ────────────────────────────────────────────────────────
    si: SenseInput = query if isinstance(query, SenseInput) else normalize_query(query)

    # ── STAGE 2: CLASSIFY ─────────────────────────────────────────────────────
    tc = classify_truth_class(si)

    # ── STAGE 3: TEMPORAL GROUNDING ───────────────────────────────────────────
    temporal = build_temporal_grounding(si, tc)

    # ── STAGE 4: PLAN ─────────────────────────────────────────────────────────
    plan = build_evidence_plan(si, tc)

    # ── STAGE 3b: AMBIGUITY (after plan so we have full picture) ─────────────
    ambiguity = detect_ambiguity(si, tc)

    # ── STAGE 5: RETRIEVE (web search — gated) ────────────────────────────────
    raw_results: list[dict[str, Any]] = []
    if (
        tc.search_required
        and plan.retrieval_lane == "web_search"
        and execute_search
        and not ambiguity.needs_human_narrowing
    ):
        _provider = provider or _get_default_provider()
        raw_query = si.input.value
        top_k = si.budget.top_k
        freshness_days = plan.freshness_requirement.max_age_days

        try:
            raw_results = await _provider.search(
                query=raw_query,
                top_k=top_k,
                freshness_days=freshness_days,
            )
        except Exception as exc:
            logger.warning("governed_sense: search failed: %s", exc)

    # ── STAGE 6: NORMALIZE ────────────────────────────────────────────────────
    # SECURITY: Apply parsing limits to prevent resource exhaustion
    raw_results = raw_results[:_MAX_EVIDENCE]  # Hard cap on evidence items
    evidence_items = normalize_results_to_items(raw_results)

    # Offline: for invariants, derive facts from the query itself
    grounded_facts: list[str] = []
    unresolved: list[str] = []
    if tc.truth_class == TruthClass.ABSOLUTE_INVARIANT:
        grounded_facts = [f"This is an invariant claim: {si.input.value[:120]}"]
    elif evidence_items:
        grounded_facts = [item.snippets[0][:150] for item in evidence_items if item.snippets]
    else:
        unresolved = ["No evidence retrieved — cannot verify claim at this time."]

    findings = NormalizedFindings(
        grounded_facts=grounded_facts,
        unresolved_questions=unresolved,
        assumptions_made=(
            [
                f"Assumed {tc.truth_class.value} classification (confidence={tc.classification_confidence:.0%})."
            ]
        ),
        contested_points=(
            [
                packet_f
                for item in evidence_items
                for claim in item.extracted_claims
                if claim.supports_target is False
                for packet_f in [claim.claim_text[:100]]
            ]
        ),
    )

    # ── STAGE 7: GATE ─────────────────────────────────────────────────────────
    conflict = detect_conflicts_from_items(evidence_items)
    ub = compute_uncertainty_band(evidence_items, conflict, ambiguity, temporal, plan)

    # ── STAGE 8: ROUTING + HANDOFF ────────────────────────────────────────────
    routing = compute_routing(tc, ub, ambiguity, conflict, bool(evidence_items))
    verdict_str = compute_verdict(tc, ub, ambiguity, routing, evidence_items)

    state_update = StateUpdate(
        stable_facts_delta=grounded_facts[:3],
        unknowns_delta=unresolved,
        conflicts_delta=[conflict.conflict_summary]
        if conflict.detected and conflict.conflict_summary
        else [],
        confidence_delta=round(1.0 - ub.sigma, 4),
        uncertainty_delta=round(ub.sigma, 4),
    )
    handoff = HandoffSpec(
        packet_type="sense_packet@v2",
        consumable_by=["arifos.mind", "arifos.heart", "arifos.judge"],
        state_update=state_update,
    )

    # Assemble canonical SensePacket
    packet = SensePacket(
        input_summary=InputSummary(
            raw_query=si.input.value,
            normalized_query=si.input.value.strip(),
            mode_used=si.input.mode.value,
            domain=si.query_frame.domain,
        ),
        truth_classification=tc,
        temporal_grounding=temporal,
        ambiguity=ambiguity,
        conflict=conflict,
        uncertainty=ub,
        evidence_plan=plan,
        entities=si.query_frame.entity_targets,
        target_claims=si.query_frame.claim_targets,
        evidence_items=evidence_items,
        normalized_findings=findings,
        routing=routing,
        handoff=handoff,
    )

    # Compute IntelligenceState + Philosophy
    intel, p_state = compute_intelligence_state(si, packet, tc, ub, session_id=session_id)

    # Inject philosophy into handoff and routing
    state_update = StateUpdate(
        stable_facts_delta=grounded_facts[:3],
        unknowns_delta=unresolved,
        conflicts_delta=[conflict.conflict_summary]
        if conflict.detected and conflict.conflict_summary
        else [],
        confidence_delta=round(intel.confidence, 4),
        uncertainty_delta=round(ub.sigma, 4),
    )

    packet.routing.extra = {"philosophy": p_state}

    # Inject verdict into packet metadata (routing carries the canonical verdict)
    packet.routing.route_reason = f"[{verdict_str}] {packet.routing.route_reason}"

    return packet, intel


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Enums
    "ExplorationState",
    "EntropyState",
    "EurekaState",
    "TruthClass",
    "TaskType",
    "DecisionProximity",
    "TimeScope",
    "InputType",
    "SensingMode",
    "EvidenceRank",
    "AmbiguityType",
    "ConflictType",
    "UncertaintyLevel",
    "StalenessRisk",
    "ClaimType",
    "Polarity",
    "EntityType",
    "ResolutionStatus",
    "QualityFlag",
    "RoutingTarget",
    # Classes
    "TruthVector",
    "IntelligenceState",
    "SenseInput",
    "InputSpec",
    "IntentSpec",
    "EntityRef",
    "ClaimTarget",
    "QueryFrame",
    "PolicySpec",
    "BudgetSpec",
    "ActorSpec",
    "TruthClassification",
    "EvidencePlan",
    "FreshnessRequirement",
    "CorroborationSpec",
    "ConflictPolicy",
    "TemporalGrounding",
    "AmbiguityModel",
    "ConflictModel",
    "UncertaintyBasis",
    "UncertaintyBand",
    "ExtractedClaim",
    "EvidenceItem",
    "NormalizedFindings",
    "RoutingDecision",
    "StateUpdate",
    "HandoffSpec",
    "InputSummary",
    "SensePacket",
    # Provider protocol
    "WebSearchProvider",
    "RealityHandlerSearchProvider",
    # Stage functions
    "normalize_query",
    "classify_truth_class",
    "build_temporal_grounding",
    "build_evidence_plan",
    "normalize_results_to_items",
    "detect_ambiguity",
    "detect_conflicts_from_items",
    "compute_uncertainty_band",
    "compute_intelligence_state",
    "compute_routing",
    "compute_verdict",
    # Main entry point
    "governed_sense",
]
