"""
ART reflex — the single precheck function.

CHECK 0 — STATE:   Which lifecycle phase is this tool in?
CHECK 1 — POWER:   What can this tool do to me?
CHECK 2 — TRUST:   Can I trust what this tool tells me?
CHECK 3 — SYSTEM:  Is the system healthy enough for this action?

One reflex. One function. One decision.

Extracted from runtime/art.py. The reflex gets lighter, not heavier.

DITEMPA BUKAN DIBERI — Reflex is forged, not configured.
"""

from __future__ import annotations
from dataclasses import dataclass

from arifosmcp.runtime.art.lifecycle import (
    SILENT_FALLBACK_HOLD_THRESHOLD,
    ToolState,
    suggest_transition,
)
from arifosmcp.runtime.art.verdict import ArtReason, ArtVerdict


# ── REQUEST ──────────────────────────────────────────────────────────


@dataclass
class ArtRequest:
    """Minimum signal ART needs to decide.

    Attributes:
        action_class:   "observe" | "mutate" | "execute"
        tool_state:     lifecycle phase of this tool (default: untrusted)
        blast_radius:   "low" | "medium" | "high" | "unknown"
        trust_level:    "evidence" | "verdict" | "unknown"
        actor_resolved: registered with AAA?
        schema_locked:  schema matches expected contract?
        degraded:       any system component down?
        reversible:     can this action be undone?
        failure_rate:   recent failure rate [0.0-1.0]; >0.3 triggers fallback
        drift_count:    schema/permission changes detected; >=3 triggers fallback
        days_since_use: days since last successful call; >90 triggers abandon
    """
    action_class: str = "observe"
    tool_state: str = ToolState.UNTRUSTED.value
    blast_radius: str = "unknown"
    trust_level: str = "unknown"
    actor_resolved: bool = False
    schema_locked: bool = False
    degraded: bool = False
    reversible: bool = False
    failure_rate: float = 0.0
    drift_count: int = 0
    days_since_use: int = 0

    # v3.1 — Discovery Surface Hardening
    schema_source: str = "builtin"
    schema_verified: bool = True
    external_surface: bool = False
    acknowledged_remote: bool = False
    silent_fallback_count: int = 0


# ── RESULT ───────────────────────────────────────────────────────────


@dataclass
class ArtResult:
    """What ART returns."""
    verdict: ArtVerdict
    reason: ArtReason
    next_tool_state: ToolState | None = None
    check_blocked: int = 0  # 0 = state gate, 1 = power, 2 = trust, 3 = system

    # ART 2.0 predictive fields (optional — populated by art_predict layer)
    trust_score: float | None = None
    trust_band: str | None = None
    blast_weight: float | None = None
    failure_risk: str | None = None
    recommended_pattern: str | None = None

    def __bool__(self) -> bool:
        return self.verdict == ArtVerdict.PROCEED


# ═══════════════════════════════════════════════════════════════════════
# THE REFLEX — ONE FUNCTION. ONE CALL. ONE DECISION.
# ═══════════════════════════════════════════════════════════════════════


def art(request: ArtRequest) -> ArtResult:
    """Agentic Recursive Tooling — the single reflex.

    Returns ArtResult with verdict (proceed/hold/block/observe_only),
    reason, suggested next state, and which check blocked.
    """

    current_state = ToolState(request.tool_state)
    next_state, transition_reason = suggest_transition(
        current_state=request.tool_state,
        action_class=request.action_class,
        failure_rate=request.failure_rate,
        schema_locked=request.schema_locked,
        degraded=request.degraded,
        drift_count=request.drift_count,
        days_since_use=request.days_since_use,
    )

    # ── CHECK 0: STATE GATES ─────────────────────────────────────────

    # ABANDONED: cannot call
    if current_state == ToolState.ABANDONED:
        return ArtResult(
            verdict=ArtVerdict.BLOCK,
            reason=ArtReason.TOOL_ABANDONED,
            next_tool_state=ToolState.ABANDONED,
        )

    # FALLBACK: observe only
    if current_state == ToolState.FALLBACK:
        if request.action_class != "observe":
            return ArtResult(
                verdict=ArtVerdict.HOLD,
                reason=ArtReason.TOOL_FALLBACK,
                next_tool_state=ToolState.FALLBACK,
            )
        return ArtResult(
            verdict=ArtVerdict.PROCEED,
            reason=ArtReason.ALL_CHECKS_PASSED,
            next_tool_state=next_state if next_state != current_state else None,
        )

    # UNTRUSTED: observe only
    if current_state == ToolState.UNTRUSTED and request.action_class not in ("observe",):
        return ArtResult(
            verdict=ArtVerdict.DEFAULT_OBSERVE,
            reason=ArtReason.TOOL_UNTRUSTED,
            next_tool_state=next_state if next_state != current_state else None,
        )

    # OBSERVED: observe + propose only (no execute, no direct mutate)
    if current_state == ToolState.OBSERVED:
        if request.action_class == "execute":
            return ArtResult(
                verdict=ArtVerdict.DEFAULT_OBSERVE,
                reason=ArtReason.TOOL_OBSERVED_EXECUTE,
            )
        if request.action_class == "mutate":
            return ArtResult(
                verdict=ArtVerdict.HOLD,
                reason=ArtReason.TOOL_OBSERVED_MUTATE,
            )

    # ── CHECK 1: POWER ───────────────────────────────────────────────

    if request.blast_radius == "unknown":
        return ArtResult(
            verdict=ArtVerdict.DEFAULT_OBSERVE,
            reason=ArtReason.BLAST_RADIUS_UNKNOWN,
            next_tool_state=next_state if next_state != current_state else None,
            check_blocked=1,
        )

    if request.action_class in ("mutate", "execute") and not request.reversible:
        return ArtResult(
            verdict=ArtVerdict.HOLD,
            reason=ArtReason.IRREVERSIBLE_NO_ROLLBACK,
            next_tool_state=next_state if next_state != current_state else None,
            check_blocked=1,
        )

    if request.action_class == "execute":
        return ArtResult(
            verdict=ArtVerdict.HOLD,
            reason=ArtReason.EXECUTE_NEEDS_ACK,
            next_tool_state=next_state if next_state != current_state else None,
            check_blocked=1,
        )

    # v3.1 — E2: EXTERNAL_SURFACE requires explicit ack
    if (request.action_class == "mutate"
            and request.external_surface
            and not request.acknowledged_remote):
        return ArtResult(
            verdict=ArtVerdict.HOLD,
            reason=ArtReason.EXTERNAL_SURFACE_UNACKNOWLEDGED,
            next_tool_state=next_state if next_state != current_state else None,
            check_blocked=1,
        )

    # ── CHECK 2: TRUST ───────────────────────────────────────────────

    if request.action_class != "observe" and not request.actor_resolved:
        return ArtResult(
            verdict=ArtVerdict.BLOCK,
            reason=ArtReason.ACTOR_UNRESOLVED,
            next_tool_state=next_state if next_state != current_state else None,
            check_blocked=2,
        )

    if request.trust_level == "unknown":
        return ArtResult(
            verdict=ArtVerdict.DEFAULT_OBSERVE,
            reason=ArtReason.TRUST_LEVEL_UNKNOWN,
            next_tool_state=next_state if next_state != current_state else None,
            check_blocked=2,
        )

    if request.trust_level == "verdict" and not request.schema_locked:
        return ArtResult(
            verdict=ArtVerdict.HOLD,
            reason=ArtReason.VERDICT_WITHOUT_SCHEMA,
            next_tool_state=next_state if next_state != current_state else None,
            check_blocked=2,
        )

    # v3.1 — E1: UNVERIFIED_SCHEMA downgrade for non-observe actions
    if (not request.schema_verified
            and request.action_class in ("mutate", "execute")):
        return ArtResult(
            verdict=ArtVerdict.DEFAULT_OBSERVE,
            reason=ArtReason.UNVERIFIED_SCHEMA_SOURCE,
            next_tool_state=next_state if next_state != current_state else None,
            check_blocked=2,
        )

    # ── CHECK 3: SYSTEM ──────────────────────────────────────────────

    if request.degraded and request.action_class in ("mutate", "execute"):
        return ArtResult(
            verdict=ArtVerdict.HOLD,
            reason=ArtReason.DEGRADED_MUTATION,
            next_tool_state=ToolState.FALLBACK,
            check_blocked=3,
        )

    # v3.1 — E3: CUMULATIVE_SILENT_FALLBACK detector
    if request.silent_fallback_count >= SILENT_FALLBACK_HOLD_THRESHOLD:
        return ArtResult(
            verdict=ArtVerdict.HOLD,
            reason=ArtReason.CUMULATIVE_SILENT_FALLBACK,
            next_tool_state=ToolState.FALLBACK,
            check_blocked=3,
        )

    # ── ALL CHECKS PASSED ────────────────────────────────────────────
    return ArtResult(
        verdict=ArtVerdict.PROCEED,
        reason=ArtReason.ALL_CHECKS_PASSED,
        next_tool_state=next_state if next_state != current_state else None,
        check_blocked=0,
    )
