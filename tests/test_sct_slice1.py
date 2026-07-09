"""
SCT Slice 1 — session capability token continuity tests.

Acceptance:
  1. init mints session_token + honest UNMEASURED apex
  2. verify_sct round-trips
  3. Drop store row → observe/triage still work with token alone
  4. Tampered token → invalid
  5. No arif_act in allowed
"""

from __future__ import annotations

import time

from arifosmcp.runtime.sct import (
    UNMEASURED,
    mint_sct,
    resolve_standing,
    unmeasured_apex,
    verify_sct,
)
from arifosmcp.tools.kernel_canonical import arif_triage
from arifosmcp.tools.session import _project_light, arif_init
from arifosmcp.tools.sense import arif_observe


def _components() -> dict:
    return {
        "alignment_profile": {"loaded": True},
        "adversarial_profile": {"loaded": True},
        "belief": {"intent_model": {"status": "ok"}},
        "next": {"recommended_next": "arif_observe"},
    }


def test_mint_verify_roundtrip():
    token, claims = mint_sct(
        sid="SEAL-sct-test",
        actor="arif",
        auth="LIMITED_MUTATE",
        av=True,
        allowed=["arif_observe", "arif_act", "arif_forge"],
    )
    assert token.startswith("sct_v1.")
    assert claims["apex"]["G"] == UNMEASURED
    assert "arif_act" not in claims["allowed"]
    assert "arif_forge" in claims["allowed"]
    out = verify_sct(token, expected_actor="arif")
    assert out is not None
    assert out["sid"] == "SEAL-sct-test"
    assert out["auth"] == "LIMITED_MUTATE"


def test_tampered_token_rejected():
    token, _ = mint_sct(sid="SEAL-x", actor="a", auth="OBSERVE_ONLY", av=False)
    bad = token[:-4] + "dead"
    assert verify_sct(bad) is None


def test_expired_token_rejected():
    token, claims = mint_sct(
        sid="SEAL-exp", actor="a", auth="OBSERVE_ONLY", av=False, ttl=1
    )
    # Force expire
    claims["exp"] = int(time.time()) - 10
    # remint not possible from claims without re-sign — use verify with now far future
    # Instead mutate: craft expired via mint then travel in time via verify now=
    assert verify_sct(token, now=time.time() + 10_000) is None


def test_project_light_emits_token_and_unmeasured_apex():
    header = _project_light(
        _components(),
        sid="SEAL-pl",
        actor_id="arif",
        constitution_hash="sha256:x",
        actor_verified=True,
        authority_override="LIMITED_MUTATE",
    )
    assert header.get("session_token", "").startswith("sct_v1.")
    apex = header.get("apex_scalars") or {}
    assert apex.get("G") == UNMEASURED
    assert apex.get("C_dark") == UNMEASURED
    assert "arif_act" not in header.get("allowed_next_verbs", [])
    assert header["session_birth"]["authority_mode"] == header["authority"]
    claims = verify_sct(header["session_token"], expected_actor="arif")
    assert claims is not None
    assert claims["auth"] == "LIMITED_MUTATE"


def test_resolve_standing_survives_store_delete():
    token, claims = mint_sct(
        sid="SEAL-ghost",
        actor="ghost-actor",
        auth="LIMITED_MUTATE",
        av=True,
    )
    # Ensure store has no row
    try:
        from arifosmcp.runtime.tools import _SESSIONS

        if "SEAL-ghost" in _SESSIONS:
            _SESSIONS.delete("SEAL-ghost")
    except Exception:
        pass

    standing = resolve_standing(
        session_token=token,
        session_id="SEAL-ghost",
        actor_id="ghost-actor",
        allow_store=True,
    )
    assert standing.valid is True
    assert standing.source == "sct"
    assert standing.authority == "LIMITED_MUTATE"
    assert standing.session_token


def test_init_triage_observe_with_token_after_store_delete():
    r = arif_init(mode="light", actor_id="sct-slice1-actor")
    header = r.result
    sid = header["session_id"]
    token = header.get("session_token")
    assert token and token.startswith("sct_v1."), f"missing token: {header.keys()}"
    assert header.get("apex_scalars", {}).get("G") == UNMEASURED

    # Delete store row — token alone must carry standing
    from arifosmcp.runtime.tools import _SESSIONS

    try:
        _SESSIONS.delete(sid)
    except Exception:
        try:
            del _SESSIONS[sid]
        except Exception:
            pass
    assert _SESSIONS.get(sid) is None

    t = arif_triage(
        mode="preflight",
        session_id=sid,
        session_token=token,
        actor_id="sct-slice1-actor",
    )
    assert t.get("status") == "OK", t
    tr = t.get("result") or {}
    assert tr.get("session_found") is True
    assert tr.get("standing_source") == "sct"
    assert t.get("session_token") or tr.get("session_token")

    # observe: search may hit network; L11 must not HOLD for missing store
    o = arif_observe(
        mode="vitals",  # cheap path, no external search required
        session_id=sid,
        session_token=token,
        actor_id="sct-slice1-actor",
    )
    assert o.get("status") != "HOLD" or "L11" not in str(o.get("reason", "")), o
    # Prefer OK; vitals may return ok wrapper
    assert o.get("status") in ("OK", "ok", "SEAL", None) or o.get("verdict") not in (
        "RETAK",
        "VOID",
    ), o
    assert o.get("session_token") or (o.get("result") or {}).get("session_token")


def test_unmeasured_apex_helper():
    a = unmeasured_apex()
    assert set(a) == {"G", "C_dark", "W3", "h"}
    assert all(v == UNMEASURED for v in a.values())
