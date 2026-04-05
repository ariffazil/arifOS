"""arifOS Runtime — The Sovereign FastMCP Instance."""

from __future__ import annotations

import sys

# Keep the historical package alias and the canonical package name mapped to
# the same runtime module. This prevents duplicate collector registration when
# tests import both `arifosmcp.runtime.*` and `arifosmcp.runtime.*`.
if __name__ == "arifosmcp.runtime":
    sys.modules.setdefault("arifosmcp.runtime", sys.modules[__name__])
elif __name__ == "arifosmcp.runtime":
    sys.modules.setdefault("arifosmcp.runtime", sys.modules[__name__])

# Simple imports
from . import bridge, contracts, metrics, models, orchestrator, sessions, tools, tools_internal
from .server import create_aaa_mcp_server, mcp

__all__ = ["mcp", "create_aaa_mcp_server", "tools", "tools_internal", "bridge", "models", "contracts", "sessions", "metrics", "orchestrator"]
