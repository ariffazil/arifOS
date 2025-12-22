"""
arifOS v45 - Conflict Routing (Sovereign Witness)
Deterministic routing based on physics attributes.
"""

from enum import Enum
from dataclasses import dataclass
from .evidence_pack import EvidencePack


class Verdict(str, Enum):
    SEAL = "SEAL"
    PARTIAL = "PARTIAL"
    SABAR = "SABAR"
    VOID = "VOID"
    HOLD_888 = "HOLD_888"


@dataclass
class RoutingResult:
    verdict: Verdict
    pathway: str  # FAST, SLOW, GOVERNED
    confidence_modifier: float
    reasons: list[str]


class ConflictRouter:
    """
    Sovereign Router - Physics First.
    Routes execution based on EvidencePack attributes.
    """

    # v45 Thresholds (Immutable)
    CONFLICT_THRESHOLD_HARD = 0.15
    COVERAGE_THRESHOLD_FULL = 1.0
    FRESHNESS_THRESHOLD_DECAY = 0.7

    @classmethod
    def evaluate(cls, pack: EvidencePack, requires_fact: bool = True) -> RoutingResult:
        reasons = []
        verdict = Verdict.SEAL
        pathway = "FAST"
        confidence_mod = 1.0

        # 1. Conflict Check (Primary Hard Floor)
        if pack.conflict_score > cls.CONFLICT_THRESHOLD_HARD:
            return RoutingResult(
                verdict=Verdict.HOLD_888,
                pathway="GOVERNED",
                confidence_modifier=0.0,
                reasons=[
                    f"Conflict score {pack.conflict_score:.2f} > {cls.CONFLICT_THRESHOLD_HARD}"
                ],
            )

        # 2. Coverage Check (Factuality)
        if requires_fact and pack.coverage_pct < cls.COVERAGE_THRESHOLD_FULL:
            # Downgrade to PARTIAL if evidence is incomplete but safe
            verdict = Verdict.PARTIAL
            pathway = "SLOW"
            reasons.append(f"Coverage {pack.coverage_pct:.2f} < 1.0")
            confidence_mod *= pack.coverage_pct

        # 3. Freshness Check (Temporal Decay)
        if pack.freshness_score < cls.FRESHNESS_THRESHOLD_DECAY:
            # Apply decay penalty
            reasons.append(
                f"Freshness {pack.freshness_score:.2f} < {cls.FRESHNESS_THRESHOLD_DECAY}"
            )
            decay_factor = pack.freshness_score / cls.FRESHNESS_THRESHOLD_DECAY
            confidence_mod *= decay_factor

            # If verdict was SEAL, downgrade to PARTIAL on staleness
            if verdict == Verdict.SEAL:
                verdict = Verdict.PARTIAL

        # 4. Pathway Selection
        # If conflict is non-zero but safe, or stale, force SLOW path
        if pack.conflict_score > 0.0 or verdict != Verdict.SEAL:
            pathway = "SLOW"

        return RoutingResult(
            verdict=verdict, pathway=pathway, confidence_modifier=confidence_mod, reasons=reasons
        )
