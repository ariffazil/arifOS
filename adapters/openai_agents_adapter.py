"""
OpenAI Agents SDK Adapter for arifOS Constitutional Kernel

This adapter wraps tools inside OpenAI Agents SDK to enforce arifOS
judgment before execution. It acts as a mandatory approval policy layer.
"""
from typing import Callable, Any, Awaitable
from functools import wraps

from arifosmcp.tools.judge import arif_judge_deliberate

class ArifOSRejectionError(Exception):
    """Raised when arifOS rejects a tool execution."""
    pass

def arifos_guarded_tool(
    reversible: bool = False,
    risk_tier: str = "high"
):
    """
    Decorator for OpenAI Agent tools. 
    Intercepts the tool call, sends intent to arifOS for constitutional judgment,
    and only executes if SEAL is returned.
    
    Usage:
        @arifos_guarded_tool(reversible=False, risk_tier="high")
        async def execute_query(query: str) -> str:
            ...
    """
    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Reconstruct intent from function name and arguments
            intent_desc = f"Execute {func.__name__} with args={args} kwargs={kwargs}"
            
            # Send intent to arifOS
            judge_output = await arif_judge_deliberate(
                proposed_action=intent_desc,
                session_id="openai_agents_session",
                reversible=reversible,
                actor_id="openai_agent",
                evidence=[],
                trace_root="openai_trace"
            )
            
            verdict = judge_output.verdict
            
            if verdict == "SEAL":
                # Execution approved, proceed with original tool
                return await func(*args, **kwargs)
            elif verdict == "SABAR":
                raise ArifOSRejectionError(f"arifOS requested SABAR (patience/replan): {judge_output.advisory}")
            elif verdict == "HOLD":
                raise ArifOSRejectionError(f"arifOS issued HOLD (human review required): {judge_output.advisory}")
            else:
                raise ArifOSRejectionError(f"arifOS issued VOID (action forbidden): {judge_output.advisory}")
                
        return wrapper
    return decorator

# TODO: Add Streamable HTTP MCP integration helpers for OpenAI Agents SDK
# to automatically import arifOS's 13 canonical tools.
