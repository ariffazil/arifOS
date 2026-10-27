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

__all__ = ["evaluate_entropy_delta", "should_stop_search", "measure_shannon_entropy", "measure_delta_s"]

PLATEAU_THRESHOLD = 0.01


def measure_shannon_entropy(text: str | None) -> float | None:
    """Measure character-level Shannon entropy normalised by log2(alphabet size)."""
    if not text or not str(text).strip():
        return None
    import math
    _str = str(text)
    freq: dict[str, int] = {}
    for ch in _str:
        freq[ch] = freq.get(ch, 0) + 1
    n = len(_str)
    if n == 0:
        return None
    h = -sum((c / n) * math.log2(c / n) for c in freq.values())
    max_h = math.log2(max(len(freq), 2))
    return round(h / max_h, 4) if max_h > 0 else None


def measure_delta_s(before_text: str | None, after_text: str | None) -> float | None:
    """Measure change in Shannon entropy: after - before."""
    s_before = measure_shannon_entropy(before_text)
    s_after = measure_shannon_entropy(after_text)
    if s_before is None or s_after is None:
        return None
    return round(s_after - s_before, 4)


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
