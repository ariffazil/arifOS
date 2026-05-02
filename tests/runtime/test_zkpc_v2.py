import pytest
import os
import json
from arifos.tools import _888_judge, _999_vault


# Verify No F14 exists in judge or vault code
def test_no_f14_drift():
    with open("/root/arifOS/arifos/tools/_888_judge.py", "r") as f:
        content = f.read()
        assert "F14" not in content, "F14 drift detected in _888_judge.py"

    with open("/root/arifOS/arifos/tools/_999_vault.py", "r") as f:
        content = f.read()
        assert "F14" not in content, "F14 drift detected in _999_vault.py"


@pytest.mark.asyncio
async def test_judge_zkpc_level_0():
    evidence_bundle = {
        "is_irreversible": True,
        "zkpc_level": 0,
        "metrics": {
            "truth_score": 1.0,
            "delta_s": 0.0,
            "omega_0": 0.04,
            "peace_squared": 1.0,
            "amanah_lock": True,
            "tri_witness_score": 1.0,
            "stakeholder_safety": 1.0,
            "floor_13_signal": 0.0,
        },
    }
    res = await _888_judge.execute(evidence_bundle)
    assert res["verdict"] == "888_HOLD"
    assert "F1_AMANAH_ZKPC" in res["rationale"]


@pytest.mark.asyncio
async def test_judge_zkpc_level_1():
    evidence_bundle = {
        "is_irreversible": True,
        "zkpc_level": 1,
        "metrics": {
            "truth_score": 1.0,
            "delta_s": 0.0,
            "omega_0": 0.04,
            "peace_squared": 1.0,
            "amanah_lock": True,
            "tri_witness_score": 1.0,
            "stakeholder_safety": 1.0,
            "floor_13_signal": 0.0,
        },
    }
    res = await _888_judge.execute(evidence_bundle)
    assert res["verdict"] == "888_HOLD"
    assert "F1_AMANAH_ZKPC" in res["rationale"]


@pytest.mark.asyncio
async def test_judge_zkpc_level_2_proof_verified_false():
    evidence_bundle = {
        "is_irreversible": True,
        "zkpc_level": 2,
        "proof_verified": False,
        "continuity_proven": True,
        "epoch_chain_valid": True,
        "signal_binding_valid": True,
        "nonce_valid": True,
        "metrics": {
            "truth_score": 1.0,
            "delta_s": 0.0,
            "omega_0": 0.04,
            "peace_squared": 1.0,
            "amanah_lock": True,
            "tri_witness_score": 1.0,
            "stakeholder_safety": 1.0,
            "floor_13_signal": 0.0,
        },
    }
    res = await _888_judge.execute(evidence_bundle)
    assert res["verdict"] == "888_HOLD"
    assert "F1_AMANAH_ZKPC" in res["rationale"]


@pytest.mark.asyncio
async def test_judge_zkpc_level_2_epoch_chain_invalid():
    evidence_bundle = {
        "is_irreversible": True,
        "zkpc_level": 2,
        "proof_verified": True,
        "continuity_proven": True,
        "epoch_chain_valid": False,
        "signal_binding_valid": True,
        "nonce_valid": True,
        "metrics": {
            "truth_score": 1.0,
            "delta_s": 0.0,
            "omega_0": 0.04,
            "peace_squared": 1.0,
            "amanah_lock": True,
            "tri_witness_score": 1.0,
            "stakeholder_safety": 1.0,
            "floor_13_signal": 0.0,
        },
    }
    res = await _888_judge.execute(evidence_bundle)
    assert res["verdict"] == "888_HOLD"


@pytest.mark.asyncio
async def test_judge_zkpc_level_2_signal_binding_invalid():
    evidence_bundle = {
        "is_irreversible": True,
        "zkpc_level": 2,
        "proof_verified": True,
        "continuity_proven": True,
        "epoch_chain_valid": True,
        "signal_binding_valid": False,
        "nonce_valid": True,
        "metrics": {
            "truth_score": 1.0,
            "delta_s": 0.0,
            "omega_0": 0.04,
            "peace_squared": 1.0,
            "amanah_lock": True,
            "tri_witness_score": 1.0,
            "stakeholder_safety": 1.0,
            "floor_13_signal": 0.0,
        },
    }
    res = await _888_judge.execute(evidence_bundle)
    assert res["verdict"] == "888_HOLD"


@pytest.mark.asyncio
async def test_judge_zkpc_level_2_all_flags_true():
    evidence_bundle = {
        "is_irreversible": True,
        "zkpc_level": 2,
        "proof_verified": True,
        "continuity_proven": True,
        "epoch_chain_valid": True,
        "signal_binding_valid": True,
        "nonce_valid": True,
        "metrics": {
            "truth_score": 1.0,
            "delta_s": 0.0,
            "omega_0": 0.04,
            "peace_squared": 1.0,
            "amanah_lock": True,
            "tri_witness_score": 1.0,
            "stakeholder_safety": 1.0,
            "floor_13_signal": 0.0,
        },
    }
    res = await _888_judge.execute(evidence_bundle)
    assert res["verdict"] == "SEAL"


@pytest.mark.asyncio
async def test_vault_rejects_natural_language_and_actor_id(monkeypatch):
    monkeypatch.setenv("ARIFOS_DEV_ALLOW_MSAP_LEVEL2", "false")
    payload = {"approval_text": "I approve", "ack_irreversible": True, "data": "important_action"}
    res = await _999_vault.execute(
        action="seal", payload=payload, operator_id="ARIF", session_id="SESS-1"
    )
    assert res["verdict"] == "888_HOLD"
    assert res["ack_irreversible_received"] is False


@pytest.mark.asyncio
async def test_vault_zkpc_v2_success(monkeypatch):
    monkeypatch.setenv("ARIFOS_DEV_ALLOW_MSAP_LEVEL2", "false")
    monkeypatch.setenv("ARIFOS_DEV_ALLOW_STRUCTURAL_ZKPC", "true")

    proof = {"pi_a": ["1", "2"], "pi_b": [["1", "2"], ["3", "4"]], "pi_c": ["1", "2"]}
    public_inputs = {
        "identity_commitment": "id_commit",
        "previous_epoch_hash": "prev_hash",
        "current_epoch_hash": "curr_hash",
        "nonce": "nonce_123",
        "payload_hash": "payload_hash_123",
        "judge_state_hash": "judge_hash_123",
        "signal_hash": "signal_hash_123",
        "secret": "THIS_SHOULD_NEVER_BE_HERE",  # pragma: allowlist secret
    }

    res = await _999_vault.execute(
        action="seal",
        payload={"data": "test"},
        operator_id="ARIF",
        session_id="SESS-123",
        zkpc_proof=proof,
        zkpc_public_inputs=public_inputs,
    )

    assert res["verdict"] == "SEAL"
    assert res["ack_irreversible_received"] is True

    # Check vault metadata stores hashes only, NO secrets
    # We must read the vault file directly or check internal metadata.
    # In this test, we can check the payload output structure.

    # Wait, the vault writes to a file. Let's read the last line of the vault file.

    vault_file = _999_vault.VAULT999_FILE
    if os.path.exists(vault_file):
        with open(vault_file, "r") as f:
            lines = f.readlines()
            if lines:
                last_entry = json.loads(lines[-1])
                zkpc_meta = last_entry.get("zkpc_metadata", {})
                assert "secret" not in zkpc_meta
                assert zkpc_meta.get("identity_commitment") == "id_commit"
                assert zkpc_meta.get("proof_hash") is not None
