import json
import os
from typing import List

from fastapi import APIRouter, BackgroundTasks, HTTPException

from arifos.core.integration.composio_client import composio_client

from .governance import postflight_check, preflight_check
from .models import (
    FloorScore,
    GovernanceVerdict,
    ToolAttribute,
    ToolCallRequest,
    ToolCallResponse,
    ToolListResponse,
)

router = APIRouter(prefix="/mcp")

# Load configuration
CONFIG_PATH = os.path.join(os.getcwd(), "config", "mcp_allowed_tools.json")

def get_allowed_tools() -> List[str]:
    if not os.path.exists(CONFIG_PATH):
        return []
    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)
        return data.get("allowed_tools", [])

@router.post("/tools/list", response_model=ToolListResponse)
async def list_tools():
    """List available, allowlisted Composio tools."""
    allowed_names = get_allowed_tools()

    # Fetch tools from Composio Client
    raw_tools = await composio_client.list_tools(filter_apps=allowed_names)

    tools = []
    for t in raw_tools:
        tools.append(ToolAttribute(
            name=t["name"],
            description=t["description"],
            input_schema=t["input_schema"]
        ))

    return ToolListResponse(tools=tools)

@router.post("/tools/call", response_model=ToolCallResponse)
async def call_tool(request: ToolCallRequest):
    """
    Execute a tool call with strict governance.
    Turn 1: Preflight (Risk/Injection) -> 888_HOLD if dangerous.
    Turn 2: Execution (Composio).
    Turn 3: Postflight (Truth/Hantu).
    """
    allowed_tools = get_allowed_tools()

    # 1. Preflight
    pre_verdict = await preflight_check(request, allowed_tools)

    if pre_verdict.verdict == "VOID":
        return ToolCallResponse(
            tool_name=request.tool_name,
            status="error",
            governance=pre_verdict,
            error=pre_verdict.consequences
        )

    if pre_verdict.verdict == "888_HOLD":
        return ToolCallResponse(
            tool_name=request.tool_name,
            status="governed_halt",
            governance=pre_verdict,
            error="Human approval required. Use /approve endpoint."
        )

    # 2. Execution
    try:
        tool_output = await composio_client.execute_tool(request.tool_name, request.arguments)
    except Exception as e:
         return ToolCallResponse(
            tool_name=request.tool_name,
            status="error",
            governance=GovernanceVerdict(verdict="VOID", floor_scores=[]),
            error=f"Execution Failed: {str(e)}"
        )

    # 3. Postflight
    post_verdict = await postflight_check(request.tool_name, tool_output)

    if post_verdict.verdict == "VOID":
         return ToolCallResponse(
            tool_name=request.tool_name,
            status="error",
            governance=post_verdict,
            error="Post-execution governance failed."
        )

    return ToolCallResponse(
        tool_name=request.tool_name,
        status="success",
        output=tool_output,
        governance=post_verdict
    )
