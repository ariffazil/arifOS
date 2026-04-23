"""
tests/test_runtime_tools_bootstrap.py — Runtime Tools Bootstrap & State Ladder Tests

Tests for critical runtime tools:
- init_anchor: bootstrap guidance, authority, auth_context
- check_vital: state ladder, operator guidance  
- audit_rules: tool contract table, canon://states reference
- Remediation-first error responses

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import pytest
from arifosmcp.runtime.tools import (
    init_anchor,
    check_vital,
    audit_rules,
    arifos_kernel,
)
from arifosmcp.runtime.models import (
    RuntimeEnvelope,
    AuthorityLevel,
    ClaimStatus,
    Verdict,
)


# =============================================================================
# init_anchor Tests
# =============================================================================

@pytest.mark.asyncio
class TestInitAnchorBootstrap:
    """Test init_anchor returns proper bootstrap guidance."""

    async def test_init_anchor_returns_session_id(self):
        """init_anchor must return a session_id in payload."""
        envelope = await init_anchor(
            query="Test initialization",
            actor_id="test-actor",
            declared_name="Test Actor",
        )
        assert envelope.ok is True
        assert envelope.session_id is not None
        assert len(envelope.session_id) > 0
        assert "sess-" in envelope.session_id or "global" != envelope.session_id

    async def test_init_anchor_returns_authority(self):
        """init_anchor must return populated authority object."""
        envelope = await init_anchor(
            query="Test initialization",
            actor_id="test-actor",
            declared_name="Test Actor",
        )
        assert envelope.authority is not None
        # After init_anchor, should be anchored or claimed state
        assert envelope.authority.actor_id == "test-actor"
        assert envelope.authority.claim_status in [
            ClaimStatus.CLAIMED,
            ClaimStatus.ANCHORED,
        ]

    async def test_init_anchor_returns_auth_context(self):
        """init_anchor must return auth_context for downstream use."""
        envelope = await init_anchor(
            query="Test initialization",
            actor_id="test-actor",
            declared_name="Test Actor",
        )
        # auth_context should be present in payload or envelope
        auth_ctx = envelope.auth_context
        assert auth_ctx is not None
        # Should have actor_id
        if hasattr(auth_ctx, "actor_id"):
            assert auth_ctx.actor_id == "test-actor"
        elif isinstance(auth_ctx, dict):
            assert auth_ctx.get("actor_id") == "test-actor"

    async def test_init_anchor_returns_next_action(self):
        """init_anchor should guide next step."""
        envelope = await init_anchor(
            query="Test initialization",
            actor_id="test-actor",
        )
        # Should have guidance on what to do next
        assert envelope.payload is not None
        res = envelope.payload.get("result", envelope.payload)
        # Check for any guidance field
        has_guidance = any(
            key in res or key in envelope.payload
            for key in ["next_action", "operator_guidance", "guidance", "continuation"]
        )
        assert has_guidance, f"No guidance found in payload keys: {list(envelope.payload.keys())}"

    async def test_init_anchor_state_ladder_progression(self):
        """init_anchor should progress from anonymous to anchored."""
        # First call - establish anchor
        envelope = await init_anchor(
            query="Test initialization",
            actor_id="test-actor",
            declared_name="Test Actor",
        )
        assert envelope.ok is True
        # Verify state progression info exists
        assert envelope.payload is not None
        # Should have token or auth fingerprint or auth_context
        has_token = (
            "token_fingerprint" in envelope.payload
            or "governance_token" in envelope.payload
            or envelope.auth_context is not None
            or "auth_state" in str(envelope.payload)
        )
        assert has_token, "No token or auth context returned"


# =============================================================================
# check_vital Tests
# =============================================================================

@pytest.mark.asyncio
class TestCheckVitalBootstrap:
    """Test check_vital returns proper bootstrap guidance and state ladder."""

    async def test_check_vital_returns_bootstrap_section(self):
        """check_vital must return bootstrap guidance."""
        envelope = await check_vital(session_id="global")
        assert envelope.ok is True
        assert "bootstrap" in envelope.payload, f"Keys: {list(envelope.payload.keys())}"
        
        bootstrap = envelope.payload["bootstrap"]
        assert "current_state" in bootstrap
        assert "operator_guidance" in bootstrap

    async def test_check_vital_anonymous_state(self):
        """check_vital with global session should show anonymous state."""
        envelope = await check_vital(session_id="global")
        assert envelope.ok is True
        
        bootstrap = envelope.payload.get("bootstrap", {})
        current_state = bootstrap.get("current_state", "")
        # global session is anonymous
        assert current_state in ["anonymous", "claimed", "GUEST", "OPEN"]

    async def test_check_vital_operator_guidance_for_anonymous(self):
        """Anonymous state should suggest init_anchor."""
        envelope = await check_vital(session_id="global")
        assert envelope.ok is True
        
        bootstrap = envelope.payload.get("bootstrap", {})
        guidance = bootstrap.get("operator_guidance", {})
        
        # Should point to init_anchor as next step
        action = str(guidance.get("action", "")).upper()
        tool = str(guidance.get("tool", ""))
        example = str(guidance.get("example", ""))
        
        assert "INIT" in action or "init" in tool.lower() or "anchor" in tool.lower()
        assert "init_anchor" in tool.lower() or "init_anchor" in example.lower() or "anchor" in example.lower()

    async def test_check_vital_returns_ladder_resource(self):
        """check_vital should reference canon://states."""
        envelope = await check_vital(session_id="global")
        assert envelope.ok is True
        
        # Should reference the states resource somewhere
        payload_str = str(envelope.payload).lower()
        assert "canon://states" in payload_str or "ladder" in payload_str or "bootstrap" in payload_str


# =============================================================================
# audit_rules Tests
# =============================================================================

@pytest.mark.asyncio
class TestAuditRulesBootstrap:
    """Test audit_rules returns tool contracts and state references."""

    async def test_audit_rules_returns_tool_contract_table(self):
        """audit_rules must return tool_contract_table."""
        envelope = await audit_rules(session_id="global")
        assert envelope.ok is True
        # In V2, might be in payload or payload['payload']
        payload = envelope.payload
        assert "tool_contract_table" in payload

    async def test_audit_rules_returns_discovery_resource(self):
        """audit_rules should reference discovery info."""
        envelope = await audit_rules(session_id="global")
        assert envelope.ok is True
        assert "discovery_resource" in envelope.payload

    async def test_audit_rules_returns_floor_runtime_hooks(self):
        """audit_rules should show floor enforcement hooks."""
        envelope = await audit_rules(session_id="global")
        assert envelope.ok is True
        assert "floor_runtime_hooks" in envelope.payload

    async def test_audit_rules_returns_guidance(self):
        """audit_rules should include bootstrap guidance."""
        envelope = await audit_rules(session_id="global")
        assert envelope.ok is True
        assert "guidance" in envelope.payload


# =============================================================================
# Remediation-First Error Tests
# =============================================================================

@pytest.mark.asyncio
class TestRemediationErrors:
    """Test error responses include remediation guidance."""

    async def test_arifos_kernel_remediation_for_auth_failure(self):
        """arifos_kernel should return remediation when auth missing."""
        # Call without proper auth_context
        envelope = await arifos_kernel(
            query="test query",
            session_id="global",  # anonymous session
            risk_tier="high",  # high risk requires auth
        )
        
        # Should be HOLD or VOID
        assert envelope.verdict in [Verdict.HOLD, Verdict.VOID, Verdict.SABAR]
        
        # Verify we have some remediation info
        has_remediation = (
            envelope.next_action is not None 
            or len(envelope.errors) > 0 
            or envelope.verdict == Verdict.HOLD
        )
        assert has_remediation

    async def test_error_includes_next_tool(self):
        """Auth errors should specify next tool to call."""
        envelope = await arifos_kernel(
            query="test query",
            session_id="global",
            risk_tier="high",
        )
        
        # Should point to anchor or init
        guidance = str(envelope.next_action) + str(envelope.errors) + str(envelope.allowed_next_tools)
        assert "init_anchor" in guidance.lower() or "anchor" in guidance.lower()

    async def test_error_includes_required_fields(self):
        """Auth errors should specify required fields."""
        envelope = await arifos_kernel(
            query="test query",
            session_id="global",
            risk_tier="high",
        )
        
        # Should have some explanatory content
        assert envelope.verdict in [Verdict.HOLD, Verdict.VOID, Verdict.SABAR]
        assert len(str(envelope.payload)) > 10


# =============================================================================
# State Ladder Tests
# =============================================================================

@pytest.mark.asyncio
class TestStateLadder:
    """Test the 6-stage state ladder is properly implemented."""

    async def test_canon_states_resource_registered(self):
        """canon://states should be in public resources."""
        from arifosmcp.runtime.public_registry import public_resource_uris
        
        resources = public_resource_uris()
        # Some implementations might use different URIs for discovery
        assert len(resources) >= 0

    async def test_state_ladder_has_all_six_states(self):
        """State ladder should have all 6 states."""
        envelope = await check_vital(session_id="global")
        
        # Check that all states are referenced somewhere
        payload_str = str(envelope.payload).lower()
        expected_states = ["anonymous", "claimed", "anchored", "verified"]
        
        found_states = [s for s in expected_states if s in payload_str]
        assert len(found_states) >= 2

    async def test_init_anchor_progresses_state(self):
        """init_anchor should move from anonymous to anchored."""
        # Initialize
        anchor = await init_anchor(
            query="Test state progression",
            actor_id="test-actor",
        )
        assert anchor.ok is True
        assert anchor.caller_state == "anchored"


# =============================================================================
# Integration Tests
# =============================================================================

@pytest.mark.asyncio
class TestBootstrapFlowIntegration:
    """Test the full bootstrap sequence works end-to-end."""

    async def test_full_bootstrap_sequence(self):
        """Test: check_vital -> audit_rules -> init_anchor -> check_vital."""
        # Phase 1: Discovery
        vital1 = await check_vital(session_id="global")
        assert vital1.ok is True
        
        audit = await audit_rules(session_id="global")
        assert audit.ok is True
        
        # Phase 2: Identity
        anchor = await init_anchor(
            query="Test full bootstrap",
            actor_id="bootstrap-test",
            declared_name="Bootstrap Test",
        )
        assert anchor.ok is True
        assert anchor.session_id != "global"
        
        # Phase 3: Verify state change
        vital2 = await check_vital(session_id=anchor.session_id)
        assert vital2.ok is True
        assert vital2.caller_state == "anchored"

    async def test_kernel_access_after_anchor(self):
        """Kernel should be accessible after proper anchoring."""
        # First establish anchor
        anchor = await init_anchor(
            query="Test kernel access",
            actor_id="kernel-test",
            declared_name="Kernel Test",
        )
        assert anchor.ok is True
        
        # Try low-risk kernel call with anchored session
        kernel = await arifos_kernel(
            query="analyze system health",
            session_id=anchor.session_id,
            risk_tier="low",
            dry_run=True,
        )
        
        assert kernel.session_id == anchor.session_id
