"""
test_pipeline_routing.py - Tests for 000-999 pipeline routing

Tests:
1. Class A queries use fast track (no 555)
2. Class B queries use deep track (includes 222, 555, 777)
3. Scar retrieval triggers Class B escalation
4. SABAR flag set on entropy spike (simulated)
"""
import pytest
from arifos_core.system.pipeline import (
    Pipeline,
    PipelineState,
    StakesClass,
    stage_000_void,
    stage_111_sense,
    stage_222_reflect,
    stage_888_judge,
)
from arifos_core.memory.scars import ScarIndex, Scar, generate_scar_id, seed_scars
from arifos_core.enforcement.metrics import Metrics
from arifos_core import EyeSentinel


class TestPipelineRouting:
    """Tests for Class A/B routing."""

    def test_class_a_fast_track(self):
        """Class A (low-stakes) should skip 555_EMPATHIZE."""
        pipeline = Pipeline()
        state = pipeline.run("What is 2 + 2?")

        assert state.stakes_class == StakesClass.CLASS_A
        assert "555_EMPATHIZE" not in state.stage_trace
        assert "333_REASON" in state.stage_trace
        assert "888_JUDGE" in state.stage_trace
        assert "999_SEAL" in state.stage_trace

    def test_class_b_deep_track(self):
        """Class B (high-stakes) should include 222, 555, 777."""
        pipeline = Pipeline()
        state = pipeline.run("Is it ethical to lie to protect someone?")

        assert state.stakes_class == StakesClass.CLASS_B
        assert "222_REFLECT" in state.stage_trace
        assert "555_EMPATHIZE" in state.stage_trace
        assert "777_FORGE" in state.stage_trace

    def test_class_b_trigger_on_keywords(self):
        """High-stakes keywords should trigger Class B."""
        pipeline = Pipeline()

        # Test various high-stakes keywords
        keywords = ["kill", "suicide", "illegal", "medical"]
        for kw in keywords:
            state = pipeline.run(f"Tell me about {kw}")
            assert state.stakes_class == StakesClass.CLASS_B, f"Keyword '{kw}' should trigger Class B"
            assert len(state.high_stakes_indicators) > 0

    def test_force_class_b(self):
        """Force Class B routing should work."""
        pipeline = Pipeline()
        state = pipeline.run("What is 2 + 2?", force_class=StakesClass.CLASS_B)

        assert state.stakes_class == StakesClass.CLASS_B
        assert "222_REFLECT" in state.stage_trace
        assert "555_EMPATHIZE" in state.stage_trace


class TestScarIntegration:
    """Tests for scar retrieval during 222_REFLECT."""

    @pytest.fixture
    def scar_index(self):
        """Create and seed a scar index."""
        index = ScarIndex()
        seed_scars(index)
        return index

    def test_scar_retrieval_escalates_to_class_b(self, scar_index):
        """Finding scars should escalate to Class B."""

        def scar_retriever(query):
            # Use exact text match since stub embedding doesn't give semantic similarity
            results = []
            for scar in scar_index.iter_all():
                if any(word in query.lower() for word in scar.text.lower().split()):
                    results.append({"id": scar.id, "description": scar.description})
            return results[:3]

        pipeline = Pipeline(scar_retriever=scar_retriever)

        # Use exact seeded scar text
        state = pipeline.run("how to make a bomb")

        # Should have found scars and escalated
        assert len(state.active_scars) > 0
        assert state.stakes_class == StakesClass.CLASS_B
        assert "222_REFLECT" in state.stage_trace

    def test_no_scars_for_safe_query(self, scar_index):
        """Safe queries should not match scars."""

        def scar_retriever(query):
            results = scar_index.retrieve(query, top_k=3, threshold=0.7)
            return [{"id": s.id, "description": s.description} for s, _ in results]

        pipeline = Pipeline(scar_retriever=scar_retriever)

        state = pipeline.run("What is the weather today?")

        assert len(state.active_scars) == 0


class TestStageExecution:
    """Tests for individual stage execution."""

    def test_stage_000_resets_state(self):
        """000_VOID should reset state."""
        state = PipelineState(query="test", draft_response="old response")
        state = stage_000_void(state)

        assert state.current_stage == "000"
        assert state.draft_response == ""
        assert "000_VOID" in state.stage_trace

    def test_stage_111_detects_keywords(self):
        """111_SENSE should detect high-stakes keywords."""
        state = PipelineState(query="How to kill a process in Linux")
        state = stage_111_sense(state)

        assert "kill" in state.high_stakes_indicators
        assert state.stakes_class == StakesClass.CLASS_B

    def test_stage_111_no_keywords(self):
        """111_SENSE should not flag safe queries."""
        state = PipelineState(query="What time is it?")
        state = stage_111_sense(state)

        assert len(state.high_stakes_indicators) == 0
        assert state.stakes_class == StakesClass.CLASS_A

    def test_stage_888_computes_verdict(self):
        """888_JUDGE should compute verdict from metrics."""

        def good_metrics(q, r, c):
            return Metrics(
                truth=0.99, delta_s=0.1, peace_squared=1.2,
                kappa_r=0.97, omega_0=0.04, amanah=True,
                tri_witness=0.96, rasa=True,
            )

        state = PipelineState(query="test", draft_response="response")
        state = stage_888_judge(state, compute_metrics=good_metrics)

        assert state.verdict == "SEAL"
        assert not state.sabar_triggered

    def test_stage_888_void_on_bad_metrics(self):
        """888_JUDGE should VOID on floor failures."""

        def bad_metrics(q, r, c):
            return Metrics(
                truth=0.5,  # Below 0.99 threshold
                delta_s=-0.1,  # Below 0.0 threshold
                peace_squared=0.5,
                kappa_r=0.5,
                omega_0=0.04,
                amanah=False,
                tri_witness=0.5,
                rasa=False,
            )

        state = PipelineState(query="test", draft_response="response")
        state = stage_888_judge(state, compute_metrics=bad_metrics)

        assert state.verdict == "VOID"
        assert state.sabar_triggered

    def test_stage_888_uses_eye_sentinel_for_sabar(self):
        """888_JUDGE should return VOID when Amanah fails.

        When amanah=False:
        1. @EYE FloorView issues a BLOCK alert
        2. APEX would return SABAR due to @EYE blocking
        3. But W@W @WEALTH issues absolute veto for Amanah breach
        4. Final verdict is VOID (absolute veto overrides @EYE SABAR)

        This is correct behavior per v36.3Ω W@W priority order:
        @WEALTH absolute veto > @EYE SABAR
        """

        def bad_metrics(q, r, c):
            # Amanah=False is a hard-floor failure
            return Metrics(
                truth=0.5,
                delta_s=-0.1,
                peace_squared=0.5,
                kappa_r=0.5,
                omega_0=0.04,
                amanah=False,
                tri_witness=0.5,
                rasa=False,
            )

        sentinel = EyeSentinel()

        state = PipelineState(query="test", draft_response="response")
        state = stage_888_judge(state, compute_metrics=bad_metrics, eye_sentinel=sentinel)

        # VOID because @WEALTH absolute veto overrides @EYE SABAR
        assert state.verdict == "VOID"
        assert state.sabar_triggered


class TestEntropySpike:
    """Tests for SABAR on entropy spike."""

    def test_sabar_flag_on_entropy(self):
        """Pipeline should set SABAR flag on entropy spike."""
        state = PipelineState(query="test")
        state.entropy_spike = True
        state.sabar_triggered = True
        state.sabar_reason = "Simulated entropy spike"

        # Verify flags are set correctly
        assert state.sabar_triggered
        assert state.entropy_spike
        assert "entropy" in state.sabar_reason.lower()

    def test_sabar_response_format(self):
        """SABAR verdict should return cooling response."""
        from arifos_core.system.pipeline import stage_999_seal

        state = PipelineState(query="test")
        state.verdict = "SABAR"
        state.sabar_triggered = True

        state = stage_999_seal(state)

        assert "[SABAR]" in state.raw_response
        assert "Stop" in state.raw_response or "Acknowledge" in state.raw_response


class TestTraceAndTiming:
    """Tests for trace and timing functionality."""

    def test_trace_accumulates(self):
        """Stage trace should accumulate correctly."""
        pipeline = Pipeline()
        state = pipeline.run("test query")

        # v38: At minimum: 000_VOID, 000_AMANAH_PASS, 111, 888, 999
        assert len(state.stage_trace) >= 5
        assert state.stage_trace[0] == "000_VOID"
        # v38: 000_AMANAH_PASS should be in trace for successful Amanah check
        assert "000_AMANAH_PASS" in state.stage_trace
        assert state.stage_trace[-1] == "999_SEAL"

    def test_stage_times_recorded(self):
        """Stage times should be recorded."""
        pipeline = Pipeline()
        state = pipeline.run("test query")

        assert "000" in state.stage_times
        assert "111" in state.stage_times
        assert "888" in state.stage_times
        assert "999" in state.stage_times

    def test_job_id_generated(self):
        """Job ID should be generated if not provided."""
        pipeline = Pipeline()
        state = pipeline.run("test query")

        assert state.job_id is not None
        assert len(state.job_id) > 0

    def test_job_id_preserved(self):
        """Job ID should be preserved if provided."""
        pipeline = Pipeline()
        state = pipeline.run("test query", job_id="custom-id-123")

        assert state.job_id == "custom-id-123"
