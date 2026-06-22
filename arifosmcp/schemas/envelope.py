"""
Cross-Organ Evidence Envelope — Item 1 of the Organ Forge
═══════════════════════════════════════════════════════════

The single contract every domain organ (GEOX, WEALTH, WELL, A-FORGE) and
every AAA-routed tool MUST return, so that arifOS 888_JUDGE can read one
shape instead of seven dialects.

Required fields on every cross-organ output:
  - result: domain payload (opaque to kernel, typed by organ)
  - epistemic_tag: 7-label evidence classification
  - evidence_quality: graded 0.0–1.0
  - source_attribution: who produced this, from what repo/commit
  - uncertainty_band: P10/P50/P90 (organ-specific shape, all 3 keys required)
  - delta_S: entropy change this answer caused (ΔS ≤ 0 per L04)
  - lineage: parent evidence_refs, sealing chain
  - actor_context: who triggered this, under which CapabilityGrant

Optional:
  - contradictions: list of contradicting evidence_refs (promotes HOLD)
  - reversibility: REVERSIBLE | PARTIALLY_REVERSIBLE | IRREVERSIBLE
  - action_cost: estimated resource cost to act on this evidence

DITEMPA BUKAN DIBERI — the missing blood type, now forged.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator

# ═══════════════════════════════════════════════════════════════════════════════
# 7-LABEL EVIDENCE CLASSIFICATION
# Extends the binary FACT/INTERPRETATION with full epistemic ladder.
# ═══════════════════════════════════════════════════════════════════════════════


class EpistemicTag(StrEnum):
    """7-label evidence ladder. Promoting a label requires a trail.

    FACT       — directly supported by current evidence or user authority
    OBSERVED   — seen in live output, logs, tests, or tool result
    DERIVED    — computed from facts with visible method
    INFERRED   — reasonable but not directly proven
    HYPOTHESIS — plausible route awaiting test (must carry a falsifier)
    UNVERIFIED — claimed but unsupported
    SIMULATION — non-authoritative rehearsal (explicit "sim" tag)
    """

    FACT = "FACT"
    OBSERVED = "OBSERVED"
    DERIVED = "DERIVED"
    INFERRED = "INFERRED"
    HYPOTHESIS = "HYPOTHESIS"
    UNVERIFIED = "UNVERIFIED"
    SIMULATION = "SIMULATION"


# ═══════════════════════════════════════════════════════════════════════════════
# REVERSIBILITY — for action classification on the envelope
# ═══════════════════════════════════════════════════════════════════════════════


class Reversibility(StrEnum):
    REVERSIBLE = "REVERSIBLE"
    PARTIALLY_REVERSIBLE = "PARTIALLY_REVERSIBLE"
    IRREVERSIBLE = "IRREVERSIBLE"


# ═══════════════════════════════════════════════════════════════════════════════
# SOURCE ATTRIBUTION — who, where, when, which commit
# ═══════════════════════════════════════════════════════════════════════════════


class SourceAttribution(BaseModel):
    """Provenance chain for the evidence."""

    organ: str = Field(
        ..., description="Federation organ that produced this (geox/wealth/well/a-forge/aaa)"
    )
    tool: str = Field(..., description="Tool name within the organ")
    repo: str | None = Field(None, description="Repo (e.g. ariffazil/geox)")
    commit_sha: str | None = Field(None, description="Git commit at time of production")
    actor_id: str | None = Field(None, description="Agent or human that triggered the call")
    capability_grant_id: str | None = Field(
        None, description="CapabilityGrant that authorized this"
    )
    produced_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# ═══════════════════════════════════════════════════════════════════════════════
# UNCERTAINTY BAND — universal P10/P50/P90 (organ-specific values inside)
# ═══════════════════════════════════════════════════════════════════════════════


class UncertaintyBand(BaseModel):
    """P10/P50/P90 envelope. Units and meaning are organ-specific.
    Required keys: p10, p50, p90. For unitless or scalar evidence, set
    all three to the same value and set dimensionless=True.
    """

    p10: float
    p50: float
    p90: float
    units: str = "unknown"
    dimensionless: bool = False

    @model_validator(mode="after")
    def _check_order(self) -> UncertaintyBand:
        if not (self.p10 <= self.p50 <= self.p90):
            raise ValueError(
                f"UncertaintyBand requires p10 ≤ p50 ≤ p90; got "
                f"{self.p10} / {self.p50} / {self.p90}"
            )
        return self


# ═══════════════════════════════════════════════════════════════════════════════
# LINEAGE — parent evidence refs + sealing chain
# ═══════════════════════════════════════════════════════════════════════════════


class Lineage(BaseModel):
    """Where did this evidence come from? Where can it flow?"""

    parent_evidence_refs: list[str] = Field(
        default_factory=list,
        description="Evidence IDs this output is derived from (empty for OBSERVED primary)",
    )
    derived_from: list[str] = Field(
        default_factory=list,
        description="Sealed vault entries this output references",
    )
    children: list[str] = Field(
        default_factory=list,
        description="Evidence IDs that have cited this one (filled by promotion)",
    )
    seal_chain: list[str] = Field(
        default_factory=list,
        description="VAULT999 seal hashes forming the chain back to L6",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ACTOR CONTEXT — who triggered this, under what authority
# ═══════════════════════════════════════════════════════════════════════════════


class ActorContext(BaseModel):
    """Identity + grant context for the call. F11 AUTH and L11."""

    actor_id: str = Field(..., description="Agent or human identity")
    actor_type: str = Field(..., description="human | agent | system | sovereign")
    session_id: str | None = Field(None, description="arif_init session hash")
    capability_grant_id: str | None = Field(None, description="Active grant for this tool")
    autonomy_band: str | None = Field(None, description="GREEN/YELLOW/ORANGE/RED/BLACK")


# ═══════════════════════════════════════════════════════════════════════════════
# CONTRADICTION ENTRY — first-class disagreement record
# ═══════════════════════════════════════════════════════════════════════════════


class ContradictionEntry(BaseModel):
    """When two organs disagree, the disagreement is a first-class event."""

    evidence_ref: str = Field(..., description="ID of the contradicting evidence")
    organ: str = Field(..., description="Organ that produced the contradiction")
    epistemic_tag: EpistemicTag
    summary: str = Field(..., description="Why this contradicts")
    weight: float = Field(1.0, ge=0.0, le=1.0, description="Severity 0..1")


# ═══════════════════════════════════════════════════════════════════════════════
# THE ENVELOPE — what every cross-organ output MUST look like
# ═══════════════════════════════════════════════════════════════════════════════


class EvidenceEnvelope(BaseModel):
    """The cross-organ evidence envelope.

    Every output from GEOX, WEALTH, WELL, A-FORGE, and AAA-routed tools
    SHOULD wrap their domain result in this shape. arifOS 888_JUDGE will
    read only this shape (plus the organ-specific domain payload inside
    ``result``).
    """

    # Identity
    envelope_id: str = Field(default_factory=lambda: f"env_{uuid4().hex[:12]}")
    schema_version: str = "1.0.0"

    # Domain payload (opaque to kernel)
    result: Any = Field(..., description="Domain-specific payload (organ dialect)")

    # 7-label evidence classification (L02 TRUTH, L07 HUMILITY)
    epistemic_tag: EpistemicTag
    evidence_quality: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Graded 0.0 (low) .. 1.0 (high). L02 threshold ≥0.99 for FACT.",
    )

    # Provenance
    source: SourceAttribution
    uncertainty: UncertaintyBand

    # Entropy & lineage
    delta_S: float = Field(0.0, description="Entropy change this answer caused. L04 requires ≤ 0.")
    lineage: Lineage = Field(default_factory=Lineage)

    # Authority
    actor: ActorContext

    # Action classification (for downstream gating)
    reversibility: Reversibility = Reversibility.REVERSIBLE
    action_cost: dict[str, Any] | None = Field(
        default=None,
        description="Optional cost estimate: {compute_seconds, tokens, money, blast_radius}",
    )

    # Contradiction
    contradictions: list[ContradictionEntry] = Field(default_factory=list)

    # Runtime provenance (L11 AUTH + L13 SOVEREIGN — disambiguate model claim from runtime)
    # Forged 2026-06-06 in response to the Royal Decree incident: a model can claim to be
    # anything in its output, but the runtime that wrapped the output knows the truth.
    # Required for any AGI-lane output bound for operator surfaces (Telegram/cockpit).
    runtime_model: str | None = Field(
        None,
        description=(
            "The actual model id that produced the result (e.g. 'minimax/MiniMax-M3', "
            "'ilmu-nemo-nano'). This is asserted by the runtime, not the model itself. "
            "A claim of model identity inside `result` is non-authoritative."
        ),
    )
    runtime_model_source: str | None = Field(
        None,
        description=(
            "How `runtime_model` was determined: 'config' (from openclaw.json) | "
            "'journal' (from openclaw-gateway logs) | 'claimed' (from model self-report, "
            "non-authoritative). Default null = unknown / not asserted."
        ),
    )
    runtime_lane: str | None = Field(
        None,
        description=(
            "Constitutional lane that produced this output: 000/111/222/333/444/555/"
            "666/777 (AGI/ASI/APEX). 888 = judge, 999 = vault. Mismatch between "
            "`runtime_lane` and the verdict authority is an L11 violation."
        ),
    )

    # Timestamps
    produced_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = Field(
        None,
        description="Optional TTL — envelope is stale after this time",
    )

    @model_validator(mode="after")
    def _check_quality_for_fact(self) -> EvidenceEnvelope:
        """L02 TRUTH: FACT requires evidence_quality ≥ 0.99.

        Note: This is a soft check that yields a value error only for
        blatant contradictions (e.g. quality > 1.0). The hard FACT
        quality gate lives in the policy engine (memory.policies.decide)
        so it can produce a HOLD decision rather than a parse error.
        """
        if self.evidence_quality > 1.0 or self.evidence_quality < 0.0:
            raise ValueError(f"evidence_quality out of [0,1]: {self.evidence_quality}")
        # L04 CLARITY
        if self.delta_S > 0.0:
            raise ValueError(f"L04 CLARITY: delta_S must be ≤ 0; got {self.delta_S}")
        return self

    def is_stale(self, now: datetime | None = None) -> bool:
        """True if the envelope has passed its expiry."""
        if self.expires_at is None:
            return False
        now = now or datetime.now(UTC)
        return now > self.expires_at

    def has_contradictions(self) -> bool:
        return len(self.contradictions) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER — wrap a raw result in an envelope
# ═══════════════════════════════════════════════════════════════════════════════


def wrap_envelope(
    result: Any,
    *,
    organ: str,
    tool: str,
    actor_id: str,
    epistemic_tag: EpistemicTag,
    evidence_quality: float,
    p10: float,
    p50: float,
    p90: float,
    units: str = "unknown",
    parent_evidence_refs: list[str] | None = None,
    actor_type: str = "agent",
    session_id: str | None = None,
    capability_grant_id: str | None = None,
    autonomy_band: str | None = None,
    delta_S: float = 0.0,
    reversibility: Reversibility = Reversibility.REVERSIBLE,
    repo: str | None = None,
    commit_sha: str | None = None,
    expires_at: datetime | None = None,
    runtime_model: str | None = None,
    runtime_model_source: str | None = None,
    runtime_lane: str | None = None,
) -> EvidenceEnvelope:
    """Convenience: wrap a domain result in the standard envelope.

    All organs and AAA-routed tools SHOULD use this helper so the shape
    stays consistent.
    """
    return EvidenceEnvelope(
        result=result,
        epistemic_tag=epistemic_tag,
        evidence_quality=evidence_quality,
        source=SourceAttribution(
            organ=organ,
            tool=tool,
            repo=repo,
            commit_sha=commit_sha,
            actor_id=actor_id,
            capability_grant_id=capability_grant_id,
        ),
        uncertainty=UncertaintyBand(p10=p10, p50=p50, p90=p90, units=units),
        delta_S=delta_S,
        lineage=Lineage(parent_evidence_refs=parent_evidence_refs or []),
        actor=ActorContext(
            actor_id=actor_id,
            actor_type=actor_type,
            session_id=session_id,
            capability_grant_id=capability_grant_id,
            autonomy_band=autonomy_band,
        ),
        reversibility=reversibility,
        expires_at=expires_at,
        runtime_model=runtime_model,
        runtime_model_source=runtime_model_source,
        runtime_lane=runtime_lane,
    )
