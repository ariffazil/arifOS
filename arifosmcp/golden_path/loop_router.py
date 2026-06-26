"""
arifOS Golden Path — Loop Router
═════════════════════════════════

Stage routing + metabolic termination for the 7-organ golden path.

Reads current session state. Determines next organ based on verdict
and readiness. Enforces metabolic ceiling. Returns routing decision.

DITEMPA BUKAN DIBERI 🔥⚒️
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .session_state import SessionState, Verdict, Readiness


class RouteAction(str, Enum):
    """What the router decides to do."""
    ADVANCE = "ADVANCE"             # Move to next organ
    RETURN_TO_333 = "RETURN_TO_333" # SABAR: go back to REASON
    RETURN_TO_111 = "RETURN_TO_111" # Critique says re-observe
    ESCALATE_SOVEREIGN = "ESCALATE_SOVEREIGN"  # HOLD: needs Arif
    TERMINATE_VOID = "TERMINATE_VOID"          # VOID: session ends
    TERMINATE_SEAL = "TERMINATE_SEAL"          # Sealed: session complete
    FORCE_HOLD = "FORCE_HOLD"      # Metabolic exhaustion


@dataclass
class RoutingDecision:
    """The router's decision on what happens next."""
    action: RouteAction
    current_stage: str
    next_stage: str | None
    reason: str
    revision_cycle: int
    loop_count: int
    metabolic_budget: int


# ── The canonical golden path order ──────────────────────────────────────────
# 2026-06-26 RSI fix: critique (555) before judge (666).
# Matches Golden Path doctrine: 000→111→333→555→666→777→999

GOLDEN_PATH = ["000", "111", "333", "555", "666", "777", "999"]


def _next_stage(current: str) -> str | None:
    """Get the next stage in the golden path."""
    try:
        idx = GOLDEN_PATH.index(current)
        if idx + 1 < len(GOLDEN_PATH):
            return GOLDEN_PATH[idx + 1]
    except ValueError:
        pass
    return None


def route(state: SessionState) -> RoutingDecision:
    """Determine the next routing decision based on current session state.

    This is the brain of the loop. It reads:
      - current_verdict (from 666_JUDGE)
      - current_readiness (from 555_CRITIQUE)
      - loop_count (metabolic budget)
      - revision_cycle (how many times we've looped)

    And decides:
      - ADVANCE to next organ
      - RETURN to 333 (after SABAR from 666_JUDGE)
      - ESCALATE to sovereign (after HOLD)
      - TERMINATE (after VOID or SEAL)
      - FORCE HOLD (metabolic exhaustion)
    """
    current = state.current_stage

    # ── Metabolic exhaustion check ──────────────────────────────────────
    if state.is_metabolically_exhausted():
        return RoutingDecision(
            action=RouteAction.FORCE_HOLD,
            current_stage=current,
            next_stage=None,
            reason=(
                f"METABOLIC CEILING: pipeline has looped {state.loop_count} times "
                f"(max={state.max_loops}) without convergence. "
                f"The forge has exhausted its budget. "
                f"Escalating to sovereign (F13). Human judgment required."
            ),
            revision_cycle=state.revision_cycle,
            loop_count=state.loop_count,
            metabolic_budget=0,
        )

    # ── VOID terminates permanently ─────────────────────────────────────
    if state.current_verdict == Verdict.VOID:
        return RoutingDecision(
            action=RouteAction.TERMINATE_VOID,
            current_stage=current,
            next_stage=None,
            reason=(
                "VOID verdict: this change CANNOT proceed. Ever. "
                "Session terminates. Recording to VAULT999 if significant."
            ),
            revision_cycle=state.revision_cycle,
            loop_count=state.loop_count,
            metabolic_budget=state.get_metabolic_budget_remaining(),
        )

    # ── HOLD escalates to sovereign ─────────────────────────────────────
    if state.current_verdict == Verdict.HOLD:
        return RoutingDecision(
            action=RouteAction.ESCALATE_SOVEREIGN,
            current_stage=current,
            next_stage=None,
            reason=(
                "HOLD verdict: floor violation requires L13 SOVEREIGN. "
                "Cannot resolve at constitutional level. "
                "Pausing for human judgment."
            ),
            revision_cycle=state.revision_cycle,
            loop_count=state.loop_count,
            metabolic_budget=state.get_metabolic_budget_remaining(),
        )

    # ── SABAR returns to 333 with context ───────────────────────────────
    if state.current_verdict == Verdict.SABAR and current == "666":
        return RoutingDecision(
            action=RouteAction.RETURN_TO_333,
            current_stage=current,
            next_stage="333",
            reason=(
                "SABAR verdict from 666_JUDGE: named floor failures must be addressed. "
                "Returning to 333_REASON with prior verdict context. "
                f"Revision cycle will become {state.revision_cycle + 1}."
            ),
            revision_cycle=state.revision_cycle + 1,
            loop_count=state.loop_count + 1,
            metabolic_budget=state.get_metabolic_budget_remaining() - 1,
        )

    # ── HOLD_FOR_REVIEW returns to 333 ──────────────────────────────────
    if state.current_readiness == Readiness.HOLD_FOR_REVIEW and current == "555":
        return RoutingDecision(
            action=RouteAction.RETURN_TO_333,
            current_stage=current,
            next_stage="333",
            reason=(
                "HOLD_FOR_REVIEW from 555_CRITIQUE: critique identified concerns. "
                "Returning to 333_REASON to address them. "
                f"Revision cycle will become {state.revision_cycle + 1}."
            ),
            revision_cycle=state.revision_cycle + 1,
            loop_count=state.loop_count + 1,
            metabolic_budget=state.get_metabolic_budget_remaining() - 1,
        )

    # ── BLOCK returns to 000 ────────────────────────────────────────────
    if state.current_readiness == Readiness.BLOCK and current == "555":
        return RoutingDecision(
            action=RouteAction.RETURN_TO_333,
            current_stage=current,
            next_stage="000",
            reason=(
                "BLOCK from 555_CRITIQUE: irreversible harm or dignity violation detected. "
                "Returning to 000_INIT. The forge must re-frame from the anchor."
            ),
            revision_cycle=state.revision_cycle + 1,
            loop_count=state.loop_count + 1,
            metabolic_budget=state.get_metabolic_budget_remaining() - 1,
        )

    # ── SEAL at 999: session complete ───────────────────────────────────
    if current == "999" and state.sealed_at:
        return RoutingDecision(
            action=RouteAction.TERMINATE_SEAL,
            current_stage=current,
            next_stage=None,
            reason=(
                "SEAL complete. Session closed. "
                "Assumption ledger written to VAULT999. "
                "The seal is the end. And the seal is the beginning."
            ),
            revision_cycle=state.revision_cycle,
            loop_count=state.loop_count,
            metabolic_budget=state.get_metabolic_budget_remaining(),
        )

    # ── Default: advance to next stage ──────────────────────────────────
    nxt = _next_stage(current)
    if nxt:
        return RoutingDecision(
            action=RouteAction.ADVANCE,
            current_stage=current,
            next_stage=nxt,
            reason=f"Advancing from {current} to {nxt} along the golden path.",
            revision_cycle=state.revision_cycle,
            loop_count=state.loop_count,
            metabolic_budget=state.get_metabolic_budget_remaining(),
        )

    # ── Fallback: at the end without seal ───────────────────────────────
    return RoutingDecision(
        action=RouteAction.FORCE_HOLD,
        current_stage=current,
        next_stage=None,
        reason=(
            f"Unexpected state: at stage {current} with no routing rule. "
            f"Escalating to sovereign."
        ),
        revision_cycle=state.revision_cycle,
        loop_count=state.loop_count,
        metabolic_budget=state.get_metabolic_budget_remaining(),
    )


__all__ = [
    "RouteAction",
    "RoutingDecision",
    "GOLDEN_PATH",
    "route",
]
