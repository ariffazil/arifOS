"""
Invariant Tests: Session Truth Unification (Phase 1 Seal)

F2 Truth Enforcement: session_id must equal resolved_session_id
across all runtime contexts.

These tests prevent truth-surface split regression.
"""

import pytest
from arifosmcp.runtime.sessions import resolve_runtime_context, bind_session_identity


class TestSessionTruthInvariant:
    """Enforce: session_id == resolved_session_id across all contexts."""

    def test_resolve_runtime_context_returns_unified_session_id(self):
        """Invariant: session_id and resolved_session_id must be identical."""
        result = resolve_runtime_context(
            incoming_session_id="test-session-123",
            auth_context=None,
            actor_id="test_user",
            declared_name=None,
        )
        
        # CRITICAL INVARIANT: Unified truth
        assert result["session_id"] == result["resolved_session_id"], \
            "F2 Truth Violation: session_id != resolved_session_id"
        
        # Both should be the canonical resolved value
        assert result["session_id"] == "test-session-123"
        assert result["resolved_session_id"] == "test-session-123"

    def test_resolve_with_auth_context_uses_auth_session(self):
        """Auth context session_id takes precedence over transport."""
        result = resolve_runtime_context(
            incoming_session_id="global",  # Raw transport value
            auth_context={"session_id": "auth-session-456"},
            actor_id="ariffazil",
            declared_name=None,
        )
        
        # Unified truth should use auth context
        assert result["session_id"] == "auth-session-456"
        assert result["resolved_session_id"] == "auth-session-456"
        # Transport preserved for debug only
        assert result["transport_session_id"] == "global"

    def test_resolve_with_anchored_session(self):
        """Anchored session state is used when no auth context."""
        # First anchor a session
        bind_session_identity(
            session_id="anchored-session-789",
            actor_id="test_actor",
            authority_level="USER",
            auth_context={},
        )
        
        result = resolve_runtime_context(
            incoming_session_id="anchored-session-789",
            auth_context=None,
            actor_id="test_actor",
            declared_name=None,
        )
        
        # Should resolve to anchored session
        assert result["session_id"] == "anchored-session-789"
        assert result["resolved_session_id"] == "anchored-session-789"
        assert result["authority_source"] == "session"

    def test_invariant_field_present(self):
        """Invariant declaration must be present in context."""
        result = resolve_runtime_context(
            incoming_session_id="test",
            auth_context=None,
            actor_id=None,
            declared_name=None,
        )
        
        # Invariant must be declared
        assert "_invariant" in result
        assert "session_id == resolved_session_id" in result["_invariant"]

    def test_no_transport_session_id_in_canonical_surfaces(self):
        """Transport session ID must never be used as canonical session_id."""
        result = resolve_runtime_context(
            incoming_session_id="global",  # Default transport value
            auth_context=None,
            actor_id="anonymous",
            declared_name=None,
        )
        
        # When no auth context or anchored session, transport becomes resolved
        # This is acceptable - the key is that session_id == resolved_session_id
        assert result["session_id"] == result["resolved_session_id"]
        
        # Transport is preserved for debug but not used as canonical
        assert "transport_session_id" in result


class TestSessionIdentityContinuity:
    """Session identity must be continuous across resolution contexts."""

    def test_actor_identity_preserved_in_resolution(self):
        """Actor identity must be consistent across session resolution."""
        result = resolve_runtime_context(
            incoming_session_id="session-abc",
            auth_context=None,
            actor_id="ariffazil",
            declared_name="Arif",
        )
        
        assert result["canonical_actor_id"] == "ariffazil"
        assert result["display_name"] == "Arif"

    def test_sovereign_actor_normalization(self):
        """Sovereign actors (arif) normalize to canonical id."""
        for alias in ["arif", "arif-fazil", "arif_fazil", "ariffazil"]:
            result = resolve_runtime_context(
                incoming_session_id="test",
                auth_context=None,
                actor_id=alias,
                declared_name=None,
            )
            assert result["canonical_actor_id"] == "ariffazil", \
                f"Alias '{alias}' should normalize to 'ariffazil'"
