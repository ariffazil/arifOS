# arifos-core/mcp_server.py
from fastmcp import FastMCP
from arifos.registry import register_all_tools

mcp = FastMCP("arifos-core")

register_all_tools(mcp)

if __name__ == "__main__":
    mcp.run()
