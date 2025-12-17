"""
test_ledger_sanity.py — Cooling Ledger Sanity Tests (v35Ω)

Smoke tests for Cooling Ledger / Vault-999 code path:
1. A typical SEAL decision can be logged with current structures
2. Entry JSON shape aligns with 99_Vault999_Seal_v35Omega.json

These are sanity checks, not comprehensive integration tests.
No new features - just verifying existing structures work.

See: canon/99_Vault999_Seal_v35Omega.json
     arifos_core/memory/cooling_ledger.py
"""

import json
import tempfile
from pathlib import Path

import pytest

from arifos_core.metrics import Metrics
from arifos_core.memory.cooling_ledger import (
    CoolingEntry,
    CoolingMetrics,
    CoolingLedger,
    LedgerConfig,
    append_entry,
    verify_chain,
    log_cooling_entry,
)


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def repo_root() -> Path:
    """Get repository root path."""
    return Path(__file__).parent.parent


@pytest.fixture
def vault999_schema(repo_root) -> dict:
    """Load Vault-999 seal schema."""
    path = repo_root / "archive" / "v35_0_0" / "canon" / "_Vault999_Seal_v35Omega.json"
    assert path.exists(), f"Vault-999 schema not found at {path}"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def temp_ledger_path():
    """Create a temporary ledger file path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "test_ledger.jsonl"


@pytest.fixture
def passing_metrics() -> Metrics:
    """Metrics that pass all floors (SEAL-worthy)."""
    return Metrics(
        truth=0.995,
        delta_s=0.1,
        peace_squared=1.2,
        kappa_r=0.97,
        omega_0=0.04,
        amanah=True,
        tri_witness=0.98,
        rasa=True,
        anti_hantu=True,
    )


# =============================================================================
# TEST 1: SEAL ENTRY CAN BE LOGGED
# =============================================================================

class TestSealEntryCanBeLogged:
    """Verify a typical SEAL decision can be logged."""

    def test_log_cooling_entry_seal(self, temp_ledger_path, passing_metrics):
        """log_cooling_entry works for SEAL verdict."""
        entry = log_cooling_entry(
            job_id="test-seal-001",
            verdict="SEAL",
            metrics=passing_metrics,
            query="What is 2 + 2?",
            candidate_output="The answer is 4.",
            stakes="normal",
            pipeline_path=["000", "111", "222", "333", "444", "555", "666", "777", "888", "999"],
            context_summary="Test SEAL entry",
            ledger_path=temp_ledger_path,
        )

        # Verify entry structure
        assert entry["verdict"] == "SEAL"
        assert entry["job_id"] == "test-seal-001"
        assert "timestamp" in entry
        assert "metrics" in entry
        assert "hash" in entry  # Hash-chain integrity

        # Verify file was written
        assert temp_ledger_path.exists()

    def test_log_cooling_entry_void(self, temp_ledger_path):
        """log_cooling_entry works for VOID verdict."""
        failing_metrics = Metrics(
            truth=0.5,  # Fails F1
            delta_s=-0.1,  # Fails F2
            peace_squared=1.0,
            kappa_r=0.95,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.95,
        )

        entry = log_cooling_entry(
            job_id="test-void-001",
            verdict="VOID",
            metrics=failing_metrics,
            query="Test query",
            candidate_output="Test output",
            stakes="high",
            ledger_path=temp_ledger_path,
        )

        assert entry["verdict"] == "VOID"
        assert len(entry["floor_failures"]) > 0  # Should have failures

    def test_cooling_entry_dataclass(self):
        """CoolingEntry dataclass works correctly."""
        metrics = CoolingMetrics(
            truth=0.99,
            delta_s=0.1,
            peace_squared=1.0,
            kappa_r=0.95,
            omega_0=0.04,
            rasa=True,
            amanah=True,
            tri_witness=0.95,
        )

        entry = CoolingEntry(
            timestamp=1234567890.0,
            query="Test query",
            candidate_output="Test output",
            metrics=metrics,
            verdict="SEAL",
            floor_failures=[],
            sabar_reason=None,
            organs={"WELL": True, "RIF": True, "WEALTH": True},
        )

        # Verify to_json_dict works
        d = entry.to_json_dict()
        assert d["verdict"] == "SEAL"
        assert d["metrics"]["truth"] == 0.99


# =============================================================================
# TEST 2: ENTRY SHAPE ALIGNS WITH VAULT-999 SCHEMA
# =============================================================================

class TestEntryShapeMatchesVault999:
    """Verify entry JSON shape aligns with 99_Vault999_Seal_v35Omega.json."""

    def test_entry_has_required_keys(self, temp_ledger_path, passing_metrics):
        """Entry has keys expected by Vault-999."""
        entry = log_cooling_entry(
            job_id="test-schema-001",
            verdict="SEAL",
            metrics=passing_metrics,
            query="Schema test",
            candidate_output="Schema test output",
            ledger_path=temp_ledger_path,
        )

        # Required keys from v35Ω schema
        required_keys = [
            "timestamp",
            "job_id",
            "verdict",
            "metrics",
            "floor_failures",
        ]

        for key in required_keys:
            assert key in entry, f"Missing required key: {key}"

    def test_metrics_in_entry_match_schema(self, temp_ledger_path, passing_metrics):
        """Metrics in entry have expected structure."""
        entry = log_cooling_entry(
            job_id="test-metrics-001",
            verdict="SEAL",
            metrics=passing_metrics,
            ledger_path=temp_ledger_path,
        )

        entry_metrics = entry["metrics"]

        # Core floor metrics (from Vault-999 constitutional_floors)
        expected_metric_keys = [
            "truth",
            "delta_s",
            "peace_squared",
            "kappa_r",
            "omega_0",
            "amanah",
            "tri_witness",
            "rasa",
            "psi",
        ]

        for key in expected_metric_keys:
            assert key in entry_metrics, f"Missing metric key: {key}"

    def test_vault999_floors_present_in_schema(self, vault999_schema):
        """Vault-999 schema has constitutional floors defined."""
        assert "constitutional_floors" in vault999_schema

        expected_floors = [
            "truth",
            "delta_s",
            "peace_squared",
            "kappa_r",
            "omega_0",
            "amanah",
            "rasa",
            "tri_witness",
            "psi",
        ]

        for floor in expected_floors:
            assert floor in vault999_schema["constitutional_floors"], (
                f"Missing floor in Vault-999 schema: {floor}"
            )

    def test_vault999_pipeline_stages(self, vault999_schema):
        """Vault-999 schema has 000→999 pipeline stages."""
        assert "pipeline" in vault999_schema

        expected_stages = ["000", "111", "222", "333", "444", "555", "666", "777", "888", "999"]
        for stage in expected_stages:
            assert stage in vault999_schema["pipeline"], (
                f"Missing pipeline stage in Vault-999 schema: {stage}"
            )


# =============================================================================
# TEST 3: HASH-CHAIN INTEGRITY
# =============================================================================

class TestHashChainIntegrity:
    """Verify hash-chain integrity functions work."""

    def test_append_and_verify_chain(self, temp_ledger_path):
        """Appending entries creates valid hash chain."""
        # Append first entry
        entry1 = {
            "job_id": "chain-001",
            "verdict": "SEAL",
            "timestamp": "2025-01-01T00:00:00Z",
        }
        append_entry(temp_ledger_path, entry1)

        # Append second entry
        entry2 = {
            "job_id": "chain-002",
            "verdict": "PARTIAL",
            "timestamp": "2025-01-01T00:01:00Z",
        }
        append_entry(temp_ledger_path, entry2)

        # Verify chain
        valid, message = verify_chain(temp_ledger_path)
        assert valid is True, f"Chain verification failed: {message}"

    def test_first_entry_has_null_prev_hash(self, temp_ledger_path):
        """First entry should have prev_hash=null."""
        entry = {"job_id": "first-001", "verdict": "SEAL"}
        append_entry(temp_ledger_path, entry)

        with open(temp_ledger_path, "r") as f:
            line = f.readline()
            parsed = json.loads(line)

        assert parsed["prev_hash"] is None


# =============================================================================
# TEST 4: LEDGER CLASS WORKS
# =============================================================================

class TestCoolingLedgerClass:
    """Verify CoolingLedger class works."""

    def test_ledger_append_and_iter(self, temp_ledger_path):
        """CoolingLedger can append and iterate entries."""
        config = LedgerConfig(ledger_path=temp_ledger_path)
        ledger = CoolingLedger(config)

        metrics = CoolingMetrics(
            truth=0.99,
            delta_s=0.1,
            peace_squared=1.0,
            kappa_r=0.95,
            omega_0=0.04,
            rasa=True,
            amanah=True,
            tri_witness=0.95,
        )

        entry = CoolingEntry(
            timestamp=1234567890.0,
            query="Test",
            candidate_output="Test output",
            metrics=metrics,
            verdict="SEAL",
            floor_failures=[],
            sabar_reason=None,
            organs={},
        )

        ledger.append(entry)

        # File should exist
        assert temp_ledger_path.exists()

        # Can iterate (though this entry is old and won't be in recent)
        # Just verify the method works
        list(ledger.iter_recent(hours=72))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
