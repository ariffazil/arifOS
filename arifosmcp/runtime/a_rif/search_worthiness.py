"""
arifosmcp/runtime/a_rif/search_worthiness.py — Search Worthiness Gate
═════════════════════════════════════════════════════════════════════

Decides whether a search is worth executing.
W = (uncertainty × importance × freshness) / (noise × injection × cost)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from arifosmcp.runtime.a_rif.engine import calculate_search_worthiness
from arifosmcp.runtime.a_rif.models import SearchDecisionReceipt

__all__ = ["calculate_search_worthiness", "evaluate_search_decision"]


DEFAULT_THRESHOLD = 1.0


def evaluate_search_decision(
    query: str,
    uncertainty: float,
    importance: float,
    freshness: float,
    noise: float = 0.2,
    injection: float = 0.1,
    cost: float = 0.1,
    threshold: float = DEFAULT_THRESHOLD,
) -> SearchDecisionReceipt:
    """Evaluate whether a search should execute based on worthiness score."""
    w_score = calculate_search_worthiness(
        uncertainty=uncertainty,
        importance=importance,
        freshness=freshness,
        noise=noise,
        injection=injection,
        cost=cost,
    )

    if w_score < threshold:
        return SearchDecisionReceipt(
            query=query,
            decision="skip",
            w_score=w_score,
            reason=f"W-score {w_score} below threshold {threshold}",
        )

    return SearchDecisionReceipt(
        query=query,
        decision="search",
        w_score=w_score,
        reason=f"W-score {w_score} meets threshold {threshold}",
    )
