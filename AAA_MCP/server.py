"""
AAA MCP SERVER (v51.0.0) - Constitutional Intelligence
Artifact · Authority · Architecture

The Application Layer for arifOS.
Zero logic - only protocol translation and routing.

Tools:
  000_init    → Gate (Authority + Injection + Amanah)
  agi_genius  → Mind (SENSE → THINK → ATLAS → FORGE)
  asi_act     → Heart (EVIDENCE → EMPATHY → ACT)
  apex_judge  → Soul (EUREKA → JUDGE → PROOF)
  999_vault   → Seal (Merkle + zkPC + Immutable Log)

Usage:
  python -m AAA_MCP              # stdio mode
  python -m AAA_MCP sse          # SSE mode for Railway

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import logging
import sys
from typing import Any, Dict, List

import mcp.types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from AAA_MCP.bridge import (
    ENGINES_AVAILABLE,
    bridge_init_router,
    bridge_agi_router,
    bridge_asi_router,
    bridge_apex_router,
    bridge_vault_router,
)
from arifos.core.enforcement.governance.rate_limiter import get_rate_limiter

logger = logging.getLogger(__name__)

# =============================================================================
# TOOL DEFINITIONS (MCP Spec Compliant)
# =============================================================================

TOOL_DESCRIPTIONS: Dict[str, Dict[str, Any]] = {
    "000_init": {
        "name": "000_init",
        "description": """000 INIT: System Ignition & Constitutional Gateway.

The first gate. All requests must pass through here.

Actions:
  - init: Full initialization (gate + reset + validate)
  - gate: Constitutional authority check only
  - reset: Clean session start
  - validate: Pre-flight validation

Floors Enforced: F1 (Amanah), F11 (CommandAuth), F12 (InjectionDefense)""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["init", "gate", "reset", "validate"],
                    "default": "init",
                    "description": "Initialization action"
                },
                "query": {"type": "string", "description": "Initial query to check"},
                "authority_token": {"type": "string", "description": "Optional authority token"},
                "session_id": {"type": "string", "description": "Optional session ID to resume"},
                "context": {"type": "object", "description": "Optional context metadata"}
            },
            "required": []
        }
    },
    "agi_genius": {
        "name": "agi_genius",
        "description": """AGI GENIUS: The Mind (Δ) - Truth & Reasoning Engine.

Consolidates: 111 SENSE + 222 THINK + 333 ATLAS + 777 FORGE

Actions:
  - sense: Lane classification + truth threshold (111)
  - think: Deep reasoning with constitutional constraints (222)
  - reflect: Clarity/entropy checking (222)
  - atlas: Meta-cognition & governance mapping (333)
  - forge: Clarity refinement + humility injection (777)
  - evaluate: Floor evaluation (F2 + F6)
  - full: Complete AGI pipeline

Floors Enforced: F2 (Truth ≥0.99), F6 (ΔS ≥0), F7 (Humility)""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["sense", "think", "reflect", "atlas", "forge", "evaluate", "full"],
                    "description": "AGI action to perform"
                },
                "query": {"type": "string", "description": "Query to process"},
                "session_id": {"type": "string", "description": "Session ID from 000_init"},
                "thought": {"type": "string", "description": "Thought content for reasoning"},
                "context": {"type": "object", "description": "Context metadata"},
                "draft": {"type": "string", "description": "Draft response for evaluation"},
                "axioms": {"type": "array", "items": {"type": "string"}, "description": "Constitutional axioms"},
                "truth_score": {"type": "number", "description": "Truth confidence (0.0-1.0)"}
            },
            "required": ["action"]
        }
    },
    "asi_act": {
        "name": "asi_act",
        "description": """ASI ACT: The Heart (Ω) - Safety & Empathy Engine.

Consolidates: 444 EVIDENCE + 555 EMPATHY + 666 ACT + 333 WITNESS

Actions:
  - evidence: Truth grounding via sources (444)
  - empathize: Power-aware recalibration (555)
  - align: Constitutional veto gates (666)
  - act: Execution with tri-witness gating (666)
  - witness: Collect tri-witness signatures (333)
  - evaluate: Floor evaluation (F3 + F4 + F5)
  - full: Complete ASI pipeline

Floors Enforced: F3 (Peace² ≥1.0), F4 (κᵣ ≥0.7), F5 (Ω₀ ∈ [0.03,0.05])""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["evidence", "empathize", "align", "act", "witness", "evaluate", "full"],
                    "description": "ASI action to perform"
                },
                "text": {"type": "string", "description": "Text to process"},
                "session_id": {"type": "string", "description": "Session ID from 000_init"},
                "query": {"type": "string", "description": "Query for evidence gathering"},
                "proposal": {"type": "string", "description": "Proposal for empathy/alignment"},
                "agi_result": {"type": "object", "description": "Result from agi_genius"},
                "stakeholders": {"type": "array", "items": {"type": "string"}, "description": "Stakeholders to consider"},
                "sources": {"type": "array", "items": {"type": "string"}, "description": "Sources for evidence"},
                "witness_request_id": {"type": "string", "description": "Witness request ID"},
                "approval": {"type": "boolean", "description": "Witness approval decision"},
                "reason": {"type": "string", "description": "Reason for witness decision"}
            },
            "required": ["action"]
        }
    },
    "apex_judge": {
        "name": "apex_judge",
        "description": """APEX JUDGE: The Soul (Ψ) - Judgment & Authority Engine.

Consolidates: 777 EUREKA + 888 JUDGE + 889 PROOF

Actions:
  - eureka: Paradox synthesis (Truth ∩ Care) (777)
  - judge: Final constitutional verdict (888)
  - proof: Cryptographic sealing (889)
  - entropy: Constitutional entropy measurement
  - parallelism: Parallelism proof
  - full: Complete APEX pipeline

Floors Enforced: F1 (Amanah), F8 (Tri-Witness ≥0.95), F9 (Anti-Hantu)

Verdicts: SEAL (approved), SABAR (retry), VOID (rejected)""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["eureka", "judge", "proof", "entropy", "parallelism", "full"],
                    "description": "APEX action to perform"
                },
                "query": {"type": "string", "description": "Original query"},
                "response": {"type": "string", "description": "Response to judge"},
                "session_id": {"type": "string", "description": "Session ID from 000_init"},
                "agi_result": {"type": "object", "description": "Result from agi_genius"},
                "asi_result": {"type": "object", "description": "Result from asi_act"},
                "data": {"type": "string", "description": "Data for cryptographic proof"},
                "verdict": {"type": "string", "enum": ["SEAL", "SABAR", "VOID"], "description": "Verdict to seal"}
            },
            "required": ["action"]
        }
    },
    "999_vault": {
        "name": "999_vault",
        "description": """999 VAULT: Immutable Seal & Governance IO.

The final gate. Seals all decisions immutably.

Actions:
  - seal: Final seal with Merkle + zkPC
  - list: List vault entries
  - read: Read vault entry
  - write: Write to vault (requires authority)
  - propose: Propose new canon entry

Targets:
  - seal: Final sealing operation
  - ledger: Constitutional ledger (immutable)
  - canon: Approved knowledge
  - fag: File Authority Guardian
  - tempa: Temporary artifacts
  - phoenix: Resurrectable memory
  - audit: Audit trail

Floors Enforced: F1 (Amanah), F8 (Tri-Witness)""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["seal", "list", "read", "write", "propose"],
                    "description": "Vault action to perform"
                },
                "session_id": {"type": "string", "description": "Session ID from 000_init"},
                "verdict": {"type": "string", "enum": ["SEAL", "SABAR", "VOID"], "description": "Verdict to seal"},
                "init_result": {"type": "object", "description": "Result from 000_init"},
                "agi_result": {"type": "object", "description": "Result from agi_genius"},
                "asi_result": {"type": "object", "description": "Result from asi_act"},
                "apex_result": {"type": "object", "description": "Result from apex_judge"},
                "target": {
                    "type": "string",
                    "enum": ["seal", "ledger", "canon", "fag", "tempa", "phoenix", "audit"],
                    "description": "Storage target"
                },
                "query": {"type": "string", "description": "Query/path for read/write"},
                "data": {"type": "object", "description": "Data to write"}
            },
            "required": ["action"]
        }
    }
}

# Tool name to router mapping
TOOL_ROUTERS = {
    "000_init": bridge_init_router,
    "agi_genius": bridge_agi_router,
    "asi_act": bridge_asi_router,
    "apex_judge": bridge_apex_router,
    "999_vault": bridge_vault_router,
}


# =============================================================================
# MCP SERVER CREATION
# =============================================================================

def create_aaa_server() -> Server:
    """Create the 5-tool AAA MCP server."""
    server = Server("AAA-Model-Context-Protocol")

    @server.list_tools()
    async def list_tools() -> List[mcp.types.Tool]:
        """List all 5 AAA tools."""
        tools_list = []
        for name, desc in TOOL_DESCRIPTIONS.items():
            tools_list.append(
                mcp.types.Tool(
                    name=name,
                    description=desc.get("description", f"Tool {name}"),
                    inputSchema=desc.get("inputSchema", {"type": "object", "properties": {}})
                )
            )
        return tools_list

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> Any:
        """Execute an AAA tool via bridge router."""
        router = TOOL_ROUTERS.get(name)
        if not router:
            return {"status": "VOID", "error": f"Unknown tool: {name}"}

        # F11: Rate limit check (Command Authority floor)
        session_id = arguments.get("session_id", "")
        rate_limiter = get_rate_limiter()
        rate_result = rate_limiter.check(name, session_id)
        if not rate_result.allowed:
            logger.warning(f"Rate limit exceeded for {name}: {rate_result.reason}")
            return {
                "status": "VOID",
                "reason": rate_result.reason,
                "rate_limit": {
                    "exceeded": True,
                    "limit_type": rate_result.limit_type,
                    "reset_in_seconds": rate_result.reset_in_seconds
                },
                "floors_checked": ["F11_CommandAuth"]
            }

        # Extract action and remove from arguments to avoid passing twice
        action = arguments.pop("action", "full")

        try:
            result = router(action=action, **arguments)
            return result
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            return {"status": "VOID", "error": str(e), "tool": name}

    return server


# =============================================================================
# ENTRY POINTS
# =============================================================================

async def main_stdio():
    """Run AAA server with stdio transport."""
    print_stats()
    async with stdio_server() as (read_stream, write_stream):
        server = create_aaa_server()
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main_sse():
    """Run AAA server with SSE transport (for Railway deployment)."""
    import os
    import uvicorn

    # SSE app creation - import from arifos for now, can be copied later
    try:
        from arifos.mcp.sse import create_sse_app
    except ImportError:
        logger.error("SSE module not available. Install arifos with SSE support.")
        sys.exit(1)

    port = int(os.environ.get("PORT", os.environ.get("AAA_MCP_PORT", 8000)))

    print_stats()
    logger.info(f"SSE Mode: http://0.0.0.0:{port}")
    logger.info(f"Health: http://0.0.0.0:{port}/health")

    # Create SSE app with AAA tools
    app = create_sse_app(
        tools={name: TOOL_ROUTERS[name] for name in TOOL_DESCRIPTIONS},
        tool_descriptions=TOOL_DESCRIPTIONS,
        server_name="AAA-MCP",
        version="v51.0"
    )
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


def print_stats():
    """Print AAA MCP server banner."""
    print("=" * 70, file=sys.stderr)
    print("AAA MCP SERVER (v51.0) - Constitutional Intelligence", file=sys.stderr)
    print("Artifact · Authority · Architecture", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print(file=sys.stderr)
    print("Mnemonic: 'Init the Genius, Act with Heart, Judge at Apex, seal in Vault.'", file=sys.stderr)
    print(file=sys.stderr)
    print("Tools:", file=sys.stderr)
    print("  000_init    → Gate (Authority + Injection + Amanah)", file=sys.stderr)
    print("  agi_genius  → Mind (SENSE → THINK → ATLAS → FORGE)", file=sys.stderr)
    print("  asi_act     → Heart (EVIDENCE → EMPATHY → ACT)", file=sys.stderr)
    print("  apex_judge  → Soul (EUREKA → JUDGE → PROOF)", file=sys.stderr)
    print("  999_vault   → Seal (Merkle + zkPC + Immutable Log)", file=sys.stderr)
    print(file=sys.stderr)
    print(f"Core Engines: {'Available' if ENGINES_AVAILABLE else 'Fallback Mode'}", file=sys.stderr)
    print("=" * 70, file=sys.stderr)


if __name__ == "__main__":
    import asyncio

    if len(sys.argv) > 1 and sys.argv[1] == "sse":
        main_sse()
    else:
        asyncio.run(main_stdio())
