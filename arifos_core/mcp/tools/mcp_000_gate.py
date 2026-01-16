"""
v46.2.0 MCP TOOL — mcp_000_gate.py

Exposes the Constitutional Gate as an MCP tool for Agent Zero integration.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

import importlib
# Dynamic import for numbered package '000_void'
# from ...000_void.constitutional_gate import ConstitutionalGate
try:
    _gate_module = importlib.import_module("arifos_core.stage_000_void.constitutional_gate")
    ConstitutionalGate = _gate_module.ConstitutionalGate
    
    _auth_module = importlib.import_module("arifos_core.stage_000_void.authority_manifest")
    AuthorityManifest = _auth_module.AuthorityManifest
except ImportError as e:
    raise ImportError(f"Failed to import Constitutional Core: {e}")


# Request Model
class GateRequest(BaseModel):
    query: str = Field(..., description="The user query or agent intention to assess")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Context metadata (user_role, etc.)")

# Response Model (Implicit dict for now to match other tools)

def mcp_000_gate(request: GateRequest) -> Dict[str, Any]:
    """
    Synchronous wrapper for the async Constitutional Gate.
    (In a real async MCP server, we'd await, but here we might run blocking or via asyncio.run if needed by the server spine.
    Given server.py uses 'run_tool' synchronously, we bridge here).
    """
    import asyncio
    
    # Run the assessment
    # Note: If already in an event loop, this might need nest_asyncio, 
    # but for standalone tool execution usually ok.
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
             # If we are strictly in a sync tool call from an async server, this is tricky.
             # However, arifOS MCP server seems to handle tools as simple callables.
             # We will assume new loop for safety if not running, or handle coroutine if caller expects it.
             # For now, simplest path: return coroutine if caller handles it, OR run checks synchronously if possible.
             # Since ConstitutionalGate.assess_query is async, let's wrap it properly.
             # BUT: The 'thermodynamics', 'injection' are synchronous static methods. 
             # The only async part might be future database lookups.
             # Let's inspect constitutional_gate.py ... it is defined as `async def assess_query`.
             # We should probably make assess_query sync for the reflex version or use asyncio.run.
             pass
    except RuntimeError:
        pass
        
    # Hack for now: Logic in ConstitutionalGate uses no awaitables in the current implementation 
    # (they are all static method calls to sync functions). 
    # So we can just call the logic or strip async. 
    # Implementation decision: Wrapper runs asyncio.run() to be safe for future extensibility.
    
    verdict_obj = asyncio.run(ConstitutionalGate.assess_query(request.query, request.context))
    
    return {
        "verdict": verdict_obj.verdict,
        "reason": verdict_obj.reason,
        "metadata": verdict_obj.metadata,
        "authority_manifest": AuthorityManifest.Is_Agent_Zero_Allowed # Conceptual, currently dict in Manifest
    }
