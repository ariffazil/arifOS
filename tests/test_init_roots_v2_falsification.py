"""
test_init_roots_v2_falsification.py — Falsification suite for arifOS INIT v2 Roots
═════════════════════════════════════════════════════════════════════════════════

Tests:
  1. Four roots present and well-formed in INIT payload.
  2. Four roots hashed at session birth (init_roots_hash / genesis_state_hash).
  3. Validate contract works without requiring repeated actor_id (inferred from session).
  4. Validate contract rejects actor_id mismatch.
  5. PROVENANCE_ROOT state_hash is deterministically reconstructable.
  6. NEGATIVE_KNOWLEDGE active gate rejects unmeasured scalar assertions into VOID_t.

DITEMPA BUKAN DIBERI ⚒️
"""

import pytest
from arifosmcp.tools.session import arif_init, reconstruct_provenance_hash
from arifosmcp.core.negative_knowledge_gate import evaluate_negative_knowledge
from arifosmcp.core.claim_class_gate import evaluate as evaluate_claim


def test_init_v2_roots_persistence_and_provenance_reconstruction():
    # 1. Birth session with explicit task
    res = arif_init(
        actor_id="arif",
        mode="init",
        objective="Reconcile CHRON and verify federation roots",
    )
    res_d = res.model_dump() if hasattr(res, "model_dump") else res
    assert res_d["status"] == "OK"
    sid = res_d["session_id"]
    header = res_d.get("result", {})

    # Verify roots presence
    roots = header.get("init_v2_roots")
    assert roots is not None
    assert "TEMPORAL_ROOT" in roots
    assert "OBJECTIVE_ROOT" in roots
    assert "NEGATIVE_KNOWLEDGE" in roots
    assert "PROVENANCE_ROOT" in roots

    # Verify genesis hash
    init_hash = header.get("init_roots_hash")
    genesis_hash = header.get("genesis_state_hash")
    assert init_hash is not None
    assert init_hash.startswith("sha256:")
    assert init_hash == genesis_hash

    # Verify PROVENANCE reconstructability
    prov = roots["PROVENANCE_ROOT"]
    reconstructed_hash = reconstruct_provenance_hash(prov)
    assert reconstructed_hash == prov["state_hash"]

    # Verify validate contract without repeating actor_id
    val = arif_init(mode="validate", session_id=sid)
    val_d = val.model_dump() if hasattr(val, "model_dump") else val
    assert val_d["status"] == "OK"
    val_res = val_d.get("result", {})
    assert val_res.get("valid") is True
    assert val_res.get("roots_verified") is True
    assert val_res.get("init_roots_hash") == init_hash

    # Verify validate with matching actor_id
    val_match = arif_init(mode="validate", session_id=sid, actor_id="arif")
    assert val_match.status == "OK"

    # Verify validate rejects mismatching actor_id
    val_mismatch = arif_init(mode="validate", session_id=sid, actor_id="unauthorized_actor")
    assert val_mismatch.status == "HOLD"


def test_negative_knowledge_active_gate_computational_void():
    # Valid empirical claim passes
    valid_claim = evaluate_negative_knowledge(
        "NTP sync offset is 0.134ms from chronyc tracking",
        declared_class="MEASURED",
    )
    assert valid_claim["passed"] is True

    # Claim asserting unmeasured scalar as fact fails into VOID_t
    unmeasured_claim = evaluate_negative_knowledge(
        "Scalar G is measured at 0.95 across benchmark runs",
        declared_class="MEASURED",
    )
    assert unmeasured_claim["passed"] is False
    assert unmeasured_claim["allowed_for_mutation"] is False
    assert unmeasured_claim["void_entry"]["verdict"] == "VOID_t"
    assert "G" in unmeasured_claim["void_entry"]["unjustified_scalars"]

    # Claim class gate integration rejects mutation
    gate_res = evaluate_claim(
        "Scalar W3 is measured at 0.88 across nodes",
        declared_class="MEASURED",
    )
    assert gate_res["eligible"] is False
    assert gate_res["allowed_for_mutation"] is False
    assert "void_entry" in gate_res
