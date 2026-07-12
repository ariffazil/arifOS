"""
Adversarial Test Suite — WS3 forge_preflight Chain
═══════════════════════════════════════════════════════════════

Tests (3 of 10 from WS3 §3.3 acceptance):

  - Gate 11: forged judge_state_hash → HOLD (preflight catches the forgery)
  - Gate 12: replayed vault receipt → HOLD (chain-walked fails; replay rejected)
  - Gate 13: expired session token → HOLD (step 1 fails)

Each test produces: case_id, expected final_gate, actual final_gate, PASS/FAIL.
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import pytest

# WS8 (2026-07-12) refactored forge_preflight into per-stage functions.
# The legacy single-function API (ForgePreflightReceipt, forge_preflight)
# was replaced. Tests adapt to whatever API surfaces exist; failing
# gracefully where the older dataclass is gone.
try:
    from arifosmcp.runtime.forge_preflight import (
        ForgePreflightReceipt,
        forge_preflight,
    )
except ImportError:
    from arifosmcp.runtime.forge_preflight import (
        run_forge_preflight as forge_preflight,
    )
    ForgePreflightReceipt = None  # dataclass removed in WS8



def _check(receipt, expected_gate: str, case_id: str) -> dict:
    actual = receipt.final_gate
    passed = actual == expected_gate
    return {
        "case_id": case_id,
        "expected_final_gate": expected_gate,
        "actual_final_gate": actual,
        "passed": passed,
        "judge_state_forged": receipt.judge_state_forged,
        "vault_chain_ok": receipt.vault_chain_walked_to_genesis,
        "step_pass_map": dict(receipt.step_pass),
    }


def test_gate_11_forged_judge_state_hash_rejected():
    """Caller asserts a judge_state_hash that does NOT match recomputed hash.
    forge_preflight MUST set judge_state_forged=True and final_gate=HOLD."""
    r = forge_preflight(
        session_id="sess_forged_test",
        actor_id="arif",
        plan_id="plan_forged",
        claimed_judge_state_hash="FORGED_AAAA_DEADBEEF",
        requested_action="write",
    )
    assert r.judge_state_forged is True, (
        f"Forged hash was not detected: judge_state_forged=False (hash={r.judge_state_hash})"
    )
    assert r.final_gate == "HOLD", f"Forged hash did not block execution: final_gate={r.final_gate}"
    assert r.step_pass.get("5_judge_hash") is False, "step 5 should fail on forged hash"
    summary = _check(r, "HOLD", "gate_11_forged_judge_state_hash")
    assert summary["passed"], f"Gate 11 failed: {summary}"


def test_gate_12_replayed_vault_receipt_rejected():
    """Caller asserts a vault entry id that does not exist in the chain.
    forge_preflight MUST fail step 7 and final_gate=HOLD."""
    r = forge_preflight(
        session_id="sess_replay_test",
        actor_id="arif",
        plan_id="plan_replay",
        claimed_vault_entry_id="vault_does_not_exist_0001",
        requested_action="delete",
    )
    assert r.vault_chain_walked_to_genesis is False, (
        f"Phantom vault entry walked the chain: vault_chain_walked_to_genesis=True"
    )
    assert r.final_gate == "HOLD", f"Replay not rejected: final_gate={r.final_gate}"
    assert r.step_pass.get("7_vault") is False, "step 7 should fail on phantom vault entry"
    summary = _check(r, "HOLD", "gate_12_replayed_vault_receipt")
    assert summary["passed"], f"Gate 12 failed: {summary}"


def test_gate_13_expired_session_rejected():
    """Caller provides an empty/expired session_id.
    forge_preflight MUST fail step 1 and final_gate=HOLD."""
    r = forge_preflight(
        session_id="sess_does_not_exist_and_is_expired_xxxx",
        actor_id="arif",
        plan_id="plan_expired",
        requested_action="commit",
    )
    assert r.step_pass.get("1_session_token") is False, (
        "Step 1 (session-token validation) should fail on expired/missing session"
    )
    assert r.final_gate == "HOLD", (
        f"Expired session did not block execution: final_gate={r.final_gate}"
    )
    summary = _check(r, "HOLD", "gate_13_expired_session")
    assert summary["passed"], f"Gate 13 failed: {summary}"


def test_forge_preflight_deterministic_id_under_same_inputs():
    """compute_preflight_id must be deterministic for the same tuple.
    A forged preflight_id is rejected by recomputation."""
    from arifosmcp.runtime.forge_preflight import compute_preflight_id

    id_a = compute_preflight_id("sess_1", "arif", "plan_1")
    id_b = compute_preflight_id("sess_1", "arif", "plan_1")
    id_c = compute_preflight_id("sess_1", "attacker", "plan_1")
    assert id_a == id_b
    assert id_a != id_c


def test_forge_preflight_irreversible_action_requires_ack():
    """Irreversible action (rm/delete/drop) should require a human-ack token.
    Without it, preflight MUST HOLD on step 10."""
    r_no_ack = forge_preflight(
        session_id="sess_irrev",
        actor_id="arif",
        plan_id="plan_irrev",
        requested_action="delete",
    )
    assert r_no_ack.human_ack_required is True
    assert r_no_ack.human_ack_valid is False
    assert r_no_ack.step_pass.get("10_human_ack") is False
    assert r_no_ack.final_gate == "HOLD"
