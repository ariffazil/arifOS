"""
arifOS Orchestrator
===================
MCP transport and coordination layer.

This subpackage is intentionally lightweight and does NOT import enforcement
dependencies to avoid spec file requirements during development.
"""

from .metabolizer import AAAMetabolizer, PresentationStrategy, UserProfile
from .mcp_gateway import MCPGateway, TransportClient, gateway

__all__ = [
    "AAAMetabolizer",
    "PresentationStrategy",
    "UserProfile",
    "MCPGateway",
    "TransportClient",
    "gateway",
]
