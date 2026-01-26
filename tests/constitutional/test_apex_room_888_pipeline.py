"""
APEX Room (777→999) integration tests.

These tests ensure:
- 888 JUDGE produces a meaningful p(truth) and a stable verdict struct
- 889 PROOF produces a verifiable Ed25519 signature over the merkle root
- 999 SEAL writes a sealed entry via the session ledger
"""

from __future__ import annotations

import uuid

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from arifos.core.apex.kernel import APEXJudicialCore


def _stub_agi() -> dict:
    return {"status": "SEAL", "think": {"confidence": 0.995}}


def _stub_asi() -> dict:
    return {"status": "SEAL", "empathy": {"kappa_r": 0.97}, "evidence": {"truth_score": 0.99}}


def test_apex_room_888_judge_and_889_proof_roundtrip() -> None:
    apex = APEXJudicialCore()
    session_id = str(uuid.uuid4())

    verdict_struct = apex.judge_888(
        session_id=session_id,
        query="Is this compliant?",
        response="Here is a careful, bounded answer. Alternatively, you could also ask for a stricter mode.",
        agi_result=_stub_agi(),
        asi_result=_stub_asi(),
        user_id="test_user",
        lane="SOFT",
    )

    assert verdict_struct["verdict"] in {"SEAL", "SABAR", "VOID", "PARTIAL", "888_HOLD"}
    assert verdict_struct["verdict"] == "SEAL"
    assert verdict_struct["p_truth"] >= 0.99

    proof = apex.proof_889(session_id=session_id, verdict_struct=verdict_struct)
    assert proof["merkle_root"]
    assert proof["signature_ed25519"]
    assert proof["public_key_ed25519"]

    pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(proof["public_key_ed25519"]))
    pub.verify(bytes.fromhex(proof["signature_ed25519"]), proof["merkle_root"].encode("utf-8"))


@pytest.mark.asyncio
async def test_apex_room_999_seal_writes_entry() -> None:
    apex = APEXJudicialCore()
    session_id = str(uuid.uuid4())

    verdict_struct = apex.judge_888(
        session_id=session_id,
        query="Is this compliant?",
        response="Here is a careful, bounded answer. Alternatively, you could also ask for a stricter mode.",
        agi_result=_stub_agi(),
        asi_result=_stub_asi(),
        user_id="test_user",
        lane="SOFT",
    )

    sealed = await apex.seal_999(
        session_id=session_id,
        verdict_struct=verdict_struct,
        init_result={"status": "SEAL", "session_id": session_id, "lane": "SOFT"},
        agi_result=_stub_agi(),
        asi_result=_stub_asi(),
    )

    assert sealed["status"] == "SEALED"
    assert sealed["seal"]["sealed"] is True
    assert sealed["seal"]["session_id"] == session_id
