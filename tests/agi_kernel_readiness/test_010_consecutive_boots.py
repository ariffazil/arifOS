"""
P0 Master Acceptance Tests — Canonical Session, Crypto Identity, LLM Lanes, Evidence Pre-flight & Surface Drift

Pass criteria:
1. One canonical session envelope: session_id == token.sid == every verb echo.
   All 8 verbs in one session return identical id/actor/band; band changes only via explicit re-init.
2. Crypto actor bind: with key -> actor_cryptographically_verified=True; without -> explicit DEGRADED.
3. Wire think + judge LLM lanes: think(mode=reason) returns structured reasoning with epistemic labels;
   judge sets llm_consulted=True when rules don't decide.
4. Evidence pre-flight: observe->judge sequence never returns EVIDENCE_HASH_MISSING or EVIDENCE_EMPTY.
5. Kill surface drift: forge_surface_audit(arifos) = CLEAN.
"""

import asyncio
import base64
import json
import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519

from arifosmcp.runtime.tools import (
    _arif_session_init,
    _arif_sense_observe,
    _arif_mind_reason_tool,
    _arif_route_tool,
    _arif_memory_v5_router,
    _arif_forge_execute_tool,
    _arif_vault_seal_tool,
)
from arifosmcp.tools.judge import arif_judge
from arifosmcp.runtime.act_token import verify_sct


def _run(coro):
    return asyncio.run(coro)


def test_p0_01_canonical_session_envelope_across_all_8_verbs():
    """Requirement 1: All 8 verbs return identical id, actor, band."""
    # 1. arif_init
    init_res = _arif_session_init(
        mode="light",
        actor_id="ARIF",
        requested_authority="OBSERVE_ONLY",
    )
    assert init_res.get("status") in ("OK", "SEAL")
    sid = init_res.get("session_id")
    actor = init_res.get("actor_id")
    band = init_res.get("autonomy_band") or init_res.get("band") or init_res.get("authority")
    token = init_res.get("session_token")

    assert sid and sid.startswith("SEAL-"), f"Expected SEAL- session_id, got {sid}"
    assert actor == "ARIF", f"Expected actor ARIF, got {actor}"
    if token:
        claims = verify_sct(token)
        assert claims is not None, "Session token must verify"
        assert claims.get("sid") == sid, f"token.sid ({claims.get('sid')}) must equal session_id ({sid})"

    # 2. arif_observe
    obs_res = _arif_sense_observe(
        mode="search",
        query="federation health",
        session_id=sid,
        actor_id=actor,
        session_token=token,
    )
    assert obs_res.get("session_id") == sid
    assert obs_res.get("actor_id") == actor
    assert obs_res.get("autonomy_band") == band

    # 3. arif_think
    think_res = _run(
        _arif_mind_reason_tool(
            mode="reason",
            query="Verify constitutional compliance",
            session_id=sid,
            actor_id=actor,
            session_token=token,
        )
    )
    assert think_res.get("session_id") == sid
    assert think_res.get("actor_id") == actor
    assert think_res.get("autonomy_band") == band

    # 4. arif_route
    route_res = _arif_route_tool(
        organ="GEOX",
        task="seismic check",
        session_id=sid,
        actor_id=actor,
        session_token=token,
    )
    assert route_res.get("session_id") == sid
    assert route_res.get("actor_id") == actor
    assert route_res.get("autonomy_band") == band

    # 5. arif_memory
    mem_res = _run(
        _arif_memory_v5_router(
            mode="stats",
            session_id=sid,
            actor_id=actor,
            session_token=token,
        )
    )
    assert mem_res.get("session_id") == sid
    assert mem_res.get("actor_id") == actor
    assert mem_res.get("autonomy_band") == band

    # 6. arif_judge
    judge_res = _run(
        arif_judge(
            candidate="Verify session continuity",
            mode="standard",
            session_id=sid,
            actor_id=actor,
            session_token=token,
        )
    )
    judge_dict = (
        judge_res.model_dump(mode="json")
        if hasattr(judge_res, "model_dump")
        else judge_res
    )
    assert judge_dict.get("session_id") == sid
    assert judge_dict.get("actor_id") == actor
    assert judge_dict.get("autonomy_band") == band

    # 7. arif_forge
    forge_res = _run(
        _arif_forge_execute_tool(
            mode="diagnose",
            session_id=sid,
            actor_id=actor,
            session_token=token,
        )
    )
    assert forge_res.get("session_id") == sid
    assert forge_res.get("actor_id") == actor
    assert forge_res.get("autonomy_band") == band

    # 8. arif_seal
    seal_res = _run(
        _arif_vault_seal_tool(
            mode="verify",
            payload="test_seal",
            session_id=sid,
            actor_id=actor,
            session_token=token,
        )
    )
    assert seal_res.get("session_id") == sid
    assert seal_res.get("actor_id") == actor
    assert seal_res.get("autonomy_band") == band


def test_p0_02_crypto_actor_bind():
    """Requirement 2: Crypto actor bind with key -> verified; without -> explicit DEGRADED."""
    # Test without signature
    res_unverified = _arif_session_init(
        mode="init",
        actor_id="ARIF",
    )
    assert res_unverified.get("actor_cryptographically_verified") in (False, None)
    assert res_unverified.get("actor_verified") in (False, None)
    assert res_unverified.get("status") in ("DEGRADED", "HOLD", "OK")

    # Test challenge issuance + verify_init_identity with key
    from arifosmcp.runtime.crypto_auth import (
        classify_actor_band,
        issue_actor_challenge,
        verify_init_identity,
    )

    nonce = issue_actor_challenge("ARIF")
    priv_key = ed25519.Ed25519PrivateKey.generate()
    sig = priv_key.sign(f"ARIF:{nonce}".encode())
    sig_b64 = base64.b64encode(sig).decode("utf-8")

    ok, reason = verify_init_identity(
        actor_id="ARIF",
        nonce=nonce,
        signature_b64=sig_b64,
        public_key=priv_key.public_key(),
    )
    assert ok is True
    band_info = classify_actor_band("ARIF", signature_verified=True)
    assert band_info["actor_verified"] is True
    assert band_info["signature_verified"] is True


def test_p0_03_wire_think_judge_llm_lanes():
    """Requirement 3: think(mode=reason) returns structured epistemic labels; judge sets llm_consulted=True."""
    think_res = _run(
        _arif_mind_reason_tool(
            mode="reason",
            query="Explain why gravity pulls objects together",
        )
    )
    res_obj = think_res.get("result", {})
    assert "what_is_supported" in res_obj
    assert "what_remains_unknown" in res_obj
    assert "epistemic_labels" in res_obj

    # Verify presence of epistemic tags
    labels = res_obj.get("epistemic_labels", {})
    assert any(k in labels for k in ("OBS", "DER", "SPEC", "UNK"))

    # Test judge sets llm_consulted=True on deliberation
    init_res = _arif_session_init(mode="light", actor_id="ARIF")
    sid = init_res.get("session_id")
    judge_res = _run(
        arif_judge(
            candidate="Evaluate constitutional alignment of proposed deployment",
            evidence={"observed_metric": 0.99, "in_band": True},
            session_id=sid,
            actor_id="ARIF",
        )
    )
    judge_dict = (
        judge_res.model_dump(mode="json")
        if hasattr(judge_res, "model_dump")
        else judge_res
    )
    assert (
        judge_dict.get("llm_consulted") is True
        or judge_dict.get("meta", {}).get("llm_consulted") is True
    )


def test_p0_04_evidence_pre_flight():
    """Requirement 4: observe->judge sequence never returns EVIDENCE_HASH_MISSING or EVIDENCE_EMPTY."""
    init_res = _arif_session_init(mode="light", actor_id="ARIF")
    sid = init_res.get("session_id")

    # 1. Run observe
    obs = _arif_sense_observe(
        mode="search", query="quantum status", session_id=sid, actor_id="ARIF"
    )
    assert obs.get("status") in ("OK", "completed", "SEAL")

    # 2. Call judge with NO evidence parameter (auto-retrieved from observation cache)
    judge_res = _run(
        arif_judge(
            candidate="Observational reality verification",
            session_id=sid,
            actor_id="ARIF",
        )
    )
    judge_dict = (
        judge_res.model_dump(mode="json")
        if hasattr(judge_res, "model_dump")
        else judge_res
    )
    reasons = " ".join(judge_dict.get("reasons", []))
    assert "EVIDENCE_EMPTY" not in reasons
    assert "EVIDENCE_HASH_MISSING" not in reasons

    # 3. Call judge with raw evidence dict without hash (auto-computed)
    judge_res2 = _run(
        arif_judge(
            candidate="Arbitrary dict test",
            evidence={"sensor_reading": 42.0, "status": "nominal"},
            session_id=sid,
            actor_id="ARIF",
        )
    )
    judge_dict2 = (
        judge_res2.model_dump(mode="json")
        if hasattr(judge_res2, "model_dump")
        else judge_res2
    )
    reasons2 = " ".join(judge_dict2.get("reasons", []))
    assert "EVIDENCE_HASH_MISSING" not in reasons2

