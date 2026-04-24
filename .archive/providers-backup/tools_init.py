"""
arifosmcp/tools/__init__.py — 13 Canonical Tool Registration
═════════════════════════════════════════════════════════════

Imports all 13 canonical arif_* tools and exposes
register_canonical_tools(mcp) for FastMCP registration.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""
from __future__ import annotations

import logging
from typing import Any

from fastmcp import FastMCP

from arifosmcp.tools.session_init import arif_session_init
from arifosmcp.tools.sense_observe import arif_sense_observe
from arifosmcp.tools.evidence_fetch import arif_evidence_fetch
from arifosmcp.tools.mind_reason import arif_mind_reason
from arifosmcp.tools.kernel_route import arif_kernel_route
from arifosmcp.tools.reply_compose import arif_reply_compose
from arifosmcp.tools.memory_recall import arif_memory_recall
from arifosmcp.tools.heart_critique import arif_heart_critique
from arifosmcp.tools.gateway_connect import arif_gateway_connect
from arifosmcp.tools.ops_measure import arif_ops_measure
from arifosmcp.tools.judge_deliberate import arif_judge_deliberate
from arifosmcp.tools.vault_seal import arif_vault_seal
from arifosmcp.tools.forge_execute import arif_forge_execute

logger = logging.getLogger(__name__)

_TOOL_HANDLERS: dict[str, Any] = {
    "arif_session_init": arif_session_init,
    "arif_sense_observe": arif_sense_observe,
    "arif_evidence_fetch": arif_evidence_fetch,
    "arif_mind_reason": arif_mind_reason,
    "arif_kernel_route": arif_kernel_route,
    "arif_reply_compose": arif_reply_compose,
    "arif_memory_recall": arif_memory_recall,
    "arif_heart_critique": arif_heart_critique,
    "arif_gateway_connect": arif_gateway_connect,
    "arif_ops_measure": arif_ops_measure,
    "arif_judge_deliberate": arif_judge_deliberate,
    "arif_vault_seal": arif_vault_seal,
    "arif_forge_execute": arif_forge_execute,
}


def register_canonical_tools(mcp: FastMCP) -> list[str]:
    """Register the 13 canonical arif_* tools with the MCP server."""
    registered: list[str] = []
    for name, handler in _TOOL_HANDLERS.items():
        try:
            mcp.tool(name=name)(handler)
            registered.append(name)
            logger.debug("Registered tool: %s", name)
        except Exception as e:
            logger.warning("Failed to register tool %s: %s", name, e)
    logger.info("Registered %d canonical tools", len(registered))
    return registered
