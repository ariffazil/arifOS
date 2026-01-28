"""
codebase/micro_loop/executor.py — Micro Loop Executor (Native v53)

Executes the Thermodynamic Loop:
HOT (000, 111, 222, 333, 555, 666) -> SYNC (444) -> COOL (777, 888, 889, 999)

Implements the "Modular-Orthogonal-Fractal" Architecture.

DITEMPA BUKAN DIBERI - Forged, Not Given
"""

import logging
import concurrent.futures
from typing import Dict, Any, Tuple, Optional
from dataclasses import asdict

from codebase.state import SessionState, SessionStore
from codebase.stages.stage_444_trinity_sync import execute_trinity_sync_stage

# Native AGI/ASI/APEX Engines (v53)
from codebase.engines.agi import AGIRoom, get_agi_room
from codebase.engines.asi import ASIRoom, get_asi_room
from codebase.engines.bridge.neuro_symbolic_bridge import NeuroSymbolicBridgeNative

logger = logging.getLogger(__name__)

class MicroLoopExecutor:
    """
    Executes a single metabolic cycle (Micro Loop).
    V53 Upgrade: Uses isolated Rooms and Delta/Omega bundles.
    """

    def __init__(self, storage_path: str = "./vault"):
        self.storage_path = storage_path
        self.session_store = SessionStore(storage_path)

    async def run(self, session_id: str, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the complete 000-999 loop natively.
        Uses parallel execution for AGI/ASI (HOT PHASE).
        """
        logger.info(f"[MICRO-LOOP] Starting cycle for session {session_id}")
        
        # 1. HOT PHASE: AGI || ASI (Parallel)
        hot_result = await self.run_hot_phase(session_id, query, context)
        if not hot_result.get("success"):
            return {"status": "VOID", "reason": f"HOT Phase Failure: {hot_result.get('error')}"}
        
        # 2. SYNC PHASE: 444 TRINITY SYNC
        sync_result = await self.run_sync_phase(session_id)
        if sync_result.get("verdict") == "VOID":
             return {"status": "VOID", "reason": "Trinity Dissent (444)"}
             
        # 3. COOL PHASE: 777-999 SEAL
        cool_result = await self.run_cool_phase(session_id, query)
        
        return {
            "session_id": session_id,
            "query": query,
            "final_verdict": cool_result["final_verdict"],
            "merkle_hash": cool_result["merkle_hash"],
            "floor_scores": cool_result["floor_scores"]
        }

    async def run_hot_phase(self, session_id: str, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Parallel execution of AGI (Mind) and ASI (Heart)."""
        logger.info(f"Session {session_id}: Entering HOT PHASE (Δ||Ω)")
        
        agi_room = get_agi_room(session_id)
        asi_room = get_asi_room(session_id)
        
        with concurrent.futures.ThreadPoolExecutor() as pool:
            import asyncio
            loop = asyncio.get_event_loop()
            
            # Execute in parallel
            try:
                tasks = [
                    loop.create_task(agi_room.run(query)),
                    loop.create_task(asi_room.run(query))
                ]
                
                delta_bundle, omega_bundle = await asyncio.gather(*tasks)
                
                logger.info(f"HOT PHASE Success: AGI={delta_bundle.vote}, ASI={omega_bundle.vote}")
                return {"success": True, "delta": delta_bundle, "omega": omega_bundle}
                
            except Exception as e:
                logger.error(f"Session {session_id}: HOT PHASE Exception: {e}")
                return {"success": False, "error": str(e)}

    async def run_sync_phase(self, session_id: str) -> Dict[str, Any]:
        """Execute 444 TRINITY SYNC."""
        logger.info(f"Session {session_id}: Entering SYNC PHASE")
        result = await execute_trinity_sync_stage(session_id)
        return result

    async def run_cool_phase(self, session_id: str, query: str) -> Dict[str, Any]:
        """Execute COOL PHASE (777-999)."""
        logger.info(f"Session {session_id}: Entering COOL PHASE")
        
        from codebase.stages.stage_999_seal import execute_seal_stage
        
        # 888 JUDGE logic usually lives in APEXRoom or Stage 888.
        # In this v53 native build, 444 already produced a verdict.
        # Seal it.
        seal_result = await execute_seal_stage(session_id)
        
        return {
            "final_verdict": seal_result["status"],
            "merkle_hash": seal_result["hash"],
            "floor_scores": {} # Aggregated in merged bundle
        }