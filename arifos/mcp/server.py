"""
arifOS MCP Server (v52.0.0)
Authority: Muhammad Arif bin Fazil
Architecture: Unified Trinity Application Layer

The Application Layer for arifOS v52.
Supports both BRIDGE mode (production) and STANDALONE mode (dev).

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

from arifos.mcp.bridge import (
    bridge_init_router,
    bridge_agi_router,
    bridge_asi_router,
    bridge_apex_router,
    bridge_vault_router,
)
from arifos.core.enforcement.governance.rate_limiter import get_rate_limiter
from arifos.mcp.mode_selector import get_mcp_mode, MCPMode
from arifos.mcp.constitutional_metrics import record_verdict
from arifos.core.enforcement.metrics import record_stage_metrics, record_verdict_metrics
from arifos.core.system.orchestrator.presenter import AAAMetabolizer

logger = logging.getLogger(__name__)

# Initialize Presenter
presenter = AAAMetabolizer()

# =============================================================================
# TOOL DESCRIPTIONS
# =============================================================================

TOOL_DESCRIPTIONS: Dict[str, Dict[str, Any]] = {
    "000_init": {
        "name": "000_init",
        "description": "System Ignition & Constitutional Gateway (F1, F11, F12)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["init", "gate", "reset", "validate"], "default": "init"},
                "query": {"type": "string"},
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
                "query": {"type": "string"},
                "response": {"type": "string"},
                "session_id": {"type": "string"}
            },
            "required": ["action"]
        }
    },
    "999_vault": {
        "name": "999_vault",
        "description": "Immutable Seal & Governance IO (F1, F8)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["seal", "list", "read", "write", "propose"]},
                "session_id": {"type": "string"},
                "target": {"type": "string", "enum": ["seal", "ledger", "canon", "fag", "tempa", "phoenix", "audit"]}
            },
            "required": ["action"]
        }
    }
}

TOOL_ROUTERS = {
    "000_init": bridge_init_router,
    "agi_genius": bridge_agi_router,
    "asi_act": bridge_asi_router,
    "apex_judge": bridge_apex_router,
    "999_vault": bridge_vault_router,
}

# =============================================================================
# SERVER FACTORY
# =============================================================================

def create_mcp_server(mode: Optional[MCPMode] = None) -> Server:
    """Create mode-aware arifOS MCP server."""
    if mode is None:
        mode = get_mcp_mode()
    
    server = Server(f"arifOS-MCP-{mode.value}")

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
            # Extract action
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
    print(f"arifOS MCP v52.0.0 starting in {mode.value} mode", file=sys.stderr)
    async with stdio_server() as (read_stream, write_stream):
        server = create_mcp_server(mode)
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main_stdio())