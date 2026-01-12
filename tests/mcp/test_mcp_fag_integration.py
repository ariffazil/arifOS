"""
Test MCP FAG Integration

Validates that arifos_fag_read tool works correctly via MCP server.
"""

import pytest
import json
from pathlib import Path
from arifos_core.mcp.tools.fag_read import (
    arifos_fag_read,
    FAGReadRequest,
    FAGReadResponse,
    TOOL_METADATA,
)


class TestMCPFAGTool:
    """Test MCP FAG read tool."""

    def test_tool_metadata_structure(self):
        """Verify TOOL_METADATA has required fields."""
        assert "name" in TOOL_METADATA
        assert "description" in TOOL_METADATA
        # Support both camelCase and snake_case for schema key
        assert "inputSchema" in TOOL_METADATA or "input_schema" in TOOL_METADATA
        assert TOOL_METADATA["name"] == "arifos_fag_read"

    def test_tool_metadata_schema(self):
        """Verify JSON schema in metadata."""
        schema = TOOL_METADATA.get("inputSchema") or TOOL_METADATA["input_schema"]
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
    """Test FAG integration with MCP server registry."""

    def test_fag_tool_registered_in_server(self):
        """Verify arifos_fag_read is registered in MCP server."""
        from arifos_core.mcp.server import TOOLS, TOOL_REQUEST_MODELS, TOOL_DESCRIPTIONS

        # Check registration
        assert "arifos_fag_read" in TOOLS
        assert "arifos_fag_read" in TOOL_REQUEST_MODELS
        assert "arifos_fag_read" in TOOL_DESCRIPTIONS

        # Validate function reference
        assert TOOLS["arifos_fag_read"] == arifos_fag_read

        # Validate request model
        assert TOOL_REQUEST_MODELS["arifos_fag_read"] == FAGReadRequest

        # Validate metadata
        assert TOOL_DESCRIPTIONS["arifos_fag_read"]["name"] == "arifos_fag_read"

    def test_tool_callable_from_registry(self, tmp_path):
        """Test calling FAG tool via server registry."""
        from arifos_core.mcp.server import TOOLS, TOOL_REQUEST_MODELS

        # Get tool from registry
        tool_func = TOOLS["arifos_fag_read"]
        request_model = TOOL_REQUEST_MODELS["arifos_fag_read"]

        # Create test file
        test_file = tmp_path / "registry_test.txt"
        test_file.write_text("Registry test")

        # Create request
        request = request_model(
            path=str(test_file),
            root=str(tmp_path),
            enable_ledger=False
        )

        # Call tool
        response = tool_func(request)

        # Validate
        assert response.verdict == "SEAL"
        assert response.content == "Registry test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
