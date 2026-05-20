"""
arifosmcp/runtime/a_rif/anomalous_contrast.py — Anomaly Detection
═════════════════════════════════════════════════════════════════

Anomalous contrast should trigger investigation, not belief.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from arifosmcp.runtime.a_rif.engine import detect_anomalous_contrast

__all__ = ["detect_anomalous_contrast", "route_from_contrast"]

CONTRAST_THRESHOLD = 0.65


def route_from_contrast(new_claims: list[str], background_claims: list[str]) -> dict:
    """Route a claim based on its anomalous contrast against background."""
    score = detect_anomalous_contrast(new_claims, background_claims)

    if score > CONTRAST_THRESHOLD:
        return {
            "route": "INVESTIGATE",
            "contrast_score": score,
            "reason": "High anomalous contrast — verify before accepting",
        }

    return {
        "route": "NORMAL",
        "contrast_score": score,
        "reason": "Contrast within expected bounds",
    }
