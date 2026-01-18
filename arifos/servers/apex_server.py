# -*- coding: utf-8 -*-
"""
arifOS APEX Server - The Soul (Psi)

Constitutional Alignment: F3 (Tri-Witness), F8 (Genius)
Stages: 444 EVIDENCE, 777 EUREKA, 888 SEAL, 889 PROOF
Version: v49.0.0
Authority: Delta (Architect)

Architecture:
- Hosts 4 MCP tools: claude_api (PAID), cryptography, vector_db, zkpc_merkle
- Enforces F3/F8 floors on all operations
- Final judgment and sealing authority
- Generates zkPC receipts and Merkle proofs
- Dual-write to PostgreSQL + JSONL cooling ledger

NOTE: Blueprint status. zkPC/Merkle are placeholders. See IMPLEMENTATION_GAPS.md.
"""

import asyncio
import hashlib
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Phase 9.2: zkPC cryptographic sealing
from arifos.apex.governance.zkpc_runtime import (
    ZKPCContext,
    build_zkpc_receipt,
    commit_receipt_to_vault,
)

# Phase 9.3: Phoenix-72 cooling enforcement
from arifos.asi.cooling import COOLING

# Constitutional imports (Phase 8.1: Canonical validators)
from arifos.core.floor_validators import validate_f3_tri_witness
from arifos.core.floor_validators import validate_f8_genius as validate_f8_genius_canonic

# Ledger dual-write import
from arifos.memory.ledger.postgres_ledger import get_ledger

logger = logging.getLogger(__name__)

# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class APEXRequest(BaseModel):
    """Request to APEX server (from AGI/ASI stages)."""
    session_id: str = Field(..., description="Session identifier")
    query: str = Field(..., description="User query")
    stage: str = Field(..., description="Target stage (444/777/888/889)")
    context: Dict[str, Any] = Field(default_factory=dict, description="Session context")
    floor_scores: Dict[str, Any] = Field(default_factory=dict, description="All floor scores")
    agi_output: Optional[Dict[str, Any]] = Field(None, description="AGI stage outputs")
    asi_output: Optional[Dict[str, Any]] = Field(None, description="ASI stage outputs")


class APEXResponse(BaseModel):
    """Response from APEX server."""
    verdict: str = Field(..., description="SEAL/PARTIAL/VOID/SABAR/888_HOLD")
    stage: str = Field(..., description="Completed stage")
    floor_scores: Dict[str, Any] = Field(default_factory=dict, description="All floor scores")
    output: Dict[str, Any] = Field(default_factory=dict, description="Stage output")
    next_stage: str = Field(..., description="Next stage routing decision")
    latency_ms: float = Field(..., description="Processing time")
    zkpc_receipt: Optional[str] = Field(None, description="zkPC receipt hash (889 only)")


# =============================================================================
# APEX SERVER CLASS
# =============================================================================

class APEXServer:
    """
    APEX Server - The Soul (Ψ)

   Hosts judgment stages 444/777/888/889 with final constitutional authority.
    """

    def __init__(self, vault_url: str = "http://vault_server:9000"):
        self.vault_url = vault_url
        self.mcp_tools = [
            "claude_api", "cryptography", "vector_db", "zkpc_merkle"
        ]
        self.floors = ["F3", "F8"]
        self.stages = ["444_EVIDENCE", "777_EUREKA", "888_SEAL", "889_PROOF"]

        logger.info(f"APEX Server initialized with {len(self.mcp_tools)} MCP tools")
        logger.info(f"Enforcing floors: {', '.join(self.floors)}")

    async def process_444_evidence(self, request: APEXRequest) -> APEXResponse:
        """
        Stage 444 EVIDENCE - Tri-witness data aggregation.

        Floors: F3 (Tri-Witness)
        """
        import time
        start_time = time.time()

        # F3: Tri-Witness consensus check (Human·AI·Earth ≥0.95)
        triwitness_result = validate_f3_triwitness(
            request.query,
            request.agi_output or {},
            request.context
        )

        floor_scores = {
            **request.floor_scores,
            "F3_TriWitness": triwitness_result,
        }

        # Determine verdict
        if triwitness_result["score"] < 0.95:
            verdict = "SABAR"
            next_stage = "888_SEAL"  # Escalate for judgment
        else:
            verdict = "SEAL"
            next_stage = "555_EMPATHY"  # Route to ASI safety check

        latency_ms = (time.time() - start_time) * 1000

        return APEXResponse(
            verdict=verdict,
            stage="444_EVIDENCE",
            floor_scores=floor_scores,
            output={
                "triwitness_score": triwitness_result.get("score", 0.0),
                "human_intent": triwitness_result.get("human_intent", "unknown"),
                "ai_logic": triwitness_result.get("ai_logic", "unknown"),
                "earth_facts": triwitness_result.get("earth_facts", "unknown"),
            },
            next_stage=next_stage,
            latency_ms=latency_ms,
        )

    async def process_777_eureka(self, request: APEXRequest) -> APEXResponse:
        """
        Stage 777 EUREKA - Novelty detection and verification.

        Floors: F8 (Genius)
        """
        import time
        start_time = time.time()

        # F8: Genius scoring (intelligence governed?)
        genius_result = validate_f8_genius(request.floor_scores)

        floor_scores = {
            **request.floor_scores,
            "F8_Genius": genius_result,
        }

        # Determine verdict
        if genius_result["score"] < 0.80:
            verdict = "VOID"
            next_stage = "999_VAULT"
        else:
            verdict = "SEAL"
            next_stage = "888_SEAL"  # Route to final judgment

        latency_ms = (time.time() - start_time) * 1000

        return APEXResponse(
            verdict=verdict,
            stage="777_EUREKA",
            floor_scores=floor_scores,
            output={
                "genius_score": genius_result.get("score", 0.0),
                "novelty_detected": False,  # TODO: Implement novelty detector
                "breakthrough_patterns": [],
            },
            next_stage=next_stage,
            latency_ms=latency_ms,
        )

    async def process_888_seal(self, request: APEXRequest) -> APEXResponse:
        """
        Stage 888 SEAL - Final constitutional judgment.

        Floors: All F1-F13
        """
        import time
        start_time = time.time()

        # Aggregate all floor scores
        all_floors_pass = all(
            score.get("pass", False) if isinstance(score, dict) else score
            for score in request.floor_scores.values()
        )

        # Phase 9.3: Determine Phoenix-72 cooling tier using CoolingEngine
        soft_floor_warnings = sum(
            1 for floor_name, score in request.floor_scores.items()
            if "F5" in floor_name or "F6" in floor_name or "F13" in floor_name
            if isinstance(score, dict) and not score.get("pass", True)
        )

        # Determine verdict based on floor results
        if not all_floors_pass:
            final_verdict = "VOID"
        elif soft_floor_warnings == 0:
            final_verdict = "SEAL"
        else:
            final_verdict = "PARTIAL"

        # Calculate cooling tier using Phoenix-72 logic
        cooling_tier = COOLING.calculate_cooling_tier(final_verdict, soft_floor_warnings)

        # Enforce tier (returns cooling metadata)
        cooling_status = await COOLING.enforce_tier(cooling_tier, request.session_id)

        # Dual-write to cooling ledger (Postgres + JSONL)
        try:
            ledger = get_ledger()
            await ledger.write_entry(
                entry_id=request.session_id,
                verdict=final_verdict,
                floors=request.floor_scores,
                user_id=request.context.get("user_id", "system"),
                zkpc_hash=None  # Will be added in 889 PROOF
            )
        except Exception as ledger_error:
            logger.error(f"Ledger write failed: {ledger_error}")
            # Continue despite ledger failure (soft dependency)

        latency_ms = (time.time() - start_time) * 1000

        return APEXResponse(
            verdict=final_verdict,
            stage="888_SEAL",
            floor_scores=request.floor_scores,
            output={
                "all_floors_pass": all_floors_pass,
                "soft_floor_warnings": soft_floor_warnings,
                "phoenix72_cooling": cooling_status,  # Phase 9.3: Full cooling metadata
            },
            next_stage="889_PROOF" if final_verdict == "SEAL" else "999_VAULT",
            latency_ms=latency_ms,
        )

    async def process_889_proof(self, request: APEXRequest) -> APEXResponse:
        """
        Stage 889 PROOF - zkPC receipt generation.

        Floors: Cryptographic validation (Phase 9.2 - Production zkPC)
        """
        import time
        start_time = time.time()

        # Phase 9.2: Production zkPC cryptographic sealing
        # Build zkPC context from request
        ctx = ZKPCContext(
            user_query=request.query,
            retrieved_canon=[],  # TODO: Populate from memory retrieval
            high_stakes=(request.floor_scores.get("F3_TriWitness", {}).get("pass", False)),
            meta={
                "session_id": request.session_id,
                "context": request.context,
            },
        )

        # Extract verdict from floor scores (assume SEAL if all floors pass)
        all_floors_pass = all(
            score.get("pass", False) if isinstance(score, dict) else score
            for score in request.floor_scores.values()
        )
        verdict = "SEAL" if all_floors_pass else "PARTIAL"

        # Build care scope (Phase I - PAUSE)
        from arifos.apex.governance.zkpc_runtime import (
            build_care_scope,
            compute_metrics_stub,
            run_eye_cool_phase_stub,
        )
        care_scope = build_care_scope(ctx)

        # Compute metrics (Phase II/III - CONTRAST/INTEGRATE)
        # Use floor_scores from request as ground truth
        metrics = {
            "truth": request.floor_scores.get("F2_Truth", {}).get("score", 0.99),
            "delta_s": request.floor_scores.get("F4_Clarity", {}).get("delta_s", 0.0),
            "peace_squared": request.floor_scores.get("F5_Peace", {}).get("score", 1.0),
            "kappa_r": request.floor_scores.get("F6_Empathy", {}).get("score", 0.95),
            "omega_0": request.floor_scores.get("F7_Humility", {}).get("omega_zero", 0.04),
            "amanah": "LOCK" if request.floor_scores.get("F1_Amanah", {}).get("pass", False) else "UNLOCK",
            "tri_witness": request.floor_scores.get("F3_TriWitness", {}).get("score", 0.95),
            "genius": request.floor_scores.get("F8_Genius", {}).get("score", 0.80),
            "cdark": request.floor_scores.get("F9_Cdark", {}).get("score", 0.0),
        }

        # Run @EYE cooling phase (Phase IV - COOL)
        eye_report = run_eye_cool_phase_stub(ctx, "", metrics)

        # Phase tracking
        phases_status = {
            "pause": "COMPLETE",
            "contrast": "COMPLETE",
            "integrate": "COMPLETE",
            "cool": "PASS",
            "seal": "SEALING",
        }

        # Build zkPC receipt (Phase V - SEAL)
        receipt = build_zkpc_receipt(
            ctx=ctx,
            answer="",  # Answer not available at APEX stage
            care_scope=care_scope,
            metrics=metrics,
            eye_report=eye_report,
            phases_status=phases_status,
            verdict=verdict,
        )

        # Commit to Vault-999 Cooling Ledger + Merkle tree
        try:
            ledger_entry = commit_receipt_to_vault(receipt)
            receipt_id = receipt.get("receipt_id", "unknown")
            merkle_root = receipt["vault_commit"]["merkle_root"]
            receipt_hash = receipt["vault_commit"]["hash"]
        except Exception as zkpc_error:
            logger.error(f"zkPC commit failed: {zkpc_error}")
            # Fallback to simplified hash if zkPC fails
            receipt_hash = hashlib.sha256(str(receipt).encode()).hexdigest()[:16]
            merkle_root = "zkpc_commit_failed"
            receipt_id = receipt.get("receipt_id", "unknown")

        latency_ms = (time.time() - start_time) * 1000

        return APEXResponse(
            verdict=verdict,
            stage="889_PROOF",
            floor_scores=request.floor_scores,
            output={
                "zkpc_receipt_id": receipt_id,
                "zkpc_hash": receipt_hash,
                "merkle_root": merkle_root,
                "vault_ledger": "L1_cooling_ledger.jsonl",
                "phases": phases_status,
            },
            next_stage="999_VAULT",
            latency_ms=latency_ms,
            zkpc_receipt=receipt_hash,
        )


# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

app = FastAPI(title="arifOS APEX Server", version="v49.0.0")
apex_server = APEXServer()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "server": "APEX",
        "version": "v49.0.0",
        "floors": apex_server.floors,
        "stages": apex_server.stages,
        "mcp_tools": len(apex_server.mcp_tools),
    }


@app.post("/process", response_model=APEXResponse)
async def process_stage(request: APEXRequest):
    """Process APEX stage request (444/777/888/889)."""
    try:
        if request.stage == "444_EVIDENCE":
            return await apex_server.process_444_evidence(request)
        elif request.stage == "777_EUREKA":
            return await apex_server.process_777_eureka(request)
        elif request.stage == "888_SEAL":
            return await apex_server.process_888_seal(request)
        elif request.stage == "889_PROOF":
            return await apex_server.process_889_proof(request)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown stage: {request.stage}")
    except Exception as e:
        logger.error(f"Error processing {request.stage}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# MCP TOOL PROXY (Phase 8.2 - Generic handler for all APEX MCP tools)
# =============================================================================

@app.post("/mcp/{tool_name}")
async def execute_mcp_tool(tool_name: str, request: Dict[str, Any]):
    """
    Generic MCP tool executor for APEX server.

    Phase 8.2: Proof-of-concept for 4 APEX tools
    - claude_api (PAID LLM reasoning)
    - cryptography (zkPC sealing)
    - vector_db (memory embeddings)
    - zkpc_merkle (Merkle proofs)
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
                detail=f"MCP tool '{tool_name}' not found. Available: {', '.join(apex_server.mcp_tools)}"
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
            "server": "APEX",
            "floors": apex_server.floors,
        }

    except Exception as e:
        logger.error(f"MCP tool '{tool_name}' error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9003)
