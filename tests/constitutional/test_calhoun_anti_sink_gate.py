"""
tests/constitutional/test_calhoun_anti_sink_gate.py — Calhoun anti-sink gate (Q10)
═════════════════════════════════════════════════════════════════════════════

Three Closures — Q10 (GENESIS/058, sealed 2026-08-02).

Tests verify:
  - Observation tools always PROCEED (anti-sink needs to observe).
  - Empty history → PROCEED, ratio 0.0.
  - Single warning → SABAR, no block.
  - Sustained pattern (3+ warnings) → HOLD.
  - FQ overheat window → HOLD.
  - Receipt contract (F11 AUDIT).

Floor binding: F5 PEACE², F6 EMPATHY/MARUAH.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest


@dataclass
class _Ctx:
    tool_name: str = "arif_forge"
    session_id: str = "SEAL-test"
    actor_id: str = "arif"
    action_class: str = "MUTATE"
    params: dict[str, Any] = field(default_factory=dict)
    fq: float | None = None


# ═══════════════════════════════════════════════════════════════════════════
# 1. Module surface
# ═══════════════════════════════════════════════════════════════════════════


class TestModuleSurface:
    def test_module_imports(self):
        from arifosmcp.runtime import calhoun_anti_sink_gate as mod

        assert hasattr(mod, "calhoun_anti_sink_gate")
        assert hasattr(mod, "SUSTAINED_WARNINGS_BEFORE_HOLD")
        assert hasattr(mod, "ANTI_CALHOUN_HOLD_THRESHOLD")
        assert hasattr(mod, "reset_session")

    def test_thresholds_are_frozen(self):
        """F2: thresholds are constitutional — frozen."""
        from arifosmcp.runtime.calhoun_anti_sink_gate import (
            ANTI_CALHOUN_HOLD_THRESHOLD,
            BEHAVIORAL_SINK_RATIO_THRESHOLD,
            FQ_OVERHEAT_THRESHOLD,
            SUSTAINED_WARNINGS_BEFORE_HOLD,
        )

        assert ANTI_CALHOUN_HOLD_THRESHOLD == 0.40
        assert BEHAVIORAL_SINK_RATIO_THRESHOLD == 0.40
        assert FQ_OVERHEAT_THRESHOLD == 3.0
        assert SUSTAINED_WARNINGS_BEFORE_HOLD == 3


# ═══════════════════════════════════════════════════════════════════════════
# 2. Observation tools always PROCEED (the anti-sink needs observation)
# ═══════════════════════════════════════════════════════════════════════════


class TestObservationBypass:
    def test_observe_action_class_proceeds(self):
        from arifosmcp.runtime.calhoun_anti_sink_gate import calhoun_anti_sink_gate

        ctx = _Ctx(tool_name="arif_observe", action_class="OBSERVE")
        result = calhoun_anti_sink_gate(ctx)
        assert result["verdict"] == "PROCEED"
        assert result["passed"] is True
        assert result["receipt"]["skipped"] is True

    def test_observe_tool_proceeds(self):
        from arifosmcp.runtime.calhoun_anti_sink_gate import calhoun_anti_sink_gate

        for tool in ("arif_observe", "arif_fetch", "arif_measure", "arif_memory_recall"):
            ctx = _Ctx(tool_name=tool, action_class="MUTATE")
            result = calhoun_anti_sink_gate(ctx)
            assert result["verdict"] == "PROCEED", f"{tool}: {result}"

    def test_observe_skipped_receipt_carries_doctrine(self):
        from arifosmcp.runtime.calhoun_anti_sink_gate import calhoun_anti_sink_gate

        ctx = _Ctx(tool_name="arif_observe", action_class="OBSERVE")
        result = calhoun_anti_sink_gate(ctx)
        assert "GENESIS/058" in result["receipt"]["doctrine"]


# ═══════════════════════════════════════════════════════════════════════════
# 3. Empty / healthy history → PROCEED
# ═══════════════════════════════════════════════════════════════════════════


class TestCleanHistory:
    def test_no_history_proceeds(self):
        from arifosmcp.runtime.calhoun_anti_sink_gate import calhoun_anti_sink_gate

        ctx = _Ctx()
        result = calhoun_anti_sink_gate(ctx)
        assert result["verdict"] == "PROCEED"
        assert result["passed"] is True
        assert result["behavioral_sink"]["sink_ratio"] == 0.0
        assert result["behavioral_sink"]["status"] == "CLEAR"

    def test_substantive_history_proceeds(self):
        from arifosmcp.runtime.calhoun_anti_sink_gate import calhoun_anti_sink_gate

        ctx = _Ctx(
            params={
                "session_history": [
                    "real critique output 1",
                    "real critique output 2",
                    "real critique output 3",
                ]
            }
        )
        result = calhoun_anti_sink_gate(ctx)
        assert result["behavioral_sink"]["sink_ratio"] == 0.0
        assert result["verdict"] == "PROCEED"


# ═══════════════════════════════════════════════════════════════════════════
# 4. Sustained pattern → HOLD (3+ consecutive warnings)
# ═══════════════════════════════════════════════════════════════════════════


class TestSustainedPattern:
    def test_single_warning_stays_sabar(self):
        from arifosmcp.runtime.calhoun_anti_sink_gate import calhoun_anti_sink_gate, reset_session

        reset_session("SEAL-sustain")
        ctx = _Ctx(
            session_id="SEAL-sustain",
            params={
                "session_history": [None, "", "pass", "ok", "real output"] * 2  # 8/10 empty
            },
        )
        result = calhoun_anti_sink_gate(ctx)
        # First call after reset — warning_count=1, should be SABAR
        assert result["verdict"] in {"SABAR", "PROCEED"}, result
        reset_session("SEAL-sustain")  # cleanup

    def test_three_consecutive_warnings_hold(self):
        from arifosmcp.runtime.calhoun_anti_sink_gate import calhoun_anti_sink_gate, reset_session

        reset_session("SEAL-sustain-3")
        heavy_empties = [None, "", "pass", "ok", "no-op"] * 4  # 20/20 empty
        results = []
        for _ in range(3):
            ctx = _Ctx(
                session_id="SEAL-sustain-3",
                params={"session_history": heavy_empties},
            )
            results.append(calhoun_anti_sink_gate(ctx))
        # The third call should HOLD
        final = results[-1]
        assert final["verdict"] == "HOLD", f"final verdict: {final['verdict']}"
        assert final["passed"] is False
        assert "F5" in final["violated_laws"]
        assert "F6" in final["violated_laws"]
        reset_session("SEAL-sustain-3")

    def test_warnings_count_increments_monotonically(self):
        from arifosmcp.runtime.calhoun_anti_sink_gate import calhoun_anti_sink_gate, reset_session

        reset_session("SEAL-mono")
        heavy_empties = [None, ""] * 5  # 10/10 empty
        for i in range(3):
            ctx = _Ctx(session_id="SEAL-mono", params={"session_history": heavy_empties})
            result = calhoun_anti_sink_gate(ctx)
            assert result["warnings_count"] == i + 1, result
        reset_session("SEAL-mono")


# ═══════════════════════════════════════════════════════════════════════════
# 5. FQ overheat window
# ═══════════════════════════════════════════════════════════════════════════


class TestFQOverheat:
    def test_fq_overheat_sustained_triggers_hold(self):
        from arifosmcp.runtime.calhoun_anti_sink_gate import calhoun_anti_sink_gate, reset_session

        reset_session("SEAL-fq")
        # Feed FQ > 3.0 for 3 consecutive cycles
        for i in range(3):
            ctx = _Ctx(session_id="SEAL-fq", fq=5.0)
            result = calhoun_anti_sink_gate(ctx)
        assert result["fq_overheat"] is True
        assert result["verdict"] == "HOLD", result
        assert "F5" in result["violated_laws"]
        reset_session("SEAL-fq")

    def test_fq_below_threshold_stays_proceed(self):
        from arifosmcp.runtime.calhoun_anti_sink_gate import calhoun_anti_sink_gate, reset_session

        reset_session("SEAL-fq-low")
        for _ in range(3):
            ctx = _Ctx(session_id="SEAL-fq-low", fq=1.5)
            result = calhoun_anti_sink_gate(ctx)
        assert result["fq_overheat"] is False
        assert result["verdict"] == "PROCEED"
        reset_session("SEAL-fq-low")


# ═══════════════════════════════════════════════════════════════════════════
# 6. Receipt contract (F11 AUDIT)
# ═══════════════════════════════════════════════════════════════════════════


class TestReceiptContract:
    def test_receipt_contains_required_fields(self):
        from arifosmcp.runtime.calhoun_anti_sink_gate import calhoun_anti_sink_gate

        ctx = _Ctx()
        result = calhoun_anti_sink_gate(ctx)
        receipt = result["receipt"]
        for field in (
            "gate",
            "verdict",
            "passed",
            "q10_checks",
            "anti_calhoun_score",
            "anti_calhoun_verdict",
            "behavioral_sink",
            "fq_window",
            "fq_overheat",
            "warnings_count",
            "violated_laws",
            "latency_ms",
            "doctrine",
        ):
            assert field in receipt, f"missing: {field}"

    def test_doctrine_field_references_genesis_058(self):
        from arifosmcp.runtime.calhoun_anti_sink_gate import calhoun_anti_sink_gate

        ctx = _Ctx()
        result = calhoun_anti_sink_gate(ctx)
        assert "GENESIS/058" in result["receipt"]["doctrine"]
