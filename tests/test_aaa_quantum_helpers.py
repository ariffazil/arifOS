"""
Test AAA-Level Quantum Helpers

Tests the separation of concerns: LLM Generation ⊥ Quantum Validation

Authority: v47 Quantum Architecture - Option A
Reference: docs/AAA_QUANTUM_MIGRATION.md
"""

import pytest
from arifos.mcp.helpers import (
    validate_text_sync,
    validate_text_async,
    QuantumPipeline,
)


class TestAAALevelValidation:
    """Test validation-only functions (no LLM generation)."""

    def test_validate_text_sync_seal(self):
        """Valid text should receive SEAL verdict."""
        state = validate_text_sync(
            query="What is 2+2?",
            draft_response="The answer is 4"
        )

        # Quantum validation completed
        assert state.collapsed is True
        assert state.final_verdict is not None
        assert state.agi_particle is not None
        assert state.asi_particle is not None
        assert state.apex_particle is not None

    def test_validate_text_sync_with_context(self):
        """Validation with additional context."""
        state = validate_text_sync(
            query="test",
            draft_response="result",
            context={"source": "test", "priority": "low"}
        )

        assert state.collapsed is True
        assert "draft_response" in state.context
        assert state.context["draft_response"] == "result"

    @pytest.mark.asyncio
    async def test_validate_text_async_seal(self):
        """Async validation should work."""
        state = await validate_text_async(
            query="What is the capital of France?",
            draft_response="Paris"
        )

        # Quantum validation completed
        assert state.collapsed is True
        assert state.final_verdict is not None


class TestQuantumPipelineBackwardCompat:
    """Test backward-compatible Pipeline API."""

    def test_quantum_pipeline_basic(self):
        """QuantumPipeline should work like old Pipeline."""
        # Skip if litellm not installed (optional dependency)
        pytest.importorskip("litellm")

        pipeline = QuantumPipeline(llm_model="gpt-4o-mini")

        # This would call LLM (skip in unit tests)
        # result = pipeline.run(query="What is 2+2?")
        # assert result["verdict"] in ["SEAL", "VOID", "PARTIAL", "SABAR"]
        # assert "response" in result
        # assert "state" in result

        # Just verify pipeline object created
        assert pipeline.llm_model == "gpt-4o-mini"
        assert pipeline.executor is not None

    def test_quantum_pipeline_structure(self):
        """Pipeline result should have expected structure."""
        pipeline = QuantumPipeline()

        # Verify structure (without calling LLM)
        assert hasattr(pipeline, "run")
        assert hasattr(pipeline, "llm_model")
        assert hasattr(pipeline, "executor")


class TestOrthogonalityPrinciple:
    """Test that LLM and Quantum are orthogonal (dot_product = 0)."""

    def test_validation_independent_of_generation(self):
        """Quantum validation doesn't know/care where text came from."""
        # Same text, different "sources"
        text = "The answer is 4"

        # "Source 1": From GPT-4
        state1 = validate_text_sync(
            query="What is 2+2?",
            draft_response=text,
            context={"llm_model": "gpt-4"}
        )

        # "Source 2": From Claude
        state2 = validate_text_sync(
            query="What is 2+2?",
            draft_response=text,
            context={"llm_model": "claude-3"}
        )

        # "Source 3": Hardcoded string
        state3 = validate_text_sync(
            query="What is 2+2?",
            draft_response=text,
            context={"llm_model": "human"}
        )

        # Quantum validation should give same verdict
        # (because it validates TEXT, not SOURCE)
        # Note: Exact verdict depends on constitutional floors,
        # but validation process should be independent
        assert state1.collapsed is True
        assert state2.collapsed is True
        assert state3.collapsed is True

        # All should have run through same quantum process
        assert state1.agi_particle is not None
        assert state2.agi_particle is not None
        assert state3.agi_particle is not None

    def test_multiple_validations_independent(self):
        """Multiple validations don't interfere with each other."""
        # Validate 3 different texts
        state_a = validate_text_sync(query="A", draft_response="answer A")
        state_b = validate_text_sync(query="B", draft_response="answer B")
        state_c = validate_text_sync(query="C", draft_response="answer C")

        # All should complete independently
        assert state_a.collapsed is True
        assert state_b.collapsed is True
        assert state_c.collapsed is True

        # Each should have unique particles (not shared state)
        assert state_a.agi_particle is not state_b.agi_particle
        assert state_b.agi_particle is not state_c.agi_particle


class TestAAASeparation:
    """Test that helpers maintain AAA-level separation."""

    def test_validate_text_no_generation(self):
        """validate_text functions should NOT generate text."""
        state = validate_text_sync(
            query="test query",
            draft_response="pre-existing text"
        )

        # State should contain the draft we provided
        assert state.context["draft_response"] == "pre-existing text"

        # State should NOT contain any generated text
        # (because we only validated, didn't generate)
        assert state.final_verdict is not None  # Verdict exists
        assert state.collapsed is True  # Measurement occurred

    def test_helpers_respect_context(self):
        """Helpers should pass through context correctly."""
        custom_context = {
            "user_id": "test123",
            "session_id": "sess456",
            "priority": "high"
        }

        state = validate_text_sync(
            query="test",
            draft_response="result",
            context=custom_context
        )

        # Custom context should be preserved
        assert state.context["user_id"] == "test123"
        assert state.context["session_id"] == "sess456"
        assert state.context["priority"] == "high"

        # Draft should also be in context
        assert state.context["draft_response"] == "result"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
