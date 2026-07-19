"""
arifosmcp/resources.py — Canonical MCP Resources surface for arifOS.

Re-exports register_resources from runtime.fastmcp_ext so the canonical
server (arifosmcp.server) can wire it via:

    from arifosmcp.resources import register_resources

This module exists to satisfy the canonical import path declared in
arifosmcp/server.py. The actual resource definitions live in
arifosmcp/runtime/fastmcp_ext/resources.py — that is where new resources
must be added.

DITEMPA BUKAN DIBERI — the resource surface is the protocol-layer home
of the constitution. APEX drift dies here, not at the discipline layer.
"""

from arifosmcp.runtime.fastmcp_ext.resources import register_arifos_resources as register_resources

__all__ = ["register_resources"]
