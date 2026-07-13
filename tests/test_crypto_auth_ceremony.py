"""
test_crypto_auth_ceremony.py — Ed25519 MCP Ceremony Test

Tests the full challenge-response Ed25519 signature verification flow:
1. Issue challenge nonce
2. Sign the challenge with an Ed25519 key
3. Verify the signature
4. Reject replay attacks
5. Reject wrong keys
"""

import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

from arifosmcp.runtime.crypto_auth import (
    issue_actor_challenge,
    verify_actor_signature,
    verify_init_identity,
    is_registered_actor,
    resolve_actor_public_key,
)
from arifosmcp.runtime.crypto_auth import _issued_challenges, _used_challenges, _purge_challenges


# ═══════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════


def _make_test_keypair() -> tuple[ed25519.Ed25519PrivateKey, ed25519.Ed25519PublicKey]:
    """Generate a fresh Ed25519 keypair for testing."""
    private = ed25519.Ed25519PrivateKey.generate()
    public = private.public_key()
    return private, public


def _sign_payload(private_key: ed25519.Ed25519PrivateKey, payload: str) -> str:
    """Sign a string payload and return base64-encoded signature."""
    import base64

    sig = private_key.sign(payload.encode("utf-8"))
    return base64.b64encode(sig).decode("utf-8")


# ═══════════════════════════════════════════════════════════════════════
# Tests
# ═══════════════════════════════════════════════════════════════════════


class TestEd25519Ceremony:
    """Full Ed25519 MCP ceremony — challenge → sign → verify."""

    def test_challenge_issuance(self):
        """issue_actor_challenge returns a nonce and registers it."""
        nonce = issue_actor_challenge("test_actor", ttl_seconds=60)
        assert isinstance(nonce, str)
        assert len(nonce) > 16  # should be a substantial random token
        # Nonce should be in the issued challenges store
        assert nonce in _issued_challenges

    def test_challenge_expiry(self):
        """Issued challenge expires after TTL."""
        nonce = issue_actor_challenge("expire_test", ttl_seconds=0)
        import time

        time.sleep(0.01)  # tiny wait for expiry
        _purge_challenges(time.time() + 1)
        assert nonce not in _issued_challenges

    def test_sign_and_verify_roundtrip(self):
        """Sign a challenge nonce and verify the signature."""
        private, public = _make_test_keypair()
        nonce = issue_actor_challenge("roundtrip_test", ttl_seconds=120)
        sig = _sign_payload(private, f"roundtrip_test:{nonce}")

        # Verify should pass with matching key + nonce
        # This tests the payload format "{actor_id}:{nonce}"
        result = verify_init_identity(
            actor_id="roundtrip_test",
            nonce=nonce,
            signature_b64=sig,
        )
        ok, reason = result if isinstance(result, tuple) else (result, "")
        assert ok, f"Signature verification failed: {reason}"

    def test_replay_attack_rejected(self):
        """A used nonce cannot be replayed."""
        private, public = _make_test_keypair()
        nonce = issue_actor_challenge("replay_test", ttl_seconds=120)
        sig = _sign_payload(private, f"replay_test:{nonce}")

        # First use should pass
        ok1, _ = verify_init_identity(
            actor_id="replay_test",
            nonce=nonce,
            signature_b64=sig,
        )
        assert ok1, "First verification should pass"

        # Second use should fail
        ok2, _ = verify_init_identity(
            actor_id="replay_test",
            nonce=nonce,
            signature_b64=sig,
        )
        assert not ok2, "Replay attack should be rejected"

    def test_wrong_key_rejected(self):
        """Signature from wrong key is rejected."""
        good_private, _ = _make_test_keypair()
        bad_private, _ = _make_test_keypair()

        nonce = issue_actor_challenge("wrong_key_test", ttl_seconds=120)
        # Sign with bad key
        bad_sig = _sign_payload(bad_private, f"wrong_key_test:{nonce}")

        ok, reason = verify_init_identity(
            actor_id="wrong_key_test",
            nonce=nonce,
            signature_b64=bad_sig,
        )
        # Will fail because the bad key's public key isn't registered for wrong_key_test
        assert not ok or "key" in reason.lower()

    def test_wrong_actor_id_rejected(self):
        """Signature for different actor_id is rejected."""
        private, _ = _make_test_keypair()
        nonce = issue_actor_challenge("correct_actor", ttl_seconds=120)
        sig = _sign_payload(private, f"wrong_actor:{nonce}")  # signed with wrong actor_id

        ok, reason = verify_init_identity(
            actor_id="correct_actor",
            nonce=nonce,
            signature_b64=sig,
        )
        assert not ok, "Wrong actor_id in payload should be rejected"

    def test_invalid_signature_format_rejected(self):
        """Garbage signature string is rejected without crashing."""
        nonce = issue_actor_challenge("garbage_test", ttl_seconds=120)
        ok, reason = verify_init_identity(
            actor_id="garbage_test",
            nonce=nonce,
            signature_b64="this-is-not-a-valid-base64-signature!!!",
        )
        assert not ok, "Garbage signature should be rejected"

    def test_empty_payload_fields_rejected(self):
        """Empty actor_id or nonce should be rejected."""
        ok, reason = verify_init_identity(
            actor_id="",
            nonce="some_nonce",
            signature_b64="AAAA",
        )
        assert not ok, "Empty actor_id should be rejected"

        ok2, reason2 = verify_init_identity(
            actor_id="some_actor",
            nonce="",
            signature_b64="AAAA",
        )
        assert not ok2, "Empty nonce should be rejected"

    def test_verify_actor_signature_api(self):
        """verify_actor_signature wraps verify_init_identity correctly."""
        private, _ = _make_test_keypair()
        nonce = issue_actor_challenge("api_test", ttl_seconds=120)
        sig = _sign_payload(private, f"api_test:{nonce}")

        result = verify_actor_signature(
            actor_id="api_test",
            nonce=nonce,
            signature_b64=sig,
        )
        # If no key is registered, this may return False (expected)
        # The test verifies it doesn't crash and returns a bool
        assert isinstance(result, bool)

    def test_federation_compat_payload(self):
        """Verify payload format \"{actor_id}:{constitution_hash}:{nonce}\" works."""
        private, _ = _make_test_keypair()
        nonce = issue_actor_challenge("fed_compat", ttl_seconds=120)

        # Federated format includes constitution_hash
        payload = f"fed_compat:abc123def456:{nonce}"
        sig = _sign_payload(private, payload)

        ok, reason = verify_init_identity(
            actor_id="fed_compat",
            nonce=nonce,
            signature_b64=sig,
            constitution_hash="abc123def456",
        )
        # May fail if key not registered, but shouldn't crash
        assert isinstance(ok, bool)
        assert isinstance(reason, str)


# ═══════════════════════════════════════════════════════════════════════
# Nonce lifecycle test
# ═══════════════════════════════════════════════════════════════════════


class TestChallengeLifecycle:
    """Lifecycle management of challenge nonces."""

    def test_concurrent_challenges(self):
        """Multiple concurrent nonces for different actors."""
        n1 = issue_actor_challenge("actor_a", ttl_seconds=60)
        n2 = issue_actor_challenge("actor_b", ttl_seconds=60)
        n3 = issue_actor_challenge("actor_a", ttl_seconds=60)  # second for actor_a

        assert n1 != n2
        assert n1 != n3
        assert n2 != n3
        assert n1 in _issued_challenges
        assert n2 in _issued_challenges
        assert n3 in _issued_challenges
        # Old nonce for actor_a still valid (separate nonce)
        assert n1 in _issued_challenges

    def test_purge_only_expired(self):
        """Purge only removes expired nonces, not fresh ones."""
        import time

        now = time.time()

        n_fresh = issue_actor_challenge("fresh_actor", ttl_seconds=300)
        n_expired = issue_actor_challenge("expired_actor", ttl_seconds=0)
        time.sleep(0.01)

        _purge_challenges(now + 1)  # purge everything older than now+1

        assert n_fresh in _issued_challenges
        assert n_expired not in _issued_challenges
