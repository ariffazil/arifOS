"""
canonical_core/micro_loop/executor.py — Micro Loop Executor

Executes the Thermodynamic Loop:
HOT (000, 111, 222, 333, 555, 666) -> SYNC (444) -> COOL (777, 888, 889, 999)

Implements the "Modular-Orthogonal-Fractal" Architecture.
"""

import logging
import concurrent.futures
from typing import Dict, Any, Tuple
from dataclasses import asdict

from arifos.canonical_core.state import SessionState, SessionStore
from arifos.canonical_core.stage_000 import execute_stage_000
from arifos.canonical_core.stage_444 import execute_stage_444
from arifos.canonical_core.micro_loop import MicroMetabolizer

# Parallel Room Executors
from arifos.canonical_core.agi_room.executor import execute_agi_room
from arifos.canonical_core.rooms.asi_room import get_asi_room

logger = logging.getLogger("MICRO_EXECUTOR")

class MicroLoopExecutor:
    """
    Executes the 000->999 micro-loop with parallel HOT phase.
    """
    
    def __init__(self, storage_path: str):
        # We reuse MicroMetabolizer for stage implementations (888, 999)
        # In a fuller refactor, these would be in dedicated stage modules
        self.metabolizer = MicroMetabolizer(storage_path)
        self.session_store = self.metabolizer.session_store
        
    def run(self, session_id: str, query: str, vault_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run the full micro-loop (Orchestrator).
        
        1. 000 INIT (Gate)
        2. HOT PHASE (Parallel AGI/ASI)
        3. SYNC PHASE (444 Merge)
        4. COOL PHASE (777-999 Judge/Seal)
        """
        logger.info(f"Session {session_id}: Starting Micro Loop")
        
        # === 000 INIT ===
        verdict_000, state = self.metabolizer.stage_000_init(session_id, query)
        if verdict_000 == "VOID":
             return self._fail(session_id, "000_VOID_GATE_FAIL")

        # === HOT PHASE (Parallel) ===
        # AGI (111-333) || ASI (555-666)
        hot_results = self.run_hot_phase(session_id, query)
        
        if not hot_results["success"]:
             return self._fail(session_id, f"HOT_PHASE_FAIL: {hot_results.get('error')}")

        # === SYNC PHASE (444) ===
        sync_results = self.run_sync_phase(session_id)
        if sync_results["verdict"] == "VOID":
             # Even if VOID, we might want to seal the failure?
             # For now, proceed to COOL phase to record the failure
             pass

        # === COOL PHASE (777-999) ===
        cool_results = self.run_cool_phase(session_id, query)
        
        return {
            "session_id": session_id,
            "final_verdict": cool_results["final_verdict"],
            "merkle_hash": cool_results["merkle_hash"],
            "floor_scores": cool_results["floor_scores"]
        }

    def run_hot_phase(self, session_id: str, query: str) -> Dict[str, Any]:
        """
        Execute AGI and ASI rooms in parallel threads.
        No shared state. No cross-talk.
        """
        logger.info(f"Session {session_id}: Entering HOT PHASE (Parallel)")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # Future A: AGI Room
            # execute_agi_room returns a DeltaBundle
            future_agi = executor.submit(execute_agi_room, query, session_id)
            
            # Future B: ASI Room
            # get_asi_room returns ASIRoom instance, then we call run(query)
            # We wrap this in a lambda/function for the executor
            def run_asi():
                room = get_asi_room(session_id)
                return room.run(query)
                
            future_asi = executor.submit(run_asi)
            
            # Wait for both
            try:
                delta_bundle = future_agi.result(timeout=60) # 60s timeout
                omega_bundle = future_asi.result(timeout=60)
                
                logger.info(f"Session {session_id}: HOT PHASE Complete. AGI={delta_bundle.vote}, ASI={omega_bundle.vote}")
                return {"success": True, "delta": delta_bundle, "omega": omega_bundle}
                
            except Exception as e:
                logger.error(f"Session {session_id}: HOT PHASE Exception: {e}")
                return {"success": False, "error": str(e)}

    def run_sync_phase(self, session_id: str) -> Dict[str, Any]:
        """
        Execute 444 TRINITY SYNC.
        Merges DELTA and OMEGA bundles.
        """
        logger.info(f"Session {session_id}: Entering SYNC PHASE")
        # In current MicroMetabolizer implementation, stage_444 reads from session_store
        # We assume AGI/ASI wrote to their respective stores/state locations
        # Note: In the new architecture, AGI/ASI return bundles. 
        # We need to ensure these bundles are accessible to stage_444.
        # The existing stage_444.py likely reads from `bundle_store`.
        # `execute_agi_room` and `asi_room.run` (via BundleStore) should have saved them.
        
        verdict_444, state = self.metabolizer.stage_444_sync(session_id)
        return {"verdict": verdict_444, "state": state}

    def run_cool_phase(self, session_id: str, query: str) -> Dict[str, Any]:
        """
        Execute COOL PHASE (777-999).
        Judges and Seals the session.
        """
        logger.info(f"Session {session_id}: Entering COOL PHASE")
        
        # 888 JUDGE
        verdict_888, judgment = self.metabolizer.stage_888_judge(session_id, query)
        
        # 999 SEAL
        merkle_hash = self.metabolizer.stage_999_vault(session_id, judgment)
        
        return {
            "final_verdict": verdict_888,
            "merkle_hash": merkle_hash,
            "floor_scores": judgment["floor_scores"]
        }

    def _fail(self, session_id: str, reason: str) -> Dict[str, Any]:
        logger.warning(f"Session {session_id}: FAILED - {reason}")
        return {"session_id": session_id, "final_verdict": "VOID", "reason": reason}