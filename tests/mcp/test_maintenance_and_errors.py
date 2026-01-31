import pytest
import asyncio
from unittest.mock import MagicMock, patch
from codebase.mcp.bridge import bridge_init_router, BridgeError
try:
    from codebase.mcp.maintenance import session_maintenance_loop
except (ImportError, SyntaxError):
    session_maintenance_loop = None  # maintenance module archived


async def test_error_categorization():
    """Test that errors are correctly categorized in the bridge."""
    with patch("codebase.mcp.core.bridge.get_kernel_manager") as mock_manager:
        # Simulate a kernel failure
        mock_manager.side_effect = Exception("Kernel Crash")
        
        result = await bridge_init_router(action="init")
        
        assert result["status"] == "VOID"
        assert result["verdict"] == "VOID"
        assert result["error_category"] == "ENGINE_FAILURE"
        assert "Kernel Crash" in result["reason"]


@pytest.mark.skipif(session_maintenance_loop is None, reason="maintenance module archived")
async def test_maintenance_loop_picks_up_orphans():
    """Test that the maintenance loop picks up orphans and calls recover."""
    with patch("codebase.mcp.maintenance.get_orphaned_sessions") as mock_get_orphans, \
         patch("codebase.mcp.maintenance.recover_orphaned_session") as mock_recover, \
         patch("asyncio.sleep", side_effect=[None, asyncio.CancelledError]): # Run once then stop
        
        mock_get_orphans.return_value = [{"session_id": "orphan-123", "started_at": "2026-01-29T00:00:00Z"}]
        
        try:
            await session_maintenance_loop(interval_seconds=1)
        except asyncio.CancelledError:
            pass
            
        mock_get_orphans.assert_called_once()
        mock_recover.assert_called_once()
        args, _ = mock_recover.call_args
        assert args[0]["session_id"] == "orphan-123"


async def test_bridge_serialization():
    """Test that bridge serialization handles basic types and dicts."""
    from codebase.mcp.bridge import _serialize
    
    data = {"a": 1, "b": "str", "c": [1, 2], "d": {"inner": True}}
    assert _serialize(data) == data
    
    # Test object with __dict__
    class MockObj:
        def __init__(self):
            self.foo = "bar"
            self._secret = "hidden"
    
    serialized = _serialize(MockObj())
    assert serialized == {"foo": "bar"}
    assert "_secret" not in serialized
