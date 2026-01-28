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
    bridge_reality_check_router,
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
    "INIT": {
        "name": "INIT",
        "description": (
            "Session initialization, authority verification, and budget allocation. "
            "Call this FIRST before using any other tool. "
            "Fail-closed access control and resource management. "
            "\n\nActions: "
            "init — Start a new session (default). "
            "gate — Run a safety checkpoint mid-session. "
            "reset — End current session and clear state. "
            "validate — Verify the session is still valid. "
            "authorize — Confirm identity with a token."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["init", "gate", "reset", "validate", "authorize"],
                    "default": "init",
                    "description": "Action primitive: init, gate, reset, validate, or authorize."
                },
                "query": {
                    "type": "string",
                    "description": "The user's greeting or initial message. Used to detect identity and intent."
                },
                "session_id": {
                    "type": "string",
                    "description": "Existing session ID. Required for gate, reset, and validate actions."
                },
                "user_token": {
                    "type": "string",
                    "description": "Identity token for the authorize action. Proves who is speaking."
                }
            }
        }
    },
    "AGI": {
        "name": "AGI",
        "description": (
            "Deep reasoning and pattern recognition (Mind Engine). "
            "Handles logic, analysis, knowledge retrieval (including Context7), and content creation. "
            "\n\nRules enforced: "
            "(1) Every claim must be factually accurate. "
            "(2) Clarity is mandatory (ΔS). "
            "(3) Uncertainty must be stated honestly (Ω₀). "
            "\n\nActions: "
            "sense — Perceive and parse input. "
            "think — Deep deliberation. "
            "reflect — Meta-cognition check. "
            "reason — Step-by-step logic. "
            "atlas — Knowledge mapping (includes docs). "
            "forge — Solve or create content. "
            "full — Run complete pipeline. "
            "physics — Apply rule-checking."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["sense", "think", "reflect", "reason", "atlas", "forge", "full", "physics"],
                    "description": "Which thinking step to run."
                },
                "query": {
                    "type": "string",
                    "description": "The question or topic to process."
                },
                "session_id": {
                    "type": "string",
                    "description": "Session ID from INIT."
                },
                "context": {
                    "type": "object",
                    "description": "Extra context for reasoning."
                }
            },
            "required": ["action"]
        }
    },
    "ASI": {
        "name": "ASI",
        "description": (
            "Safety, bias, and empathy audit (Heart Engine). "
            "Evaluates whether an action is safe, fair, and reversible. "
            "\n\nRules enforced: "
            "(1) Actions must be reversible. "
            "(2) The weakest stakeholder must be protected. "
            "(3) No deceptive cleverness (F9 Anti-Hantu). "
            "\n\nActions: "
            "evidence — Gather facts. "
            "empathize — Impact assessment. "
            "evaluate — Safety check. "
            "act — Execute approved action. "
            "witness — Record audit event. "
            "stakeholder — Deep analysis. "
            "diffusion — Impact propagation. "
            "audit — Compliance review. "
            "full — Run complete pipeline."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["evidence", "empathize", "evaluate", "act", "witness", "stakeholder", "diffusion", "audit", "full"],
                    "description": "Which safety step to run."
                },
                "text": {
                    "type": "string",
                    "description": "The text or content to evaluate."
                },
                "query": {
                    "type": "string",
                    "description": "The context or action."
                },
                "session_id": {
                    "type": "string",
                    "description": "Session ID from INIT."
                },
                "reasoning": {
                    "type": "string",
                    "description": "Stakeholder reasoning for evaluation."
                },
                "agi_context": {
                    "type": "object",
                    "description": "AGI output for evaluation chaining."
                }
            },
            "required": ["action"]
        }
    },
    "APEX": {
        "name": "APEX",
        "description": (
            "Judicial consensus and final verdict (Soul Engine). "
            "The final approval or rejection decision after AGI and ASI have completed. "
            "\n\nVerdicts: "
            "SEAL — Approved. All checks passed. "
            "PARTIAL — Approved with warnings. "
            "VOID — Rejected. Rule broken. "
            "888_HOLD — Paused for review. "
            "SABAR — Stopped for violation. "
            "\n\nActions: "
            "eureka — Combined insight. "
            "judge — Evaluate response. "
            "decide — Synthesize final verdict. "
            "proof — Generate evidence. "
            "entropy — Measure clarity gain. "
            "full — Run complete pipeline."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["eureka", "judge", "decide", "proof", "entropy", "full"],
                    "description": "Which judgment step to run."
                },
                "verdict": {
                    "type": "string",
                    "enum": ["SEAL", "PARTIAL", "SABAR", "VOID", "888_HOLD"],
                    "description": "The proposed constitutional verdict."
                },
                "query": {
                    "type": "string",
                    "description": "The original request."
                },
                "response": {
                    "type": "string",
                    "description": "The proposed output."
                },
                "session_id": {
                    "type": "string",
                    "description": "Session ID from INIT."
                },
                "reasoning": {
                    "type": "string",
                    "description": "Verbal reasoning for decision."
                },
                "safety_evaluation": {
                    "type": "object",
                    "description": "ASI evaluation context."
                }
            },
            "required": ["action"]
        }
    },
    "VAULT": {
        "name": "VAULT",
        "description": (
            "Immutable ledger and audit trail (Resources). "
            "Permanent storage in tamper-proof log (Merkle-tree sealed). "
            "\n\nRules enforced: "
            "(1) Significant decisions are recorded. "
            "(2) Records are permanent. "
            "(3) Provable audit chain (F1 Amanah). "
            "\n\nActions: "
            "seal — Permanently record decision. "
            "list — Enumerate artifacts. "
            "read — Retrieve record. "
            "write — Create draft artifact. "
            "propose — Suggest rule change."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["seal", "list", "read", "write", "propose"],
                    "description": "Archival action."
                },
                "session_id": {
                    "type": "string",
                    "description": "Session ID from INIT."
                },
                "verdict": {
                    "type": "string",
                    "description": "Verdict to seal."
                },
                "target": {
                    "type": "string",
                    "enum": ["seal", "ledger", "canon", "fag", "tempa", "phoenix", "audit"],
                    "description": "Vault destination."
                },
                "decision_data": {
                    "type": "object",
                    "description": "Complete proof payload for sealing."
                }
            },
            "required": ["action"]
        }
    },
    "TRINITY": {
        "name": "TRINITY",
        "description": (
            "Full metabolic loop AGI→ASI→APEX→VAULT (Tools + Resources). "
            "Runs the complete constitutional cycle in a single call. "
            "\n\nStructure: "
            "(1) AGI Reason. (2) ASI Evaluate. (3) APEX Judge. (4) VAULT Record. "
            "\n\nRules: All 13 floors strictly enforced. Strictly governed path."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The request to process through the full pipeline."
                },
                "session_id": {
                    "type": "string",
                    "description": "Session ID from INIT."
                }
            },
            "required": ["query"]
        }
    },
    "REALITY": {
        "name": "REALITY",
        "description": (
            "Fact-checking via external sources (Brave Search / Grounding). "
            "Live internet fact-check with F7 Humility disclosure. "
            "\n\nRules: "
            "(1) Data labeled as external. "
            "(2) Sources cited. "
            "(3) Honestly state when results are uncertain."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Question requiring external verification."
                },
                "session_id": {
                    "type": "string",
                    "description": "Session ID from INIT."
                }
            },
            "required": ["query"]
        }
    },
}

# =============================================================================
# TOOL ROUTERS (v53.2.7 — 7-Tool Constitutional Architecture)
# =============================================================================

TOOL_ROUTERS = {
    "INIT": bridge_init_router,
    "AGI": bridge_agi_router,
    "ASI": bridge_asi_router,
    "APEX": bridge_apex_router,
    "VAULT": bridge_vault_router,
    "TRINITY": bridge_trinity_loop_router,
    "REALITY": bridge_reality_check_router,
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
            if name in ["TRINITY", "REALITY"]:
                # These tools don't use action pattern - direct kwargs
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