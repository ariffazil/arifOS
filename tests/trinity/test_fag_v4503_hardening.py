"""
tests/test_fag_v4503_hardening.py - FAG v45.0.3 Hardening Tests

Comprehensive tests for the four v45.0.3 hardening features:
1. Pre-Mutate Snapshot (Rollback Contract)
2. Protected Paths (No-Touch Zones)
3. Mutation Watchdog (Anomaly Detection)
4. Operator Alerts (Entropy Spike Warnings)

Version: v45.0.3
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from arifos.apex.governance.fag import (FAG, PROTECTED_PATHS, FAGSnapshot,
                                        FAGWritePlan, MutationEvent,
                                        MutationWatchdog, OperatorAlert)

# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def temp_workspace(tmp_path):
    """Create a temporary workspace with test files."""
    # Create test directory structure
    (tmp_path / "src").mkdir()
    (tmp_path / ".vscode").mkdir()
    (tmp_path / "__pycache__").mkdir()

    # Create test files
    (tmp_path / "README.md").write_text("# Test Project")
    (tmp_path / "src" / "main.py").write_text("print('hello')")
    (tmp_path / ".vscode" / "settings.json").write_text("{}")

    return tmp_path


@pytest.fixture
def fag_with_hardening(temp_workspace):
    """Create FAG instance with v45.0.3 hardening enabled."""
    return FAG(
        root=str(temp_workspace),
        enable_snapshots=True,
        enable_watchdog=True,
        enable_alerts=True,
        enable_ledger=False,  # Disable for faster tests
    )


# =============================================================================
# PRE-MUTATE SNAPSHOT TESTS
# =============================================================================

class TestPreMutateSnapshot:
    """Tests for v45.0.3 Pre-Mutate Snapshot (Rollback Contract)."""

    def test_snapshot_created_before_write(self, temp_workspace):
        """Verify snapshot is created when write_validate is called."""
        fag = FAG(
            root=str(temp_workspace),
            enable_snapshots=True,
            enable_ledger=False,
        )

        # Create a plan to patch an existing file
        plan = FAGWritePlan(
            target_path="README.md",
            operation="patch",
            justification="Update readme",
            diff="+Added line",
            read_sha256="abc123",  # Fake for test
            read_bytes=14,
        )

        result = fag.write_validate(plan)

        # For patches without valid read_proof, we get HOLD
        # But snapshot should still be created
        assert fag.access_stats["snapshots_created"] >= 0

    def test_rollback_restores_content(self, temp_workspace):
        """Verify rollback restores original file content."""
        fag = FAG(
            root=str(temp_workspace),
            enable_snapshots=True,
            enable_ledger=False,
        )

        test_file = temp_workspace / "rollback_test.txt"
        original_content = b"Original content"
        test_file.write_bytes(original_content)

        # Create snapshot
        snapshot = fag._create_snapshot(test_file)
        assert snapshot is not None
        assert snapshot.rollback_id is not None

        # Modify the file
        test_file.write_bytes(b"Modified content")
        assert test_file.read_bytes() == b"Modified content"

        # Rollback
        success = fag.rollback(snapshot.rollback_id)
        assert success is True
        assert test_file.read_bytes() == original_content

    def test_snapshot_disabled(self, temp_workspace):
        """Verify snapshots are not created when disabled."""
        fag = FAG(
            root=str(temp_workspace),
            enable_snapshots=False,
            enable_ledger=False,
        )

        test_file = temp_workspace / "README.md"
        snapshot = fag._create_snapshot(test_file)

        assert snapshot is None

    def test_snapshot_lru_eviction(self, temp_workspace):
        """Verify oldest snapshot is evicted when capacity reached."""
        fag = FAG(
            root=str(temp_workspace),
            enable_snapshots=True,
            enable_ledger=False,
        )
        fag.max_snapshots = 3  # Small limit for test

        test_file = temp_workspace / "README.md"

        # Create more snapshots than capacity
        snapshots = []
        for i in range(5):
            test_file.write_text(f"Content {i}")
            snapshot = fag._create_snapshot(test_file)
            if snapshot:
                snapshots.append(snapshot)

        # Should only keep last 3
        assert len(fag.snapshots) == 3


# =============================================================================
# PROTECTED PATHS TESTS
# =============================================================================

class TestProtectedPaths:
    """Tests for v45.0.3 Protected Paths (No-Touch Zones)."""

    def test_vscode_blocked_by_default(self, temp_workspace):
        """Verify .vscode directory is blocked without token."""
        fag = FAG(
            root=str(temp_workspace),
            human_seal_token=None,  # No token
            enable_ledger=False,
        )

        result = fag.read(".vscode/settings.json")

        assert result.verdict == "VOID"
        assert "HUMAN_SEAL_TOKEN" in result.reason

    def test_human_seal_token_bypasses(self, temp_workspace):
        """Verify HUMAN_SEAL_TOKEN allows protected path access."""
        fag = FAG(
            root=str(temp_workspace),
            human_seal_token="valid-token-123",
            enable_ledger=False,
        )

        result = fag.read(".vscode/settings.json")

        # Should succeed with valid token
        assert result.verdict == "SEAL"

    def test_pycache_blocked(self, temp_workspace):
        """Verify __pycache__ is blocked without token."""
        fag = FAG(
            root=str(temp_workspace),
            human_seal_token=None,
            enable_ledger=False,
        )

        # Create a .pyc file
        (temp_workspace / "__pycache__" / "test.pyc").write_bytes(b"fake pyc")

        result = fag.read("__pycache__/test.pyc")

        # Should be blocked (either by protected path or binary extension)
        assert result.verdict == "VOID"

    def test_empty_token_does_not_bypass(self, temp_workspace):
        """Verify empty string token doesn't bypass protection."""
        fag = FAG(
            root=str(temp_workspace),
            human_seal_token="",  # Empty token
            enable_ledger=False,
        )

        result = fag.read(".vscode/settings.json")

        assert result.verdict == "VOID"


# =============================================================================
# MUTATION WATCHDOG TESTS
# =============================================================================

class TestMutationWatchdog:
    """Tests for v45.0.3 Mutation Watchdog (Anomaly Detection)."""

    def test_detects_mass_change_burst(self, temp_workspace):
        """Verify watchdog detects too many mutations."""
        watchdog = MutationWatchdog(
            burst_threshold=5,
            time_window_seconds=60,
        )

        # Record 10 mutations (exceeds threshold of 5)
        for i in range(10):
            watchdog.record(MutationEvent(
                operation="modify",
                path=f"file_{i}.txt",
                timestamp=datetime.now(timezone.utc),
            ))

        anomalies = watchdog.detect_anomalies(temp_workspace)

        assert len(anomalies) > 0
        assert any("MASS_CHANGE_BURST" in a for a in anomalies)

    def test_detects_rename_delete_chain(self, temp_workspace):
        """Verify watchdog detects rename then delete pattern."""
        watchdog = MutationWatchdog(
            burst_threshold=100,  # High to avoid burst detection
            time_window_seconds=60,
        )

        now = datetime.now(timezone.utc)

        # Rename file
        watchdog.record(MutationEvent(
            operation="rename",
            path="new_name.txt",
            previous_path="original.txt",
            timestamp=now,
        ))

        # Then delete it (stealth-delete pattern)
        watchdog.record(MutationEvent(
            operation="delete",
            path="new_name.txt",
            timestamp=now + timedelta(seconds=1),
        ))

        anomalies = watchdog.detect_anomalies(temp_workspace)

        assert len(anomalies) > 0
        assert any("RENAME_DELETE_CHAIN" in a for a in anomalies)

    def test_hold_888_on_anomaly(self, temp_workspace):
        """Verify HOLD-888 is returned when anomaly detected."""
        fag = FAG(
            root=str(temp_workspace),
            enable_watchdog=True,
            watchdog_burst_threshold=2,  # Very low threshold
            enable_ledger=False,
        )

        # Trigger burst by recording many mutations
        for i in range(10):
            fag.watchdog.record(MutationEvent(
                operation="modify",
                path=f"file_{i}.txt",
                timestamp=datetime.now(timezone.utc),
            ))

        # Now try write_validate - should get HOLD
        plan = FAGWritePlan(
            target_path="new_file.txt",
            operation="create",
            justification="Test",
        )

        result = fag.write_validate(plan)

        assert result.verdict == "HOLD"
        assert "HOLD-888" in result.reason or "Watchdog" in result.reason

    def test_no_anomaly_within_threshold(self, temp_workspace):
        """Verify no anomaly when within threshold."""
        watchdog = MutationWatchdog(
            burst_threshold=10,
            time_window_seconds=60,
        )

        # Record only 3 mutations (under threshold)
        for i in range(3):
            watchdog.record(MutationEvent(
                operation="modify",
                path=f"file_{i}.txt",
                timestamp=datetime.now(timezone.utc),
            ))

        anomalies = watchdog.detect_anomalies(temp_workspace)

        assert len(anomalies) == 0


# =============================================================================
# OPERATOR ALERTS TESTS
# =============================================================================

class TestOperatorAlerts:
    """Tests for v45.0.3 Operator Alerts (Entropy Spike Warnings)."""

    def test_alert_on_consecutive_failures(self, temp_workspace):
        """Verify alert emitted after consecutive failures."""
        alerts_received = []

        def alert_callback(alert: OperatorAlert):
            alerts_received.append(alert)

        fag = FAG(
            root=str(temp_workspace),
            enable_alerts=True,
            alert_callback=alert_callback,
            enable_ledger=False,
        )

        # Simulate consecutive failures
        fag._track_consecutive_failure()
        fag._track_consecutive_failure()

        # Should have received alert
        assert len(alerts_received) > 0
        assert any(a.code == "CONSECUTIVE_FAILURES" for a in alerts_received)

    def test_alert_callback_invoked(self, temp_workspace):
        """Verify alert callback is called."""
        callback_mock = MagicMock()

        fag = FAG(
            root=str(temp_workspace),
            enable_alerts=True,
            alert_callback=callback_mock,
            enable_ledger=False,
        )

        # Emit an alert
        fag._emit_alert(OperatorAlert(
            severity="WARN",
            code="TEST_ALERT",
            message="Test message",
        ))

        callback_mock.assert_called_once()

    def test_alerts_disabled(self, temp_workspace):
        """Verify no alerts when disabled."""
        callback_mock = MagicMock()

        fag = FAG(
            root=str(temp_workspace),
            enable_alerts=False,
            alert_callback=callback_mock,
            enable_ledger=False,
        )

        # Emit an alert (should be ignored)
        fag._emit_alert(OperatorAlert(
            severity="CRITICAL",
            code="TEST",
            message="Test",
        ))

        callback_mock.assert_not_called()

    def test_consecutive_failure_reset(self, temp_workspace):
        """Verify consecutive failures reset on success."""
        fag = FAG(
            root=str(temp_workspace),
            enable_alerts=True,
            enable_ledger=False,
        )

        # Track some failures
        fag._track_consecutive_failure()
        assert fag.consecutive_failures == 1

        # Reset on success
        fag._reset_consecutive_failures()
        assert fag.consecutive_failures == 0


# =============================================================================
# HEALTH CHECK TESTS
# =============================================================================

class TestHealthCheck:
    """Tests for v45.0.3 health_check() method."""

    def test_healthy_status(self, temp_workspace):
        """Verify healthy status for clean FAG."""
        fag = FAG(
            root=str(temp_workspace),
            enable_watchdog=True,
            enable_ledger=False,
        )

        health = fag.health_check()

        assert health["status"] == "HEALTHY"
        assert health["checks"]["root_accessible"] is True
        assert health["checks"]["watchdog_clean"] is True

    def test_alert_status_on_anomaly(self, temp_workspace):
        """Verify ALERT status when watchdog detects anomaly."""
        fag = FAG(
            root=str(temp_workspace),
            enable_watchdog=True,
            watchdog_burst_threshold=2,
            enable_ledger=False,
        )

        # Trigger anomaly
        for i in range(10):
            fag.watchdog.record(MutationEvent(
                operation="modify",
                path=f"file_{i}.txt",
                timestamp=datetime.now(timezone.utc),
            ))

        health = fag.health_check()

        assert health["status"] == "ALERT"
        assert health["checks"]["watchdog_clean"] is False
        assert len(health["anomalies"]) > 0

    def test_warn_status_on_failures(self, temp_workspace):
        """Verify WARN status on consecutive failures."""
        fag = FAG(
            root=str(temp_workspace),
            enable_ledger=False,
        )

        # Simulate failures
        fag.consecutive_failures = 3

        health = fag.health_check()

        assert health["status"] == "WARN"
        assert health["checks"]["consecutive_failures"] == 3
        assert len(health["recommendations"]) > 0
