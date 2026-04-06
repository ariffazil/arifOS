import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from arifosmcp.runtime.server import mcp


def get_tools_json():
    # In FastMCP 3.x, tools are registered decorators. We can access the underlying tools.
    # The mcp._mcp_server has list_tools() which is an async function or we can just read mcp._tools
    tools = []
    for tool_name in mcp._tools.keys():
        t = mcp._tools[tool_name]
        tools.append({"name": t.name, "description": t.description, "schema": t.parameters})
    print(json.dumps(tools, indent=2))


if __name__ == "__main__":
    get_tools_json()
