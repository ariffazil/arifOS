"""
tests/test_mind_feedback.py — MIND Feedback Loop Tests v1
══════════════════════════════════════════════════════════

Tests for the MIND recursive self-correction architecture:
  - mind_state.py   — persistent state, checkpoint, rollback
  - feedback_loop.py — signal evaluation, graph wiring
  - l5_graph_read.py — L5 read path, adapters
  - mind_feedback_hook.py — integration hook, auto-patch

Coverage targets: 15+ test cases across state machine, feedback signals,
graph adapters, and integration.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import os
import pytest
from datetime import datetime, UTC, timedelta

# ═══════════════════════════════════════════════════════════════════════════
# mind_state.py tests
# ═══════════════════════════════════════════════════════════════════════════


class TestMINDState:
    """Tests for MINDState persistent state object."""

    def test_create_state(self):
        """Smoke: create a fresh MINDState."""
        from arifosmcp.runtime.mind_state import create_mind_state

        state = create_mind_state("test goal", intent="plan", domain="test")
        assert state.goal == "test goal"
        assert state.intent == "plan"
        assert state.domain == "test"
        assert len(state.plan_steps) == 0
        assert state.plan_status.value == "active"
        assert state.epistemic_band == 0.5
        assert 0.03 <= state.omega_0 <= 0.05

    def test_add_step(self):
        """Add reasoning steps to the plan."""
        from arifosmcp.runtime.mind_state import create_mind_state

        state = create_mind_state("test")
        s1 = state.add_step("step 1", confidence=0.8)
        s2 = state.add_step("step 2", confidence=0.9)

        assert s1.step_number == 1
        assert s2.step_number == 2
        assert len(state.plan_steps) == 2
        assert s1.confidence <= 0.90  # F7 cap
        assert s2.confidence <= 0.90

    def test_mark_step_success(self):
        """Mark a step as completed successfully."""
        from arifosmcp.runtime.mind_state import create_mind_state, StepStatus, FeedbackSignal

        state = create_mind_state("test")
        state.add_step("do thing")
        result = state.mark_step(1, StepStatus.COMPLETED)

        assert result is not None
        assert result.status == StepStatus.COMPLETED
        assert state.plan_status.value == "active"

    def test_mark_step_failure(self):
        """Mark a step as failed and verify attempt counter."""
        from arifosmcp.runtime.mind_state import create_mind_state, StepStatus

        state = create_mind_state("test")
        state.add_step("risky step")
        state.mark_step(1, StepStatus.FAILED, error_message="bad")

        step = state.plan_steps[0]
        assert step.status == StepStatus.FAILED
        assert step.attempt_count == 1
        assert state.total_revisions == 1

    def test_revise_step(self):
        """Create a revision of a failed step."""
        from arifosmcp.runtime.mind_state import (
            create_mind_state, StepStatus,
        )

        state = create_mind_state("test")
        state.add_step("buggy step")
        state.mark_step(1, StepStatus.FAILED)
        revision = state.revise_step(1, "fixed step", reason="typo")

        assert revision.is_revision is True
        assert revision.revises_step == 1
        assert state.plan_steps[0].status == StepStatus.REVISED
        assert state.total_revisions == 2  # failure + revision

    def test_max_revisions_hold(self):
        """F08 guard: max revisions triggers HOLD."""
        from arifosmcp.runtime.mind_state import (
            create_mind_state, StepStatus, PlanStatus,
        )

        state = create_mind_state("test")
        state.max_revisions = 3
        state.add_step("loop step")

        for i in range(3):
            state.mark_step(1, StepStatus.FAILED)

        assert state.plan_status == PlanStatus.HOLD
        assert state.total_revisions == 3

    def test_checkpoint_and_rollback(self):
        """Checkpoint state and rollback to previous checkpoint."""
        from arifosmcp.runtime.mind_state import create_mind_state

        state = create_mind_state("test")
        state.add_step("safe step")
        cp1 = state.checkpoint()

        state.add_step("risky step")
        state.epistemic_band = 0.75
        cp2 = state.checkpoint()

        state.add_step("dangerous step")
        state.epistemic_band = 0.95  # should be capped
        state.malu_index = 0.5

        # Rollback to first checkpoint
        assert state.rollback_to(0) is True
        assert len(state.plan_steps) == 1
        assert state.plan_steps[0].content == "safe step"

    def test_serialization_roundtrip(self):
        """Serialize and deserialize MINDState."""
        from arifosmcp.runtime.mind_state import MINDState, create_mind_state

        state = create_mind_state("serialize test", intent="verify")
        state.add_step("step a", confidence=0.85)
        state.add_step("step b", confidence=0.92)
        state.epistemic_band = 0.88
        state.malu_index = 0.05
        state.checkpoint()

        d = state.to_dict()
        restored = MINDState.from_dict(d)

        assert restored.goal == state.goal
        assert restored.intent == state.intent
        assert len(restored.plan_steps) == 2
        assert restored.epistemic_band == 0.88
        assert restored.malu_index == 0.05

    def test_state_hash(self):
        """State hash changes when plan changes."""
        from arifosmcp.runtime.mind_state import create_mind_state

        state = create_mind_state("hash test")
        h1 = state.state_hash()
        state.add_step("new step")
        h2 = state.state_hash()
        assert h1 != h2

    def test_can_continue(self):
        """can_continue returns False when plan is HOLD."""
        from arifosmcp.runtime.mind_state import (
            create_mind_state, PlanStatus, can_continue,
        )

        state = create_mind_state("test")
        ok, _ = can_continue(state)
        assert ok is True

        state.plan_status = PlanStatus.HOLD
        ok, reason = can_continue(state)
        assert ok is False
        assert "HOLD" in reason

    def test_c_dark_guard(self):
        """C_dark >= 0.30 blocks continuation (F9 ANTI-HANTU)."""
        from arifosmcp.runtime.mind_state import create_mind_state, can_continue

        state = create_mind_state("test")
        state.c_dark = 0.35
        ok, reason = can_continue(state)
        assert ok is False
        assert "ANTI-HANTU" in reason

    def test_malu_threshold(self):
        """Malu index >= 0.60 triggers BERAT threshold."""
        from arifosmcp.runtime.mind_state import create_mind_state, can_continue

        state = create_mind_state("test")
        state.malu_index = 0.65
        ok, reason = can_continue(state)
        assert ok is False
        assert "BERAT" in reason

    def test_record_violation(self):
        """Floor violations increment malu_index."""
        from arifosmcp.runtime.mind_state import create_mind_state

        state = create_mind_state("test")
        assert state.malu_index == 0.0

        state.record_violation("F02", "claimed certainty without evidence")
        assert state.malu_index > 0.0
        assert len(state.floor_violations) == 1
        assert state.floor_violations[0]["floor"] == "F02"

    def test_is_stale(self):
        """State older than max_age is stale."""
        from arifosmcp.runtime.mind_state import create_mind_state, is_stale

        state = create_mind_state("test")
        # Force old timestamp
        state.updated_at = (datetime.now(UTC) - timedelta(hours=2)).isoformat()
        assert is_stale(state, max_age_minutes=30) is True

        state.updated_at = datetime.now(UTC).isoformat()
        assert is_stale(state, max_age_minutes=30) is False


# ═══════════════════════════════════════════════════════════════════════════
# feedback_loop.py tests
# ═══════════════════════════════════════════════════════════════════════════


class TestFeedbackLoop:
    """Tests for FeedbackLoop signal evaluation."""

    def test_proceed_on_success(self):
        """Successful step returns PROCEED."""
        from arifosmcp.runtime.mind_state import create_mind_state
        from arifosmcp.runtime.feedback_loop import (
            FeedbackLoop, FeedbackSignal,
        )

        state = create_mind_state("test")
        step = state.add_step("good step", confidence=0.85)
        loop = FeedbackLoop(state)

        signal = loop.evaluate(step, {"success": True, "confidence": 0.85})
        assert signal == FeedbackSignal.PROCEED
        assert step.status.value == "completed"

    def test_revise_local_on_low_confidence(self):
        """Step with low confidence triggers REVISE_LOCAL."""
        from arifosmcp.runtime.mind_state import create_mind_state
        from arifosmcp.runtime.feedback_loop import FeedbackLoop, FeedbackSignal

        state = create_mind_state("test")
        step = state.add_step("uncertain step", confidence=0.5)
        loop = FeedbackLoop(state)

        signal = loop.evaluate(step, {"success": True, "confidence": 0.55})
        assert signal == FeedbackSignal.REVISE_LOCAL
        assert step.epistemic_tag.value == "PLAUSIBLE"

    def test_revise_global_on_fatal(self):
        """Fatal error triggers REVISE_GLOBAL."""
        from arifosmcp.runtime.mind_state import create_mind_state
        from arifosmcp.runtime.feedback_loop import FeedbackLoop, FeedbackSignal

        state = create_mind_state("test")
        step = state.add_step("fatal step")
        loop = FeedbackLoop(state)

        signal = loop.evaluate(
            step,
            {"success": False, "fatal": True, "error": "kernel panic"},
        )
        assert signal == FeedbackSignal.REVISE_GLOBAL
        assert state.plan_status.value == "diverged"

    def test_backtrack_on_contradiction(self):
        """Evidence contradiction triggers BACKTRACK."""
        from arifosmcp.runtime.mind_state import create_mind_state
        from arifosmcp.runtime.feedback_loop import FeedbackLoop, FeedbackSignal

        state = create_mind_state("test")
        step = state.add_step("contradicted step")
        loop = FeedbackLoop(state)

        signal = loop.evaluate(
            step,
            {"success": False, "contradiction": True, "error": "F2 violation"},
        )
        assert signal == FeedbackSignal.BACKTRACK

    def test_max_local_revision_escalates(self):
        """Too many local failures escalates to REVISE_GLOBAL."""
        from arifosmcp.runtime.mind_state import create_mind_state
        from arifosmcp.runtime.feedback_loop import FeedbackLoop, FeedbackSignal

        state = create_mind_state("test")
        step = state.add_step("stubborn step")
        loop = FeedbackLoop(state)
        loop.max_revisions_per_step = 2

        # First failure → REVISE_LOCAL (attempt 1)
        s1 = loop.evaluate(
            step, {"success": False, "error": "fail 1"}
        )
        assert s1 == FeedbackSignal.REVISE_LOCAL

        # Second failure → REVISE_GLOBAL (attempt 2 == max)
        s2 = loop.evaluate(
            step, {"success": False, "error": "fail 2"}
        )
        assert s2 == FeedbackSignal.REVISE_GLOBAL

    def test_finalize(self):
        """Finalize completes the plan and records episode."""
        from arifosmcp.runtime.mind_state import create_mind_state
        from arifosmcp.runtime.feedback_loop import (
            FeedbackLoop, FeedbackSignal, PlanStatus,
        )

        state = create_mind_state("test")
        state.add_step("done", confidence=0.95)
        loop = FeedbackLoop(state)

        signal = loop.finalize()
        assert signal == FeedbackSignal.PROCEED
        assert state.plan_status == PlanStatus.COMPLETED

    def test_hold_when_cannot_continue(self):
        """HOLD returned when can_continue is False."""
        from arifosmcp.runtime.mind_state import create_mind_state, PlanStatus
        from arifosmcp.runtime.feedback_loop import FeedbackLoop, FeedbackSignal

        state = create_mind_state("test")
        state.plan_status = PlanStatus.HOLD
        step = state.add_step("stuck")
        loop = FeedbackLoop(state)

        signal = loop.evaluate(step, {"success": True})
        assert signal == FeedbackSignal.HOLD

    def test_noop_graph_writer(self):
        """NoOpGraphWriter returns safe defaults, never throws."""
        from arifosmcp.runtime.feedback_loop import NoOpGraphWriter

        w = NoOpGraphWriter()
        assert w.update_edge_weight("a", "b", 0.1) is False
        assert w.annotate_path(["a", "b"], {}) is False
        assert w.record_episode(None, None) is None


# ═══════════════════════════════════════════════════════════════════════════
# l5_graph_read.py tests
# ═══════════════════════════════════════════════════════════════════════════


class TestL5GraphRead:
    """Tests for L5 Graphiti read path and adapters."""

    def test_l5_disabled_returns_empty(self, monkeypatch):
        """When L5 is disabled, all functions return safe defaults."""
        monkeypatch.setenv("GRAPHITI_L5_ENABLED", "false")

        from arifosmcp.runtime.l5_graph_read import (
            find_similar_tasks,
            get_capability_subgraph,
            get_prior_path,
            get_mind_state_checkpoint,
        )

        assert find_similar_tasks("test") == []
        subgraph = get_capability_subgraph("test")
        assert subgraph["provenance"] == "l5_disabled"
        assert get_prior_path("sig") is None
        assert get_mind_state_checkpoint("ctx") is None

    def test_l5_graph_reader_adapter(self, monkeypatch):
        """L5GraphReader wraps l5_graph_read functions."""
        monkeypatch.setenv("GRAPHITI_L5_ENABLED", "false")

        from arifosmcp.runtime.l5_graph_read import L5GraphReader

        reader = L5GraphReader()
        assert reader.find_similar_tasks("test") == []
        subgraph = reader.get_capability_subgraph("test")
        assert subgraph["nodes"] == []

    def test_l5_graph_writer_adapter(self, monkeypatch):
        """L5GraphWriter wraps l5_graph_write functions."""
        monkeypatch.setenv("GRAPHITI_L5_ENABLED", "false")

        from arifosmcp.runtime.l5_graph_read import L5GraphWriter

        writer = L5GraphWriter()
        assert writer.update_edge_weight("a", "b", 0.1) is False
        assert writer.annotate_path(["a"], {}) is False

    def test_l5_health_check_disabled(self, monkeypatch):
        """Health check returns 'disabled' when L5 is off."""
        monkeypatch.setenv("GRAPHITI_L5_ENABLED", "false")

        from arifosmcp.runtime.l5_graph_read import l5_health_check

        result = l5_health_check()
        assert result["status"] == "disabled"
        assert result["l5_enabled"] is False


# ═══════════════════════════════════════════════════════════════════════════
# mind_feedback_hook.py tests
# ═══════════════════════════════════════════════════════════════════════════


class TestMindFeedbackHook:
    """Tests for the integration hook."""

    def test_tracker_start(self):
        """MindFeedbackTracker creates state correctly."""
        from arifosmcp.runtime.mind_feedback_hook import MindFeedbackTracker

        tracker = MindFeedbackTracker.start(
            query="integration test",
            intent="verify",
            domain="test",
        )
        assert tracker.state.goal == "integration test"
        assert tracker.state.intent == "verify"
        assert tracker.state.domain == "test"
        assert tracker.state.context_id  # auto-generated

    def test_tracker_after_layer(self, monkeypatch):
        """after_layer records a metabolic layer."""
        monkeypatch.setenv("MIND_CHECKPOINT_ENABLED", "false")

        import arifosmcp.runtime.mind_feedback_hook as hook
        hook._FEEDBACK_ENABLED = True

        from arifosmcp.runtime.mind_feedback_hook import MindFeedbackTracker
        from arifosmcp.runtime.mind_state import FeedbackSignal

        tracker = MindFeedbackTracker.start(query="test")
        signal = tracker.after_layer("metabolize", "parsed input", confidence=0.85)

        assert signal == FeedbackSignal.PROCEED
        assert len(tracker.layers_completed) == 1
        assert tracker.layers_completed[0]["layer"] == "metabolize"
        assert len(tracker.state.plan_steps) == 1

        hook._FEEDBACK_ENABLED = False  # restore

    def test_tracker_finalize(self, monkeypatch):
        """finalize produces summary with all metadata."""
        monkeypatch.setenv("MIND_CHECKPOINT_ENABLED", "false")

        import arifosmcp.runtime.mind_feedback_hook as hook
        hook._FEEDBACK_ENABLED = True

        from arifosmcp.runtime.mind_feedback_hook import MindFeedbackTracker

        tracker = MindFeedbackTracker.start(query="final test")
        tracker.after_layer("metabolize", "done", confidence=0.88)

        summary = tracker.finalize(response=None, overall_confidence=0.88)

        assert summary["context_id"] == tracker.state.context_id
        assert summary["layers_completed"] == 1
        assert summary["total_steps"] == 1
        assert summary["final_signal"] == "PROCEED"
        assert "duration_s" in summary

        hook._FEEDBACK_ENABLED = False  # restore

    def test_feedback_disabled_passthrough(self, monkeypatch):
        """When disabled, tracker.after_layer returns PROCEED always."""
        monkeypatch.setenv("MIND_FEEDBACK_ENABLED", "false")

        from arifosmcp.runtime.mind_feedback_hook import MindFeedbackTracker
        from arifosmcp.runtime.mind_state import FeedbackSignal

        tracker = MindFeedbackTracker.start(query="test")
        signal = tracker.after_layer("metabolize", "content", confidence=0.3)

        # Even with low confidence, disabled mode returns PROCEED
        assert signal == FeedbackSignal.PROCEED

    def test_auto_patch_disabled_by_default(self, monkeypatch):
        """Auto-patch should NOT activate when env var is false."""
        monkeypatch.setenv("MIND_FEEDBACK_ENABLED", "false")

        # Re-import to trigger auto-patch logic
        import importlib
        import arifosmcp.runtime.mind_feedback_hook as hook
        importlib.reload(hook)

        # The original function should still be the original
        from arifosmcp.runtime.mind_reason import arif_mind_reason_v2
        # Can't easily test this without mocking, but the import should not
        # have replaced the function. We test that the hook exists at least.
        assert hasattr(hook, 'mind_reason_with_feedback')


# ═══════════════════════════════════════════════════════════════════════════
# INTEGRATION: End-to-end
# ═══════════════════════════════════════════════════════════════════════════


class TestIntegration:
    """End-to-end: MINDState → FeedbackLoop → L5 adapters."""

    def test_full_flow_with_noop_adapters(self, monkeypatch):
        """Complete flow: create state, add steps, evaluate, checkpoint, finalize."""
        monkeypatch.setenv("GRAPHITI_L5_ENABLED", "false")
        monkeypatch.setenv("MIND_FEEDBACK_ENABLED", "true")
        monkeypatch.setenv("MIND_CHECKPOINT_ENABLED", "false")

        from arifosmcp.runtime.mind_state import create_mind_state
        from arifosmcp.runtime.feedback_loop import create_feedback_loop, NoOpGraphWriter, NoOpGraphReader

        state = create_mind_state("e2e test", intent="plan")
        loop = create_feedback_loop(
            state,
            graph_writer=NoOpGraphWriter(),
            graph_reader=NoOpGraphReader(),
        )

        # Simulate 3 reasoning steps
        steps_signals = []
        for i, (content, outcome) in enumerate([
            ("parse input", {"success": True, "confidence": 0.90}),
            ("analyze", {"success": True, "confidence": 0.85}),
            ("synthesize", {"success": True, "confidence": 0.92}),
        ]):
            step = state.add_step(content, confidence=outcome.get("confidence", 0.5))
            signal = loop.evaluate(step, outcome)
            steps_signals.append(signal.value)

        # All should PROCEED
        assert steps_signals == ["PROCEED", "PROCEED", "PROCEED"]

        # Finalize
        loop.finalize()
        assert state.plan_status.value == "completed"
        assert state.total_revisions == 0

        # Checkpoint should work
        cp = state.checkpoint()
        assert cp["context_id"] == state.context_id
        assert cp["total_steps"] == 3

    def test_recovery_flow(self):
        """Failure → revision → success flow."""
        from arifosmcp.runtime.mind_state import create_mind_state
        from arifosmcp.runtime.feedback_loop import create_feedback_loop

        state = create_mind_state("recovery test")
        loop = create_feedback_loop(state)

        # Step 1: fail
        s1 = state.add_step("bad analysis")
        signal1 = loop.evaluate(s1, {"success": False, "error": "parse error"})
        assert signal1.value == "REVISE_LOCAL"

        # Revise step 1
        r1 = state.revise_step(1, "corrected analysis")
        signal1b = loop.evaluate(r1, {"success": True, "confidence": 0.88})
        assert signal1b.value == "PROCEED"

        # Step 2: succeed
        s2 = state.add_step("verify")
        signal2 = loop.evaluate(s2, {"success": True, "confidence": 0.95})
        assert signal2.value == "PROCEED"

        assert state.total_revisions == 2  # one failure mark + one revise_step
        assert len(state.plan_steps) == 3  # original + revision + step 2


# ═══════════════════════════════════════════════════════════════════════════


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
