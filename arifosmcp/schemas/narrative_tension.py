"""
arifosmcp/schemas/narrative_tension.py
═══════════════════════════════════════════════════════════════════
Cross-node contract for Narrative Tension / Frame Graph analysis.

This schema formalises what a reporter's geometry leaks: paradox tension,
power asymmetry, implicit frames, and contradictions between claim and
outcome. It is the perception kernel's data structure for reading the
denyut nadi kuasa in human text.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, field_validator


class BaseNode(BaseModel):
    """Common provenance fields for every node in the narrative graph."""

    node_type: str = Field(..., description="Discriminator for the node kind.")
    node_id: str = Field(..., description="Stable identifier for this node.")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the node was forged.",
    )
    created_by: str = Field(
        default="arifOS-paradox-engine",
        description="Agent or process that produced this node.",
    )
    constitution_hash: str | None = Field(
        default=None,
        description="Hash of the constitution under which this node was produced.",
    )
    epistemic_tag: str = Field(
        default="PLAUSIBLE",
        pattern="^(CLAIM|PLAUSIBLE|HYPOTHESIS|EVIDENCE|ESTIMATE)$",
        description="Confidence class for the node's contents.",
    )
    provenance: str = Field(
        default="",
        description="Human-readable provenance for this node.",
    )
    receipt_refs: list[str] = Field(
        default_factory=list,
        description="VAULT999 receipt references that anchor this node.",
    )


class ArticleNode(BaseNode):
    """A text artefact ingested for frame analysis."""

    article_id: str = Field(..., description="Unique article identifier.")
    title: str = Field(..., description="Headline or title.")
    source: str = Field(default="", description="Publication / outlet.")
    author: str | None = Field(default=None, description="Reporter byline.")
    published_at: str | None = Field(default=None, description="ISO-8601 publish timestamp.")
    url: str | None = Field(default=None, description="Canonical URL if available.")
    full_text_hash: str | None = Field(default=None, description="SHA256 prefix of full text.")
    tags: list[str] = Field(default_factory=list)
    public_interest: str = Field(
        default="MEDIUM",
        pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$",
    )


class ActorNode(BaseNode):
    """An actor observed in the narrative frame."""

    name: str = Field(..., description="Actor name or descriptor.")
    actor_type: str = Field(
        default="unknown",
        description="individual | group | government | corporation | institution | unknown",
    )
    role_in_frame: str = Field(
        default="other",
        description="hero | gatekeeper | villain_implicit | villain_explicit | victim | observer | other",
    )
    quote_count: int = Field(default=0, ge=0)
    agency_score: float = Field(default=0.5, ge=0.0, le=1.0)
    protection_level: float = Field(default=0.5, ge=0.0, le=1.0)


class ClaimNode(BaseNode):
    """A single claim extracted from the text."""

    claim_text: str = Field(..., description="The claim as stated or paraphrased.")
    claimer: str = Field(default="", description="Who made the claim.")
    claimer_type: str = Field(default="unknown")
    evidence_support: float = Field(default=0.5, ge=0.0, le=1.0)
    hedging_detected: bool = Field(default=False)
    hedging_phrases: list[str] = Field(default_factory=list)
    contradicts: list[str] = Field(default_factory=list)
    supported_by: list[str] = Field(default_factory=list)


class ParadoxTensionNode(BaseNode):
    """
    A detected paradox / tension in the narrative geometry.

    This is the first-class object the perception kernel returns when it
    senses that a reporter's text is carrying more meaning than the literal
    surface allows.
    """

    tension_id: str = Field(..., description="Short tension identifier, e.g. PH-T1.")
    tension_class: str = Field(
        ...,
        description=(
            "PROMISE_VS_OUTCOME | PASSIVE_OBSTACLE | SLIP_PHRASE | VOICE_ASYMMETRY | "
            "EXPLICIT_VS_IMPLICIT | DEADLINE_VOID | JURISDICTION_TRAP | OTHER"
        ),
    )
    trigger_kind: str = Field(..., description="Specific trigger pattern.")
    severity: float = Field(..., ge=0.0, le=1.0)
    shadow_score: float = Field(default=0.0, ge=0.0, le=1.0)
    article_ref: str = Field(..., description="Reference to the source ArticleNode.")
    actor_refs: list[str] = Field(default_factory=list)
    claim_refs: list[str] = Field(default_factory=list)
    description: str = Field(..., description="What the kernel detected.")
    what_reporter_couldnt_say: str = Field(
        default="",
        description="The implicit meaning the reporter could not state explicitly.",
    )
    evidence_snippets: list[str] = Field(default_factory=list)
    recommended_action: str = Field(
        default="OBSERVE",
        pattern="^(OBSERVE|REPORT|HOLD|ESCALATE|SEAL)$",
    )
    governance_pattern: str = Field(
        default="",
        description="Recommended arifOS governance pattern to apply.",
    )
    auto_tags: list[str] = Field(default_factory=list)


class FrameGraph(BaseNode):
    """The complete frame graph for an article."""

    article: ArticleNode
    actors: list[ActorNode] = Field(default_factory=list)
    claims: list[ClaimNode] = Field(default_factory=list)
    tensions: list[ParadoxTensionNode] = Field(default_factory=list)


class KernelVerdict(BaseModel):
    """Aggregate verdict produced by the perception kernel for an article."""

    kernel_verdict_id: str = Field(...)
    article_id: str = Field(...)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    shadow_drift_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    max_severity: float = Field(default=0.0, ge=0.0, le=1.0)
    smoking_gun: str | None = Field(default=None)
    smoking_gun_severity: float | None = Field(default=None)
    overall_verdict: str = Field(
        default="OBSERVE",
        pattern="^(SEAL|OBSERVE|REPORT|HOLD|ESCALATE|VOID)$",
    )
    governance_patterns_detected: list[str] = Field(default_factory=list)
    auto_tags: list[str] = Field(default_factory=list)
    detected_actors: int = Field(default=0)
    detected_claims: int = Field(default=0)
    detected_tensions: int = Field(default=0)
    voice_asymmetry: str = Field(default="")
    epistemic_isolation_flag: bool = Field(
        default=False,
        description="True when the reporter cannot state the tension explicitly.",
    )
    epistemic_isolation_note: str = Field(default="")
    vault_uris: list[str] = Field(default_factory=list)
    constitution_hash: str | None = Field(default=None)


class NarrativeTensionRequest(BaseModel):
    """Request to detect narrative tension in a text."""

    article_id: str | None = Field(
        default=None,
        description="Optional stable article identifier; used to load golden cases.",
    )
    title: str = Field(..., description="Article title / headline.")
    source: str = Field(default="", description="Publication source.")
    author: str | None = Field(default=None)
    published_at: str | None = Field(default=None)
    url: str | None = Field(default=None)
    text: str = Field(..., description="Full article text to analyse.")
    tags: list[str] = Field(default_factory=list)
    public_interest: str = Field(default="MEDIUM", pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    actor_hints: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Optional hints for actor extraction.",
    )

    @field_validator("public_interest", mode="before")
    @classmethod
    def _coerce_public_interest(cls, v: Any) -> str:
        if isinstance(v, bool):
            return "HIGH" if v else "MEDIUM"
        return str(v).upper()


class NarrativeTensionResponse(BaseModel):
    """Response after narrative tension analysis."""

    status: str = Field(default="OK")
    tool: str = Field(default="arif_detect_narrative_tension")
    verdict: str = Field(default="OBSERVE")
    frame_graph: FrameGraph
    kernel_verdict: KernelVerdict
    vault_receipt: dict[str, Any] | None = Field(
        default=None,
        description="Best-effort VAULT999 receipt summary.",
    )
    next_safe_action: str = Field(default="")


__all__ = [
    "ArticleNode",
    "ActorNode",
    "ClaimNode",
    "ParadoxTensionNode",
    "FrameGraph",
    "KernelVerdict",
    "NarrativeTensionRequest",
    "NarrativeTensionResponse",
]
