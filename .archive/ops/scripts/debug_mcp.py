import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from arifosmcp.runtime.server import mcp

    print(f"Type of mcp: {type(mcp)}")
    print(f"Has 'tool' attribute: {hasattr(mcp, 'tool')}")
    if hasattr(mcp, "tool"):
        print(f"Type of mcp.tool: {type(mcp.tool)}")

    # Check underlying server if any
    if hasattr(mcp, "_server"):
        print(f"Type of mcp._server: {type(mcp._server)}")
        print(f"mcp._server has 'tool': {hasattr(mcp._server, 'tool')}")

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
