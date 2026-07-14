"""
arifosmcp/prompts.py — Canonical MCP Prompts surface for arifOS.

Re-exports register_prompts from runtime.fastmcp_ext so the canonical
server (arifosmcp.server) can wire it via:

    from arifosmcp.prompts import register_prompts

This module exists to satisfy the canonical import path declared in
arifosmcp/server.py. The actual prompt definitions live in
arifosmcp/runtime/fastmcp_ext/prompts.py — that is where new prompts
must be added.

DITEMPA BUKAN DIBERI — the prompt surface is the protocol-layer home
of governance ceremonies. Embed resources by reference; never restate.
"""

from arifosmcp.runtime.fastmcp_ext.prompts import register_arifos_prompts as register_prompts

__all__ = ["register_prompts"]
