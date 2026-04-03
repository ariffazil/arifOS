"""arifOS Runtime — The Sovereign FastMCP Instance."""

from __future__ import annotations

import sys

# Keep the historical package alias and the canonical package name mapped to
# the same runtime module. This prevents duplicate collector registration when
# tests import both `arifosmcp.runtime.*` and `arifos_mcp.runtime.*`.
if __name__ == "arifos_mcp.runtime":
    sys.modules.setdefault("arifosmcp.runtime", sys.modules[__name__])
elif __name__ == "arifosmcp.runtime":
    sys.modules.setdefault("arifos_mcp.runtime", sys.modules[__name__])

# Simple imports
from . import models
from . import contracts
from . import sessions
from . import metrics
from . import bridge
from . import orchestrator
from . import tools_internal
from . import tools

from .server import mcp, create_aaa_mcp_server

__all__ = ["mcp", "create_aaa_mcp_server", "tools", "tools_internal", "bridge", "models", "contracts", "sessions", "metrics", "orchestrator"]
