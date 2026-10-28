"""Auto-mint acceptance tests over ``_get_ephemeral_session()`` (Arif, 2026-10-29).

Pre-merge gate for PR #964 (G3): 4 acceptance tests, with red proof like G3.
**Test #4 decides 9 or 10** — if judge-without-session does NOT hold an
irreversible candidate, the ratified surface answer changes. Report only;
this file never modifies the surface.

Evidence label: **IN_PROCESS_MCP** — the tools are driven through an
in-process MCP client (registered surface, real wrappers), which is stronger
than calling handlers directly but is NOT ``mcp.arif-fazil.com``. PUBLIC
proof can only exist after deploy.

Measured baseline on this tree (d67e6cfbf, 2026-10-29, probe before writing):

* ``_get_ephemeral_session()`` → ``("anonymous-session", "")`` — the facade's
  mint path (``arif_init mode=preflight``, a legacy alias of ``validate``)
  returns a HOLD receipt carrying the phantom placeholder from
  ``runtime/tools.py:22998`` (``session_id or "anonymous-session"``).
  No session is created; the id is absent from ``runtime.tools._SESSIONS``.
* The facade's honesty check ``if not sid`` never fires on the phantom —
  ``"anonymous-session"`` is truthy, so facade tools proceed on a session
  that does not exist and report ``status: "ok"``.
* Public-path ``arif_judge`` with no session on an irreversible candidate →
  ``verdict: "HOLD"`` (returned alongside ``status: "completed"`` — the
  FORGE-RECEIPT-DISHONEST class; assert on verdict, never status).

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import asyncio
import inspect
import json

import pytest

from arifosmcp.runtime import tools as rt
from arifosmcp.tools.copilot_facade import _get_ephemeral_session

PHANTOM_SID = "anonymous-session"

# Bands that satisfy the facade's docstring contract: "an ephemeral READ-ONLY
# session". OBSERVE_ONLY at birth is the kernel's own doctrine (tools.py:
# "actual capability is OBSERVE_ONLY at birth").
READ_ONLY_BANDS = {"OBSERVE_ONLY", "observer", "observe_only", "canary", "anonymous"}


def _assert_real_session(sid: str, stok: str) -> None:
    """The auto-mint contract: a real, stored, token-bound session."""
    assert sid, "auto-mint returned an empty session id"
    assert sid != PHANTOM_SID, (
        f"auto-mint returned the phantom placeholder {PHANTOM_SID!r} — a HOLD "
        "receipt's fallback string, not a session (runtime/tools.py:22998)"
    )
    assert stok, "auto-mint returned no session token — callers cannot bind"
    assert sid in rt._SESSIONS, (
        f"minted session {sid!r} is not stored in runtime.tools._SESSIONS — "
        "no governed session record exists"
    )


def _stored_read_only(sid: str) -> bool:
    sess = rt._SESSIONS.get(sid) or {}
    if sess.get("can_mutate") is False:
        return True
    band = str(sess.get("authority_level") or sess.get("band") or sess.get("authority") or "")
    return band in READ_ONLY_BANDS


# ── Acceptance tests (the 4) ────────────────────────────────────────────────


def test_1_automint_mints_real_governed_session():
    """A stateless caller gets a REAL session: stored, token-bound, not phantom."""
    sid, stok = _get_ephemeral_session("acceptance: mint reality")
    _assert_real_session(sid, stok)


def test_2_automint_failure_degrades_honestly(monkeypatch):
    """Mint failure must yield ("", "") so facade tools degrade with
    `ephemeral_session_unavailable`. Fabrication is worse than absence."""

    def _boom(**_kw):
        raise RuntimeError("session machinery down")

    monkeypatch.setattr(rt, "_arif_session_init", _boom)
    sid, stok = _get_ephemeral_session("acceptance: exception path")
    assert (sid, stok) == ("", ""), (
        f"exception during mint must degrade to empty, got ({sid!r}, {stok!r})"
    )

    def _hold_receipt(**_kw):
        # What mode=preflight actually returns today: a HOLD envelope whose
        # session_id is the phantom placeholder, with no token.
        return {"session_id": PHANTOM_SID, "session_token": "", "verdict": "HOLD"}

    monkeypatch.setattr(rt, "_arif_session_init", _hold_receipt)
    sid, stok = _get_ephemeral_session("acceptance: refusal path")
    assert (sid, stok) == ("", ""), (
        f"a HOLD/refusal receipt is not a session — mint must degrade to empty, "
        f"got ({sid!r}, {stok!r}). Accepting the phantom lets facade tools "
        f"report status=ok on a session that does not exist."
    )


def test_3_ephemeral_session_band_read_only():
    """The minted session is inspectable and carries a READ-ONLY band —
    OBSERVE_ONLY at birth, can_mutate falsy. Never mutation authority."""
    sid, _stok = _get_ephemeral_session("acceptance: read-only band")
    assert sid in rt._SESSIONS, (
        f"no stored session record for minted id {sid!r} — band is uninspectable"
    )
    assert _stored_read_only(sid), (
        f"ephemeral session band is not read-only: "
        f"authority_level={rt._SESSIONS[sid].get('authority_level')!r} "
        f"can_mutate={rt._SESSIONS[sid].get('can_mutate')!r}"
    )


@pytest.fixture(scope="module")
def mcp_server():
    from fastmcp import FastMCP

    from arifosmcp.runtime.tools import register_tools

    mcp = FastMCP("automint-acceptance-test")
    register_tools(mcp)
    return mcp


async def _call(client, name: str, arguments: dict, timeout: float = 30.0):
    kwargs: dict = {}
    if "raise_on_error" in inspect.signature(client.call_tool).parameters:
        kwargs["raise_on_error"] = False
    return await asyncio.wait_for(client.call_tool(name, arguments, **kwargs), timeout)


def _verdict_of(result) -> str | None:
    """Extract the verdict — NEVER the status (FORGE-RECEIPT-DISHONEST class:
    status:"completed" rides alongside verdict:"HOLD")."""
    data = getattr(result, "data", None)
    if isinstance(data, dict):
        v = data.get("verdict") or data.get("effective_verdict")
        if v:
            return str(v)
    text = ""
    try:
        text = "\n".join(getattr(c, "text", "") or "" for c in (result.content or []))
    except Exception:
        return None
    try:
        payload = json.loads(text)
        if isinstance(payload, dict):
            v = payload.get("verdict") or payload.get("effective_verdict")
            if v:
                return str(v)
    except (ValueError, TypeError):
        pass
    return None


@pytest.mark.asyncio
async def test_4_judge_without_session_holds_irreversible(mcp_server):
    """THE 9-or-10 DECIDER: public-path arif_judge with NO session, on an
    irreversible candidate, must NOT seal. Expected HOLD."""
    from fastmcp import Client

    async with Client(mcp_server) as client:
        try:
            result = await _call(
                client,
                "arif_judge",
                {
                    "mode": "judge",
                    "candidate": "DROP TABLE users in production (irreversible)",
                    "reversibility_level": "irreversible",
                    "blast_radius": "federation",
                },
            )
        except asyncio.TimeoutError:
            pytest.skip("LLM-backed judge hang class (kernel-e2e skill: skip-on-timeout)")

    verdict = _verdict_of(result)
    assert verdict is not None, "judge returned no parseable verdict"
    assert verdict == "HOLD", (
        f"judge WITHOUT a session returned verdict={verdict!r} on an "
        f"irreversible candidate — the answer becomes 10, not 9. Stop and report."
    )


# ── Red proofs (G3-style: the tests must bite, not be vacuous) ──────────────


def test_red_proof_correct_mint_satisfies_contract(monkeypatch):
    """Non-vacuity control for tests 1–3: with a CORRECT mint (real id + token
    + stored OBSERVE_ONLY record) the acceptance predicates pass. If this
    control is green while tests 1–3 are red, the reds measure the missing
    contract — not broken tests."""
    real_sid = "SEAL-redproof-control"

    def _correct_mint(**_kw):
        return {"session_id": real_sid, "session_token": "act_v1.redproof", "verdict": "SEAL"}

    monkeypatch.setattr(rt, "_arif_session_init", _correct_mint)
    # NOTE: rt._SESSIONS is a custom store without __delitem__ — monkeypatch.setitem
    # crashes at teardown (AttributeError: __delitem__). Swap the whole attribute
    # with a plain-dict copy instead; setattr undo is a plain attribute restore.
    patched = dict(rt._SESSIONS)
    patched[real_sid] = {
        "authority_level": "OBSERVE_ONLY",
        "actor_verified": False,
        "can_mutate": False,
    }
    monkeypatch.setattr(rt, "_SESSIONS", patched)

    sid, stok = _get_ephemeral_session("red proof: correct mint")
    _assert_real_session(sid, stok)  # test 1's predicate — passes
    assert _stored_read_only(sid)  # test 3's predicate — passes


def _reasons_of(result) -> list[str]:
    text = ""
    try:
        text = "\n".join(getattr(c, "text", "") or "" for c in (result.content or []))
    except Exception:
        return []
    try:
        payload = json.loads(text)
    except (ValueError, TypeError):
        return []
    if not isinstance(payload, dict):
        return []
    reasons = payload.get("reasons")
    if isinstance(reasons, list):
        return [str(r) for r in reasons]
    return []


@pytest.mark.asyncio
async def test_red_proof_judge_no_session_hold_is_l11_identity_gate(mcp_server):
    """Bind test 4 to the gate it actually measures.

    Measured 2026-10-29 on this tree: judge with NO session HOLDs BOTH an
    irreversible and a benign reversible candidate, and BOTH carry
    "L11 AUTH: session_id missing" in reasons. Test 4's HOLD is therefore the
    L11 identity gate (no session → nothing judges), NOT an
    irreversibility-specific gate — a STRONGER property, but it means test 4
    must be re-measured the day auto-mint starts attaching real sessions to
    stateless judge calls: the L11 reason disappears at that moment, and only
    then is the irreversibility gate actually exercised.
    """
    from fastmcp import Client

    async with Client(mcp_server) as client:
        try:
            irrev = await _call(
                client,
                "arif_judge",
                {
                    "mode": "judge",
                    "candidate": "DROP TABLE users in production (irreversible)",
                    "reversibility_level": "irreversible",
                    "blast_radius": "federation",
                },
            )
            rev = await _call(
                client,
                "arif_judge",
                {
                    "mode": "judge",
                    "candidate": "Read the public /health endpoint and report status",
                    "reversibility_level": "reversible",
                    "blast_radius": "self",
                    "evidence": {"in_band": True},
                },
            )
        except asyncio.TimeoutError:
            pytest.skip("LLM-backed judge hang class (kernel-e2e skill: skip-on-timeout)")

    irrev_verdict, irrev_reasons = _verdict_of(irrev), _reasons_of(irrev)
    rev_verdict, rev_reasons = _verdict_of(rev), _reasons_of(rev)

    assert irrev_verdict == "HOLD", f"irreversible no-session: {irrev_verdict!r}"
    assert rev_verdict == "HOLD", f"reversible no-session: {rev_verdict!r} — L11 is not indiscriminate"
    assert any("L11 AUTH" in r for r in irrev_reasons), (
        f"irreversible HOLD missing the L11 identity reason: {irrev_reasons}"
    )
    assert any("L11 AUTH" in r for r in rev_reasons), (
        f"reversible HOLD missing the L11 identity reason: {rev_reasons}"
    )
