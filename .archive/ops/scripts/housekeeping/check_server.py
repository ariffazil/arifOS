from arifosmcp.runtime.server import mcp
print(f"MCP server loaded: {mcp.name}")
print(f"Tools: {[t.name for t in mcp.list_tools()]}")
