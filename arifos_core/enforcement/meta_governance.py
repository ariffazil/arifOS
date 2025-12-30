"""
meta_governance.py — Cross-Model Tri-Witness Aggregator (v45.1)

This module implements the "Governor of Governors" pattern:
- Multiple AI models vote on a decision
- Votes are weighted by confidence
- Consensus threshold determines final verdict

This is the 888_JUDGE aggregator for multi-model sovereignty.

Usage:
    from arifos_core.enforcement.meta_governance import meta_select, WitnessVote

    votes = [
        WitnessVote(witness_id="claude", preference="B", confidence=0.95, reason="HOLD purity"),
        WitnessVote(witness_id="gpt", preference="B", confidence=0.90, reason="Truth unverifiable"),
        WitnessVote(witness_id="gemini", preference="B", confidence=0.92, reason="Lower heat"),
    ]

    result = meta_select(votes, high_stakes=True)
    print(result)  # MetaVerdict with consensus and final decision
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timezone
from enum import Enum


# =============================================================================
# Data Models
# =============================================================================


class MetaVerdict(str, Enum):
    """Verdict from meta-selection (cross-model)."""

    SEAL = "SEAL"  # Consensus >= 0.95, proceed
    PARTIAL = "PARTIAL"  # Consensus >= 0.80 but < 0.95, proceed with flag
    HOLD_888 = "HOLD-888"  # Consensus < 0.80 OR high stakes with uncertainty
    DEADLOCK = "DEADLOCK"  # No clear majority


@dataclass
class WitnessVote:
    """A single witness vote in the Tri-Witness protocol."""

    witness_id: str  # e.g., "claude", "gpt", "gemini", "grok"
    preference: str  # e.g., "A", "B", or specific option
    confidence: float  # [0.0, 1.0] — how confident the witness is
    reason: str  # Why this preference
    timestamp: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class MetaSelectionResult:
    """Result of a meta-selection (cross-model vote)."""

    timestamp: str
    winner: str
    consensus: float  # Weighted agreement score
    verdict: MetaVerdict
    vote_count: int
    tally: Dict[str, float] = field(default_factory=dict)
    reasons: List[str] = field(default_factory=list)
    dissent: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = [
            "=" * 60,
            "🔮 TRI-WITNESS META-SELECTION RESULT",
            "=" * 60,
            f"Timestamp: {self.timestamp}",
            f"Winner: {self.winner}",
            f"Consensus: {self.consensus:.2%}",
            f"Verdict: {self.verdict.value}",
            f"Vote Count: {self.vote_count}",
            "",
            "📊 Vote Tally:",
        ]
        for option, weight in sorted(self.tally.items(), key=lambda x: -x[1]):
            lines.append(f"  {option}: {weight:.2f}")

        if self.reasons:
            lines.append("")
            lines.append("📝 Consensus Reasons:")
            for r in self.reasons[:3]:  # Top 3 reasons
                lines.append(f"  • {r}")

        if self.dissent:
            lines.append("")
            lines.append("⚠️ Dissent:")
            for d in self.dissent:
                lines.append(f"  • {d}")

        lines.append("=" * 60)
        return "\n".join(lines)


# =============================================================================
# Core Meta-Selection Algorithm
# =============================================================================

CONSENSUS_SEAL_THRESHOLD = 0.95  # Require 95% weighted consensus for SEAL
CONSENSUS_PARTIAL_THRESHOLD = 0.80  # Require 80% for PARTIAL


def meta_select(
    votes: List[WitnessVote],
    high_stakes: bool = False,
    require_unanimity: bool = False,
) -> MetaSelectionResult:
    """
    Aggregate multiple witness votes into a single meta-verdict.

    This is the 888_JUDGE aggregator for cross-model sovereignty.

    Args:
        votes: List of WitnessVote from different models
        high_stakes: If True, raises threshold and may trigger HOLD-888
        require_unanimity: If True, any dissent triggers HOLD-888

    Returns:
        MetaSelectionResult with winner, consensus, and verdict

    Algorithm:
        1. Tally weighted votes by preference
        2. Compute consensus as (winner_weight / total_weight)
        3. Apply threshold to determine verdict
        4. In high_stakes mode, lower consensus triggers HOLD-888
    """
    if not votes:
        return MetaSelectionResult(
            timestamp=datetime.now(timezone.utc).isoformat(),
            winner="NONE",
            consensus=0.0,
            verdict=MetaVerdict.DEADLOCK,
            vote_count=0,
            reasons=["No votes provided"],
        )

    # Step 1: Tally weighted votes
    tally: Dict[str, float] = {}
    reasons_by_preference: Dict[str, List[str]] = {}

    for vote in votes:
        pref = vote.preference
        tally[pref] = tally.get(pref, 0.0) + vote.confidence

        if pref not in reasons_by_preference:
            reasons_by_preference[pref] = []
        reasons_by_preference[pref].append(f"[{vote.witness_id}] {vote.reason}")

    # Step 2: Determine winner
    total_weight = sum(tally.values())
    winner = max(tally.items(), key=lambda x: x[1])[0]
    winner_weight = tally[winner]

    # Step 3: Compute consensus
    consensus = winner_weight / total_weight if total_weight > 0 else 0.0

    # Step 4: Collect reasons
    winner_reasons = reasons_by_preference.get(winner, [])

    # Step 5: Collect dissent
    dissent = []
    for pref, reasons in reasons_by_preference.items():
        if pref != winner:
            dissent.extend(reasons)

    # Step 6: Determine verdict
    if require_unanimity and dissent:
        verdict = MetaVerdict.HOLD_888
    elif high_stakes and consensus < CONSENSUS_SEAL_THRESHOLD:
        # In high stakes, we need strong consensus
        verdict = MetaVerdict.HOLD_888
    elif consensus >= CONSENSUS_SEAL_THRESHOLD:
        verdict = MetaVerdict.SEAL
    elif consensus >= CONSENSUS_PARTIAL_THRESHOLD:
        verdict = MetaVerdict.PARTIAL
    elif consensus >= 0.5:
        # Weak majority
        verdict = MetaVerdict.HOLD_888
    else:
        verdict = MetaVerdict.DEADLOCK

    return MetaSelectionResult(
        timestamp=datetime.now(timezone.utc).isoformat(),
        winner=winner,
        consensus=consensus,
        verdict=verdict,
        vote_count=len(votes),
        tally=tally,
        reasons=winner_reasons,
        dissent=dissent,
    )


# =============================================================================
# Convenience Functions
# =============================================================================


def create_vote(
    witness_id: str,
    preference: str,
    confidence: float,
    reason: str,
) -> WitnessVote:
    """Create a witness vote."""
    return WitnessVote(
        witness_id=witness_id,
        preference=preference,
        confidence=confidence,
        reason=reason,
    )


def tri_witness_vote(
    claude_vote: tuple,  # (preference, confidence, reason)
    gpt_vote: tuple,
    gemini_vote: tuple,
    high_stakes: bool = False,
) -> MetaSelectionResult:
    """
    Convenience function for the standard Tri-Witness pattern.

    Usage:
        result = tri_witness_vote(
            claude_vote=("B", 0.95, "HOLD purity"),
            gpt_vote=("B", 0.90, "Truth unverifiable"),
            gemini_vote=("B", 0.92, "Lower heat"),
            high_stakes=True,
        )
    """
    votes = [
        WitnessVote("claude", claude_vote[0], claude_vote[1], claude_vote[2]),
        WitnessVote("gpt", gpt_vote[0], gpt_vote[1], gpt_vote[2]),
        WitnessVote("gemini", gemini_vote[0], gemini_vote[1], gemini_vote[2]),
    ]
    return meta_select(votes, high_stakes=high_stakes)


def quad_witness_vote(
    claude_vote: tuple,
    gpt_vote: tuple,
    gemini_vote: tuple,
    grok_vote: tuple,
    high_stakes: bool = False,
) -> MetaSelectionResult:
    """
    Quad-Witness pattern (includes Grok).
    """
    votes = [
        WitnessVote("claude", claude_vote[0], claude_vote[1], claude_vote[2]),
        WitnessVote("gpt", gpt_vote[0], gpt_vote[1], gpt_vote[2]),
        WitnessVote("gemini", gemini_vote[0], gemini_vote[1], gemini_vote[2]),
        WitnessVote("grok", grok_vote[0], grok_vote[1], grok_vote[2]),
    ]
    return meta_select(votes, high_stakes=high_stakes)


# =============================================================================
# CLI Interface
# =============================================================================

if __name__ == "__main__":
    # Example: The actual Tri-Witness vote from this conversation
    print("=== LIVE TRI-WITNESS EXAMPLE ===")
    print("Scenario: RLHF selection between Response A (warm) and Response B (cold HOLD)")
    print()

    result = tri_witness_vote(
        claude_vote=("B", 0.95, "HOLD purity - truth unverifiable"),
        gpt_vote=("B", 0.90, "Constitutional drift risk in RLHF signals"),
        gemini_vote=("B", 0.92, "Lower heat under uncertainty"),
        high_stakes=True,
    )

    print(result)
