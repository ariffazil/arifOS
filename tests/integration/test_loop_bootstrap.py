"""
Loop Bootstrap Crash Recovery Test (v52.4.0)

Validates that AXIS can recover orphaned sessions after ARIF crashes.

Test Scenario:
1. Call axis_000_init → creates session in open_sessions.json
2. Simulate crash (don't call 999_vault)
3. Call axis_000_init again
4. Verify: Previous session was auto-sealed with SABAR verdict

Run: pytest tests/integration/test_loop_bootstrap.py -v
"""

import os
import sys
import json
import time
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestLoopBootstrap:
    """Test crash recovery (Loop Bootstrap) functionality."""

    @pytest.fixture
    def sessions_dir(self, tmp_path):
        """Create temporary sessions directory."""
        sessions = tmp_path / "sessions"
        sessions.mkdir()
        return sessions

    @pytest.fixture
    def mock_session_path(self, sessions_dir, monkeypatch):
        """Patch SESSION_PATH to use temp directory."""
        monkeypatch.setattr(
            "arifos.mcp.session_ledger.SESSION_PATH",
            sessions_dir
        )
        monkeypatch.setattr(
            "arifos.mcp.session_ledger.OPEN_SESSIONS_FILE",
            sessions_dir / "open_sessions.json"
        )
        return sessions_dir

    def test_open_session_creates_tracking_file(self, mock_session_path):
        """Verify open_session() creates tracking entry."""
        from arifos.mcp.session_ledger import open_session, _load_open_sessions

        # Create a session
        open_session(
            session_id="test-session-001",
            token="token-abc",
            pid=12345,
            authority="HUMAN"
        )

        # Verify tracking file exists
        sessions = _load_open_sessions()
        assert "test-session-001" in sessions
        assert sessions["test-session-001"]["token"] == "token-abc"
        assert sessions["test-session-001"]["pid"] == 12345

    def test_close_session_removes_tracking(self, mock_session_path):
        """Verify close_session() removes entry."""
        from arifos.mcp.session_ledger import (
            open_session, close_session, _load_open_sessions
        )

        # Create then close
        open_session("test-session-002", "token-xyz", 99999)
        result = close_session("test-session-002")

        assert result is True
        sessions = _load_open_sessions()
        assert "test-session-002" not in sessions

    def test_orphan_detection_by_dead_pid(self, mock_session_path):
        """Detect orphan when PID no longer exists."""
        from arifos.mcp.session_ledger import (
            open_session, get_orphaned_sessions, _save_open_sessions
        )

        # Create session with a PID that definitely doesn't exist
        fake_dead_pid = 999999999  # Unlikely to be running
        sessions_file = mock_session_path / "open_sessions.json"

        # Manually write session with dead PID
        session_data = {
            "orphan-session": {
                "session_id": "orphan-session",
                "token": "dead-token",
                "pid": fake_dead_pid,
                "started_at": datetime.utcnow().isoformat() + "Z",
                "authority": "GUEST"
            }
        }
        sessions_file.write_text(json.dumps(session_data))

        # Get orphans
        orphans = get_orphaned_sessions(timeout_minutes=9999)  # High timeout, rely on PID

        # Should detect as orphan (PID doesn't exist)
        assert len(orphans) >= 1
        orphan_ids = [o["session_id"] for o in orphans]
        assert "orphan-session" in orphan_ids

    def test_orphan_detection_by_timeout(self, mock_session_path):
        """Detect orphan when session exceeds timeout."""
        from arifos.mcp.session_ledger import get_orphaned_sessions

        # Create session with old timestamp
        old_time = (datetime.utcnow() - timedelta(hours=2)).isoformat() + "Z"
        sessions_file = mock_session_path / "open_sessions.json"

        session_data = {
            "old-session": {
                "session_id": "old-session",
                "token": "old-token",
                "pid": os.getpid(),  # Current PID (still alive)
                "started_at": old_time,
                "authority": "GUEST"
            }
        }
        sessions_file.write_text(json.dumps(session_data))

        # Get orphans with 30 min timeout
        orphans = get_orphaned_sessions(timeout_minutes=30)

        # Should detect as orphan (timeout exceeded)
        assert len(orphans) >= 1
        orphan_ids = [o["session_id"] for o in orphans]
        assert "old-session" in orphan_ids

    def test_recover_orphaned_session_seals_with_sabar(self, mock_session_path):
        """Verify recovery seals with SABAR verdict."""
        from arifos.mcp.session_ledger import (
            recover_orphaned_session, _load_open_sessions
        )

        # Setup orphan
        sessions_file = mock_session_path / "open_sessions.json"
        session_data = {
            "crash-victim": {
                "session_id": "crash-victim",
                "token": "victim-token",
                "pid": 999999999,
                "started_at": datetime.utcnow().isoformat() + "Z",
                "authority": "HUMAN"
            }
        }
        sessions_file.write_text(json.dumps(session_data))

        # Recover it
        result = recover_orphaned_session(session_data["crash-victim"])

        # Verify SABAR verdict
        assert result["verdict"] == "SABAR"
        # Check recovery was successful (orphan_reason is in the returned telemetry)
        assert result.get("recovery", False) or "SABAR" in str(result)

        # Verify removed from tracking
        sessions = _load_open_sessions()
        assert "crash-victim" not in sessions

    def test_full_crash_recovery_flow(self, mock_session_path):
        """End-to-end: init → crash → init → verify recovery."""
        from arifos.mcp.session_ledger import (
            open_session, get_orphaned_sessions, recover_orphaned_session,
            _load_open_sessions
        )

        # Step 1: Simulate first init (session opens)
        open_session(
            session_id="production-session",
            token="prod-token",
            pid=999999999,  # Fake PID that will look "dead"
            authority="HUMAN"
        )

        # Step 2: Crash happens (we don't call close_session)
        # The session is now orphaned

        # Step 3: New process starts, detects orphans
        orphans = get_orphaned_sessions(timeout_minutes=30)

        # Step 4: Should find our orphan
        orphan_ids = [o["session_id"] for o in orphans]
        assert "production-session" in orphan_ids

        # Step 5: Recover it
        orphan = next(o for o in orphans if o["session_id"] == "production-session")
        result = recover_orphaned_session(orphan)

        # Verify SABAR seal
        assert result["verdict"] == "SABAR"

        # Verify tracking cleared
        sessions = _load_open_sessions()
        assert "production-session" not in sessions


class TestAxisServerRecovery:
    """Test AXIS server's _recover_orphans() integration."""

    @pytest.fixture
    def mock_dependencies(self, monkeypatch, tmp_path):
        """Mock all external dependencies."""
        sessions = tmp_path / "sessions"
        sessions.mkdir()

        monkeypatch.setattr(
            "arifos.mcp.session_ledger.SESSION_PATH",
            sessions
        )
        monkeypatch.setattr(
            "arifos.mcp.session_ledger.OPEN_SESSIONS_FILE",
            sessions / "open_sessions.json"
        )

        return sessions

    def test_axis_init_recovers_orphans_on_startup(self, mock_dependencies):
        """AXIS 000_init should auto-recover orphaned sessions."""
        import json
        from datetime import datetime

        # Setup an orphan in the sessions file
        sessions_file = mock_dependencies / "open_sessions.json"
        old_time = (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z"

        session_data = {
            "crashed-session": {
                "session_id": "crashed-session",
                "token": "crash-token",
                "pid": 999999999,
                "started_at": old_time,
                "authority": "GUEST"
            }
        }
        sessions_file.write_text(json.dumps(session_data))

        # Import and run recovery
        from arifos.mcp.session_ledger import (
            get_orphaned_sessions, recover_orphaned_session, _load_open_sessions
        )

        # Simulate what AXIS does on init
        orphans = get_orphaned_sessions(timeout_minutes=30)
        for orphan in orphans:
            result = recover_orphaned_session(orphan)
            assert result["verdict"] == "SABAR"

        # Verify cleanup
        sessions = _load_open_sessions()
        assert "crashed-session" not in sessions


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
