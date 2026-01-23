"""
Tests for arifOS Session Ledger Module (v50.5.17)

Validates:
- Session persistence (999-000 loop)
- Hash chain integrity
- Thread-safe operations
- BBB_LEDGER integration
- Context injection for 000_init

Constitutional Floor: F1 (Amanah) - Trustworthy session persistence

DITEMPA BUKAN DIBERI
"""

import pytest
import json
import tempfile
import threading
from pathlib import Path
from datetime import datetime
from unittest.mock import patch

from arifos.mcp.session_ledger import (
    SessionLedger,
    SessionEntry,
    get_ledger,
    inject_memory,
    seal_memory,
)


class TestSessionEntry:
    """Tests for SessionEntry dataclass."""

    def test_entry_creation(self):
        """SessionEntry creates correctly with required fields."""
        entry = SessionEntry(
            session_id="test-123",
            timestamp=datetime.now().isoformat(),
            verdict="SEAL"
        )
        assert entry.session_id == "test-123"
        assert entry.verdict == "SEAL"
        assert entry.init_result == {}
        assert entry.merkle_root == ""

    def test_entry_with_results(self):
        """SessionEntry accepts Trinity results."""
        entry = SessionEntry(
            session_id="test-456",
            timestamp=datetime.now().isoformat(),
            verdict="SEAL",
            init_result={"status": "SEAL", "session_id": "test-456"},
            genius_result={"action": "think", "status": "SEAL"},
            act_result={"action": "act", "status": "SEAL"},
            judge_result={"verdict": "SEAL"}
        )
        assert entry.init_result["status"] == "SEAL"
        assert entry.genius_result["action"] == "think"

    def test_entry_compute_hash(self):
        """SessionEntry computes consistent hash."""
        entry = SessionEntry(
            session_id="hash-test",
            timestamp="2026-01-23T12:00:00",
            verdict="SEAL"
        )
        hash1 = entry.compute_hash()
        hash2 = entry.compute_hash()

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex

    def test_entry_different_content_different_hash(self):
        """Different content produces different hash."""
        entry1 = SessionEntry(
            session_id="hash-1",
            timestamp="2026-01-23T12:00:00",
            verdict="SEAL"
        )
        entry2 = SessionEntry(
            session_id="hash-2",
            timestamp="2026-01-23T12:00:00",
            verdict="SEAL"
        )

        assert entry1.compute_hash() != entry2.compute_hash()


class TestSessionLedger:
    """Tests for SessionLedger class."""

    @pytest.fixture
    def temp_ledger(self, tmp_path):
        """Create a ledger with temporary paths."""
        with patch.object(SessionLedger, '__init__', lambda self: None):
            ledger = SessionLedger()
            ledger.session_path = tmp_path / "sessions"
            ledger.bbb_path = tmp_path / "bbb"
            ledger.session_path.mkdir(parents=True)
            ledger.bbb_path.mkdir(parents=True)
            ledger._current_session = None
            ledger._chain_head = None
            ledger._lock = threading.Lock()
            ledger._lock_file_path = ledger.session_path / ".ledger.lock"
            return ledger

    def test_ledger_first_session(self, temp_ledger):
        """First session has no previous context."""
        context = temp_ledger.get_context_for_init()

        assert context["is_first_session"] is True
        assert context["previous_session"] is None
        assert context["chain_length"] == 0

    def test_ledger_seal_session(self, temp_ledger):
        """seal_session creates entry correctly."""
        entry = temp_ledger.seal_session(
            session_id="seal-test",
            verdict="SEAL",
            init_result={"status": "SEAL"},
            genius_result={"status": "SEAL"},
            act_result={"status": "SEAL"},
            judge_result={"verdict": "SEAL"},
            telemetry={"duration_ms": 100},
            context_summary="Test session completed",
            key_insights=["insight 1", "insight 2"]
        )

        assert entry.session_id == "seal-test"
        assert entry.verdict == "SEAL"
        assert entry.context_summary == "Test session completed"
        assert len(entry.key_insights) == 2

    def test_ledger_chain_integrity(self, temp_ledger):
        """Sealed sessions maintain chain integrity."""
        # Seal first session
        entry1 = temp_ledger.seal_session(
            session_id="chain-1",
            verdict="SEAL",
            init_result={},
            genius_result={},
            act_result={},
            judge_result={},
            telemetry={}
        )

        # Seal second session
        entry2 = temp_ledger.seal_session(
            session_id="chain-2",
            verdict="SEAL",
            init_result={},
            genius_result={},
            act_result={},
            judge_result={},
            telemetry={}
        )

        # Second entry should reference first
        assert entry2.prev_hash == entry1.entry_hash
        assert entry2.entry_hash != entry1.entry_hash

    def test_ledger_get_last_session(self, temp_ledger):
        """get_last_session returns most recent entry."""
        # Seal a session
        temp_ledger.seal_session(
            session_id="last-test",
            verdict="SEAL",
            init_result={},
            genius_result={},
            act_result={},
            judge_result={},
            telemetry={},
            context_summary="Last session"
        )

        # Get it back
        last = temp_ledger.get_last_session()

        assert last is not None
        assert last.session_id == "last-test"
        assert last.context_summary == "Last session"

    def test_ledger_context_injection(self, temp_ledger):
        """get_context_for_init returns correct context."""
        # Seal a session with context
        temp_ledger.seal_session(
            session_id="context-test",
            verdict="SEAL",
            init_result={},
            genius_result={},
            act_result={},
            judge_result={},
            telemetry={},
            context_summary="Previous work on feature X",
            key_insights=["Use pattern Y", "Avoid Z"]
        )

        # Get context for next init
        context = temp_ledger.get_context_for_init()

        assert context["is_first_session"] is False
        assert context["previous_session"]["session_id"] == "context-test"
        assert context["context_summary"] == "Previous work on feature X"
        assert "Use pattern Y" in context["key_insights"]
        assert context["chain_length"] == 1


class TestSessionLedgerThreadSafety:
    """Tests for thread-safe ledger operations."""

    @pytest.fixture
    def temp_ledger(self, tmp_path):
        """Create a ledger with temporary paths."""
        with patch.object(SessionLedger, '__init__', lambda self: None):
            ledger = SessionLedger()
            ledger.session_path = tmp_path / "sessions"
            ledger.bbb_path = tmp_path / "bbb"
            ledger.session_path.mkdir(parents=True)
            ledger.bbb_path.mkdir(parents=True)
            ledger._current_session = None
            ledger._chain_head = None
            ledger._lock = threading.Lock()
            ledger._lock_file_path = ledger.session_path / ".ledger.lock"
            return ledger

    def test_concurrent_sealing(self, temp_ledger):
        """Concurrent seal operations maintain integrity."""
        results = []

        def seal_session(idx):
            entry = temp_ledger.seal_session(
                session_id=f"concurrent-{idx}",
                verdict="SEAL",
                init_result={},
                genius_result={},
                act_result={},
                judge_result={},
                telemetry={}
            )
            results.append(entry.session_id)

        threads = [threading.Thread(target=seal_session, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All sessions should be sealed
        assert len(results) == 10

        # All session IDs should be unique
        assert len(set(results)) == 10


class TestHelperFunctions:
    """Tests for module-level helper functions."""

    def test_get_ledger_singleton(self):
        """get_ledger returns singleton instance."""
        import arifos.mcp.session_ledger as module

        # Clear singleton
        module._session_ledger = None

        ledger1 = get_ledger()
        ledger2 = get_ledger()

        assert ledger1 is ledger2

    def test_inject_memory_first_session(self):
        """inject_memory works for first session."""
        context = inject_memory()

        assert "is_first_session" in context
        assert "previous_session" in context
        assert "context_summary" in context

    def test_seal_memory_creates_entry(self):
        """seal_memory creates ledger entry."""
        # This will actually write to the real ledger
        result = seal_memory(
            session_id=f"seal-test-{datetime.now().timestamp()}",
            verdict="SEAL",
            init_result={"test": True},
            genius_result={},
            act_result={},
            judge_result={},
            telemetry={}
        )

        # seal_memory returns a dict with entry hash
        assert result is not None
        assert "entry_hash" in result
        assert len(result["entry_hash"]) == 64


class TestVerdictHandling:
    """Tests for different verdict types."""

    @pytest.fixture
    def temp_ledger(self, tmp_path):
        """Create a ledger with temporary paths."""
        with patch.object(SessionLedger, '__init__', lambda self: None):
            ledger = SessionLedger()
            ledger.session_path = tmp_path / "sessions"
            ledger.bbb_path = tmp_path / "bbb"
            ledger.session_path.mkdir(parents=True)
            ledger.bbb_path.mkdir(parents=True)
            ledger._current_session = None
            ledger._chain_head = None
            ledger._lock = threading.Lock()
            ledger._lock_file_path = ledger.session_path / ".ledger.lock"
            return ledger

    def test_seal_verdict_stored(self, temp_ledger):
        """SEAL verdict entries are stored."""
        entry = temp_ledger.seal_session(
            session_id="seal-verdict",
            verdict="SEAL",
            init_result={},
            genius_result={},
            act_result={},
            judge_result={},
            telemetry={}
        )

        # Should be stored
        assert entry.entry_hash != ""
        json_files = list(temp_ledger.session_path.glob("*.json"))
        assert len(json_files) >= 1

    def test_sabar_verdict_stored(self, temp_ledger):
        """SABAR verdict entries are stored."""
        entry = temp_ledger.seal_session(
            session_id="sabar-verdict",
            verdict="SABAR",
            init_result={},
            genius_result={},
            act_result={},
            judge_result={},
            telemetry={}
        )

        assert entry.verdict == "SABAR"
        assert entry.entry_hash != ""

    def test_void_verdict_stored(self, temp_ledger):
        """VOID verdict entries are stored in ledger (for audit)."""
        entry = temp_ledger.seal_session(
            session_id="void-verdict",
            verdict="VOID",
            init_result={},
            genius_result={},
            act_result={},
            judge_result={},
            telemetry={}
        )

        assert entry.verdict == "VOID"
        # Note: session_ledger stores all verdicts
        # The EUREKA sieve filtering happens in 999_vault before calling seal
        assert entry.entry_hash != ""
