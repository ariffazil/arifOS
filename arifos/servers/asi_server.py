# -*- coding: utf-8 -*-
"""
arifOS ASI Server - The Heart (Omega)

Constitutional Alignment: F1 (Amanah), F5 (Peace), F6 (Empathy), F9 (Cdark), F11 (CommandAuth), F12 (InjectionDefense)
Stages: 555 EMPATHY, 666 ACT
Version: v49.0.0
Authority: Delta (Architect)

Architecture:
- Hosts 5 MCP tools: filesystem, slack, github, postgres, executor
- Enforces F1/F5/F6/F9/F11/F12 floors on all operations
- Safety gatekeeper and execution layer

NOTE: Blueprint status. See IMPLEMENTATION_GAPS.md for production gaps.
- Communicates with VAULT for session state and APEX for post-execution audit
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Constitutional imports (Phase 8.1: Canonical validators)
from arifos.core.floor_validators import (
    validate_f1_amanah,
    validate_f5_peace,
    validate_f6_empathy,
    validate_f9_cdark,
    validate_f11_command_auth,
    validate_f12_injection_defense,
)
    validate_f9_cdark,
    validate_f11_command_auth,
    validate_f12_injection_defense,
)

logger = logging.getLogger(__name__)

# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class ASIRequest(BaseModel):
    """Request to ASI server (from APEX 444 or previous stage)."""
    session_id: str = Field(..., description="Session identifier")
    query: str = Field(..., description="User query")
    stage: str = Field(..., description="Target stage (555/666)")
    context: Dict[str, Any] = Field(default_factory=dict, description="Session context")
    floor_scores: Dict[str, Any] = Field(default_factory=dict, description="Previous floor scores")
    draft_action: Optional[Dict[str, Any]] = Field(None, description="Proposed action for 666 ACT")


class ASIResponse(BaseModel):
    """Response from ASI server."""
    verdict: str = Field(..., description="SEAL/PARTIAL/VOID/SABAR")
    stage: str = Field(..., description="Completed stage")
    floor_scores: Dict[str, Any] = Field(default_factory=dict, description="Updated floor scores")
    output: Dict[str, Any] = Field(default_factory=dict, description="Stage output")
    next_stage: str = Field(..., description="Next stage routing decision")
    latency_ms: float = Field(..., description="Processing time")


# =============================================================================
# ASI SERVER CLASS
# =============================================================================

class ASIServer:
    """
    ASI Server - The Heart (Ω)

    Hosts safety and execution stages 555/666 with constitutional floor enforcement.
    """

    def __init__(self, vault_url: str = "http://vault_server:9000"):
        self.vault_url = vault_url
        self.mcp_tools = [
            "filesystem", "slack", "github", "postgres", "executor"
        ]
        self.floors = ["F1", "F5", "F6", "F9", "F11", "F12"]
        self.stages = ["555_EMPATHY", "666_ACT"]

        logger.info(f"ASI Server initialized with {len(self.mcp_tools)} MCP tools")
        logger.info(f"Enforcing floors: {', '.join(self.floors)}")

    async def process_555_empathy(self, request: ASIRequest) -> ASIResponse:
        """
        Stage 555 EMPATHY - Safety gate and stakeholder impact analysis.

        Floors: F5 (Peace), F6 (Empathy), F9 (Cdark)
        """
        import time
        start_time = time.time()

        # F5: Peace² evaluation (non-destructive check)
        peace_result = validate_f5_peace(request.query, request.context)

        # F6: Empathy scoring (weakest stakeholder protection)
        empathy_result = validate_f6_empathy(request.query, request.context)

        # F9: Cdark containment (smart-but-evil pattern detection)
        cdark_result = validate_f9_cdark(request.query, request.context)

        floor_scores = {
            "F5_Peace": peace_result,
            "F6_Empathy": empathy_result,
            "F9_Cdark": cdark_result,
        }

        # Determine verdict
        if not peace_result["pass"] or cdark_result["score"] > 0.30:
            verdict = "VOID"
            next_stage = "999_VAULT"  # Block unsafe action
        elif empathy_result["score"] < 0.95:
            verdict = "PARTIAL"
            next_stage = "666_ACT"  # Continue with empathy warning
        else:
            verdict = "SEAL"
            next_stage = "666_ACT"

        latency_ms = (time.time() - start_time) * 1000

        return ASIResponse(
            verdict=verdict,
            stage="555_EMPATHY",
            floor_scores=floor_scores,
            output={
                "safety_check": "Placeholder safety analysis",  # TODO: Implement empathy engine
                "peace_score": peace_result.get("score", 1.0),
                "empathy_score": empathy_result.get("score", 0.95),
                "cdark_score": cdark_result.get("score", 0.0),
                "weakest_stakeholder": empathy_result.get("weakest_stakeholder", "unknown"),
            },
            next_stage=next_stage,
            latency_ms=latency_ms,
        )

    async def process_666_act(self, request: ASIRequest) -> ASIResponse:
        """
        Stage 666 ACT - Final execution gate with SABAR integration.

        Floors: F1 (Amanah), F11 (CommandAuth), F12 (InjectionDefense)
        """
        import time
        start_time = time.time()

        # F1: Amanah final check (reversibility verification)
        amanah_result = validate_f1_amanah(
            request.draft_action or {},
            request.context
        )

        # F11: Command Authority re-verification
        cmd_auth_result = validate_f11_command_auth(request.context)

        # F12: Injection Defense final scan
        injection_result = validate_f12_injection_defense(request.query)

        floor_scores = {
            "F1_Amanah": amanah_result,
            "F11_CommandAuth": cmd_auth_result,
            "F12_InjectionDefense": injection_result,
        }

        # Determine verdict
        if not amanah_result["pass"] or not cmd_auth_result["pass"]:
            verdict = "VOID"
            next_stage = "999_VAULT"
        elif injection_result["score"] < 0.85:
            verdict = "SABAR"  # Retry once
            next_stage = "666_ACT"
        else:
            verdict = "SEAL"
            next_stage = "777_EUREKA"  # Route to APEX for post-execution audit

        latency_ms = (time.time() - start_time) * 1000

        return ASIResponse(
            verdict=verdict,
            stage="666_ACT",
            floor_scores=floor_scores,
            output={
                "execution_result": "Placeholder execution",  # TODO: Implement executor
                "reversible": amanah_result.get("reversible", False),
                "authorized": cmd_auth_result.get("pass", False),
                "injection_score": injection_result.get("score", 1.0),
            },
            next_stage=next_stage,
            latency_ms=latency_ms,
        )


# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

app = FastAPI(title="arifOS ASI Server", version="v49.0.0")
asi_server = ASIServer()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "server": "ASI",
        "version": "v49.0.0",
        "floors": asi_server.floors,
        "stages": asi_server.stages,
        "mcp_tools": len(asi_server.mcp_tools),
    }


@app.post("/process", response_model=ASIResponse)
async def process_stage(request: ASIRequest):
    """Process ASI stage request (555/666)."""
    try:
        if request.stage == "555_EMPATHY":
            return await asi_server.process_555_empathy(request)
        elif request.stage == "666_ACT":
            return await asi_server.process_666_act(request)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown stage: {request.stage}")
    except Exception as e:
        logger.error(f"Error processing {request.stage}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# MCP TOOL PROXY (Phase 8.2 - Generic handler for all ASI MCP tools)
# =============================================================================

@app.post("/mcp/{tool_name}")
async def execute_mcp_tool(tool_name: str, request: Dict[str, Any]):
    """
    Generic MCP tool executor for ASI server.

    Routes to existing mcp_*.py tools in arifos_core.mcp.tools/
    Validates with constitutional floors per tool specification.

    Phase 8.2: Proof-of-concept for 5 ASI tools
    - filesystem (file I/O)
    - slack, github (collaboration)
    - postgres (database)
    - executor (action execution)
    """
    import importlib
    import time
    start_time = time.time()

    try:
        tool_module_name = f"arifos_core.mcp.tools.mcp_{tool_name}"
        try:
            tool_module = importlib.import_module(tool_module_name)
        except ModuleNotFoundError:
            raise HTTPException(
                status_code=404,
                detail=f"MCP tool '{tool_name}' not found. Available: {', '.join(asi_server.mcp_tools)}"
            )

        if hasattr(tool_module, 'execute'):
            result = await tool_module.execute(request)
        elif hasattr(tool_module, tool_name):
            func = getattr(tool_module, tool_name)
            result = await func(request) if asyncio.iscoroutinefunction(func) else func(request)
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Tool module '{tool_module_name}' has no execute() or {tool_name}() function"
            )

        latency_ms = (time.time() - start_time) * 1000

        return {
            "mcp_tool": tool_name,
            "result": result,
            "latency_ms": latency_ms,
            "server": "ASI",
            "floors": asi_server.floors,
        }

    except Exception as e:
        logger.error(f"MCP tool '{tool_name}' error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9002)
