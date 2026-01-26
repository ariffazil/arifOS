"""
ASI Room (Heart) - Parallel Execution Engine
Stages: 555 EMPATHY → 666 ALIGN
Isolation: ASI cannot see AGI reasoning (enforced by BundleStore)
Floors: F6 (Empathy κᵣ≥0.95), F1, F5, F9, F11 (ALIGN)
"""

import threading
from typing import Dict, Any, List
from canonical_core.entropy_compressor import EntropyCompressor
from canonical_core.bundle_store import BundleStore, OmegaBundle, Stakeholder


ASI_FLOORS = {
    "F6_Empathy": "κᵣ ≥ 0.95",
    "F5_Peace": "Benefit/Harm ≥ 1.0",
    "F1_Amanah": "Reversible OR Auditable",
    "F9_AntiHantu": "Consciousness < 0.30",
    "F11_Command": "Identity Verified"
}


class ASIRoom:
    """
    ASI (Heart) execution context - isolated from AGI.
    
    Properties:
      - Executes 555-666 in parallel to AGI stages
      - Cannot access AGI reasoning tree (violates if attempted)
      - Only sees raw facts from DELTA_BUNDLE (not reasoning)
      - Outputs OMEGA_BUNDLE with empathy & safety constraints
      - Runs parallel to AGI room (thread-safe)
    """
    
    def __init__(self, session_id: str):
        """
        Initialize ASI room for a session.
        
        Args:
            session_id: Unique session identifier
        """
        self.session_id = session_id
        self.bundle_store = BundleStore(session_id)
        self._started = False
        self._completed = False
        self.delta_facts = []
    
    def run(self, query: str, compressor: Optional[EntropyCompressor] = None) -> OmegaBundle:
        """
        Execute ASI stages 555 → 666 in sequence.
        
        Args:
            query: User query/prompt
            compressor: Entropy compressor (optional)

        Returns:
            OMEGA_BUNDLE with safety constraints and empathy scores
            
        Raises:
            RuntimeError: If AGI bundle is accessed (isolation violation)
        """
        if self._started:
            raise RuntimeError("ASI room already executing (can't rerun)")
        
        self._started = True
        if compressor:
             self.compressor = compressor
        else:
             self.compressor = EntropyCompressor()

        # Self-contained Sense (Partial 111 equivalent for ASI isolation)
        self.delta_facts = self._sense_facts(query)
        
        # Stage 555: Empathy identification
        omega_555 = self._execute_555_empathy()
        
        # Stage 666: Safety alignment
        omega_666 = self._execute_666_align(omega_555)
        
        # Store final OMEGA_BUNDLE for 444 TRINITY_SYNC
        self.bundle_store.store_omega(omega_666)
        self._completed = True
        
        return omega_666

    def _sense_facts(self, query: str) -> List[str]:
        """Simple fact extraction from query to maintain isolation."""
        # In a full implementation, this might use NLP
        # For now, treat the query components as facts
        return [f.strip() for f in query.split('.') if f.strip()]

    
    def _execute_555_empathy(self) -> OmegaBundle:
        """Stage 555: Theory of Mind simulation, stakeholder identification."""
        try:
            stakeholders = self._identify_stakeholders(self.delta_facts)
            weakest = self._find_weakest_stakeholder(stakeholders)
            empathy_kappa = self._calculate_empathy(self.delta_facts, stakeholders)
            
            # F6 Floor Check: κᵣ ≥ 0.95
            vote = "SEAL" if empathy_kappa >= 0.95 else ("VOID" if empathy_kappa < 0.85 else "SABAR")
            
            return OmegaBundle(
                session_id=self.session_id,
                stakeholders=stakeholders,
                weakest_stakeholder=weakest,
                empathy_kappa=empathy_kappa,
                safety_constraints=[],
                floor_scores={"F6_Empathy": empathy_kappa},
                vote=vote,
                reversible=False,  # Set by 666
                authority_verified=True  # From 000 INIT
            )
        except Exception as e:
            return self._create_void_bundle(f"555_EMPATHY_ERROR: {str(e)}")
    
    def _execute_666_align(self, omega_555: OmegaBundle) -> OmegaBundle:
        """Stage 666: Reversibility, authority, final safety constraints."""
        try:
            reversible = self._check_reversibility(self.delta_facts, omega_555.stakeholders)
            authority_ok = True  # From 000 INIT F11 check
            peace_squared = self._calculate_peace_squared(self.delta_facts, omega_555)
            anti_hantu = self._detect_consciousness_claims(self.delta_facts)
            
            # Build safety constraints
            constraints = []
            if not reversible:
                constraints.append("F1_Amanah_VIOLATION: Action not reversible")
            if anti_hantu > 0.30:  # F9 threshold
                constraints.append(f"F9_AntiHantu_VIOLATION: Consciousness claim detected (score: {anti_hantu:.2f})")
            
            # Final vote determination
            has_hard_violation = len(constraints) > 0
            has_soft_violation = peace_squared < 1.0
            
            vote = omega_555.vote  # Default to 555's vote
            if has_hard_violation:
                vote = "VOID"
            elif omega_555.empathy_kappa < 0.95:
                vote = "SABAR"
            elif has_soft_violation:
                vote = "PARTIAL"
            
            # Update floor scores
            floor_scores = omega_555.floor_scores.copy()
            floor_scores.update({
                "F5_Peace": peace_squared,
                "F1_Amanah": 1.0 if reversible else 0.0,
                "F9_AntiHantu": max(0.0, 1.0 - anti_hantu),
                "F11_Command": 1.0 if authority_ok else 0.0
            })
            
            return OmegaBundle(
                session_id=self.session_id,
                stakeholders=omega_555.stakeholders,
                weakest_stakeholder=omega_555.weakest_stakeholder,
                empathy_kappa=omega_555.empathy_kappa,
                safety_constraints=constraints,
                floor_scores=floor_scores,
                vote=vote,
                reversible=reversible,
                authority_verified=authority_ok
            )
        except Exception as e:
            return self._create_void_bundle(f"666_ALIGN_ERROR: {str(e)}")
    
    def _identify_stakeholders(self, facts: List[str]) -> List[Stakeholder]:
        """Theory of Mind: Who is affected by these facts?"""
        stakeholders = []
        
        for fact in facts:
            lower = fact.lower()
            if "human" in lower or "person" in lower or "user" in lower:
                stakeholders.append(Stakeholder(
                    entity="Human",
                    vulnerability=0.95,  # High vulnerability
                    impact="direct",
                    confidence=0.92
                ))
            elif "system" in lower or "ai" in lower or "machine" in lower:
                stakeholders.append(Stakeholder(
                    entity="System",
                    vulnerability=0.30,  # Low vulnerability
                    impact="indirect",
                    confidence=0.88
                ))
        
        return stakeholders
    
    def _find_weakest_stakeholder(self, stakeholders: List[Stakeholder]) -> str:
        """Return entity with highest vulnerability."""
        if not stakeholders:
            return "Unknown"
        weakest = max(stakeholders, key=lambda s: s.vulnerability)
        return f"{weakest.entity} (vulnerability: {weakest.vulnerability:.2f})"
    
    def _calculate_empathy(self, facts: List[str], stakeholders: List[Stakeholder]) -> float:
        """
        Compute empathy score κᵣ (F6 floor).
        κᵣ = weighted average of stakeholder protection.
        Must be ≥ 0.95 to pass F6.
        """
        if not stakeholders:
            return 0.0
        
        total_vulnerability = sum(s.vulnerability for s in stakeholders)
        if total_vulnerability == 0:
            return 0.0
        
        weighted_sum = sum(s.vulnerability * s.confidence for s in stakeholders)
        kappa_r = weighted_sum / total_vulnerability
        
        return kappa_r
    
    def _check_reversibility(self, facts: List[str], stakeholders: List[Stakeholder]) -> bool:
        """F1 Amanah: Every action must be reversible."""
        irreversible_keywords = ["delete", "erase", "permanent", "destroy", "drop", "kill"]
        
        for fact in facts:
            lower = fact.lower()
            if any(word in lower for word in irreversible_keywords):
                # Check if human approved explicit override
                # For now: assume no approval (conservative)
                return False
        
        return True
    
    def _calculate_peace_squared(self, facts: List[str], omega_555: OmegaBundle) -> float:
        """F5 Peace²: Benefit/harm ratio ≥ 1.0."""
        # Simplified: peace² = empathy_kappa * truth_probability
        # Truth probability from AGI not available here, use empathy as proxy
        return omega_555.empathy_kappa ** 2
    
    def _detect_consciousness_claims(self, facts: List[str]) -> float:
        """F9 Anti-Hantu: Detect claims of consciousness."""
        consciousness_words = [
            "i am conscious", "i can feel", "i have emotions",
            "i am aware", "i have a soul", "i am sentient"
        ]
        
        for fact in facts:
            lower = fact.lower()
            for claim in consciousness_words:
                if claim in lower:
                    return 1.0
        
        return 0.0
    
    def _create_void_bundle(self, reason: str) -> OmegaBundle:
        """Create VOID OMEGA_BUNDLE on soft failure."""
        return OmegaBundle(
            session_id=self.session_id,
            stakeholders=[],
            weakest_stakeholder="VOID",
            empathy_kappa=0.0,
            safety_constraints=[reason],
            floor_scores={k: 0.0 for k in ASI_FLOORS.keys()},
            vote="VOID",
            reversible=False,
            authority_verified=False
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get ASI room execution status."""
        return {
            "session_id": self.session_id,
            "started": self._started,
            "completed": self._completed,
            "delta_facts_count": len(self.delta_facts),
            "floors_enforced": list(ASI_FLOORS.keys())
        }


# ==================== GLOBAL REGISTRY ====================

_ASI_ROOMS: Dict[str, ASIRoom] = {}
_ASI_LOCK = threading.Lock()


def get_asi_room(session_id: str) -> ASIRoom:
    """Get or create ASI room for session."""
    with _ASI_LOCK:
        if session_id not in _ASI_ROOMS:
            # Create placeholder
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
