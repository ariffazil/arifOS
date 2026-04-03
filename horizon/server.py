"""
Deprecated Horizon shim.

Canonical public deployment must use ``server.py:mcp`` at the repository root.
This module remains only as a backwards-compatible import bridge during
reconciliation and should not be referenced in deployment docs or configs.
"""

from arifos_mcp.server_horizon import mcp

DEPRECATION_NOTICE = (
    "Deprecated: use server.py:mcp as the canonical public entrypoint. "
    "This shim is kept only for transitional compatibility."
)

__all__ = ["mcp", "DEPRECATION_NOTICE"]
