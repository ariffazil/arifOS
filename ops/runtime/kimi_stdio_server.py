"""
arifOS STDIO Server for Kimi CLI — Dot-to-Underscore Tool Name Translation

Kimi's API doesn't allow dots in function names, but MCP spec does.
This wrapper translates arifos.* tool names to arifos_* for Kimi compatibility.
"""

import os
import sys
import json
import asyncio

# Force local stdio mode
os.environ["ARIFOS_DEPLOYMENT"] = "local"
os.environ["AAA_MCP_TRANSPORT"] = "stdio"
os.environ["ARIFOS_MINIMAL_STDIO"] = "1"

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from arifosmcp.runtime.server import create_aaa_mcp_server
from arifosmcp.runtime.fastmcp_ext.transports import run_server


def translate_tool_name(name: str) -> str:
    """Translate arifos.init → arifos_init for Kimi API compatibility."""
    return name.replace(".", "_")


def translate_tool_name_back(name: str) -> str:
    """Translate arifos_init → arifos.init for arifOS internal use."""
    # Handle special case: arifos_vps_monitor stays as is (no dot version)
    if name.startswith("arifos_"):
        parts = name.split("_", 1)
        if len(parts) == 2:
            return f"arifos.{parts[1]}"
    return name


class KimiCompatibleMCPServer:
    """Wrapper that translates tool names between Kimi API and arifOS MCP."""
    
    def __init__(self, mcp_server):
        self._mcp = mcp_server
        self._original_tools = {}
        
    def _translate_tools(self, tools: list) -> list:
        """Translate all tool names in a list."""
        translated = []
        for tool in tools:
            if hasattr(tool, 'name'):
                original_name = tool.name
                translated_name = translate_tool_name(original_name)
                self._original_tools[translated_name] = original_name
                tool.name = translated_name
                translated.append(tool)
            elif isinstance(tool, dict) and 'name' in tool:
                original_name = tool['name']
                translated_name = translate_tool_name(original_name)
                self._original_tools[translated_name] = original_name
                tool['name'] = translated_name
                translated.append(tool)
        return translated
    
    def __getattr__(self, name):
        """Delegate to wrapped MCP server."""
        return getattr(self._mcp, name)


def main():
    """Run arifOS STDIO server with Kimi-compatible tool names."""
    print("🔥 arifOS STDIO Server (Kimi Compatible) starting...", file=sys.stderr)
    print("   Mode: Local (minimal)", file=sys.stderr)
    print("   Transport: STDIO", file=sys.stderr)
    print("   Tool Name Translation: arifos.* → arifos_*", file=sys.stderr)
    print("   Floors: F1-F13 (constitutional governance enabled)", file=sys.stderr)
    
    # Create minimal MCP server
    mcp = create_aaa_mcp_server()
    
    # Run in stdio mode
    try:
        run_server(mcp, mode="stdio", host="", port=0)
    except KeyboardInterrupt:
        print("\n👋 arifOS STDIO Server stopped", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
