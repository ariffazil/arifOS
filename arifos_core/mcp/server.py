"""
arifOS MCP Server - Tool registry and dispatcher.

This module provides a minimal, framework-agnostic MCP server
that can be wrapped by any MCP host implementation.

Tools are registered in a simple registry and can be invoked
either directly or through the run_tool dispatcher.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from .models import (
    JudgeRequest,
    JudgeResponse,
    RecallRequest,
    RecallResponse,
    AuditRequest,
    AuditResponse,
    ApexLlamaRequest,
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


# =============================================================================
# TOOL REGISTRY
# =============================================================================

# Map of tool name -> callable
TOOLS: Dict[str, Callable] = {
    "arifos_judge": arifos_judge,
    "arifos_recall": arifos_recall,
    "arifos_audit": arifos_audit,
    "arifos_fag_read": arifos_fag_read,
    # APEX_LLAMA: local Llama via Ollama (unguarded raw model)
    "APEX_LLAMA": apex_llama,
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
        result = tool_fn(**payload)

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
            "version": self.version,
            "description": (
                "arifOS Constitutional Governance MCP Server. "
                "Provides tools for judging queries, recalling memories, "
                "and auditing the governance ledger."
            ),
            "tools": list(TOOLS.keys()),
        }


# Default server instance
mcp_server = MCPServer()
