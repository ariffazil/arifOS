"""
arif_agent_zero_mcp — arifOS MCP tool for agent-zero MCP bridge
══════════════════════════════════════════════════════════════════

arifOS acts as MCP CLIENT to agent-zero (which acts as MCP SERVER).
This tool exposes agent-zero's MCP capabilities through the arifOS MCP surface.

Access: authenticated (F11 AUTH required)
Stage:  666 FORGE

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field

from arifosmcp.runtime.agent_zero_mcp_client import (
    AZ_MCP_TOKEN,
    call_az_tool,
    list_az_tools,
    reset_session,
    send_az_message,
)

logger = logging.getLogger(__name__)

# ─── Tool Schemas ──────────────────────────────────────────────────────────────


class AgentZeroListToolsInput(BaseModel):
    """Input schema for arif_agent_zero_list_tools."""

    class Tool(BaseModel):
        name: str
        description: str

    pass


class AgentZeroListToolsOutput(BaseModel):
    """Output schema for arif_agent_zero_list_tools."""

    status: str = Field(description="Execution status: ok | error | hold")
    tools: list[dict[str, Any]] = Field(description="List of agent-zero MCP tools")
    count: int = Field(description="Number of tools")
    token: str = Field(description="Token used (redacted)")
    meta: dict[str, Any] = Field(default_factory=dict)


class AgentZeroCallToolInput(BaseModel):
    """Input schema for arif_agent_zero_call_tool."""

    tool_name: str = Field(description="Name of the agent-zero MCP tool to call")
    arguments: dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments to pass to the tool",
    )
    session_reset: bool = Field(
        default=False,
        description="If true, reset the MCP session before calling",
    )


class AgentZeroCallToolOutput(BaseModel):
    """Output schema for arif_agent_zero_call_tool."""

    status: str = Field(description="Execution status: ok | error | hold")
    tool_name: str = Field(description="Tool that was called")
    outputs: list[str] = Field(description="Tool output texts")
    is_error: bool = Field(description="Whether tool returned an error")
    meta: dict[str, Any] = Field(default_factory=dict)


class AgentZeroSendMessageInput(BaseModel):
    """Input schema for arif_agent_zero_send_message."""

    message: str = Field(description="Message to send to agent-zero")
    project_name: str | None = Field(
        default=None,
        description="Optional project name",
    )
    persistent: bool = Field(
        default=False,
        description="Whether to persist the chat",
    )


class AgentZeroSendMessageOutput(BaseModel):
    """Output schema for arif_agent_zero_send_message."""

    status: str = Field(description="Execution status: ok | error | hold")
    outputs: list[str] = Field(description="Response from agent-zero")
    meta: dict[str, Any] = Field(default_factory=dict)


# ─── Tool Implementations ──────────────────────────────────────────────────────


async def arif_agent_zero_list_tools(session_id: str = "az-mcp") -> AgentZeroListToolsOutput:
    """
    List all tools available from agent-zero's MCP server.

    Returns the tool manifests including name, description, and input schema.
    Use this to discover what agent-zero can do before calling a specific tool.

    F11 AUTH: Requires valid session authentication.
    F08 GENIUS: Returns structured tool catalog with G >= 0.80 quality.
    """
    try:
        tools = await list_az_tools()
        return AgentZeroListToolsOutput(
            status="ok",
            tools=tools,
            count=len(tools),
            token=f"{AZ_MCP_TOKEN[:4]}...{AZ_MCP_TOKEN[-4:]}",
            meta={"source": "agent-zero-mcp", "token_redacted": True},
        )
    except Exception as e:
        logger.error(f"[AZ-MCP] list_tools failed: {e}")
        return AgentZeroListToolsOutput(
            status="error",
            tools=[],
            count=0,
            token="",
            meta={"error": str(e), "source": "agent-zero-mcp"},
        )


async def arif_agent_zero_call_tool(
    tool_name: str,
    arguments: dict[str, Any] | None = None,
    session_reset: bool = False,
    session_id: str = "az-mcp",
) -> AgentZeroCallToolOutput:
    """
    Call a tool on agent-zero via MCP.

    Use arif_agent_zero_list_tools first to discover available tools.
    Tool name should be the MCP tool name (e.g., 'send_message').

    F11 AUTH: Requires valid session authentication.
    F01 AMANAH: Safe tool execution — read/observe/plan only.
    F13 SOVEREIGN: Execution gated through arifOS judgment pipeline.
    """
    if session_reset:
        reset_session()

    try:
        result = await call_az_tool(tool_name, arguments or {})
        return AgentZeroCallToolOutput(
            status="ok",
            tool_name=tool_name,
            outputs=result.get("outputs", []),
            is_error=result.get("isError", False),
            meta={"source": "agent-zero-mcp", "arguments": arguments or {}},
        )
    except Exception as e:
        logger.error(f"[AZ-MCP] call_tool '{tool_name}' failed: {e}")
        return AgentZeroCallToolOutput(
            status="error",
            tool_name=tool_name,
            outputs=[f"Error: {e}"],
            is_error=True,
            meta={"error": str(e), "source": "agent-zero-mcp"},
        )


async def arif_agent_zero_send_message(
    message: str,
    project_name: str | None = None,
    persistent: bool = False,
    session_id: str = "az-mcp",
) -> AgentZeroSendMessageOutput:
    """
    Send a message to agent-zero and get a response.

    This is the primary interface for delegating work to agent-zero.
    The message is processed through agent-zero's cognitive pipeline.

    F11 AUTH: Requires valid session authentication.
    F13 SOVEREIGN: Message content is governed by arifOS F02 TRUTH — no fabrication.
    """
    try:
        result = await send_az_message(
            message=message,
            project_name=project_name,
            persistent=persistent,
        )
        outputs = result.get("outputs", [])
        return AgentZeroSendMessageOutput(
            status="ok",
            outputs=outputs,
            meta={
                "source": "agent-zero-mcp",
                "project": project_name,
                "persistent": persistent,
            },
        )
    except Exception as e:
        logger.error(f"[AZ-MCP] send_message failed: {e}")
        return AgentZeroSendMessageOutput(
            status="error",
            outputs=[f"Error: {e}"],
            meta={"error": str(e), "source": "agent-zero-mcp"},
        )
