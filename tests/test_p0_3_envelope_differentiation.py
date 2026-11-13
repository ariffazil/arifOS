"""P0-3 acceptance — envelope differentiation for verified callers (A2, repair-2026-11-01).

Root cause under test: judge.py's collapse auto-compute (contract: "Phase 1:
observe-only, never blocks", enforce=False) fills the four BIJAKSANA dials for
ANY caller that omits them; the bridge then treats those advisory auto-values as
caller-asserted measurements (actor_B auto ≈ 0.46 < 0.5 floor → BRIDGE_BLOCKED)
and returns a blanket HOLD before the main loop — so a benign observe from a
session-bound VERIFIED caller looked identical to a stranger's fail-closed HOLD
(the A2 "outsiders cannot tell design from bug" defect).

Differentiation contract proven to exist downstream when the bridge does not
block (measured 2026-10-31): verified + healthy dials → SABAR/PARTIAL_PROCEED;
unverified → OBSERVE_ONLY/NO_IDENTITY_BOUND.

Cases:
  (d) verified + benign observe, dials omitted → allow-class (NOT blanket HOLD)
  (e) verified + fake receipt + MUTATE/federation → HOLD, with the receipt
      verification failure DISCLOSED (differentiated hold, not silent HOLD)
  (f) control: unverified + benign observe → fail-closed (OBSERVE_ONLY/HOLD)
  (g) differentiation matrix: (d) and (e) verdicts must DIFFER
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("ARIFOS_PUBLIC_TOOL_PROFILE", "full")
os.environ.setdefault("ARIFOS_PHYSICS_DISABLED", "1")
sys.path.insert(0, str(Path(__file__).parent.parent))

from arifosmcp.runtime.server import create_aaa_mcp_server

BENIGN = "p03 benign observation: system uptime check"
MUTATE_CANDIDATE = "rotate VAULT999 signing key, push to prod"
FAKE_RECEIPT = "arif-approved-2026-11-01"
TEST_ACTOR = "p03-test-actor"
_HOLD_FAMILY = ("HOLD", "VOID")


def _envelope(call_result):
    if hasattr(call_result, "content") and call_result.content:
        for c in call_result.content:
            if hasattr(c, "text"):
                try:
                    return json.loads(c.text)
                except Exception:
                    return {"raw": c.text}
    return {}


async def _judge(client, **kwargs):
    res = await client.call_tool("arif_judge", kwargs)
    return _envelope(res)


def _test_pubkey_hex() -> str:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    priv = Ed25519PrivateKey.generate()
    return priv.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    ).hex()


async def _init_and_verify(client, actor: str = TEST_ACTOR) -> str:
    res = await client.call_tool(
        "arif_init", {"mode": "init", "actor_id": actor, "intent": "p03 acceptance session"}
    )
    env = _envelope(res)
    session_id = env.get("session_id") or (env.get("session") or {}).get("session_id")
    assert session_id, f"arif_init returned no session_id: {json.dumps(env)[:300]}"
    from arifosmcp.runtime.session import mark_session_ed25519_verified

    ok = mark_session_ed25519_verified(session_id, actor, _test_pubkey_hex())
    assert ok, f"mark_session_ed25519_verified failed for {session_id} — test premise broken"
    return session_id


@pytest.mark.asyncio
async def test_d_verified_benign_observe_allow_class():
    """(d) Verified caller, benign observe, no dials declared → NOT blanket HOLD."""
    server = create_aaa_mcp_server()
    async with __import__("fastmcp").Client(server) as client:
        sid = await _init_and_verify(client)
        res = await _judge(
            client,
            mode="observe",
            candidate=BENIGN,
            actor_id=TEST_ACTOR,
            session_id=sid,
        )
    verdict = str(res.get("verdict", "")).upper()
    assert res.get("actor_verified") is True, f"verified premise broken: {res.get('actor_verified')}"
    assert verdict not in _HOLD_FAMILY, (
        f"(d) verified benign observe must not be blanket HOLD (A2); got "
        f"verdict={verdict!r} reason_code={res.get('reason_code')!r} "
        f"reasons={json.dumps(res.get('reasons'))[:400]}"
    )


@pytest.mark.asyncio
async def test_e_verified_fake_receipt_mutate_holds_with_disclosure():
    """(e) Verified caller + fabricated receipt + MUTATE/federation → HOLD,
    and the envelope must DISCLOSE why the receipt did not count."""
    server = create_aaa_mcp_server()
    async with __import__("fastmcp").Client(server) as client:
        sid = await _init_and_verify(client)
        res = await _judge(
            client,
            mode="judge",
            candidate=MUTATE_CANDIDATE,
            actor_id=TEST_ACTOR,
            session_id=sid,
            sovereign_receipt=FAKE_RECEIPT,
            reversibility_level="R2_REVERSIBLE_WRITE",
            blast_radius="federation",
        )
    verdict = str(res.get("verdict", "")).upper()
    blob = json.dumps(res)
    assert verdict in _HOLD_FAMILY or verdict == "OBSERVE_ONLY", (
        f"(e) fake receipt + federation blast must HOLD; got {verdict!r}"
    )
    assert '"f13_promoted_allow_to_seal": true' not in blob
    rv = (res.get("meta") or {}).get("sovereign_receipt_verification") or {}
    assert rv.get("verified") is False and rv.get("reason") not in (None, ""), (
        f"(e) envelope must disclose the receipt verification result; got meta={json.dumps(rv)[:300]}"
    )


@pytest.mark.asyncio
async def test_f_unverified_still_fail_closed():
    """(f) Control — unverified benign observe stays fail-closed."""
    server = create_aaa_mcp_server()
    async with __import__("fastmcp").Client(server) as client:
        res = await _judge(
            client,
            mode="observe",
            candidate=BENIGN,
            actor_id=TEST_ACTOR,
        )
    verdict = str(res.get("verdict", "")).upper()
    assert res.get("actor_verified") in (False, None)
    assert verdict in ("OBSERVE_ONLY", "HOLD"), (
        f"(f) unverified must remain fail-closed; got {verdict!r}"
    )


@pytest.mark.asyncio
async def test_g_differentiation_matrix():
    """(g) The A2 essence: verified allow-case and verified hold-case must DIFFER."""
    server = create_aaa_mcp_server()
    async with __import__("fastmcp").Client(server) as client:
        sid = await _init_and_verify(client, actor="p03-matrix-actor")
        allow_case = await _judge(
            client,
            mode="observe",
            candidate=BENIGN,
            actor_id="p03-matrix-actor",
            session_id=sid,
        )
        hold_case = await _judge(
            client,
            mode="judge",
            candidate=MUTATE_CANDIDATE,
            actor_id="p03-matrix-actor",
            session_id=sid,
            sovereign_receipt=FAKE_RECEIPT,
            reversibility_level="R2_REVERSIBLE_WRITE",
            blast_radius="federation",
        )
    v_allow = str(allow_case.get("verdict", "")).upper()
    v_hold = str(hold_case.get("verdict", "")).upper()
    assert v_allow != v_hold, (
        f"(g) verified allow-case and hold-case must produce DIFFERENT verdicts "
        f"(A2: design must be distinguishable from bug); got allow={v_allow!r} hold={v_hold!r}"
    )
