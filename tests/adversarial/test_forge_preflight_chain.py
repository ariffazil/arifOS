"""
Adversarial Test Suite — WS3 forge_preflight Chain

Tests (3 of 10 from WS3 §3.3 acceptance):

  - Gate 11: forged judge_state_hash → HOLD (preflight catches the forgery)
  - Gate 12: replayed vault receipt → HOLD (chain-walked fails; replay rejected)
  - Gate 13: expired session token → HOLD (step 1 fails)

Each test produces: case_id, expected final_gate, actual final_gate, PASS/FAIL.
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime.forge_preflight import run_forge_preflight as forge_preflight


def _check(receipt: dict, expected_gate: str, case_id: str) -> dict:
    actual = receipt.get("final_gate", "UNKNOWN")
    passed = actual == expected_gate
    return {
        "case_id": case_id,
        "expected_final_gate": expected_gate,
        "actual_final_gate": actual,
        "passed": passed,
        "judge_state_forged": not receipt.get("judge_hash_match", True),
        "vault_chain_ok": receipt.get("vault_receipt_valid", False),
        "step_pass_map": {},
    }


def test_gate_11_forged_judge_state_hash_rejected():
    r = forge_preflight(
        session_id="sess_forged_test",
        actor_id="arif",
        plan_id="plan_forged",
        judge_state_hash="FORGED_AAAA_DEADBEEF",
    )
    assert r.get("judge_hash_match") is False, (
        f"Forged hash was not detected: judge_hash_match should be False, got {r.get('judge_hash_match')}"
    )
    assert r.get("final_gate") == "HOLD", f"Forged hash did not block: {r}"
    summary = _check(r, "HOLD", "gate_11_forged_judge_state_hash")
    assert summary["passed"], f"Gate 11 failed: {summary}"


def test_gate_12_replayed_vault_receipt_rejected():
    r = forge_preflight(
        session_id="sess_replay_test",
        actor_id="arif",
        plan_id="plan_replay",
        vault_entry_id="vault_does_not_exist_0001",
    )
    assert r.get("vault_receipt_valid") is False, (
        f"Phantom vault entry walked: vault_receipt_valid should be False"
    )
    assert r.get("final_gate") == "HOLD", f"Replay not rejected: {r}"
    summary = _check(r, "HOLD", "gate_12_replayed_vault_receipt")
    assert summary["passed"], f"Gate 12 failed: {summary}"


def test_gate_13_expired_session_rejected():
    r = forge_preflight(
        session_id="sess_does_not_exist_and_is_expired_xxxx",
        actor_id="arif",
        plan_id="plan_expired",
    )
    assert r.get("session_valid") is False, (
        "Step 1 (session-token validation) should fail on expired/missing session"
    )
    assert r.get("final_gate") == "HOLD", f"Expired session did not block: {r}"
    summary = _check(r, "HOLD", "gate_13_expired_session")
    assert summary["passed"], f"Gate 13 failed: {summary}"


def test_forge_preflight_irreversible_action_requires_ack():
    r_no_ack = forge_preflight(
        session_id="sess_irrev",
        actor_id="arif",
        plan_id="plan_irrev",
        ack_irreversible=False,
    )
    assert r_no_ack.get("human_ack_required") is True
    assert r_no_ack.get("human_ack_valid") is False
    assert r_no_ack.get("final_gate") == "HOLD"
