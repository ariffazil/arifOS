"""
arifosmcp/core/conflict_resolver.py — Cross-Organ Conflict Resolver (#422)

Deterministic tie-breaking under 100ms.
Conflict resolution is NOT cognitive — it is constitutional.

The resolver NEVER analyzes, NEVER re-interprets, NEVER reasons.
It compares pre-declared authority weights + verdict classes only.

Design invariant: If conflict resolution requires reading payloads,
the design is already wrong. Resolver sees only headers.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import time
from enum import IntEnum

from arifosmcp.core.decision_contract import (
    ConflictEnvelope,
    ResolutionResult,
)


# ── Verdict dominance (total order) ──────────────────────────────
# Higher rank = more authoritative / more restrictive


class VerdictRank(IntEnum):
    PROCEED = 1
    SEAL = 2
    PARTIAL = 3
    SABAR = 4
    UNKNOWN = 5
    HOLD = 6
    VOID = 7  # highest — always wins


VERDICT_RANK: dict[str, VerdictRank] = {
    "PROCEED": VerdictRank.PROCEED,
    "SEAL_OBSERVE_ONLY": VerdictRank.PROCEED,  # OBSERVE_ONLY = read-only = same rank as PROCEED
    "SEAL": VerdictRank.SEAL,
    "PARTIAL": VerdictRank.PARTIAL,
    "SABAR": VerdictRank.SABAR,
    "UNKNOWN": VerdictRank.UNKNOWN,
    "HOLD": VerdictRank.HOLD,
    "VOID": VerdictRank.VOID,
}


# ── Organ authority hierarchy ────────────────────────────────────
# Higher rank = more constitutional authority


class OrganRank(IntEnum):
    CLERK = 1
    GEOX = 2
    WEALTH = 3
    WELL = 4
    AAA = 5
    A_FORGE = 6
    ARIFOS = 7
    HUMAN = 8  # highest — sovereign


ORGAN_RANK: dict[str, OrganRank] = {
    "clerk": OrganRank.CLERK,
    "geox": OrganRank.GEOX,
    "wealth": OrganRank.WEALTH,
    "well": OrganRank.WELL,
    "aaa": OrganRank.AAA,
    "a-forge": OrganRank.A_FORGE,
    "arifos": OrganRank.ARIFOS,
    "human": OrganRank.HUMAN,
}


# ── Escalation (direct contradictions) ──────────────────────────


def _needs_escalation(rank_a: VerdictRank, rank_b: VerdictRank) -> bool:
    """
    Check if the conflict requires 888_HOLD escalation.
    Escalation needed when:
    - One says PROCEED, other says VOID (true contradiction)
    - Both are UNKNOWN (insufficient information)
    - Both are HOLD (deadlock — needs human)

    NOT escalated (resolved by dominance):
    - SEAL vs HOLD → HOLD wins (monotonic — more restrictive dominates)
    - PARTIAL vs SEAL → SEAL wins
    - SABAR vs HOLD → HOLD wins
    """
    # True contradiction: one wants to proceed, other wants to void
    if rank_a == VerdictRank.PROCEED and rank_b == VerdictRank.VOID:
        return True
    if rank_b == VerdictRank.PROCEED and rank_a == VerdictRank.VOID:
        return True

    # Deadlock: both HOLD
    if rank_a == VerdictRank.HOLD and rank_b == VerdictRank.HOLD:
        return True

    # Both unknown
    if rank_a == VerdictRank.UNKNOWN and rank_b == VerdictRank.UNKNOWN:
        return True

    return False


# ── Resolver ─────────────────────────────────────────────────────


def resolve_conflict(envelope: ConflictEnvelope) -> ResolutionResult:
    """
    O(1) conflict resolution. No LLM. No reasoning. Pure lookup + compare.

    Rules:
    1. VOID always wins (hard stop)
    2. Higher organ authority wins (arifOS > GEOX)
    3. Within same organ, more restrictive verdict wins (HOLD > SEAL)
    4. If irreversible → bypass resolver → 888_HOLD
    5. If direct contradiction → escalate to 888_HOLD

    Returns ResolutionResult with latency in microseconds.
    """
    t0 = time.monotonic_ns()

    # Rule 4: Irreversible → always escalate
    if envelope.is_irreversible:
        return ResolutionResult(
            winner_organ="human",
            winner_verdict="888_HOLD",
            resolution_method="escalate",
            reason="Irreversible action requires sovereign approval (F1/F13)",
            requires_888_hold=True,
            latency_us=(time.monotonic_ns() - t0) // 1000,
        )

    rank_a = VERDICT_RANK.get(envelope.verdict_a, VerdictRank.UNKNOWN)
    rank_b = VERDICT_RANK.get(envelope.verdict_b, VerdictRank.UNKNOWN)
    organ_a_rank = ORGAN_RANK.get(envelope.organ_a.lower(), OrganRank.CLERK)
    organ_b_rank = ORGAN_RANK.get(envelope.organ_b.lower(), OrganRank.CLERK)

    # Rule 1: VOID always wins
    if rank_a == VerdictRank.VOID and rank_b != VerdictRank.VOID:
        return ResolutionResult(
            winner_organ=envelope.organ_a,
            winner_verdict=envelope.verdict_a,
            resolution_method="dominance",
            reason="VOID dominates all other verdicts",
            requires_888_hold=False,
            latency_us=(time.monotonic_ns() - t0) // 1000,
        )
    if rank_b == VerdictRank.VOID and rank_a != VerdictRank.VOID:
        return ResolutionResult(
            winner_organ=envelope.organ_b,
            winner_verdict=envelope.verdict_b,
            resolution_method="dominance",
            reason="VOID dominates all other verdicts",
            requires_888_hold=False,
            latency_us=(time.monotonic_ns() - t0) // 1000,
        )

    # Rule 5: Direct contradiction → escalate
    if _needs_escalation(rank_a, rank_b):
        return ResolutionResult(
            winner_organ="human",
            winner_verdict="888_HOLD",
            resolution_method="escalate",
            reason=(
                f"Direct contradiction: {envelope.verdict_a} ({envelope.organ_a}) "
                f"vs {envelope.verdict_b} ({envelope.organ_b}) — requires human judgment"
            ),
            requires_888_hold=True,
            latency_us=(time.monotonic_ns() - t0) // 1000,
        )

    # Rule 2: Higher organ authority wins
    if organ_a_rank != organ_b_rank:
        if organ_a_rank > organ_b_rank:
            return ResolutionResult(
                winner_organ=envelope.organ_a,
                winner_verdict=envelope.verdict_a,
                resolution_method="authority",
                reason=(
                    f"{envelope.organ_a} (rank {organ_a_rank}) "
                    f"outranks {envelope.organ_b} (rank {organ_b_rank})"
                ),
                requires_888_hold=False,
                latency_us=(time.monotonic_ns() - t0) // 1000,
            )
        else:
            return ResolutionResult(
                winner_organ=envelope.organ_b,
                winner_verdict=envelope.verdict_b,
                resolution_method="authority",
                reason=(
                    f"{envelope.organ_b} (rank {organ_b_rank}) "
                    f"outranks {envelope.organ_a} (rank {organ_a_rank})"
                ),
                requires_888_hold=False,
                latency_us=(time.monotonic_ns() - t0) // 1000,
            )

    # Rule 3: Same organ, more restrictive wins
    if rank_a >= rank_b:
        return ResolutionResult(
            winner_organ=envelope.organ_a,
            winner_verdict=envelope.verdict_a,
            resolution_method="dominance",
            reason=f"Same authority, more restrictive: {envelope.verdict_a} >= {envelope.verdict_b}",
            requires_888_hold=False,
            latency_us=(time.monotonic_ns() - t0) // 1000,
        )
    else:
        return ResolutionResult(
            winner_organ=envelope.organ_b,
            winner_verdict=envelope.verdict_b,
            resolution_method="dominance",
            reason=f"Same authority, more restrictive: {envelope.verdict_b} >= {envelope.verdict_a}",
            requires_888_hold=False,
            latency_us=(time.monotonic_ns() - t0) // 1000,
        )


# ── Multi-organ resolution ──────────────────────────────────────


def resolve_multi_organ(
    envelopes: list[ConflictEnvelope],
) -> ResolutionResult:
    """
    Resolve conflicts across N organs.
    Iteratively applies pairwise resolution.

    For 3+ organs: resolve pairs, then resolve winners.
    """
    if not envelopes:
        return ResolutionResult(
            winner_organ="human",
            winner_verdict="888_HOLD",
            resolution_method="escalate",
            reason="No conflicts to resolve",
            requires_888_hold=True,
            latency_us=0,
        )

    if len(envelopes) == 1:
        return resolve_conflict(envelopes[0])

    # C1 fix: pre-scan all envelopes for VOID before iterative loop.
    # VOID always wins — if any envelope has VOID verdict, the pairwise chain
    # must reach it even if an earlier pair escalates to 888_HOLD.
    for env in envelopes:
        rank_a = VERDICT_RANK.get(env.verdict_a, VerdictRank.UNKNOWN)
        rank_b = VERDICT_RANK.get(env.verdict_b, VerdictRank.UNKNOWN)
        if rank_a == VerdictRank.VOID or rank_b == VerdictRank.VOID:
            winner = env.organ_a if rank_a == VerdictRank.VOID else env.organ_b
            winner_verdict = env.verdict_a if rank_a == VerdictRank.VOID else env.verdict_b
            return ResolutionResult(
                winner_organ=winner,
                winner_verdict=winner_verdict,
                resolution_method="dominance",
                reason="VOID dominates all — pre-scan caught in multi-organ set",
                requires_888_hold=False,
                latency_us=0,
            )

    # Iterative pairwise resolution
    current = resolve_conflict(envelopes[0])
    for env in envelopes[1:]:
        # Create a new envelope with current winner vs next contender
        pairwise = ConflictEnvelope(
            conflict_id=env.conflict_id,
            organ_a=current.winner_organ,
            verdict_a=current.winner_verdict,
            organ_b=env.organ_b,
            verdict_b=env.verdict_b,
            conflict_domain=env.conflict_domain,
            is_irreversible=env.is_irreversible,
        )
        current = resolve_conflict(pairwise)
        if current.requires_888_hold:
            break  # No point continuing — needs human

    return current
