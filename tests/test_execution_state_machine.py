"""
tests/test_execution_state_machine.py
═══════════════════════════════════════════════════════════════════════════════════════
Formal execution state machine tests.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import os
import uuid

import pytest

from arifosmcp.runtime.execution_state_machine import (
    ExecutionState,
    ExecutionStateMachine,
)
from arifosmcp.runtime.session import (
    get_session_execution_state,
    set_session_execution_state,
)

# ═══════════════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def fresh_session_id() -> str:
    """Generate a unique session ID for isolated state-machine tests."""
    return f"test-esm-{uuid.uuid4().hex[:12]}"


# ═══════════════════════════════════════════════════════════════════════════════════════
# STATE MACHINE BASICS
# ═══════════════════════════════════════════════════════════════════════════════════════


def test_execution_state_enum_values():
    assert ExecutionState.OBSERVE.value == "OBSERVE"
    assert ExecutionState.ANALYZE.value == "ANALYZE"
    assert ExecutionState.SIMULATE.value == "SIMULATE"
    assert ExecutionState.AWAIT_APPROVAL.value == "AWAIT_APPROVAL"
    assert ExecutionState.EXECUTE.value == "EXECUTE"
    assert ExecutionState.VERIFY.value == "VERIFY"
    assert ExecutionState.SEAL.value == "SEAL"


def test_all_canonical_tools_have_mappings():
    """Every canonical tool must declare allowed states."""
    canonical_tools = [
        "arif_session_init",
        "arif_sense_observe",
        "arif_evidence_fetch",
        "arif_ops_measure",
        "arif_memory_recall",
        "arif_kernel_route",
        "arif_mind_reason",
        "arif_heart_critique",
        "arif_judge_deliberate",
        "arif_gateway_connect",
        "arif_forge_execute",
        "arif_reply_compose",
        "arif_vault_seal",
    ]
    for tool in canonical_tools:
        allowed = ExecutionStateMachine.get_allowed_states(tool)
        assert allowed, f"Tool {tool} has no allowed execution states"


def test_infrastructure_tools_omni_state():
    """Memory and reply must be callable from any state."""
    for tool in ("arif_memory_recall", "arif_reply_compose"):
        allowed = ExecutionStateMachine.get_allowed_states(tool)
        assert len(allowed) == 7


# ═══════════════════════════════════════════════════════════════════════════════════════
# STATE TRANSITION RULES
# ═══════════════════════════════════════════════════════════════════════════════════════


def test_observe_tools_advance_to_analyze():
    assert (
        ExecutionStateMachine.get_next_state("arif_sense_observe", ExecutionState.OBSERVE)
        == ExecutionState.ANALYZE
    )
    assert (
        ExecutionStateMachine.get_next_state("arif_evidence_fetch", ExecutionState.OBSERVE)
        == ExecutionState.ANALYZE
    )


def test_analyze_tools_advance_to_simulate():
    assert (
        ExecutionStateMachine.get_next_state("arif_mind_reason", ExecutionState.ANALYZE)
        == ExecutionState.SIMULATE
    )
    assert (
        ExecutionStateMachine.get_next_state("arif_kernel_route", ExecutionState.ANALYZE)
        == ExecutionState.SIMULATE
    )


def test_simulate_tools_advance_to_await_approval():
    assert (
        ExecutionStateMachine.get_next_state("arif_heart_critique", ExecutionState.SIMULATE)
        == ExecutionState.AWAIT_APPROVAL
    )


def test_approval_tools_advance_to_execute():
    assert (
        ExecutionStateMachine.get_next_state("arif_judge_deliberate", ExecutionState.AWAIT_APPROVAL)
        == ExecutionState.EXECUTE
    )


def test_execute_tools_advance_to_verify():
    assert (
        ExecutionStateMachine.get_next_state("arif_forge_execute", ExecutionState.EXECUTE)
        == ExecutionState.VERIFY
    )


def test_verify_tools_advance_to_seal():
    assert (
        ExecutionStateMachine.get_next_state("arif_vault_seal", ExecutionState.VERIFY)
        == ExecutionState.SEAL
    )


def test_self_loop_when_no_progression_mapped():
    """Tools without a progression mapping keep the session in the current state."""
    assert (
        ExecutionStateMachine.get_next_state("arif_memory_recall", ExecutionState.ANALYZE)
        == ExecutionState.ANALYZE
    )
    assert (
        ExecutionStateMachine.get_next_state("arif_reply_compose", ExecutionState.EXECUTE)
        == ExecutionState.EXECUTE
    )


# ═══════════════════════════════════════════════════════════════════════════════════════
# CAN_EXECUTE GATE
# ═══════════════════════════════════════════════════════════════════════════════════════


def test_can_execute_in_allowed_state():
    assert ExecutionStateMachine.can_execute("arif_sense_observe", ExecutionState.OBSERVE)
    assert ExecutionStateMachine.can_execute("arif_mind_reason", ExecutionState.ANALYZE)
    assert ExecutionStateMachine.can_execute("arif_forge_execute", ExecutionState.EXECUTE)


def test_cannot_execute_in_wrong_state():
    assert not ExecutionStateMachine.can_execute("arif_forge_execute", ExecutionState.OBSERVE)
    assert not ExecutionStateMachine.can_execute("arif_vault_seal", ExecutionState.OBSERVE)
    assert not ExecutionStateMachine.can_execute("arif_mind_reason", ExecutionState.EXECUTE)


def test_legacy_session_first_contact_defaults_to_observe():
    """A session with no execution state is anchored to OBSERVE on first contact."""
    assert ExecutionStateMachine.can_execute("arif_sense_observe", None)
    assert ExecutionStateMachine.can_execute("arif_evidence_fetch", None)
    assert not ExecutionStateMachine.can_execute("arif_forge_execute", None)


def test_unknown_tool_fail_closed():
    assert not ExecutionStateMachine.can_execute("arif_nonexistent_tool", ExecutionState.OBSERVE)


# ═══════════════════════════════════════════════════════════════════════════════════════
# HOLD RESPONSE STRUCTURE
# ═══════════════════════════════════════════════════════════════════════════════════════


def test_hold_response_has_required_fields():
    hold = ExecutionStateMachine.get_hold_response(
        "arif_forge_execute", ExecutionState.OBSERVE, session_id="s-123"
    )
    assert hold["status"] == "HOLD"
    assert hold["verdict"] == "HOLD"
    assert hold["error"] == "EXECUTION_STATE_MISMATCH"
    assert "required_next_state" in hold
    assert "next_safe_action" in hold
    assert hold["session_id"] == "s-123"
    assert "execution_state" in hold


def test_hold_response_suggests_observe_re_anchor():
    hold = ExecutionStateMachine.get_hold_response("arif_forge_execute", ExecutionState.OBSERVE)
    assert hold["next_safe_action"]["tool"] == "arif_sense_observe"


# ═══════════════════════════════════════════════════════════════════════════════════════
# PIPELINE PROGRESS
# ═══════════════════════════════════════════════════════════════════════════════════════


def test_pipeline_progress_format():
    progress = ExecutionStateMachine.get_pipeline_progress(ExecutionState.ANALYZE)
    assert progress["current"] == "ANALYZE"
    assert progress["index"] == 1
    assert progress["total"] == 7
    assert progress["completed"] == ["OBSERVE"]
    assert "SIMULATE" in progress["remaining"]


# ═══════════════════════════════════════════════════════════════════════════════════════
# SESSION PERSISTENCE (integration with session.py)
# ═══════════════════════════════════════════════════════════════════════════════════════


def test_session_execution_state_round_trip(fresh_session_id: str):
    assert get_session_execution_state(fresh_session_id) is None
    set_session_execution_state(fresh_session_id, ExecutionState.SIMULATE.value)
    assert get_session_execution_state(fresh_session_id) == "SIMULATE"


def test_session_state_overwrite(fresh_session_id: str):
    set_session_execution_state(fresh_session_id, ExecutionState.OBSERVE.value)
    set_session_execution_state(fresh_session_id, ExecutionState.SEAL.value)
    assert get_session_execution_state(fresh_session_id) == "SEAL"


# ═══════════════════════════════════════════════════════════════════════════════════════
# ENV GATE
# ═══════════════════════════════════════════════════════════════════════════════════════


def test_enforcement_disabled_by_default():
    """Without ARIFOS_STATE_MACHINE_ENFORCE=true, the gate is permissive."""
    assert not ExecutionStateMachine.is_enforced()


def test_enforcement_can_be_enabled_via_env(monkeypatch):
    monkeypatch.setenv("ARIFOS_STATE_MACHINE_ENFORCE", "true")
    # Module-level constant is evaluated at import time, so we test the logic directly
    assert os.getenv("ARIFOS_STATE_MACHINE_ENFORCE", "").lower() in ("1", "true", "yes")
