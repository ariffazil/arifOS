"""
Unit tests for P36 Dignity & P40 Consequence Gates
Verifies the operationalization of the Humanity / Carrying Capacity Cluster in arifOS.
"""

import pytest
from arifosmcp.runtime.consequence_gate import evaluate_consequence
from arifosmcp.runtime.dignity_gate import evaluate_dignity


def test_agent_cannot_self_authorize_irreversible_drop():
    """Agent A trying to drop table without sovereign sign-off triggers 888_HOLD."""
    action = {
        "action_type": "drop_table",
        "target": "users_and_claims",
        "action_class": "T3",
        "has_rollback_proof": False
    }
    result = evaluate_consequence(action, caller="333_agi_worker")
    assert result.verdict == "888_HOLD"
    assert result.is_irreversible is True
    assert result.requires_human_f13 is True
    assert "Consequence is non-delegable" in result.reason


def test_human_sovereign_can_authorize_irreversible_action():
    """Human sovereign Arif can authorize irreversible action and carries consequence."""
    action = {
        "action_type": "drop_table",
        "target": "temporary_legacy_table",
        "action_class": "T3",
        "has_rollback_proof": False
    }
    result = evaluate_consequence(action, caller="arif")
    assert result.verdict == "PASS"
    assert result.is_irreversible is True
    assert "Human sovereign carries moral and operational consequence" in result.reason


def test_reversible_action_auto_passes():
    """Reversible action with rollback proof passes autonomously."""
    action = {
        "action_type": "update_config",
        "action_class": "T1",
        "has_rollback_proof": True
    }
    result = evaluate_consequence(action, caller="777_forge")
    assert result.verdict == "PASS"
    assert result.is_irreversible is False


def test_h5_scar_blocked_from_public_telemetry():
    """Private human scar cannot be leaked to public logs."""
    content = "Detailed personal trauma notes regarding scar-042"
    result = evaluate_dignity(content, surface_type="public_log", data_classification="H5")
    assert result.verdict == "888_HOLD"
    assert result.contains_private_scars is True
    assert result.sanitized_output == "[REDACTED_H5_SOVEREIGN_SCAR]"


def test_machine_labels_sanitized_on_human_surface():
    """Machine labels [OBS], [ACT], [DER] are sanitized on human chat surfaces."""
    content = "[OBS] The system load is normal. [DER] We should proceed."
    result = evaluate_dignity(content, surface_type="human_chat", data_classification="PUBLIC")
    assert result.verdict == "SANITIZED"
    assert result.label_leak_detected is True
    assert "[OBS]" not in result.sanitized_output
    assert "[DER]" not in result.sanitized_output
    assert "The system load is normal.  We should proceed." in result.sanitized_output
