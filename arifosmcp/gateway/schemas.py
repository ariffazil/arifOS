"""
arifOS Kernel Primitives — Typed Constitutional Objects
══════════════════════════════════════════════════════

These schemas convert narrative ambiguity into structured, auditable
epistemic objects that can drive governance actions.

Every object carries:
  - identity: who/what this is
  - provenance: where it came from
  - epistemic_tag: CLAIM | PLAUSIBLE | HYPOTHESIS | EVIDENCE | VOID
  - receipt_ref: backlink to the receipt that sealed it
  - constitution_hash: which version of the constitution bound it

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════

class EpistemicTag(str, Enum):
    CLAIM = "CLAIM"
    PLAUSIBLE = "PLAUSIBLE"
    HYPOTHESIS = "HYPOTHESIS"
    EVIDENCE = "EVIDENCE"
    VOID = "VOID"


class TensionClass(str, Enum):
    PROMISE_VS_OUTCOME = "PROMISE_VS_OUTCOME"
    PASSIVE_OBSTACLE = "PASSIVE_OBSTACLE"
    SLIP_PHRASE = "SLIP_PHRASE"
    VOICE_ASYMMETRY = "VOICE_ASYMMETRY"
    EXPLICIT_VS_IMPLICIT = "EXPLICIT_VS_IMPLICIT"
    DEADLINE_VOID = "DEADLINE_VOID"
    JURISDICTION_TRAP = "JURISDICTION_TRAP"
    MEANING_LEAK = "MEANING_LEAK"
    SHADOW_DRIFT = "SHADOW_DRIFT"
    CONSTITUTIONAL_PARADOX = "CONSTITUTIONAL_PARADOX"


class TriggerKind(str, Enum):
    NAMED_ACTOR_SLIP_UNDER_HEDGED_FRAME = "named_actor_slip_under_hedged_frame"
    CONTRADICTORY_TIMELINE = "contradictory_timeline"
    PASSIVE_AGENCY_REMOVAL = "passive_agency_removal"
    QUOTE_ASYMMETRY = "quote_asymmetry"
    HEDGING_VS_HARD_FACT_COLLISION = "hedging_vs_hard_fact_collision"
    DEADLINE_WITHOUT_CLOSURE = "deadline_without_closure"
    MULTI_JURISDICTION_PING_PONG = "multi_jurisdiction_ping_pong"


class Verdict(str, Enum):
    SEAL = "SEAL"
    HOLD = "HOLD"
    VOID = "VOID"
    SABAR = "SABAR"
    ESCALATE = "ESCALATE"


class RiskClass(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    SOVEREIGN = "SOVEREIGN"


class ActionClass(str, Enum):
    OBSERVE = "OBSERVE"
    ANALYZE = "ANALYZE"
    REPORT = "REPORT"
    RECOMMEND = "RECOMMEND"
    HOLD = "HOLD"
    SEAL = "SEAL"


# ═══════════════════════════════════════════════════════════════════════════════
# BASE
# ═══════════════════════════════════════════════════════════════════════════════

class KernelNode(BaseModel):
    """Base for all constitutional kernel objects."""
    node_id: str = Field(default_factory=lambda: f"NODE-{uuid.uuid4().hex[:12]}")
    node_type: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    created_by: str = "arifOS-paradox-engine"
    constitution_hash: str = "sha256:arifos-constitution-v2026.05.05-SSCT"
    epistemic_tag: EpistemicTag = EpistemicTag.CLAIM
    provenance: str = ""
    receipt_refs: list[str] = Field(default_factory=list)
    _version: int = 1

    def content_hash(self) -> str:
        """Deterministic hash of node content for Merkle leaf."""
        payload = self.model_dump_json(exclude={"node_id", "created_at", "receipt_refs"})
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    @property
    def version(self) -> int:
        return self._version


# ═══════════════════════════════════════════════════════════════════════════════
# KERNEL PRIMITIVES
# ═══════════════════════════════════════════════════════════════════════════════

class ArticleNode(KernelNode):
    """A news article or institutional document ingested into the kernel."""
    node_type: Literal["ArticleNode"] = "ArticleNode"
    title: str
    source: str  # e.g., "Kosmo", "The Edge", "BERNAMA"
    author: str
    published_at: str
    url: str | None = None
    full_text_hash: str = ""
    article_id: str = Field(default_factory=lambda: f"ARTICLE-{uuid.uuid4().hex[:8]}")
    tags: list[str] = Field(default_factory=list)
    public_interest: RiskClass = RiskClass.MEDIUM


class ActorNode(KernelNode):
    """An actor (person, institution, group) in the frame graph."""
    node_type: Literal["ActorNode"] = "ActorNode"
    name: str
    actor_type: str  # "individual", "institution", "group", "government", "corporation"
    role_in_frame: str  # "hero", "gatekeeper", "victim", "villain_implicit", "observer"
    quote_count: int = 0
    agency_score: float = Field(default=0.5, ge=0.0, le=1.0)
    protection_level: float = Field(default=0.0, ge=0.0, le=1.0)


class ClaimNode(KernelNode):
    """A single claim extracted from the article."""
    node_type: Literal["ClaimNode"] = "ClaimNode"
    claim_text: str
    claimer: str
    claimer_type: str = "institution"
    evidence_support: float = Field(default=0.5, ge=0.0, le=1.0)
    hedging_detected: bool = False
    hedging_phrases: list[str] = Field(default_factory=list)
    contradicts: list[str] = Field(default_factory=list)
    supported_by: list[str] = Field(default_factory=list)


class ParadoxTensionNode(KernelNode):
    """The core kernel primitive — a detected tension/paradox in narrative."""
    node_type: Literal["ParadoxTensionNode"] = "ParadoxTensionNode"
    tension_id: str  # e.g., "PH-T1"
    tension_class: TensionClass
    trigger_kind: TriggerKind
    severity: float = Field(ge=0.0, le=1.0)
    shadow_score: float = Field(default=0.0, ge=0.0, le=1.0)
    article_ref: str = ""  # ArticleNode.node_id
    actor_refs: list[str] = Field(default_factory=list)
    claim_refs: list[str] = Field(default_factory=list)
    description: str = ""
    what_reporter_couldnt_say: str = ""
    evidence_snippets: list[str] = Field(default_factory=list)
    recommended_action: ActionClass = ActionClass.OBSERVE
    governance_pattern: str = ""  # "ACCIDENT_REPORT_LITIGATION_HOLD", etc.
    auto_tags: list[str] = Field(default_factory=list)


class TensionActivity(KernelNode):
    """Records an action taken on a tension node (detect, review, score, escalate)."""
    node_type: Literal["TensionActivity"] = "TensionActivity"
    activity_id: str = Field(default_factory=lambda: f"ACT-{uuid.uuid4().hex[:8]}")
    tension_ref: str  # ParadoxTensionNode.node_id
    action: ActionClass
    performed_by: str = "arifOS-paradox-engine"
    result: str = ""
    new_severity: float | None = None
    new_shadow_score: float | None = None


class ReceiptNode(KernelNode):
    """Immutable audit receipt for any kernel action."""
    node_type: Literal["ReceiptNode"] = "ReceiptNode"
    receipt_id: str = Field(default_factory=lambda: f"RCPT-{uuid.uuid4().hex[:12]}")
    activity_ref: str = ""
    tension_ref: str = ""
    node_ref: str = ""
    action: str = ""
    verdict: Verdict = Verdict.SEAL
    merkle_leaf_index: int | None = None
    merkle_root: str = ""
    content_hash: str = ""


class MerkleLeaf(KernelNode):
    """A leaf in the Merkle tree audit log."""
    node_type: Literal["MerkleLeaf"] = "MerkleLeaf"
    leaf_index: int
    tree_id: str
    content_hash: str = ""
    inclusion_proof: list[str] = Field(default_factory=list)
    root_hash: str = ""


# ═══════════════════════════════════════════════════════════════════════════════
# AGGREGATE
# ═══════════════════════════════════════════════════════════════════════════════

class ArticleFrameGraph(KernelNode):
    """Complete frame graph for one article."""
    node_type: Literal["ArticleFrameGraph"] = "ArticleFrameGraph"
    article: ArticleNode
    actors: list[ActorNode] = Field(default_factory=list)
    claims: list[ClaimNode] = Field(default_factory=list)
    tensions: list[ParadoxTensionNode] = Field(default_factory=list)
    activities: list[TensionActivity] = Field(default_factory=list)
    receipts: list[ReceiptNode] = Field(default_factory=list)
    shadow_drift_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    overall_verdict: Verdict = Verdict.HOLD
    auto_tags: list[str] = Field(default_factory=list)
    vault_uri: str = ""


# ═══════════════════════════════════════════════════════════════════════════════
# SERIALIZATION HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def serialize_graph(graph: ArticleFrameGraph) -> str:
    """Serialize the full frame graph to canonical JSON."""
    return graph.model_dump_json(indent=2)


def compute_merkle_leaf(node: KernelNode, tree_id: str, leaf_index: int) -> MerkleLeaf:
    """Create a Merkle leaf from any kernel node."""
    content_hash = node.content_hash()
    return MerkleLeaf(
        leaf_index=leaf_index,
        tree_id=tree_id,
        content_hash=content_hash,
        node_id=f"MERKLE-{uuid.uuid4().hex[:8]}",
    )
