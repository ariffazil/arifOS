"""
Budget Enforcement Schema — arifOS Federation
═══════════════════════════════════════════════

P0.5 from the 2026-06-09 readiness audit:
"Session cumulative budget must be embedded. Execution budget, tool budget,
entropy budget, retry budget, and external side-effect budget need enforcement."

This schema defines the canonical budget model that EVERY session and tool call
must respect. Without it, agentic autonomy can sprawl without bounds.

DITEMPA BUKAN DIBERI — Budget is the nervous system of governed agency.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class BudgetDomain(StrEnum):
    """Budget dimensions that constrain agentic action."""

    ENTROPY = "entropy"  # ΔS — disorder introduced
    TOKEN = "token"  # LLM token consumption
    EXECUTION = "execution"  # Tool calls, mutations, deploys
    RETRY = "retry"  # Consecutive failures
    SIDE_EFFECT = "side_effect"  # External API calls, emails, deployments
    WALL_CLOCK = "wall_clock"  # Session duration
    BLAST_RADIUS = "blast_radius"  # Scope of potential damage


class BudgetState(StrEnum):
    """Current state of a budget dimension."""

    ABUNDANT = "ABUNDANT"  # >50% remaining
    ADEQUATE = "ADEQUATE"  # 25-50% remaining
    CONSTRAINED = "CONSTRAINED"  # 10-25% remaining
    CRITICAL = "CRITICAL"  # <10% remaining
    EXHAUSTED = "EXHAUSTED"  # 0 remaining — HOLD


@dataclass
class BudgetLimit:
    """A single budget dimension with current and max values."""

    domain: BudgetDomain
    max_value: float
    current_value: float = 0.0
    warn_at: float = 0.75  # fraction of max — warn
    hold_at: float = 0.90  # fraction of max — HOLD
    void_at: float = 1.0  # fraction of max — VOID (exhausted)

    @property
    def remaining(self) -> float:
        return max(0.0, self.max_value - self.current_value)

    @property
    def fraction_used(self) -> float:
        if self.max_value <= 0:
            return 1.0
        return min(1.0, self.current_value / self.max_value)

    @property
    def state(self) -> BudgetState:
        f = self.fraction_used
        if f >= self.void_at:
            return BudgetState.EXHAUSTED
        if f >= self.hold_at:
            return BudgetState.CRITICAL
        if f >= self.warn_at:
            return BudgetState.CONSTRAINED
        if f >= 0.5:
            return BudgetState.ADEQUATE
        return BudgetState.ABUNDANT


# ── Canonical Session Budget ──
# These are the DEFAULT limits for a sovereign session.
# Individual tool calls may have tighter per-call limits.

CANONICAL_SESSION_BUDGET: dict[BudgetDomain, BudgetLimit] = {
    BudgetDomain.ENTROPY: BudgetLimit(
        domain=BudgetDomain.ENTROPY,
        max_value=1.0,  # ΔS max for session (thermodynamic)
        warn_at=0.50,
        hold_at=0.75,
        void_at=0.95,
    ),
    BudgetDomain.TOKEN: BudgetLimit(
        domain=BudgetDomain.TOKEN,
        max_value=500_000,  # Max tokens per session
        warn_at=0.70,
        hold_at=0.85,
        void_at=0.95,
    ),
    BudgetDomain.EXECUTION: BudgetLimit(
        domain=BudgetDomain.EXECUTION,
        max_value=100,  # Max tool calls per session
        warn_at=0.70,
        hold_at=0.85,
        void_at=0.95,
    ),
    BudgetDomain.RETRY: BudgetLimit(
        domain=BudgetDomain.RETRY,
        max_value=10,  # Max consecutive retries
        warn_at=0.50,
        hold_at=0.70,
        void_at=0.90,
    ),
    BudgetDomain.SIDE_EFFECT: BudgetLimit(
        domain=BudgetDomain.SIDE_EFFECT,
        max_value=5,  # Max external side-effects
        warn_at=0.50,
        hold_at=0.75,
        void_at=0.90,
    ),
    BudgetDomain.WALL_CLOCK: BudgetLimit(
        domain=BudgetDomain.WALL_CLOCK,
        max_value=3600,  # 1 hour session max
        warn_at=0.70,
        hold_at=0.85,
        void_at=0.95,
    ),
    BudgetDomain.BLAST_RADIUS: BudgetLimit(
        domain=BudgetDomain.BLAST_RADIUS,
        max_value=3,  # Max blast radius score (1-10 scale, 3=conservative)
        warn_at=0.50,
        hold_at=0.70,
        void_at=0.85,
    ),
}


def check_budget(
    budgets: dict[BudgetDomain, BudgetLimit],
    domain: BudgetDomain,
    cost: float,
) -> tuple[bool, str]:
    """Check if a proposed cost can fit within the budget.

    Returns (allowed, reason).
    """
    limit = budgets.get(domain)
    if limit is None:
        return True, f"no budget defined for {domain.value}"

    limit.current_value += cost
    state = limit.state

    if state == BudgetState.EXHAUSTED:
        return False, (
            f"BUDGET EXHAUSTED: {domain.value} at {limit.fraction_used:.0%} "
            f"({limit.current_value:.0f}/{limit.max_value:.0f})"
        )
    if state == BudgetState.CRITICAL:
        # Allow but warn — the caller should HOLD before the next call
        return True, (
            f"BUDGET CRITICAL: {domain.value} at {limit.fraction_used:.0%} "
            f"— only {limit.remaining:.0f} remaining"
        )

    return True, "ok"
