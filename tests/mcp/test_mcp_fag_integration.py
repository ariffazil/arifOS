"""
Test MCP FAG Integration

Validates that arifos_fag_read tool works correctly via MCP server.
"""

import pytest
import json
from pathlib import Path
from arifos.mcp.tools.fag_read import (
    arifos_fag_read,
    FAGReadRequest,
    FAGReadResponse,
    TOOL_METADATA,
)


class TestMCPFAGTool:
    """Test MCP FAG read tool."""

    def test_tool_metadata_structure(self):
        """Verify TOOL_METADATA has required fields (v49)."""
        assert "name" in TOOL_METADATA
        assert "description" in TOOL_METADATA
        # v49 uses "parameters" for Pydantic JSON schema
        assert "parameters" in TOOL_METADATA
        assert TOOL_METADATA["name"] == "arifos_fag_read"

    def test_tool_metadata_schema(self):
        """Verify JSON schema in metadata (v49)."""
        # v49 stores Pydantic JSON schema in "parameters"
        schema = TOOL_METADATA["parameters"]
        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "path" in schema["properties"]
        assert "root" in schema["properties"]
        assert "enable_ledger" in schema["properties"]

    def test_request_model_validation(self):
        """Test FAGReadRequest Pydantic validation."""
        # Valid request
        req = FAGReadRequest(
            path="README.md",
            root=".",
            enable_ledger=True
        )
        assert req.path == "README.md"
        assert req.root == "."
        assert req.enable_ledger is True

    def test_read_safe_file_via_mcp(self, tmp_path):
        """Test reading a safe file via MCP tool."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello arifOS FAG")

        # Call MCP tool
        request = FAGReadRequest(
            path=str(test_file),
            root=str(tmp_path),
            enable_ledger=False
        )
        response = arifos_fag_read(request)

        # Validate response
        assert isinstance(response, FAGReadResponse)
        assert response.verdict == "SEAL"
        assert response.content == "Hello arifOS FAG"
        assert response.reason is None
        assert response.floor_scores is not None
        assert response.floor_scores["F1_amanah"] == 1.0

    def test_read_forbidden_file_via_mcp(self, tmp_path):
        """Test reading .env file via MCP tool (should be blocked)."""
        # Create .env file
        env_file = tmp_path / ".env"
        env_file.write_text("SECRET_KEY=dangerous")

        # Call MCP tool
        request = FAGReadRequest(
            path=str(env_file),
            root=str(tmp_path),
            enable_ledger=False
        )
        response = arifos_fag_read(request)

        # Validate VOID verdict
        assert response.verdict == "VOID"
        assert response.content is None
        assert response.reason is not None
        assert "F9" in response.reason or "forbidden" in response.reason.lower()

    def test_read_nonexistent_file_via_mcp(self, tmp_path):
        """Test reading nonexistent file via MCP tool."""
        request = FAGReadRequest(
            path=str(tmp_path / "nonexistent.txt"),
            root=str(tmp_path),
            enable_ledger=False
        )
        response = arifos_fag_read(request)

        # Validate VOID verdict
        assert response.verdict == "VOID"
        assert response.content is None
        assert response.reason is not None
        assert "F2" in response.reason or "not exist" in response.reason.lower()

    def test_path_traversal_blocked_via_mcp(self, tmp_path):
        """Test path traversal is blocked via MCP tool."""
        # Create file outside jail
        outside = tmp_path.parent / "outside.txt"
        outside.write_text("Secret data")

        # Try path traversal
        request = FAGReadRequest(
            path="../outside.txt",
            root=str(tmp_path),
            enable_ledger=False
        )
        response = arifos_fag_read(request)

        # Validate VOID verdict (F1 Amanah breach)
        assert response.verdict == "VOID"
        assert response.content is None
        assert response.reason is not None
        assert "F1" in response.reason or "jail" in response.reason.lower()

    def test_ledger_integration_via_mcp(self, tmp_path):
        """Test Cooling Ledger integration via MCP tool."""
        # Create test file
        test_file = tmp_path / "ledger_test.txt"
        test_file.write_text("FAG ledger test")

        # Call with ledger enabled
        request = FAGReadRequest(
            path=str(test_file),
            root=str(tmp_path),
            enable_ledger=True
        )
        response = arifos_fag_read(request)

        # Validate ledger entry ID is present
        assert response.verdict == "SEAL"
        assert response.ledger_entry_id is not None
        assert len(response.ledger_entry_id) > 0

    def test_json_serialization(self, tmp_path):
        """Test that response can be JSON serialized (MCP requirement)."""
        test_file = tmp_path / "json_test.txt"
        test_file.write_text("JSON test")

        request = FAGReadRequest(
            path=str(test_file),
            root=str(tmp_path),
            enable_ledger=False
        )
        response = arifos_fag_read(request)

        # Convert to dict (Pydantic models)
        response_dict = response.model_dump()

        # Serialize to JSON
        json_str = json.dumps(response_dict)
        assert len(json_str) > 0

        # Deserialize
        parsed = json.loads(json_str)
        assert parsed["verdict"] == "SEAL"
        assert parsed["content"] == "JSON test"


class TestMCPServerIntegration:
    """Test FAG integration with MCP server registry.

    NOTE (v49): Server registry pattern (arifos.mcp.server) deprecated in v49.
    v49 uses unified_server with FastMCP decorators instead of manual registration.
    These tests are skipped pending v49 server architecture validation tests.
    """

    @pytest.mark.skip(reason="v49: arifos.mcp.server module removed, replaced with unified_server")
    def test_fag_tool_registered_in_server(self):
        """Verify arifos_fag_read is registered in MCP server (v49: OBSOLETE)."""
        pytest.skip("v49: Server registry pattern deprecated. Use unified_server instead.")

    @pytest.mark.skip(reason="v49: arifos.mcp.server module removed, replaced with unified_server")
    def test_tool_callable_from_registry(self, tmp_path):
        """Test calling FAG tool via server registry (v49: OBSOLETE)."""
        pytest.skip("v49: Server registry pattern deprecated. Use unified_server instead.")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
