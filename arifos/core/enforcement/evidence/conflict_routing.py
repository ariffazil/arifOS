"""
arifOS v46 - Conflict Routing (Sovereign Witness)
Deterministic routing based on physics attributes.

ARCHITECTURAL CLARIFICATION:
This module returns ROUTING RECOMMENDATIONS based on evidence quality.
It does NOT issue constitutional verdicts - only APEX PRIME has that authority.

v46 Refactor: Replaced Verdict enum with RoutingSignal to enforce architectural clarity.
"""

from dataclasses import dataclass
from .evidence_pack import EvidencePack
from .routing_signal import RoutingSignal, routing_signal_to_pathway


@dataclass
class RoutingResult:
    """
    Evidence-based routing recommendation.

    Fields:
        signal: Routing recommendation (NOT a constitutional verdict)
        pathway: Execution pathway (FAST, SLOW, GOVERNED)
        confidence_modifier: Confidence adjustment based on evidence quality
        reasons: Human-readable routing rationale
    """
    signal: RoutingSignal
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
        """
        Evaluate EvidencePack and return routing recommendation.

        IMPORTANT: This returns a RoutingSignal (routing recommendation),
        NOT a constitutional Verdict. Only APEX PRIME issues verdicts.

        Args:
            pack: EvidencePack with conflict, coverage, freshness scores
            requires_fact: Whether factual verification is required

        Returns:
            RoutingResult with signal, pathway, and confidence modifier
        """
        reasons = []
        signal = RoutingSignal.FAST_PATH
        confidence_mod = 1.0

        # 1. Conflict Check (Primary Hard Floor)
        if pack.conflict_score > cls.CONFLICT_THRESHOLD_HARD:
            return RoutingResult(
                signal=RoutingSignal.GOVERNED,
                pathway="GOVERNED",
                confidence_modifier=0.0,
                reasons=[
                    f"Conflict score {pack.conflict_score:.2f} > {cls.CONFLICT_THRESHOLD_HARD}"
                ],
            )

        # 1b. Fail-closed: "No evidence" on factual routing blocks processing
        if requires_fact and pack.coverage_pct <= 0.0:
            return RoutingResult(
                signal=RoutingSignal.BLOCKED,
                pathway="GOVERNED",
                confidence_modifier=0.0,
                reasons=["No evidence coverage for factual routing (coverage_pct=0.0)"],
            )

        # 2. Coverage Check (Factuality)
        if requires_fact and pack.coverage_pct < cls.COVERAGE_THRESHOLD_FULL:
            # Route to SLOW path if evidence is incomplete but safe
            signal = RoutingSignal.SLOW_PATH
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

            # If signal was FAST_PATH, downgrade to SLOW_PATH on staleness
            if signal == RoutingSignal.FAST_PATH:
                signal = RoutingSignal.SLOW_PATH

        # 4. Determine final pathway from signal
        pathway = routing_signal_to_pathway(signal)

        # Override pathway if any issues detected
        if pack.conflict_score > 0.0 or signal != RoutingSignal.FAST_PATH:
            pathway = "SLOW"

        return RoutingResult(
            signal=signal, pathway=pathway, confidence_modifier=confidence_mod, reasons=reasons
        )
