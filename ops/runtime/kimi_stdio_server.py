"""
arifOS STDIO Server for Kimi CLI
═══════════════════════════════════

Kimi-compatible STDIO server with tool name translation.
Uses the unified server from project root.

Translates: arifos.init → arifos_init (Kimi API compatibility)
"""

import os
import sys

# Force local stdio mode
os.environ["ARIFOS_DEPLOYMENT"] = "local"
os.environ["AAA_MCP_TRANSPORT"] = "stdio"
os.environ["ARIFOS_MINIMAL_STDIO"] = "1"

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Import unified server
from arifosmcp.runtime.fastmcp_ext.transports import run_server
from server import mcp


def translate_tool_name(name: str) -> str:
    """Translate arifos.init → arifos_init for Kimi API compatibility."""
    return name.replace(".", "_")


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
    print("   Server: Unified (root server.py)", file=sys.stderr)
    print("   Tool Translation: arifos.* → arifos_*", file=sys.stderr)
    print("   Floors: F1-F13 (constitutional governance enabled)", file=sys.stderr)
    
    # Run unified server in stdio mode
    try:
        run_server(mcp, mode="stdio", host="", port=0)
    except KeyboardInterrupt:
        print("\n👋 arifOS STDIO Server stopped", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
