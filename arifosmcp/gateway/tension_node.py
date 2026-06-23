"""
Paradox Tension Node — arifOS Belief Graph Schema
══════════════════════════════════════════════════

First-class epistemic object for institutional paradox detection.
Companion schemas: ClaimNode, EvidenceNode, ActorNode, ReceiptNode.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════


class TensionClass(StrEnum):
    HARD_CONTRADICTION = "hard_contradiction"
    INSTITUTIONAL_PARADOX = "institutional_paradox"
    TIMELINE_INCOHERENCE = "timeline_incoherence"
    ROLE_RESPONSIBILITY_GAP = "role_responsibility_gap"
    MEANING_LEAK = "meaning_leak"
    SHADOW_DRIFT = "shadow_drift"
    PUBLIC_PRIVATE_DIVERGENCE = "public_private_divergence"


class TensionStatus(StrEnum):
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    ESCALATED = "escalated"
    PARTIALLY_RESOLVED = "partially_resolved"
    RESOLVED = "resolved"
    ARCHIVED = "archived"


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResolutionType(StrEnum):
    CLARIFIED_BY_EVIDENCE = "clarified_by_evidence"
    SUPERSEDED_BY_NEW_VERSION = "superseded_by_new_version"
    ADMITTED_BY_ACTOR = "admitted_by_actor"
    TIMED_OUT_AND_ESCALATED = "timed_out_and_escalated"
    REMAINS_CONTESTED = "remains_contested"


class EdgeType(StrEnum):
    SUPPORTS = "supports"
    ATTACKS = "attacks"
    REFINES = "refines"
    UNDERCUTS = "undercuts"
    DEPENDS_ON = "depends_on"
    TRIGGERED_BY = "triggered_by"
    RESOLVED_BY = "resolved_by"
    MASKED_BY = "masked_by"
    WITNESSED_BY = "witnessed_by"


class ActorRole(StrEnum):
    SOVEREIGN = "sovereign"
    INSTITUTION = "institution"
    GATEKEEPER = "gatekeeper"
    OPERATOR = "operator"
    VICTIM = "victim"
    WITNESS = "witness"
    MEDIA = "media"
    REGULATOR = "regulator"
    LEGAL = "legal"


class ClaimType(StrEnum):
    PROMISE = "promise"
    DENIAL = "denial"
    EXPLANATION = "explanation"
    ACCUSATION = "accusation"
    FINDING = "finding"
    MITIGATION = "mitigation"
    DEFLECTION = "deflection"


class EpistemicTag(StrEnum):
    FACT = "FACT"
    CLAIM = "CLAIM"
    PLAUSIBLE = "PLAUSIBLE"
    HYPOTHESIS = "HYPOTHESIS"
    ESTIMATE = "ESTIMATE"
    SPECULATION = "SPECULATION"


# ═══════════════════════════════════════════════════════════════════════════
# COMPANION NODES
# ═══════════════════════════════════════════════════════════════════════════


class ClaimNode(BaseModel):
    """A single claim extracted from text — the atomic unit of tension analysis."""

    claim_id: str
    text: str
    claim_type: ClaimType
    speaker: str  # actor_ref
    epistemic_tag: EpistemicTag = EpistemicTag.CLAIM
    source_uri: str = ""
    extracted_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    evidence_refs: list[str] = Field(default_factory=list)
    contradicts: list[str] = Field(default_factory=list)  # claim_ids
    supports: list[str] = Field(default_factory=list)  # claim_ids
    hedging_score: float = Field(default=0.0, ge=0.0, le=1.0)
    verifiable: bool = False

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "claim_id": "claim_release_soon",
                    "text": "Kerajaan negeri bersedia mendedahkan laporan penuh insiden itu",
                    "claim_type": "promise",
                    "speaker": "actor_mb_selangor",
                    "epistemic_tag": "CLAIM",
                    "contradicts": ["claim_legal_constraints"],
                    "hedging_score": 0.15,
                }
            ]
        }
    }


class EvidenceNode(BaseModel):
    """Observable fact, document, or record that grounds a claim."""

    evidence_id: str
    evidence_type: str  # document, testimony, timeline, data_point, news_article, court_record
    description: str
    source_uri: str = ""
    captured_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    hash: str = ""  # sha256 of content
    classification: str = "PUBLIC"  # PUBLIC, CONFIDENTIAL, RESTRICTED
    reliability: float = Field(default=1.0, ge=0.0, le=1.0)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "evidence_id": "ev_kosmo_2026_06_12",
                    "evidence_type": "news_article",
                    "description": "Kosmo! report on MB Selangor statement regarding Putra Heights report disclosure",
                    "source_uri": "https://www.kosmo.com.my/2026/06/12/pendedahan-laporan-putra-heights-berdepan-kekangan-undang-undang/",
                    "reliability": 0.85,
                }
            ]
        }
    }


class ActorNode(BaseModel):
    """Institutional or individual actor in the governance graph."""

    actor_id: str
    name: str
    role: ActorRole
    entity_type: str = ""  # government, glc, private, court, ngo, community
    jurisdiction: str = ""  # negeri, persekutuan, both
    speaks_through: list[str] = Field(default_factory=list)  # claim_ids
    acts_through: list[str] = Field(default_factory=list)  # activity_ids
    power_score: float = Field(default=0.5, ge=0.0, le=1.0)
    visibility_score: float = Field(default=0.5, ge=0.0, le=1.0)
    accountability_score: float = Field(default=0.5, ge=0.0, le=1.0)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "actor_id": "actor_petronas",
                    "name": "Petronas / Petronas Gas Berhad",
                    "role": "operator",
                    "entity_type": "glc",
                    "jurisdiction": "persekutuan",
                    "power_score": 0.92,
                    "visibility_score": 0.35,
                    "accountability_score": 0.28,
                }
            ]
        }
    }


class ReceiptNode(BaseModel):
    """Governance action receipt — proof that an action happened."""

    receipt_id: str
    action_type: str  # report_submitted, review_started, disclosure_published, override_signed
    object_ref: str  # what was acted on (report_id, claim_id, incident_id)
    actor_ref: str
    timestamp: str
    reason_code: str = ""
    previous_receipt_hash: str = ""
    hash: str = ""  # sha256 of this receipt
    signature: str = ""

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "receipt_id": "rcpt_report_submitted_2026_04",
                    "action_type": "report_submitted",
                    "object_ref": "RPT-INC-20250401-PHGS01",
                    "actor_ref": "actor_independent_committee",
                    "timestamp": "2026-04-01T00:00:00+08:00",
                    "reason_code": "INVESTIGATION_COMPLETE",
                }
            ]
        }
    }


class ActivityNode(BaseModel):
    """A governed action or process in the timeline."""

    activity_id: str
    activity_type: str
    description: str
    started_at: str = ""
    completed_at: str | None = None
    actors_involved: list[str] = Field(default_factory=list)
    produced_refs: list[str] = Field(default_factory=list)
    used_refs: list[str] = Field(default_factory=list)
    status: str = "pending"


# ═══════════════════════════════════════════════════════════════════════════
# PROVENANCE (W3C PROV-aligned)
# ═══════════════════════════════════════════════════════════════════════════


class Provenance(BaseModel):
    generated_by_activity: str
    generated_by_agent: str
    reviewed_by: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    derived_from: list[str] = Field(default_factory=list)
    qualified_association: list[dict[str, str]] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════
# SCORES
# ═══════════════════════════════════════════════════════════════════════════


class TensionScores(BaseModel):
    confidence: float = Field(ge=0.0, le=1.0)
    credibility: float = Field(ge=0.0, le=1.0)
    coherence_strain: float = Field(ge=0.0, le=1.0)
    public_interest: float = Field(default=0.5, ge=0.0, le=1.0)
    harm_potential: float = Field(default=0.0, ge=0.0, le=1.0)
    shadow_score: float = Field(default=0.0, ge=0.0, le=1.0)
    meaning_leak_intensity: float = Field(default=0.0, ge=0.0, le=1.0)
    maruah_impact: float = Field(default=0.0, ge=-1.0, le=1.0)


# ═══════════════════════════════════════════════════════════════════════════
# GOVERNANCE BINDING
# ═══════════════════════════════════════════════════════════════════════════


class GovernanceBinding(BaseModel):
    floor_bindings: list[str] = Field(default_factory=list)
    required_action: str = ""
    hold_code: str | None = None
    escalate_after_s: int = 0
    epistemic_tag: EpistemicTag = EpistemicTag.CLAIM
    requires_888_hold: bool = False


# ═══════════════════════════════════════════════════════════════════════════
# TELEMETRY
# ═══════════════════════════════════════════════════════════════════════════


class TensionTelemetry(BaseModel):
    epoch: str = ""
    dS: float = 0.0
    peace2: float = 0.0
    kappa_r: float = 0.0
    shadow: float = 0.0
    confidence: float = 0.0
    psi_le: float = 0.0
    verdict: str = "open_tension"
    witness: dict[str, float] = Field(
        default_factory=lambda: {"human": 0.42, "ai": 0.32, "earth": 0.26}
    )
    qdf: str = ""


# ═══════════════════════════════════════════════════════════════════════════
# RESOLUTION
# ═══════════════════════════════════════════════════════════════════════════


class Resolution(BaseModel):
    resolution_type: ResolutionType | None = None
    resolved_by_activity: str | None = None
    resolved_by_agent: str | None = None
    resolved_at: str | None = None
    resolution_evidence_refs: list[str] = Field(default_factory=list)
    residual_uncertainty: float = Field(default=0.0, ge=0.0, le=1.0)


# ═══════════════════════════════════════════════════════════════════════════
# TENSION NODE (primary)
# ═══════════════════════════════════════════════════════════════════════════


class ParadoxTensionNode(BaseModel):
    """First-class epistemic object for institutional paradox.

    A tension node is not an error — it is an auditable unresolved structure
    in the belief graph that can trigger governance transitions, deeper inquiry,
    or protective holds.
    """

    tension_id: str
    type: str = Field(default="paradox_tension_node", frozen=True)
    title: str
    status: TensionStatus = TensionStatus.OPEN
    severity: Severity = Severity.MEDIUM
    tension_class: TensionClass
    summary: str = ""

    # References to companion nodes
    incident_refs: list[str] = Field(default_factory=list)
    subject_refs: list[str] = Field(default_factory=list)
    claim_refs: list[str] = Field(default_factory=list, min_length=2)
    actor_refs: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list, min_length=1)

    # Sub-objects
    provenance: Provenance
    scores: TensionScores
    relations: dict[str, list[str]] = Field(
        default_factory=lambda: {
            "supports": [],
            "attacks": [],
            "refines": [],
            "undercuts": [],
            "depends_on": [],
            "triggered_by": [],
            "resolved_by": [],
            "masked_by": [],
            "witnessed_by": [],
        }
    )

    # Temporal
    observed_from: str = ""
    observed_to: str | None = None
    deadline_at: str | None = None

    # Governance
    governance: GovernanceBinding = Field(default_factory=GovernanceBinding)

    # Resolution (only when status = resolved)
    resolution: Resolution | None = None

    # arifOS telemetry
    telemetry: TensionTelemetry = Field(default_factory=TensionTelemetry)

    model_config = {
        "json_schema_extra": {"examples": ["see contracts/paradox_tension_node.v1.json"]}
    }


# ═══════════════════════════════════════════════════════════════════════════
# BELIEF GRAPH (container)
# ═══════════════════════════════════════════════════════════════════════════


class BeliefGraph(BaseModel):
    """Container for an annotated governance episode."""

    graph_id: str
    title: str
    tensions: list[ParadoxTensionNode] = Field(default_factory=list)
    claims: list[ClaimNode] = Field(default_factory=list)
    evidence: list[EvidenceNode] = Field(default_factory=list)
    actors: list[ActorNode] = Field(default_factory=list)
    receipts: list[ReceiptNode] = Field(default_factory=list)
    activities: list[ActivityNode] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    def add_claim(self, claim: ClaimNode) -> None:
        self.claims.append(claim)

    def add_tension(self, tension: ParadoxTensionNode) -> None:
        self.tensions.append(tension)

    def find_claim(self, claim_id: str) -> ClaimNode | None:
        for c in self.claims:
            if c.claim_id == claim_id:
                return c
        return None

    def find_actor(self, actor_id: str) -> ActorNode | None:
        for a in self.actors:
            if a.actor_id == actor_id:
                return a
        return None

    def open_tensions(self) -> list[ParadoxTensionNode]:
        return [t for t in self.tensions if t.status != TensionStatus.RESOLVED]

    def critical_tensions(self) -> list[ParadoxTensionNode]:
        return [t for t in self.tensions if t.severity == Severity.CRITICAL]

    def to_provenance_chain(self) -> list[dict[str, Any]]:
        """Export as PROV-aligned activity chain."""
        chain: list[dict[str, Any]] = []
        for a in sorted(self.activities, key=lambda x: x.started_at):
            chain.append(
                {
                    "activity_id": a.activity_id,
                    "type": a.activity_type,
                    "started_at": a.started_at,
                    "actors": a.actors_involved,
                    "produced": a.produced_refs,
                }
            )
        for r in self.receipts:
            chain.append(
                {
                    "receipt_id": r.receipt_id,
                    "action_type": r.action_type,
                    "actor": r.actor_ref,
                    "timestamp": r.timestamp,
                    "hash": r.hash,
                }
            )
        return chain
