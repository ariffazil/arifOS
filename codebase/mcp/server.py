"""
AAA MCP Server (v53.1.0-CODEBASE)
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
)
from codebase.enforcement.governance.rate_limiter import get_rate_limiter
from codebase.mcp.mode_selector import get_mcp_mode, MCPMode
from codebase.mcp.constitutional_metrics import record_verdict
from codebase.enforcement.metrics import record_stage_metrics, record_verdict_metrics
from codebase.system.orchestrator.presenter import AAAMetabolizer

logger = logging.getLogger(__name__)

# Initialize Presenter
presenter = AAAMetabolizer()

# =============================================================================
# TOOL DESCRIPTIONS (v53.2.0 - Simplified 6-Tool Architecture)
# =============================================================================

TOOL_DESCRIPTIONS: Dict[str, Dict[str, Any]] = {
    "init_000": {
        "name": "init_000",
        "description": "000 INIT: Constitutional Ignition, Identity Verification & Session Management. Actions: init (start session), gate (checkpoint), reset (clear session), validate (verify state), authorize (verify identity).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["init", "gate", "reset", "validate", "authorize"], "default": "init"},
                "query": {"type": "string", "description": "Greeting or query to ignite context"},
                "session_id": {"type": "string"},
                "user_token": {"type": "string", "description": "For authorize action"}
            }
        }
    },
    "agi_genius": {
        "name": "agi_genius",
        "description": "AGI Mind Engine (F2,F4,F7,F10): SENSE → THINK → REASON → FORGE. Actions: sense (perceive), think (deliberate), reflect (introspect), reason (logical analysis), atlas (knowledge mapping), forge (create), full (complete pipeline), physics (quantum constitutional).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["sense", "think", "reflect", "reason", "atlas", "forge", "full", "physics"]},
                "query": {"type": "string"},
                "session_id": {"type": "string"},
                "context": {"type": "object", "description": "Additional context for reasoning"}
            },
            "required": ["action"]
        }
    },
    "asi_act": {
        "name": "asi_act",
        "description": "ASI Heart Engine (F1,F5,F6,F9): EVIDENCE → EMPATHY → EVALUATE → ACT. Actions: evidence (gather facts), empathize (stakeholder analysis), evaluate (safety check), act (execute), stakeholder (semantic stakeholder reasoning), diffusion (impact propagation), audit (constitutional audit), full (complete pipeline).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["evidence", "empathize", "evaluate", "act", "witness", "stakeholder", "diffusion", "audit", "full"]},
                "text": {"type": "string"},
                "query": {"type": "string"},
                "session_id": {"type": "string"},
                "reasoning": {"type": "string", "description": "For evaluate action"},
                "stakeholder_graph": {"type": "object", "description": "For diffusion action"},
                "agi_context": {"type": "object", "description": "AGI output for chaining"}
            },
            "required": ["action"]
        }
    },
    "apex_judge": {
        "name": "apex_judge",
        "description": "APEX Soul Engine (F3,F8,F11,F12,F13): EUREKA → DECIDE → PROOF. Actions: eureka (insight), judge (evaluate), decide (synthesize verdict), proof (generate evidence), entropy (measure), full (complete pipeline).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["eureka", "judge", "decide", "proof", "entropy", "full"]},
                "verdict": {"type": "string", "enum": ["SEAL", "PARTIAL", "SABAR", "VOID", "888_HOLD"]},
                "query": {"type": "string"},
                "response": {"type": "string"},
                "session_id": {"type": "string"},
                "reasoning": {"type": "string", "description": "For decide action"},
                "safety_evaluation": {"type": "object", "description": "ASI evaluation for decide"},
                "authority_check": {"type": "object", "description": "Init authorization for decide"}
            },
            "required": ["action"]
        }
    },
    "vault_999": {
        "name": "vault_999",
        "description": "VAULT-999 Immutable Memory (F1,F8): Seal decisions, read/write governance artifacts. Actions: seal (immutable record), list (enumerate artifacts), read (retrieve), write (store), propose (suggest canon).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["seal", "list", "read", "write", "propose"]},
                "session_id": {"type": "string"},
                "verdict": {"type": "string"},
                "target": {"type": "string", "enum": ["seal", "ledger", "canon", "fag", "tempa", "phoenix", "audit"]},
                "query": {"type": "string"},
                "response": {"type": "string"},
                "decision_data": {"type": "object", "description": "Full decision payload for seal"}
            },
            "required": ["action"]
        }
    },
    "trinity_loop": {
        "name": "trinity_loop",
        "description": "Trinity Metabolic Loop: Complete AGI→ASI→APEX→VAULT pipeline in one call. Runs full constitutional governance cycle.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "User query to process"},
                "session_id": {"type": "string"}
            },
            "required": ["query"]
        }
    }
}

# =============================================================================
# TOOL ROUTERS (v53.2.0 - Simplified 6-Tool Architecture)
# =============================================================================

TOOL_ROUTERS = {
    "init_000": bridge_init_router,
    "agi_genius": bridge_agi_router,
    "asi_act": bridge_asi_router,
    "apex_judge": bridge_apex_router,
    "vault_999": bridge_vault_router,
    "trinity_loop": bridge_trinity_loop_router,
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

        # Rate Limit Check
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
            if name == "trinity_loop":
                # Trinity loop doesn't use action pattern - direct kwargs
                result = await router(**arguments)
            else:
                # Standard tools use action pattern
                action = arguments.pop("action", "full")
                result = await router(action=action, **arguments)
            
            duration = time.time() - start
            duration_ms = duration * 1000
            
            record_verdict(
                tool=name,
                verdict=result.get("verdict", "UNKNOWN"),
                duration=duration,
                mode=mode.value
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