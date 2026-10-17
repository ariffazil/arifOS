"""Reality/authority separation (2026-10-17).

External assessment: "completed + HOLD + next-action" was ambiguous, and the
next agent could read HOLD as "nothing happened". The wire now carries three
distinct signals:
  status        — did execution finish?
  result_state  — is there a result payload?
  hold_scope    — what is held: MUTATION, EXECUTION, or NONE?
"""

from __future__ import annotations

from arifosmcp.runtime.verbosity import trim_for_verbosity


def _minimal(resp: dict) -> dict:
    return trim_for_verbosity(resp, "minimal")


def test_completed_read_is_result_ready_but_mutation_held():
    resp = {
        "tool": "arif_observe",
        "status": "completed",
        "effective_verdict": "HOLD",
        "execution_state": "AWAIT_INPUT",
        "result": {"cpu": 12.0},
        "risk": {"action_class": "OBSERVE"},
        "session_id": "s-probe",
    }
    out = _minimal(resp)
    assert out["status"] == "completed"
    assert out["execution_state"] == "AWAIT_INPUT"
    assert out["result_state"] == "RESULT_READY"
    assert out["hold_scope"] == "MUTATION"


def test_blocked_mutation_has_no_result():
    resp = {
        "tool": "arif_forge",
        "status": "HOLD",
        "effective_verdict": "HOLD",
        "execution_state": "AWAIT_INPUT",
        "result": None,
        "risk": {"action_class": "EXECUTE"},
        "session_id": "s-probe",
    }
    out = _minimal(resp)
    assert out["result_state"] == "NO_RESULT"
    assert out["hold_scope"] == "EXECUTION"


def test_clean_seal_has_no_hold_scope():
    resp = {
        "tool": "arif_seal",
        "status": "completed",
        "effective_verdict": "SEAL",
        "result": {"sealed": True},
        "risk": {"action_class": "IRREVERSIBLE"},
        "session_id": "s-probe",
    }
    out = _minimal(resp)
    assert out["result_state"] == "RESULT_READY"
    assert out["hold_scope"] == "NONE"
