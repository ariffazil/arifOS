"""arifOS Runtime — The Sovereign FastMCP Instance."""

from __future__ import annotations

import sys

# Keep the historical package alias and the canonical package name mapped to
# the same runtime module. This prevents duplicate collector registration when
# code imports both `mcp.runtime.*` and `arifosmcp.runtime.*`.
if __name__ == "arifosmcp.runtime":
    # If imported as arifosmcp.runtime, ensure mcp.runtime also points here
    sys.modules.setdefault("mcp.runtime", sys.modules[__name__])
elif __name__ == "mcp.runtime":
    # If imported as mcp.runtime (legacy), ensure arifosmcp.runtime also points here
    sys.modules.setdefault("arifosmcp.runtime", sys.modules[__name__])

__all__ = [
    "mcp",
    "create_aaa_mcp_server",
    "tools",
    "tools_internal",
    "bridge",
    "models",
    "contracts",
    "sessions",
    "metrics",
    "orchestrator",
]


def __getattr__(name: str):
    if name in {"mcp", "create_aaa_mcp_server"}:
        from .server import create_aaa_mcp_server, mcp

        return {"mcp": mcp, "create_aaa_mcp_server": create_aaa_mcp_server}[name]
    raise AttributeError(name)
