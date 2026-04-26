"""
test_invariants_session.py — Session Continuity Invariants

F2 Truth: Session truth must be consistent across all surfaces.
"""
import pytest
import asyncio
from arifosmcp.runtime.tools import init_anchor
from arifosmcp.runtime.sessions import (
    resolve_runtime_context,
    bind_session_identity,
    get_session_identity,
    clear_session_identity,
)


class TestSessionTruthSurfaceInvariant:
    """Invariant: All status surfaces report same resolved_session_id"""

    @pytest.mark.asyncio
    async def test_init_anchor_session_truth(self):
        """init_anchor must expose transport + resolved session"""
        envelope = await init_anchor(
            actor_id='arif',
            intent='test session truth',
            session_id='truth-test-001'
        )
        
        result = envelope.payload
        # All truth fields must be present
        assert "transport_session_id" in result, "Missing transport_session_id"
        assert "resolved_session_id" in result, "Missing resolved_session_id"
        assert "session_id" in result, "Missing session_id (backward compat)"
        
        # session_id must equal resolved_session_id (backward compat = truth)
        assert result["session_id"] == result["resolved_session_id"], \
            "session_id must alias resolved_session_id"
        
        # auth_context must carry resolved truth
        assert envelope.auth_context is not None, "Missing auth_context"
        assert envelope.auth_context.session_id == result["resolved_session_id"], \
            "auth_context.session_id must equal resolved_session_id"

    @pytest.mark.asyncio
    async def test_get_caller_status_session_consistency(self):
        """get_caller_status must report same session as init_anchor"""
        session_id = "consistency-test-002"
        
        # Anchor first
        anchored_env = await init_anchor(
            actor_id='ariffazil',
            intent='test consistency',
            session_id=session_id
        )
        anchored = anchored_env.payload["result"]
        
        # Query status
        status_env = await init_anchor(mode="status",session_id=session_id)
        status = status_env.payload
        
        # Session truth must be identical
        assert status["resolved_session_id"] == anchored["resolved_session_id"], \
            "Status must report same resolved session as anchor"
        # Use envelope authority for comparison
        assert status_env.authority.actor_id.lower() == anchored_env.authority.actor_id.lower(), \
            "Status must report same actor as anchor"


class TestGlobalSessionIsolationInvariant:
    """Invariant: 'global' session is always anonymous, never inherits anchored state"""

    @pytest.mark.asyncio
    async def test_global_never_anchored(self):
        """global session must report anonymous even after other sessions anchor"""
        # Anchor a different session
        await init_anchor(
            actor_id='arif',
            intent='test global isolation',
            session_id='other-session-003'
        )
        
        # global session should still be anonymous
        global_status = await init_anchor(mode="status",session_id='global')
        assert global_status.caller_state == 'anonymous', \
            "global session must remain anonymous"
        assert global_status.authority.actor_id == 'anonymous', \
            "global session authority must be anonymous"
        # global should NOT have kernel access
        assert 'arifos_kernel' not in global_status.allowed_next_tools, \
            "global session must be blocked from kernel"

    def test_global_in_resolution_context(self):
        """resolve_runtime_context must handle global correctly"""
        ctx = resolve_runtime_context(
            incoming_session_id="global",
            auth_context=None,
            actor_id="anonymous",
            declared_name=None,
        )
        assert ctx["transport_session_id"] == "global", "Transport should be global"
        assert ctx["authority_source"] == "fallback", "Should be fallback source"


class TestSessionPrecedenceInvariant:
    """Invariant: auth_context.session_id > anchored state > request > global"""

    def test_auth_context_takes_precedence(self):
        """Verified auth_context.session_id wins over transport"""
        ctx = resolve_runtime_context(
            incoming_session_id="global",  # Transport is global
            auth_context={"session_id": "verified-session-004"},  # But auth says otherwise
            actor_id="arif",
            declared_name=None,
        )
        assert ctx["resolved_session_id"] == "verified-session-004", \
            "auth_context.session_id must override transport"
        assert ctx["authority_source"] == "token", \
            "Must indicate token-based authority"

    def test_anchored_state_fallback(self):
        """Anchored state used when no auth_context"""
        session_id = "anchored-fallback-005"
        bind_session_identity(
            session_id=session_id,
            actor_id="ariffazil",
            authority_level="sovereign",
            auth_context={"actor_id": "ariffazil"},
        )
        
        ctx = resolve_runtime_context(
            incoming_session_id=session_id,
            auth_context=None,  # No auth context
            actor_id="arif",
            declared_name=None,
        )
        assert ctx["resolved_session_id"] == session_id, \
            "Should use anchored session when no auth_context"
        assert ctx["authority_source"] == "session", \
            "Must indicate session-based authority"


class TestNoGlobalLeakInvariant:
    """Invariant: Anchored sessions never report session_id as 'global'"""

    @pytest.mark.asyncio
    async def test_no_global_in_anchored_output(self):
        """Once anchored, session_id must never be 'global'"""
        session_id = "no-global-006"
        
        result = await init_anchor(
            actor_id='arif',
            intent='test no global leak',
            session_id=session_id
        )
        
        # All session surfaces must be actual session, not global
        assert result.session_id != "global", "envelope.session_id must not be global"
        assert result.payload["result"]["session_id"] != "global", "payload.session_id must not be global"
        assert result.payload["result"]["resolved_session_id"] != "global", "resolved_session_id must not be global"
        if result.auth_context:
            assert result.auth_context.session_id != "global", "auth_context.session_id must not be global"


class TestSessionIdentityBindingInvariant:
    """Invariant: Session + Identity are bound together atomically"""

    def test_session_maps_to_actor(self):
        """Session lookup returns correct actor"""
        session_id = "binding-test-007"
        bind_session_identity(
            session_id=session_id,
            actor_id="ariffazil",
            authority_level="sovereign",
            auth_context={"actor_id": "ariffazil"},
        )
        
        stored = get_session_identity(session_id)
        assert stored is not None
        assert stored["actor_id"] == "ariffazil"
        
        clear_session_identity(session_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
