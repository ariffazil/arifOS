"""
APEX Room (Soul) - Judicial Consensus Engine
Stages: 444 TRINITY_SYNC
Isolation: APEX is the ONLY layer that sees both Delta and Omega simultaneously.
Floors: F3 (Tri-Witness ≥0.95), F8 (Genius Index ≥0.80)
"""

import threading
import logging
from typing import Dict, Any, List, Optional
from codebase.bundle_store import BundleStore
from codebase.bundles import DeltaBundle, OmegaBundle, MergedBundle

logger = logging.getLogger(__name__)

from codebase.engines.apex.apex_components import (
    JudiciaryValidator,
    TrinityConsensusEngine
)

class APEXRoom:
    """
    APEX (Soul) execution context.
    v53 Upgrade: Trinity Consensus and Judicial Validation.
    """
    
    def __init__(self, session_id: str):
        """
        Initialize APEX room for a session.
        """
        self.session_id = session_id
        self.bundle_store = BundleStore(session_id)
        self._started = False
        self._completed = False
        
        # v53 Components
        self.validator = JudiciaryValidator()
        self.consensus_engine = TrinityConsensusEngine()

    async def run_trinity_sync(self) -> MergedBundle:
        """
        Execute Stage 444: Trinity Sync.
        Retrieves both bundles and computes consensus.
        """
        if self._started:
            raise RuntimeError("APEX room already executing")
        
        logger.info(f"[APEX-ROOM] Conducting Trinity Sync for {self.session_id}")
        self._started = True
        
        delta = self.bundle_store.get_delta()
        omega = self.bundle_store.get_omega()
        
        if not delta or not omega:
            raise ValueError(f"Missing bundles for Trinity Sync: Delta={bool(delta)}, Omega={bool(omega)}")
            
        # 1. Compute Consensus
        consensus = self.consensus_engine.compute_consensus(delta, omega)
        
        # 2. Map Floor Scores
        merged = MergedBundle(
            session_id=self.session_id,
            delta_bundle=delta,
            omega_bundle=omega,
            consensus=consensus
        )
        
        # 3. Apply Trinity Dissent Law
        merged.apply_trinity_dissent_law()
        
        # 4. Final Seal (internal to bundle)
        merged.seal()
        
        self.bundle_store.store_merged(merged)
        self._completed = True
        
        return merged


# ==================== GLOBAL REGISTRY ====================

_APEX_ROOMS: Dict[str, APEXRoom] = {}
_APEX_LOCK = threading.Lock()


def get_apex_room(session_id: str) -> APEXRoom:
    """Get or create APEX room for session."""
    with _APEX_LOCK:
        if session_id not in _APEX_ROOMS:
            _APEX_ROOMS[session_id] = APEXRoom(session_id)
        return _APEX_ROOMS[session_id]


def purge_apex_room(session_id: str) -> None:
    """Remove APEX room from registry (session cleanup)."""
    with _APEX_LOCK:
        if session_id in _APEX_ROOMS:
            if session_id in _APEX_ROOMS:
                del _APEX_ROOMS[session_id]


def list_active_apex_rooms() -> List[str]:
    """List all active APEX room session IDs."""
    with _APEX_LOCK:
        return list(_APEX_ROOMS.keys())

# ==================== TESTS ====================

def test_apex_engine_initialization():
    """Test APEX room metadata."""
    session_id = "test_apex_001"
    room = APEXRoom(session_id)
    assert room.session_id == session_id

async def test_apex_trinity_sync():
    """Test Stage 444 Trinity Sync."""
    session_id = "test_apex_002"
    from codebase.bundle_store import get_store, DeltaBundle, OmegaBundle
    from codebase.bundles import EngineVote, AGIFloorScores
    
    # 1. Setup bundles in store
    store = get_store(session_id)
    delta = DeltaBundle(session_id=session_id, query="test", draft="test", truth_score=0.99, vote=EngineVote.SEAL)
    omega = OmegaBundle(session_id=session_id, weakest_stakeholder="User", empathy_kappa=0.99, vote=EngineVote.SEAL)
    
    store.store_delta(delta)
    store.store_omega(omega)
    
    # 2. Run sync
    room = APEXRoom(session_id)
    merged = await room.run_trinity_sync()
    
    assert merged.pre_verdict == "SEAL"
    assert merged.consensus.votes_agree is True
    assert merged.bundle_hash is not None

async def run_tests():
    test_apex_engine_initialization()
    await test_apex_trinity_sync()
    from codebase.engines.apex.apex_engine import list_active_apex_rooms, purge_apex_room
    print(f"Active APEX rooms: {list_active_apex_rooms()}")
    purge_apex_room("test_apex_001")
    purge_apex_room("test_apex_002")
    print("✅ All APEX Engine tests PASSED")

if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_tests())
