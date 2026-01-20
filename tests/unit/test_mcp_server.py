"""
arifOS MCP Server Unit Tests - Test MCP tools and server.

Tests the MCP server, tool registry, and individual tools.
All tests are independent and use the actual pipeline (with stub LLM).

Run with:
    pytest tests/unit/test_mcp_server.py -v
"""

from __future__ import annotations

import pytest


# =============================================================================
# TEST CLASS: TOOL REGISTRY
# =============================================================================

class TestToolRegistry:
    """Test the MCP tool registry."""

    def test_list_tools_returns_dict(self):
        """list_tools should return a dict."""
        from arifos.core.mcp import list_tools

        tools = list_tools()
        assert isinstance(tools, dict)

    def test_list_tools_contains_expected_tools(self):
        """list_tools should contain expected tool names."""
        from arifos.core.mcp import list_tools

        tools = list_tools()
        assert "arifos_judge" in tools
        assert "arifos_recall" in tools
        assert "arifos_audit" in tools
        assert "APEX_LLAMA" in tools

    def test_list_tools_returns_at_least_three_tools(self):
        """list_tools should return at least the core tools."""
        from arifos.core.mcp import list_tools

        tools = list_tools()
        assert len(tools) >= 3

    def test_tools_are_callable(self):
        """All registered tools should be callable."""
        from arifos.core.mcp import list_tools

        tools = list_tools()
        for name, fn in tools.items():
            assert callable(fn), f"Tool {name} is not callable"


# =============================================================================
# TEST CLASS: JUDGE TOOL
# =============================================================================

class TestJudgeTool:
    """Test the arifos_judge tool."""

    def test_judge_import(self):
        """arifos_judge should be importable."""
        from arifos.core.mcp import arifos_judge
        assert callable(arifos_judge)

    def test_judge_returns_response(self):
        """arifos_judge should return a JudgeResponse."""
        from arifos.core.mcp import arifos_judge
        from arifos.core.mcp.models import JudgeRequest, JudgeResponse

        request = JudgeRequest(query="What is 2 + 2?")
        result = arifos_judge(request)

        assert isinstance(result, JudgeResponse)

    def test_judge_returns_verdict(self):
        """arifos_judge should return a verdict string."""
        from arifos.core.mcp import arifos_judge
        from arifos.core.mcp.models import JudgeRequest

        request = JudgeRequest(query="What is the capital of Japan?")
        result = arifos_judge(request)

        assert result.verdict in ["SEAL", "PARTIAL", "VOID", "SABAR", "888_HOLD", "UNKNOWN", "ERROR"]

    def test_judge_returns_reason(self):
        """arifos_judge should return a reason string."""
        from arifos.core.mcp import arifos_judge
        from arifos.core.mcp.models import JudgeRequest

        request = JudgeRequest(query="Hello world")
        result = arifos_judge(request)

        assert isinstance(result.reason, str)
        assert len(result.reason) > 0

    def test_judge_handles_simple_factual_query(self):
        """arifos_judge should handle simple factual queries."""
        from arifos.core.mcp import arifos_judge
        from arifos.core.mcp.models import JudgeRequest

        request = JudgeRequest(query="Define machine learning")
        result = arifos_judge(request)

        # Simple factual queries should typically SEAL
        assert result.verdict in ["SEAL", "PARTIAL", "UNKNOWN"]

    def test_judge_with_user_id(self):
        """arifos_judge should accept optional user_id."""
        from arifos.core.mcp import arifos_judge
        from arifos.core.mcp.models import JudgeRequest

        request = JudgeRequest(query="Test query", user_id="test_user_123")
        result = arifos_judge(request)

        assert result.verdict is not None


# =============================================================================
# TEST CLASS: RECALL TOOL
# =============================================================================

class TestRecallTool:
    """Test the arifos_recall tool."""

    def test_recall_import(self):
        """arifos_recall should be importable."""
        from arifos.core.mcp import arifos_recall
        assert callable(arifos_recall)

    def test_recall_returns_response(self):
        """arifos_recall should return a RecallResponse."""
        from arifos.core.mcp import arifos_recall
        from arifos.core.mcp.models import RecallRequest, RecallResponse

        request = RecallRequest(user_id="test_user", prompt="What is Amanah?")
        result = arifos_recall(request)

        assert isinstance(result, RecallResponse)

    def test_recall_returns_memories_list(self):
        """arifos_recall should return a memories list."""
        from arifos.core.mcp import arifos_recall
        from arifos.core.mcp.models import RecallRequest

        request = RecallRequest(user_id="test_user", prompt="test query")
        result = arifos_recall(request)

        assert isinstance(result.memories, list)

    def test_recall_includes_confidence_ceiling(self):
        """arifos_recall should include confidence ceiling."""
        from arifos.core.mcp import arifos_recall
        from arifos.core.mcp.models import RecallRequest

        request = RecallRequest(user_id="test_user", prompt="test")
        result = arifos_recall(request)

        assert result.confidence_ceiling == 0.85

    def test_recall_includes_l7_available_flag(self):
        """arifos_recall should include l7_available flag."""
        from arifos.core.mcp import arifos_recall
        from arifos.core.mcp.models import RecallRequest

        request = RecallRequest(user_id="test_user", prompt="test")
        result = arifos_recall(request)

        assert isinstance(result.l7_available, bool)

    def test_recall_includes_caveat(self):
        """arifos_recall should include a caveat string."""
        from arifos.core.mcp import arifos_recall
        from arifos.core.mcp.models import RecallRequest

        request = RecallRequest(user_id="test_user", prompt="test")
        result = arifos_recall(request)

        # Should have a caveat (either governance warning or error message)
        assert isinstance(result.caveat, str)
        assert len(result.caveat) > 0


# =============================================================================
# TEST CLASS: AUDIT TOOL
# =============================================================================

class TestAuditTool:
    """Test the arifos_audit tool."""

    def test_audit_import(self):
        """arifos_audit should be importable."""
        from arifos.core.mcp import arifos_audit
        assert callable(arifos_audit)

    def test_audit_returns_response(self):
        """arifos_audit should return an AuditResponse."""
        from arifos.core.mcp import arifos_audit
        from arifos.core.mcp.models import AuditRequest, AuditResponse

        request = AuditRequest(user_id="test_user", days=7)
        result = arifos_audit(request)

        assert isinstance(result, AuditResponse)

    def test_audit_returns_entries_list(self):
        """arifos_audit should return an entries list."""
        from arifos.core.mcp import arifos_audit
        from arifos.core.mcp.models import AuditRequest

        request = AuditRequest(user_id="test_user", days=7)
        result = arifos_audit(request)

        assert isinstance(result.entries, list)

    def test_audit_returns_stub_status(self):
        """arifos_audit should return stub status (not_implemented)."""
        from arifos.core.mcp import arifos_audit
        from arifos.core.mcp.models import AuditRequest

        request = AuditRequest(user_id="test_user", days=7)
        result = arifos_audit(request)

        assert result.status == "not_implemented"

    def test_audit_includes_note(self):
        """arifos_audit should include a note about future implementation."""
        from arifos.core.mcp import arifos_audit
        from arifos.core.mcp.models import AuditRequest

        request = AuditRequest(user_id="test_user", days=30)
        result = arifos_audit(request)

        assert "future" in result.note.lower() or "coming" in result.note.lower()


# =============================================================================
# TEST CLASS: RUN_TOOL DISPATCHER
# =============================================================================

class TestRunToolDispatcher:
    """Test the run_tool dispatcher function."""

    def test_run_tool_import(self):
        """run_tool should be importable."""
        from arifos.core.mcp import run_tool
        assert callable(run_tool)

    def test_run_tool_with_judge(self):
        """run_tool should work with arifos_judge."""
        from arifos.core.mcp import run_tool

        result = run_tool("arifos_judge", {"query": "Test query"})

        assert isinstance(result, dict)
        assert "verdict" in result
        assert "reason" in result

    def test_run_tool_with_recall(self):
        """run_tool should work with arifos_recall."""
        from arifos.core.mcp import run_tool

        result = run_tool("arifos_recall", {"user_id": "test", "prompt": "test"})

        assert isinstance(result, dict)
        assert "memories" in result
        assert "confidence_ceiling" in result

    def test_run_tool_with_audit(self):
        """run_tool should work with arifos_audit."""
        from arifos.core.mcp import run_tool

        result = run_tool("arifos_audit", {"user_id": "test", "days": 7})

        assert isinstance(result, dict)
        assert "entries" in result
        assert "status" in result

    def test_run_tool_unknown_tool_raises(self):
        """run_tool should raise ValueError for unknown tool."""
        from arifos.core.mcp import run_tool

        with pytest.raises(ValueError) as exc_info:
            run_tool("unknown_tool", {})

        assert "Unknown tool" in str(exc_info.value)


# =============================================================================
# TEST CLASS: MCP SERVER CLASS
# =============================================================================

class TestMCPServerClass:
    """Test the MCPServer class."""

    def test_mcp_server_import(self):
        """MCPServer should be importable."""
        from arifos.core.mcp.server import MCPServer
        assert MCPServer is not None

    def test_mcp_server_instantiation(self):
        """MCPServer should be instantiable."""
        from arifos.core.mcp.server import MCPServer

        server = MCPServer()
        assert server is not None

    def test_mcp_server_has_name(self):
        """MCPServer should have a name."""
        from arifos.core.mcp.server import MCPServer

        server = MCPServer()
        assert server.name == "arifos-mcp"

    def test_mcp_server_has_version(self):
        """MCPServer should have a version."""
        from arifos.core.mcp.server import MCPServer

        server = MCPServer()
        assert server.version is not None

    def test_mcp_server_list_tools(self):
        """MCPServer.list_tools should return tool descriptions."""
        from arifos.core.mcp.server import MCPServer

        server = MCPServer()
        tools = server.list_tools()

        assert isinstance(tools, dict)
        assert "arifos_judge" in tools
        assert "description" in tools["arifos_judge"]

    def test_mcp_server_call_tool(self):
        """MCPServer.call_tool should execute a tool."""
        from arifos.core.mcp.server import MCPServer

        server = MCPServer()
        result = server.call_tool("arifos_judge", {"query": "Test"})

        assert isinstance(result, dict)
        assert "verdict" in result

    def test_mcp_server_get_info(self):
        """MCPServer.get_info should return server info."""
        from arifos.core.mcp.server import MCPServer

        server = MCPServer()
        info = server.get_info()

        assert "name" in info
        assert "version" in info
        assert "tools" in info


# =============================================================================
# TEST CLASS: TOOL DESCRIPTIONS
# =============================================================================

class TestToolDescriptions:
    """Test tool description schemas."""

    def test_get_tool_descriptions_import(self):
        """get_tool_descriptions should be importable."""
        from arifos.core.mcp.server import get_tool_descriptions
        assert callable(get_tool_descriptions)

    def test_tool_descriptions_have_required_fields(self):
        """Tool descriptions should have required fields."""
        from arifos.core.mcp.server import get_tool_descriptions

        descriptions = get_tool_descriptions()

        for name, desc in descriptions.items():
            assert "name" in desc, f"Tool {name} missing 'name'"
            assert "description" in desc, f"Tool {name} missing 'description'"
            # Legacy tools like arifos_fag_read expose input_schema instead
            if name == "arifos_fag_read":
                assert "input_schema" in desc, "arifos_fag_read missing 'input_schema'"
            else:
                assert "parameters" in desc, f"Tool {name} missing 'parameters'"

    def test_tool_descriptions_have_json_schema(self):
        """Tool descriptions should have JSON schema for parameters."""
        from arifos.core.mcp.server import get_tool_descriptions

        descriptions = get_tool_descriptions()

        for name, desc in descriptions.items():
            if name == "arifos_fag_read":
                # FAG metadata uses 'input_schema' with JSON schema layout
                params = desc["input_schema"]
            else:
                params = desc["parameters"]
                assert params["type"] == "object", f"Tool {name} params should be object"
            assert "properties" in params, f"Tool {name} params missing 'properties'"
