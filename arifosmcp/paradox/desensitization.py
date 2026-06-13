"""
arifosmcp/paradox/desensitization.py — Unified Anchor Desensitization Detector

Prevents paradox anchors from becoming ornamental wallpaper.
When an anchor fires repeatedly without downstream state change,
its D_a score rises until it triggers a warning or is flagged as desensitized.

Formula: D_a = N_fires_without_state_change / (N_anchor_fires + ε)

Thresholds:
  D_a ≤ 0.5  → healthy (anchor is functioning as intended)
  D_a > 0.5  → warning (anchor may be wallpaper — review trigger thresholds)
  D_a > 0.7  → desensitized (anchor firing without effect — suppress until change)

One detector, shared across all 5 organs.
DITEMPA BUKAN DIBERI — Forged, Not Given
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

# ═══════════════════════════════════════════════════════════════════════════════
# THRESHOLDS — Golden constants
# ═══════════════════════════════════════════════════════════════════════════════

DESENSITIZATION_WARNING_THRESHOLD = 0.5
DESENSITIZATION_CRITICAL_THRESHOLD = 0.7
FIRE_LOG_MAX_ENTRIES = 20
FIRE_LOG_WINDOW = 10  # How many recent fires to count for "without change"


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL FIRE LOG — Shared across all organs
# ═══════════════════════════════════════════════════════════════════════════════

_ANCHOR_FIRE_LOG: dict[str, list[float]] = {}


def _get_fire_log(anchor_id: str) -> list[float]:
    """Get or create the fire log for an anchor."""
    if anchor_id not in _ANCHOR_FIRE_LOG:
        _ANCHOR_FIRE_LOG[anchor_id] = []
    return _ANCHOR_FIRE_LOG[anchor_id]


def _clear_fire_log(anchor_id: str | None = None) -> None:
    """Clear fire log for testing. If anchor_id is None, clear all."""
    if anchor_id is None:
        _ANCHOR_FIRE_LOG.clear()
    else:
        _ANCHOR_FIRE_LOG.pop(anchor_id, None)


# ═══════════════════════════════════════════════════════════════════════════════
# RESULT — Desensitization assessment
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class DesensitizationResult:
    """Result of a desensitization check on a paradox anchor."""
    anchor_id: str
    total_fires: int
    desensitization_score: float
    status: str  # healthy | warning | desensitized
    recommendation: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "anchor_id": self.anchor_id,
            "total_fires": self.total_fires,
            "desensitization_score": round(self.desensitization_score, 2),
            "status": self.status,
            "recommendation": self.recommendation,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# DETECTOR — Core D_a computation
# ═══════════════════════════════════════════════════════════════════════════════


def check_desensitization(
    anchor_id: str,
    state_changed: bool = True,
) -> DesensitizationResult:
    """
    Compute desensitization score D_a for a paradox anchor.

    D_a = N_fires_without_state_change / (N_fires + ε)

    If D_a > DESENSITIZATION_CRITICAL_THRESHOLD, the anchor is functioning
    as ornament, not control — paradox quotes must not become wallpaper.

    Args:
        anchor_id: The paradox anchor ID (e.g., "H_TxC", "R_HxC")
        state_changed: Whether downstream state actually changed

    Returns:
        DesensitizationResult with status and recommendation
    """
    now = time.time()
    log = _get_fire_log(anchor_id)
    log.append(now)

    # Cap the fire log
    if len(log) > FIRE_LOG_MAX_ENTRIES:
        _ANCHOR_FIRE_LOG[anchor_id] = log[-FIRE_LOG_MAX_ENTRIES:]

    total_fires = len(log)

    # Estimate fires without state change
    if not state_changed:
        fires_without_change = min(total_fires, FIRE_LOG_WINDOW)
    else:
        fires_without_change = max(0, total_fires // 3)

    epsilon = 0.01
    d_a = fires_without_change / (total_fires + epsilon)

    result = DesensitizationResult(
        anchor_id=anchor_id,
        total_fires=total_fires,
        desensitization_score=d_a,
        status="healthy",
        recommendation=None,
    )

    if d_a > DESENSITIZATION_CRITICAL_THRESHOLD:
        result.status = "desensitized"
        result.recommendation = (
            f"Anchor {anchor_id} firing {total_fires} times without state change. "
            "Paradox quote may be wallpaper. Review trigger thresholds or "
            "suppress until downstream behavior changes."
        )
    elif d_a > DESENSITIZATION_WARNING_THRESHOLD:
        result.status = "warning"
        result.recommendation = (
            f"Anchor {anchor_id} approaching desensitization (D_a={d_a:.2f}). "
            "Consider widening trigger gap or raising severity_on_fire."
        )

    return result
