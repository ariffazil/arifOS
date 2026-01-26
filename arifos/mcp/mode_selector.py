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
    # Lazy imports to reduce startup time
    if mode == MCPMode.BRIDGE:
        # Production: Pure bridge to cores
        try:
            from arifos.mcp.tools import v51_bridge
            return v51_bridge.get_tools()
        except ImportError as e:
            # Cores not available, fall back to standalone
            import warnings
            warnings.warn(f"Bridge mode requested but cores unavailable: {e}")
            return select_implementation(MCPMode.STANDALONE)
    
    else:  # STANDALONE or AUTO (with no cores)
        # Development: Inline logic, no core dependency
        from arifos.mcp.tools import mcp_aaa
        return mcp_aaa.get_tools()
