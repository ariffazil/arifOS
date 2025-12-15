"""
test_pipeline_with_memory.py - L7 Memory Pipeline Integration Tests

Integration tests verifying:
1. L7 Memory recall at 111_SENSE stage
2. L7 Memory store at 999_SEAL stage with EUREKA Sieve
3. Fail-open behavior (pipeline continues when L7 unavailable)

Author: arifOS Project
Version: v38.2-alpha
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from arifos_core.pipeline import (
    Pipeline,
    PipelineState,
    StakesClass,
    stage_111_sense,
    stage_999_seal,
    is_l7_enabled,
)
from arifos_core.memory.memory import (
    Memory,
    RecallResult,
    StoreAtSealResult,
    SieveResult,
)
from arifos_core.memory.mem0_client import (
    Mem0Client,
    Mem0Config,
    MemoryHit,
    SearchResult,
    StoreResult,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_mem0_client():
    """Create a mock Mem0 client."""
    client = Mock(spec=Mem0Client)
    client.is_available = True
    client.initialization_error = None
    client.config = Mem0Config(enabled=True)
    return client


@pytest.fixture
def mock_memory_with_hits():
    """Create a mock Memory with recall hits."""
    memory = Mock(spec=Memory)
    memory.is_available = True

    # Mock recall result with memories
    recall_result = RecallResult(
        memories=[
            MemoryHit(
                memory_id="mem-1",
                content="User previously asked about governance",
                metadata={"topic": "governance"},
                score=0.82,
                user_id="test-user",
                timestamp="2025-01-01T00:00:00Z",
            ),
            MemoryHit(
                memory_id="mem-2",
                content="User prefers technical explanations",
                metadata={"topic": "preferences"},
                score=0.75,
                user_id="test-user",
                timestamp="2025-01-02T00:00:00Z",
            ),
        ],
        total_found=2,
        l7_available=True,
    )

    return recall_result


@pytest.fixture
def basic_pipeline_state():
    """Create a basic pipeline state for testing."""
    return PipelineState(
        query="What is Amanah?",
        job_id="test-job-1",
        l7_user_id="test-user-123",
    )


# =============================================================================
# TEST: L7 RECALL AT 111_SENSE
# =============================================================================

class TestL7RecallAt111Sense:
    """Integration tests for L7 Memory recall at 111_SENSE stage."""

    def test_recall_injects_memories_into_context_blocks(self, basic_pipeline_state, mock_memory_with_hits):
        """Test that recalled memories are injected into context_blocks."""
        # v42: patch in system.pipeline where the actual implementation lives
        with patch('arifos_core.system.pipeline.is_l7_enabled', return_value=True):
            with patch('arifos_core.system.pipeline._l7_recall', return_value=mock_memory_with_hits):
                state = stage_111_sense(basic_pipeline_state)

                # Check that memories were injected
                l7_blocks = [b for b in state.context_blocks if b.get("type") == "l7_memory"]
                assert len(l7_blocks) == 2

                # Verify first memory content
                assert l7_blocks[0]["text"] == "User previously asked about governance"
                assert l7_blocks[0]["score"] == 0.82
                assert "caveat" in l7_blocks[0]

    def test_recall_stores_result_in_state(self, basic_pipeline_state, mock_memory_with_hits):
        """Test that recall result is stored in state.l7_recall_result."""
        # v42: patch in system.pipeline where the actual implementation lives
        with patch('arifos_core.system.pipeline.is_l7_enabled', return_value=True):
            with patch('arifos_core.system.pipeline._l7_recall', return_value=mock_memory_with_hits):
                state = stage_111_sense(basic_pipeline_state)

                assert state.l7_recall_result is not None
                assert state.l7_recall_result.has_memories is True
                assert len(state.l7_recall_result.memories) == 2

    def test_recall_requires_user_id(self):
        """Test that recall is skipped without user_id."""
        state = PipelineState(
            query="Test query",
            job_id="test-1",
            l7_user_id="",  # Empty user_id
        )

        # v42: patch in system.pipeline where the actual implementation lives
        with patch('arifos_core.system.pipeline.is_l7_enabled', return_value=True):
            state = stage_111_sense(state)

            # No recall should happen
            l7_blocks = [b for b in state.context_blocks if b.get("type") == "l7_memory"]
            assert len(l7_blocks) == 0


# =============================================================================
# TEST: L7 STORE AT 999_SEAL
# =============================================================================

class TestL7StoreAt999Seal:
    """Integration tests for L7 Memory store at 999_SEAL stage."""

    def test_seal_verdict_triggers_store(self):
        """Test that SEAL verdict triggers L7 storage."""
        state = PipelineState(
            query="Test query",
            job_id="test-1",
            l7_user_id="test-user",
            verdict="SEAL",
            draft_response="This is the response",
        )

        mock_store_result = StoreAtSealResult(
            success=True,
            sieve_result=SieveResult(
                should_store=True,
                verdict="SEAL",
                ttl_days=None,
                reason="SEAL stored forever",
            ),
            memory_id="new-mem-123",
        )

        # v42: patch in system.pipeline where the actual implementation lives
        with patch('arifos_core.system.pipeline.is_l7_enabled', return_value=True):
            with patch('arifos_core.system.pipeline._l7_store', return_value=mock_store_result):
                state = stage_999_seal(state)

                assert state.l7_store_result is not None
                assert state.l7_store_result.success is True

    def test_void_verdict_blocked_by_sieve(self):
        """Test that VOID verdict is blocked by EUREKA Sieve."""
        state = PipelineState(
            query="Test query",
            job_id="test-1",
            l7_user_id="test-user",
            verdict="VOID",
            draft_response="",
        )

        mock_store_result = StoreAtSealResult(
            success=False,
            sieve_result=SieveResult(
                should_store=False,
                verdict="VOID",
                ttl_days=0,
                reason="VOID is discarded by EUREKA Sieve",
            ),
            error="Verdict VOID is discarded by EUREKA Sieve",
        )

        # v42: patch in system.pipeline where the actual implementation lives
        with patch('arifos_core.system.pipeline.is_l7_enabled', return_value=True):
            with patch('arifos_core.system.pipeline._l7_store', return_value=mock_store_result):
                state = stage_999_seal(state)

                # VOID is blocked - store_result should show failure
                if state.l7_store_result:
                    assert state.l7_store_result.success is False
                    assert state.l7_store_result.sieve_result.should_store is False

    def test_store_includes_metadata(self):
        """Test that store includes job metadata."""
        state = PipelineState(
            query="What is Amanah?",
            job_id="test-job-123",
            l7_user_id="test-user",
            verdict="SEAL",
            draft_response="Amanah means trust",
            stakes_class=StakesClass.CLASS_A,
            stage_trace=["000_VOID", "111_SENSE", "888_JUDGE", "999_SEAL"],
        )

        captured_metadata = {}

        def capture_store(content, user_id, verdict, metadata=None):
            captured_metadata.update(metadata or {})
            return StoreAtSealResult(
                success=True,
                sieve_result=SieveResult(
                    should_store=True,
                    verdict="SEAL",
                    ttl_days=None,
                    reason="stored",
                ),
                memory_id="test",
            )

        # v42: patch in system.pipeline where the actual implementation lives
        with patch('arifos_core.system.pipeline.is_l7_enabled', return_value=True):
            with patch('arifos_core.system.pipeline._l7_store', side_effect=capture_store):
                stage_999_seal(state)

                assert captured_metadata.get("job_id") == "test-job-123"
                assert captured_metadata.get("stakes_class") == "A"


# =============================================================================
# TEST: FAIL-OPEN BEHAVIOR
# =============================================================================

class TestFailOpenBehavior:
    """Integration tests for fail-open behavior when L7 is unavailable."""

    def test_pipeline_continues_when_l7_disabled(self):
        """Test that pipeline continues when L7 is disabled."""
        state = PipelineState(
            query="Test query",
            job_id="test-1",
            l7_user_id="test-user",
        )

        # v42: patch in system.pipeline where the actual implementation lives
        with patch('arifos_core.system.pipeline.is_l7_enabled', return_value=False):
            # Pipeline should not throw error
            state = stage_111_sense(state)

            # No L7 blocks should be added
            l7_blocks = [b for b in state.context_blocks if b.get("type") == "l7_memory"]
            assert len(l7_blocks) == 0

            # Recall result should be None
            assert state.l7_recall_result is None

    def test_pipeline_continues_when_recall_throws(self, basic_pipeline_state):
        """Test that pipeline continues when recall throws exception."""
        def raise_error(*args, **kwargs):
            raise Exception("Connection failed")

        # v42: patch in system.pipeline where the actual implementation lives
        with patch('arifos_core.system.pipeline.is_l7_enabled', return_value=True):
            with patch('arifos_core.system.pipeline._l7_recall', side_effect=raise_error):
                # Should not throw - fail-open
                state = stage_111_sense(basic_pipeline_state)

                # Pipeline should continue normally
                assert state.current_stage == "111"

    def test_pipeline_continues_when_store_throws(self):
        """Test that pipeline continues when store throws exception."""
        state = PipelineState(
            query="Test query",
            job_id="test-1",
            l7_user_id="test-user",
            verdict="SEAL",
            draft_response="response",
        )

        def raise_error(*args, **kwargs):
            raise Exception("Storage failed")

        # v42: patch in system.pipeline where the actual implementation lives
        with patch('arifos_core.system.pipeline.is_l7_enabled', return_value=True):
            with patch('arifos_core.system.pipeline._l7_store', side_effect=raise_error):
                # Should not throw - fail-open
                state = stage_999_seal(state)

                # Pipeline should complete normally
                assert state.current_stage == "999"
                assert state.raw_response is not None


# =============================================================================
# TEST: FULL PIPELINE INTEGRATION
# =============================================================================

class TestFullPipelineIntegration:
    """Full pipeline integration tests with L7 Memory."""

    def test_full_pipeline_with_user_id(self):
        """Test full pipeline run with user_id parameter."""
        pipeline = Pipeline()

        # Run pipeline with user_id
        state = pipeline.run(
            query="What is the capital of France?",
            user_id="integration-test-user",
        )

        # Verify user_id was set
        assert state.l7_user_id == "integration-test-user"

        # Pipeline should complete
        assert "999_SEAL" in state.stage_trace
        assert state.verdict is not None

    def test_full_pipeline_without_user_id(self):
        """Test full pipeline run without user_id (L7 skipped)."""
        pipeline = Pipeline()

        # Run pipeline without user_id
        state = pipeline.run(
            query="What is 2 + 2?",
        )

        # user_id should be empty
        assert state.l7_user_id == ""

        # Pipeline should still complete
        assert "999_SEAL" in state.stage_trace
        assert state.verdict is not None


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
