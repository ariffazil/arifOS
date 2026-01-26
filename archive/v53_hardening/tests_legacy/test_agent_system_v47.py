#!/usr/bin/env python3
"""
Integration Tests for Model-Agnostic Agent System (v47.0)

Tests the complete agent loading, session management, and validation workflow.

Version: v47.0
"""

import sys
import tempfile
import json
from pathlib import Path
from unittest.mock import patch
import os

# Add arifos_core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from arifos.core.trinity.agent_loader import AgentLoader, AgentConfig
from arifos.core.trinity.session_manager import (
    SessionManager,
    SessionInfo,
    SessionIsolationError,
    AgentSession
)
from arifos.core.trinity.config_validator import ConfigValidator


def test_agent_loader_loads_all_roles():
    """Test that AgentLoader successfully loads all 4 agent roles."""
    print("\n[TEST] Loading all agent configurations...")

    loader = AgentLoader("config/agents.yaml")

    # Test loading each role
    roles = ["architect", "engineer", "auditor", "validator"]
    for role in roles:
        config = loader.get_agent_config(role)

        assert config.role, f"Role '{role}' missing role field"
        assert config.llm_provider, f"Role '{role}' missing LLM provider"
        assert config.llm_model, f"Role '{role}' missing LLM model"
        assert config.workspace, f"Role '{role}' missing workspace"
        assert config.identity_file, f"Role '{role}' missing identity file"

        print(f"  [OK] {role}: {config.llm_provider}/{config.llm_model}")

    print("[PASS] All agent configurations loaded successfully")


def test_identity_files_readable():
    """Test that all identity files can be loaded and are non-empty."""
    print("\n[TEST] Loading identity files...")

    loader = AgentLoader("config/agents.yaml")
    roles = ["architect", "engineer", "auditor", "validator"]

    for role in roles:
        identity = loader.load_identity(role)

        assert identity, f"Identity file empty for role '{role}'"
        assert len(identity) > 100, f"Identity file suspiciously short for '{role}'"

        # Check for key content
        assert ("role" in identity.lower() or "responsibility" in identity.lower() or
                "job" in identity.lower() or "what you do" in identity.lower()), \
            f"Identity file for '{role}' missing role/job/responsibility content"

        print(f"  [OK] {role}: {len(identity)} characters")

    print("[PASS] All identity files loaded and validated")


def test_session_isolation_enforcement():
    """Test that SessionManager enforces role isolation."""
    print("\n[TEST] Session isolation enforcement...")

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SessionManager(lock_dir=tmpdir)

        # Start session for Engineer role
        session1 = manager.start_session(
            role="engineer",
            session_id="test-session-1",
            llm_provider="anthropic",
            llm_model="claude-sonnet-4.5",
            workspace=".claude"
        )

        print(f"  [OK] Started session: {session1.role}")

        # Try to start another session for same role (should fail)
        try:
            session2 = manager.start_session(
                role="engineer",
                session_id="test-session-2",
                llm_provider="anthropic",
                llm_model="claude-sonnet-4.5",
                workspace=".claude"
            )
            raise AssertionError("Should have raised SessionIsolationError")
        except SessionIsolationError as e:
            print(f"  [OK] Isolation enforced: {e}")

        # Start session for different role (should succeed)
        session3 = manager.start_session(
            role="architect",
            session_id="test-session-3",
            llm_provider="google",
            llm_model="gemini-2.5-flash",
            workspace=".antigravity"
        )

        print(f"  [OK] Different role allowed: {session3.role}")

        # Cleanup
        manager.close_session("engineer")
        manager.close_session("architect")

    print("[PASS] Session isolation working correctly")


def test_context_manager_cleanup():
    """Test that AgentSession context manager cleans up properly."""
    print("\n[TEST] Context manager cleanup...")

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SessionManager(lock_dir=tmpdir)

        # Use context manager
        with AgentSession(
            manager=manager,
            role="engineer",
            session_id="test-context",
            llm_provider="anthropic",
            llm_model="claude-sonnet-4.5",
            workspace=".claude"
        ) as session:
            print(f"  [OK] Session started: {session.session_id}")
            assert "engineer" in manager.active_sessions

        # After context exit, session should be closed
        assert "engineer" not in manager.active_sessions
        print("  [OK] Session cleaned up after context exit")

    print("[PASS] Context manager cleanup working")


def test_stale_lock_cleanup():
    """Test cleanup of stale lock files."""
    print("\n[TEST] Stale lock cleanup...")

    with tempfile.TemporaryDirectory() as tmpdir:
        lock_dir = Path(tmpdir)
        manager = SessionManager(lock_dir=str(lock_dir))

        # Create a fake stale lock file with non-existent PID
        stale_lock = lock_dir / "engineer.lock"
        stale_data = {
            "role": "engineer",
            "session_id": "stale-session",
            "llm_provider": "anthropic",
            "llm_model": "claude-sonnet-4.5",
            "pid": 999999,  # Non-existent PID
            "started_at": "2026-01-01T00:00:00",
            "workspace": ".claude"
        }

        with open(stale_lock, 'w', encoding='utf-8') as f:
            json.dump(stale_data, f)

        print(f"  [OK] Created stale lock: {stale_lock.name}")

        # Mock _pid_exists to return False for our test PID
        original_pid_exists = manager._pid_exists
        def mock_pid_exists(pid):
            if pid == 999999:
                return False  # Our test PID is stale
            return original_pid_exists(pid)

        manager._pid_exists = mock_pid_exists

        # Cleanup should remove it
        removed = manager.cleanup_stale_locks()
        assert removed == 1, f"Expected 1 lock removed, got {removed}"
        assert not stale_lock.exists(), "Stale lock not removed"

        print(f"  [OK] Removed {removed} stale lock(s)")

    print("[PASS] Stale lock cleanup working")


def test_separation_of_powers_validation():
    """Test that separation of powers is validated."""
    print("\n[TEST] Separation of powers validation...")

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SessionManager(lock_dir=tmpdir)

        # Start sessions for different roles
        manager.start_session(
            role="architect",
            session_id="session-1",
            llm_provider="google",
            llm_model="gemini-2.5-flash",
            workspace=".antigravity"
        )

        manager.start_session(
            role="engineer",
            session_id="session-2",
            llm_provider="anthropic",
            llm_model="claude-sonnet-4.5",
            workspace=".claude"
        )

        # Should be valid (different roles)
        is_valid = manager.validate_separation_of_powers()
        assert is_valid, "Separation of powers should be valid"

        print("  [OK] Separation of powers validated")

        # Cleanup
        manager.close_session("architect")
        manager.close_session("engineer")

    print("[PASS] Separation of powers validation working")


def test_config_validation():
    """Test configuration validation against constitutional requirements."""
    print("\n[TEST] Configuration validation...")

    validator = ConfigValidator("config/agents.yaml")
    is_valid, errors, warnings = validator.validate()

    # Should pass (warnings about API keys are OK)
    assert is_valid, f"Configuration validation failed: {errors}"

    print(f"  [OK] Configuration valid (0 errors, {len(warnings)} warnings)")

    # Warnings should be about API keys only
    for warning in warnings:
        assert "API_KEY" in warning or "api_key" in warning.lower(), \
            f"Unexpected warning: {warning}"

    print("[PASS] Configuration validation working")


def test_floor_requirements():
    """Test that floor assignments match constitutional requirements."""
    print("\n[TEST] Constitutional floor requirements...")

    loader = AgentLoader("config/agents.yaml")

    # Engineer must have F1, F2, F5
    engineer = loader.get_agent_config("engineer")
    required_engineer_floors = {"F1", "F2", "F5"}
    engineer_floors = set(engineer.floors)

    assert required_engineer_floors.issubset(engineer_floors), \
        f"Engineer missing required floors: {required_engineer_floors - engineer_floors}"

    print(f"  [OK] Engineer has required floors: {', '.join(required_engineer_floors)}")

    # Validator must have all 12 floors
    validator = loader.get_agent_config("validator")
    all_floors = {f"F{i}" for i in range(1, 13)}
    validator_floors = set(validator.floors)

    assert validator_floors == all_floors, \
        f"Validator missing floors: {all_floors - validator_floors}"

    print(f"  [OK] Validator has all 12 floors")

    # Auditor must have F8
    auditor = loader.get_agent_config("auditor")
    assert "F8" in auditor.floors, "Auditor missing F8 (Tri-Witness)"

    print(f"  [OK] Auditor has F8 (Tri-Witness)")

    # Architect must have F4, F7
    architect = loader.get_agent_config("architect")
    required_architect_floors = {"F4", "F7"}
    architect_floors = set(architect.floors)

    assert required_architect_floors.issubset(architect_floors), \
        f"Architect missing required floors: {required_architect_floors - architect_floors}"

    print(f"  [OK] Architect has required floors: {', '.join(required_architect_floors)}")

    print("[PASS] All floor requirements satisfied")


def test_workspace_mapping():
    """Test that workspace directories are correctly mapped."""
    print("\n[TEST] Workspace mapping...")

    loader = AgentLoader("config/agents.yaml")

    expected_workspaces = {
        "architect": ".antigravity",
        "engineer": ".claude",
        "auditor": ".codex",
        "validator": ".kimi"
    }

    for role, expected_workspace in expected_workspaces.items():
        config = loader.get_agent_config(role)
        actual_workspace = str(config.workspace)

        assert expected_workspace in actual_workspace, \
            f"Role '{role}' workspace mismatch: expected '{expected_workspace}', got '{actual_workspace}'"

        print(f"  [OK] {role}: {config.workspace}")

    print("[PASS] All workspaces correctly mapped")


def test_handoff_protocol_simulation():
    """Test simulated handoff between Architect → Engineer → Auditor."""
    print("\n[TEST] Handoff protocol simulation...")

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SessionManager(lock_dir=tmpdir)
        loader = AgentLoader("config/agents.yaml")

        # Architect session (design phase)
        print("\n  Phase 1: Architect designs...")
        with AgentSession(
            manager=manager,
            role="architect",
            session_id="design-phase",
            llm_provider="google",
            llm_model="gemini-2.5-flash",
            workspace=".antigravity"
        ) as architect_session:
            architect_config = loader.get_agent_config("architect")
            print(f"    [OK] Architect active: {architect_config.llm_provider}/{architect_config.llm_model}")
            assert architect_session.role == "architect"

        # Engineer session (implementation phase)
        print("\n  Phase 2: Engineer implements...")
        with AgentSession(
            manager=manager,
            role="engineer",
            session_id="implementation-phase",
            llm_provider="anthropic",
            llm_model="claude-sonnet-4.5",
            workspace=".claude"
        ) as engineer_session:
            engineer_config = loader.get_agent_config("engineer")
            print(f"    [OK] Engineer active: {engineer_config.llm_provider}/{engineer_config.llm_model}")
            assert engineer_session.role == "engineer"

        # Auditor session (review phase)
        print("\n  Phase 3: Auditor reviews...")
        with AgentSession(
            manager=manager,
            role="auditor",
            session_id="review-phase",
            llm_provider="openai",
            llm_model="gpt-4",
            workspace=".codex"
        ) as auditor_session:
            auditor_config = loader.get_agent_config("auditor")
            print(f"    [OK] Auditor active: {auditor_config.llm_provider}/{auditor_config.llm_model}")
            assert auditor_session.role == "auditor"

        print("\n  [OK] All phases completed successfully")

    print("[PASS] Handoff protocol simulation successful")


def run_all_tests():
    """Run all integration tests."""
    print("=" * 80)
    print("arifOS Model-Agnostic Agent System Integration Tests (v47.0)")
    print("=" * 80)

    tests = [
        test_agent_loader_loads_all_roles,
        test_identity_files_readable,
        test_session_isolation_enforcement,
        test_context_manager_cleanup,
        test_stale_lock_cleanup,
        test_separation_of_powers_validation,
        test_config_validation,
        test_floor_requirements,
        test_workspace_mapping,
        test_handoff_protocol_simulation
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\n[FAIL] {test.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 80)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 80)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
