"""
tests/security/test_tokens.py — F11 Command Auth: Token Tests

Tests for core/security/tokens.py with open mode and semantic bypass.
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import os
import pytest
from unittest.mock import patch

from core.security.tokens import (
    TokenResult,
    ValidationResult,
    mint_governance_token,
    validate_governance_token,
    hash_governance_token,
    clear_nonce_registry,
    _actor_clearance,
    _current_bucket,
    BOOTSTRAP_ACTORS,
    OPEN_MODE,
    SEMANTIC_BYPASS_ACTORS,
)


class TestTokenResult:
    """Test the TokenResult dataclass."""

    def test_token_result_defaults(self):
        """TokenResult should have sensible defaults."""
        result = TokenResult(valid=False)
        assert result.valid is False
        assert result.token == ""
        assert result.session_id == ""
        assert result.actor_id == ""
        assert result.clearance == "none"
        assert result.error == ""

    def test_token_result_with_values(self):
        """TokenResult should accept all values."""
        result = TokenResult(
            valid=True,
            token="test.token.signature",
            session_id="sess-123",
            actor_id="arif",
            clearance="sovereign",
        )
        assert result.valid is True
        assert result.token == "test.token.signature"
        assert result.session_id == "sess-123"
        assert result.actor_id == "arif"
        assert result.clearance == "sovereign"


class TestValidationResult:
    """Test the ValidationResult dataclass."""

    def test_validation_result_defaults(self):
        """ValidationResult should have sensible defaults."""
        result = ValidationResult(valid=False)
        assert result.valid is False
        assert result.session_id == ""
        assert result.actor_id == ""
        assert result.clearance == "none"
        assert result.error == ""
        assert result.expired is False


class TestActorClearance:
    """Test the actor clearance determination."""

    def test_sovereign_prefix(self):
        """Actor IDs with 'sovereign:' prefix get sovereign clearance."""
        assert _actor_clearance("sovereign:admin") == "sovereign"
        assert _actor_clearance("sovereign:user") == "sovereign"

    def test_apex_prefix(self):
        """Actor IDs with 'apex:' prefix get apex clearance."""
        assert _actor_clearance("apex:engineer") == "apex"
        assert _actor_clearance("apex:auditor") == "apex"

    def test_agent_prefix(self):
        """Actor IDs with 'agent:' prefix get agent clearance."""
        assert _actor_clearance("agent:claude") == "agent"
        assert _actor_clearance("agent:gpt") == "agent"

    def test_user_default(self):
        """Regular actor IDs get user clearance by default."""
        assert _actor_clearance("arif") == "user"
        assert _actor_clearance("john") == "user"
        assert _actor_clearance("admin") == "user"


class TestCurrentBucket:
    """Test the timestamp bucket function."""

    def test_bucket_is_integer(self):
        """Current bucket should return an integer."""
        bucket = _current_bucket()
        assert isinstance(bucket, int)

    def test_bucket_increases_over_time(self):
        """Bucket should be based on time and increase."""
        import time

        bucket1 = _current_bucket()
        time.sleep(0.01)  # Small sleep
        bucket2 = _current_bucket()
        # Buckets should be the same (5-minute windows)
        assert bucket1 == bucket2


class TestMintGovernanceToken:
    """Test token minting functionality."""

    def test_mint_with_whitelisted_actor(self):
        """Should mint token for whitelisted actor."""
        with patch("core.security.tokens.BOOTSTRAP_ACTORS", {"testuser"}):
            result = mint_governance_token(
                actor_id="testuser",
                session_id="sess-123",
            )
            assert result.valid is True
            assert result.actor_id == "testuser"
            assert result.session_id == "sess-123"
            assert result.token != ""
            assert result.clearance == "user"

    def test_mint_with_semantic_bypass_arif(self):
        """Actor 'arif' should bypass whitelist and get sovereign clearance."""
        with patch("core.security.tokens.BOOTSTRAP_ACTORS", set()):
            result = mint_governance_token(
                actor_id="arif",
                session_id="sess-123",
            )
            assert result.valid is True
            assert result.actor_id == "arif"
            assert result.clearance == "sovereign"  # Bypass gets sovereign

    def test_mint_with_semantic_bypass_sovereign(self):
        """Actor 'sovereign' should bypass whitelist."""
        with patch("core.security.tokens.BOOTSTRAP_ACTORS", set()):
            result = mint_governance_token(
                actor_id="sovereign",
                session_id="sess-123",
            )
            assert result.valid is True
            assert result.clearance == "sovereign"

    def test_mint_rejects_non_whitelisted(self):
        """Should reject non-whitelisted actors when BOOTSTRAP_ACTORS is set."""
        with patch("core.security.tokens.BOOTSTRAP_ACTORS", {"alloweduser"}):
            result = mint_governance_token(
                actor_id="unauthorized",
                session_id="sess-123",
            )
            assert result.valid is False
            assert "F11_AUTH_FAILURE" in result.error

    def test_mint_with_open_mode(self):
        """Should accept any actor when OPEN_MODE is enabled."""
        with patch("core.security.tokens.OPEN_MODE", True):
            with patch("core.security.tokens.BOOTSTRAP_ACTORS", {"otheruser"}):
                result = mint_governance_token(
                    actor_id="randomuser",
                    session_id="sess-123",
                )
                assert result.valid is True
                assert result.actor_id == "randomuser"

    def test_mint_token_structure(self):
        """Minted token should have correct structure."""
        result = mint_governance_token(
            actor_id="arif",
            session_id="sess-123",
        )
        # Token format: header.claims.signature
        parts = result.token.split(".")
        assert len(parts) == 3
        assert all(parts)  # All parts should be non-empty


class TestValidateGovernanceToken:
    """Test token validation functionality."""

    def test_validate_valid_token(self):
        """Should validate a correctly minted token."""
        # First mint a token
        mint_result = mint_governance_token(
            actor_id="arif",
            session_id="sess-123",
        )
        assert mint_result.valid is True

        # Then validate it
        validation = validate_governance_token(
            token=mint_result.token,
            expected_session_id="sess-123",
        )
        assert validation.valid is True
        assert validation.session_id == "sess-123"
        assert validation.actor_id == "arif"

    def test_validate_wrong_session(self):
        """Should reject token with wrong session ID."""
        mint_result = mint_governance_token(
            actor_id="arif",
            session_id="sess-123",
        )
        validation = validate_governance_token(
            token=mint_result.token,
            expected_session_id="sess-456",  # Wrong session
        )
        assert validation.valid is False
        assert "F11_SESSION_MISMATCH" in validation.error

    def test_validate_malformed_token(self):
        """Should reject malformed tokens."""
        validation = validate_governance_token(
            token="invalid-token",
            expected_session_id="sess-123",
        )
        assert validation.valid is False
        assert "F11_TOKEN_MALFORMED" in validation.error

    def test_validate_tampered_token(self):
        """Should reject tampered tokens."""
        mint_result = mint_governance_token(
            actor_id="arif",
            session_id="sess-123",
        )
        # Tamper with the token
        tampered = mint_result.token[:-10] + "TAMPERED!!"
        validation = validate_governance_token(
            token=tampered,
            expected_session_id="sess-123",
        )
        assert validation.valid is False
        assert "F11_TOKEN_INVALID" in validation.error

    def test_validate_with_open_mode_bypass(self):
        """Should bypass validation when OPEN_MODE is enabled."""
        with patch("core.security.tokens.OPEN_MODE", True):
            validation = validate_governance_token(
                token="any.token.here",  # Invalid token
                expected_session_id="sess-123",
            )
            assert validation.valid is True
            assert validation.actor_id == "arif"
            assert validation.clearance == "sovereign"


class TestHashGovernanceToken:
    """Test token hashing functionality."""

    def test_hash_produces_string(self):
        """Hash should produce a string."""
        token = "test.token.signature"
        hash_result = hash_governance_token(token)
        assert isinstance(hash_result, str)
        assert len(hash_result) == 64  # SHA-256 hex is 64 chars

    def test_hash_is_deterministic(self):
        """Same token should produce same hash."""
        token = "test.token.signature"
        hash1 = hash_governance_token(token)
        hash2 = hash_governance_token(token)
        assert hash1 == hash2

    def test_hash_is_unique(self):
        """Different tokens should produce different hashes."""
        hash1 = hash_governance_token("token1.here.sig")
        hash2 = hash_governance_token("token2.here.sig")
        assert hash1 != hash2


class TestSemanticBypass:
    """Test the semantic bypass functionality."""

    def test_arif_in_semantic_bypass(self):
        """'arif' should be in semantic bypass actors."""
        assert "arif" in SEMANTIC_BYPASS_ACTORS

    def test_sovereign_in_semantic_bypass(self):
        """'sovereign' should be in semantic bypass actors."""
        assert "sovereign" in SEMANTIC_BYPASS_ACTORS

    def test_arif_gets_sovereign_clearance(self):
        """'arif' actor should get sovereign clearance."""
        result = mint_governance_token(
            actor_id="arif",
            session_id="sess-123",
        )
        assert result.valid is True
        assert result.clearance == "sovereign"


class TestOpenModeConfiguration:
    """Test the open mode configuration."""

    def test_open_mode_respects_env_var(self):
        """OPEN_MODE should be configurable via environment variable."""
        # Test with true values
        for value in ["true", "TRUE", "1", "yes", "on"]:
            with patch.dict(os.environ, {"ARIFOS_OPEN_MODE": value}):
                # Need to reimport to pick up new env var
                import importlib
                from core.security import tokens

                importlib.reload(tokens)
                assert tokens.OPEN_MODE is True

        # Test with false values
        for value in ["false", "FALSE", "0", "no", "", "off"]:
            with patch.dict(os.environ, {"ARIFOS_OPEN_MODE": value}):
                import importlib
                from core.security import tokens

                importlib.reload(tokens)
                assert tokens.OPEN_MODE is False


class TestIntegration:
    """Integration tests for full token lifecycle."""

    def test_full_token_lifecycle(self):
        """Test complete mint -> validate -> hash lifecycle."""
        # Mint
        mint_result = mint_governance_token(
            actor_id="arif",
            session_id="integration-test",
        )
        assert mint_result.valid is True

        # Validate
        validation = validate_governance_token(
            token=mint_result.token,
            expected_session_id="integration-test",
        )
        assert validation.valid is True
        assert validation.actor_id == "arif"

        # Hash
        token_hash = hash_governance_token(mint_result.token)
        assert len(token_hash) == 64

    def test_arif_workflow(self):
        """Test the 'arif' semantic bypass workflow."""
        # As 'arif', I should be able to mint tokens without whitelist
        with patch("core.security.tokens.BOOTSTRAP_ACTORS", set()):
            mint_result = mint_governance_token(
                actor_id="arif",
                session_id="arif-session",
            )
            assert mint_result.valid is True
            assert mint_result.clearance == "sovereign"

            # Validate the token
            validation = validate_governance_token(
                token=mint_result.token,
                expected_session_id="arif-session",
            )
            assert validation.valid is True
            assert validation.actor_id == "arif"
            assert validation.clearance == "sovereign"


class TestNonceContinuity:
    """Test token nonce continuity between tools and sessions."""

    def setup_method(self):
        """Clear nonce registry before each test."""
        clear_nonce_registry()

    def teardown_method(self):
        """Clear nonce registry after each test."""
        clear_nonce_registry()

    def test_auto_generated_nonce(self):
        """Tokens should auto-generate nonces when not provided."""
        result = mint_governance_token(
            actor_id="arif",
            session_id="test-session",
        )
        assert result.valid is True

        # Extract nonce from token
        validation = validate_governance_token(
            token=result.token,
            expected_session_id="test-session",
        )
        assert validation.valid is True
        assert validation.nonce != ""
        assert len(validation.nonce) == 32  # 32 hex chars

    def test_custom_nonce_preserved(self):
        """Custom nonces should be preserved in token."""
        custom_nonce = "my-custom-nonce-1234567890abcdef"
        result = mint_governance_token(
            actor_id="arif",
            session_id="test-session",
            auth_nonce=custom_nonce,
        )
        assert result.valid is True

        validation = validate_governance_token(
            token=result.token,
            expected_session_id="test-session",
        )
        assert validation.valid is True
        # Nonce is truncated to 32 chars in the token
        assert validation.nonce == custom_nonce[:32]

    def test_nonce_replay_detection(self):
        """Same nonce should not be reusable in same session."""
        nonce = "unique-nonce-1234567890abcdef"

        # First use should succeed
        result1 = mint_governance_token(
            actor_id="arif",
            session_id="test-session",
            auth_nonce=nonce,
        )
        assert result1.valid is True

        # Second use of same nonce should fail
        result2 = mint_governance_token(
            actor_id="arif",
            session_id="test-session",
            auth_nonce=nonce,
        )
        assert result2.valid is False
        assert "F11_NONCE_REPLAY" in result2.error

    def test_nonce_continuity_across_tools(self):
        """Nonces should track continuity across multiple tools in same session."""
        session_id = "continuity-test-session"

        # Tool 1 mints token
        token1 = mint_governance_token(
            actor_id="arif",
            session_id=session_id,
        )
        assert token1.valid is True

        # Tool 2 mints another token with different nonce
        token2 = mint_governance_token(
            actor_id="arif",
            session_id=session_id,
        )
        assert token2.valid is True

        # Both should have different nonces
        val1 = validate_governance_token(token1.token, session_id)
        val2 = validate_governance_token(token2.token, session_id)

        assert val1.nonce != val2.nonce
        assert val1.valid is True
        assert val2.valid is True

    def test_same_nonce_different_sessions_allowed(self):
        """Same nonce can be used in different sessions."""
        nonce = "shared-nonce-1234567890abcdef"

        # Use in session 1
        result1 = mint_governance_token(
            actor_id="arif",
            session_id="session-1",
            auth_nonce=nonce,
        )
        assert result1.valid is True

        # Use in session 2 (should succeed - different session)
        result2 = mint_governance_token(
            actor_id="arif",
            session_id="session-2",
            auth_nonce=nonce,
        )
        assert result2.valid is True

    def test_validation_returns_nonce(self):
        """Validation should return the nonce for continuity tracking."""
        result = mint_governance_token(
            actor_id="arif",
            session_id="test-session",
        )

        validation = validate_governance_token(
            token=result.token,
            expected_session_id="test-session",
        )

        assert validation.nonce is not None
        assert len(validation.nonce) > 0

    def test_open_mode_allows_any_actor(self):
        """In open mode, any actor can mint tokens."""
        with patch("core.security.tokens.OPEN_MODE", True):
            with patch("core.security.tokens.BOOTSTRAP_ACTORS", {"otheruser"}):
                # Random actor should succeed in open mode
                result = mint_governance_token(
                    actor_id="randomuser",
                    session_id="test-session",
                )
                assert result.valid is True
                assert result.actor_id == "randomuser"

    def test_nonce_truncation(self):
        """Long nonces should be truncated to 32 chars."""
        long_nonce = "a" * 100
        result = mint_governance_token(
            actor_id="arif",
            session_id="test-session",
            auth_nonce=long_nonce,
        )
        assert result.valid is True

        validation = validate_governance_token(
            token=result.token,
            expected_session_id="test-session",
        )
        assert len(validation.nonce) == 32
        assert validation.nonce == "a" * 32

    def test_clear_nonce_registry(self):
        """Clearing registry should reset nonce tracking."""
        nonce = "reset-test-nonce-1234567890ab"
        session = "reset-session"

        # Use nonce
        result1 = mint_governance_token(
            actor_id="arif",
            session_id=session,
            auth_nonce=nonce,
        )
        assert result1.valid is True

        # Try to reuse (should fail)
        result2 = mint_governance_token(
            actor_id="arif",
            session_id=session,
            auth_nonce=nonce,
        )
        assert result2.valid is False

        # Clear registry
        clear_nonce_registry(session)

        # Now should succeed
        result3 = mint_governance_token(
            actor_id="arif",
            session_id=session,
            auth_nonce=nonce,
        )
        assert result3.valid is True

    def test_session_isolation(self):
        """Nonce tracking should be isolated per session."""
        nonce = "isolated-nonce-1234567890abc"

        # Use in session A
        result_a = mint_governance_token(
            actor_id="arif",
            session_id="session-A",
            auth_nonce=nonce,
        )
        assert result_a.valid is True

        # Use in session B (should work)
        result_b = mint_governance_token(
            actor_id="arif",
            session_id="session-B",
            auth_nonce=nonce,
        )
        assert result_b.valid is True

        # Try again in session A (should fail)
        result_a2 = mint_governance_token(
            actor_id="arif",
            session_id="session-A",
            auth_nonce=nonce,
        )
        assert result_a2.valid is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
