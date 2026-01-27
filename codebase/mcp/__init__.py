"""
codebase MCP Server Package (v52.6.0-SEAL UPDATED)

Model Context Protocol implementation for arifOS constitutional AI governance.

Entry points:
- aaa-mcp         # stdio transport (Claude Desktop)
- aaa-mcp sse     # SSE transport (Railway/Cloud)

Tool Classes (v52.6.0 Architecture):
- TrinityHatTool: 6th tool - 3-Loop compressor
- AGITool: Mind engine with metrics/parallel/evidence
- ASITool: Heart engine with empathy and ethics  
- APEXTool: Soul engine with judgment
- VaultTool: Immutable ledger sealing

DITEMPA BUKAN DIBERI
"""

__version__ = "v52.6.0-SEAL"

# Tool classes - import what actually exists
from codebase.mcp.tools import (
    TrinityHatTool,
    AGITool,
    ASITool,
    APEXTool,
    VaultTool,
)

# v52.6.0 compatibility - expose tool instances if needed
# But don't import functions that don't exist

try:
    # Bridge imports - these may not exist yet
    from codebase.mcp.bridge import (
        bridge_trinity_hat_router,
        bridge_agi_router,
        bridge_asi_router,
        bridge_apex_router,
        bridge_vault_router,
    )
    _bridge_available = True
except ImportError:
    _bridge_available = False

__all__ = [
    # Tool classes
    "TrinityHatTool",
    "AGITool",
    "ASITool", 
    "APEXTool",
    "VaultTool",
    # Version
    "__version__",
]
