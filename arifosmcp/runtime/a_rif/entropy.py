"""
arifosmcp/runtime/a_rif/entropy.py — Entropy-Based Search Stopping Law
══════════════════════════════════════════════════════════════════════

Search is useful only if it reduces uncertainty.
ΔS = entropy_after - entropy_before

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from arifosmcp.runtime.a_rif.engine import evaluate_entropy_delta
from arifosmcp.runtime.a_rif.models import EntropyReport

__all__ = ["evaluate_entropy_delta", "should_stop_search"]

PLATEAU_THRESHOLD = 0.01


def should_stop_search(
    before: float,
    after: float,
    plateau_threshold: float = PLATEAU_THRESHOLD,
) -> EntropyReport:
    """
    Decide whether to stop searching based on entropy change.

    - delta_s > 0  → search increased uncertainty → VOID
    - |delta_s| < plateau → no meaningful change → STOP
    - delta_s < -plateau → uncertainty reduced → CONTINUE
    """
    delta_s = evaluate_entropy_delta(before, after)

    if delta_s > 0:
        return EntropyReport(
            before=before,
            after=after,
            delta_s=delta_s,
            recommendation="void",
            reason="Search increased uncertainty (positive ΔS)",
        )

    if abs(delta_s) < plateau_threshold:
        return EntropyReport(
            before=before,
            after=after,
            delta_s=delta_s,
            recommendation="stop",
            reason="Entropy plateau — no meaningful reduction",
        )

    return EntropyReport(
        before=before,
        after=after,
        delta_s=delta_s,
        recommendation="continue",
        reason="Uncertainty reduced — search is productive",
    )
