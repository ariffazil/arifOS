"""R1 — SE stage engine unit tests.

Law: stage stays at 000 until a full proof bundle is admissible.
Manual bumps are VOID. Illegal advances HOLD.

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime.se_stage_engine import (
    SE_STAGE_INIT,
    SE_STAGE_SENSE,
    IdentityCoherence,
    SotProof,
    SpineProof,
    StageProofBundle,
    get_se_stage,
    reset_for_tests,
    set_stage_manual,
    try_advance,
)


@pytest.fixture(autouse=True)
def _clean_stage():
    reset_for_tests()
    yield
    reset_for_tests()


def _good_bundle(target: str = SE_STAGE_SENSE) -> StageProofBundle:
    return StageProofBundle(
        identity=IdentityCoherence(
            standing_actor="ARIF",
            birth_actor="ARIF",
            sct_claims_actor="ARIF",
        ),
        spine=SpineProof(
            all_green=True,
            skipped=0,
            substrate_gate="GREEN",
            vault_replay_pass=True,
            fast_mode=False,
            score="9/9",
            constitutional_grade=True,
        ),
        sot=SotProof(
            active=True,
            sot_id="apex-sot-v2",
            sot_hash="sha256:deadbeef",
            hold_reason="",
        ),
        target_stage=target,
        issuer="unit-test",
    )


def test_default_stage_is_000():
    st = get_se_stage()
    assert st["se_stage"] == SE_STAGE_INIT
    assert st["at_init"] is True


def test_manual_bump_is_void():
    result = set_stage_manual("111", actor="attacker")
    assert result["verdict"] == "VOID"
    assert result["reason"] == "manual_stage_bump_forbidden"
    assert get_se_stage()["se_stage"] == SE_STAGE_INIT


def test_illegal_advance_without_identity():
    b = _good_bundle()
    bad = StageProofBundle(
        identity=IdentityCoherence("ARIF", "AGENT", "ARIF"),
        spine=b.spine,
        sot=b.sot,
        target_stage=SE_STAGE_SENSE,
    )
    result = try_advance(bad)
    assert result["verdict"] == "HOLD"
    assert "identity_incoherent" in result["reasons"]
    assert result["advanced"] is False
    assert get_se_stage()["se_stage"] == SE_STAGE_INIT


def test_illegal_advance_fast_mode_spine():
    b = _good_bundle()
    bad = StageProofBundle(
        identity=b.identity,
        spine=SpineProof(
            all_green=True,
            skipped=0,
            substrate_gate="GREEN",
            vault_replay_pass=True,
            fast_mode=True,  # forbidden
            score="2/9",
        ),
        sot=b.sot,
        target_stage=SE_STAGE_SENSE,
    )
    result = try_advance(bad)
    assert result["verdict"] == "HOLD"
    assert "spine_fast_mode_forbidden" in result["reasons"]
    assert get_se_stage()["se_stage"] == SE_STAGE_INIT


def test_illegal_advance_skipped_checks():
    b = _good_bundle()
    bad = StageProofBundle(
        identity=b.identity,
        spine=SpineProof(
            all_green=False,
            skipped=7,
            substrate_gate="AMBER",
            vault_replay_pass=True,
            fast_mode=False,
        ),
        sot=b.sot,
        target_stage=SE_STAGE_SENSE,
    )
    result = try_advance(bad)
    assert result["verdict"] == "HOLD"
    assert any("spine_skipped" in r for r in result["reasons"])


def test_illegal_advance_vault_fail():
    b = _good_bundle()
    bad = StageProofBundle(
        identity=b.identity,
        spine=SpineProof(
            all_green=True,
            skipped=0,
            substrate_gate="GREEN",
            vault_replay_pass=False,
            fast_mode=False,
        ),
        sot=b.sot,
        target_stage=SE_STAGE_SENSE,
    )
    result = try_advance(bad)
    assert result["verdict"] == "HOLD"
    assert "vault_replay_not_pass" in result["reasons"]


def test_illegal_advance_sot_missing():
    b = _good_bundle()
    bad = StageProofBundle(
        identity=b.identity,
        spine=b.spine,
        sot=SotProof(active=False, hold_reason="sot_not_active"),
        target_stage=SE_STAGE_SENSE,
    )
    result = try_advance(bad)
    assert result["verdict"] == "HOLD"
    assert "sot_not_active" in result["reasons"]


def test_legal_advance_with_full_proof():
    result = try_advance(_good_bundle())
    assert result["verdict"] == "SEAL"
    assert result["advanced"] is True
    assert result["current_stage"] == SE_STAGE_SENSE
    assert get_se_stage()["se_stage"] == SE_STAGE_SENSE
    assert get_se_stage()["proof_digest"]


def test_cannot_skip_stages():
    # First hop 000→111 ok
    assert try_advance(_good_bundle())["advanced"] is True
    # Skip to 333 without 222 — HOLD
    skip = StageProofBundle(
        identity=IdentityCoherence("ARIF", "ARIF", "ARIF"),
        spine=SpineProof(
            all_green=True,
            skipped=0,
            substrate_gate="GREEN",
            vault_replay_pass=True,
            fast_mode=False,
        ),
        sot=SotProof(active=True, sot_id="apex-sot-v2", sot_hash="sha256:x"),
        target_stage="333",
    )
    result = try_advance(skip)
    assert result["verdict"] == "HOLD"
    assert any("not_adjacent_hop" in r for r in result["reasons"])
    assert get_se_stage()["se_stage"] == SE_STAGE_SENSE
