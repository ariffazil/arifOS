"""
tests/runtime/test_tools_advanced.py — Advanced Runtime Tools Tests (11 Mega-Tools Edition)

Verifies the consolidated 11-tool surface and dispatcher logic.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Any

class TestMegaToolRegistration:
    """Test the registration of the 11 Mega-Tools"""

    def test_mega_tool_count(self):
        """Verify exactly 11 tools are registered in the public registry"""
        from arifosmcp.runtime.public_registry import public_tool_names
        names = public_tool_names()
        assert len(names) == 11
        assert "init_anchor" in names
        assert "arifos_kernel" in names
        assert "apex_soul" in names

    def test_mega_tool_schemas(self):
        """Verify schemas contain the required 'mode' and 'payload'"""
        from arifosmcp.runtime.public_registry import public_tool_specs
        for spec in public_tool_specs():
            properties = spec.input_schema.get("properties", {})
            assert "mode" in properties
            assert "payload" in properties

class TestMegaToolDispatch:
    """Test the dispatcher logic in tools.py"""

    @pytest.mark.asyncio
    async def test_init_anchor_dispatch(self):
        """Test init_anchor dispatches to init_anchor_impl"""
        from arifosmcp.runtime.tools import init_anchor
        # Patch where the implementation is imported in tools.py
        with patch("arifosmcp.runtime.tools.init_anchor_impl", new_callable=AsyncMock) as mock_impl:
            mock_impl.return_value = MagicMock()
            await init_anchor(mode="init", payload={"actor_id": "arif", "intent": "test"})
            mock_impl.assert_called_once()

    @pytest.mark.asyncio
    async def test_kernel_dispatch(self):
        """Test arifos_kernel dispatches to arifos_kernel_impl"""
        from arifosmcp.runtime.tools import arifos_kernel
        # Patch where the implementation is imported in tools.py
        with patch("arifosmcp.runtime.tools.arifos_kernel_impl", new_callable=AsyncMock) as mock_impl:
            mock_impl.return_value = MagicMock()
            await arifos_kernel(mode="kernel", payload={"query": "test"})
            mock_impl.assert_called_once()

    @pytest.mark.asyncio
    async def test_invalid_mode(self):
        """Test that an invalid mode raises ValueError"""
        from arifosmcp.runtime.tools import init_anchor
        with pytest.raises(ValueError, match="Invalid mode"):
            await init_anchor(mode="invalid_mode", payload={})

class TestTrinityAlignment:
    """Test trinity and stage mapping in contracts.py"""

    def test_trinity_mapping(self):
        from arifosmcp.runtime.contracts import TRINITY_BY_TOOL
        assert TRINITY_BY_TOOL["init_anchor"] == "PSI Ψ"
        assert TRINITY_BY_TOOL["agi_mind"] == "DELTA Δ"
        assert TRINITY_BY_TOOL["asi_heart"] == "OMEGA Ω"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
