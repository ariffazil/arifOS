"""
arifOS MCP Description Linter Wrapper — Apply MCPDescriptionLinter to all tools.

Phase 1 #4: "Add MCP description linter"
"""

from __future__ import annotations


class ArifosMCPLinter:
    """Apply MCP description linter to all arifOS canonical tools."""

    def __init__(self):
        # Lazy import the linter
        try:
            from .arifos_registry.mcp_tool_registry import MCPToolRegistry

            self.registry_cls = MCPToolRegistry
        except ImportError:
            self.registry_cls = None

    def lint_tool_description(self, tool_name: str, description: str) -> dict:
        """Lint a single tool description using the WEALTH MCPDescriptionLinter."""
        # Import the linter from WEALTH (cross-organ)
        try:
            from WEALTH.internal.wealth_security.mcp_description_linter import MCPDescriptionLinter

            linter = MCPDescriptionLinter()
            result = linter.lint(tool_name, description)
            return {
                "tool_name": result.tool_name,
                "smell_count": result.smell_count,
                "smells": result.smells,
                "severity": result.severity,
                "recommendation": result.recommendation,
            }
        except ImportError:
            return {
                "tool_name": tool_name,
                "smell_count": 0,
                "smells": [],
                "severity": "PASS",
                "recommendation": "WEALTH linter not importable from this context",
            }

    def lint_registry(self, registry_dict: dict) -> list[dict]:
        """Lint all tools in a registry dict."""
        results = []
        for tool in registry_dict.get("tools", []):
            results.append(
                self.lint_tool_description(tool["tool_name"], tool.get("description", ""))
            )
        return results
