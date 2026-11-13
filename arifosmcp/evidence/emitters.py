"""
Envelope Emitters — per-organ helpers that wrap domain results.

These are the bridges between each organ's native return shape and the
cross-organ EvidenceEnvelope. The body of the work is small; the
discipline is the shape.

Each emitter takes the organ's domain result + the actor/session
context and produces a typed EvidenceEnvelope ready for arifOS 888_JUDGE.

DITEMPA BUKAN DIBERI — the blood type is forged.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from arifosmcp.schemas.envelope import (
    ContradictionEntry,
    EpistemicTag,
    EvidenceEnvelope,
    Reversibility,
    SourceAttribution,
    UncertaintyBand,
    ActorContext,
    Lineage,
)
from arifosmcp.evidence.law_evidence import compile_law_evidence, recommend_verdict


# ═══════════════════════════════════════════════════════════════════════════════
# Shared envelope builder
# ═══════════════════════════════════════════════════════════════════════════════


def _envelope(
    *,
    result: Any,
    organ: str,
    tool: str,
    actor_id: str,
    epistemic_tag: EpistemicTag,
    evidence_quality: float,
    p10: float,
    p50: float,
    p90: float,
    units: str = "unknown",
    session_id: Optional[str] = None,
    capability_grant_id: Optional[str] = None,
    autonomy_band: Optional[str] = None,
    actor_type: str = "agent",
    delta_S: float = 0.0,
    reversibility: Reversibility = Reversibility.REVERSIBLE,
    parent_evidence_refs: Optional[list[str]] = None,
    contradictions: Optional[list[ContradictionEntry]] = None,
    expires_at: Optional[datetime] = None,
    repo: Optional[str] = None,
    commit_sha: Optional[str] = None,
) -> EvidenceEnvelope:
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
        contradictions=contradictions or [],
        expires_at=expires_at,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# GEOX — earth evidence emitter
# ═══════════════════════════════════════════════════════════════════════════════


def emit_geox(
    *,
    tool: str,
    result: Any,
    actor_id: str,
    evidence_quality: float = 0.85,
    p10: float = 0.0,
    p50: float = 0.0,
    p90: float = 0.0,
    units: str = "geo",
    epistemic_tag: EpistemicTag = EpistemicTag.OBSERVED,
    session_id: Optional[str] = None,
    parent_evidence_refs: Optional[list[str]] = None,
    contradictions: Optional[list[ContradictionEntry]] = None,
    delta_S: float = 0.0,
) -> EvidenceEnvelope:
    """Wrap a GEOX tool result in the standard envelope.

    Convention: depth/error/volume results use OBSERVED; interpretations
    use DERIVED; prospects use HYPOTHESIS.
    """
    return _envelope(
        result=result,
        organ="geox",
        tool=tool,
        actor_id=actor_id,
        epistemic_tag=epistemic_tag,
        evidence_quality=evidence_quality,
        p10=p10,
        p50=p50,
        p90=p90,
        units=units,
        session_id=session_id,
        actor_type="agent",
        delta_S=delta_S,
        parent_evidence_refs=parent_evidence_refs,
        contradictions=contradictions,
        reversibility=Reversibility.REVERSIBLE,
        repo="ariffazil/geox",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# WEALTH — capital evidence emitter
# ═══════════════════════════════════════════════════════════════════════════════


def emit_wealth(
    *,
    tool: str,
    result: Any,
    actor_id: str,
    evidence_quality: float = 0.85,
    p10: float = 0.0,
    p50: float = 0.0,
    p90: float = 0.0,
    units: str = "USD",
    epistemic_tag: EpistemicTag = EpistemicTag.DERIVED,
    session_id: Optional[str] = None,
    reversibility: Reversibility = Reversibility.REVERSIBLE,
    parent_evidence_refs: Optional[list[str]] = None,
    contradictions: Optional[list[ContradictionEntry]] = None,
    delta_S: float = 0.0,
    action_cost: Optional[dict] = None,
) -> EvidenceEnvelope:
    """Wrap a WEALTH tool result in the standard envelope.

    Convention: macro/prices = OBSERVED; NPV/IRR/EMV = DERIVED; deal
    verdicts = HYPOTHESIS unless human-confirmed.
    """
    env = _envelope(
        result=result,
        organ="wealth",
        tool=tool,
        actor_id=actor_id,
        epistemic_tag=epistemic_tag,
        evidence_quality=evidence_quality,
        p10=p10,
        p50=p50,
        p90=p90,
        units=units,
        session_id=session_id,
        actor_type="agent",
        delta_S=delta_S,
        reversibility=reversibility,
        parent_evidence_refs=parent_evidence_refs,
        contradictions=contradictions,
        repo="ariffazil/wealth",
    )
    if action_cost is not None:
        env = env.model_copy(update={"action_cost": action_cost})
    return env


# ═══════════════════════════════════════════════════════════════════════════════
# WELL — readiness evidence emitter
# ═══════════════════════════════════════════════════════════════════════════════


def emit_well(
    *,
    tool: str,
    result: Any,
    actor_id: str,
    evidence_quality: float = 0.80,
    p10: float = 0.0,
    p50: float = 0.0,
    p90: float = 0.0,
    units: str = "readiness",
    epistemic_tag: EpistemicTag = EpistemicTag.OBSERVED,
    session_id: Optional[str] = None,
    parent_evidence_refs: Optional[list[str]] = None,
    contradictions: Optional[list[ContradictionEntry]] = None,
    delta_S: float = 0.0,
) -> EvidenceEnvelope:
    """Wrap a WELL tool result in the standard envelope.

    WELL always uses OBSERVED — it measures substrate state, not
    interprets it. Reflection, not judgment.
    """
    return _envelope(
        result=result,
        organ="well",
        tool=tool,
        actor_id=actor_id,
        epistemic_tag=epistemic_tag,
        evidence_quality=evidence_quality,
        p10=p10,
        p50=p50,
        p90=p90,
        units=units,
        session_id=session_id,
        actor_type="agent",
        delta_S=delta_S,
        parent_evidence_refs=parent_evidence_refs,
        contradictions=contradictions,
        reversibility=Reversibility.REVERSIBLE,
        repo="ariffazil/well",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# A-FORGE — execution evidence emitter
# ═══════════════════════════════════════════════════════════════════════════════


def emit_aforge(
    *,
    tool: str,
    result: Any,
    actor_id: str,
    evidence_quality: float = 0.95,
    p10: float = 0.0,
    p50: float = 0.0,
    p90: float = 0.0,
    units: str = "execution",
    epistemic_tag: EpistemicTag = EpistemicTag.OBSERVED,
    session_id: Optional[str] = None,
    reversibility: Reversibility = Reversibility.REVERSIBLE,
    parent_evidence_refs: Optional[list[str]] = None,
    contradictions: Optional[list[ContradictionEntry]] = None,
    delta_S: float = 0.0,
    action_cost: Optional[dict] = None,
) -> EvidenceEnvelope:
    """Wrap an A-FORGE execution result in the standard envelope.

    A-FORGE outputs are typically OBSERVED (build result, deploy
    receipt) with very high evidence_quality because the executor
    actually did the thing. IRREVERSIBLE actions are flagged here so
    the compiler can enforce L01.
    """
    env = _envelope(
        result=result,
        organ="a-forge",
        tool=tool,
        actor_id=actor_id,
        epistemic_tag=epistemic_tag,
        evidence_quality=evidence_quality,
        p10=p10,
        p50=p50,
        p90=p90,
        units=units,
        session_id=session_id,
        actor_type="agent",
        delta_S=delta_S,
        reversibility=reversibility,
        parent_evidence_refs=parent_evidence_refs,
        contradictions=contradictions,
        repo="ariffazil/A-FORGE",
    )
    if action_cost is not None:
        env = env.model_copy(update={"action_cost": action_cost})
    return env
