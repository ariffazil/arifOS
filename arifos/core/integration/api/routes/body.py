"""
arifOS Body API (v51) - Sovereign Governance Oracle.

Exposes the Trinity Metabolic Loop over standard HTTP/REST.
This is the "Mouth" of arifOS.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from arifos.mcp.tools.mcp_trinity import (
    mcp_000_init,
    mcp_agi_genius,
    mcp_asi_act,
    mcp_apex_judge,
    mcp_999_vault,
)

router = APIRouter(prefix="/v1", tags=["body"])

# =============================================================================
# REQUEST MODELS
# =============================================================================

class GovernRequest(BaseModel):
    query: str = Field(..., description="The user query or agent intent")
    authority_token: str = Field("", description="Sovereign authority token")
    session_id: Optional[str] = Field(None, description="Existing session ID")
    context: Dict[str, Any] = Field(default_factory=dict, description="Metadata and state")

class GovernResponse(BaseModel):
    verdict: str
    response: str
    session_id: str
    floors_passed: list[str]
    ledger_hash: str
    telemetry: Dict[str, Any]

# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post("/govern", response_model=Dict[str, Any])
async def govern(request: GovernRequest):
    """
    The main metabolic entry point.
    Runs a query through the full Trinity pipeline (000-999).
    """
    try:
        # 1. 000_INIT
        init_res = await mcp_000_init(
            action="init",
            query=request.query,
            authority_token=request.authority_token,
            session_id=request.session_id
        )
        
        if init_res["status"] == "VOID":
            return {
                "verdict": "VOID",
                "reason": f"Ignition Failed: {init_res['reason']}",
                "session_id": init_res["session_id"]
            }

        # 2. AGI_GENIUS (Mind)
        agi_res = await mcp_agi_genius(
            action="full",
            query=request.query,
            session_id=init_res["session_id"]
        )

        # 3. ASI_ACT (Heart)
        asi_res = await mcp_asi_act(
            action="full",
            text=agi_res["reasoning"],
            session_id=init_res["session_id"],
            agi_result=agi_res
        )

        # 4. APEX_JUDGE (Soul)
        apex_res = await mcp_apex_judge(
            action="full",
            query=request.query,
            response=agi_res["reasoning"],
            session_id=init_res["session_id"],
            agi_result=agi_res,
            asi_result=asi_res
        )

        # 5. 999_VAULT (Seal)
        vault_res = await mcp_999_vault(
            action="seal",
            session_id=init_res["session_id"],
            verdict=apex_res["verdict"],
            init_result=init_res,
            agi_result=agi_res,
            asi_result=asi_res,
            apex_result=apex_res
        )

        return {
            "verdict": apex_res["verdict"],
            "response": agi_res["reasoning"],
            "session_id": init_res["session_id"],
            "floors_checked": apex_res["floors_checked"],
            "proof_hash": apex_res["proof_hash"],
            "audit_hash": vault_res["audit_hash"],
            "status": "SEALED" if apex_res["verdict"] == "SEAL" else "BLOCKED"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health():
    """System Vitality check."""
    return {
        "status": "ALIVE",
        "version": "v51.2.0",
        "motto": "Ditempa Bukan Diberi",
        "engines": ["AGI", "ASI", "APEX"]
    }
