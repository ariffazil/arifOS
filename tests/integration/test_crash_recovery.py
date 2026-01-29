"""
arifOS Crash Recovery Integration Tests (v52.4.0)

Tests the Loop Bootstrap mechanism:
1. Session starts via 000_init
2. Session crashes (doesn't call 999_vault)
3. On next 000_init, orphaned session is auto-recovered with SABAR

DITEMPA BUKAN DIBERI
"""

import os
import sys
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def temp_session_dir(tmp_path):
    """Create temporary session directory for testing."""
    sessions_dir = tmp_path / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    return sessions_dir


@pytest.fixture
def temp_vault_dir(tmp_path):
    """Create temporary VAULT999 directory for testing."""
    vault_dir = tmp_path / "VAULT999" / "BBB_LEDGER" / "entries"
    vault_dir.mkdir(parents=True, exist_ok=True)
    return vault_dir


@pytest.fixture(autouse=True)
def mock_session_paths(monkeypatch, temp_session_dir, temp_vault_dir):
    """Mock the session ledger paths to use temp directories."""
    monkeypatch.setattr(
        "arifos.mcp.session_ledger.SESSION_PATH",
        temp_session_dir
    )
    monkeypatch.setattr(
        "arifos.mcp.session_ledger.BBB_LEDGER_PATH",
        temp_vault_dir
    )
    monkeypatch.setattr(
        "arifos.mcp.session_ledger.OPEN_SESSIONS_FILE",
        temp_session_dir / "open_sessions.json"
    )


# =============================================================================
# UNIT TESTS: Session Tracking
# =============================================================================

class TestOpenSessionTracking:
    """Tests for open_session(), close_session(), get_orphaned_sessions()"""

    def test_open_session_creates_entry(self, temp_session_dir):
        """Open session should create entry in open_sessions.json"""
        from arifos.mcp.session_ledger import open_session, _load_open_sessions

        open_session(
            session_id="test-123",
            token="token-abc",
            pid=os.getpid()
        )

        sessions = _load_open_sessions()
        assert "test-123" in sessions
        assert sessions["test-123"]["token"] == "token-abc"
        assert sessions["test-123"]["pid"] == os.getpid()

    def test_close_session_removes_entry(self, temp_session_dir):
        """Close session should remove entry from open_sessions.json"""
        from arifos.mcp.session_ledger import open_session, close_session, _load_open_sessions

        open_session("test-456", "token-def", os.getpid())
        assert "test-456" in _load_open_sessions()

        result = close_session("test-456")
        assert result is True
        assert "test-456" not in _load_open_sessions()

    def test_close_nonexistent_session_returns_false(self, temp_session_dir):
        """Closing nonexistent session should return False"""
        from arifos.mcp.session_ledger import close_session

        result = close_session("nonexistent-session")
        assert result is False

    def test_get_orphaned_sessions_by_timeout(self, temp_session_dir):
        """Sessions older than timeout should be detected as orphaned"""
        from arifos.mcp.session_ledger import get_orphaned_sessions, _save_open_sessions

        # Create a session that started 60 minutes ago
        old_time = (datetime.utcnow() - timedelta(minutes=60)).isoformat() + "Z"
        sessions = {
            "old-session": {
                "session_id": "old-session",
                "token": "old-token",
                "pid": os.getpid(),  # Still running, but too old
                "started_at": old_time
            }
        }
        _save_open_sessions(sessions)

        orphans = get_orphaned_sessions(timeout_minutes=30)
        assert len(orphans) == 1
        assert orphans[0]["session_id"] == "old-session"
        assert "timeout" in orphans[0]["orphan_reason"].lower()

    def test_get_orphaned_sessions_by_dead_pid(self, temp_session_dir):
        """Sessions with dead PIDs should be detected as orphaned"""
        from arifos.mcp.session_ledger import get_orphaned_sessions, _save_open_sessions

        # Create a session with a very high (likely dead) PID
        sessions = {
            "dead-pid-session": {
                "session_id": "dead-pid-session",
                "token": "token-xyz",
                "pid": 999999999,  # Very unlikely to exist
                "started_at": datetime.utcnow().isoformat() + "Z"  # Recent
            }
        }
        _save_open_sessions(sessions)

        orphans = get_orphaned_sessions(timeout_minutes=60)  # Long timeout
        assert len(orphans) == 1
        assert orphans[0]["session_id"] == "dead-pid-session"
        assert "no longer running" in orphans[0]["orphan_reason"].lower()

    def test_active_session_not_orphaned(self, temp_session_dir):
        """Recent sessions with active PIDs should not be orphaned"""
        from arifos.mcp.session_ledger import open_session, get_orphaned_sessions

        # Open a session with current PID
        open_session("active-session", "active-token", os.getpid())

        orphans = get_orphaned_sessions(timeout_minutes=30)
        assert len(orphans) == 0


# =============================================================================
# INTEGRATION TESTS: Crash Recovery
# =============================================================================

class TestCrashRecovery:
    """Tests for the full crash recovery flow"""

    def test_recover_orphaned_session(self, temp_session_dir, temp_vault_dir):
        """Orphaned sessions should be auto-sealed with SABAR verdict"""
        from arifos.mcp.session_ledger import (
            open_session,
            get_orphaned_sessions,
            recover_orphaned_session,
            _load_open_sessions,
        )

        # Step 1: Simulate starting a session
        open_session("crash-session", "crash-token", 999999999)

        # Step 2: Detect as orphaned (dead PID)
        orphans = get_orphaned_sessions(timeout_minutes=60)
        assert len(orphans) == 1
        assert orphans[0]["session_id"] == "crash-session"

        # Step 3: Recover the orphaned session
        result = recover_orphaned_session(orphans[0])

        # Verify recovery result
        assert result["sealed"] is True
        assert result["verdict"] == "SABAR"
        assert "crash-session" in result["session_id"]

        # Verify session removed from open_sessions
        assert "crash-session" not in _load_open_sessions()

        # Verify seal written to VAULT999
        vault_files = list(temp_vault_dir.glob("*.md"))
        assert len(vault_files) >= 1

    def test_multiple_orphan_recovery(self, temp_session_dir, temp_vault_dir):
        """Multiple orphaned sessions should all be recovered"""
        from arifos.mcp.session_ledger import (
            _save_open_sessions,
            get_orphaned_sessions,
            recover_orphaned_session,
            _load_open_sessions,
        )

        # Create multiple orphaned sessions
        sessions = {
            f"orphan-{i}": {
                "session_id": f"orphan-{i}",
                "token": f"token-{i}",
                "pid": 999999990 + i,  # Dead PIDs
                "started_at": datetime.utcnow().isoformat() + "Z"
            }
            for i in range(3)
        }
        _save_open_sessions(sessions)

        # Recover all orphans
        orphans = get_orphaned_sessions(timeout_minutes=60)
        assert len(orphans) == 3

        for orphan in orphans:
            result = recover_orphaned_session(orphan)
            assert result["sealed"] is True
            assert result["verdict"] == "SABAR"

        # All should be removed
        remaining = _load_open_sessions()
        assert len(remaining) == 0


# =============================================================================
# AXIS SERVER TESTS
# =============================================================================

class TestAXISLoopBootstrap:
    """Tests for AXIS server's Loop Bootstrap integration"""

    
    async def test_axis_000_init_recovers_orphans(self, temp_session_dir, temp_vault_dir, monkeypatch):
        """AXIS 000_init should recover orphaned sessions before starting new one"""
        from arifos.mcp.session_ledger import _save_open_sessions, _load_open_sessions

        # Create an orphaned session
        sessions = {
            "orphan-to-recover": {
                "session_id": "orphan-to-recover",
                "token": "orphan-token",
                "pid": 999999999,
                "started_at": datetime.utcnow().isoformat() + "Z"
            }
        }
        _save_open_sessions(sessions)

        # Mock the mcp_000_init function
        async def mock_init(*args, **kwargs):
            return {
                "status": "SEAL",
                "session_id": "new-session-123",
                "authority": "GUEST"
            }

        monkeypatch.setattr(
            "arifos.mcp.servers.axis.mcp_000_init",
            mock_init
        )

        # Import after mocking
        from arifos.mcp.servers.axis import axis_000_init

        # Call axis_000_init (should recover orphan first)
        result = await axis_000_init(
            ctx=None,
            action="init",
            query="Test query"
        )

        # Verify new session started
        assert result["status"] == "SEAL"
        assert result["session_id"] == "new-session-123"

        # Verify orphan was recovered (removed from open_sessions)
        remaining = _load_open_sessions()
        assert "orphan-to-recover" not in remaining

        # Verify new session is tracked
        assert "new-session-123" in remaining

    
    async def test_axis_999_vault_closes_session(self, temp_session_dir, monkeypatch):
        """AXIS 999_vault should close session tracking after seal"""
        from arifos.mcp.session_ledger import open_session, _load_open_sessions

        # Create an open session
        open_session("session-to-close", "close-token", os.getpid())
        assert "session-to-close" in _load_open_sessions()

        # Mock the mcp_999_vault function
        async def mock_vault(*args, **kwargs):
            return {
                "status": "SEAL",
                "merkle_root": "mock-merkle",
                "entry_hash": "mock-hash"
            }

        monkeypatch.setattr(
            "arifos.mcp.servers.axis.mcp_999_vault",
            mock_vault
        )

        # Import after mocking
        from arifos.mcp.servers.axis import axis_999_vault

        # Call axis_999_vault
        result = await axis_999_vault(
            ctx=None,
            action="seal",
            session_id="session-to-close",
            verdict="SEAL"
        )

        # Verify seal succeeded
        assert result["status"] == "SEAL"

        # Verify session removed from tracking
        remaining = _load_open_sessions()
        assert "session-to-close" not in remaining


# =============================================================================
# PYTEST MARKERS
# =============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )


# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration
