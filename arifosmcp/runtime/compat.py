"""
arifOS FastMCP Compatibility Layer
=================================

Single source of truth for FastMCP 2.x/3.x compatibility.
Consolidates: fastmcp_compat.py + fastmcp_version.py

All FastMCP version-specific code goes here.
No other module should import FastMCP directly.

Status: PHASE 1 - Consolidation
Branch: refactor/v2.0-abi
"""

from __future__ import annotations

import logging
from typing import Any, Callable

import fastmcp

logger = logging.getLogger(__name__)

# =============================================================================
# VERSION DETECTION
# =============================================================================

_version_parts = fastmcp.__version__.split('.')
VERSION_MAJOR = int(_version_parts[0])
VERSION_MINOR = int(_version_parts[1]) if len(_version_parts) > 1 else 0
VERSION_PATCH = int(_version_parts[2]) if len(_version_parts) > 2 else 0

IS_FASTMCP_3 = VERSION_MAJOR >= 3
IS_FASTMCP_2 = VERSION_MAJOR == 2

logger.info(f"[COMPAT] FastMCP version: {fastmcp.__version__} (3.x: {IS_FASTMCP_3})")

# =============================================================================
# EXCEPTION COMPATIBILITY
# =============================================================================

from fastmcp.exceptions import FastMCPError

try:
    from fastmcp.exceptions import ToolError
    HAS_TOOL_ERROR = True
except ImportError:
    HAS_TOOL_ERROR = False
    class ToolError(FastMCPError):
        """Tool execution error (FastMCP 2.x compatibility shim)."""
        pass

try:
    from fastmcp.exceptions import AuthorizationError
    HAS_AUTHORIZATION_ERROR = True
except ImportError:
    HAS_AUTHORIZATION_ERROR = False
    class AuthorizationError(FastMCPError):
        """Authorization error (FastMCP 2.x compatibility shim)."""
        def __init__(self, message: str = "Unauthorized", *, operation: str | None = None, resource: str | None = None):
            super().__init__(message)
            self.operation = operation
            self.resource = resource

# =============================================================================
# CONTEXT COMPATIBILITY
# =============================================================================

try:
    from fastmcp.server.context import Context
    HAS_CONTEXT = True
except ImportError:
    HAS_CONTEXT = False
    Context = Any

try:
    from fastmcp import Context  # Context injected; None fallback
    HAS_CURRENT_CONTEXT = True
except ImportError:
    HAS_CURRENT_CONTEXT = False
    CurrentContext = Any

# =============================================================================
# FASTMCP CLASS
# =============================================================================

from fastmcp import FastMCP

# =============================================================================
# HTTP APP CREATION
# =============================================================================

def create_http_app(mcp: FastMCP, stateless: bool = True) -> Any:
    """
    Create HTTP app compatible with FastMCP 2.x and 3.x.

    FastMCP 3.x: mcp.http_app(stateless_http=True)
    FastMCP 2.x: mcp.streamable_http_app() or mcp.http_app()
    """
    if IS_FASTMCP_3:
        return mcp.http_app(stateless_http=stateless)

    if hasattr(mcp, 'streamable_http_app'):
        return mcp.streamable_http_app()
    elif hasattr(mcp, 'http_app'):
        return mcp.http_app()

    raise RuntimeError("No HTTP app method available on FastMCP instance")

# =============================================================================
# CUSTOM ROUTE REGISTRATION
# =============================================================================

def custom_route(
    mcp: FastMCP,
    path: str,
    methods: list[str],
    **kwargs
) -> Callable:
    """
    Register custom HTTP route compatible with FastMCP 2.x and 3.x.
    """
    if hasattr(mcp, 'custom_route'):
        return mcp.custom_route(path, methods=methods, **kwargs)
    elif hasattr(mcp, 'route'):
        return mcp.route(path, methods=methods, **kwargs)

    raise RuntimeError("FastMCP instance has no custom_route or route method")

# =============================================================================
# TRANSPORT MODE
# =============================================================================

def get_compatible_transport(preferred: str = "streamable-http") -> str:
    """
    Get transport mode compatible with current FastMCP version.

    FastMCP 3.x: "streamable-http", "http", "stdio", "sse"
    FastMCP 2.x: "http", "stdio", "sse" (no "streamable-http")
    """
    if IS_FASTMCP_3:
        return preferred

    if preferred == "streamable-http":
        return "http"
    return preferred

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Version
    "VERSION_MAJOR",
    "VERSION_MINOR",
    "VERSION_PATCH",
    "IS_FASTMCP_3",
    "IS_FASTMCP_2",

    # Exceptions
    "FastMCPError",
    "ToolError",
    "AuthorizationError",
    "HAS_TOOL_ERROR",
    "HAS_AUTHORIZATION_ERROR",

    # Context
    "Context",
    "CurrentContext",
    "HAS_CONTEXT",
    "HAS_CURRENT_CONTEXT",

    # FastMCP
    "FastMCP",

    # Functions
    "create_http_app",
    "custom_route",
    "get_compatible_transport",
]
