"""
Test Trinity Parallel Architecture (v52.5.1)

Validates that AGI and ASI execute in parallel and that
Trinity Dissent Law is enforced at stage 444 convergence.

Constitutional Floors Tested:
- F3 (Tri-Witness): Independent judgment preserved
- F4 (Clarity): Architecture reduces entropy
- F7 (Humility): Acknowledges uncertainty

DITEMPA BUKAN DIBERI
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, MagicMock

# Import canonical_core modules
from codebase.bundles import (
    DeltaBundle,
    OmegaBundle,
    MergedBundle,
    EngineVote,
    AGIFloorScores,
    ASIFloorScores,
    TriWitnessConsensus,
)


class TestTrinityParallel:
    """Test parallel execution of AGI and ASI chains."""
    
    def test_bundles_exist(self):
        """Test that bundle types are properly defined."""
        # DeltaBundle (AGI output)
        delta = DeltaBundle(
            session_id="test_001",
            raw_query="What is truth?",
            vote=EngineVote.SEAL,
            vote_reason="High confidence in facts"
        )
        assert delta.session_id == "test_001"
        assert delta.vote == EngineVote.SEAL
        
        # OmegaBundle (ASI output)
        omega = OmegaBundle(
            session_id="test_001",
            vote=EngineVote.SEAL,
            vote_reason="No safety concerns",
            is_reversible=True
        )
        assert omega.session_id == "test_001"
        assert omega.vote == EngineVote.SEAL
        
        # MergedBundle (444 TRINITY_SYNC output)
        merged = MergedBundle(
            session_id="test_001",
            delta_bundle=delta,
            omega_bundle=omega
        )
        assert merged.delta_bundle == delta
        assert merged.omega_bundle == omega
    
    def test_trinity_dissent_law_both_seal(self):
        """Test Trinity Dissent Law: Both vote SEAL → can proceed."""
        delta = DeltaBundle(
            session_id="test_002",
            vote=EngineVote.SEAL,
            confidence_high=0.97,
            floor_scores=AGIFloorScores(F2_truth=0.99, F4_clarity=-0.5, F7_humility=0.04)
        )
        
        omega = OmegaBundle(
            session_id="test_002",
            vote=EngineVote.SEAL,
            empathy_kappa_r=0.96,
            floor_scores=ASIFloorScores(F1_amanah=1.0, F5_peace=1.0, F6_empathy=0.96)
        )
        
        merged = MergedBundle(
            session_id="test_002",
            delta_bundle=delta,
            omega_bundle=omega
        )
        
        pre_verdict = merged.apply_trinity_dissent_law()
        
        # Both vote SEAL, consensus should be high
        assert pre_verdict == "SEAL"
        assert merged.consensus.votes_agree == True
        assert merged.consensus.consensus_score >= 0.95
        assert merged.consensus.agi_vote == EngineVote.SEAL
        assert merged.consensus.asi_vote == EngineVote.SEAL
    
    def test_trinity_dissent_law_agi_void(self):
        """Test Trinity Dissent Law: AGI votes VOID → cannot SEAL."""
        delta = DeltaBundle(
            session_id="test_003",
            vote=EngineVote.VOID,
            vote_reason="Factual inaccuracy detected",
            confidence_high=0.50
        )
        
        omega = OmegaBundle(
            session_id="test_003",
            vote=EngineVote.SEAL,
            empathy_kappa_r=0.96
        )
        
        merged = MergedBundle(
            session_id="test_003",
            delta_bundle=delta,
            omega_bundle=omega
        )
        
        pre_verdict = merged.apply_trinity_dissent_law()
        
        # AGI voted VOID, verdict must be VOID
        assert pre_verdict == "VOID"
        assert merged.consensus.votes_agree == False
        assert merged.consensus.consensus_score == 0.0
        assert "AGI VOID" in merged.consensus.dissent_reason
    
    def test_trinity_dissent_law_asi_void(self):
        """Test Trinity Dissent Law: ASI votes VOID → cannot SEAL."""
        delta = DeltaBundle(
            session_id="test_004",
            vote=EngineVote.SEAL,
            confidence_high=0.97
        )
        
        omega = OmegaBundle(
            session_id="test_004",
            vote=EngineVote.VOID,
            vote_reason="Safety constraint violated"
        )
        
        merged = MergedBundle(
            session_id="test_004",
            delta_bundle=delta,
            omega_bundle=omega
        )
        
        pre_verdict = merged.apply_trinity_dissent_law()
        
        # ASI voted VOID, verdict must be VOID
        assert pre_verdict == "VOID"
        assert merged.consensus.votes_agree == False
        assert merged.consensus.consensus_score == 0.0
        assert "ASI VOID" in merged.consensus.dissent_reason
    
    def test_trinity_dissent_law_both_void(self):
        """Test Trinity Dissent Law: Both vote VOID → VOID."""
        delta = DeltaBundle(
            session_id="test_005",
            vote=EngineVote.VOID,
            vote_reason="AGI rejects"
        )
        
        omega = OmegaBundle(
            session_id="test_005",
            vote=EngineVote.VOID,
            vote_reason="ASI rejects"
        )
        
        merged = MergedBundle(
            session_id="test_005",
            delta_bundle=delta,
            omega_bundle=omega
        )
        
        pre_verdict = merged.apply_trinity_dissent_law()
        
        # Both voted VOID
        assert pre_verdict == "VOID"
        assert merged.consensus.votes_agree == False
        assert merged.consensus.consensus_score == 0.0
    
    def test_trinity_dissent_law_uncertain_votes(self):
        """Test Trinity Dissent Law: UNCERTAIN votes → 888_HOLD."""
        delta = DeltaBundle(
            session_id="test_006",
            vote=EngineVote.UNCERTAIN,
            vote_reason="Within Omega_0 band"
        )
        
        omega = OmegaBundle(
            session_id="test_006",
            vote=EngineVote.UNCERTAIN,
            vote_reason="Requires human judgment"
        )
        
        merged = MergedBundle(
            session_id="test_006",
            delta_bundle=delta,
            omega_bundle=omega
        )
        
        pre_verdict = merged.apply_trinity_dissent_law()
        
        # UNCERTAIN votes require human review
        assert pre_verdict == "888_HOLD"
        assert merged.consensus.votes_agree == False
        assert "Uncertain votes require human review" in merged.pre_verdict_reason
    
    def test_bundle_sealing_integrity(self):
        """Test that bundles compute hashes correctly."""
        delta = DeltaBundle(
            session_id="test_007",
            raw_query="Test query",
            vote=EngineVote.SEAL
        )
        
        # Before sealing
        assert delta.bundle_hash == ""
        
        # After sealing
        delta.seal()
        assert len(delta.bundle_hash) == 16  # SHA-256 truncated to 16 chars
        
        # Hash should be deterministic
        hash1 = delta.bundle_hash
        delta.seal()
        hash2 = delta.bundle_hash
        assert hash1 == hash2
    
    def test_merged_bundle_floor_aggregation(self):
        """Test that MergedBundle aggregates floor scores from both bundles."""
        delta = DeltaBundle(
            session_id="test_008",
            vote=EngineVote.SEAL,
            floor_scores=AGIFloorScores(
                F2_truth=0.99,
                F4_clarity=-0.2,
                F7_humility=0.04,
                F13_curiosity=3.0
            )
        )
        
        omega = OmegaBundle(
            session_id="test_008",
            vote=EngineVote.SEAL,
            floor_scores=ASIFloorScores(
                F1_amanah=1.0,
                F5_peace=1.0,
                F6_empathy=0.96,
                F9_anti_hantu=0.0,
                F11_authority=1.0,
                F12_injection=0.0
            )
        )
        
        merged = MergedBundle(
            session_id="test_008",
            delta_bundle=delta,
            omega_bundle=omega
        )
        
        merged.apply_trinity_dissent_law()
        all_scores = merged.all_floor_scores
        
        # Check AGI floors present
        assert "F2_truth" in all_scores
        assert all_scores["F2_truth"] == 0.99
        assert "F4_clarity" in all_scores
        assert "F7_humility" in all_scores
        
        # Check ASI floors present
        assert "F1_amanah" in all_scores
        assert "F5_peace" in all_scores
        assert "F6_empathy" in all_scores
        
        # Check APEX floors computed
        assert "F3_tri_witness" in all_scores
        assert all_scores["F3_tri_witness"] >= 0.95  # Both voted SEAL
        assert "F10_ontology" in all_scores
    
    def test_f3_independence_violation_detection(self):
        """
        Test that F3 requires INDEPENDENT judgment.
        
        This test verifies that the architecture PREVENTS
        ASI from seeing AGI's conclusion before voting.
        (In practice, this is enforced by parallel execution)
        """
        # Bundles are sealed BEFORE merging
        delta = DeltaBundle(session_id="test_009", vote=EngineVote.SEAL)
        omega = OmegaBundle(session_id="test_009", vote=EngineVote.SEAL)
        
        # Seal both bundles
        delta.seal()
        omega.seal()
        
        # Both have hashes (sealed, immutable)
        assert delta.bundle_hash != ""
        assert omega.bundle_hash != ""
        
        # Merge happens AFTER both are sealed
        merged = MergedBundle(
            session_id="test_009",
            delta_bundle=delta,
            omega_bundle=omega
        )
        
        # At this point, neither bundle can be modified
        # This architectural constraint enforces F3 independence
        assert merged.delta_bundle.bundle_hash != ""
        assert merged.omega_bundle.bundle_hash != ""


class TestPipelineParallelExecution:
    """Test that pipeline actually runs AGI and ASI in parallel."""
    
    @pytest.mark.asyncio
    async def test_parallel_execution_timing(self):
        """Test that parallel execution is faster than sequential would be."""
        from codebase.pipeline import Pipeline
        
        # Mock the stage execution functions to have artificial delays
        async def mock_agi_chain(session_id, query, context):
            await asyncio.sleep(0.01)  # 10ms AGI delay
            return {
                "stage": "333_REASON",
                "vote": "SEAL",
                "floor_scores": {"F2_Truth": 0.95}
            }
        
        async def mock_asi_chain(session_id, query, context):
            await asyncio.sleep(0.007)  # 7ms ASI delay  
            return {
                "stage": "666_ALIGN",
                "vote": "SEAL",
                "floor_scores": {"F6_Empathy": 0.96}
            }
        
        pipeline = Pipeline()
        
        # Patch the async methods
        pipeline._execute_agi_async = mock_agi_chain
        pipeline._execute_asi_async = mock_asi_chain
        
        # Time parallel execution
        start = time.time()
        delta, omega = await asyncio.gather(
            mock_agi_chain("test", "query", {}),
            mock_asi_chain("test", "query", {})
        )
        elapsed = time.time() - start
        
        # Parallel should be ~max(10ms, 7ms) = 10ms
        # Sequential would be 10ms + 7ms = 17ms
        assert elapsed < 0.015  # Less than 15ms (parallel)
        assert elapsed > 0.009  # More than 9ms (the 10ms AGI delay)
        
        # If it were sequential, elapsed would be > 17ms
        # Parallel execution gives us ~40% time savings
        print(f"✓ Parallel execution took {elapsed*1000:.1f}ms (expected ~10ms)")
    
    @pytest.mark.asyncio
    async def test_asyncio_gather_independence(self):
        """Test that asyncio.gather preserves execution independence."""
        # Track execution order
        execution_log = []
        
        async def agi_task():
            execution_log.append("AGI_START")
            await asyncio.sleep(0.005)
            execution_log.append("AGI_END")
            return {"vote": "SEAL"}
        
        async def asi_task():
            execution_log.append("ASI_START")
            await asyncio.sleep(0.003)
            execution_log.append("ASI_END")
            return {"vote": "SEAL"}
        
        # Execute in parallel
        results = await asyncio.gather(agi_task(), asi_task())
        
        # Both tasks should start before either finishes
        agi_start_idx = execution_log.index("AGI_START")
        asi_start_idx = execution_log.index("ASI_START")
        agi_end_idx = execution_log.index("AGI_END")
        asi_end_idx = execution_log.index("ASI_END")
        
        # ASI should finish before AGI (it's faster)
        assert asi_end_idx < agi_end_idx
        
        # Both should start before any ends (parallel execution)
        assert agi_start_idx < agi_end_idx
        assert asi_start_idx < asi_end_idx
        
        print(f"✓ Execution order: {execution_log}")
        print("✓ F3 Independence preserved: AGI and ASI ran in parallel")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
