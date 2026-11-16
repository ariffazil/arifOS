"""CACAT B red/green tests — arif_verify pubkey-registry binding (F1/F11).

Defect class: the MCP verify lane (`arif_verify` / _arif_ed25519_verify_tool)
verified signatures against the CALLER-SUPPLIED public key. Any Ed25519 key
holder could consume a challenge issued for a registered actor and get
verified=true — possession of *some* key, never *the registered key*.

Contract under test (single source of truth, K7):
  1. If a registered pubkey resolves for the claimed actor, the signature MUST
     verify against the REGISTERED key and the caller-supplied key MUST equal
     it; mismatch => verified=False reason=pubkey_registry_mismatch.
  2. Honest path (registered key + matching signature) => verified=True.
  3. Unregistered/anon actors keep the derived-fingerprint binding
     (self-asserted anon, no authority promotion).
"""

import base64
import asyncio

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
)

from arifosmcp.runtime import crypto_auth
from arifosmcp.runtime import tools as _tools
from arifosmcp.runtime.tools import _arif_ed25519_verify_tool

# The module binds arif_verify through the Epoch-1 canonical wrapper, which
# flattens the raw result into the session envelope. Test the RAW contract
# (the function body at tools.py:26571) via functools.wraps' __wrapped__.
_arif_verify_raw = _arif_ed25519_verify_tool.__wrapped__

ACTOR = "kimi-code"  # in _ALWAYS_CHALLENGEABLE — issuance needs no registry


def _keypair() -> tuple[Ed25519PrivateKey, str]:
    sk = Ed25519PrivateKey.generate()
    pk_hex = sk.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()
    return sk, pk_hex


def _sign(sk: Ed25519PrivateKey, actor_id: str, challenge: str) -> str:
    payload = f"{actor_id}:{challenge}".encode()
    return base64.b64encode(sk.sign(payload)).decode()


def _pub(sk: Ed25519PrivateKey):
    return sk.public_key()


@pytest.fixture()
def registry(monkeypatch):
    """Honest registry: kimi-code resolves to HONEST key; others resolve None."""
    honest_sk, honest_hex = _keypair()
    monkeypatch.setattr(
        crypto_auth,
        "resolve_actor_public_key",
        lambda actor_id: (
            _pub(honest_sk) if crypto_auth._normalize_actor(actor_id) == ACTOR else None
        ),
    )
    return {"sk": honest_sk, "hex": honest_hex}


def _challenge_for(actor_id: str) -> str:
    challenge, _ = crypto_auth.issue_actor_challenge_b64(actor_id, ttl_seconds=60)
    return challenge


def test_forged_key_rejected_for_registered_actor(registry):
    """RED under defect: attacker key signed the challenge, registry key differs."""
    challenge = _challenge_for(ACTOR)
    atk_sk, atk_hex = _keypair()
    sig = _sign(atk_sk, ACTOR, challenge)
    res = asyncio.run(
        _arif_verify_raw(
            challenge=challenge,
            signature=sig,
            actor_pubkey=atk_hex,
            session_id="",
            actor_id=ACTOR,
        )
    )
    assert res.get("verified") is False, res
    assert res.get("reason") == "pubkey_registry_mismatch", res


def test_registered_key_accepted(registry):
    """GREEN both sides: registry key + honest signature => verified."""
    challenge = _challenge_for(ACTOR)
    sig = _sign(registry["sk"], ACTOR, challenge)
    res = asyncio.run(
        _arif_verify_raw(
            challenge=challenge,
            signature=sig,
            actor_pubkey=registry["hex"],
            session_id="",
            actor_id=ACTOR,
        )
    )
    assert res.get("verified") is True, res
    assert res.get("ed25519_verified") is False  # no session_id => not bound


def test_anon_fingerprint_path_unchanged(registry):
    """Unregistered caller: fingerprint-derived binding still works (no authority)."""
    import hashlib

    anon_sk, anon_hex = _keypair()
    fingerprint = f"anon:{hashlib.sha256(bytes.fromhex(anon_hex)).hexdigest()[:16]}"
    challenge = _challenge_for(ACTOR)  # issuance still from the challengeable set
    rec = crypto_auth._issued_challenges[challenge]
    rec.actor_id = fingerprint  # self-asserted anon binding, as before the fix
    res = asyncio.run(
        _arif_verify_raw(
            challenge=challenge,
            signature=_sign(anon_sk, fingerprint, challenge),
            actor_pubkey=anon_hex,
            session_id="",
            actor_id=None,
        )
    )
    assert res.get("verified") is True, res
    assert str(res.get("actor_id", "")).startswith("anon:"), res


def test_registry_unavailable_fails_closed(registry, monkeypatch):
    """Identity surface fails CLOSED when registry lookup raises."""

    def _boom(actor_id):
        raise RuntimeError("registry down")

    monkeypatch.setattr(crypto_auth, "resolve_actor_public_key", _boom)
    challenge = _challenge_for(ACTOR)
    sig = _sign(registry["sk"], ACTOR, challenge)
    res = asyncio.run(
        _arif_verify_raw(
            challenge=challenge,
            signature=sig,
            actor_pubkey=registry["hex"],
            session_id="",
            actor_id=ACTOR,
        )
    )
    assert res.get("verified") is False, res
    assert "pubkey_registry" in str(res.get("reason")), res
