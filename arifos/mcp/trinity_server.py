"""
arifOS Trinity MCP Server (v50.5.24)
5-Tool Constitutional Framework

The Metabolic Standard compressed to 5 memorable tools:
    000_init    → Gate (Authority + Injection + Amanah)
    agi_genius  → Mind (SENSE → THINK → ATLAS)
    asi_act     → Heart (EVIDENCE → EMPATHY → ACT)
    apex_judge  → Soul (EUREKA → JUDGE → PROOF)
    999_vault   → Seal (PROOF + Immutable Log)

Mnemonic: "Init the Genius, Act with Heart, Judge at Apex, seal in Vault."

Usage:
    stdio: python -m arifos.mcp trinity
    SSE:   python -m arifos.mcp trinity-sse

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import logging
import sys
from typing import Any, Callable, Dict, List

import mcp.types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from arifos.mcp.tools.mcp_trinity import (
    mcp_000_init,
    mcp_agi_genius,
    mcp_asi_act,
    mcp_apex_judge,
    mcp_999_vault,
)

logger = logging.getLogger(__name__)

# =============================================================================
# 5 TRINITY TOOLS
# =============================================================================

TOOLS: Dict[str, Callable] = {
    "000_init": mcp_000_init,
    "agi_genius": mcp_agi_genius,
    "asi_act": mcp_asi_act,
    "apex_judge": mcp_apex_judge,
    "999_vault": mcp_999_vault,
}

# =============================================================================
# TOOL DESCRIPTIONS (MCP Spec Compliant)
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
                "query": {
                    "type": "string",
                    "description": "Initial query to check"
                },
                "authority_token": {
                    "type": "string",
                    "description": "Optional authority token"
                },
                "session_id": {
                    "type": "string",
                    "description": "Optional session ID to resume"
                },
                "context": {
                    "type": "object",
                    "description": "Optional context metadata"
                }
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
                "query": {
                    "type": "string",
                    "description": "Query to process"
                },
                "session_id": {
                    "type": "string",
                    "description": "Session ID from 000_init"
                },
                "thought": {
                    "type": "string",
                    "description": "Thought content for reasoning"
                },
                "context": {
                    "type": "object",
                    "description": "Context metadata"
                },
                "draft": {
                    "type": "string",
                    "description": "Draft response for evaluation"
                },
                "axioms": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Constitutional axioms to apply"
                },
                "truth_score": {
                    "type": "number",
                    "description": "Truth confidence (0.0-1.0)"
                }
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
                "text": {
                    "type": "string",
                    "description": "Text to process"
                },
                "session_id": {
                    "type": "string",
                    "description": "Session ID from 000_init"
                },
                "query": {
                    "type": "string",
                    "description": "Query for evidence gathering"
                },
                "proposal": {
                    "type": "string",
                    "description": "Proposal for empathy/alignment"
                },
                "agi_result": {
                    "type": "object",
                    "description": "Result from agi_genius"
                },
                "stakeholders": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Stakeholders to consider"
                },
                "sources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Sources for evidence"
                },
                "witness_request_id": {
                    "type": "string",
                    "description": "Witness request ID for signing"
                },
                "approval": {
                    "type": "boolean",
                    "description": "Witness approval decision"
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for witness decision"
                }
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
  - entropy: Constitutional entropy measurement (Agent Zero)
  - parallelism: Parallelism proof (Agent Zero)
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
                "query": {
                    "type": "string",
                    "description": "Original query"
                },
                "response": {
                    "type": "string",
                    "description": "Response to judge"
                },
                "session_id": {
                    "type": "string",
                    "description": "Session ID from 000_init"
                },
                "agi_result": {
                    "type": "object",
                    "description": "Result from agi_genius"
                },
                "asi_result": {
                    "type": "object",
                    "description": "Result from asi_act"
                },
                "data": {
                    "type": "string",
                    "description": "Data for cryptographic proof"
                },
                "verdict": {
                    "type": "string",
                    "enum": ["SEAL", "SABAR", "VOID"],
                    "description": "Verdict to seal"
                }
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
                "session_id": {
                    "type": "string",
                    "description": "Session ID from 000_init"
                },
                "verdict": {
                    "type": "string",
                    "enum": ["SEAL", "SABAR", "VOID"],
                    "description": "Verdict to seal"
                },
                "init_result": {
                    "type": "object",
                    "description": "Result from 000_init"
                },
                "agi_result": {
                    "type": "object",
                    "description": "Result from agi_genius"
                },
                "asi_result": {
                    "type": "object",
                    "description": "Result from asi_act"
                },
                "apex_result": {
                    "type": "object",
                    "description": "Result from apex_judge"
                },
                "target": {
                    "type": "string",
                    "enum": ["seal", "ledger", "canon", "fag", "tempa", "phoenix", "audit"],
                    "description": "Storage target"
                },
                "query": {
                    "type": "string",
                    "description": "Query/path for read/write"
                },
                "data": {
                    "type": "object",
                    "description": "Data to write"
                }
            },
            "required": ["action"]
        }
    }
}

# =============================================================================
# MCP SERVER CREATION
# =============================================================================

def create_trinity_server() -> Server:
    """Create the 5-tool Trinity MCP server."""
    server = Server("arifOS-Trinity-v50.5.24")

    @server.list_tools()
    async def list_tools() -> List[mcp.types.Tool]:
        """List all 5 Trinity tools."""
        tools_list = []
        for name in TOOLS:
            desc = TOOL_DESCRIPTIONS.get(name, {})
            tools_list.append(
                mcp.types.Tool(
                    name=name,
                    description=desc.get("description", f"Tool {name}"),
                    inputSchema=desc.get("inputSchema", {
                        "type": "object",
                        "properties": {}
                    })
                )
            )
        return tools_list

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a Trinity tool."""
        tool = TOOLS.get(name)
        if not tool:
            raise ValueError(f"Unknown tool: {name}")

        try:
            import inspect
            if inspect.iscoroutinefunction(tool):
                return await tool(**arguments)
            else:
                return tool(**arguments)
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            return {"status": "VOID", "error": str(e), "tool": name}

    return server


# =============================================================================
# MAIN ENTRY POINTS
# =============================================================================

async def main_stdio():
    """Run Trinity server with stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        server = create_trinity_server()
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main_sse():
    """Run Trinity server with SSE transport."""
    import os
    import uvicorn
    from arifos.mcp.sse import create_sse_app

    port = int(os.environ.get("PORT", os.environ.get("AAA_MCP_PORT", 8000)))

    logger.info("=" * 60)
    logger.info("arifOS Trinity SSE Server v50.5.24")
    logger.info("5-Tool Constitutional Framework")
    logger.info("=" * 60)
    logger.info(f"Tools: {list(TOOLS.keys())}")
    logger.info(f"Port: {port}")
    logger.info(f"Health: http://0.0.0.0:{port}/health")
    logger.info(f"Docs: http://0.0.0.0:{port}/docs")
    logger.info("=" * 60)

    # Create SSE app with Trinity tools
    app = create_sse_app(
        tools=TOOLS,
        tool_descriptions=TOOL_DESCRIPTIONS,
        server_name="arifOS-Trinity",
        version="v50.5.24"
    )
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


def print_stats():
    """Print Trinity server statistics."""
    print("=" * 80, file=sys.stderr)
    print("arifOS Trinity MCP Server v50.5.24 - 5-Tool Constitutional Framework", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    print(file=sys.stderr)
    print("Mnemonic: 'Init the Genius, Act with Heart, Judge at Apex, seal in Vault.'", file=sys.stderr)
    print(file=sys.stderr)
    print("Trinity Tools (5):", file=sys.stderr)
    print("  000_init    → Gate (Authority + Injection + Amanah)", file=sys.stderr)
    print("  agi_genius  → Mind (SENSE → THINK → ATLAS → FORGE)", file=sys.stderr)
    print("  asi_act     → Heart (EVIDENCE → EMPATHY → ACT)", file=sys.stderr)
    print("  apex_judge  → Soul (EUREKA → JUDGE → PROOF)", file=sys.stderr)
    print("  999_vault   → Seal (Merkle + zkPC + Immutable Log)", file=sys.stderr)
    print(file=sys.stderr)
    print("Constitutional Floors:", file=sys.stderr)
    print("  000_init:    F1, F11, F12", file=sys.stderr)
    print("  agi_genius:  F2, F6, F7", file=sys.stderr)
    print("  asi_act:     F3, F4, F5, F9, F11, F12", file=sys.stderr)
    print("  apex_judge:  F1, F7, F8, F9", file=sys.stderr)
    print("  999_vault:   F1, F8", file=sys.stderr)
    print(file=sys.stderr)
    print("Verdicts: SEAL (approved) | SABAR (retry) | VOID (rejected)", file=sys.stderr)
    print("=" * 80, file=sys.stderr)


if __name__ == "__main__":
    import asyncio

    print_stats()

    # Check for SSE mode
    if len(sys.argv) > 1 and sys.argv[1] == "sse":
        main_sse()
    else:
        asyncio.run(main_stdio())
