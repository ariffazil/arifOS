"""
canonical_core/loop_manager.py — ARIF Loop Orchestrator

Manages the MACRO LOOP (Sessions):
1. Session Registry (UUIDs, timestamps)
2. Loop Scheduler (Phoenix-72 timers)
3. Macro Loop Execution (000->999)

Mnemonic: "Salam ↔ Salam"
"""

import uuid
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from .micro_loop.executor import MicroLoopExecutor
from .vault.learning_loop import VaultLearningLoop

logger = logging.getLogger("LOOP_MANAGER")

class SessionRegistry:
    """In-memory registry of active and historical sessions."""
    
    def __init__(self):
        self.active_sessions: Dict[str, float] = {}  # session_id -> start_time
        self.history: List[str] = []  # List of sealed session_ids
        
    def register(self, session_id: str):
        self.active_sessions[session_id] = time.time()
        
    def archive(self, session_id: str):
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            self.history.append(session_id)

class LoopScheduler:
    """
    Manages Phoenix-72 timers and session cooling.
    """
    def __init__(self):
        self.timers: Dict[str, datetime] = {}
        
    def set_cooling_timer(self, session_id: str, tier: int):
        """Set unlock time based on cooling tier."""
        now = datetime.utcnow()
        if tier == 0: # L0 Immediate
            unlock_time = now
        elif tier == 2: # L2 Phoenix (VOID)
            unlock_time = now + timedelta(hours=72)
        elif tier == 3: # L3 Weekly (SABAR)
            unlock_time = now + timedelta(days=7)
        elif tier == 4: # L4 Monthly (PARTIAL)
            unlock_time = now + timedelta(days=30)
        elif tier == 5: # L5 Eternal (SEAL + Genius)
            unlock_time = now # No cooling needed for subsequent use (archived)
        else:
            unlock_time = now
            
        self.timers[session_id] = unlock_time
        logger.info(f"Cooling timer set for {session_id} (Tier {tier}): {unlock_time}")

    def check_timers(self) -> List[str]:
        """Return list of session_ids that are ready to unlock."""
        now = datetime.utcnow()
        ready = [sid for sid, t in self.timers.items() if now >= t]
        for sid in ready:
            del self.timers[sid]
        return ready

class LoopManager:
    """
    The Orchestrator of the Macro Loop.
    """
    
    def __init__(self, storage_path: str = "./vault"):
        self.registry = SessionRegistry()
        self.scheduler = LoopScheduler()
        self.executor = MicroLoopExecutor(storage_path)
        self.learning = VaultLearningLoop(storage_path)
        self.storage_path = storage_path
        
    def execute_macro_loop(self, query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute one cycle of the Macro Loop.
        
        1. SALAM 000 INIT START
        2. Run Micro Loop (HOT -> SYNC -> COOL)
        3. Schedule Cooling (Phoenix-72)
        4. Trigger Learning Loop (Vault -> Next Session)
        """
        if not session_id:
            session_id = f"sess_{uuid.uuid4().hex[:8]}"
            
        logger.info(f"SALAM 000 INIT START: Session {session_id}")
        self.registry.register(session_id)
        
        # 1. Load Vault Context (from Learning Loop)
        # Extracts patterns and Ω₀ baseline from previous sealed entries
        vault_context = self.learning.get_baseline_context()
        logger.info(f"Loaded Vault Context: Ω₀={vault_context.get('omega_0_band')}")
        
        # 2. Run Micro Loop (Delegates to Executor)
        # 000 -> HOT (AGI||ASI) -> 444 -> COOL (777->999)
        result = self.executor.run(session_id, query, vault_context)
        
        # 3. Schedule Cooling
        verdict = result.get("final_verdict", "VOID")
        
        # Determine Tier based on Verdict (Simplified)
        if verdict == "SEAL":
            tier = 0 # or 5
        elif verdict == "SABAR":
            tier = 3
        elif verdict == "VOID":
            tier = 2
        else:
            tier = 4 # Partial/Unknown
            
        self.scheduler.set_cooling_timer(session_id, tier)
        
        # 4. Archive Session
        self.registry.archive(session_id)
        
        # 5. Trigger Learning Loop (Async in production)
        # This updates the baseline for the NEXT session
        self.learning.process_session(result)
        
        logger.info(f"SALAM RESTART: Session {session_id} sealed. Verdict: {verdict}")
        
        return result

# Singleton
loop_manager = LoopManager()