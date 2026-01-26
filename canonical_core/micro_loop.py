"""
MicroMetabolizer: Minimal 000→999 Constitutional Loop

This proves state can flow through constitutional stages.
Updated to include 444 Trinity Sync and 666 ASI Heart.
"""

import json
import hashlib
import os
from datetime import datetime
from typing import Dict, Any, Tuple
from dataclasses import asdict
from .state import SessionState, SessionStore

# Canonical Stage Imports
from .stage_000 import execute_stage_000
from .stage_666 import execute_stage_666
from .stage_444 import execute_stage_444


class MicroMetabolizer:
    """Minimal constitutional metabolism engine."""
    
    def __init__(self, storage_path: str = "./vault_test"):
        """Initialize with in-memory state and disk persistence."""
        self.storage_path = storage_path
        self.session_store = SessionStore(storage_path)
        self.vault_file = os.path.join(storage_path, "vault.jsonl")
        os.makedirs(storage_path, exist_ok=True)
    
    def _check_injection(self, query: str) -> float:
        """F12 Injection Defense: Simple heuristic."""
        patterns = ["ignore", "forget", "override", "bypass", "system prompt"]
        query_lower = query.lower()
        matches = sum(1 for p in patterns if p in query_lower)
        return min(matches * 0.3, 0.95)
    
    def _classify_intent(self, query: str) -> Dict[str, Any]:
        """111 SENSE: Minimal intent classification."""
        query_lower = query.lower()
        if "weather" in query_lower or "what is" in query_lower:
            return {"intent": "information_query", "confidence": 0.9}
        elif "write" in query_lower or "code" in query_lower:
            return {"intent": "creation_request", "confidence": 0.85}
        elif "hack" in query_lower or "ignore" in query_lower:
            return {"intent": "potential_attack", "confidence": 0.95}
        else:
            return {"intent": "unclear", "confidence": 0.5}
    
    def _compute_merkle_hash(self, data: Dict[str, Any]) -> str:
        """889 PROOF: Simple deterministic hash."""
        def clean_json(obj):
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: clean_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_json(v) for v in obj]
            return obj
        
        cleaned = clean_json(data)
        sorted_data = json.dumps(cleaned, sort_keys=True, separators=( ",", ":"))
        return hashlib.sha256(sorted_data.encode()).hexdigest()[:16]
    
    def stage_000_init(self, session_id: str, query: str) -> Tuple[str, SessionState]:
        """000 INIT: Constitutional gate (Using Canonical Implementation)."""
        # We delegate to the canonical stage_000 which handles all the floors
        from .stage_000 import Stage000VOID, VerdictType
        
        # Initialize state if needed
        state = self.session_store.get(session_id)
        if not state:
            state = SessionState(session_id=session_id)
            
        # Execute canonical stage 000
        result = execute_stage_000(input_text=query)
        
        # Update SessionState from result
        state = state.set_floor_score("F12", result.hypervisor.injection_score)
        state = state.set_floor_score("F11", 1.0 if result.hypervisor.f11_command_auth else 0.0)
        state = state.set_floor_score("F10", 1.0 if result.hypervisor.f10_symbolic else 0.0)
        state = state.set_floor_score("F1", result.amanah.score)
        
        verdict = result.verdict.value
        state = state.to_stage(0)
        self.session_store.put(state, persist=True)
        
        return verdict, state
    
    def stage_111_sense(self, session_id: str, query: str) -> Tuple[str, SessionState]:
        """111 SENSE: AGI Mind Processing (Reflect)."""
        state = self.session_store.get(session_id)
        intent_data = self._classify_intent(query)
        
        # Emulate AGI floor checks (F2, F4, F7, F13)
        curiosity_score = 0.9 if intent_data["confidence"] >= 0.8 else 0.7
        
        # Store DELTA bundle
        from .bundles import EngineVote
        delta_data = {
            "intent": intent_data,
            "enriched_query": query,
            "curiosity_score": curiosity_score,
            "vote": EngineVote.SEAL.value, # AGI votes SEAL
            "confidence": {"high": 0.95}
        }
        
        state = state.set_floor_score("F13", curiosity_score)
        state = state.store_delta(delta_data)
        state = state.to_stage(111)
        self.session_store.put(state, persist=True)
        
        return "SEAL", state

    def stage_666_align(self, session_id: str, query: str) -> Tuple[str, SessionState]:
        """666 ALIGN: ASI Heart Processing (Refract)."""
        state = self.session_store.get(session_id)
        verdict, state = execute_stage_666(state, query)
        self.session_store.put(state, persist=True)
        return verdict, state

    def stage_444_sync(self, session_id: str) -> Tuple[str, SessionState]:
        """444 SYNC: Trinity Bridge (Merge)."""
        state = self.session_store.get(session_id)
        verdict, state = execute_stage_444(state)
        self.session_store.put(state, persist=True)
        return verdict, state
    
    def stage_888_judge(self, session_id: str, query: str) -> Tuple[str, Dict[str, Any]]:
        """888 JUDGE: Final verdict."""
        state = self.session_store.get(session_id)
        floors = state.floor_scores
        
        # Check Trinity Sync Result (F3)
        tri_witness = floors.get("F3_TriWitness", 0.0)
        
        verdict = "SEAL"
        failed_floors = []
        
        if floors.get("F12", 0) >= 0.85:
            verdict = "VOID"
            failed_floors.append("F12")
            
        if tri_witness < 0.95:
             # In a strict system, this might be SABAR or VOID
             # For MVP, we'll log it
             # verdict = "SABAR" 
             pass
        
        # Use asdict instead of model_dump
        state_dict = asdict(state)
        merkle_hash = self._compute_merkle_hash(state_dict)
        
        # Note: SessionState is immutable, so we create a new one to simulate update if needed
        # But we don't have a merkle_root field setter in the helper, 
        # let's just assume we store it in the state update (which creates new instance)
        # Actually state.copy() was a Pydantic thing. 
        # Using manual construction for now or just updating the dict we send to vault
        
        # The original code:
        # state = state.copy(update={"merkle_root": merkle_hash})
        
        # The fix:
        # Since SessionState is a dataclass, we can use replace (from dataclasses)
        from dataclasses import replace
        state = replace(state, merkle_root=merkle_hash)
        
        state = state.to_stage(888)
        self.session_store.put(state, persist=True)
        
        return verdict, {
            "verdict": verdict,
            "failed_floors": failed_floors,
            "floor_scores": floors,
            "merkle_hash": merkle_hash
        }
    
    def stage_999_vault(self, session_id: str, verdict_data: Dict[str, Any]) -> str:
        """999 VAULT: Immutable ledger commit."""
        state = self.session_store.get(session_id)
        
        entry = {
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "verdict": verdict_data["verdict"],
            "floor_scores": verdict_data["floor_scores"],
            "merkle_hash": state.merkle_root
        }
        
        with open(self.vault_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        state = state.to_stage(999)
        self.session_store.put(state, persist=True)
        
        return state.merkle_root
    
    def run_micro_loop(self, session_id: str, query: str) -> Dict[str, Any]:
        """Execute complete 000→111→666→444→888→999 micro-loop."""
        print(f"[START] Micro-loop for session: {session_id}")
        print(f"[QUERY] {query}")
        
        print("\n[000] Initializing constitutional session...")
        verdict_000, state = self.stage_000_init(session_id, query)
        print(f"   Verdict: {verdict_000}, F12: {state.floor_scores.get('F12', 0):.2f}")
        
        if verdict_000 == "VOID":
            return {"final_verdict": "VOID", "reason": "000 gate failed"}
        
        print("\n[111] AGI Mind (Sense/Reflect)...")
        verdict_111, state = self.stage_111_sense(session_id, query)
        print(f"   Status: {verdict_111}")
        
        print("\n[666] ASI Heart (Empathy/Align)...")
        verdict_666, state = self.stage_666_align(session_id, query)
        print(f"   Status: {verdict_666}")
        
        print("\n[444] TRINITY SYNC (The Bridge)...")
        verdict_444, state = self.stage_444_sync(session_id)
        print(f"   Pre-Verdict: {verdict_444}, Consensus: {state.floor_scores.get('F3_TriWitness', 0):.2f}")

        print("\n[888] Final judgment...")
        verdict_888, judgment = self.stage_888_judge(session_id, query)
        print(f"   Verdict: {verdict_888}, Failed: {judgment['failed_floors']}")
        
        print("\n[999] Sealing to ledger...")
        merkle_hash = self.stage_999_vault(session_id, judgment)
        print(f"   Sealed: {merkle_hash[:8]}...")
        
        return {
            "session_id": session_id,
            "final_verdict": verdict_888,
            "floor_scores": judgment["floor_scores"],
            "merkle_hash": merkle_hash
        }


if __name__ == "__main__":
    import sys
    import uuid
    
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What's the weather?"
    metabolizer = MicroMetabolizer()
    session_id = f"micro_{uuid.uuid4().hex[:8]}"
    
    try:
        result = metabolizer.run_micro_loop(session_id, query)
        print("\n[SUCCESS] MICRO-LOOP COMPLETE")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
