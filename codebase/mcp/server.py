"""
AAA MCP Server (v53.2.7-CODEBASE-AAA7)
Artifact · Authority · Architecture

Authority: Muhammad Arif bin Fazil
Architecture: Unified Trinity Application Layer (Codebase Edition)

The Application Layer for arifOS v53.
Now equipped with Constitutional Physics via Proxy Kernels.

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import logging
import sys
import time
from typing import Any, Dict, Optional

import mcp.types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from codebase.mcp.bridge import (
    bridge_init_router,
    bridge_agi_router,
    bridge_asi_router,
    bridge_apex_router,
    bridge_vault_router,
    bridge_trinity_loop_router,
    bridge_reality_check_router,
    bridge_asi_audit_router,
    bridge_asi_stakeholder_router,
    bridge_atlas_router,
)
from codebase.mcp.rate_limiter import get_rate_limiter
from codebase.mcp.mode_selector import get_mcp_mode, MCPMode
from codebase.mcp.constitutional_metrics import record_verdict
from codebase.enforcement.metrics import record_stage_metrics, record_verdict_metrics
from codebase.system.orchestrator.presenter import AAAMetabolizer

logger = logging.getLogger(__name__)

# Initialize Presenter
presenter = AAAMetabolizer()

# =============================================================================
# TOOL DESCRIPTIONS (v53.2.7 — Plain-Language Constitutional Governance)
#
# These descriptions ARE the constitution. Any AI or human reading them must
# understand what each tool does, what rules govern its use, and what outcomes
# to expect — without needing any prior knowledge of arifOS.
#
# Verdict outcomes returned by every tool:
#   SEAL      — Approved. All rules passed. Safe to act on the result.
#   PARTIAL   — Approved with warnings. Some safety checks flagged concerns.
#   VOID      — Rejected. A hard rule was broken. Do not act on this result.
#   888_HOLD  — Paused. Needs explicit human confirmation before proceeding.
#   SABAR     — Stopped. A serious violation occurred. Repair before retry.
# =============================================================================

TOOL_DESCRIPTIONS: Dict[str, Dict[str, Any]] = {
    "_ignite_": {
        "name": "_ignite_",
        "description": (
            "Session start & Authority verification [000-111]. "
            "Authenticates the Sovereign (Arif) and initializes the metabolic loop. "
            "Sets the constitutional boundaries for the current session."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Initial greeting or task."},
                "user_token": {"type": "string"},
            },
        },
    },
    "_logic_": {
        "name": "_logic_",
        "description": (
            "Deep Logical Reasoning & Sequential Thinking (Δ Mind). "
            "Uses chain-of-thought to reduce cognitive entropy. "
            "Enforces F2 (Truth) and F4 (Clarity)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Topic to analyze."},
                "session_id": {"type": "string"},
            },
            "required": ["query"],
        },
    },
    "_senses_": {
        "name": "_senses_",
        "description": (
            "External Reality Grounding (Brave/Perplexity). "
            "Fetches real-time data to verify internal logic against the outside world. "
            "Honors F7 Humility by citing sources explicitly."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query."},
                "session_id": {"type": "string"},
            },
            "required": ["query"],
        },
    },
    "_atlas_": {
        "name": "_atlas_",
        "description": (
            "Knowledge Mapping & Repository Topology. "
            "Visualizes the connections within the codebase and documentation. "
            "Maintains the Context7 epistemic atlas."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Area of repo to map."},
                "session_id": {"type": "string"},
            },
        },
    },
    "_forge_": {
        "name": "_forge_",
        "description": (
            "Structural Synthesis & Code Generation. "
            "The Architect's hands. Creates artifacts, modifies code, and builds systems. "
            "Strictly TDD-compliant."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Feature to build or bug to fix."},
                "session_id": {"type": "string"},
            },
            "required": ["task"],
        },
    },
    "_audit_": {
        "name": "_audit_",
        "description": (
            "Constitutional Compliance Scan (Ω Heart). "
            "Scans proposals for bias, safety risks, and floor violations. "
            "The pre-Witness self-check for the Architect."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "proposal": {"type": "string", "description": "Action to audit."},
                "session_id": {"type": "string"},
            },
            "required": ["proposal"],
        },
    },
    "_decree_": {
        "name": "_decree_",
        "description": (
            "Final Judgment & Immutable Sealing [888-999]. "
            "Collapses the wave function of decision into a SEALED verdict. "
            "Records the event in the VAULT-999 Ledger."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "verdict_data": {"type": "object", "description": "The consensus payload."},
                "session_id": {"type": "string"},
            },
            "required": ["verdict_data"],
        },
    },
}

# =============================================================================
# TOOL ROUTERS (v53.2.7 — 7-Tool Constitutional Architecture)
# =============================================================================

TOOL_ROUTERS = {
    "_ignite_": bridge_init_router,
    "_logic_": bridge_agi_router,
    "_senses_": bridge_reality_check_router,
    "_atlas_": bridge_atlas_router,
    "_forge_": bridge_agi_router,
    "_audit_": bridge_asi_audit_router,
    "_decree_": bridge_apex_router,
}

# =============================================================================
# SERVER FACTORY
# =============================================================================


def create_mcp_server(mode: Optional[MCPMode] = None) -> Server:
    """Create mode-aware arifOS MCP server."""
    if mode is None:
        mode = get_mcp_mode()

    server = Server(f"AAA-MCP-CODEBASE-{mode.value}")

    @server.list_tools()
    async def list_tools() -> list[mcp.types.Tool]:
        return [
            mcp.types.Tool(
                name=name, description=desc["description"], inputSchema=desc["inputSchema"]
            )
            for name, desc in TOOL_DESCRIPTIONS.items()
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[mcp.types.TextContent]:
        router = TOOL_ROUTERS.get(name)
        if not router:
            return [mcp.types.TextContent(type="text", text=f"VOID: Unknown tool {name}")]

        # Rate Limit Check
        session_id = arguments.get("session_id", "anonymous")
        limiter = get_rate_limiter()
        rate_result = limiter.check(name, session_id)

        if not rate_result.allowed:
            return [
                mcp.types.TextContent(
                    type="text", text=f"VOID: Rate limit exceeded ({rate_result.reason})"
                )
            ]

        start = time.time()
        try:
            if name == "_ignite_":
                result = await router(action="init", **arguments)
            elif name == "_logic_":
                result = await router(action="think", **arguments)
            elif name == "_senses_":
                result = await router(**arguments)
            elif name == "_atlas_":
                result = await router(**arguments)
            elif name == "_forge_":
                result = await router(action="forge", query=arguments.get("task"), **arguments)
            elif name == "_audit_":
                result = await router(text=arguments.get("proposal"), **arguments)
            elif name == "_decree_":
                result = await router(action="full", **arguments)
            else:
                # Fallback for dynamic tools
                action = arguments.pop("action", "full")
                result = await router(action=action, **arguments)

            duration = time.time() - start
            duration_ms = duration * 1000

            record_verdict(
                tool=name,
                verdict=result.get("verdict", "UNKNOWN"),
                duration=duration,
                mode=mode.value,
            )

            record_stage_metrics(name, duration_ms)
            record_verdict_metrics(result.get("verdict", "UNKNOWN"))

            formatted_text = presenter.process(result)
            return [mcp.types.TextContent(type="text", text=formatted_text)]

        except Exception as e:
            logger.error(f"Execution error in {name}: {e}")
            return [mcp.types.TextContent(type="text", text=f"ERROR: {str(e)}")]

    return server


# =============================================================================
# ENTRY POINTS
# =============================================================================


async def main_stdio():
    """Run standard stdio server."""
    mode = get_mcp_mode()
    print(f"[BOOT] Codebase MCP v53.1.0 starting in {mode.value} mode", file=sys.stderr)
    print("[PHYSICS] Constitutional Engines Loaded: AGI, ASI, APEX", file=sys.stderr)

    async with stdio_server() as (read_stream, write_stream):
        server = create_mcp_server(mode)
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main():
    """Entry point for console_scripts."""
    import asyncio

    asyncio.run(main_stdio())


if __name__ == "__main__":
    main()
