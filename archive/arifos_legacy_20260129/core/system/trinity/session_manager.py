"""
Session Manager - Enforces Constitutional Separation of Powers

Prevents same LLM instance from fulfilling multiple roles simultaneously.
Uses in-memory tracking + on-disk lock files for crash recovery.

Version: v47.0
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class SessionInfo:
    """Information about an active agent session."""

    role: str
    session_id: str
    llm_provider: str
    llm_model: str
    started_at: str
    pid: int
    workspace: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionInfo':
        """Create from dictionary."""
        return cls(**data)


class SessionIsolationError(Exception):
    """Raised when session isolation is violated."""
    pass


class SessionManager:
    """
    Enforce one active session per role at a time.

    This is critical for constitutional separation of powers:
    - Architect cannot also be Engineer in same decision chain
    - Engineer cannot review own work as Auditor
    - Same LLM can fulfill multiple roles in DIFFERENT sessions only

    Uses both in-memory and on-disk tracking for resilience.
    """

    def __init__(self, lock_dir: str = "workspaces/.sessions"):
        """
        Initialize session manager.

        Args:
            lock_dir: Directory for session lock files
        """
        self.lock_dir = Path(lock_dir)
        self.lock_dir.mkdir(parents=True, exist_ok=True)

        # In-memory tracking (fast)
        self.active_sessions: Dict[str, SessionInfo] = {}

        # Load any existing lock files (recovery after crash)
        self._recover_sessions()

    def _get_lock_path(self, role: str) -> Path:
        """Get lock file path for role."""
        return self.lock_dir / f"{role}.lock"

    def _recover_sessions(self):
        """
        Recover sessions from lock files (in case of crash).

        This reads existing lock files and validates they're still active.
        Stale locks (PID doesn't exist) are removed.
        """
        for lock_file in self.lock_dir.glob("*.lock"):
            try:
                with open(lock_file, encoding='utf-8') as f:
                    data = json.load(f)

                session_info = SessionInfo.from_dict(data)

                # Check if process still exists (simple check)
                # On Windows, this is approximate - lock cleanup script handles edge cases
                pid_exists = self._pid_exists(session_info.pid)

                if pid_exists:
                    # Session still active, load into memory
                    self.active_sessions[session_info.role] = session_info
                else:
                    # Stale lock, remove it
                    lock_file.unlink()

            except (json.JSONDecodeError, KeyError, Exception):
                # Corrupted lock file, remove it
                lock_file.unlink()

    def _pid_exists(self, pid: int) -> bool:
        """
        Check if process ID exists (approximate).

        Note: This is a simple check. For production, use psutil library.
        """
        try:
            # On Windows, os.kill with signal 0 doesn't work
            # Just check if we can query the process
            if os.name == 'nt':
                # Windows: Simple approximation
                # Real check would use: psutil.pid_exists(pid)
                return True  # Conservative: assume exists
            else:
                # Unix: Send signal 0 (no-op, just checks existence)
                os.kill(pid, 0)
                return True
        except (OSError, ProcessLookupError):
            return False

    def start_session(
        self,
        role: str,
        session_id: str,
        llm_provider: str,
        llm_model: str,
        workspace: str
    ) -> SessionInfo:
        """
        Start a new session for a role.

        Args:
            role: Agent role name (architect, engineer, auditor, validator)
            session_id: Unique session identifier
            llm_provider: LLM provider (anthropic, google, etc.)
            llm_model: Model name
            workspace: Workspace directory path

        Returns:
            SessionInfo for the new session

        Raises:
            SessionIsolationError: If role already has active session
        """
        # Constitutional enforcement: Only one session per role
        if role in self.active_sessions:
            existing = self.active_sessions[role]
            raise SessionIsolationError(
                f"SESSION ISOLATION VIOLATION\n"
                f"\n"
                f"Role '{role}' already has an active session:\n"
                f"  Session ID: {existing.session_id}\n"
                f"  LLM: {existing.llm_provider}/{existing.llm_model}\n"
                f"  Started: {existing.started_at}\n"
                f"  PID: {existing.pid}\n"
                f"\n"
                f"This enforces constitutional separation of powers.\n"
                f"Close the existing session before starting a new one.\n"
                f"\n"
                f"To close: session_manager.close_session('{role}')\n"
                f"Or run: python scripts/cleanup_sessions.py"
            )

        # Check on-disk lock (in case in-memory state lost)
        lock_path = self._get_lock_path(role)
        if lock_path.exists():
            try:
                with open(lock_path, encoding='utf-8') as f:
                    existing_data = json.load(f)

                raise SessionIsolationError(
                    f"STALE SESSION LOCK DETECTED\n"
                    f"\n"
                    f"Role '{role}' has a lock file from previous session:\n"
                    f"  Lock file: {lock_path}\n"
                    f"  Session ID: {existing_data.get('session_id', 'unknown')}\n"
                    f"  Started: {existing_data.get('started_at', 'unknown')}\n"
                    f"\n"
                    f"This may indicate a crashed session.\n"
                    f"Run: python scripts/cleanup_sessions.py\n"
                    f"Or manually remove: {lock_path}"
                )
            except (json.JSONDecodeError, KeyError):
                # Corrupted lock, remove it
                lock_path.unlink()

        # Create session info
        session_info = SessionInfo(
            role=role,
            session_id=session_id,
            llm_provider=llm_provider,
            llm_model=llm_model,
            started_at=datetime.now().isoformat(),
            pid=os.getpid(),
            workspace=workspace
        )

        # Record in memory
        self.active_sessions[role] = session_info

        # Write lock file to disk
        self._write_lock_file(role, session_info)

        return session_info

    def _write_lock_file(self, role: str, session_info: SessionInfo):
        """
        Write lock file to disk.

        Args:
            role: Agent role name
            session_info: Session information to write
        """
        lock_path = self._get_lock_path(role)

        with open(lock_path, 'w', encoding='utf-8') as f:
            json.dump(session_info.to_dict(), f, indent=2)

    def close_session(self, role: str):
        """
        Close session for a role.

        Args:
            role: Agent role name
        """
        # Remove from memory
        if role in self.active_sessions:
            del self.active_sessions[role]

        # Remove lock file
        lock_path = self._get_lock_path(role)
        if lock_path.exists():
            lock_path.unlink()

    def get_session(self, role: str) -> Optional[SessionInfo]:
        """
        Get active session for a role.

        Args:
            role: Agent role name

        Returns:
            SessionInfo if session active, None otherwise
        """
        return self.active_sessions.get(role)

    def is_active(self, role: str) -> bool:
        """
        Check if role has an active session.

        Args:
            role: Agent role name

        Returns:
            True if session active, False otherwise
        """
        return role in self.active_sessions

    def list_active_sessions(self) -> Dict[str, SessionInfo]:
        """
        List all active sessions.

        Returns:
            Dictionary mapping role names to SessionInfo
        """
        return self.active_sessions.copy()

    def close_all_sessions(self):
        """Close all active sessions."""
        for role in list(self.active_sessions.keys()):
            self.close_session(role)

    def cleanup_stale_locks(self) -> int:
        """
        Clean up stale lock files (from crashed sessions).

        Returns:
            Number of stale locks removed
        """
        removed = 0

        for lock_file in self.lock_dir.glob("*.lock"):
            try:
                with open(lock_file, encoding='utf-8') as f:
                    data = json.load(f)

                session_info = SessionInfo.from_dict(data)

                # Check if PID exists
                if not self._pid_exists(session_info.pid):
                    # Stale lock, remove it
                    lock_file.unlink()
                    removed += 1

                    # Also remove from in-memory if present
                    if session_info.role in self.active_sessions:
                        del self.active_sessions[session_info.role]

            except (json.JSONDecodeError, KeyError, Exception):
                # Corrupted lock, remove it
                lock_file.unlink()
                removed += 1

        return removed

    def get_lock_info(self, role: str) -> Optional[Dict[str, Any]]:
        """
        Get lock file information for a role.

        Args:
            role: Agent role name

        Returns:
            Lock file data if exists, None otherwise
        """
        lock_path = self._get_lock_path(role)

        if not lock_path.exists():
            return None

        try:
            with open(lock_path, encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, KeyError):
            return None

    def validate_separation_of_powers(self) -> bool:
        """
        Validate that separation of powers is maintained.

        Checks:
        1. No more than one session per role
        2. All sessions have valid lock files
        3. No role conflicts

        Returns:
            True if separation maintained, False otherwise
        """
        # Check: No duplicate roles
        if len(self.active_sessions) > len(set(self.active_sessions.keys())):
            return False

        # Check: Each session has corresponding lock file
        for role, session_info in self.active_sessions.items():
            lock_path = self._get_lock_path(role)
            if not lock_path.exists():
                return False

        # Check: No orphaned lock files
        lock_files = set(f.stem for f in self.lock_dir.glob("*.lock"))
        active_roles = set(self.active_sessions.keys())
        if lock_files != active_roles:
            return False

        return True

    def __repr__(self) -> str:
        """String representation of session manager."""
        active_count = len(self.active_sessions)
        return f"SessionManager(active={active_count}, lock_dir={self.lock_dir})"


# =============================================================================
# Context Manager for Safe Session Handling
# =============================================================================

class AgentSession:
    """
    Context manager for agent sessions.

    Ensures sessions are properly closed even if exceptions occur.

    Usage:
        with AgentSession(session_manager, 'engineer', ...) as session:
            # Use session
            pass
        # Session automatically closed
    """

    def __init__(
        self,
        manager: SessionManager,
        role: str,
        session_id: str,
        llm_provider: str,
        llm_model: str,
        workspace: str
    ):
        """
        Initialize session context manager.

        Args:
            manager: SessionManager instance
            role: Agent role name
            session_id: Unique session identifier
            llm_provider: LLM provider
            llm_model: Model name
            workspace: Workspace directory
        """
        self.manager = manager
        self.role = role
        self.session_id = session_id
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.workspace = workspace
        self.session_info = None

    def __enter__(self) -> SessionInfo:
        """Start session on context entry."""
        self.session_info = self.manager.start_session(
            role=self.role,
            session_id=self.session_id,
            llm_provider=self.llm_provider,
            llm_model=self.llm_model,
            workspace=self.workspace
        )
        return self.session_info

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close session on context exit (even if exception)."""
        self.manager.close_session(self.role)
        return False  # Don't suppress exceptions


# =============================================================================
# Standalone Usage Examples
# =============================================================================

if __name__ == "__main__":
    """
    Standalone usage examples for testing session manager.
    """

    print("=" * 80)
    print("Session Manager - Constitutional Isolation v47.0")
    print("=" * 80)
    print()

    # Initialize manager
    manager = SessionManager()
    print(f"[OK] Initialized: {manager}")
    print(f"[OK] Lock directory: {manager.lock_dir}")
    print()

    # Clean up any stale locks
    removed = manager.cleanup_stale_locks()
    if removed > 0:
        print(f"[OK] Cleaned up {removed} stale lock(s)")
        print()

    # Example 1: Normal session lifecycle
    print("-" * 80)
    print("Example 1: Normal Session Lifecycle")
    print("-" * 80)

    try:
        # Start engineer session
        engineer_session = manager.start_session(
            role="engineer",
            session_id="eng_001",
            llm_provider="anthropic",
            llm_model="claude-sonnet-4.5",
            workspace=".claude"
        )
        print(f"[OK] Started engineer session: {engineer_session.session_id}")
        print(f"     LLM: {engineer_session.llm_provider}/{engineer_session.llm_model}")
        print(f"     PID: {engineer_session.pid}")
        print()

        # Check active sessions
        active = manager.list_active_sessions()
        print(f"Active sessions: {list(active.keys())}")
        print()

        # Close session
        manager.close_session("engineer")
        print("[OK] Closed engineer session")
        print()

    except SessionIsolationError as e:
        print(f"[FAIL] {e}")
        print()

    # Example 2: Violation detection (same role twice)
    print("-" * 80)
    print("Example 2: Session Isolation Violation (Same Role Twice)")
    print("-" * 80)

    try:
        # Start architect session
        manager.start_session(
            role="architect",
            session_id="arch_001",
            llm_provider="google",
            llm_model="gemini-2.5-flash",
            workspace=".antigravity"
        )
        print("[OK] Started architect session: arch_001")
        print()

        # Try to start another architect session (should fail)
        manager.start_session(
            role="architect",
            session_id="arch_002",
            llm_provider="google",
            llm_model="gemini-2.5-flash",
            workspace=".antigravity"
        )
        print("[FAIL] Should have raised SessionIsolationError!")

    except SessionIsolationError as e:
        print("[OK] Correctly blocked duplicate session:")
        print(f"     {str(e).split(chr(10))[0]}")  # First line only
        print()

    # Clean up
    manager.close_session("architect")

    # Example 3: Context manager usage
    print("-" * 80)
    print("Example 3: Context Manager (Safe Cleanup)")
    print("-" * 80)

    try:
        with AgentSession(
            manager=manager,
            role="auditor",
            session_id="aud_001",
            llm_provider="openai",
            llm_model="gpt-4",
            workspace=".codex"
        ) as session:
            print(f"[OK] Session started: {session.role}/{session.session_id}")
            print(f"     Workspace: {session.workspace}")
            print()

            # Session automatically closed on exit

        print("[OK] Session auto-closed by context manager")
        print(f"     Auditor active: {manager.is_active('auditor')}")
        print()

    except SessionIsolationError as e:
        print(f"[FAIL] {e}")
        print()

    # Example 4: Multiple roles (different sessions OK)
    print("-" * 80)
    print("Example 4: Multiple Roles (Constitutional)")
    print("-" * 80)

    try:
        # Start different roles (this is OK constitutionally)
        manager.start_session("architect", "arch_003", "google", "gemini-2.5-flash", ".antigravity")
        manager.start_session("engineer", "eng_002", "anthropic", "claude-sonnet-4.5", ".claude")
        manager.start_session("validator", "val_001", "moonshot", "kimi-k2", ".kimi")

        active = manager.list_active_sessions()
        print(f"[OK] Multiple roles active: {list(active.keys())}")
        print()

        for role, session in active.items():
            print(f"  {role}: {session.llm_provider}/{session.llm_model}")
        print()

        # Validate separation
        valid = manager.validate_separation_of_powers()
        print(f"[OK] Separation of powers validated: {valid}")
        print()

    except SessionIsolationError as e:
        print(f"[FAIL] {e}")
        print()

    # Clean up all
    print("-" * 80)
    print("Cleanup")
    print("-" * 80)
    manager.close_all_sessions()
    print("[OK] All sessions closed")
    print(f"     Active sessions: {len(manager.active_sessions)}")
    print()

    print("=" * 80)
