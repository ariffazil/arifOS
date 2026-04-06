import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from arifosmcp.runtime.server import mcp


def get_tools_json():
    tools = []
    # FastMCP decorators add to _tools or _dependencies
    if hasattr(mcp, "_tools"):
        tools = mcp._tools.values()
    else:
        try:
            tools = [tool for name, tool in mcp._mcp_server.tools.items()]
        except Exception:
            try:
                tools = [t for name, t in mcp._app.tools.items()]
            except Exception:
                pass
    output = []
    for t in tools:
        output.append(
            {
                "name": getattr(t, "name", str(t)),
                "description": getattr(t, "description", ""),
            }
        )
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    get_tools_json()
