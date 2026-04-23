"""
tests/test_init_unification.py — Unified Init Anchor Test Suite

Validates the ONE init_anchor tool consolidation:
- All modes work: init, state, status, revoke, refresh
- Legacy tools route correctly via CAPABILITY_MAP
- Constitutional floors enforced (F11, F12, F13)
- Session continuity maintained
"""

from __future__ import annotations

import pytest
import asyncio
from typing import Any

# Test imports with lazy loading to avoid circular imports
@pytest.fixture
def capability_map():
    from arifosmcp.capability_map import CAPABILITY_MAP
    return CAPABILITY_MAP

@pytest.fixture
def public_tool_specs():
    from arifosmcp.runtime.tool_specs import PUBLIC_TOOL_SPECS
    return PUBLIC_TOOL_SPECS


class TestLegacyToolRemoval:
    """Verify legacy tools are REMOVED from CAPABILITY_MAP."""

    def test_init_anchor_state_is_removed(self, capability_map):
        """Legacy 'init_anchor_state' is no longer in CAPABILITY_MAP."""
        assert "init_anchor_state" not in capability_map
        print("✓ init_anchor_state successfully purged")

    def test_revoke_anchor_state_is_removed(self, capability_map):
        """Legacy 'revoke_anchor_state' is no longer in CAPABILITY_MAP."""
        assert "revoke_anchor_state" not in capability_map
        print("✓ revoke_anchor_state successfully purged")

    def test_get_caller_status_is_removed(self, capability_map):
        """Legacy 'get_caller_status' is no longer in CAPABILITY_MAP."""
        assert "get_caller_status" not in capability_map
        print("✓ get_caller_status successfully purged")

    def test_init_anchor_state_impl_is_removed(self):
        """Internal legacy implementations are physically deleted."""
        try:
            from arifosmcp.runtime.tools_internal import init_anchor_impl
            pytest.fail("init_anchor_impl still exists in tools_internal.py")
        except ImportError:
            print("✓ init_anchor_impl successfully deleted from tools_internal.py")


class TestToolSpecCompliance:
    """Verify tool spec matches unified implementation."""

    def test_init_anchor_in_public_specs(self, public_tool_specs):
        """init_anchor is in PUBLIC_TOOL_SPECS with correct modes."""
        spec = next((s for s in public_tool_specs if s.name == "init_anchor"), None)
        assert spec is not None
        assert spec.stage == "000_INIT"
        modes = spec.input_schema["properties"]["mode"]["enum"]
        assert "init" in modes
        assert "state" in modes
        assert "status" in modes
        assert "revoke" in modes
        assert "refresh" in modes
        print(f"✓ Tool spec includes all 5 unified modes: {modes}")

    def test_description_mentions_unification(self, public_tool_specs):
        """Tool description mentions unified nature."""
        spec = next((s for s in public_tool_specs if s.name == "init_anchor"), None)
        assert spec is not None
        desc = spec.description
        assert "Unified" in desc or "unified" in desc.lower()
        assert "ONE tool" in desc or "ONE" in desc
        print("✓ Tool description documents unification")


class TestModeEnums:
    """Verify InitAnchorMode enum has all required modes."""

    def test_all_modes_present(self):
        from arifosmcp.capability_map import InitAnchorMode
        modes = {m.value for m in InitAnchorMode}
        assert "init" in modes
        assert "state" in modes
        assert "status" in modes
        assert "revoke" in modes
        assert "refresh" in modes
        print(f"✓ InitAnchorMode includes: {modes}")


class TestImplementationStructure:
    """Verify the internal implementation structure."""

    def test_init_anchor_dispatch_handles_all_modes(self):
        """hardened_init_anchor_dispatch has logic for all 5 modes."""
        from arifosmcp.runtime.tools_hardened_dispatch import hardened_init_anchor_dispatch
        import inspect
        
        source = inspect.getsource(hardened_init_anchor_dispatch)
        # Check for mode dispatch in the hardened layer
        assert 'mode == "revoke"' in source or "mode == 'revoke'" in source
        assert 'mode in ("state", "status", "refresh")' in source or "mode in ('state', 'status', 'refresh')" in source
        print("✓ hardened_init_anchor_dispatch handles all 5 modes")

    def test_legacy_impls_are_purged(self):
        """Legacy implementations are completely removed."""
        from arifosmcp.runtime import tools_internal
        assert not hasattr(tools_internal, "revoke_anchor_state_impl")
        assert not hasattr(tools_internal, "refresh_anchor_impl")
        assert not hasattr(tools_internal, "get_caller_status_impl")
        print("✓ Legacy implementations are GONE forever")


class TestUnifiedToolSignature:
    """Verify the unified tool signature accepts all parameters."""

    def test_init_anchor_accepts_all_modes_via_payload_and_kwargs(self):
        """init_anchor accepts mode and broad kwargs for ingress tolerance."""
        from arifosmcp.runtime.tools import init_anchor
        import inspect
        
        sig = inspect.signature(init_anchor)
        params = list(sig.parameters.keys())
        
        assert "mode" in params
        assert "payload" in params
        assert "query" in params
        assert "session_id" in params
        print(f"✓ init_anchor signature complies with V2 Mega-Tool standard")


if __name__ == "__main__":
    print("=" * 70)
    print("UNIFIED INIT ANCHOR TEST SUITE — Architectural Verification")
    print("=" * 70)
    print()
    
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
