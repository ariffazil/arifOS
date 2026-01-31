"""
arifOS MCP Configuration Modes
"""

from enum import Enum
import os
import logging

logger = logging.getLogger(__name__)


class MCPMode(Enum):
    """MCP operational modes."""

    BRIDGE = "bridge"  # Production: Pure delegation to cores
    STANDALONE = "standalone"  # Development: Inline fallback logic
    AUTO = "auto"  # Auto-detect based on core availability


def get_mcp_mode() -> MCPMode:
    """Determine operational mode from environment (ARIFOS_MCP_MODE)."""
    mode_str = os.getenv("ARIFOS_MCP_MODE", "auto").lower()
    try:
        return MCPMode(mode_str)
    except ValueError:
        logger.warning(f"Invalid ARIFOS_MCP_MODE: {mode_str}, defaulting to 'auto'")
        return MCPMode.AUTO
