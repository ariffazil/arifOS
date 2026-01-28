"""
arifOS Session Ledger (v52.4.0)
Memory Bridge: MCP ↔ VAULT999

The 999-000 Loop:
    999_vault SEALS session → writes to ledger
    000_init OPENS session → reads from ledger

Storage:
    Machine: codebase/mcp/sessions/*.json (transient)
    Human:   VAULT999/BBB_LEDGER/entries/*.md (permanent)

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import threading
import logging
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Cross-platform file locking
if sys.platform == 'win32':
    import msvcrt
    def _lock_file(f):
        msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
    def _unlock_file(f):
        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
else:
    import fcntl
    def _lock_file(f):
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
    def _unlock_file(f):
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

logger = logging.getLogger(__name__)

# =============================================================================
# PATHS
# =============================================================================

# Root of arifOS (go up from codebase/mcp/ → codebase/ → arifOS/)
ARIFOS_ROOT = Path(__file__).parent.parent.parent
VAULT999_PATH = ARIFOS_ROOT / "VAULT999"
BBB_LEDGER_PATH = VAULT999_PATH / "BBB_LEDGER" / "entries"
SESSION_PATH = Path(__file__).parent / "sessions"

# Ensure directories exist
SESSION_PATH.mkdir(parents=True, exist_ok=True)
BBB_LEDGER_PATH.mkdir(parents=True, exist_ok=True)


# =============================================================================
# SESSION DATA
# =============================================================================

@dataclass
class SessionEntry:
    """A sealed session entry for the ledger."""
    session_id: str
    timestamp: str
    verdict: str  # SEAL, SABAR, VOID

    # Trinity Results
    init_result: Dict[str, Any] = field(default_factory=dict)
    genius_result: Dict[str, Any] = field(default_factory=dict)
    act_result: Dict[str, Any] = field(default_factory=dict)
    judge_result: Dict[str, Any] = field(default_factory=dict)

    # Telemetry
    telemetry: Dict[str, Any] = field(default_factory=dict)

    # Cryptographic
    prev_hash: str = ""
    merkle_root: str = ""
    entry_hash: str = ""

    # Context for next session
    context_summary: str = ""
    key_insights: List[str] = field(default_factory=list)

    def compute_hash(self) -> str:
        """Compute SHA256 hash of this entry."""
        content = json.dumps(asdict(self), sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()


# =============================================================================
# SESSION LEDGER
# =============================================================================

class SessionLedger:
    """
    Manages the 999-000 loop session persistence.

    Machine storage: JSON in arifos/mcp/sessions/
    Human storage: Markdown in VAULT999/BBB_LEDGER/entries/

    Thread Safety:
    - Uses threading.Lock for in-process synchronization
    - Uses file-based locking for cross-process safety
    """

    # Class-level lock for thread safety
    _class_lock = threading.Lock()

    def __init__(self):
        self.session_path = SESSION_PATH
        self.bbb_path = BBB_LEDGER_PATH
        self._current_session: Optional[SessionEntry] = None
        self._chain_head: Optional[str] = None
        self._lock = threading.Lock()
        self._lock_file_path = self.session_path / ".ledger.lock"
        self._load_chain_head()

    @contextmanager
    def _acquire_lock(self):
        """
        Acquire both thread lock and file lock for safe concurrent access.

        Uses:
        - threading.Lock for in-process synchronization
        - File-based lock for cross-process safety
        """
        with self._lock:
            # Ensure lock file exists
            self._lock_file_path.touch(exist_ok=True)

            try:
                with open(self._lock_file_path, 'r+') as lock_file:
                    try:
                        _lock_file(lock_file)
                        yield
                    finally:
                        try:
                            _unlock_file(lock_file)
                        except Exception:
                            pass  # Ignore unlock errors
            except Exception as e:
                logger.warning(f"File lock failed, proceeding with thread lock only: {e}")
                yield

    def _load_chain_head(self):
        """Load the latest entry hash from chain."""
        chain_file = self.session_path / "chain_head.txt"
        if chain_file.exists():
            self._chain_head = chain_file.read_text().strip()

    def _save_chain_head(self, hash: str):
        """Save the latest entry hash."""
        chain_file = self.session_path / "chain_head.txt"
        chain_file.write_text(hash)
        self._chain_head = hash

    # =========================================================================
    # READ (for 000_init)
    # =========================================================================

    def get_last_session(self) -> Optional[SessionEntry]:
        """
        Get the last sealed session for 000_init to inject.

        Returns:
            SessionEntry if exists, None if first session
        """
        if not self._chain_head:
            return None

        json_file = self.session_path / f"{self._chain_head[:16]}.json"
        if not json_file.exists():
            return None

        data = json.loads(json_file.read_text())
        return SessionEntry(**data)

    def get_context_for_init(self) -> Dict[str, Any]:
        """
        Get context to inject into 000_init.

        Returns:
            Dict with previous session summary, key insights, and continuity data
        """
        last = self.get_last_session()

        if not last:
            return {
                "is_first_session": True,
                "previous_session": None,
                "context_summary": "First session - no prior context",
                "key_insights": [],
                "chain_length": 0
            }

        return {
            "is_first_session": False,
            "previous_session": {
                "session_id": last.session_id,
                "timestamp": last.timestamp,
                "verdict": last.verdict,
                "entry_hash": last.entry_hash
            },
            "context_summary": last.context_summary,
            "key_insights": last.key_insights,
            "chain_length": self._count_chain()
        }

    def _count_chain(self) -> int:
        """Count total entries in chain."""
        return len(list(self.session_path.glob("*.json")))

    # =========================================================================
    # WRITE (for 999_vault)
    # =========================================================================

    def seal_session(
        self,
        session_id: str,
        verdict: str,
        init_result: Dict[str, Any],
        genius_result: Dict[str, Any],
        act_result: Dict[str, Any],
        judge_result: Dict[str, Any],
        telemetry: Dict[str, Any],
        context_summary: str = "",
        key_insights: List[str] = None
    ) -> SessionEntry:
        """
        Seal a session and write to ledger.

        This is called by 999_vault at end of session.

        Args:
            session_id: Current session ID
            verdict: Final verdict (SEAL, SABAR, VOID)
            init_result: Result from 000_init
            genius_result: Result from agi_genius
            act_result: Result from asi_act
            judge_result: Result from apex_judge
            telemetry: Full telemetry data
            context_summary: Summary for next session
            key_insights: Key insights to carry forward

        Returns:
            The sealed SessionEntry

        Thread Safety:
            This method acquires both thread and file locks before
            modifying the ledger to prevent race conditions.
        """
        with self._acquire_lock():
            # Create entry
            entry = SessionEntry(
                session_id=session_id,
                timestamp=datetime.now(timezone.utc).isoformat() + "Z",
                verdict=verdict,
                init_result=init_result,
                genius_result=genius_result,
                act_result=act_result,
                judge_result=judge_result,
                telemetry=telemetry,
                prev_hash=self._chain_head or "GENESIS",
                context_summary=context_summary or self._generate_summary(judge_result),
                key_insights=key_insights or []
            )

            # Compute hashes
            entry.entry_hash = entry.compute_hash()
            entry.merkle_root = self._compute_merkle([
                entry.init_result,
                entry.genius_result,
                entry.act_result,
                entry.judge_result
            ])

            # Write to machine storage (JSON)
            self._write_json(entry)

            # Write to human storage (Markdown in VAULT999)
            self._write_markdown(entry)

            # Update chain head
            self._save_chain_head(entry.entry_hash)

            return entry

    def _write_json(self, entry: SessionEntry):
        """Write entry to JSON file."""
        filename = f"{entry.entry_hash[:16]}.json"
        filepath = self.session_path / filename
        filepath.write_text(json.dumps(asdict(entry), indent=2))

    def _write_markdown(self, entry: SessionEntry):
        """Write entry to Markdown in VAULT999/BBB_LEDGER."""
        filename = f"{entry.timestamp[:10]}_{entry.session_id[:8]}.md"
        filepath = self.bbb_path / filename

        md_content = f"""# Session Seal: {entry.session_id[:8]}

**Timestamp:** {entry.timestamp}
**Verdict:** {entry.verdict}
**Entry Hash:** `{entry.entry_hash[:16]}...`
**Previous:** `{entry.prev_hash[:16]}...`

---

## Summary

{entry.context_summary}

## Key Insights

{chr(10).join(f"- {i}" for i in entry.key_insights) if entry.key_insights else "- No key insights recorded"}

---

## Telemetry

```yaml
verdict: {entry.verdict}
p_truth: {entry.telemetry.get('p_truth', 'N/A')}
TW: {entry.telemetry.get('TW', 'N/A')}
dS: {entry.telemetry.get('dS', 'N/A')}
peace2: {entry.telemetry.get('peace2', 'N/A')}
kappa_r: {entry.telemetry.get('kappa_r', 'N/A')}
omega_0: {entry.telemetry.get('omega_0', 'N/A')}
```

---

## Merkle Root

`{entry.merkle_root}`

---

**DITEMPA BUKAN DIBERI**
"""
        filepath.write_text(md_content)

    def _generate_summary(self, judge_result: Dict[str, Any]) -> str:
        """Generate context summary from judge result."""
        synthesis = judge_result.get("synthesis", "")
        verdict = judge_result.get("verdict", "UNKNOWN")
        return f"Previous session ended with {verdict}. {synthesis[:200]}"

    def _compute_merkle(self, items: List[Dict]) -> str:
        """Compute Merkle root from items."""
        if not items:
            return hashlib.sha256(b"EMPTY").hexdigest()

        hashes = [
            hashlib.sha256(json.dumps(item, sort_keys=True).encode()).hexdigest()
            for item in items
        ]

        while len(hashes) > 1:
            if len(hashes) % 2:
                hashes.append(hashes[-1])
            hashes = [
                hashlib.sha256((hashes[i] + hashes[i+1]).encode()).hexdigest()
                for i in range(0, len(hashes), 2)
            ]

        return hashes[0]


# =============================================================================
# OPEN SESSION TRACKING (Loop Bootstrap)
# =============================================================================

OPEN_SESSIONS_FILE = SESSION_PATH / "open_sessions.json"


@dataclass
class OpenSession:
    """An in-progress session (not yet sealed)."""
    session_id: str
    token: str
    pid: int
    started_at: str
    authority: str = "GUEST"


def _load_open_sessions() -> Dict[str, Dict]:
    """Load open sessions from disk."""
    if not OPEN_SESSIONS_FILE.exists():
        return {}
    try:
        return json.loads(OPEN_SESSIONS_FILE.read_text())
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Failed to load open_sessions.json: {e}")
        return {}


def _save_open_sessions(sessions: Dict[str, Dict]) -> None:
    """Save open sessions to disk."""
    try:
        OPEN_SESSIONS_FILE.write_text(json.dumps(sessions, indent=2))
    except OSError as e:
        logger.error(f"Failed to save open_sessions.json: {e}")


def open_session(session_id: str, token: str, pid: int, authority: str = "GUEST") -> None:
    """
    Record a session as 'in progress' (called by 000_init).

    This enables Loop Bootstrap: if the process crashes before 999_vault,
    the next startup can detect and recover the orphaned session.

    Args:
        session_id: The session ID from 000_init
        token: The session token issued by AXIS
        pid: Process ID (for detecting crashed processes)
        authority: Authority level (888_JUDGE or GUEST)
    """
    sessions = _load_open_sessions()
    sessions[session_id] = {
        "session_id": session_id,
        "token": token,
        "pid": pid,
        "started_at": datetime.now(timezone.utc).isoformat() + "Z",
        "authority": authority
    }
    _save_open_sessions(sessions)
    logger.info(f"Session opened: {session_id[:8]} (pid={pid})")


def close_session(session_id: str) -> bool:
    """
    Mark a session as sealed (called by 999_vault).

    Removes the session from open_sessions.json after successful sealing.

    Args:
        session_id: The session ID to close

    Returns:
        True if session was found and closed, False otherwise
    """
    sessions = _load_open_sessions()
    if session_id in sessions:
        del sessions[session_id]
        _save_open_sessions(sessions)
        logger.info(f"Session closed: {session_id[:8]}")
        return True
    else:
        logger.warning(f"Session not found in open_sessions: {session_id[:8]}")
        return False


def get_orphaned_sessions(timeout_minutes: int = 30) -> List[Dict[str, Any]]:
    """
    Find sessions that started but never sealed (Loop Bootstrap).

    A session is considered orphaned if:
    1. It's been open longer than timeout_minutes
    2. OR the process ID no longer exists (crashed)

    Args:
        timeout_minutes: How long before a session is considered orphaned

    Returns:
        List of orphaned session dicts
    """
    sessions = _load_open_sessions()
    orphans = []
    now = datetime.now(timezone.utc)

    for session_id, session_data in sessions.items():
        is_orphaned = False
        reason = ""

        # Check 1: Process still running?
        pid = session_data.get("pid", 0)
        if pid and not _pid_exists(pid):
            is_orphaned = True
            reason = f"Process {pid} no longer running"

        # Check 2: Timeout exceeded?
        if not is_orphaned:
            started_at = session_data.get("started_at", "")
            if started_at:
                try:
                    start_time = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                    age_minutes = (now - start_time.replace(tzinfo=None)).total_seconds() / 60
                    if age_minutes > timeout_minutes:
                        is_orphaned = True
                        reason = f"Session open for {age_minutes:.1f} minutes (timeout={timeout_minutes})"
                except (ValueError, TypeError):
                    pass

        if is_orphaned:
            orphans.append({
                **session_data,
                "orphan_reason": reason
            })
            logger.warning(f"Orphaned session detected: {session_id[:8]} - {reason}")

    return orphans


def _pid_exists(pid: int) -> bool:
    """Check if a process ID exists (cross-platform)."""
    if sys.platform == 'win32':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
            if handle:
                kernel32.CloseHandle(handle)
                return True
            return False
        except Exception:
            return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False


def recover_orphaned_session(session_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Auto-seal an orphaned session with SABAR verdict.

    Called during Loop Bootstrap to recover work from crashed sessions.

    Args:
        session_data: The orphaned session dict from get_orphaned_sessions()

    Returns:
        Seal result dict
    """
    session_id = session_data.get("session_id", "UNKNOWN")
    reason = session_data.get("orphan_reason", "Unknown crash")

    # Create minimal telemetry for recovered session
    telemetry = {
        "verdict": "SABAR",
        "recovery": True,
        "orphan_reason": reason,
        "original_started_at": session_data.get("started_at", ""),
        "recovered_at": datetime.now(timezone.utc).isoformat() + "Z"
    }

    # Seal with SABAR (recoverable, needs attention)
    result = seal_memory(
        session_id=session_id,
        verdict="SABAR",
        init_result={"recovered": True, "original_session": session_data},
        genius_result={},
        act_result={},
        judge_result={"synthesis": f"Session recovered after crash: {reason}"},
        telemetry=telemetry,
        context_summary=f"RECOVERED SESSION: {reason}. Original session started at {session_data.get('started_at', 'unknown')}.",
        key_insights=["Session was recovered via Loop Bootstrap", f"Reason: {reason}"]
    )

    # Remove from open sessions
    close_session(session_id)

    logger.info(f"Orphaned session recovered: {session_id[:8]} → SABAR")
    return result


# =============================================================================
# SINGLETON
# =============================================================================

_ledger: Optional[SessionLedger] = None

def get_ledger() -> SessionLedger:
    """Get the singleton session ledger."""
    global _ledger
    if _ledger is None:
        _ledger = SessionLedger()
    return _ledger


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def inject_memory() -> Dict[str, Any]:
    """
    Called by 000_init to inject previous session context.

    Returns:
        Context dict with previous session data
    """
    return get_ledger().get_context_for_init()


def seal_memory(
    session_id: str,
    verdict: str,
    init_result: Dict,
    genius_result: Dict,
    act_result: Dict,
    judge_result: Dict,
    telemetry: Dict,
    context_summary: str = "",
    key_insights: List[str] = None
) -> Dict[str, Any]:
    """
    Called by 999_vault to seal session.

    Returns:
        Seal result with entry hash and merkle root
    """
    entry = get_ledger().seal_session(
        session_id=session_id,
        verdict=verdict,
        init_result=init_result,
        genius_result=genius_result,
        act_result=act_result,
        judge_result=judge_result,
        telemetry=telemetry,
        context_summary=context_summary,
        key_insights=key_insights
    )

    return {
        "sealed": True,
        "session_id": entry.session_id,
        "entry_hash": entry.entry_hash,
        "merkle_root": entry.merkle_root,
        "timestamp": entry.timestamp,
        "verdict": entry.verdict,
        "prev_hash": entry.prev_hash
    }
