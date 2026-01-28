"""
Tests for arifOS MCP Utils Server

Run: pytest tests/test_mcp_utils.py -v
"""

import asyncio
import os
import pytest
from unittest.mock import patch, MagicMock

# Import the tools
from arifos.mcp.mcp_utils_server import (
    tool_fetch_url,
    tool_shell,
    tool_grep_search,
    _validate_shell_command,
)


class TestShellValidation:
    """Test shell command validation."""

    def test_allowed_commands(self):
        """Test that allowed commands pass validation."""
        allowed = [
            "python script.py",
            "git status",
            "ls -la",
            "pytest -v",
            "docker ps",
            "npm install",
        ]
        for cmd in allowed:
            is_valid, error = _validate_shell_command(cmd)
            assert is_valid, f"Command '{cmd}' should be allowed: {error}"

    def test_blocked_commands(self):
        """Test that dangerous commands are blocked."""
        blocked = [
            "rm -rf /",
            "sudo rm -rf /",
            "mkfs.ext4 /dev/sda",
            ":(){ :|:& };:",
        ]
        for cmd in blocked:
            is_valid, error = _validate_shell_command(cmd)
            assert not is_valid, f"Command '{cmd}' should be blocked"

    def test_unknown_commands_blocked(self):
        """Test that unknown commands are blocked."""
        is_valid, error = _validate_shell_command("unknown_cmd arg")
        assert not is_valid
        assert "not in allowed commands list" in error


class TestShellTool:
    """Test shell tool execution."""

    @pytest.mark.asyncio
    async def test_echo_command(self):
        """Test basic echo command."""
        result = await tool_shell("echo hello world")
        assert result["status"] == "success"
        assert result["returncode"] == 0
        assert "hello world" in result["stdout"]

    @pytest.mark.asyncio
    async def test_pwd_command(self):
        """Test pwd command returns current directory."""
        result = await tool_shell("pwd")
        assert result["status"] == "success"
        assert result["returncode"] == 0
        assert len(result["stdout"].strip()) > 0

    @pytest.mark.asyncio
    async def test_blocked_command_rejected(self):
        """Test that blocked commands are rejected before execution."""
        result = await tool_shell("rm -rf /")
        assert result["status"] == "error"
        assert "Security validation failed" in result["error"]

    @pytest.mark.asyncio
    async def test_invalid_cwd(self):
        """Test invalid working directory."""
        result = await tool_shell("echo test", cwd="/nonexistent/path")
        assert result["status"] == "error"
        assert "Working directory does not exist" in result["error"]

    @pytest.mark.asyncio
    async def test_timeout(self):
        """Test command timeout."""
        result = await tool_shell("sleep 10", timeout=1)
        assert result["status"] == "error"
        assert "timed out" in result["error"]


class TestGrepSearch:
    """Test grep search tool."""

    @pytest.mark.asyncio
    async def test_search_in_current_file(self):
        """Test searching in the current test file."""
        result = await tool_grep_search(
            pattern="async def test_",
            path=__file__,
            output_mode="content"
        )
        assert result["status"] == "success"
        assert result["match_count"] > 0
        assert len(result["matches"]) > 0

    @pytest.mark.asyncio
    async def test_files_mode(self):
        """Test files-only output mode."""
        result = await tool_grep_search(
            pattern="class.*",
            path=__file__,
            output_mode="files"
        )
        assert result["status"] == "success"
        assert __file__ in result["matches"]

    @pytest.mark.asyncio
    async def test_invalid_path(self):
        """Test invalid path handling."""
        result = await tool_grep_search(
            pattern="test",
            path="/nonexistent/path"
        )
        assert result["status"] == "error"
        assert "Path does not exist" in result["error"]

    @pytest.mark.asyncio
    async def test_glob_filter(self):
        """Test file glob filtering."""
        result = await tool_grep_search(
            pattern="def ",
            path=".",
            glob="*.py",
            head_limit=5
        )
        assert result["status"] == "success"
        # Should only find .py files
        for match in result["matches"]:
            assert match["file"].endswith(".py")


class TestFetchUrl:
    """Test URL fetching tool."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not pytest.importorskip("httpx", reason="httpx not installed"),
        reason="httpx not installed"
    )
    async def test_invalid_url_scheme(self):
        """Test that non-http schemes are rejected."""
        result = await tool_fetch_url("ftp://example.com/file.txt")
        assert result["status"] == "error"
        assert "Invalid URL scheme" in result["error"]

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not pytest.importorskip("httpx", reason="httpx not installed"),
        reason="httpx not installed"
    )
    async def test_malformed_url(self):
        """Test malformed URL handling."""
        result = await tool_fetch_url("not a valid url")
        assert result["status"] == "error"

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not pytest.importorskip("httpx", reason="httpx not installed"),
        reason="httpx not installed"
    )
    async def test_successful_fetch(self):
        """Test successful URL fetch (requires internet)."""
        # Use httpbin for reliable testing
        result = await tool_fetch_url(
            "https://httpbin.org/get",
            extract_text=False,
            timeout=10
        )
        # Note: May fail if no internet, so we just check structure
        if result["status"] == "success":
            assert "status_code" in result
            assert result["content"] is not None


class TestIntegration:
    """Integration tests for the full server."""

    @pytest.mark.asyncio
    async def test_server_creation(self):
        """Test that the server can be created."""
        from arifos.mcp.mcp_utils_server import create_utils_server
        server = await create_utils_server()
        assert server is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
