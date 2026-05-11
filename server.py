"""Compatibility shim for the packaged arifOS server.

The canonical runtime implementation lives in `arifosmcp.server`, which is the
module shipped in the Docker image and imported by transport/runtime entrypoints.
Keep this root module as a thin re-export for local scripts and older tests.
"""

from arifosmcp.capability_map import LEGACY_TOOL_MAP
from arifosmcp.server import GlobalPanicMiddleware, app, main, mcp

__all__ = [
    "LEGACY_TOOL_MAP",
    "GlobalPanicMiddleware",
    "app",
    "main",
    "mcp",
]


if __name__ == "__main__":
    main()
