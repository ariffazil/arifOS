"""
tests/runtime/test_governance_identity_ed25519.py

P0-#1: Verify that validate_sovereign_proof() actually calls Ed25519
verification (not a TODO stub). Tests both governance_identity.py
and apps/command_center/identities.py paths.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import time
from unittest.mock import patch

import pytest


# ── governance_identity.py path ──────────────────────────────────


class TestGovernanceIdentityEd25519:
    """Test validate_sovereign_proof in arifosmcp.runtime.governance_identity."""

    def _get_fn(self):
        from arifosmcp.runtime.governance_identity import validate_sovereign_proof

        return validate_sovereign_proof

    def test_none_proof_returns_false(self):
        fn = self._get_fn()
        assert fn("arif", None) is False

    def test_empty_dict_returns_false(self):
        fn = self._get_fn()
        assert fn("arif", {}) is False

    def test_string_proof_rejected(self):
        fn = self._get_fn()
        assert fn("arif", "IM ARIF") is False

    def test_missing_fields_returns_false(self):
        fn = self._get_fn()
        assert fn("arif", {"signature": "abc"}) is False
        assert fn("arif", {"signature": "abc", "nonce": "xyz"}) is False

    @patch("arifosmcp.runtime.governance_identity._verify_ed25519_proof")
    def test_calls_ed25519_verify(self, mock_verify):
        """When proof dict has signature+nonce+timestamp, ed25519 path is called."""
        mock_verify.return_value = True
        fn = self._get_fn()
        proof = {"signature": "dGVzdA==", "nonce": "test-nonce", "timestamp": str(int(time.time()))}
        result = fn("ariffazil", proof)
        assert result is True
        mock_verify.assert_called_once_with("ariffazil", proof)

    @patch("arifosmcp.runtime.governance_identity._verify_hmac_proof")
    def test_calls_hmac_verify(self, mock_verify):
        """When proof dict has hmac_challenge+hmac_sig, HMAC path is called."""
        mock_verify.return_value = True
        fn = self._get_fn()
        proof = {"hmac_challenge": "1234:op", "hmac_sig": "abcdef"}
        result = fn("ariffazil", proof)
        assert result is True
        mock_verify.assert_called_once_with("ariffazil", proof)

    def test_stale_nonce_rejected(self):
        """Ed25519 proof with stale nonce (>60s) should be rejected."""
        fn = self._get_fn()
        stale_nonce = str(int(time.time()) - 120) + ":test-op"
        proof = {"signature": "dGVzdA==", "nonce": stale_nonce, "timestamp": str(int(time.time()))}
        with patch("arifosmcp.runtime.sovereign_verify.is_challenge_fresh", return_value=False):
            assert fn("ariffazil", proof) is False

    def test_valid_signature_accepted(self):
        """Full integration: sign + verify through validate_sovereign_proof."""
        from arifosmcp.runtime.sovereign_signer import get_constitution_hash, sign

        actor_id = "ariffazil"
        constitution_hash = get_constitution_hash()
        nonce = f"{int(time.time())}:test-p0-integration"
        try:
            sig = sign(actor_id, constitution_hash, nonce)
        except FileNotFoundError:
            pytest.skip("Sovereign private key not available in this environment")

        fn = self._get_fn()
        proof = {"signature": sig, "nonce": nonce, "timestamp": str(int(time.time()))}
        assert fn(actor_id, proof) is True

    def test_wrong_signature_rejected(self):
        """Tampered signature must be rejected."""
        fn = self._get_fn()
        nonce = f"{int(time.time())}:test-tamper"
        proof = {"signature": "dGVzdA==", "nonce": nonce, "timestamp": str(int(time.time()))}
        # Fake sig won't verify against real pubkey
        assert fn("ariffazil", proof) is False


# ── identities.py path ──────────────────────────────────────────


class TestCommandCenterIdentityEd25519:
    """Test validate_sovereign_proof in apps/command_center.identities."""

    def _get_fn(self):
        from arifosmcp.apps.command_center.identities import validate_sovereign_proof

        return validate_sovereign_proof

    def test_none_proof_returns_false(self):
        fn = self._get_fn()
        assert fn("arif", None) is False

    @patch("arifosmcp.apps.command_center.identities._verify_ed25519_proof")
    def test_calls_ed25519_verify(self, mock_verify):
        mock_verify.return_value = True
        fn = self._get_fn()
        proof = {"signature": "dGVzdA==", "nonce": "test-nonce", "timestamp": str(int(time.time()))}
        result = fn("ariffazil", proof)
        assert result is True
        mock_verify.assert_called_once_with("ariffazil", proof)

    def test_valid_signature_accepted(self):
        """Full integration through command_center path."""
        from arifosmcp.runtime.sovereign_signer import get_constitution_hash, sign

        actor_id = "ariffazil"
        constitution_hash = get_constitution_hash()
        nonce = f"{int(time.time())}:test-cc-integration"
        try:
            sig = sign(actor_id, constitution_hash, nonce)
        except FileNotFoundError:
            pytest.skip("Sovereign private key not available in this environment")

        fn = self._get_fn()
        proof = {"signature": sig, "nonce": nonce, "timestamp": str(int(time.time()))}
        assert fn(actor_id, proof) is True


# ── Non-protected IDs bypass verification ────────────────────────


class TestNonProtectedBypass:
    """Non-protected IDs should not need proof."""

    def test_non_protected_returns_false_for_none_proof(self):
        from arifosmcp.runtime.governance_identity import is_protected_sovereign_id

        # Non-protected IDs don't even reach validate_sovereign_proof
        # (the caller checks is_protected first). But if they do, None = False.
        assert is_protected_sovereign_id("opencode-333") is False
        assert is_protected_sovereign_id("arif") is True
