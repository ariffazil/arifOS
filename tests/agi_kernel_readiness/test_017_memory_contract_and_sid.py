"""M365 P1/P2 regressions — memory response contract + session-resume honesty.

P1 (k-def-arif-memory-empty-payload):
  Invariant A — every memory-handler path returns a schema-valid success OR a
  schema-valid explicit failure payload.
  Invariant B — an empty payload never masquerades as success.

P2 (k-def-session-resume-stale-sid):
  Invariant C — resume never fabricates continuity.
  Invariant D — absent/stale session → explicit NOT_FOUND, or a new SID minted
  only through the documented init path.
  Invariant E — every SID returned to a caller is recognized by the canonical
  session validator in the same runtime scope.

Evidence base:
  /root/forge_work/receipts/RECEIPT-copilot-memory-ingest-2026-10-29.md (B1)
  journal 2026-10-29: hollow_success_gate missing_result_and_content,
  KERNEL PANIC 'No response returned' (server.py GlobalPanicMiddleware),
  init echoing stale client sid while minting a fresh unregistered handle.

Thermodynamic HOLD is expected on mutation paths — these tests assert the
REFUSAL SHAPE (explicit, schema-valid), never that mutation is allowed.
"""

import asyncio
import warnings

import pytest

from arifosmcp.runtime import tools as T
from arifosmcp.runtime import session as S
from arifosmcp.runtime.tools import _arif_session_init, _arif_memory_v5_router
from arifosmcp.runtime.session_auth import validate_session

ACTOR = "m365-regress"


def _run(coro):
    return asyncio.run(coro)


def _payload_of(resp):
    """Structured payload a caller can read, across dict / RuntimeEnvelope shapes."""
    if resp is None:
        return None
    if isinstance(resp, dict):
        for k in ("result", "payload", "content"):
            v = resp.get(k)
            if v:
                return v
        return None
    payload = getattr(resp, "payload", None)
    return payload or None


def _substance(resp) -> bool:
    p = _payload_of(resp)
    if isinstance(p, dict):
        return bool(p)
    if isinstance(p, str):
        return bool(p.strip())
    return p is not None


def _text(resp) -> str:
    import json

    try:
        if hasattr(resp, "model_dump"):
            resp = resp.model_dump()
        return json.dumps(resp, default=str)
    except Exception:
        return str(resp)


def _new_session():
    init_res = _arif_session_init(mode="light", actor_id=ACTOR)
    sid = init_res.get("session_id")
    token = init_res.get("session_token")
    assert sid, f"light init produced no session_id: {init_res}"
    return sid, token


# ── P1: memory response contract ─────────────────────────────────────────────


def test_p1_01_recall_success_returns_structured_payload():
    sid, token = _new_session()
    resp = _run(
        _arif_memory_v5_router(
            mode="recall",
            query="m365 contract probe",
            session_id=sid,
            actor_id=ACTOR,
            session_token=token,
        )
    )
    assert resp is not None
    assert _substance(resp), f"recall returned empty payload: {_text(resp)[:400]}"


def test_p1_02_remember_refusal_is_explicit_failure_not_empty():
    """No-lease / governed refusal must carry an explicit structured failure.

    Before the fix this path reaches the wire as an empty result that the
    hollow_success_gate rewrites to UNMEASURED (RECEIPT B1, AMEND 15:20).
    """
    sid, token = _new_session()
    resp = _run(
        _arif_memory_v5_router(
            mode="remember",
            content="M365 contract test — governed refusal shape",
            truth_class={"status": "OBS", "confidence": 0.9},
            session_id=sid,
            actor_id=ACTOR,
            session_token=token,
        )
    )
    assert resp is not None, (
        "remember returned None — transport would panic 'No response returned'"
    )
    text = _text(resp)
    assert _substance(resp), (
        "remember refusal arrived as an empty payload (invariant A violated): "
        f"{text[:500]}"
    )


def test_p1_03_exception_path_yields_explicit_failure(monkeypatch):
    """A raising dispatcher must surface as an explicit structured failure."""
    sid, token = _new_session()
    import arifosmcp.runtime.megaTools.tool_13_arif_memory as d13

    async def _boom(**kwargs):
        raise RuntimeError("downstream dispatcher exploded (m365 test)")

    monkeypatch.setattr(d13, "arif_memory", _boom)
    resp = _run(
        _arif_memory_v5_router(
            mode="remember",
            content="x",
            session_id=sid,
            actor_id=ACTOR,
            session_token=token,
        )
    )
    assert resp is not None, "exception path returned None — empty payload on the wire"
    assert _substance(resp), (
        f"exception path returned empty payload: {_text(resp)[:400]}"
    )


def test_p1_04_malformed_downstream_none_is_repaired(monkeypatch):
    """A None-returning backend must never reach the wire as an empty payload."""
    sid, token = _new_session()
    import arifosmcp.runtime.megaTools.tool_13_arif_memory as d13

    async def _void(**kwargs):
        return None

    monkeypatch.setattr(d13, "arif_memory", _void)
    resp = _run(
        _arif_memory_v5_router(
            mode="remember",
            content="x",
            session_id=sid,
            actor_id=ACTOR,
            session_token=token,
        )
    )
    assert resp is not None, "None downstream propagated to caller (KERNEL PANIC fuel)"
    assert _substance(resp), (
        f"malformed downstream produced empty payload: {_text(resp)[:400]}"
    )


def test_p1_05_empty_payload_never_masquerades_as_success():
    """Whatever shape comes back: success-tense status requires substance."""
    sid, token = _new_session()
    for mode in ("remember", "recall", "inspect", "audit"):
        resp = _run(
            _arif_memory_v5_router(
                mode=mode,
                query="m365",
                content="m365",
                memory_id="mem-none",
                session_id=sid,
                actor_id=ACTOR,
                session_token=token,
            )
        )
        assert resp is not None, f"mode={mode} returned None"
        status = ""
        if isinstance(resp, dict):
            status = str(resp.get("status", "")).lower()
        else:
            status = str(getattr(resp, "status", "")).lower()
        if status in ("ok", "completed", "success", "seal"):
            assert _substance(resp), f"mode={mode}: success status with empty payload"


def test_p1_06_doctrine_field_is_schema_valid():
    """schemas/session.py declares doctrine as dict; the writer assigns str.

    PydanticSerializationUnexpectedValue on every manifest dump pollutes the
    kernel journal and makes the init payload schema-invalid.
    """
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        _arif_session_init(mode="light", actor_id=ACTOR)
    bad = [
        w
        for w in caught
        if "PydanticSerializationUnexpectedValue" in str(w.message)
        and "doctrine" in str(w.message)
    ]
    assert not bad, f"doctrine serialization warning present: {bad[0].message}"


# ── P2: honest session continuity ────────────────────────────────────────────


def test_p2_01_valid_resume_finds_live_session():
    sid, token = _new_session()
    res = _arif_session_init(mode="resume", session_id=sid, actor_id=ACTOR)
    text = _text(res)
    assert "not found" not in text.lower(), f"live session failed resume: {text[:300]}"


def test_p2_02_missing_session_is_explicit_not_found():
    ghost = "SEAL-" + "0" * 16
    res = _arif_session_init(mode="resume", session_id=ghost, actor_id=ACTOR)
    status = str(res.get("status", "")).lower() if isinstance(res, dict) else ""
    verdict = str(res.get("verdict", "")).lower() if isinstance(res, dict) else ""
    assert status in ("hold", "void") or verdict in ("hold", "void"), (
        f"resume of unknown session must be an explicit refusal: {_text(res)[:300]}"
    )
    assert "not found" in _text(res).lower(), (
        f"refusal does not name NOT_FOUND honestly: {_text(res)[:300]}"
    )


def test_p2_03_stale_sid_after_restart_is_honest():
    """Simulate restart: drop the session from BOTH live surfaces.

    init(mode=init) carrying the stale sid/token must not hand back a sid
    that no validator in this process can resolve (invariant E).
    """
    sid, token = _new_session()
    T._SESSIONS.pop(sid, None)
    S._SESSION_IDENTITY.pop(sid, None)

    res = _arif_session_init(
        mode="init", actor_id=ACTOR, session_id=sid, session_token=token
    )
    assert isinstance(res, dict), _text(res)[:200]
    returned = res.get("session_id")
    assert returned, f"init returned no session_id: {_text(res)[:300]}"
    live = (returned in T._SESSIONS) or (returned in S._SESSION_IDENTITY)
    assert live, (
        f"init echoed session_id {returned!r} that this runtime cannot resolve "
        "(stale-SID ghost; invariant C/E violated)"
    )


def test_p2_04_every_returned_sid_is_validator_recognized():
    sid, token = _new_session()
    res = _arif_session_init(
        mode="init", actor_id=ACTOR, session_id=sid, session_token=token
    )
    if not isinstance(res, dict):
        pytest.skip("non-dict init envelope")
    sids = set()
    if res.get("session_id"):
        sids.add(res["session_id"])
    if res.get("handle"):
        sids.add(res["handle"])
    birth = res.get("session_birth")
    if isinstance(birth, dict) and birth.get("session_id"):
        sids.add(birth["session_id"])
    assert sids, f"no session identifiers in init response: {_text(res)[:300]}"
    for s in sids:
        v = validate_session(s, ACTOR)
        assert v.get("valid"), f"init returned sid {s!r} that the validator rejects"


def test_p2_05_remember_after_simulated_restart_is_explicit():
    """P1×P2 integration: stale-sid session state must produce an EXPLICIT
    structured refusal (not an empty payload) on the memory mutation path."""
    sid, token = _new_session()
    T._SESSIONS.pop(sid, None)
    S._SESSION_IDENTITY.pop(sid, None)
    resp = _run(
        _arif_memory_v5_router(
            mode="remember",
            content="m365 restart-shape",
            truth_class={"status": "OBS", "confidence": 0.9},
            session_id=sid,
            actor_id=ACTOR,
            session_token=token,
        )
    )
    assert resp is not None, "remember after sid-loss returned None"
    assert _substance(resp), (
        f"stale-session remember produced empty payload: {_text(resp)[:500]}"
    )


def test_p1_07_wire_wrapper_flattens_envelope():
    """k-def-arif-memory-empty-payload (WIRE): a RuntimeEnvelope returned by a
    handler must reach the canonical normalizer as a dict with its payload
    readable as `result` — not as an opaque object stuffed under "result".
    This is the path on which remember refusals arrived empty on the wire."""
    from arifosmcp.runtime.model import RuntimeEnvelope

    env = RuntimeEnvelope(
        tool="arif_memory",
        canonical_tool_name="arif_memory",
        session_id="SEAL-wiretest0000000",
        payload={"mode": "remember", "note": "lease required"},
    )

    async def _handler(**kwargs):
        return env

    wrapped = T._wrap_with_canonical_normalization(_handler, "arif_memory")
    out = _run(wrapped())
    assert isinstance(out, dict), "wire wrapper returned non-dict"
    res = out.get("result")
    assert isinstance(res, dict) and res, (
        f"wire result lost the envelope payload: {_text(out)[:400]}"
    )
    assert res.get("note") == "lease required"


def test_p2_06_stale_client_ref_becomes_resolvable_alias():
    """k-def-session-resume-stale-sid: after a simulated restart, init carrying
    the stale sid must register it as an alias onto the freshly minted session,
    so the echoed sid IS resolvable by the canonical validator (invariant E).
    Live sids are never hijacked — sid here is ghosted first."""
    sid, token = _new_session()
    T._SESSIONS.pop(sid, None)
    S._SESSION_IDENTITY.pop(sid, None)

    res = _arif_session_init(
        mode="init", actor_id=ACTOR, session_id=sid, session_token=token
    )
    assert isinstance(res, dict), _text(res)[:200]
    assert sid in T._SESSIONS, f"stale client_ref {sid} was not aliased into _SESSIONS"
    v = validate_session(sid, ACTOR)
    assert v.get("valid"), f"canonical validator still rejects aliased sid {sid}"


def test_p1_08_gate_deny_carries_explicit_failure(monkeypatch):
    """WIRE P1: when the pre-execution constitutional gate denies (effective
    thermodynamic HOLD), the router must hand back an EXPLICIT structured
    failure — never a thin envelope the hollow_success_gate rewrites to a
    generic UNMEASURED note. Verdict must stay HOLD (invariant G)."""
    sid, token = _new_session()
    thin = {
        "status": "HOLD",
        "verdict": "HOLD",
        "reasons": [],
        "meta": {"reason": "EFFECTIVE_HOLD_NEEDS_REVIEW"},
    }
    monkeypatch.setattr(T, "_constitutional_gate", lambda *a, **k: dict(thin))
    resp = _run(
        _arif_memory_v5_router(
            mode="remember", content="m365 gate-deny", session_id=sid,
            actor_id=ACTOR, session_token=token,
        )
    )
    assert isinstance(resp, dict), _text(resp)[:200]
    assert resp.get("verdict") == "HOLD", "gate deny must not soften the verdict"
    res = resp.get("result")
    assert isinstance(res, dict) and res, (
        f"gate deny returned empty result (invariant A violated): {_text(resp)[:300]}"
    )
    assert res.get("blocked") is True and res.get("mode") == "remember"
    assert "EFFECTIVE_HOLD" in _text(res)


def test_p2_07_alias_never_mints_sovereign_or_seal_without_crypto():
    """888-C2 negative regression (mirror semantics).

    The alias performs NO independent identity binding: _SESSIONS is the
    single write path, so the ghost record must be label-IDENTICAL to the
    freshly minted live session — never stronger, never sovereign, and
    verified=False for a token-less claim. If the kernel stamps its own
    session-birth governance SEAL on the live record (verified=False is the
    truth axis there), the ghost mirrors it equally; that parity — not an
    alias mint — is the property under test.
    """
    import uuid as _uuid

    ghost = "SEAL-" + _uuid.uuid4().hex[:16]
    res = _arif_session_init(mode="init", actor_id="arif", session_id=ghost)
    assert isinstance(res, dict), _text(res)[:200]
    live = res.get("session_id")
    assert live and live != ghost, f"init did not mint a fresh session: {live!r}"
    assert ghost in T._SESSIONS, "stale client_ref was not aliased (invariant E)"

    g = S._SESSION_IDENTITY.get(ghost) or {}
    l = S._SESSION_IDENTITY.get(live) or {}

    def sig(r):
        return (
            str(r.get("authority_level", "")).lower(),
            bool(r.get("verified", False)),
            (r.get("governance") or {}).get("verdict"),
        )

    assert sig(g) == sig(l), f"alias diverged from live labels: ghost={sig(g)} live={sig(l)}"
    assert g.get("authority_level", "").lower() not in ("sovereign", "full"), (
        f"alias record carries {g.get('authority_level')!r} from a bare claim — F13 violation"
    )
    assert g.get("verified") is False, (
        "ghost verified=True without cryptographic standing"
    )
    assert l.get("verified") is False, (
        "premise drift: live itself verified without crypto — surface separately"
    )
