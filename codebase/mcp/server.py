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
)
from codebase.enforcement.governance.rate_limiter import get_rate_limiter
from codebase.mcp.mode_selector import get_mcp_mode, MCPMode
from codebase.mcp.constitutional_metrics import record_verdict
from codebase.enforcement.metrics import record_stage_metrics, record_verdict_metrics
from codebase.system.orchestrator.presenter import AAAMetabolizer
from codebase.mcp.tools.mcp_tools_v53 import (
    authorize, reason, evaluate, decide, seal
)
# NEW: Constitutional Physics
from codebase.system.constitution import execute_constitutional_physics

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
        "description": "000 INIT: Full Constitutional Ignition & 7D Context Mapping.",
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
        "description": "Mind Engine: SENSE → THINK → ATLAS → FORGE",
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
        "description": "Heart Engine: EVIDENCE → EMPATHY → ACT",
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
        "description": "Soul Engine: EUREKA → JUDGE → PROOF",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["eureka", "judge", "proof", "entropy", "parallelism", "full"]},
                "verdict": {"type": "string", "enum": ["SEAL", "PARTIAL", "SABAR", "VOID", "888_HOLD"]},
                "query": {"type": "string"},
                "response": {"type": "string"},
                "session_id": {"type": "string"}
            },
            "required": ["action"]
        }
    },
    "vault_999": {
        "name": "vault_999",
        "description": "Immutable Seal & Governance IO",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["seal", "list", "read", "write", "propose"]},
                "session_id": {"type": "string"},
                "verdict": {"type": "string"},
                "target": {"type": "string"}
            },
            "required": ["action"]
        }
    },
    # v53 HUMAN LANGUAGE TOOLS
    "authorize": {
        "name": "authorize",
        "description": "Verify user identity. Call FIRST.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "user_token": {"type": "string"},
                "session_id": {"type": "string"}
            },
            "required": ["query"]
        }
    },
    "reason": {
        "name": "reason",
        "description": "Perform logical analysis.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "context": {"type": "object"},
                "style": {"type": "string"},
                "session_id": {"type": "string"}
            },
            "required": ["query", "session_id"]
        }
    },
    "evaluate": {
        "name": "evaluate",
        "description": "Check reasoning for safety.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "reasoning": {"type": "string"},
                "query": {"type": "string"},
                "session_id": {"type": "string"}
            },
            "required": ["reasoning", "query", "session_id"]
        }
    },
    "decide": {
        "name": "decide",
        "description": "Synthesize final verdict.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "reasoning": {"type": "string"},
                "safety_evaluation": {"type": "object"},
                "authority_check": {"type": "object"},
                "session_id": {"type": "string"}
            },
            "required": ["query", "reasoning", "safety_evaluation", "authority_check", "session_id"]
        }
    },
    "seal": {
        "name": "seal",
        "description": "Record decision immutably.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "verdict": {"type": "string"},
                "query": {"type": "string"},
                "response": {"type": "string"},
                "decision_data": {"type": "object"}
            },
            "required": ["session_id", "verdict", "query", "response", "decision_data"]
        }
    },
    "physics": {
        "name": "physics",
        "description": "Run Quantum Constitutional Physics (Kimi Orthogonal Directive).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "user_id": {"type": "string"}
            },
            "required": ["query"]
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
    # Physics
    "physics": execute_constitutional_physics,
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
            if name == "physics":
                # Special handling for physics (direct kwarg mapping)
                result = await router(
                    query=arguments.get("query", ""),
                    user_id=arguments.get("user_id", "anonymous")
                )
            elif name in ["authorize", "reason", "evaluate", "decide", "seal"]:
                result_obj = await router(**arguments)
                if hasattr(result_obj, "__dataclass_fields__"):
                     result = asdict(result_obj)
                else:
                     result = result_obj
            else:
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