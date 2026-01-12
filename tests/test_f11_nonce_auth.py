"""
tests/test_f11_nonce_auth.py

Unit tests for F11 Nonce Manager (Command Authentication)

Tests:
1. Nonce generation
2. Valid nonce verification
3. Invalid nonce rejection
4. Replay attack prevention (nonce reuse)
5. Nonce expiration (if enabled)
6. Channel verification
7. User management (multiple users)
"""

import time

import pytest

from arifos_core.guards.nonce_manager import (
    NonceManager,
    NonceStatus,
)


class TestNonceGeneration:
    """Test nonce generation functionality."""

    def test_nonce_format(self):
        """Test that generated nonces follow X7K9F{counter} format."""
        manager = NonceManager()

        nonce1 = manager.generate_nonce("user1")
        assert nonce1.startswith("X7K9F")
        assert nonce1[5:].isdigit()  # Counter part is numeric

        nonce2 = manager.generate_nonce("user2")
        assert nonce2.startswith("X7K9F")
        assert nonce2 != nonce1  # Different nonces for different users

    def test_nonce_uniqueness(self):
        """Test that nonces are unique across generations."""
        manager = NonceManager()

        nonces = [manager.generate_nonce(f"user{i}") for i in range(10)]
        assert len(nonces) == len(set(nonces))  # All unique

    def test_nonce_counter_increment(self):
        """Test that nonce counter increments correctly."""
        manager = NonceManager()

        nonce1 = manager.generate_nonce("user1")
        nonce2 = manager.generate_nonce("user2")

        counter1 = int(nonce1[5:])
        counter2 = int(nonce2[5:])

        assert counter2 == counter1 + 1


class TestNonceVerification:
    """Test nonce verification functionality."""

    def test_valid_nonce_verification(self):
        """Test that valid nonces are accepted."""
        manager = NonceManager()

        nonce = manager.generate_nonce("user123")
        result = manager.verify_nonce("user123", nonce)

        assert result.status == "PASS"
        assert result.nonce_status == NonceStatus.VALID
        assert result.authenticated is True
        assert "verified" in result.reason.lower()

    def test_invalid_nonce_rejection(self):
        """Test that invalid nonces are rejected."""
        manager = NonceManager()

        manager.generate_nonce("user123")  # Generate correct nonce
        result = manager.verify_nonce("user123", "X7K9F999")  # Wrong nonce

        assert result.status == "SABAR"
        assert result.nonce_status == NonceStatus.INVALID
        assert result.authenticated is False
        assert "invalid nonce" in result.reason.lower()

    def test_verification_without_generation(self):
        """Test verification fails if no nonce was generated."""
        manager = NonceManager()

        result = manager.verify_nonce("user123", "X7K9F1")

        assert result.status == "SABAR"
        assert result.nonce_status == NonceStatus.INVALID
        assert result.authenticated is False
        assert "no nonce found" in result.reason.lower()


class TestReplayAttackPrevention:
    """Test replay attack prevention (Pauli Exclusion)."""

    def test_nonce_reuse_blocked(self):
        """Test that using the same nonce twice is blocked."""
        manager = NonceManager()

        nonce = manager.generate_nonce("user123")

        # First use: should succeed
        result1 = manager.verify_nonce("user123", nonce)
        assert result1.status == "PASS"
        assert result1.authenticated is True

        # Second use: should fail (replay attack)
        result2 = manager.verify_nonce("user123", nonce)
        assert result2.status == "SABAR"
        assert result2.nonce_status == NonceStatus.REPLAY
        assert result2.authenticated is False
        assert "replay attack" in result2.reason.lower()

    def test_different_users_cannot_reuse_nonce(self):
        """Test that nonces are user-specific."""
        manager = NonceManager()

        nonce1 = manager.generate_nonce("user1")
        nonce2 = manager.generate_nonce("user2")

        # User1 uses their nonce: success
        result1 = manager.verify_nonce("user1", nonce1)
        assert result1.status == "PASS"

        # User2 tries to use user1's nonce: fail
        result2 = manager.verify_nonce("user2", nonce1)
        assert result2.status == "SABAR"


class TestNonceExpiration:
    """Test nonce expiration functionality."""

    def test_expiration_disabled_by_default(self):
        """Test that nonces don't expire by default."""
        manager = NonceManager()  # No expiration set

        nonce = manager.generate_nonce("user123")
        time.sleep(0.1)  # Wait a bit

        result = manager.verify_nonce("user123", nonce)
        assert result.status == "PASS"  # Should still work

    def test_expiration_enforced_when_enabled(self):
        """Test that expired nonces are rejected."""
        manager = NonceManager(nonce_expiration_seconds=1)  # 1 second expiration

        nonce = manager.generate_nonce("user123")
        time.sleep(1.5)  # Wait for expiration

        result = manager.verify_nonce("user123", nonce)
        assert result.status == "SABAR"
        assert result.nonce_status == NonceStatus.EXPIRED
        assert "expired" in result.reason.lower()

    def test_non_expired_nonce_accepted(self):
        """Test that non-expired nonces are still accepted."""
        manager = NonceManager(nonce_expiration_seconds=10)  # 10 second expiration

        nonce = manager.generate_nonce("user123")
        time.sleep(0.1)  # Short wait, not expired

        result = manager.verify_nonce("user123", nonce)
        assert result.status == "PASS"


class TestChannelVerification:
    """Test channel verification functionality."""

    def test_channel_verification_success(self):
        """Test that matching channel identifiers pass verification."""
        manager = NonceManager()

        channel_id = "direct_input_stream_abc123"
        nonce = manager.generate_nonce("user123", channel_identifier=channel_id)

        result = manager.verify_nonce("user123", nonce, channel_identifier=channel_id)
        assert result.status == "PASS"

    def test_channel_mismatch_blocked(self):
        """Test that mismatched channels are blocked (paste attack)."""
        manager = NonceManager()

        original_channel = "direct_input_stream_abc123"
        nonce = manager.generate_nonce("user123", channel_identifier=original_channel)

        # Try to verify from different channel (e.g., pasted)
        different_channel = "clipboard_paste_xyz789"
        result = manager.verify_nonce("user123", nonce, channel_identifier=different_channel)

        assert result.status == "SABAR"
        assert "channel mismatch" in result.reason.lower()
        assert "paste attack" in result.reason.lower()


class TestMultipleUsers:
    """Test management of multiple users simultaneously."""

    def test_multiple_users_independent_nonces(self):
        """Test that multiple users can have independent nonces."""
        manager = NonceManager()

        users = [f"user{i}" for i in range(5)]
        nonces = {user: manager.generate_nonce(user) for user in users}

        # All nonces should be different
        assert len(set(nonces.values())) == len(users)

        # Each user can verify their own nonce
        for user, nonce in nonces.items():
            result = manager.verify_nonce(user, nonce)
            assert result.status == "PASS"

    def test_nonce_revocation(self):
        """Test that nonces can be revoked."""
        manager = NonceManager()

        nonce = manager.generate_nonce("user123")

        # Revoke the nonce
        revoked = manager.revoke_nonce("user123")
        assert revoked is True

        # Try to verify revoked nonce
        result = manager.verify_nonce("user123", nonce)
        assert result.status == "SABAR"  # Should fail

    def test_get_current_nonce(self):
        """Test retrieval of current nonce."""
        manager = NonceManager()

        # No nonce yet
        assert manager.get_current_nonce("user123") is None

        # Generate nonce
        nonce = manager.generate_nonce("user123")

        # Retrieve it
        retrieved = manager.get_current_nonce("user123")
        assert retrieved == nonce


class TestEdgeCases:
    """Edge case tests for nonce manager."""

    def test_empty_user_id(self):
        """Test handling of empty user ID."""
        manager = NonceManager()

        nonce = manager.generate_nonce("")
        assert nonce.startswith("X7K9F")

        result = manager.verify_nonce("", nonce)
        assert result.status == "PASS"

    def test_special_characters_in_user_id(self):
        """Test handling of special characters in user ID."""
        manager = NonceManager()

        user_ids = ["user@example.com", "user-123", "user_456", "用户789"]

        for user_id in user_ids:
            nonce = manager.generate_nonce(user_id)
            result = manager.verify_nonce(user_id, nonce)
            assert result.status == "PASS"

    def test_concurrent_nonce_generation(self):
        """Test rapid concurrent nonce generation."""
        manager = NonceManager()

        nonces = [manager.generate_nonce(f"user{i}") for i in range(100)]
        assert len(nonces) == len(set(nonces))  # All unique


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
