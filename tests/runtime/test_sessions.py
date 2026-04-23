"""
tests/runtime/test_sessions.py — Session Management Tests

Tests for runtime/sessions.py — identity binding and session continuity
"""

import pytest
from unittest.mock import Mock, patch


class TestSessionNormalization:
    """Test _normalize_session_id function."""

    def test_normalize_with_valid_session(self):
        """Test normalizing a valid session ID."""
        from arifosmcp.runtime.sessions import _normalize_session_id

        result = _normalize_session_id("test-session-123")
        assert result == "test-session-123"

    def test_normalize_with_none_creates_new(self):
        """Test that None creates a new session ID."""
        from arifosmcp.runtime.sessions import _normalize_session_id

        result = _normalize_session_id(None)
        assert result.startswith("session-")
        assert len(result) == 16  # "session-" + 8 hex chars

    def test_normalize_with_empty_string_creates_new(self):
        """Test that empty string creates a new session ID."""
        from arifosmcp.runtime.sessions import _normalize_session_id

        result = _normalize_session_id("")
        assert result.startswith("session-")


class TestSessionIdentityBinding:
    """Test session identity binding functions."""

    def test_bind_and_get_identity(self):
        """Test binding and retrieving session identity."""
        from arifosmcp.runtime.sessions import bind_session_identity, get_session_identity

        # Bind identity with explicit verified actor_id
        bind_session_identity(
            session_id="test-bind-001",
            actor_id="ariffazil",
            authority_level="sovereign",
            auth_context={"verified": True},
            human_approval=True,
        )

        # Retrieve identity
        identity = get_session_identity("test-bind-001")
        assert identity is not None
        assert identity["actor_id"] == "ariffazil"  # Explicit verified identity
        assert identity["authority_level"] == "sovereign"
        assert identity["human_approval"] is True

    def test_get_identity_nonexistent(self):
        """Test getting identity for non-existent session."""
        from arifosmcp.runtime.sessions import get_session_identity

        identity = get_session_identity("nonexistent-session-xyz")
        assert identity is None

    def test_clear_session_identity(self):
        """Test clearing session identity."""
        from arifosmcp.runtime.sessions import (
            bind_session_identity,
            get_session_identity,
            clear_session_identity,
        )

        # Bind and verify
        bind_session_identity(
            session_id="test-clear-001",
            actor_id="test-user",
            authority_level="user",
            auth_context={},
        )
        assert get_session_identity("test-clear-001") is not None

        # Clear and verify
        clear_session_identity("test-clear-001")
        assert get_session_identity("test-clear-001") is None


class TestActiveSession:
    """Test active session management."""

    def test_set_and_resolve_active_session(self):
        """Test setting and resolving active session."""
        from arifosmcp.runtime.sessions import set_active_session, _resolve_session_id

        # Set active session
        set_active_session("active-session-001")

        # Resolve with None should return active session
        result = _resolve_session_id(None)
        assert result == "active-session-001"

    def test_resolve_session_with_provided_id(self):
        """Test resolving with provided ID takes precedence."""
        from arifosmcp.runtime.sessions import set_active_session, _resolve_session_id

        set_active_session("active-session")
        result = _resolve_session_id("provided-session")

        # Provided ID takes precedence
        assert result == "provided-session"


class TestRuntimeContext:
    """Test runtime context resolution."""

    def test_resolve_runtime_context_anonymous(self):
        """Test context resolution for anonymous user."""
        from arifosmcp.runtime.sessions import resolve_runtime_context

        context = resolve_runtime_context(
            incoming_session_id=None, auth_context=None, actor_id=None, declared_name=None
        )

        assert context["canonical_actor_id"] == "anonymous"
        assert context["transport_session_id"] == "global"

    def test_resolve_runtime_context_with_actor(self):
        """Test context resolution with verified actor ID."""
        from arifosmcp.runtime.sessions import resolve_runtime_context

        context = resolve_runtime_context(
            incoming_session_id="session-123",
            auth_context=None,
            actor_id="ariffazil",
            declared_name="Arif Fazil",
        )

        # Explicit verified identity preserved
        assert context["canonical_actor_id"] == "ariffazil"
        assert context["display_name"] == "Arif Fazil"

    def test_resolve_runtime_context_invalid_actor(self):
        """Test context resolution with invalid/malformed actor_id is rejected."""
        from arifosmcp.runtime.sessions import resolve_runtime_context

        # Malformed actor_id (contains special chars) should be rejected
        context = resolve_runtime_context(
            incoming_session_id="session-123",
            auth_context=None,
            actor_id="arif<script>alert(1)</script>",
            declared_name=None,
        )

        # Invalid actor should fall back to anonymous
        assert context["canonical_actor_id"] == "anonymous"


class TestSessionCounting:
    """Test session counting functionality."""

    def test_list_active_sessions_count(self):
        """Test counting active sessions."""
        from arifosmcp.runtime.sessions import (
            bind_session_identity,
            list_active_sessions_count,
            clear_session_identity,
        )

        # Get initial count
        initial_count = list_active_sessions_count()

        # Bind a new session
        bind_session_identity(
            session_id="count-test-001", actor_id="test", authority_level="user", auth_context={}
        )

        # Count should increase
        new_count = list_active_sessions_count()
        assert new_count == initial_count + 1

        # Cleanup
        clear_session_identity("count-test-001")


class TestIdentityMismatchCases:
    """Zero-Day hardening mismatch test cases per external validator amendments."""

    def test_resolve_canonical_actor_guessable_alias_rejected(self):
        """Test that guessable alias 'arif' is NOT promoted to ariffazil."""
        from arifosmcp.runtime.sessions import _resolve_canonical_actor

        # "arif" is NOT in the sovereign identity map and should not be promoted
        result = _resolve_canonical_actor("arif", None)
        assert result == "arif"  # Preserved as-is, not promoted

    def test_resolve_canonical_actor_explicit_verified(self):
        """Test that explicit verified ariffazil is recognized."""
        from arifosmcp.runtime.sessions import _resolve_canonical_actor

        result = _resolve_canonical_actor("ariffazil", None)
        assert result == "ariffazil"

    def test_resolve_canonical_actor_malformed_rejected(self):
        """Test that malformed actor_id is rejected."""
        from arifosmcp.runtime.sessions import _resolve_canonical_actor

        # Script injection attempt should be rejected
        result = _resolve_canonical_actor("<script>alert(1)</script>", None)
        assert result == "anonymous"

        # Path traversal attempt should be rejected
        result = _resolve_canonical_actor("../../../etc/passwd", None)
        assert result == "anonymous"

    def test_resolve_runtime_context_token_overrides_transport(self):
        """Test that verified token identity outranks transport-provided actor."""
        from arifosmcp.runtime.sessions import resolve_runtime_context

        # auth_context has verified session, transport has different actor
        context = resolve_runtime_context(
            incoming_session_id="transport-session",
            auth_context={"session_id": "verified-token-session"},
            actor_id="untrusted-actor",
            declared_name=None,
        )

        # Token should win
        assert context["session_id"] == "verified-token-session"
        assert context["authority_source"] == "token"

    def test_resolve_runtime_context_stale_session_with_valid_token(self):
        """Test stale session_id + valid token uses token."""
        from arifosmcp.runtime.sessions import resolve_runtime_context

        context = resolve_runtime_context(
            incoming_session_id="stale-session-xyz",
            auth_context={"session_id": "fresh-valid-token"},
            actor_id="some-actor",
            declared_name=None,
        )

        # Token identity should win over stale transport session
        assert context["session_id"] == "fresh-valid-token"
        assert context["authority_source"] == "token"

    def test_resolve_runtime_context_anonymous_transport_no_session(self):
        """Test anonymous transport without session gets anonymous identity."""
        from arifosmcp.runtime.sessions import resolve_runtime_context

        context = resolve_runtime_context(
            incoming_session_id=None,
            auth_context=None,
            actor_id=None,
            declared_name=None,
        )

        assert context["canonical_actor_id"] == "anonymous"
        assert context["transport_session_id"] == "global"
        assert context["authority_source"] == "fallback"
