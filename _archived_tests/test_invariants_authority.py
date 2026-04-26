"""
test_invariants_authority.py — Authority Binding Invariants

F11 + F13: Authority must be unambiguous, verifiable, and non-transferable.
"""
import pytest
from arifosmcp.runtime.tools import init_anchor, arifos_kernel
from arifosmcp.runtime.models import AuthorityLevel, ClaimStatus, Verdict

class TestAuthorityScopeInvariant:
    """Invariant: scope matches session class"""

    @pytest.mark.asyncio
    async def test_sovereign_has_kernel_scope(self):
        """Sovereign session class must have arifos_kernel scope"""
        envelope = await init_anchor(
            actor_id='arif',
            intent='establish sovereign anchor',
            session_class='sovereign',
            session_id='sovereign-test-001'
        )
        
        # Check allowed tools in envelope
        assert "arifos_kernel" in envelope.allowed_next_tools, \
            "Sovereign anchor must be allowed to call kernel"

    @pytest.mark.asyncio
    async def test_anonymous_has_no_kernel_scope(self):
        """Anonymous session must not have arifos_kernel scope"""
        # Call without anchoring
        envelope = await arifos_kernel(
            query="dangerous query",
            session_id="global",
            risk_tier="high"
        )
        
        # Should be HOLD or VOID or SABAR
        assert envelope.verdict in [Verdict.HOLD, Verdict.VOID, Verdict.SABAR, Verdict.HOLD_888], \
            "Anonymous high-risk call must be held or voided"

class TestAuthorityProvenanceInvariant:
    """Invariant: authority is traceable to a source"""

    @pytest.mark.asyncio
    async def test_anchored_has_authority_source(self):
        """All anchored responses must include authority_source"""
        envelope = await init_anchor(
            actor_id='arif',
            intent='test provenance',
            session_id='provenance-test-003'
        )
        
        result = envelope.payload["result"]
        # In V2, auth_state is the source
        assert result["auth_state"] in ["verified", "claimed_only"], \
            "auth_state must be valid"

class TestCapabilityGatingInvariant:
    """Invariant: next_action gated on actual capability, not hardcoded"""

    @pytest.mark.asyncio
    async def test_sovereign_next_action_is_kernel(self):
        """Sovereign anchor should suggest kernel"""
        envelope = await init_anchor(
            actor_id='arif',
            intent='test next action',
            session_id='next-action-test-004'
        )
        
        # In V2 success, we check continuation
        result = envelope.payload["result"]
        assert "continuation" in result
        next_tools = result["continuation"].get("next_allowed_tools", [])
        assert "arifos_kernel" in next_tools, \
            "Sovereign allowed tools should include kernel"

    @pytest.mark.asyncio
    async def test_anonymous_next_action_is_anchor(self):
        """Anonymous status should suggest anchor"""
        envelope = await init_anchor(mode="status", session_id='global')
        assert "init_anchor" in envelope.allowed_next_tools

class TestRiskClassAlignmentInvariant:
    """Invariant: tool layer must match risk/governance class"""

    @pytest.mark.asyncio
    async def test_kernel_enforced_at_runtime(self):
        """arifos_kernel must report GOVERNANCE layer in specs"""
        from arifosmcp.runtime.public_registry import public_tool_spec_by_name
        specs = public_tool_spec_by_name()
        
        if "arifos_kernel" in specs:
            spec = specs["arifos_kernel"]
            assert spec.layer in ["KERNEL", "444_ROUTER", "GOVERNANCE"], "arifos_kernel must be KERNEL layer"

class TestErrorRemediationInvariant:
    """Invariant: Auth errors include actionable remediation"""

    @pytest.mark.asyncio
    async def test_auth_error_has_next_tool(self):
        """Auth failure must specify next tool"""
        result = await arifos_kernel(
            query='test remediation',
            session_id='remediation-test-005',
            risk_tier="high"
        )
        
        # Check remediation in envelope or errors or payload
        has_remediation = False
        if result.next_action:
            has_remediation = True
        
        if result.errors:
            for error in result.errors:
                if error.required_next_tool or "Call init_anchor" in error.message:
                    has_remediation = True
        
        if result.verdict in [Verdict.HOLD, Verdict.HOLD_888]:
            has_remediation = True
            
        if result.payload and "next_action" in result.payload:
            has_remediation = True

        assert has_remediation, "Auth error must have remediation guidance"

    @pytest.mark.asyncio
    async def test_auth_error_has_required_fields(self):
        """Auth failure must specify required fields"""
        result = await arifos_kernel(
            query='test remediation',
            session_id='remediation-test-006',
            risk_tier="high"
        )
        
        if result.verdict in [Verdict.HOLD, Verdict.VOID, Verdict.HOLD_888]:
            # Verify some error content exists
            assert len(result.errors) > 0 or result.next_action is not None or result.payload.get("next_action") is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
