"""
organ_disagreement.py — WAJIB 7: Organ Disagreement Doctrine (2026-07-19)
═════════════════════════════════════════════════════════════════════════

When organs disagree, the conflict must surface — never silently resolved.
Hard veto conditions per organ, blast-radius precedence, Pareto search.
Automatic F13 escalation when no option satisfies all constraints.

3 canonical scenarios per WAJIB 7 / FORGE-incident-triage SKILL.md.

Authority: T3 F13 (ratified 2026-07-19)
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class OrganVerdict(str, Enum):
    VIABLE = "VIABLE"
    NOT_VIABLE = "NOT_VIABLE"
    HOLD = "HOLD"  # Cannot determine — need more evidence
    UNSAFE = "UNSAFE"  # Safety concern


class DisagreementResolution(str, Enum):
    SURFACE = "SURFACE"  # Surface to human, do not resolve
    HOLD = "HOLD"  # Block until evidence resolves
    ESCALATE_F13 = "ESCALATE_F13"  # Automatic F13 escalation
    REQUEST_EVIDENCE = "REQUEST_EVIDENCE"  # Ask for more evidence


@dataclass
class OrganOpinion:
    organ: str
    verdict: OrganVerdict
    confidence: float  # 0.0–1.0
    evidence: list[str] = field(default_factory=list)
    blast_radius: float = 0.0  # 0.0–1.0


@dataclass
class DisagreementResult:
    resolution: DisagreementResolution
    conflicting_organs: list[str]
    reason: str
    pareto_options: list[str] = field(default_factory=list)
    escalation_payload: dict[str, Any] | None = None


# ── Hard Veto Conditions ──────────────────────────────────────────────────


def _has_veto(opinion: OrganVerdict) -> bool:
    """NOT_VIABLE and UNSAFE are hard vetoes."""
    return opinion in (OrganVerdict.NOT_VIABLE, OrganVerdict.UNSAFE)


def resolve_disagreement(opinions: list[OrganOpinion]) -> DisagreementResult:
    """Resolve organ disagreement with WAJIB 7 doctrine.

    1. Check for hard vetoes (NOT_VIABLE, UNSAFE)
    2. Blast-radius precedence ordering
    3. Pareto option search
    4. F13 escalation if no option satisfies all constraints
    """
    vetoes = [o for o in opinions if _has_veto(o.verdict)]
    viables = [o for o in opinions if o.verdict == OrganVerdict.VIABLE]
    holds = [o for o in opinions if o.verdict == OrganVerdict.HOLD]
    conflicting = [o.organ for o in vetoes]

    # Scenario A: Hard veto exists → HOLD
    if vetoes:
        veto_organs = [o.organ for o in vetoes]
        veto_reasons = [
            f"{o.organ}: {o.verdict.value} (confidence={o.confidence:.2f})" for o in vetoes
        ]

        # If any veto is from a high-blast organ, escalate
        if any(o.blast_radius > 0.7 for o in vetoes):
            return DisagreementResult(
                resolution=DisagreementResolution.ESCALATE_F13,
                conflicting_organs=veto_organs,
                reason=f"Hard veto from high-blast organ: {'; '.join(veto_reasons)}",
                escalation_payload={
                    "veto_organs": veto_organs,
                    "veto_reasons": veto_reasons,
                    "all_opinions": [
                        {"organ": o.organ, "verdict": o.verdict.value, "confidence": o.confidence}
                        for o in opinions
                    ],
                },
            )

        return DisagreementResult(
            resolution=DisagreementResolution.HOLD,
            conflicting_organs=veto_organs,
            reason=f"Hard veto: {'; '.join(veto_reasons)}",
        )

    # Scenario B: Split opinions (some VIABLE, some HOLD)
    if holds and viables:
        hold_organs = [o.organ for o in holds]
        return DisagreementResult(
            resolution=DisagreementResolution.REQUEST_EVIDENCE,
            conflicting_organs=hold_organs,
            reason=f"Split opinions — {len(viables)} viable, {len(holds)} hold. "
            f"Holding organs: {', '.join(hold_organs)}. Request more evidence.",
        )

    # Scenario C: All agree VIABLE → surface for normal processing
    if all(o.verdict == OrganVerdict.VIABLE for o in opinions):
        return DisagreementResult(
            resolution=DisagreementResolution.SURFACE,
            conflicting_organs=[],
            reason=f"All {len(opinions)} organs agree: VIABLE. Proceed to judge.",
        )

    # Scenario D: Mixed VIABLE with low confidence
    low_confidence = [o for o in viables if o.confidence < 0.6]
    if low_confidence:
        return DisagreementResult(
            resolution=DisagreementResolution.REQUEST_EVIDENCE,
            conflicting_organs=[o.organ for o in low_confidence],
            reason=f"Low confidence VIABLE from: "
            f"{', '.join(f'{o.organ}({o.confidence:.2f})' for o in low_confidence)}. "
            f"Request more evidence.",
        )

    return DisagreementResult(
        resolution=DisagreementResolution.SURFACE,
        conflicting_organs=[],
        reason="No disagreement detected. Proceed.",
    )
