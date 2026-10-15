"""
test_signed_envelope.py — tamper tests for SIGNED-ENVELOPE v1 (GAP #1 slice).

Spec: arifosmcp/docs/SIGNED-ENVELOPE-v1.md
Proves:
  (a) valid envelope verifies
  (b) any byte-tamper of payload or actor_id is rejected
  (c) replayed nonce within window rejected
  (d) wrong-key signature rejected
plus window expiry, flag gating (check_arguments), canonical determinism,
and a real-key integration case against the AAA registry (skipped when the
host key material is absent).

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arifosmcp.runtime import signed_envelope as se
from arifosmcp.runtime.signed_envelope import (
    KEY_NOT_REGISTERED,
    MALFORMED_ENVELOPE,
    NONCE_REPLAY,
    PAYLOAD_HASH_MISMATCH,
    SIGNATURE_INVALID,
    TIMESTAMP_OUT_OF_WINDOW,
    NonceStore,
    payload_digest,
    sign_envelope,
    verify_envelope,
)

PAYLOAD = {"name": "arif_init", "arguments": {"actor_id": "aaa-gateway"}, "task": "gap1"}


@pytest.fixture()
def keypair():
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()
    return priv, pub


def test_a_valid_envelope_verifies(keypair):
    priv, pub = keypair
    env = sign_envelope(
        actor_id="test-agent",
        session_id="sess-1",
        payload=PAYLOAD,
        private_key=priv,
    )
    ok, code = verify_envelope(env, PAYLOAD, resolve_key=lambda _a: pub)
    assert ok is True
    assert code == "OK"


def test_b_payload_tamper_rejected(keypair):
    priv, pub = keypair
    env = sign_envelope(
        actor_id="test-agent", session_id="sess-1", payload=PAYLOAD, private_key=priv
    )
    tampered = dict(PAYLOAD)
    tampered["task"] = "gap1-TAMPERED"
    ok, code = verify_envelope(env, tampered, resolve_key=lambda _a: pub)
    assert ok is False
    assert code == PAYLOAD_HASH_MISMATCH


def test_b_actor_tamper_rejected(keypair):
    priv, pub = keypair
    env = sign_envelope(
        actor_id="test-agent", session_id="sess-1", payload=PAYLOAD, private_key=priv
    )
    forged = dict(env)
    forged["actor_id"] = "someone-else"
    ok, code = verify_envelope(forged, PAYLOAD, resolve_key=lambda a: pub if a == "someone-else" else pub)
    assert ok is False
    assert code == SIGNATURE_INVALID


def test_b_sig_byte_tamper_rejected(keypair):
    priv, pub = keypair
    env = sign_envelope(
        actor_id="test-agent", session_id="sess-1", payload=PAYLOAD, private_key=priv
    )
    raw = bytearray(__import__("base64").b64decode(env["sig"]))
    raw[0] ^= 0x01
    env["sig"] = __import__("base64").b64encode(bytes(raw)).decode()
    ok, code = verify_envelope(env, PAYLOAD, resolve_key=lambda _a: pub)
    assert ok is False
    assert code == SIGNATURE_INVALID


def test_c_replayed_nonce_rejected_within_window(keypair):
    priv, pub = keypair
    env = sign_envelope(
        actor_id="test-agent",
        session_id="sess-1",
        payload=PAYLOAD,
        private_key=priv,
        nonce="ab" * 16,
        timestamp=1_000_000,
    )
    store = NonceStore()
    ok1, _ = verify_envelope(
        env, PAYLOAD, now=1_000_000, window_seconds=300, nonce_store=store, resolve_key=lambda _a: pub
    )
    assert ok1 is True
    ok2, code2 = verify_envelope(
        env, PAYLOAD, now=1_000_100, window_seconds=300, nonce_store=store, resolve_key=lambda _a: pub
    )
    assert ok2 is False
    assert code2 == NONCE_REPLAY


def test_c_nonce_reusable_after_window_expiry(keypair):
    priv, pub = keypair
    env = sign_envelope(
        actor_id="test-agent",
        session_id="sess-1",
        payload=PAYLOAD,
        private_key=priv,
        nonce="cd" * 16,
        timestamp=2_000_000,
    )
    store = NonceStore()
    ok1, _ = verify_envelope(
        env, PAYLOAD, now=2_000_000, window_seconds=300, nonce_store=store, resolve_key=lambda _a: pub
    )
    assert ok1 is True
    ok2, code2 = verify_envelope(
        env, PAYLOAD, now=2_000_301, window_seconds=300, nonce_store=store, resolve_key=lambda _a: pub
    )
    # Outside the window the timestamp check fires before replay could — either
    # way the call is rejected; past-window replay must never PASS.
    assert ok2 is False
    assert code2 in (NONCE_REPLAY, TIMESTAMP_OUT_OF_WINDOW)


def test_d_wrong_key_signature_rejected(keypair):
    priv, _pub = keypair
    impostor = Ed25519PrivateKey.generate()
    env = sign_envelope(
        actor_id="test-agent", session_id="sess-1", payload=PAYLOAD, private_key=priv
    )
    ok, code = verify_envelope(env, PAYLOAD, resolve_key=lambda _a: impostor.public_key())
    assert ok is False
    assert code == SIGNATURE_INVALID


def test_d_unregistered_actor_rejected(keypair):
    priv, pub = keypair
    env = sign_envelope(
        actor_id="ghost", session_id="sess-1", payload=PAYLOAD, private_key=priv
    )
    ok, code = verify_envelope(env, PAYLOAD, resolve_key=lambda _a: None)
    assert ok is False
    assert code == KEY_NOT_REGISTERED


def test_timestamp_out_of_window_rejected(keypair):
    priv, pub = keypair
    env = sign_envelope(
        actor_id="test-agent",
        session_id="sess-1",
        payload=PAYLOAD,
        private_key=priv,
        timestamp=1_000_000,
    )
    ok, code = verify_envelope(
        env, PAYLOAD, now=1_000_000 + 301, window_seconds=300, resolve_key=lambda _a: pub
    )
    assert ok is False
    assert code == TIMESTAMP_OUT_OF_WINDOW


def test_malformed_envelope_rejected(keypair):
    _, pub = keypair
    ok, code = verify_envelope({"v": 1, "alg": "rsa256"}, PAYLOAD, resolve_key=lambda _a: pub)
    assert ok is False
    assert code in (MALFORMED_ENVELOPE, "ENVELOPE_MISSING_FIELDS")


def test_canonical_determinism():
    a = {"b": 2, "a": 1, "c": {"z": [2, 1], "y": "ä"}}
    b = {"c": {"y": "ä", "z": [2, 1]}, "a": 1, "b": 2}
    assert se.canonical_bytes(a) == se.canonical_bytes(b)
    assert payload_digest(a) == payload_digest(b)


def test_check_arguments_flag_gating(keypair, monkeypatch):
    priv, pub = keypair
    monkeypatch.delenv("ARIF_ENVELOPE_SIGNED", raising=False)
    # Flag off: everything passes through untouched, even a garbage envelope.
    assert se.check_arguments({"signed_envelope": {"junk": True}}) is None
    assert se.check_arguments(None) is None

    monkeypatch.setenv("ARIF_ENVELOPE_SIGNED", "1")
    env = sign_envelope(
        actor_id="test-agent", session_id="s", payload=PAYLOAD, private_key=priv
    )
    good = {**PAYLOAD, "signed_envelope": env}
    assert se.check_arguments(good, resolve_key=lambda _a: pub) is None  # valid → proceed

    bad_env = dict(env)
    bad_env["payload_hash"] = "0" * 64
    bad = {**PAYLOAD, "signed_envelope": bad_env}
    rejection = se.check_arguments(bad, resolve_key=lambda _a: pub)
    assert rejection is not None
    assert rejection["code"] == PAYLOAD_HASH_MISMATCH

    # Absent envelope under flag-on still passes this slice (spec §6).
    assert se.check_arguments(dict(PAYLOAD)) is None


def test_real_aaa_key_end_to_end():
    """Sign with the real AAA control-plane key, verify via registries."""
    key_path = Path("/root/AAA/auth/keys/aaa_private.key")
    if not key_path.is_file():
        pytest.skip("AAA control-plane key not present on this host")
    env = sign_envelope(
        actor_id="aaa", session_id="integration-gap1", payload=PAYLOAD, key_path=str(key_path)
    )
    ok, code = verify_envelope(env, PAYLOAD)  # default resolver chain
    assert ok is True, f"real-key verify failed: {code}"
    assert env["actor_id"] == "aaa"
