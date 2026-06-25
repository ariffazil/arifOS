"""
tests/test_latency_budget.py — Tests for #423 Latency Budget

Test failure behavior first. DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import time

import pytest

from arifosmcp.core.decision_contract import (
    DecisionClass,
    JudgeResult,
    classify_decision,
)
from arifosmcp.core.latency_budget import (
    LATENCY_BUDGETS,
    JudgeCache,
    JudgePipelineResult,
    LatencyBudget,
    LatencyMetrics,
    classify_and_judge,
    judge_with_budget,
)


# ═══════════════════════════════════════════════════════════════════
# BUDGET DEFINITION
# ═══════════════════════════════════════════════════════════════════


class TestLatencyBudgets:
    """Test budget definitions."""

    def test_all_classes_have_budgets(self):
        """Every DecisionClass has a defined budget."""
        for cls in DecisionClass:
            assert cls in LATENCY_BUDGETS, f"Missing budget for {cls}"

    def test_c0_auto_is_fastest(self):
        """C0_AUTO has the tightest budget."""
        budgets = list(LATENCY_BUDGETS.values())
        min_budget = min(b.max_latency_ms for b in budgets if b.max_latency_ms > 0)
        assert LATENCY_BUDGETS[DecisionClass.C0_AUTO].max_latency_ms == min_budget

    def test_c4_sovereign_is_unbounded(self):
        """C4_SOVEREIGN has no latency limit (human loop)."""
        assert LATENCY_BUDGETS[DecisionClass.C4_SOVEREIGN].max_latency_ms == 0

    def test_budgets_are_ascending(self):
        """Budgets increase with decision complexity."""
        order = [
            DecisionClass.C0_AUTO,
            DecisionClass.C1_FAST,
            DecisionClass.C2_STANDARD,
            DecisionClass.C3_DEEP,
        ]
        for i in range(len(order) - 1):
            assert LATENCY_BUDGETS[order[i]].max_latency_ms < LATENCY_BUDGETS[order[i + 1]].max_latency_ms


# ═══════════════════════════════════════════════════════════════════
# JUDGE CACHE
# ═══════════════════════════════════════════════════════════════════


class TestJudgeCache:
    """Test the judge cache."""

    def test_cache_hit(self):
        """Cached decision is returned on second call."""
        cache = JudgeCache()
        result = JudgeResult(
            verdict="SEAL",
            decision_class="C2_STANDARD",
            latency_ms=50.0,
            within_budget=True,
            reason="test",
        )
        cache.put("sig-001", "C2_STANDARD", result)

        cached = cache.get("sig-001", "C2_STANDARD")
        assert cached is not None
        assert cached.verdict == "SEAL"

    def test_cache_miss(self):
        """Cache miss returns None."""
        cache = JudgeCache()
        assert cache.get("nonexistent", "C2_STANDARD") is None

    def test_cache_stats(self):
        """Cache tracks hits and misses."""
        cache = JudgeCache()
        cache.get("a", "C2_STANDARD")  # miss
        cache.put("a", "C2_STANDARD", JudgeResult(
            verdict="SEAL", decision_class="C2_STANDARD",
            latency_ms=0, within_budget=True, reason="",
        ))
        cache.get("a", "C2_STANDARD")  # hit

        stats = cache.stats
        assert stats["misses"] == 1
        assert stats["hits"] == 1
        assert stats["entries"] == 1

    def test_cache_eviction(self):
        """Cache evicts oldest when full."""
        cache = JudgeCache(max_entries=3)
        result = JudgeResult(
            verdict="SEAL", decision_class="C2_STANDARD",
            latency_ms=0, within_budget=True, reason="",
        )
        for i in range(5):
            cache.put(f"sig-{i}", "C2_STANDARD", result)

        assert cache.stats["entries"] == 3

    def test_cache_clear(self):
        """Clear empties cache."""
        cache = JudgeCache()
        cache.put("a", "C2_STANDARD", JudgeResult(
            verdict="SEAL", decision_class="C2_STANDARD",
            latency_ms=0, within_budget=True, reason="",
        ))
        cache.clear()
        assert cache.stats["entries"] == 0


# ═══════════════════════════════════════════════════════════════════
# JUDGE WITH BUDGET
# ═══════════════════════════════════════════════════════════════════


class TestJudgeWithBudget:
    """Test the budget-aware judge pipeline."""

    def test_within_budget(self):
        """Fast judge returns within budget."""
        def fast_judge():
            return {"verdict": "SEAL", "reason": "All floors pass"}

        result = judge_with_budget(
            decision_class=DecisionClass.C3_DEEP.value,
            judge_fn=fast_judge,
        )
        assert result.judge_result.verdict == "SEAL"
        assert result.judge_result.within_budget
        assert result.from_cache is False
        assert result.degradation_reason is None

    def test_latency_breach_degrades(self):
        """Judge that exceeds budget → degraded verdict."""
        def slow_judge():
            time.sleep(0.15)  # 150ms — exceeds C1_FAST (50ms)
            return {"verdict": "SEAL", "reason": "Too slow"}

        result = judge_with_budget(
            decision_class=DecisionClass.C1_FAST.value,
            judge_fn=slow_judge,
        )
        assert result.judge_result.verdict == "HOLD"  # C1 degrades to HOLD
        assert not result.judge_result.within_budget
        assert result.degradation_reason is not None
        assert "Latency breach" in result.degradation_reason

    def test_c2_degrades_to_sabar(self):
        """C2_STANDARD degrades to SABAR (retry allowed)."""
        def slow_judge():
            time.sleep(0.25)  # 250ms — exceeds C2_STANDARD (200ms)
            return {"verdict": "SEAL", "reason": "Too slow"}

        result = judge_with_budget(
            decision_class=DecisionClass.C2_STANDARD.value,
            judge_fn=slow_judge,
        )
        assert result.judge_result.verdict == "SABAR"

    def test_c4_sovereign_no_timeout(self):
        """C4_SOVEREIGN always returns 888_HOLD, no timeout."""
        def any_judge():
            return {"verdict": "SEAL", "reason": "Should not be called"}

        result = judge_with_budget(
            decision_class=DecisionClass.C4_SOVEREIGN.value,
            judge_fn=any_judge,
        )
        assert result.judge_result.verdict == "888_HOLD"
        assert result.judge_result.within_budget  # unbounded = always within

    def test_cache_integration(self):
        """Cached decisions are returned without calling judge_fn."""
        cache = JudgeCache()
        call_count = 0

        def counting_judge():
            nonlocal call_count
            call_count += 1
            return {"verdict": "SEAL", "reason": "test"}

        # First call — cache miss
        r1 = judge_with_budget(
            decision_class=DecisionClass.C2_STANDARD.value,
            judge_fn=counting_judge,
            cache=cache,
            context_signature="sig-001",
        )
        assert not r1.from_cache
        assert call_count == 1

        # Second call — cache hit
        r2 = judge_with_budget(
            decision_class=DecisionClass.C2_STANDARD.value,
            judge_fn=counting_judge,
            cache=cache,
            context_signature="sig-001",
        )
        assert r2.from_cache
        assert call_count == 1  # not called again

    def test_sub_budget_tracking(self):
        """Sub-budgets are tracked."""
        def judge():
            time.sleep(0.01)  # 10ms
            return {"verdict": "SEAL", "reason": "test"}

        result = judge_with_budget(
            decision_class=DecisionClass.C3_DEEP.value,
            judge_fn=judge,
        )
        assert result.sub_budget.judge_ms > 5  # at least 5ms
        assert result.sub_budget.total_ms > 0


# ═══════════════════════════════════════════════════════════════════
# CLASSIFY AND JUDGE
# ═══════════════════════════════════════════════════════════════════


class TestClassifyAndJudge:
    """Test the convenience pipeline."""

    def test_observe_fast(self):
        """OBSERVE + low risk → C0_AUTO → fast path."""
        def judge():
            return {"verdict": "PROCEED", "reason": "observation only"}

        result = classify_and_judge(
            action_class="OBSERVE",
            risk_class="low",
            is_irreversible=False,
            has_cached_verdict=False,
            judge_fn=judge,
        )
        assert result.judge_result.decision_class == DecisionClass.C0_AUTO.value
        assert result.judge_result.within_budget

    def test_irreversible_sovereign(self):
        """Irreversible → C4_SOVEREIGN → 888_HOLD."""
        def judge():
            return {"verdict": "SEAL", "reason": "Should not run"}

        result = classify_and_judge(
            action_class="ATOMIC",
            risk_class="atomic",
            is_irreversible=True,
            has_cached_verdict=False,
            judge_fn=judge,
        )
        assert result.judge_result.verdict == "888_HOLD"


# ═══════════════════════════════════════════════════════════════════
# LATENCY METRICS
# ═══════════════════════════════════════════════════════════════════


class TestLatencyMetrics:
    """Test metrics tracking."""

    def test_record_decision(self):
        """Metrics record decisions correctly."""
        metrics = LatencyMetrics()

        result = JudgePipelineResult(
            judge_result=JudgeResult(
                verdict="SEAL", decision_class="C2_STANDARD",
                latency_ms=50, within_budget=True, reason="",
            ),
            sub_budget=None,  # type: ignore
            from_cache=False,
        )
        metrics.record(result)

        assert metrics.total_decisions == 1
        assert metrics.within_budget == 1
        assert metrics.breaches == 0

    def test_breach_rate(self):
        """Breach rate is computed correctly."""
        metrics = LatencyMetrics()

        # 3 within budget, 1 breach
        for _ in range(3):
            metrics.record(JudgePipelineResult(
                judge_result=JudgeResult(
                    verdict="SEAL", decision_class="C2_STANDARD",
                    latency_ms=50, within_budget=True, reason="",
                ),
                sub_budget=None, from_cache=False,  # type: ignore
            ))

        metrics.record(JudgePipelineResult(
            judge_result=JudgeResult(
                verdict="HOLD", decision_class="C1_FAST",
                latency_ms=100, within_budget=False, reason="breach",
            ),
            sub_budget=None, from_cache=False,  # type: ignore
        ))

        assert metrics.breach_rate == pytest.approx(0.25)

    def test_health_check_healthy(self):
        """Health check returns HEALTHY when metrics are good."""
        metrics = LatencyMetrics()
        for i in range(20):
            metrics.record(JudgePipelineResult(
                judge_result=JudgeResult(
                    verdict="SEAL", decision_class="C2_STANDARD",
                    latency_ms=50, within_budget=True, reason="",
                ),
                sub_budget=None, from_cache=(i % 3 == 0),  # some cache hits
            ))

        health = metrics.health_check()
        assert health["status"] == "HEALTHY"
        assert len(health["warnings"]) == 0

    def test_health_check_high_breach_rate(self):
        """Health check warns on high breach rate."""
        metrics = LatencyMetrics()
        # 7 breaches out of 10 = 70% breach rate
        for i in range(10):
            metrics.record(JudgePipelineResult(
                judge_result=JudgeResult(
                    verdict="HOLD" if i < 7 else "SEAL",
                    decision_class="C2_STANDARD",
                    latency_ms=100 if i < 7 else 50,
                    within_budget=i >= 7,
                    reason="",
                ),
                sub_budget=None, from_cache=False,  # type: ignore
            ))

        health = metrics.health_check()
        assert health["status"] == "WARNING"
        assert any("HIGH_BREACH_RATE" in w for w in health["warnings"])


# ═══════════════════════════════════════════════════════════════════
# FAILURE BEHAVIOR TESTS
# ═══════════════════════════════════════════════════════════════════


class TestFailureBehavior:
    """Test failure behavior — the most important tests."""

    def test_force_delay_on_fast_class(self):
        """Force 300ms delay on FAST class → verdict=HOLD, reason=LATENCY_BREACH."""
        def slow_judge():
            time.sleep(0.3)
            return {"verdict": "SEAL", "reason": "Should be degraded"}

        result = judge_with_budget(
            decision_class=DecisionClass.C1_FAST.value,
            judge_fn=slow_judge,
        )
        assert result.judge_result.verdict == "HOLD"
        assert "Latency breach" in result.degradation_reason  # type: ignore

    def test_degradation_never_guesses(self):
        """Degradation always returns a safe verdict, never PROCEED."""
        for cls in DecisionClass:
            if cls == DecisionClass.C4_SOVEREIGN:
                continue  # unbounded

            budget = LATENCY_BUDGETS[cls]
            def slow_judge():
                time.sleep(budget.max_latency_ms / 1000 + 0.05)
                return {"verdict": "SEAL", "reason": "Too slow"}

            result = judge_with_budget(
                decision_class=cls.value,
                judge_fn=slow_judge,
            )
            # Degraded verdict must be HOLD or SABAR or 888_HOLD — never PROCEED/SEAL
            assert result.judge_result.verdict in ("HOLD", "SABAR", "888_HOLD"), \
                f"Class {cls.value} degraded to unsafe verdict: {result.judge_result.verdict}"

    def test_unknown_class_defaults_conservative(self):
        """Unknown decision class → C3_DEEP (conservative)."""
        def judge():
            return {"verdict": "SEAL", "reason": "test"}

        result = judge_with_budget(
            decision_class="UNKNOWN_CLASS",
            judge_fn=judge,
        )
        # Should use C3_DEEP budget (1000ms)
        assert result.judge_result.within_budget
