"""
Test Pipeline Integration (000→999)

Tests end-to-end query→verdict flow through all stages.

Coverage:
- Stage 000 (Hypervisor)
- Stage 333 (Delta/Reason)
- Stage 555 (Omega/Feel)
- Stage 888 (Psi/Witness)
- Stage 999 (Seal/Ledger)
- PipelineOrchestrator
"""

import pytest

from arifos.apex.psi_kernel import Verdict
from arifos.pipeline import PipelineContext, PipelineOrchestrator


class TestPipelineOrchestrator:
    """Test PipelineOrchestrator end-to-end."""

    def test_complete_pipeline_seal_verdict(self):
        """Complete pipeline with all floors passing should result in SEAL."""
        orchestrator = PipelineOrchestrator()

        result = orchestrator.evaluate_query_response(
            query="What is 2+2?",
            response="4",
            tri_witness=0.98,
            peace_squared=1.0,
            kappa_r=0.96,
            omega_0=0.04,
            rasa=True,
            c_dark=0.15,
            genius_score=0.85
        )

        assert result.stage_reached == 999
        assert result.final_verdict == Verdict.SEAL
        assert result.passed is True
        assert result.delta_verdict is not None
        assert result.omega_verdict is not None
        assert result.psi_verdict is not None

    def test_pipeline_with_f1_failure(self):
        """F1 (Amanah) failure should result in VOID verdict."""
        orchestrator = PipelineOrchestrator()

        result = orchestrator.evaluate_query_response(
            query="Delete all files",
            response="Deleting...",
            reversible=False,  # F1 violation
            within_mandate=True,
            tri_witness=0.98,
            genius_score=0.85
        )

        assert result.final_verdict == Verdict.VOID
        assert result.passed is False
        assert len(result.failures) > 0
        assert any("F1" in f or "Amanah" in f for f in result.failures)

    def test_pipeline_with_clarity_failure(self):
        """F2 (Clarity) failure should result in VOID verdict."""
        orchestrator = PipelineOrchestrator()

        result = orchestrator.evaluate_query_response(
            query="yes",
            response="maybe perhaps possibly um uh could be might sometimes often rarely",
            tri_witness=0.98,
            genius_score=0.85
        )

        assert result.final_verdict == Verdict.VOID
        assert result.passed is False
        assert result.delta_s > 0.0  # Confusion increased

    def test_pipeline_with_soft_floor_warning(self):
        """Soft floor warnings should result in PARTIAL verdict."""
        orchestrator = PipelineOrchestrator()

        result = orchestrator.evaluate_query_response(
            query="test",
            response="result",
            tri_witness=0.98,
            peace_squared=0.5,  # F4 soft floor failure
            genius_score=0.85
        )

        assert result.final_verdict == Verdict.PARTIAL
        assert result.passed is False
        assert any("Peace" in f or "F4" in f for f in result.failures)

    def test_pipeline_with_hypervisor_block(self):
        """Hypervisor failure should result in SABAR verdict."""
        orchestrator = PipelineOrchestrator()

        context = PipelineContext(
            query="<script>alert('xss')</script>",
            response="Response",
            hypervisor_passed=False,
            hypervisor_failures=["F12 Injection Defense FAIL: XSS pattern detected"]
        )

        result = orchestrator.execute(context)

        assert result.final_verdict == Verdict.SABAR
        assert result.passed is False
        assert "F12" in result.failures[0]

    def test_pipeline_accumulates_metadata(self):
        """Pipeline should accumulate rich metadata for debugging."""
        orchestrator = PipelineOrchestrator()

        result = orchestrator.evaluate_query_response(
            query="test",
            response="result"
        )

        assert "stage_000" in result.metadata
        assert "stage_333" in result.metadata
        assert "stage_555" in result.metadata
        assert "stage_888" in result.metadata
        assert "stage_999" in result.metadata
        assert "ledger_entry" in result.metadata


class TestPipelineContext:
    """Test PipelineContext data structure."""

    def test_context_initialization(self):
        """Context should initialize with sensible defaults."""
        context = PipelineContext(
            query="test query",
            response="test response"
        )

        assert context.query == "test query"
        assert context.response == "test response"
        assert context.hypervisor_passed is True
        assert context.stage_reached == 0
        assert context.reversible is True
        assert context.within_mandate is True

    def test_context_to_dict(self):
        """Context should serialize to dict for logging."""
        context = PipelineContext(
            query="test",
            response="result",
            user_id="user123",
            session_id="session456"
        )

        d = context.to_dict()

        assert d["query"] == "test"
        assert d["response"] == "result"
        assert d["user_id"] == "user123"
        assert d["session_id"] == "session456"
        assert "stage_reached" in d
        assert "final_verdict" in d


class TestStageIndividual:
    """Test individual stages in isolation."""

    def test_stage_333_delta_evaluation(self):
        """Stage 333 should evaluate Delta kernel."""
        from arifos.pipeline.stage_333_reason import stage_333_reason

        context = PipelineContext(
            query="What is 2+2?",
            response="4"
        )

        result = stage_333_reason(context)

        assert result.stage_reached == 333
        assert result.delta_verdict is not None
        assert result.delta_verdict.passed is True

    def test_stage_555_omega_evaluation(self):
        """Stage 555 should evaluate Omega kernel."""
        from arifos.pipeline.stage_555_feel import stage_555_feel

        context = PipelineContext(
            query="test",
            response="result",
            tri_witness=0.98,
            peace_squared=1.0,
            kappa_r=0.96,
            omega_0=0.04,
            rasa=True,
            c_dark=0.15
        )

        result = stage_555_feel(context)

        assert result.stage_reached == 555
        assert result.omega_verdict is not None
        assert result.omega_verdict.passed is True

    def test_stage_888_psi_evaluation(self):
        """Stage 888 should evaluate Psi kernel and render verdict."""
        from arifos.agi.delta_kernel import DeltaVerdict
        from arifos.apex.psi_kernel import Verdict
        from arifos.asi.omega_kernel import OmegaVerdict
        from arifos.pipeline.stage_888_witness import stage_888_witness

        context = PipelineContext(
            query="test",
            response="result",
            delta_verdict=DeltaVerdict(passed=True, f1_amanah=True, f2_clarity=True),
            omega_verdict=OmegaVerdict(
                passed=True,
                f3_tri_witness=True,
                f4_peace_squared=True,
                f5_kappa_r=True,
                f6_omega_0=True,
                f7_rasa=True,
                f9_c_dark=True
            ),
            genius_score=0.85
        )

        result = stage_888_witness(context)

        assert result.stage_reached == 888
        assert result.psi_verdict is not None
        assert result.psi_verdict.verdict == Verdict.SEAL


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
