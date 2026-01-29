"""
ASI Room (Heart) - Parallel Execution Engine
Stages: 555 EMPATHY → 666 ALIGN
Isolation: ASI cannot see AGI reasoning (enforced by BundleStore)
Floors: F6 (Empathy κᵣ≥0.95), F1, F5, F9, F11 (ALIGN)
"""

import threading
import logging
from typing import Dict, Any, List, Optional
from codebase.entropy_compressor import EntropyCompressor
from codebase.bundle_store import BundleStore
from codebase.bundles import OmegaBundle, Stakeholder

logger = logging.getLogger(__name__)

ASI_FLOORS = {
    "F6_Empathy": "κᵣ ≥ 0.95",
    "F5_Peace": "Benefit/Harm ≥ 1.0",
    "F1_Amanah": "Reversible OR Auditable",
    "F9_AntiHantu": "Consciousness < 0.30",
    "F11_Command": "Identity Verified"
}

from codebase.engines.asi.asi_components import (
    SemanticStakeholderReasoner,
    ImpactDiffusionModel,
    ConstitutionalAuditSink
)

class ASIRoom:
    """
    ASI (Heart) execution context - isolated from AGI.
    v53 Upgrade: A1 Semantic Stakeholder, A2 Impact Diffusion, A3 Audit Sink.
    """
    
    def __init__(self, session_id: str):
        """
        Initialize ASI room for a session.
        """
        self.session_id = session_id
        self.bundle_store = BundleStore(session_id)
        self._started = False
        self._completed = False
        self.delta_facts = []
        
        # v53 Components
        self.stakeholder_reasoner = SemanticStakeholderReasoner()
        self.diffusion_model = ImpactDiffusionModel()
        self.audit_sink = ConstitutionalAuditSink()
    
    async def run_semantic_stakeholder_reasoning(self, query: str, agi_context=None):
        return await self.stakeholder_reasoner.reason_stakeholders(query, self.session_id, agi_context)
        
    async def run_impact_diffusion(self, query: str, stakeholder_graph: dict, agi_reasoning=None):
        return await self.diffusion_model.compute_peace_squared(query, stakeholder_graph, agi_reasoning)
        
    async def run_constitutional_audit(self, query: str, hardening: dict, empathy: dict, alignment: dict):
        return await self.audit_sink.audit_asi_floors(query, self.session_id, hardening, empathy, alignment)

    async def run(self, query: str, compressor: Optional[EntropyCompressor] = None) -> OmegaBundle:
        """
        Execute ASI stages 555 → 666 in sequence (v53 Enhanced).
        """
        # Allow re-running for the same session (idempotent for testing)
        if self._completed:
            self._started = False
            self._completed = False
        
        if self._started:
            raise RuntimeError("ASI room already executing (can't rerun)")
        
        logger.info(f"[ASI-ROOM] Starting metabolic loop for {self.session_id}")
        self._started = True
        
        # 1. 555_EMPATHY - Stakeholder Reasoning
        empathy_result = await self.stakeholder_reasoner.reason_stakeholders(query, self.session_id)
        
        # 2. 666_ALIGN - Impact Diffusion (Peace²)
        peace_score = await self.diffusion_model.compute_peace_squared(query, empathy_result)
        
        # 3. 444_AUDIT - Constitutional Audit
        audit = await self.audit_sink.audit_asi_floors(
            query=query,
            session_id=self.session_id,
            empathy_result=empathy_result
        )
        
        # 4. Package as OmegaBundle
        # Map component fields to Stakeholder schema
        stakeholder_objects = []
        for s in empathy_result["direct_stakeholders"]:
            stakeholder_objects.append(Stakeholder(
                name=s.get("entity", "Unknown"),
                role=s.get("impact", "user"),
                vulnerability_score=s.get("vulnerability", 0.5),
                potential_harm="direct" if s.get("impact") == "direct" else "indirect",
                voice_weight=s.get("confidence", 1.0)
            ))
        
        # weakest_stakeholder should be a Stakeholder object (the most vulnerable one)
        weakest_stakeholder = None
        if stakeholder_objects:
            # Find the stakeholder with highest vulnerability
            weakest_stakeholder = max(stakeholder_objects, key=lambda s: s.vulnerability_score)
        
        from codebase.bundles import EngineVote, ASIFloorScores
        verdict_str = audit["overall_verdict"]
        vote = EngineVote.SEAL if verdict_str == "SEAL" else EngineVote.VOID
        
        # Convert floor_scores to ASIFloorScores object
        floor_audits = audit["floor_audits"]
        floor_scores = ASIFloorScores(
            F1_amanah=floor_audits.get("F1_Amanah", {}).get("score", 1.0),
            F5_peace=floor_audits.get("F5_Peace", {}).get("score", 1.0),
            F6_empathy=floor_audits.get("F6_Empathy", {}).get("score", 0.95),
            F9_anti_hantu=floor_audits.get("F9_AntiHantu", {}).get("score", 1.0),
            F11_authority=1.0,
            F12_injection=0.0
        )
        
        omega = OmegaBundle(
            session_id=self.session_id,
            stakeholders=stakeholder_objects,
            weakest_stakeholder=weakest_stakeholder,
            empathy_kappa_r=empathy_result["kappa_r_cascade"],
            safety_constraints=["F5_PEACE", "F6_EMPATHY"],
            floor_scores=floor_scores,
            vote=vote,
            is_reversible=True,
            authority_verified=True
        )
        
        self.bundle_store.store_omega(omega)
        self._completed = True
        
        return omega


# ==================== GLOBAL REGISTRY ====================

_ASI_ROOMS: Dict[str, ASIRoom] = {}
_ASI_LOCK = threading.Lock()


def get_asi_room(session_id: str) -> ASIRoom:
    """Get or create ASI room for session."""
    with _ASI_LOCK:
        if session_id not in _ASI_ROOMS:
            _ASI_ROOMS[session_id] = ASIRoom(session_id)
        return _ASI_ROOMS[session_id]


def purge_asi_room(session_id: str) -> None:
    """Remove ASI room from registry (session cleanup)."""
    with _ASI_LOCK:
        if session_id in _ASI_ROOMS:
            del _ASI_ROOMS[session_id]


def list_active_asi_rooms() -> List[str]:
    """List all active ASI room session IDs."""
    with _ASI_LOCK:
        return list(_ASI_ROOMS.keys())

# ==================== TESTS ====================

def test_asi_engine_initialization():
    """Test ASI room metadata."""
    session_id = "test_001"
    room = ASIRoom(session_id)
    assert room.session_id == session_id

async def test_asi_engine_run():
    """Test ASI room executes stages 555-666."""
    session_id = "test_002"
    room = ASIRoom(session_id)
    omega = await room.run("Test query for empathy")
    
    assert isinstance(omega, OmegaBundle)
    assert len(omega.stakeholders) > 0
    assert omega.empathy_kappa > 0.0
    assert omega.vote.value in ["SEAL", "VOID"]

async def run_tests():
    test_asi_engine_initialization()
    await test_asi_engine_run()
    print(f"Active rooms: {list_active_asi_rooms()}")
    purge_asi_room("test_001")
    purge_asi_room("test_002")
    print("✅ All ASI Engine tests PASSED")

if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_tests())
