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

from codebase.mcp.tools.canonical_trinity import (
    mcp_init,
    mcp_agi,
    mcp_asi,
    mcp_apex,
    mcp_vault,
    mcp_trinity,
    mcp_reality,
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
    "_init_": {
        "name": "_init_",
        "description": "Session gate + security [000-111]. Authenticates authority and blocks injections.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["init", "gate", "reset", "validate", "authorize"]},
                "query": {"type": "string"},
                "user_token": {"type": "string"},
                "session_id": {"type": "string"}
            },
            "required": ["action"]
        }
    },
    "_agi_": {
        "name": "_agi_",
        "description": "Mind engine (Δ) [111-333]. Sense, Think, Map, Forge. Enforces Truth (F2) & Clarity (F4).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["sense", "think", "reflect", "reason", "atlas", "forge", "full", "physics"]},
                "query": {"type": "string"},
                "session_id": {"type": "string"},
                "context": {"type": "object"}
            },
            "required": ["action"]
        }
    },
    "_asi_": {
        "name": "_asi_",
        "description": "Heart engine (Ω) [444-666]. Empathy, Safety, Alignment. Enforces Peace (F5) & Empathy (F6).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["evidence", "empathize", "evaluate", "act", "witness", "stakeholder", "diffusion", "audit", "full"]},
                "query": {"type": "string"},
                "reasoning": {"type": "string"},
                "session_id": {"type": "string"},
                "text": {"type": "string"}
            },
            "required": ["action"]
        }
    },
    "_apex_": {
        "name": "_apex_",
        "description": "Soul engine (Ψ) [777-888]. Judicial consensus and final verdict. Enforces Genius (F8) & Ontology (F10).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["eureka", "judge", "decide", "proof", "entropy", "full"]},
                "query": {"type": "string"},
                "response": {"type": "string"},
                "verdict": {"type": "string", "enum": ["SEAL", "PARTIAL", "SABAR", "VOID", "888_HOLD"]},
                "reasoning": {"type": "string"},
                "session_id": {"type": "string"}
            },
            "required": ["action"]
        }
    },
    "_vault_": {
        "name": "_vault_",
        "description": "Immutable ledger (Seal) [999]. Permanent audit trail and Merkle sealing.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["seal", "list", "read", "write", "propose"]},
                "verdict": {"type": "string"},
                "decision_data": {"type": "object"},
                "target": {"type": "string", "enum": ["seal", "ledger", "canon", "fag", "tempa", "phoenix", "audit"]},
                "session_id": {"type": "string"}
            },
            "required": ["action"]
        }
    },
    "_trinity_": {
        "name": "_trinity_",
        "description": "Full metabolic pipeline [000-999]. Chains AGI -> ASI -> APEX -> VAULT.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "session_id": {"type": "string"}
            },
            "required": ["query"]
        }
    },
    "_reality_": {
        "name": "_reality_",
        "description": "External Fact-Checking [F7]. Verifies claims against live internet data.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "session_id": {"type": "string"}
            },
            "required": ["query"]
        }
    }
}

# =============================================================================
# TOOL ROUTERS (v53.2.7 — 7-Tool Constitutional Architecture)
# =============================================================================

        try:
            if name == "_init_":
                result = await mcp_init(**arguments)
            elif name == "_agi_":
                result = await mcp_agi(**arguments)
            elif name == "_asi_":
                result = await mcp_asi(**arguments)
            elif name == "_apex_":
                result = await mcp_apex(**arguments)
            elif name == "_vault_":
                result = await mcp_vault(**arguments)
            elif name == "_trinity_":
                result = await mcp_trinity(**arguments)
            elif name == "_reality_":
                result = await mcp_reality(**arguments)
            else:
                return [mcp.types.TextContent(type="text", text=f"VOID: Tool {name} not implemented")]

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
