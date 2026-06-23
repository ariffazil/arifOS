"""
ART lifecycle — tool state machine and transition logic.

Extracted from runtime/art.py to keep the reflex under its 500-line
weight ceiling. This module holds the ToolState enum, state transition
function, and cross-domain lifecycle insight.

DITEMPA BUKAN DIBERI — Lifecycle is forged, not configured.
"""

from __future__ import annotations
from enum import StrEnum


# ═══════════════════════════════════════════════════════════════════════
# v3.1 — DISCOVERY SURFACE HARDENING
# ═══════════════════════════════════════════════════════════════════════
SILENT_FALLBACK_HOLD_THRESHOLD: int = 2


class ToolState(StrEnum):
    """Four tool states — the lifecycle of any tool in an agent's world.

    UNTRUSTED — New tool. Never used. Schema unknown. (Heidegger: present-at-hand)
        Allowed: observe only.
        Transition to OBSERVED: first successful observe.

    OBSERVED — Tool probed, schema known, reliability unproven. (Piaget: assimilation)
        Allowed: observe + propose only.
        Transition to TRUSTED: low failure rate (<10%), schema locked.

    TRUSTED — Tool reliable, schema locked, low failure. (Heidegger: ready-to-hand)
        Allowed: observe + mutate + execute (with gates).
        Transition to FALLBACK: failure >30% OR drift >=3 OR degraded.

    FALLBACK — Tool broken, drifting, failing. (Heidegger: unready-to-hand)
        Allowed: observe only.
        Transition to TRUSTED: recovered (failure <5%, schema locked).
        Transition to ABANDONED: catastrophic (failure >50% + drift >=5).

    ABANDONED — Tool removed from active set.
        Allowed: block all.
    """

    UNTRUSTED = "untrusted"
    OBSERVED = "observed"
    TRUSTED = "trusted"
    FALLBACK = "fallback"
    ABANDONED = "abandoned"


def suggest_transition(
    current_state: str,
    action_class: str,
    failure_rate: float,
    schema_locked: bool,
    degraded: bool,
    drift_count: int,
    days_since_use: int,
) -> tuple[ToolState, "ArtReason | None"]:  # type: ignore[name-defined]  # noqa: F821
    """Suggest next tool state based on usage signals.

    Implicitly encodes the 8-phase agentic loop:
      Mapping      → UNTRUSTED (tool just discovered)
      Exploration  → UNTRUSTED observe → OBSERVED
      Forging      → OBSERVED + reliable → TRUSTED
      Production   → TRUSTED (active use under gates)
      Testing      → TRUSTED → FALLBACK (failure/drift detected)
      Optimization → signals that prevent unnecessary transitions
      Abandonment  → FALLBACK terminal OR stale → ABANDONED
      Fallback     → FALLBACK recovered → TRUSTED
    """
    # Import here to avoid circular dependency at module level
    from arifosmcp.runtime.art.verdict import ArtReason

    current = ToolState(current_state)

    # UNTRUSTED → OBSERVED: first successful observe
    if current == ToolState.UNTRUSTED and action_class == "observe":
        return ToolState.OBSERVED, None

    # OBSERVED → TRUSTED: proven reliability
    if current == ToolState.OBSERVED and failure_rate < 0.1 and schema_locked:
        return ToolState.TRUSTED, None

    # TRUSTED → FALLBACK: failure, drift, or degradation
    if current == ToolState.TRUSTED:
        if failure_rate > 0.3:
            return ToolState.FALLBACK, ArtReason.FAILURE_RATE_HIGH
        if drift_count >= 3:
            return ToolState.FALLBACK, ArtReason.DRIFT_DETECTED
        if degraded:
            return ToolState.FALLBACK, ArtReason.DEGRADED_MUTATION

    # FALLBACK → TRUSTED: recovered
    if current == ToolState.FALLBACK and failure_rate < 0.05 and schema_locked and not degraded:
        return ToolState.TRUSTED, None

    # FALLBACK → ABANDONED: unrecoverable
    if current == ToolState.FALLBACK and failure_rate > 0.5 and drift_count >= 5:
        return ToolState.ABANDONED, None

    # Any → ABANDONED: stale
    if current not in (ToolState.ABANDONED, ToolState.UNTRUSTED) and days_since_use > 90:
        return ToolState.ABANDONED, ArtReason.TOOL_STALE

    return current, None
