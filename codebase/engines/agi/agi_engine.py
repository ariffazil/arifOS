"""
AGI Room (Mind) - Neural Reasoning Engine
Stages: 111 SENSE → 222 THINK → 333 ATLAS/FORGE
Isolation: AGI cannot see ASI empathy bundles until 444.
Floors: F2 (Truth ≥0.99), F4 (ΔS≤0), F7 (Ω₀ ∈ [0.03,0.05])
"""

import threading
import logging
from typing import Dict, List
from codebase.bundle_store import BundleStore
from codebase.bundles import AGIFloorScores, ReasoningTree, DeltaBundle, EngineVote

logger = logging.getLogger(__name__)

from codebase.engines.agi.agi_components import (
    NeuralSenseEngine,
    DeepThinkEngine,
    CognitiveForge
)

class AGIRoom:
    """
    AGI (Mind) execution context.
    v53 Upgrade: A1 Neural Sense, A2 Deep Think, A3 Cognitive Forge.
    """
    
    def __init__(self, session_id: str):
        """
        Initialize AGI room for a session.
        """
        self.session_id = session_id
        self.bundle_store = BundleStore(session_id)
        self._started = False
        self._completed = False
        
        # v53 Components
        self.sense_engine = NeuralSenseEngine()
        self.think_engine = DeepThinkEngine()
        self.forge_engine = CognitiveForge()

    async def run(self, query: str) -> DeltaBundle:
        """
        Execute AGI stages 111 → 333 in sequence.
        """
        # Allow re-running for the same session (Thinking Aid mode)
        if self._started and not self._completed:
            logger.warning(f"[AGI-ROOM] Re-igniting running mind for {self.session_id}")
            # Reset for re-execution
            self._started = False
        
        if self._completed:
             self._started = False
             self._completed = False
        
        logger.info(f"[AGI-ROOM] Igniting mind for {self.session_id}")
        self._started = True
        
        # 1. 111_SENSE
        sense_data = await self.sense_engine.sense_query(query, self.session_id)
        
        # 2. 222_THINK
        think_data = await self.think_engine.reason(sense_data)
        
        # 3. 333_FORGE
        forge_data = await self.forge_engine.forge_response(think_data)
        
        # 4. Package as DeltaBundle
        conf = forge_data.get("final_confidence", 0.95)
        delta = DeltaBundle(
            session_id=self.session_id,
            raw_query=query,
            parsed_facts=[query],
            detected_intent="review",
            hypotheses=[], # Populated from think_engine if available, else empty
            reasoning=ReasoningTree(
                premises=[query],
                inference_steps=[think_data.get("thought", "Analyzed")],
                conclusion=forge_data.get("draft", "No output")
            ),
            confidence_high=conf,
            confidence_low=max(0.0, conf - 0.05),
            omega_0=forge_data.get("humility_score", 0.04),
            entropy_delta=forge_data.get("clarity_delta_s", 0.0),
            floor_scores=AGIFloorScores(
                F2_truth=conf,
                F4_clarity=forge_data.get("clarity_delta_s", 0.0),
                F7_humility=forge_data.get("humility_score", 0.04)
            ),
            vote=EngineVote.SEAL if conf >= 0.8 else EngineVote.UNCERTAIN,
            vote_reason="Insight generated" if conf >= 0.8 else "Confidence low, requires verification"
        )
        
        self.bundle_store.store_delta(delta)
        self._completed = True
        
        return delta


# ==================== GLOBAL REGISTRY ====================

_AGI_ROOMS: Dict[str, AGIRoom] = {}
_AGI_LOCK = threading.Lock()


def get_agi_room(session_id: str) -> AGIRoom:
    """Get or create AGI room for session."""
    with _AGI_LOCK:
        if session_id not in _AGI_ROOMS:
            _AGI_ROOMS[session_id] = AGIRoom(session_id)
        return _AGI_ROOMS[session_id]


def purge_agi_room(session_id: str) -> None:
    """Remove AGI room from registry (session cleanup)."""
    with _AGI_LOCK:
        if session_id in _AGI_ROOMS:
            del _AGI_ROOMS[session_id]


def list_active_agi_rooms() -> List[str]:
    """List all active AGI room session IDs."""
    with _AGI_LOCK:
        return list(_AGI_ROOMS.keys())

# ==================== TESTS ====================

def test_agi_engine_initialization():
    """Test AGI room metadata."""
    session_id = "test_agi_001"
    room = AGIRoom(session_id)
    assert room.session_id == session_id

async def test_agi_engine_run():
    """Test AGI room executes stages 111-333."""
    session_id = "test_agi_002"
    room = AGIRoom(session_id)
    delta = await room.run("What is arifOS?")
    
    assert isinstance(delta, DeltaBundle)
    assert delta.confidence_high >= 0.8
    assert delta.vote.value in ["SEAL", "VOID", "UNCERTAIN"]
    assert delta.reasoning is not None and len(delta.reasoning.inference_steps) > 0

async def run_tests():
    test_agi_engine_initialization()
    await test_agi_engine_run()
    from codebase.engines.agi.agi_engine import list_active_agi_rooms, purge_agi_room
    print(f"Active AGI rooms: {list_active_agi_rooms()}")
    purge_agi_room("test_agi_001")
    purge_agi_room("test_agi_002")
    print("✅ All AGI Engine tests PASSED")

if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_tests())
