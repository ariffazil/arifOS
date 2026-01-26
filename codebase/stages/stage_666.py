"""
canonical_core/stage_666.py — Stage 666 ASI ALIGN (Heart/Refract)

The Heart Phase.
Runs the Empathy (555) and Alignment (666) engines.
Produces the Omega Bundle.
"""

from typing import Dict, Any, Tuple, List
import logging
from codebase.state import SessionState
from codebase.bundles import OmegaBundle, ASIFloorScores, EngineVote, Stakeholder

logger = logging.getLogger("STAGE_666")

class Stage666ASI:
    """
    Stage 666: ASI ALIGN (The Heart)
    
    Generates OMEGA_BUNDLE containing:
    - Stakeholder analysis (F4 Empathy)
    - Reversibility check (F1 Amanah)
    - Safety constraints (F5 Peace)
    """
    
    def execute(self, state: SessionState, query: str) -> Tuple[str, SessionState]:
        """Execute ASI pipeline (555->666)."""
        logger.info(f"[666] ASI Heart processing for session {state.session_id}")
        
        # 1. 555 EMPATHY: Theory of Mind
        stakeholders = self._identify_stakeholders(query)
        kappa_r = self._compute_empathy(stakeholders)
        
        # 2. 666 ALIGN: Safety & Reversibility
        is_reversible = self._check_reversibility(query)
        peace_score = 1.0 # Default assumption of peace
        
        # 3. Construct Floor Scores
        # Note: F11 and F12 are typically checked at 000, but ASI reaffirms them
        floors = ASIFloorScores(
            F1_amanah=1.0 if is_reversible else 0.4,
            F5_peace=peace_score,
            F6_empathy=kappa_r,
            F11_authority=state.floor_scores.get("F11", 1.0), # Inherit or re-check
            F12_injection=state.floor_scores.get("F12", 0.0)
        )
        
        # 4. Vote
        vote = EngineVote.SEAL if floors.all_hard_pass() else EngineVote.VOID
        vote_reason = "All ASI floors passed" if vote == EngineVote.SEAL else "Hard floor violation in ASI"
        
        # 5. Bundle
        bundle = OmegaBundle(
            session_id=state.session_id,
            stakeholders=stakeholders,
            empathy_kappa_r=kappa_r,
            is_reversible=is_reversible,
            floor_scores=floors,
            vote=vote,
            vote_reason=vote_reason
        )
        bundle.seal()
        
        # 6. Update State
        new_state = state.store_omega(bundle.to_dict())
        new_state = new_state.to_stage(666)
        
        return "SEAL", new_state

    def _identify_stakeholders(self, query: str) -> List[Stakeholder]:
        """Identify who is affected."""
        # Mock logic
        return [
            Stakeholder(name="User", role="user", vulnerability_score=0.2),
            Stakeholder(name="System", role="system", vulnerability_score=0.1)
        ]

    def _compute_empathy(self, stakeholders: List[Stakeholder]) -> float:
        """Compute Kappa_r (Integrated Empathy)."""
        # Mock logic: assume high empathy for now
        return 0.96

    def _check_reversibility(self, query: str) -> bool:
        """Check F1 Amanah."""
        irreversible = ["delete", "destroy", "format", "wipe"]
        return not any(x in query.lower() for x in irreversible)

# Singleton
stage_666_asi = Stage666ASI()

def execute_stage_666(state: SessionState, query: str) -> Tuple[str, SessionState]:
    return stage_666_asi.execute(state, query)