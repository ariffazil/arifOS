"""
AAA MCP Server (v52.5.1-SEAL)
Artifact · Authority · Architecture

Authority: Muhammad Arif bin Fazil
Architecture: Unified Trinity Application Layer

The Application Layer for arifOS v52.
Provides 5 Trinity Tools: 000_init, agi_genius, asi_act, apex_judge, vault_999

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
)
from codebase.enforcement.governance.rate_limiter import get_rate_limiter
from codebase.mcp.mode_selector import get_mcp_mode, MCPMode
from codebase.mcp.constitutional_metrics import record_verdict
from codebase.enforcement.metrics import record_stage_metrics, record_verdict_metrics
from codebase.system.orchestrator.presenter import AAAMetabolizer
from codebase.mcp.tools.mcp_tools_v53 import (
    authorize, reason, evaluate, decide, seal
)
from dataclasses import asdict

logger = logging.getLogger(__name__)

# Initialize Presenter
presenter = AAAMetabolizer()

# =============================================================================
# TOOL DESCRIPTIONS
# =============================================================================

TOOL_DESCRIPTIONS: Dict[str, Dict[str, Any]] = {
    "init_000": {
        "name": "init_000",
        "description": "000 INIT: Full Constitutional Ignition & 7D Context Mapping. Triggers F1-F13 metabolic boot sequence.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["init", "gate", "reset", "validate"], "default": "init"},
                "query": {"type": "string", "description": "Greeting or query to ignite context (e.g. 'Im Arif')"},
                "session_id": {"type": "string"}
            }
        }
    },
    "agi_genius": {
        "name": "agi_genius",
        "description": "Mind Engine: SENSE → THINK → ATLAS → FORGE (F2, F6, F7)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["sense", "think", "reflect", "atlas", "forge", "evaluate", "full"]},
                "query": {"type": "string"},
                "session_id": {"type": "string"}
            },
            "required": ["action"]
        }
    },
    "asi_act": {
        "name": "asi_act",
        "description": "Heart Engine: EVIDENCE → EMPATHY → ACT (F3, F4, F5)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["evidence", "empathize", "align", "act", "witness", "evaluate", "full"]},
                "text": {"type": "string"},
                "session_id": {"type": "string"}
            },
            "required": ["action"]
        }
    },
    "apex_judge": {
        "name": "apex_judge",
        "description": "Soul Engine: EUREKA → JUDGE → PROOF (F1, F8, F9)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["eureka", "judge", "proof", "entropy", "parallelism", "full"]},
                "verdict": {
                    "type": "string",
                    "enum": ["SEAL", "PARTIAL", "SABAR", "VOID", "888_HOLD"],
                    "description": "Verdict to seal"
                },
                "query": {"type": "string"},
                "response": {"type": "string"},
                "session_id": {"type": "string"}
            },
            "required": ["action"]
        }
    },
    "vault_999": {
        "name": "vault_999",
        "description": "Immutable Seal & Governance IO (F1, F8)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["seal", "list", "read", "write", "propose"]},
                "session_id": {"type": "string"},
                "verdict": {"type": "string", "enum": ["SEAL", "PARTIAL", "SABAR", "VOID", "888_HOLD"], "default": "SEAL"},
                "target": {"type": "string", "enum": ["seal", "ledger", "canon", "fag", "tempa", "phoenix", "audit"]}
            },
            "required": ["action"]
        }
    },
    # =========================================================================
    # v53 HUMAN LANGUAGE TOOLS
    # =========================================================================
    "authorize": {
        "name": "authorize",
        "description": "Verify user identity, check rate limits, detect prompt injection. Call this FIRST.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The user's request text"},
                "user_token": {"type": "string", "description": "Ed25519 signature token"},
                "session_id": {"type": "string", "description": "Session ID"}
            },
            "required": ["query"]
        }
    },
    "reason": {
        "name": "reason",
        "description": "Perform logical analysis and chain-of-thought reasoning.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Question to reason about"},
                "context": {"type": "object", "description": "Prior session context"},
                "style": {"type": "string", "enum": ["standard", "detailed", "brief"]},
                "session_id": {"type": "string"}
            },
            "required": ["query", "session_id"]
        }
    },
    "evaluate": {
        "name": "evaluate",
        "description": "Check reasoning for harm, bias, and fairness issues.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "reasoning": {"type": "string", "description": "Response to evaluate"},
                "query": {"type": "string"},
                "session_id": {"type": "string"}
            },
            "required": ["reasoning", "query", "session_id"]
        }
    },
    "decide": {
        "name": "decide",
        "description": "Synthesize final verdict (Logic + Safety + Authority).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "reasoning": {"type": "string"},
                "safety_evaluation": {"type": "object"},
                "authority_check": {"type": "object"},
                "session_id": {"type": "string"},
                "urgency": {"type": "string", "enum": ["normal", "urgent", "crisis"]}
            },
            "required": ["query", "reasoning", "safety_evaluation", "authority_check", "session_id"]
        }
    },
    "seal": {
        "name": "seal",
        "description": "Record decision immutably in ledger.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "verdict": {"type": "string", "enum": ["APPROVE", "CONDITIONAL", "REJECT", "ESCALATE"]},
                "query": {"type": "string"},
                "response": {"type": "string"},
                "decision_data": {"type": "object"},
                "metadata": {"type": "object"}
            },
            "required": ["session_id", "verdict", "query", "response", "decision_data"]
        }
    }
}

TOOL_ROUTERS = {
    "init_000": bridge_init_router,
    "agi_genius": bridge_agi_router,
    "asi_act": bridge_asi_router,
    "apex_judge": bridge_apex_router,
    "vault_999": bridge_vault_router,
    # v53 Routers
    "authorize": authorize,
    "reason": reason,
    "evaluate": evaluate,
    "decide": decide,
    "seal": seal,
}

# =============================================================================
# SERVER FACTORY
# =============================================================================

def create_mcp_server(mode: Optional[MCPMode] = None) -> Server:
    """Create mode-aware arifOS MCP server."""
    if mode is None:
        mode = get_mcp_mode()
    
    server = Server(f"AAA-MCP-{mode.value}")

    @server.list_tools()
    async def list_tools() -> list[mcp.types.Tool]:
        return [
            mcp.types.Tool(
                name=name,
                description=desc["description"],
                inputSchema=desc["inputSchema"]
            )
            for name, desc in TOOL_DESCRIPTIONS.items()
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[mcp.types.TextContent]:
        router = TOOL_ROUTERS.get(name)
        if not router:
            return [mcp.types.TextContent(type="text", text=f"VOID: Unknown tool {name}")]

        # F11: Rate Limit Check
        session_id = arguments.get("session_id", "anonymous")
        limiter = get_rate_limiter()
        rate_result = limiter.check(name, session_id)
        
        if not rate_result.allowed:
            return [mcp.types.TextContent(
                type="text", 
                text=f"VOID: Rate limit exceeded ({rate_result.reason})"
            )]

        start = time.time()
        try:
            # v53 tools do not use 'action' param logic
            if name in ["authorize", "reason", "evaluate", "decide", "seal"]:
                result_obj = await router(**arguments)
                # Convert dataclass to dict if needed
                if hasattr(result_obj, "__dataclass_fields__"):
                     result = asdict(result_obj)
                else:
                     result = result_obj
            else:
                # v52 tools use action param
                action = arguments.pop("action", "full")
                result = await router(action=action, **arguments)
            
            # Record metrics
            duration = time.time() - start
            duration_ms = duration * 1000
            
            # 1. MCP Rolling Metrics
            record_verdict(
                tool=name,
                verdict=result.get("verdict", "UNKNOWN"),
                duration=duration,
                mode=mode.value
            )
            
            # 2. Core Prometheus Metrics
            record_stage_metrics(name, duration_ms)
            record_verdict_metrics(result.get("verdict", "UNKNOWN"))
            
            # Metabolize Result using Presenter (Human-Optimized Output)
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
    print(f"AAA MCP v52.5.1 starting in {mode.value} mode", file=sys.stderr)
    async with stdio_server() as (read_stream, write_stream):
        server = create_mcp_server(mode)
        await server.run(read_stream, write_stream, server.create_initialization_options())

async def main():
    """Main entry point for the MCP server."""
    await main_stdio()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())