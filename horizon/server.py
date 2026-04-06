"""
arifOS Horizon Adapter
=====================

DEPRECATED: Import from arifosmcp.server_horizon instead.

This file is kept for backward compatibility with existing Horizon deployments.
All new code should import from arifosmcp.server_horizon.

Status: DEPRECATED - redirects to arifosmcp.server_horizon
Branch: refactor/v2.0-abi
"""

# Redirect to canonical location
from arifosmcp.server_horizon import mcp

__all__ = ["mcp"]
