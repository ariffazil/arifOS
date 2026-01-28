# arifos/mcp/mode_selector.py

from enum import Enum
from typing import Dict, Any, Optional
import os

class MCPMode(Enum):
    """MCP operational modes."""
    BRIDGE = "bridge"      # Production: Pure delegation to cores
    STANDALONE = "standalone"  # Development: Inline fallback logic
    AUTO = "auto"         # Auto-detect based on core availability

def get_mcp_mode() -> MCPMode:
    """
    Determine operational mode from environment.
    
    Environment variable: ARIFOS_MCP_MODE
    Options: bridge, standalone, auto
    Default: auto
    """
    mode_str = os.getenv("ARIFOS_MCP_MODE", "auto").lower()
    
    try:
        return MCPMode(mode_str)
    except ValueError:
        # Invalid mode, default to AUTO
        import warnings
        warnings.warn(f"Invalid ARIFOS_MCP_MODE: {mode_str}, defaulting to 'auto'")
        return MCPMode.AUTO

def select_implementation(mode: MCPMode) -> Dict[str, Any]:
    """
    Select MCP tool implementations based on mode.

    Returns:
        Dict mapping tool names to implementation functions
    """
    # All modes now use native codebase implementations
    from codebase.mcp.tools.mcp_trinity import (
        mcp_000_init,
        mcp_agi_genius,
        mcp_asi_act,
        mcp_apex_judge,
        mcp_999_vault,
    )

    return {
        "init_000": mcp_000_init,
        "agi_genius": mcp_agi_genius,
        "asi_act": mcp_asi_act,
        "apex_judge": mcp_apex_judge,
        "vault_999": mcp_999_vault,
    }
