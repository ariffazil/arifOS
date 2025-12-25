"""
arifOS MCP Server - Tool registry and dispatcher.

This module provides a minimal, framework-agnostic MCP server
that can be wrapped by any MCP host implementation.

Tools are registered in a simple registry and can be invoked
either directly or through the run_tool dispatcher.
"""

from __future__ import annotations

import sys
from typing import Any, Callable, Dict, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server

from .models import (
    JudgeRequest,
    JudgeResponse,
    RecallRequest,
    RecallResponse,
    AuditRequest,
    AuditResponse,
    ApexLlamaRequest,
    VerdictResponse,
)
from .tools.judge import arifos_judge
from .tools.recall import arifos_recall
from .tools.audit import arifos_audit
from .tools.fag_read import (
    arifos_fag_read,
    FAGReadRequest,
    FAGReadResponse,
    TOOL_METADATA as FAG_METADATA,
)
from .tools.apex_llama import apex_llama

# Phase 1-3 MCP Tools (Constitutional Pipeline)
from .tools import (
    mcp_000_reset_sync,
    mcp_111_sense_sync,
    mcp_222_reflect_sync,
    mcp_444_evidence_sync,
    mcp_555_empathize_sync,
    mcp_666_align_sync,
    mcp_777_forge_sync,
    mcp_888_judge_sync,
    mcp_889_proof_sync,
    mcp_999_seal_sync,
)


# =============================================================================
# TOOL REGISTRY
# =============================================================================

# Map of tool name -> callable
TOOLS: Dict[str, Callable] = {
    # Legacy tools
    "arifos_judge": arifos_judge,
    "arifos_recall": arifos_recall,
    "arifos_audit": arifos_audit,
    "arifos_fag_read": arifos_fag_read,
    "APEX_LLAMA": apex_llama,

    # Phase 1-3 Constitutional Pipeline
    "mcp_000_reset": mcp_000_reset_sync,
    "mcp_111_sense": mcp_111_sense_sync,
    "mcp_222_reflect": mcp_222_reflect_sync,
    "mcp_444_evidence": mcp_444_evidence_sync,
    "mcp_555_empathize": mcp_555_empathize_sync,
    "mcp_666_align": mcp_666_align_sync,
    "mcp_777_forge": mcp_777_forge_sync,
    "mcp_888_judge": mcp_888_judge_sync,
    "mcp_889_proof": mcp_889_proof_sync,
    "mcp_999_seal": mcp_999_seal_sync,
}

# Map of tool name -> request model class (for payload conversion)
TOOL_REQUEST_MODELS: Dict[str, type] = {
    "arifos_judge": JudgeRequest,
    "arifos_recall": RecallRequest,
    "arifos_audit": AuditRequest,
    "arifos_fag_read": FAGReadRequest,
    "APEX_LLAMA": ApexLlamaRequest,
}

# Tool descriptions for MCP discovery
TOOL_DESCRIPTIONS: Dict[str, Dict[str, Any]] = {
    "arifos_judge": {
        "name": "arifos_judge",
        "description": (
            "Judge a query through the arifOS governed pipeline. "
            "Returns a verdict (SEAL/PARTIAL/VOID/SABAR/888_HOLD) "
            "based on 9 constitutional floors."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query to judge",
                },
                "user_id": {
                    "type": "string",
                    "description": "Optional user ID for context",
                },
            },
            "required": ["query"],
        },
    },
    "arifos_recall": {
        "name": "arifos_recall",
        "description": (
            "Recall relevant memories from L7 (Mem0 + Qdrant). "
            "All recalled memories are capped at 0.85 confidence. "
            "Memories are suggestions, not facts (INV-4)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "User ID for memory isolation",
                },
                "prompt": {
                    "type": "string",
                    "description": "Query prompt for semantic search",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum memories to return (default: 5)",
                    "default": 5,
                },
            },
            "required": ["user_id", "prompt"],
        },
    },
    "arifos_audit": {
        "name": "arifos_audit",
        "description": (
            "Retrieve audit/ledger data for a user. "
            "STUB: Full implementation coming in future sprint."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "User ID to audit",
                },
                "days": {
                    "type": "integer",
                    "description": "Days to look back (default: 7)",
                    "default": 7,
                },
            },
            "required": ["user_id"],
        },
    },
    "arifos_fag_read": FAG_METADATA,
    "APEX_LLAMA": {
        "name": "APEX_LLAMA",
        "description": (
            "Call local Llama via Ollama and return the raw model output. "
            "This is an un-governed helper; use arifos_judge to cage it."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Prompt to send to the Llama model",
                },
                "model": {
                    "type": "string",
                    "description": "Ollama model name (e.g. llama3, llama3:8b)",
                    "default": "llama3",
                },
                "max_tokens": {
                    "type": "integer",
                    "description": "Maximum tokens to generate",
                    "default": 512,
                },
            },
            "required": ["prompt"],
        },
    },

    # =========================================================================
    # PHASE 1-3 CONSTITUTIONAL PIPELINE TOOLS
    # =========================================================================

    "mcp_000_reset": {
        "name": "mcp_000_reset",
        "description": (
            "Initialize a new governance session. Generates a session ID, "
            "clears active memory, and sets up the metabolic pipeline. "
            "Constitutional: F1 (Amanah) - session initialization. "
            "Always returns PASS."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "Optional session ID (generated if not provided)",
                },
            },
        },
    },

    "mcp_111_sense": {
        "name": "mcp_111_sense",
        "description": (
            "Lane classification and truth threshold determination. "
            "Classifies queries into HARD (factual), SOFT (explanatory), "
            "PHATIC (social), or REFUSE (harmful/violations). "
            "Constitutional: F2 (Truth) - determines required threshold. "
            "Always returns PASS."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Query to classify",
                },
            },
            "required": ["query"],
        },
    },

    "mcp_222_reflect": {
        "name": "mcp_222_reflect",
        "description": (
            "Omega0 prediction for epistemic honesty. Predicts uncertainty "
            "band (Omega0) based on confidence and generates humility annotations. "
            "Constitutional: F7 (Humility) - uncertainty disclosure. "
            "Always returns PASS."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Query being evaluated",
                },
                "confidence": {
                    "type": "number",
                    "description": "Confidence score [0.0, 1.0]",
                },
            },
            "required": ["query", "confidence"],
        },
    },

    "mcp_444_evidence": {
        "name": "mcp_444_evidence",
        "description": (
            "Truth grounding via tri-witness convergence (HUMAN-AI-EARTH). "
            "Validates claims against sources, detects hallucinations, "
            "generates cryptographic proof hashes. "
            "Constitutional: F2 (Truth), F3 (Tri-Witness). "
            "Returns: PASS, PARTIAL, or VOID."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "claim": {
                    "type": "string",
                    "description": "Claim to validate",
                },
                "sources": {
                    "type": "array",
                    "description": "Evidence sources (witness, id, score, text)",
                    "items": {"type": "object"},
                },
                "lane": {
                    "type": "string",
                    "description": "Truth lane (HARD/SOFT/PHATIC)",
                },
            },
            "required": ["claim", "sources", "lane"],
        },
    },

    "mcp_555_empathize": {
        "name": "mcp_555_empathize",
        "description": (
            "Power-aware recalibration (Peace^2 and kappa_r). Detects dismissive "
            "or aggressive tone, calculates peace score, adjusts for power "
            "dynamics. Constitutional: F5 (Peace^2), F6 (kappa_r/Empathy). "
            "Returns: PASS or PARTIAL (never VOID)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "response_text": {
                    "type": "string",
                    "description": "Response text to evaluate",
                },
                "recipient_context": {
                    "type": "object",
                    "description": "Recipient context (audience_level, power_level, etc.)",
                },
            },
            "required": ["response_text"],
        },
    },

    "mcp_666_align": {
        "name": "mcp_666_align",
        "description": (
            "ABSOLUTE VETO GATES for constitutional violations. "
            "Detects F1 (credential exposure, deception), F8 (low GENIUS, "
            "high C_dark), F9 (consciousness claims). NO PARTIAL - only "
            "PASS or VOID. Constitutional firewall before execution."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "User query",
                },
                "execution_plan": {
                    "type": "object",
                    "description": "Execution plan to validate",
                },
                "metrics": {
                    "type": "object",
                    "description": "GENIUS metrics (G, C_dark)",
                },
                "draft_text": {
                    "type": "string",
                    "description": "Draft response text",
                },
            },
            "required": ["query", "execution_plan", "metrics", "draft_text"],
        },
    },

    "mcp_777_forge": {
        "name": "mcp_777_forge",
        "description": (
            "Clarity refinement and humility injection. Detects contradictions, "
            "improves clarity (reduces entropy), injects humility markers "
            "based on Omega0. Constitutional: F4 (DeltaS/Clarity), F7 (Humility). "
            "Always returns PASS."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "draft_response": {
                    "type": "string",
                    "description": "Draft response to refine",
                },
                "omega_zero": {
                    "type": "number",
                    "description": "Omega0 uncertainty band",
                },
            },
            "required": ["draft_response", "omega_zero"],
        },
    },

    "mcp_888_judge": {
        "name": "mcp_888_judge",
        "description": (
            "Final verdict aggregation via decision tree. Aggregates verdicts "
            "from tools 222-777, applies veto cascade (any VOID -> VOID), "
            "emits SEAL (all PASS), PARTIAL (any PARTIAL), or VOID. "
            "Constitutional judiciary - final decision maker."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "verdicts": {
                    "type": "object",
                    "description": "Dict of tool_id -> verdict",
                },
            },
            "required": ["verdicts"],
        },
    },

    "mcp_889_proof": {
        "name": "mcp_889_proof",
        "description": (
            "Generate cryptographic proof (Merkle tree) of verdict chain. "
            "Creates SHA-256 proof hash, builds Merkle path, validates proof. "
            "Constitutional: F2 (Truth - proves no hallucination), "
            "F4 (Clarity - transparent). Always returns PASS."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "verdict_chain": {
                    "type": "array",
                    "description": "List of verdict strings ['222:PASS', '444:PASS', ...]",
                    "items": {"type": "string"},
                },
                "decision_tree": {
                    "type": "object",
                    "description": "Decision tree with tool metadata",
                },
                "claim": {
                    "type": "string",
                    "description": "Claim being proved",
                },
            },
            "required": ["verdict_chain"],
        },
    },

    "mcp_999_seal": {
        "name": "mcp_999_seal",
        "description": (
            "Final verdict sealing and memory routing. Creates base64 seal, "
            "generates audit log ID, routes to memory location, validates seal. "
            "Constitutional: F1 (Amanah - audit trail), F9 (Anti-Hantu - "
            "timestamps). Always returns PASS."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "verdict": {
                    "type": "string",
                    "description": "Final verdict (SEAL/PARTIAL/VOID/SABAR/HOLD)",
                },
                "proof_hash": {
                    "type": "string",
                    "description": "SHA-256 proof hash from Tool 889",
                },
                "decision_metadata": {
                    "type": "object",
                    "description": "Decision metadata (query, response, floor_verdicts)",
                },
            },
            "required": ["verdict", "proof_hash"],
        },
    },
}


# =============================================================================
# SERVER FUNCTIONS
# =============================================================================

def list_tools() -> Dict[str, Callable]:
    """
    List all available MCP tools.

    Returns:
        Dict mapping tool names to their callable implementations
    """
    return TOOLS.copy()


def get_tool_descriptions() -> Dict[str, Dict[str, Any]]:
    """
    Get tool descriptions for MCP discovery.

    Returns:
        Dict mapping tool names to their JSON Schema descriptions
    """
    return TOOL_DESCRIPTIONS.copy()


def run_tool(name: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Run a tool by name with the given payload.

    This is the main dispatcher for MCP tool invocations.
    It converts the payload to the appropriate request model,
    calls the tool function, and returns the response as a dict.

    Args:
        name: Tool name (e.g., "arifos_judge")
        payload: Dict with tool parameters

    Returns:
        Response as a dict, or None if tool not found

    Raises:
        ValueError: If tool name is not found
        Exception: If tool execution fails
    """
    if name not in TOOLS:
        raise ValueError(f"Unknown tool: {name}. Available: {list(TOOLS.keys())}")

    tool_fn = TOOLS[name]
    request_model = TOOL_REQUEST_MODELS.get(name)

    # Convert payload to request model if available
    if request_model:
        request = request_model(**payload)
        result = tool_fn(request)
    else:
        # MCP tools expect a dict as single argument
        result = tool_fn(payload)

    # Convert response to dict
    if hasattr(result, "model_dump"):
        return result.model_dump()
    elif hasattr(result, "dict"):
        return result.dict()
    else:
        return dict(result) if result else None


# =============================================================================
# MCP-READY INTERFACE
# =============================================================================

class MCPServer:
    """
    MCP-ready server class.

    This class provides a structured interface that can be wrapped
    by an MCP SDK or host implementation.

    Usage:
        server = MCPServer()
        tools = server.list_tools()
        result = server.call_tool("arifos_judge", {"query": "What is Amanah?"})
    """

    def __init__(self) -> None:
        self.name = "arifos-mcp"
        self.version = "0.1.0"

    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        """List available tools with their descriptions."""
        return get_tool_descriptions()

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool by name.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result as dict
        """
        result = run_tool(name, arguments)
        return result if result else {"error": "No result"}

    def get_info(self) -> Dict[str, Any]:
        """Get server information."""
        return {
            "name": self.name,
            "version": "1.0.0",
            "description": (
                "arifOS Constitutional Governance MCP Server. "
                "Provides 15 tools: 5 legacy (judge, recall, audit, fag_read, APEX_LLAMA) "
                "+ 10 constitutional pipeline tools (000->999) for real-time governance. "
                "All tools enforce the 9 Constitutional Floors (F1-F9). "
                "Complete audit trail with cryptographic proofs (Merkle tree + SHA-256)."
            ),
            "tools": list(TOOLS.keys()),
            "tool_count": len(TOOLS),
            "phases": {
                "legacy": ["arifos_judge", "arifos_recall", "arifos_audit", "arifos_fag_read", "APEX_LLAMA"],
                "phase_1": ["mcp_000_reset", "mcp_111_sense"],
                "phase_2": ["mcp_222_reflect", "mcp_444_evidence", "mcp_555_empathize",
                           "mcp_666_align", "mcp_777_forge", "mcp_888_judge"],
                "phase_3": ["mcp_889_proof", "mcp_999_seal"],
            },
        }

    async def run_stdio(self) -> None:
        """
        Run the MCP server using stdio transport.

        This method initializes the MCP SDK server, registers all 15 tools,
        and runs the stdio transport for IDE integration (VSCode/Cursor).

        Constitutional: F1 (Amanah) - Clean session lifecycle with graceful shutdown.
        """
        from mcp import types

        # Create MCP Server instance
        server = Server(self.name)

        # Get tool descriptions
        tool_descriptions = get_tool_descriptions()

        # Register list_tools handler
        @server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List all available tools."""
            tools = []
            for tool_name, tool_desc in tool_descriptions.items():
                tools.append(
                    types.Tool(
                        name=tool_name,
                        description=tool_desc.get("description", ""),
                        inputSchema=tool_desc.get("parameters", {})
                    )
                )
            return tools

        # Register call_tool handler
        @server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict
        ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """Execute tool and return result."""
            result = run_tool(name, arguments)
            if not result:
                result = {"error": f"Tool {name} returned no result"}

            # Convert result to JSON string for TextContent
            import json
            result_text = json.dumps(result, indent=2)

            return [types.TextContent(type="text", text=result_text)]

        # Run stdio transport
        print(f"[arifOS MCP] Starting server: {self.name} v1.0.0", file=sys.stderr)
        print(f"[arifOS MCP] Tools registered: {len(tool_descriptions)}", file=sys.stderr)
        print("[arifOS MCP] Stdio transport active. Ready for IDE connection.", file=sys.stderr)

        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )


# Default server instance
mcp_server = MCPServer()
