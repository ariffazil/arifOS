# -*- coding: utf-8 -*-
"""
v49.1 Stabilization Tests

Tests for the v49.1 stabilization fixes:
- BLOCKER 1: Parallel Pipeline wiring
- BLOCKER 2: Phoenix-72 Cooling enforcement
- HIGH 1: Real zkPC metrics
- HIGH 2: EUREKA Sieve persistence
- HIGH 3: Docker configs (not testable here)

Constitutional Alignment: F2 (Truth) + F4 (Clarity)
Authority: Auditor (Codex)
"""

import asyncio
import json
import pytest
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# =============================================================================
# BLOCKER 1: Parallel Pipeline Tests
# =============================================================================


class TestPipelineConfig:
    """Tests for PipelineConfig dataclass."""

    def test_default_config_sequential(self):
        """Default config should have parallel_mode=False."""
        from arifos.core.orchestrator.pipeline import PipelineConfig

        config = PipelineConfig()
        assert config.parallel_mode is False
        assert config.fallback_on_parallel_error is True
        assert config.parallel_timeout_ms == 250

    def test_parallel_mode_enabled(self):
        """Config with parallel_mode=True."""
        from arifos.core.orchestrator.pipeline import PipelineConfig

        config = PipelineConfig(parallel_mode=True)
        assert config.parallel_mode is True


class TestPipelineParallelMode:
    """Tests for Pipeline parallel mode wiring."""

    def test_pipeline_default_sequential(self):
        """Pipeline defaults to sequential mode."""
        from arifos.core.orchestrator.pipeline import Pipeline

        pipeline = Pipeline()
        assert pipeline.parallel_mode is False

    def test_pipeline_enable_parallel(self):
        """Pipeline.enable_parallel() switches to parallel mode."""
        from arifos.core.orchestrator.pipeline import Pipeline

        pipeline = Pipeline()
        assert pipeline.parallel_mode is False
        pipeline.enable_parallel()
        assert pipeline.parallel_mode is True

    def test_pipeline_disable_parallel(self):
        """Pipeline.disable_parallel() switches back to sequential."""
        from arifos.core.orchestrator.pipeline import Pipeline, PipelineConfig

        config = PipelineConfig(parallel_mode=True)
        pipeline = Pipeline(config=config)
        assert pipeline.parallel_mode is True
        pipeline.disable_parallel()
        assert pipeline.parallel_mode is False

    def test_pipeline_with_config_parallel(self):
        """Pipeline respects config parallel_mode."""
        from arifos.core.orchestrator.pipeline import Pipeline, PipelineConfig

        config = PipelineConfig(parallel_mode=True)
        pipeline = Pipeline(config=config)
        assert pipeline.parallel_mode is True


# =============================================================================
# BLOCKER 2: Phoenix-72 Cooling Tests
# =============================================================================


class TestCoolingTierCalculation:
    """Tests for cooling tier calculation."""

    def test_seal_no_warnings_tier_0(self):
        """SEAL with no warnings = Tier 0 (immediate)."""
        from arifos.core.asi.cooling import calculate_cooling_tier

        tier = calculate_cooling_tier("SEAL", warnings=0)
        assert tier == 0

    def test_seal_one_warning_tier_1(self):
        """SEAL with 1 warning = Tier 1 (42h)."""
        from arifos.core.asi.cooling import calculate_cooling_tier

        tier = calculate_cooling_tier("SEAL", warnings=1)
        assert tier == 1

    def test_seal_multiple_warnings_tier_2(self):
        """SEAL with 2+ warnings = Tier 2 (72h)."""
        from arifos.core.asi.cooling import calculate_cooling_tier

        tier = calculate_cooling_tier("SEAL", warnings=2)
        assert tier == 2

    def test_partial_tier_1_or_2(self):
        """PARTIAL = Tier 1 or 2 based on warnings."""
        from arifos.core.asi.cooling import calculate_cooling_tier

        tier_low = calculate_cooling_tier("PARTIAL", warnings=1)
        tier_high = calculate_cooling_tier("PARTIAL", warnings=3)
        assert tier_low == 1
        assert tier_high == 2

    def test_sabar_tier_2(self):
        """SABAR = Tier 2 (72h)."""
        from arifos.core.asi.cooling import calculate_cooling_tier

        tier = calculate_cooling_tier("SABAR", warnings=0)
        assert tier == 2

    def test_void_tier_3(self):
        """VOID = Tier 3 (168h)."""
        from arifos.core.asi.cooling import calculate_cooling_tier

        tier = calculate_cooling_tier("VOID", warnings=0)
        assert tier == 3

    def test_888_hold_tier_3(self):
        """888_HOLD = Tier 3 (168h)."""
        from arifos.core.asi.cooling import calculate_cooling_tier

        tier = calculate_cooling_tier("888_HOLD", warnings=0)
        assert tier == 3


class TestCoolingEntry:
    """Tests for CoolingEntry dataclass."""

    def test_cooling_entry_creation(self):
        """Test CoolingEntry creation and serialization."""
        from arifos.core.asi.cooling import CoolingEntry, CoolingStatus

        now = datetime.now(timezone.utc)
        entry = CoolingEntry(
            entry_id="phoenix_test_123",
            session_id="sess_123",
            tier=2,
            tier_label="TIER_2_CONSTITUTIONAL",
            cooling_hours=72,
            start_time=now.isoformat(),
            cool_until=(now + timedelta(hours=72)).isoformat(),
            status=CoolingStatus.COOLING.value,
            verdict="PARTIAL",
            floor_scores={"F2_truth": 0.98},
        )

        assert entry.entry_id == "phoenix_test_123"
        assert entry.tier == 2
        assert entry.status == "COOLING"

        # Test serialization
        data = entry.to_dict()
        assert isinstance(data, dict)
        assert data["entry_id"] == "phoenix_test_123"

    def test_cooling_entry_is_expired_tier_0(self):
        """Tier 0 entries are always complete."""
        from arifos.core.asi.cooling import CoolingEntry, CoolingStatus

        now = datetime.now(timezone.utc)
        entry = CoolingEntry(
            entry_id="phoenix_test_123",
            session_id="sess_123",
            tier=0,
            tier_label="TIER_0_IMMEDIATE",
            cooling_hours=0,
            start_time=now.isoformat(),
            cool_until=now.isoformat(),
            status=CoolingStatus.COMPLETE.value,
            verdict="SEAL",
            floor_scores={},
        )

        assert entry.is_cooling_complete() is True


class TestCoolingLedger:
    """Tests for CoolingLedger persistence."""

    def test_ledger_append_and_get(self):
        """Test appending and retrieving cooling entries."""
        from arifos.core.asi.cooling import CoolingEntry, CoolingLedger, CoolingStatus

        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "test_cooling.jsonl"
            ledger = CoolingLedger(ledger_path=ledger_path)

            now = datetime.now(timezone.utc)
            entry = CoolingEntry(
                entry_id="phoenix_test_456",
                session_id="sess_456",
                tier=1,
                tier_label="TIER_1_STANDARD",
                cooling_hours=42,
                start_time=now.isoformat(),
                cool_until=(now + timedelta(hours=42)).isoformat(),
                status=CoolingStatus.COOLING.value,
                verdict="PARTIAL",
                floor_scores={},
            )

            # Append
            success = ledger.append(entry)
            assert success is True

            # Get
            retrieved = ledger.get("phoenix_test_456")
            assert retrieved is not None
            assert retrieved.entry_id == "phoenix_test_456"
            assert retrieved.tier == 1

    def test_ledger_get_by_session(self):
        """Test retrieving entries by session ID."""
        from arifos.core.asi.cooling import CoolingEntry, CoolingLedger, CoolingStatus

        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "test_cooling.jsonl"
            ledger = CoolingLedger(ledger_path=ledger_path)

            now = datetime.now(timezone.utc)

            # Add two entries for same session
            for i in range(2):
                entry = CoolingEntry(
                    entry_id=f"phoenix_test_{i}",
                    session_id="sess_shared",
                    tier=1,
                    tier_label="TIER_1_STANDARD",
                    cooling_hours=42,
                    start_time=now.isoformat(),
                    cool_until=(now + timedelta(hours=42)).isoformat(),
                    status=CoolingStatus.COOLING.value,
                    verdict="PARTIAL",
                    floor_scores={},
                )
                ledger.append(entry)

            # Get by session
            entries = ledger.get_by_session("sess_shared")
            assert len(entries) == 2


@pytest.mark.asyncio
class TestCoolingEngineEnforcement:
    """Tests for CoolingEngine enforcement."""

    async def test_enforce_tier_0_immediate(self):
        """Tier 0 should complete immediately."""
        from arifos.core.asi.cooling import CoolingEngine, CoolingLedger

        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "test_cooling.jsonl"
            ledger = CoolingLedger(ledger_path=ledger_path)
            engine = CoolingEngine(ledger=ledger)

            result = await engine.enforce_tier(
                tier=0,
                session_id="test_sess",
                verdict="SEAL",
            )

            assert result["tier"] == 0
            assert result["status"] == "COMPLETE"
            assert "Immediate release" in result["message"]

    async def test_enforce_tier_1_starts_cooling(self):
        """Tier 1 should start cooling (not block by default)."""
        from arifos.core.asi.cooling import CoolingEngine, CoolingLedger

        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "test_cooling.jsonl"
            ledger = CoolingLedger(ledger_path=ledger_path)
            engine = CoolingEngine(ledger=ledger)

            result = await engine.enforce_tier(
                tier=1,
                session_id="test_sess",
                verdict="PARTIAL",
                block_until_cooled=False,  # Don't actually wait
            )

            assert result["tier"] == 1
            assert result["status"] == "COOLING"
            assert result["cooling_hours"] == 42
            assert "entry_id" in result


# =============================================================================
# HIGH 1: zkPC Metrics Tests
# =============================================================================


class TestZKPCMetrics:
    """Tests for zkPC metrics."""

    def test_zkpc_metrics_validation_stub(self):
        """Stub metrics should fail validation."""
        from arifos.core.apex.governance.zkpc_runtime import ZKPCMetrics

        metrics = ZKPCMetrics(
            delta_s=0.0,
            peace_squared=1.0,
            truth_score=0.99,
            agi_confidence=0.5,
            agi_entropy=0.5,
            agi_curiosity=0.85,
            asi_empathy=0.95,
            asi_peace=1.0,
            asi_humility=0.04,
            tri_witness=0.95,
            genius_score=0.80,
            dark_cleverness=0.15,
            pause_duration_ms=0.0,
            contrast_duration_ms=0.0,
            integrate_duration_ms=0.0,
            cool_duration_ms=0.0,
            total_duration_ms=0.0,
            is_stub=True,
        )

        is_valid, issues = metrics.validate()
        assert is_valid is False
        assert len(issues) > 0
        assert any("stub" in issue.lower() for issue in issues)

    def test_zkpc_metrics_validation_real(self):
        """Real metrics with proper timing should pass validation."""
        from arifos.core.apex.governance.zkpc_runtime import ZKPCMetrics

        metrics = ZKPCMetrics(
            delta_s=-0.05,  # Entropy reduced
            peace_squared=1.2,
            truth_score=0.995,
            agi_confidence=0.85,
            agi_entropy=0.3,
            agi_curiosity=0.9,
            asi_empathy=0.97,
            asi_peace=1.1,
            asi_humility=0.04,
            tri_witness=0.96,
            genius_score=0.88,
            dark_cleverness=0.12,
            pause_duration_ms=5.5,
            contrast_duration_ms=3.2,
            integrate_duration_ms=1.1,
            cool_duration_ms=2.3,
            total_duration_ms=12.1,
            is_stub=False,
        )

        is_valid, issues = metrics.validate()
        assert is_valid is True
        assert len(issues) == 0


class TestZKPCRuntime:
    """Tests for ZKPCRuntime."""

    def test_build_care_scope(self):
        """Test PAUSE phase - build care scope."""
        from arifos.core.apex.governance.zkpc_runtime import ZKPCContext, ZKPCRuntime

        runtime = ZKPCRuntime()
        ctx = ZKPCContext(
            user_query="Test query",
            retrieved_canon=["000_LAW.md"],
            high_stakes=True,
            meta={"session_id": "test_sess"},
        )

        care_scope = runtime.build_care_scope(ctx)

        assert "query_hash" in care_scope
        assert care_scope["stakes_level"] == "HIGH"
        assert care_scope["canon_refs"] == 1
        assert "pause_duration_ms" in care_scope

    def test_compute_metrics_with_real_data(self):
        """Test CONTRAST phase with real floor scores."""
        from arifos.core.apex.governance.zkpc_runtime import ZKPCContext, ZKPCRuntime

        runtime = ZKPCRuntime()
        ctx = ZKPCContext(
            user_query="Test query",
            retrieved_canon=[],
            high_stakes=False,
            meta={"session_id": "test_sess"},
            floor_scores={
                "F2_truth": 0.995,
                "F4_clarity": -0.05,
                "F5_peace": 1.2,
                "F6_empathy": 0.97,
                "F7_humility": 0.04,
                "F8_genius": 0.88,
            },
        )

        # First build care scope to set timing
        runtime.build_care_scope(ctx)

        # Then compute metrics
        metrics = runtime.compute_metrics(ctx)

        assert metrics.is_stub is False
        assert metrics.truth_score == 0.995
        assert metrics.delta_s == -0.05


# =============================================================================
# HIGH 2: EUREKA Sieve Tests
# =============================================================================


class TestEurekaSieveBandAssignment:
    """Tests for EUREKA Sieve band assignment."""

    def test_void_verdict_goes_to_l5(self):
        """VOID verdict should go to L5_VOID."""
        from arifos.core.vault.memory_tower import EurekaSieve

        sieve = EurekaSieve()
        result = sieve.assess_ttl(
            novelty_score=0.9,
            tri_witness_consensus=0.99,
            verdict="VOID",
            constitutional_pass=False,
        )

        assert result["memory_band"] == "L5_VOID"
        assert result["ttl_days"] == 1

    def test_seal_high_consensus_goes_to_l1(self):
        """SEAL with high consensus should go to L1_ARCHIVE."""
        from arifos.core.vault.memory_tower import EurekaSieve

        sieve = EurekaSieve()
        result = sieve.assess_ttl(
            novelty_score=0.5,
            tri_witness_consensus=0.99,
            verdict="SEAL",
            constitutional_pass=True,
        )

        assert result["memory_band"] == "L1_ARCHIVE"
        assert result["ttl_days"] is None  # Permanent

    def test_high_novelty_goes_to_l2(self):
        """High novelty should go to L2_WITNESS."""
        from arifos.core.vault.memory_tower import EurekaSieve

        sieve = EurekaSieve()
        result = sieve.assess_ttl(
            novelty_score=0.85,
            tri_witness_consensus=0.8,
            verdict="PARTIAL",
            constitutional_pass=True,
        )

        assert result["memory_band"] == "L2_WITNESS"
        assert result["ttl_days"] == 90

    def test_standard_goes_to_l4(self):
        """Standard interaction should go to L4_SESSION."""
        from arifos.core.vault.memory_tower import EurekaSieve

        sieve = EurekaSieve()
        result = sieve.assess_ttl(
            novelty_score=0.3,
            tri_witness_consensus=0.8,
            verdict="PARTIAL",
            constitutional_pass=True,
        )

        assert result["memory_band"] == "L4_SESSION"
        assert result["ttl_days"] == 7


class TestEurekaSievePersistence:
    """Tests for EUREKA Sieve persistence."""

    def test_store_and_recall_memory(self):
        """Test storing and recalling memory."""
        from arifos.core.vault.memory_tower import EurekaSieve

        with tempfile.TemporaryDirectory() as tmpdir:
            sieve = EurekaSieve(base_path=Path(tmpdir))

            result = sieve.store_memory(
                session_id="test_sess",
                content="Test content for memory",
                novelty_score=0.7,
                tri_witness_consensus=0.92,
                verdict="SEAL",
                constitutional_pass=True,
            )

            assert result["stored"] is True
            assert "entry_id" in result
            assert result["memory_band"] == "L2_WITNESS"

            # Recall
            entry = sieve.recall_memory(result["entry_id"])
            assert entry is not None
            assert entry.content == "Test content for memory"

    def test_l5_void_not_stored(self):
        """L5_VOID should not store content."""
        from arifos.core.vault.memory_tower import EurekaSieve

        with tempfile.TemporaryDirectory() as tmpdir:
            sieve = EurekaSieve(base_path=Path(tmpdir))

            result = sieve.store_memory(
                session_id="test_sess",
                content="Voided content",
                novelty_score=0.9,
                tri_witness_consensus=0.99,
                verdict="VOID",
                constitutional_pass=False,
            )

            assert result["stored"] is False
            assert "does not store content" in result["reason"]

    def test_memory_stats(self):
        """Test memory statistics."""
        from arifos.core.vault.memory_tower import EurekaSieve

        with tempfile.TemporaryDirectory() as tmpdir:
            sieve = EurekaSieve(base_path=Path(tmpdir))

            # Store a few entries
            sieve.store_memory(
                session_id="test_sess",
                content="Content 1",
                novelty_score=0.7,
                tri_witness_consensus=0.92,
                verdict="SEAL",
                constitutional_pass=True,
            )

            stats = sieve.get_memory_stats()
            assert "bands" in stats
            assert "total_entries" in stats
            assert stats["total_entries"] >= 1


class TestMemoryEntry:
    """Tests for MemoryEntry dataclass."""

    def test_memory_entry_not_expired_permanent(self):
        """Permanent entries should never expire."""
        from arifos.core.vault.memory_tower import MemoryEntry

        entry = MemoryEntry(
            entry_id="mem_test_123",
            session_id="sess_123",
            memory_band="L1_ARCHIVE",
            content_hash="abc123",
            content="Test content",
            timestamp=datetime.now(timezone.utc).isoformat(),
            ttl_days=None,
            expiry="PERMANENT",
            novelty_score=0.8,
            consensus_score=0.99,
            verdict="SEAL",
            metadata={},
        )

        assert entry.is_expired() is False

    def test_memory_entry_expired(self):
        """Test expired entry detection."""
        from arifos.core.vault.memory_tower import MemoryEntry

        past = datetime.now(timezone.utc) - timedelta(days=10)
        entry = MemoryEntry(
            entry_id="mem_test_456",
            session_id="sess_456",
            memory_band="L4_SESSION",
            content_hash="def456",
            content="Old content",
            timestamp=past.isoformat(),
            ttl_days=7,
            expiry=(past + timedelta(days=7)).isoformat(),  # Expired
            novelty_score=0.3,
            consensus_score=0.8,
            verdict="PARTIAL",
            metadata={},
        )

        assert entry.is_expired() is True


# =============================================================================
# Integration Tests
# =============================================================================


class TestV49_1Integration:
    """Integration tests for v49.1 components."""

    def test_zkpc_with_real_cooling(self):
        """Test zkPC with real Phoenix-72 cooling."""
        from arifos.core.apex.governance.zkpc_runtime import ZKPCContext, ZKPCRuntime, ZKPCMetrics

        runtime = ZKPCRuntime()
        ctx = ZKPCContext(
            user_query="What is the meaning of truth?",
            retrieved_canon=["000_LAW.md"],
            high_stakes=False,
            meta={"session_id": "integration_test"},
            floor_scores={
                "F2_truth": 0.995,
                "F4_clarity": -0.02,
                "F5_peace": 1.1,
            },
        )

        receipt = runtime.execute_full_flow(ctx, "Truth is alignment with reality.")

        assert "receipt_id" in receipt
        assert receipt["receipt_data"]["validation"]["is_stub"] is False
        assert "timing" in receipt
        assert receipt["timing"]["total_ms"] > 0


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
