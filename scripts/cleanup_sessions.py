#!/usr/bin/env python3
"""
Session Cleanup Utility

Cleans up stale session lock files from crashed agent sessions.

Usage:
    python scripts/cleanup_sessions.py              # Interactive cleanup
    python scripts/cleanup_sessions.py --force      # Force cleanup without prompt
    python scripts/cleanup_sessions.py --status     # Show status only

Version: v47.0
"""

import sys
import argparse
from pathlib import Path

# Add arifos_core to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from arifos_core.trinity.session_manager import SessionManager


def show_status(manager: SessionManager):
    """
    Show current session status.

    Args:
        manager: SessionManager instance
    """
    print("=" * 80)
    print("Session Status")
    print("=" * 80)
    print()

    # Active sessions
    active = manager.list_active_sessions()

    if active:
        print(f"Active sessions: {len(active)}")
        print()

        for role, session in active.items():
            print(f"  Role: {role}")
            print(f"    Session ID: {session.session_id}")
            print(f"    LLM: {session.llm_provider}/{session.llm_model}")
            print(f"    Started: {session.started_at}")
            print(f"    PID: {session.pid}")
            print(f"    Workspace: {session.workspace}")
            print()
    else:
        print("No active sessions.")
        print()

    # Lock files
    lock_files = list(manager.lock_dir.glob("*.lock"))

    if lock_files:
        print(f"Lock files: {len(lock_files)}")
        print()

        for lock_file in lock_files:
            lock_info = manager.get_lock_info(lock_file.stem)
            if lock_info:
                print(f"  {lock_file.name}:")
                print(f"    Role: {lock_info.get('role', 'unknown')}")
                print(f"    Session ID: {lock_info.get('session_id', 'unknown')}")
                print(f"    Started: {lock_info.get('started_at', 'unknown')}")
                print(f"    PID: {lock_info.get('pid', 'unknown')}")
                print()
    else:
        print("No lock files found.")
        print()

    # Validation
    valid = manager.validate_separation_of_powers()
    status = "[OK] VALID" if valid else "[FAIL] INVALID"
    print(f"Separation of powers: {status}")
    print()


def cleanup_sessions(manager: SessionManager, force: bool = False) -> int:
    """
    Clean up stale session locks.

    Args:
        manager: SessionManager instance
        force: If True, skip confirmation prompt

    Returns:
        Number of locks removed
    """
    # Check for stale locks
    lock_files = list(manager.lock_dir.glob("*.lock"))

    if not lock_files:
        print("[OK] No lock files to clean up.")
        return 0

    print(f"Found {len(lock_files)} lock file(s).")
    print()

    # Show what will be cleaned
    stale_count = 0
    for lock_file in lock_files:
        lock_info = manager.get_lock_info(lock_file.stem)
        if lock_info:
            pid = lock_info.get('pid', 'unknown')
            pid_exists = manager._pid_exists(pid) if isinstance(pid, int) else False

            if not pid_exists:
                stale_count += 1
                print(f"  Stale: {lock_file.name}")
                print(f"    Role: {lock_info.get('role', 'unknown')}")
                print(f"    PID: {pid} (process not found)")
                print()

    if stale_count == 0:
        print("[OK] All lock files appear valid (processes still running).")
        print()
        print("NOTE: Lock files with running PIDs were NOT removed.")
        print("      If these are actually stale, close the agent sessions manually.")
        return 0

    # Confirm cleanup
    if not force:
        print(f"Will remove {stale_count} stale lock file(s).")
        response = input("Continue? [y/N]: ").strip().lower()

        if response not in ('y', 'yes'):
            print("Cancelled.")
            return 0

    # Perform cleanup
    removed = manager.cleanup_stale_locks()

    print()
    print(f"[OK] Removed {removed} stale lock file(s).")

    return removed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Clean up stale agent session lock files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/cleanup_sessions.py              # Interactive cleanup
  python scripts/cleanup_sessions.py --force      # Force cleanup
  python scripts/cleanup_sessions.py --status     # Show status only

Constitutional Context:
  Session lock files enforce separation of powers by preventing
  the same LLM from fulfilling multiple roles simultaneously.

  Stale locks occur when:
  - Agent process crashes
  - System reboots
  - Manual termination (Ctrl+C)

  This script safely removes locks where the process no longer exists.
        """
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Skip confirmation prompt'
    )

    parser.add_argument(
        '--status',
        action='store_true',
        help='Show status only (no cleanup)'
    )

    parser.add_argument(
        '--lock-dir',
        default='workspaces/.sessions',
        help='Lock file directory (default: workspaces/.sessions)'
    )

    args = parser.parse_args()

    # Initialize session manager
    try:
        manager = SessionManager(lock_dir=args.lock_dir)
    except Exception as e:
        print(f"[FAIL] Error initializing session manager: {e}")
        return 1

    # Show status
    show_status(manager)

    # Status only mode
    if args.status:
        return 0

    # Cleanup mode
    try:
        removed = cleanup_sessions(manager, force=args.force)

        if removed > 0:
            print()
            print("=" * 80)
            print("Updated Status")
            print("=" * 80)
            print()
            show_status(manager)

        return 0

    except KeyboardInterrupt:
        print()
        print("Cancelled by user.")
        return 130

    except Exception as e:
        print(f"[FAIL] Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
