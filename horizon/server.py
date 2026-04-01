"""
arifOS Horizon Adapter
=====================

DEPRECATED: Import from arifos_mcp.server_horizon instead.

This file is kept for backward compatibility with existing Horizon deployments.
All new code should import from arifos_mcp.server_horizon.

Status: DEPRECATED - redirects to arifos_mcp.server_horizon
Branch: refactor/v2.0-abi
"""

# Redirect to canonical location
from arifos_mcp.server_horizon import mcp

__all__ = ["mcp"]
