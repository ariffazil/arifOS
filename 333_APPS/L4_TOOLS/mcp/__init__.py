"""
codebase MCP Server Package (v53.2.0-SEAL)

Model Context Protocol implementation for arifOS constitutional AI governance.

Entry points:
- codebase-mcp-sse    # SSE transport (Railway/Cloud)
- aaa-mcp-sse         # Alias

Note: Heavy imports are done lazily to avoid startup delays.

DITEMPA BUKAN DIBERI
"""

__version__ = "v53.2.0-SEAL"

# Core exports (lightweight)
from .rate_limiter import (
    RateLimiter,
    RateLimitResult,
    get_rate_limiter,
    rate_limited,
    RATE_LIMIT_ENABLED,
)
from .immutable_ledger import (
    ImmutableLedger,
    LedgerRecord,
)
from .mode_selector import (
    get_mcp_mode,
    MCPMode,
)

# Tool classes should be imported directly when needed:
#   from codebase.mcp.tools import TrinityHatTool, AGITool, ASITool, APEXTool, VaultTool
#   from codebase.mcp.bridge import bridge_agi_router, bridge_asi_router, bridge_apex_router

__all__ = [
    "__version__",
    # Rate Limiter (F11 Command Auth)
    "RateLimiter",
    "RateLimitResult",
    "get_rate_limiter",
    "rate_limited",
    "RATE_LIMIT_ENABLED",
    # Immutable Ledger (F8 Tri-Witness)
    "ImmutableLedger",
    "LedgerRecord",
    # Mode Selector
    "get_mcp_mode",
    "MCPMode",
]
