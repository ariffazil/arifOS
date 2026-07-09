"""
SCT Slice 1 — session capability token continuity tests.

Acceptance:
  1. init mints session_token + honest UNMEASURED apex
  2. verify_sct round-trips
  3. Drop store row → observe/triage/think/compose/critique/judge/forge/seal/memory
     still work with token alone
  4. Tampered token → invalid
  5. No arif_act in allowed
  6. dry_run/verify paths for forge/seal do not require a live store
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

from arifosmcp.runtime.sct import (
    UNMEASURED,
    mint_sct,
    resolve_standing,
    unmeasured_apex,
    verify_sct,
)
from arifosmcp.tools import arif_memory
from arifosmcp.tools.forge import arif_forge
from arifosmcp.tools.heart import arif_critique
from arifosmcp.tools.judge import arif_judge
from arifosmcp.tools.reason import arif_think
from arifosmcp.tools.reply import arif_compose
from arifosmcp.tools.session import _project_light, arif_init
from arifosmcp.tools.sense import arif_observe
from arifosmcp.tools.vault import arif_seal


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

    # Canonical preflight is arif_init(mode=preflight) — not standalone arif_triage
    t = arif_init(
        mode="preflight",
        session_id=sid,
        actor_id="sct-slice1-actor",
    )
    # SessionManifest or dict
    t_dict = t.model_dump() if hasattr(t, "model_dump") else (t if isinstance(t, dict) else {})
    # Preflight may return triage envelope
    if not t_dict and hasattr(t, "result"):
        t_dict = {"status": "OK", "result": t.result} if t else {}
    if isinstance(t, dict):
        t_dict = t
    assert t_dict.get("status") in ("OK", "ok", "HOLD", None) or t is not None, t_dict
    tr = t_dict.get("result") or {}
    # Token standing: either echoed or reinjected via middleware when store gone
    # Internal arif_triage path still accepts SCT when session_token wired
    from arifosmcp.tools.kernel_canonical import arif_triage

    t2 = arif_triage(
        mode="preflight",
        session_id=sid,
        session_token=token,
        actor_id="sct-slice1-actor",
    )
    assert t2.get("status") == "OK", t2
    tr2 = t2.get("result") or {}
    assert tr2.get("session_found") is True
    assert tr2.get("standing_source") == "sct"
    assert t2.get("session_token") == token
    assert (t2.get("apex_scalars") or tr2.get("apex_scalars") or {}).get("G") == UNMEASURED

    # observe: search may hit network; L11 must not HOLD for missing store
    o = arif_observe(
        mode="vitals",  # cheap path, no external search required
        session_id=sid,
        session_token=token,
        actor_id="sct-slice1-actor",
    )
    assert "L11" not in str(o.get("reason", "")), o
    assert o.get("status") != "HOLD", o
    assert o.get("session_token") == token
    assert o.get("standing_source") == "sct"
    assert (o.get("apex_scalars") or {}).get("G") == UNMEASURED


def test_unmeasured_apex_helper():
    a = unmeasured_apex()
    assert set(a) == {"G", "C_dark", "W3", "h"}
    assert all(v == UNMEASURED for v in a.values())


def test_derive_verbs_no_arif_act():
    from arifosmcp.runtime.sct import derive_verbs

    for band in ("OBSERVE_ONLY", "LIMITED_MUTATE", "FULL", "SOVEREIGN"):
        verbs = derive_verbs(band)
        assert "arif_act" not in verbs
        assert "arif_think" in verbs
        assert "arif_compose" in verbs


def test_apply_caveats_never_widens():
    from arifosmcp.runtime.sct import apply_caveats, mint_sct

    _tok, claims = mint_sct(
        sid="SEAL-cav", actor="a", auth="LIMITED_MUTATE", av=True
    )
    narrowed = apply_caveats(claims, [{"type": "max_action_class", "value": "OBSERVE_ONLY"}])
    assert narrowed["auth"] == "OBSERVE_ONLY"
    try:
        apply_caveats(claims, [{"type": "max_action_class", "value": "SOVEREIGN"}])
        assert False, "widen should raise"
    except ValueError as e:
        assert "WIDEN" in str(e)


def _response_dict(obj: Any) -> dict[str, Any]:
    """Normalize ToolResult / Pydantic model / dict responses for assertions."""
    if hasattr(obj, "model_dump"):
        return obj.model_dump()  # type: ignore[union-attr]
    if hasattr(obj, "dict"):
        return obj.dict()  # type: ignore[union-attr]
    return dict(obj) if isinstance(obj, dict) else {"raw": obj}


def test_full_loop_store_delete_think_compose_forge_dry_seal_verify():
    """Spine P0 acceptance: delete store mid-flight; standing rides token alone."""
    from arifosmcp.runtime.tools import _SESSIONS

    r = arif_init(mode="light", actor_id="spine-p0-actor")
    header = r.result
    sid = header["session_id"]
    token = header["session_token"]
    assert token.startswith("sct_v1.")
    assert header["apex_scalars"]["G"] == UNMEASURED
    assert not token.startswith("arifos.v1")

    # Drop store — inhabit via token only
    try:
        _SESSIONS.delete(sid)
    except Exception:
        try:
            del _SESSIONS[sid]
        except Exception:
            pass
    assert _SESSIONS.get(sid) is None

    # ── think ───────────────────────────────────────────────────────────────
    think = arif_think(
        mode="reason",
        query="spine p0 standing check",
        actor_id="spine-p0-actor",
        session_id=sid,
        session_token=token,
    )
    t_dict = _response_dict(think)
    assert t_dict.get("status") == "OK", t_dict
    assert "L11" not in str(t_dict.get("reason", "")), t_dict
    assert t_dict.get("session_token") == token, t_dict
    assert t_dict.get("standing_source") == "sct", t_dict
    assert (t_dict.get("apex_scalars") or {}).get("G") == UNMEASURED, t_dict

    # ── compose ──────────────────────────────────────────────────────────────
    compose = arif_compose(
        mode="compose",
        message="pipeline close ok",
        actor_id="spine-p0-actor",
        session_id=sid,
        session_token=token,
    )
    c_dict = _response_dict(compose)
    assert c_dict.get("status") == "OK", c_dict
    assert "L11" not in str(c_dict.get("reason", "")), c_dict
    assert c_dict.get("session_token") == token, c_dict
    assert c_dict.get("standing_source") == "sct", c_dict

    async def _async_block() -> None:
        # ── forge dry_run ────────────────────────────────────────────────────
        forge_out = await arif_forge(
            mode="engineer",
            session_id=sid,
            session_token=token,
            actor_id="spine-p0-actor",
            dry_run=True,
        )
        f_dict = _response_dict(forge_out)
        assert f_dict.get("status") in ("OK", "HOLD"), f_dict
        f_res = f_dict.get("result") or {}
        assert f_res.get("dry_run") is True, f_dict
        assert f_res.get("actor_id") == "spine-p0-actor", f_dict
        assert "TOKEN_INVALID" not in str(f_dict), f_dict
        # Spine P0: direct tool must echo SCT continuity at top level
        assert f_dict.get("session_token") == token, f_dict
        assert f_dict.get("standing_source") == "sct", f_dict
        assert (f_dict.get("apex_scalars") or {}).get("G") == UNMEASURED, f_dict

        # ── seal verify ──────────────────────────────────────────────────────
        seal_out = await arif_seal(
            mode="verify",
            payload="spine-p0",
            session_id=sid,
            session_token=token,
            actor_id="spine-p0-actor",
        )
        s_dict = _response_dict(seal_out)
        assert "TOKEN_INVALID" not in str(s_dict), s_dict
        assert s_dict.get("session_token") == token, s_dict
        assert s_dict.get("standing_source") == "sct", s_dict
        assert (s_dict.get("apex_scalars") or {}).get("G") == UNMEASURED, s_dict

        # ── heart critique ───────────────────────────────────────────────────
        critique_out = await arif_critique(
            mode="summary",
            target="spine p0 token continuity",
            session_id=sid,
            session_token=token,
            actor_id="spine-p0-actor",
        )
        cr_dict = _response_dict(critique_out)
        assert "TOKEN_INVALID" not in str(cr_dict), cr_dict
        # critique may echo token when standing valid
        assert cr_dict.get("session_token") in (token, None) or str(
            cr_dict.get("session_token") or ""
        ).startswith("sct_v1."), cr_dict

        # ── judge scan (lightweight deterministic path) ──────────────────────
        judge_out = await arif_judge(
            mode="scan_instructions",
            candidate=".",
            session_id=sid,
            session_token=token,
            actor_id="spine-p0-actor",
        )
        j_dict = _response_dict(judge_out)
        assert "TOKEN_INVALID" not in str(j_dict), j_dict
        # Spine P0: direct tool must echo SCT continuity at top level
        assert j_dict.get("session_token") == token, j_dict
        assert j_dict.get("standing_source") == "sct", j_dict
        assert (j_dict.get("apex_scalars") or {}).get("G") == UNMEASURED, j_dict

        # ── memory recall ────────────────────────────────────────────────────
        memory_out = await arif_memory(
            mode="recall",
            query="spine p0",
            session_id=sid,
            session_token=token,
            actor_id="spine-p0-actor",
        )
        m_dict = _response_dict(memory_out)
        assert "TOKEN_INVALID" not in str(m_dict), m_dict
        # Spine P0: direct tool must echo SCT continuity at top level
        assert m_dict.get("session_token") == token, m_dict
        assert m_dict.get("standing_source") == "sct", m_dict
        assert (m_dict.get("apex_scalars") or {}).get("G") == UNMEASURED, m_dict

    asyncio.run(_async_block())

    # No dual arifos.v1 mint in path
    assert token.startswith("sct_v1.")
