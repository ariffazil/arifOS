"""
Sovereign Executor Tool (MCP Wrapper)
The "Hand" of the Agent.
"""
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from arifos.system.executor import SovereignExecutor

# Initialize the Executor Facade
_executor = SovereignExecutor()

class ExecutorRequest(BaseModel):
    """Request model for Sovereign Executor."""
    command: str = Field(..., description="The shell command to execute.")
    intent: str = Field(..., description="The reason/intent for this action (for Constitutional verification).")

def arifos_executor(request: ExecutorRequest) -> Dict[str, Any]:
    """
    Execute a command via the Sovereign Execution Engine.

    Args:
        request: ExecutorRequest containing command and intent.

    Returns:
        Dict containing the execution result or constitutional verdict.
    """
    # The Facade expects a query string that typically includes intent.
    # For this tool, we construct a structured query/context for the Interceptor.

    full_context_query = f"[INTENT: {request.intent}] [COMMAND: {request.command}]"

    return _executor.execute(full_context_query)
