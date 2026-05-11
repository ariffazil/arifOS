"""
core/paradox/conflict_resolver.py — P3 Conflicting Verdicts Resolution

Implements PARADOX_DOCTRINE_V1 Section 4 (P3 — Conflicting Verdicts).

Conservative Wins protocol:
  VOID > HOLD > SABAR > PARTIAL > SEAL

When multiple agents disagree, the most restrictive verdict prevails.
Dissenter reasoning is always preserved in the audit trail.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# Canonical verdict conservatism ranking (higher = more restrictive)
_VERDICT_RANK: dict[str, int] = {
    "VOID": 5,
    "void": 5,
    "HOLD_888": 4,
    "hold_888": 4,
    "HOLD": 4,
    "hold": 4,
    "SABAR": 3,
    "sabar": 3,
    "PARTIAL": 2,
    "partial": 2,
    "SEAL": 1,
    "seal": 1,
}


@dataclass
class ConflictResolution:
    final_verdict: str
    method: str
    dissenter: str | None
    all_dissenters: list[str] = field(default_factory=list)
    dissenter_preserved: bool = True
    trust_consequences: dict[str, Any] = field(default_factory=dict)
    escalation_required: bool = False


def conservative_wins(verdicts: list[str]) -> str:
    """Return the most conservative verdict from a list.

    Ranking (most restrictive first):
        VOID > HOLD > SABAR > PARTIAL > SEAL
    """
    if not verdicts:
        return "SEAL"

    ranked = [(v, _VERDICT_RANK.get(v, 0)) for v in verdicts]
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked[0][0]


def resolve_verdict_conflict(
    verdicts: list[dict[str, Any]],
    recent_conflict_count: int = 0,
) -> ConflictResolution:
    """Resolve conflicting agent verdicts per Conservative Wins.

    Args:
        verdicts: List of dicts with keys: agent, verdict, reasoning_hash, confidence
        recent_conflict_count: Number of recent conflicts between same agents (24h window)

    Returns:
        ConflictResolution with final_verdict, method, dissenter info, trust notes.
    """
    if not verdicts:
        return ConflictResolution(
            final_verdict="SEAL",
            method="UNANIMOUS_EMPTY",
            dissenter=None,
        )

    if len(verdicts) == 1:
        return ConflictResolution(
            final_verdict=verdicts[0].get("verdict", "SEAL"),
            method="SINGLE_AGENT",
            dissenter=None,
        )

    verdict_values = [v.get("verdict", "SEAL") for v in verdicts]
    final = conservative_wins(verdict_values)

    # If all agents already agree on the conservative outcome, it is unanimous
    non_consensus = any(v != final for v in verdict_values)
    method = "CONSERVATIVE_WINS" if non_consensus else "UNANIMOUS"

    dissenters = [
        v["agent"] for v in verdicts
        if v.get("verdict", "") != final
    ]

    # Escalation trigger: same pair(s) conflicting 3+ times in 24h window
    escalation = recent_conflict_count >= 3

    return ConflictResolution(
        final_verdict=final,
        method=method,
        dissenter=dissenters[0] if dissenters else None,
        all_dissenters=dissenters,
        dissenter_preserved=True,
        trust_consequences={
            "dissenter_trust_adjustment": 0.0,
            "note": (
                "Disagreement is healthy. "
                "Only pattern of repeated dissent-when-wrong is penalized."
            ),
        },
        escalation_required=escalation,
    )
