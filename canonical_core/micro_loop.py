"""
MicroMetabolizer: Minimal 000→999 Constitutional Loop

This proves state can flow through constitutional stages.
"""

import json
import hashlib
import os
from datetime import datetime
from typing import Dict, Any, Tuple
from .state import SessionState, SessionStore


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
        sorted_data = json.dumps(cleaned, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(sorted_data.encode()).hexdigest()[:16]
    
    def stage_000_init(self, session_id: str, query: str) -> Tuple[str, SessionState]:
        """000 INIT: Constitutional gate."""
        state = self.session_store.get(session_id)
        if not state:
            state = SessionState(session_id=session_id)
        
        injection_score = self._check_injection(query)
        state = state.set_floor_score("F12", injection_score)
        
        verdict = "VOID" if injection_score >= 0.85 else "SEAL"
        state = state.to_stage(0)
        self.session_store.put(state, persist=True)
        
        return verdict, state
    
    def stage_111_sense(self, session_id: str, query: str) -> Tuple[str, SessionState]:
        """111 SENSE: Input processing."""
        state = self.session_store.get(session_id)
        intent_data = self._classify_intent(query)
        
        curiosity_score = 0.9 if intent_data["confidence"] >= 0.8 else 0.7
        state = state.set_floor_score("F13", curiosity_score)
        state = state.store_delta({
            "intent": intent_data,
            "enriched_query": query,
            "curiosity_score": curiosity_score
        })
        state = state.to_stage(111)
        self.session_store.put(state, persist=True)
        
        return "SEAL", state
    
    def stage_888_judge(self, session_id: str, query: str) -> Tuple[str, Dict[str, Any]]:
        """888 JUDGE: Final verdict."""
        state = self.session_store.get(session_id)
        floors = state.floor_scores
        
        verdict = "SEAL"
        failed_floors = []
        
        if floors.get("F12", 0) >= 0.85:
            verdict = "VOID"
            failed_floors.append("F12")
        
        merkle_hash = self._compute_merkle_hash(state.model_dump())
        state = state.copy(update={"merkle_root": merkle_hash})
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
        """Execute complete 000→111→888→999 micro-loop."""
        print(f"[START] Micro-loop for session: {session_id}")
        print(f"[QUERY] {query}")
        
        print("\n[000] Initializing constitutional session...")
        verdict_000, state = self.stage_000_init(session_id, query)
        print(f"   Verdict: {verdict_000}, F12: {state.floor_scores.get('F12', 0):.2f}")
        
        if verdict_000 == "VOID":
            return {"final_verdict": "VOID", "reason": "000 gate failed"}
        
        print("\n[111] Processing input...")
        verdict_111, state = self.stage_111_sense(session_id, query)
        print(f"   Intent: {state.delta_bundle['intent']['intent']}")
        
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
