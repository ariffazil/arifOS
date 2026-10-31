"""P0-1 acceptance — sovereign_receipt promotion gate (repair-2026-11-01).

Root cause under test: judge.py counted ANY non-empty sovereign_receipt
string as an F13 receipt and promoted ALLOW→SEAL on the intercept path,
letting an unverified/verified caller reach SEAL for a federation-blast
key rotation with zero evidence.

Acceptance (repair brief P0-1):
  (a) verified actor + fake receipt + MUTATE/IRREVERSIBLE + blast=federation
      → must HOLD (not SEAL; f13_promoted_allow_to_seal falsy)
  (b) verified actor + NO receipt + IRREVERSIBLE → must HOLD/escalate
  (c) unverified actor + any receipt → OBSERVE_ONLY/HOLD, never SEAL
  (d) verifier unit matrix: fake string, real ledger row, wrong candidate,
      wrong actor, HOLD-decision row, unsigned row, tampered row

Test-only key material: a fresh Ed25519 keypair generated in-process for
mark_session_ed25519_verified. NEVER a production key; NEVER key-path reads.
"""

from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

import pytest

os.environ.setdefault("ARIFOS_PUBLIC_TOOL_PROFILE", "full")
os.environ.setdefault("ARIFOS_PHYSICS_DISABLED", "1")
sys.path.insert(0, str(Path(__file__).parent.parent))

from arifosmcp.runtime.server import create_aaa_mcp_server

MUTATE_CANDIDATE = "rotate VAULT999 signing key, push to prod"
FAKE_RECEIPT = "arif-approved-2026-11-01"
TEST_ACTOR = "p01-test-actor"
_HOLD_FAMILY = ("HOLD", "VOID", "SABAR", "OBSERVE_ONLY", "UNKNOWN")


def _envelope(call_result):
    if hasattr(call_result, "content") and call_result.content:
        for c in call_result.content:
            if hasattr(c, "text"):
                try:
                    return json.loads(c.text)
                except Exception:
                    return {"raw": c.text}
    return {}


def _verdict(res: dict) -> str:
    return str(res.get("verdict", "")).upper()


async def _judge(client, **kwargs):
    res = await client.call_tool("arif_judge", kwargs)
    return _envelope(res)


def _test_pubkey_hex() -> str:
    """Fresh test-only Ed25519 key (in-process; no key files touched)."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    priv = Ed25519PrivateKey.generate()
    return priv.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    ).hex()


async def _init_and_verify(client, actor: str = TEST_ACTOR) -> str:
    """arif_init → session, then mark Ed25519-verified with the TEST key."""
    res = await client.call_tool(
        "arif_init",
        {"mode": "init", "actor_id": actor, "intent": "p01 acceptance test session"},
    )
    env = _envelope(res)
    session_id = env.get("session_id") or (env.get("session") or {}).get("session_id")
    assert session_id, f"arif_init returned no session_id: {json.dumps(env)[:300]}"
    from arifosmcp.runtime.session import mark_session_ed25519_verified

    ok = mark_session_ed25519_verified(session_id, actor, _test_pubkey_hex())
    assert ok, f"mark_session_ed25519_verified failed for {session_id} — test premise broken"
    return session_id


# ── (d) verifier unit matrix ────────────────────────────────────────────────


def _mint_test_row(
    vault_path: Path,
    candidate: str,
    actor: str = TEST_ACTOR,
    decision: str = "SEAL",
    signature: str = "cd" * 64,
    session_id: str = "SEAL-p01-test",
) -> str:
    """Fabricate a self-consistent ledger row (test keyring equivalent)."""
    from arifosmcp.core.vault_receipt import VaultReceipt, compute_receipt_hash
    from arifosmcp.runtime.sovereign_receipt_verify import candidate_intent_hash

    receipt = VaultReceipt(
        receipt_id=str(uuid.uuid4()),
        ts=datetime.now(UTC).isoformat(),
        monotonic_counter=1,
        parent_hash="",
        session_id=session_id,
        session_merkle_root="",
        actor_id=actor,
        organ_id="arifOS",
        actor_pubkey_epoch=1,
        actor_signature=signature,
        intent_summary="p01 test receipt",
        intent_hash=candidate_intent_hash(candidate),
        requested_authority="sovereign",
        pre_state_hash="",
        decision=decision,
        verdict_hash="0" * 64,
        floors_evaluated=["F13"],
        floors_violated=[],
        conflict_resolved=False,
        conflict_resolution="none",
        decision_class="C4_SOVEREIGN",
        latency_ms=1.0,
        within_budget=True,
        witness_count=1,
        witness_dissent=[],
        receipt_hash="",
    )
    receipt.receipt_hash = compute_receipt_hash(receipt)
    with open(vault_path, "a") as fh:
        fh.write(json.dumps(receipt.to_dict(), sort_keys=True) + "\n")
    return receipt.receipt_id


def _verify(receipt, candidate, actor=TEST_ACTOR, vault_path=None):
    from arifosmcp.runtime.sovereign_receipt_verify import verify_sovereign_receipt

    return verify_sovereign_receipt(receipt, candidate, actor_id=actor, vault_path=vault_path)


def test_v_fake_string_not_found(tmp_path):
    rep = _verify(FAKE_RECEIPT, MUTATE_CANDIDATE, vault_path=tmp_path / "r.jsonl")
    assert rep["verified"] is False
    assert rep["reason"] in ("NOT_FOUND", "LEDGER_UNAVAILABLE")


def test_v_real_seal_row_verifies(tmp_path):
    vault = tmp_path / "r.jsonl"
    rid = _mint_test_row(vault, MUTATE_CANDIDATE)
    rep = _verify(rid, MUTATE_CANDIDATE, vault_path=vault)
    assert rep["verified"] is True, rep
    assert rep["reason"] == "VERIFIED"
    assert rep["signature_checked"] is False  # disclosed honest limit


def test_v_wrong_candidate_mismatch(tmp_path):
    vault = tmp_path / "r.jsonl"
    rid = _mint_test_row(vault, MUTATE_CANDIDATE)
    rep = _verify(rid, "some totally different action", vault_path=vault)
    assert rep["verified"] is False and rep["reason"] == "CANDIDATE_MISMATCH"


def test_v_wrong_actor_mismatch(tmp_path):
    vault = tmp_path / "r.jsonl"
    rid = _mint_test_row(vault, MUTATE_CANDIDATE)
    rep = _verify(rid, MUTATE_CANDIDATE, actor="someone-else", vault_path=vault)
    assert rep["verified"] is False and rep["reason"] == "ACTOR_MISMATCH"


def test_v_hold_decision_authorizes_nothing(tmp_path):
    vault = tmp_path / "r.jsonl"
    rid = _mint_test_row(vault, MUTATE_CANDIDATE, decision="HOLD")
    rep = _verify(rid, MUTATE_CANDIDATE, vault_path=vault)
    assert rep["verified"] is False and rep["reason"] == "DECISION_NOT_SEAL"


def test_v_unsigned_row_rejected(tmp_path):
    vault = tmp_path / "r.jsonl"
    rid = _mint_test_row(vault, MUTATE_CANDIDATE, signature="")
    rep = _verify(rid, MUTATE_CANDIDATE, vault_path=vault)
    assert rep["verified"] is False and rep["reason"] == "UNSIGNED"


def test_v_tampered_row_fails_hash_integrity(tmp_path):
    vault = tmp_path / "r.jsonl"
    rid = _mint_test_row(vault, MUTATE_CANDIDATE)
    rows = [json.loads(l) for l in vault.read_text().splitlines() if l.strip()]
    rows[0]["decision"] = "VOID"  # tamper AFTER hash computation
    vault.write_text(json.dumps(rows[0], sort_keys=True) + "\n")
    rep = _verify(rid, MUTATE_CANDIDATE, vault_path=vault)
    assert rep["verified"] is False and rep["reason"] == "HASH_INTEGRITY_FAIL"


# ── (a)(b)(c) integration through the in-process MCP server ────────────────


@pytest.mark.asyncio
async def test_a_verified_actor_fake_receipt_mutate_holds():
    server = create_aaa_mcp_server()
    async with __import__("fastmcp").Client(server) as client:
        session_id = await _init_and_verify(client)
        res = await _judge(
            client,
            candidate=MUTATE_CANDIDATE,
            actor_id=TEST_ACTOR,
            session_id=session_id,
            mode="judge",
            sovereign_receipt=FAKE_RECEIPT,
            # Reachable promotion shape (reproduced 2026-11-01): this class
            # skips the F2/F9/Q9c pre-gates that mask the IRREVERSIBLE shape,
            # and the fake receipt string disarms the critical-blast Gate 4.
            reversibility_level="R2_REVERSIBLE_WRITE",
            blast_radius="federation",
        )
    blob = json.dumps(res)
    assert '"f13_promoted_allow_to_seal": true' not in blob, (
        f"(a) fake receipt must not set f13_promoted_allow_to_seal; "
        f"envelope={blob[:600]}"
    )
    assert '"verdict": "SEAL"' not in blob, (
        f"(a) no SEAL verdict may appear anywhere for a fake receipt; "
        f"envelope={blob[:600]}"
    )
    assert _verdict(res) not in ("SEAL",), (
        f"(a) fake receipt must not promote to SEAL; got verdict="
        f"{res.get('verdict')!r} full={blob[:600]}"
    )


@pytest.mark.asyncio
async def test_b_verified_actor_no_receipt_irreversible_holds():
    server = create_aaa_mcp_server()
    async with __import__("fastmcp").Client(server) as client:
        session_id = await _init_and_verify(client)
        res = await _judge(
            client,
            candidate=MUTATE_CANDIDATE,
            actor_id=TEST_ACTOR,
            session_id=session_id,
            mode="judge",
            reversibility_level="IRREVERSIBLE",
            blast_radius="federation",
        )
    assert _verdict(res) in _HOLD_FAMILY, (
        f"(b) IRREVERSIBLE without receipt must HOLD/escalate; got {res.get('verdict')!r}"
    )


@pytest.mark.asyncio
async def test_c_unverified_actor_any_receipt_not_seal():
    server = create_aaa_mcp_server()
    async with __import__("fastmcp").Client(server) as client:
        res = await _judge(
            client,
            candidate=MUTATE_CANDIDATE,
            actor_id=TEST_ACTOR,
            mode="judge",
            sovereign_receipt=FAKE_RECEIPT,
            reversibility_level="R2_REVERSIBLE_WRITE",
            blast_radius="federation",
        )
    blob = json.dumps(res)
    assert '"f13_promoted_allow_to_seal": true' not in blob, (
        f"(c) unverified actor + receipt must not set promotion flag; envelope={blob[:600]}"
    )
    assert '"verdict": "SEAL"' not in blob, (
        f"(c) unverified actor + receipt must never surface a SEAL verdict; envelope={blob[:600]}"
    )
    assert _verdict(res) not in ("SEAL",), (
        f"(c) unverified actor + receipt must never SEAL; got {res.get('verdict')!r}"
    )
