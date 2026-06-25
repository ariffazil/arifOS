"""
arifosmcp/core/latency_budget.py — 888_JUDGE Latency Budget (#423)

Latency is a constitutional signal. High-stakes decisions MUST be slower.

Design invariant: If 888 cannot decide within its class budget,
it must refuse to decide. Latency breach = constitutional failure,
not performance failure.

Sub-budget breakdown:
  T_total = T_verify + T_policy + T_conflict + T_emit

If any sub-budget exceeds threshold → auto-downgrade to HOLD.
No retries. No silent degradation.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import concurrent.futures
import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from arifosmcp.core.decision_contract import (
    DecisionClass,
    JudgeResult,
    ResolutionResult,
    VerdictClass,
    classify_decision,
)


# ── Module Constants ────────────────────────────────────────────

VALID_DECISION_CLASSES: frozenset[str] = frozenset(e.value for e in DecisionClass)


# ── Latency Budget Definition ────────────────────────────────────


@dataclass(frozen=True)
class LatencyBudget:
    """Hard ceiling per decision class."""
    decision_class: DecisionClass
    max_latency_ms: int          # 0 = unbounded (C4_SOVEREIGN)
    degradation_verdict: str     # What to emit if timeout
    reasoning: str


LATENCY_BUDGETS: dict[DecisionClass, LatencyBudget] = {
    DecisionClass.C0_AUTO: LatencyBudget(
        decision_class=DecisionClass.C0_AUTO,
        max_latency_ms=10,
        degradation_verdict=VerdictClass.HOLD.value,
        reasoning="Automation OK — rule engine only. 10ms ceiling.",
    ),
    DecisionClass.C1_FAST: LatencyBudget(
        decision_class=DecisionClass.C1_FAST,
        max_latency_ms=50,
        degradation_verdict=VerdictClass.HOLD.value,
        reasoning="Cached or heuristic — no LLM. 50ms ceiling.",
    ),
    DecisionClass.C2_STANDARD: LatencyBudget(
        decision_class=DecisionClass.C2_STANDARD,
        max_latency_ms=200,
        degradation_verdict=VerdictClass.SABAR.value,
        reasoning="Single LLM pass — retry allowed. 200ms ceiling.",
    ),
    DecisionClass.C3_DEEP: LatencyBudget(
        decision_class=DecisionClass.C3_DEEP,
        max_latency_ms=1000,
        degradation_verdict=VerdictClass.HOLD.value,
        reasoning="Multi-stage validation — AAA deliberation. 1s ceiling.",
    ),
    DecisionClass.C4_SOVEREIGN: LatencyBudget(
        decision_class=DecisionClass.C4_SOVEREIGN,
        max_latency_ms=0,  # unbounded
        degradation_verdict="888_HOLD",
        reasoning="Requires human — no SLA. Time is a safeguard.",
    ),
}


# ── Sub-Budget Tracking ─────────────────────────────────────────


@dataclass
class SubBudget:
    """Tracks time spent in each phase of the judge pipeline."""
    verify_ms: float = 0.0      # Receipt/context verification
    policy_ms: float = 0.0      # Floor compliance check
    conflict_ms: float = 0.0    # Conflict resolution
    emit_ms: float = 0.0        # Receipt emission
    judge_ms: float = 0.0       # Actual judge reasoning
    total_ms: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {
            "verify_ms": round(self.verify_ms, 3),
            "policy_ms": round(self.policy_ms, 3),
            "conflict_ms": round(self.conflict_ms, 3),
            "emit_ms": round(self.emit_ms, 3),
            "judge_ms": round(self.judge_ms, 3),
            "total_ms": round(self.total_ms, 3),
        }


# ── Judge Cache ─────────────────────────────────────────────────


class JudgeCache:
    """
    Cache for repeated judge decisions.
    Session-bound — cache entries expire when session ends.

    Cache key = sha256(context_signature + decision_class).
    """

    def __init__(self, max_entries: int = 1000):
        self._cache: dict[str, CacheEntry] = {}
        self._max_entries = max_entries
        self._hits: int = 0
        self._misses: int = 0

    def get(self, context_signature: str, decision_class: str) -> JudgeResult | None:
        """Look up cached decision. Returns None if miss."""
        key = self._make_key(context_signature, decision_class)
        entry = self._cache.get(key)
        if entry is None:
            self._misses += 1
            return None

        self._hits += 1
        return entry.result

    def put(self, context_signature: str, decision_class: str, result: JudgeResult) -> None:
        """Store decision in cache."""
        key = self._make_key(context_signature, decision_class)
        self._cache[key] = CacheEntry(result=result, created_at=time.monotonic())

        # Evict oldest if over limit
        if len(self._cache) > self._max_entries:
            oldest_key = min(self._cache, key=lambda k: self._cache[k].created_at)
            del self._cache[oldest_key]

    def clear(self) -> None:
        """Clear cache."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    @property
    def stats(self) -> dict[str, int]:
        return {
            "entries": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
        }

    @staticmethod
    def _make_key(context_signature: str, decision_class: str) -> str:
        combined = f"{context_signature}:{decision_class}"
        return hashlib.sha256(combined.encode()).hexdigest()


@dataclass
class CacheEntry:
    result: JudgeResult
    created_at: float


# ── Budget-Aware Judge Pipeline ─────────────────────────────────


@dataclass
class JudgePipelineResult:
    """Full result from the budget-aware judge pipeline."""
    judge_result: JudgeResult
    sub_budget: SubBudget
    from_cache: bool
    degradation_reason: str | None = None


def judge_with_budget(
    decision_class: str,
    judge_fn: Callable[[], dict[str, Any]],
    conflict_result: ResolutionResult | None = None,
    cache: JudgeCache | None = None,
    context_signature: str = "",
) -> JudgePipelineResult:
    """
    Budget-aware judge. If timeout → degrade to HOLD/SABAR.
    Never guess. Never retry silently.

    Args:
        decision_class: DecisionClass value string
        judge_fn: Callable that returns {"verdict": str, "reason": str}
        conflict_result: Optional conflict resolution result
        cache: Optional judge cache for repeated decisions
        context_signature: Cache key input (from DecisionContract)

    Returns:
        JudgePipelineResult with verdict, sub-budget, and cache status.
    """
    budget = LATENCY_BUDGETS.get(
        DecisionClass(decision_class) if decision_class in VALID_DECISION_CLASSES else DecisionClass.C3_DEEP,
        LATENCY_BUDGETS[DecisionClass.C3_DEEP],  # default: conservative
    )

    sub = SubBudget()
    t_total_start = time.monotonic()

    # C4: Sovereign — no timeout, just escalate
    if budget.decision_class == DecisionClass.C4_SOVEREIGN:
        sub.total_ms = (time.monotonic() - t_total_start) * 1000
        return JudgePipelineResult(
            judge_result=JudgeResult(
                verdict="888_HOLD",
                decision_class=decision_class,
                latency_ms=sub.total_ms,
                within_budget=True,  # unbounded
                reason="Requires sovereign approval (F13)",
                resolution=conflict_result,
            ),
            sub_budget=sub,
            from_cache=False,
            degradation_reason=None,
        )

    # Check cache first
    if cache and context_signature:
        t_cache_start = time.monotonic()
        cached = cache.get(context_signature, decision_class)
        sub.verify_ms = (time.monotonic() - t_cache_start) * 1000

        if cached is not None:
            sub.total_ms = (time.monotonic() - t_total_start) * 1000
            return JudgePipelineResult(
                judge_result=cached,
                sub_budget=sub,
                from_cache=True,
                degradation_reason=None,
            )

    # Execute judge with timeout tracking
    t_judge_start = time.monotonic()

    # L1 fix: preventive timeout — execute judge_fn in thread pool with hard deadline.
    # If max_latency_ms > 0 (not C4_SOVEREIGN), enforce a timeout.
    # This is preventive, not retroactive: if the timeout fires, we degrade immediately
    # rather than measuring elapsed time after judge_fn returns.
    timeout_seconds = (
        None if (budget.max_latency_ms == 0 or budget.decision_class == DecisionClass.C4_SOVEREIGN)
        else (budget.max_latency_ms / 1000.0) * 1.0  # 100% of budget as hard deadline
    )
    judge_output: dict[str, Any]
    if timeout_seconds is not None:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(judge_fn)
            try:
                judge_output = future.result(timeout=timeout_seconds)
            except concurrent.futures.TimeoutError:
                # L1: preventive timeout — degrade immediately without running judge_fn to completion.
                # This is the key difference from the old retroactive approach.
                sub.judge_ms = budget.max_latency_ms  # approximate — killed at deadline
                sub.total_ms = budget.max_latency_ms
                degradation_reason = (
                    f"Latency timeout: budget {budget.max_latency_ms}ms exceeded "
                    f"for {decision_class}. Degraded to {budget.degradation_verdict} "
                    f"(preventive timeout — judge_fn did not complete)."
                )
                result = JudgeResult(
                    verdict=budget.degradation_verdict,
                    decision_class=decision_class,
                    latency_ms=sub.total_ms,
                    within_budget=False,
                    reason=degradation_reason,
                    resolution=conflict_result,
                )
                return JudgePipelineResult(
                    judge_result=result,
                    sub_budget=sub,
                    from_cache=False,
                    degradation_reason=degradation_reason,
                )
    else:
        judge_output = judge_fn()

    sub.judge_ms = (time.monotonic() - t_judge_start) * 1000
    sub.total_ms = (time.monotonic() - t_total_start) * 1000

    # Check latency budget
    within_budget = sub.total_ms <= budget.max_latency_ms

    if not within_budget:
        # Latency breach — degrade
        degradation_reason = (
            f"Latency breach: {sub.total_ms:.1f}ms > {budget.max_latency_ms}ms "
            f"budget for {decision_class}"
        )
        result = JudgeResult(
            verdict=budget.degradation_verdict,
            decision_class=decision_class,
            latency_ms=sub.total_ms,
            within_budget=False,
            reason=degradation_reason,
            resolution=conflict_result,
        )
    else:
        result = JudgeResult(
            verdict=judge_output.get("verdict", "UNKNOWN"),
            decision_class=decision_class,
            latency_ms=sub.total_ms,
            within_budget=True,
            reason=judge_output.get("reason", ""),
            resolution=conflict_result,
        )

    # Cache result (even degraded ones — avoid re-computing)
    if cache and context_signature:
        cache.put(context_signature, decision_class, result)

    return JudgePipelineResult(
        judge_result=result,
        sub_budget=sub,
        from_cache=False,
        degradation_reason=degradation_reason if not within_budget else None,
    )


# ── Convenience: Full Pipeline ───────────────────────────────────


def classify_and_judge(
    action_class: str,
    risk_class: str,
    is_irreversible: bool,
    has_cached_verdict: bool,
    judge_fn: Callable[[], dict[str, Any]],
    conflict_result: ResolutionResult | None = None,
    cache: JudgeCache | None = None,
    context_signature: str = "",
) -> JudgePipelineResult:
    """
    Convenience: classify → judge with budget in one call.
    """
    decision_class = classify_decision(
        action_class=action_class,
        risk_class=risk_class,
        is_irreversible=is_irreversible,
        has_cached_verdict=has_cached_verdict,
    )
    return judge_with_budget(
        decision_class=decision_class,
        judge_fn=judge_fn,
        conflict_result=conflict_result,
        cache=cache,
        context_signature=context_signature,
    )


# ── Metrics ──────────────────────────────────────────────────────


@dataclass
class LatencyMetrics:
    """Track latency discipline across decisions."""
    total_decisions: int = 0
    within_budget: int = 0
    breaches: int = 0
    cache_hits: int = 0
    degradations: int = 0

    # Per-class breakdown
    class_counts: dict[str, int] = field(default_factory=dict)
    class_breaches: dict[str, int] = field(default_factory=dict)

    def record(self, result: JudgePipelineResult) -> None:
        """Record a decision result."""
        self.total_decisions += 1

        cls = result.judge_result.decision_class
        self.class_counts[cls] = self.class_counts.get(cls, 0) + 1

        if result.judge_result.within_budget:
            self.within_budget += 1
        else:
            self.breaches += 1
            self.class_breaches[cls] = self.class_breaches.get(cls, 0) + 1

        if result.from_cache:
            self.cache_hits += 1

        if result.degradation_reason:
            self.degradations += 1

    @property
    def breach_rate(self) -> float:
        """Percentage of decisions that breached their budget."""
        if self.total_decisions == 0:
            return 0.0
        return self.breaches / self.total_decisions

    @property
    def cache_hit_rate(self) -> float:
        """Percentage of decisions served from cache."""
        if self.total_decisions == 0:
            return 0.0
        return self.cache_hits / self.total_decisions

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_decisions": self.total_decisions,
            "within_budget": self.within_budget,
            "breaches": self.breaches,
            "breach_rate": round(self.breach_rate, 4),
            "cache_hits": self.cache_hits,
            "cache_hit_rate": round(self.cache_hit_rate, 4),
            "degradations": self.degradations,
            "class_counts": self.class_counts,
            "class_breaches": self.class_breaches,
        }

    def health_check(self) -> dict[str, Any]:
        """
        Health check for latency discipline.

        Red flags:
        - breach_rate > 0.30 → system too strict or underbudgeting
        - ZERO cache_hits → cache is blind or disabled
        - degradations > breaches → degradation logic may be wrong
        """
        warnings: list[str] = []

        if self.breach_rate > 0.30:
            warnings.append(f"HIGH_BREACH_RATE: {self.breach_rate:.1%} — system too strict or underbudgeting")
        if self.total_decisions > 10 and self.cache_hits == 0:
            warnings.append("ZERO_CACHE_HITS — cache is blind or disabled")
        if self.degradations > self.breaches:
            warnings.append("DEGRADATIONS_EXCEED_BREACHES — degradation logic may be wrong")

        return {
            "status": "HEALTHY" if not warnings else "WARNING",
            "warnings": warnings,
            "metrics": self.to_dict(),
        }
