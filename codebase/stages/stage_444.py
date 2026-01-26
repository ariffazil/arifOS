"""
canonical_core/stage_444.py — Stage 444 TRINITY_SYNC

The Bridge Phase.
Synchronizes the independent AGI (Delta) and ASI (Omega) bundles.
Enforces the Trinity Dissent Law.

Mnemonic: "Init the Genius, Act with Heart, Sync the Bridge, Judge at Apex, Seal in Vault."
"""

from typing import Dict, Any, Tuple
import logging

from codebase.state import SessionState
from codebase.bundles import (
    DeltaBundle,
    OmegaBundle,
    MergedBundle,
    EngineVote,
    AGIFloorScores,
    ASIFloorScores
)

logger = logging.getLogger("STAGE_444")

class Stage444Sync:
    """
    Stage 444: TRINITY SYNC (The Bridge)
    
    Merges AGI and ASI parallel processing streams.
    """
    
    def execute(self, state: SessionState) -> Tuple[str, SessionState]:
        """
        Execute Stage 444 synchronization.
        
        Args:
            state: Current session state containing delta and omega bundles.
            
        Returns:
            Tuple[verdict, updated_state]
        """
        logger.info(f"[444] Syncing Trinity Bridge for session {state.session_id}")
        
        # 1. Hydrate Bundles from State
        delta = self._hydrate_delta(state.delta_bundle or {}, state.session_id)
        omega = self._hydrate_omega(state.omega_bundle or {}, state.session_id)
        
        # 2. Create Merged Bundle
        merged = MergedBundle(
            session_id=state.session_id,
            delta_bundle=delta,
            omega_bundle=omega
        )
        
        # 3. Apply Trinity Dissent Law
        pre_verdict = merged.apply_trinity_dissent_law()
        
        # 4. Seal the Sync
        merged.seal()
        
        logger.info(f"   Consensus Score: {merged.consensus.consensus_score:.2f}")
        logger.info(f"   Pre-Verdict: {pre_verdict} ({merged.pre_verdict_reason})")
        
        # 5. Update State
        new_state = state.set_floor_score("F3_TriWitness", merged.consensus.consensus_score)
        new_state = new_state.to_stage(444)
        
        return pre_verdict, new_state

    def _hydrate_delta(self, data: Dict[str, Any], session_id: str) -> DeltaBundle:
        """Reconstruct DeltaBundle from dict."""
        # Minimal hydration for MVP
        floors = data.get("floor_scores", {})
        return DeltaBundle(
            session_id=session_id,
            vote=EngineVote(data.get("vote", "UNCERTAIN")),
            vote_reason=data.get("vote_reason", ""),
            confidence_high=data.get("confidence", {}).get("high", 0.97),
            floor_scores=AGIFloorScores(
                F2_truth=floors.get("F2_truth", 0.0),
                F4_clarity=floors.get("F4_clarity", 0.0),
                F7_humility=floors.get("F7_humility", 0.04)
            )
        )

    def _hydrate_omega(self, data: Dict[str, Any], session_id: str) -> OmegaBundle:
        """Reconstruct OmegaBundle from dict."""
        floors = data.get("floor_scores", {})
        return OmegaBundle(
            session_id=session_id,
            vote=EngineVote(data.get("vote", "UNCERTAIN")),
            vote_reason=data.get("vote_reason", ""),
            empathy_kappa_r=data.get("empathy_kappa_r", 0.0),
            floor_scores=ASIFloorScores(
                F1_amanah=floors.get("F1_amanah", 0.0),
                F5_peace=floors.get("F5_peace", 1.0),
                F6_empathy=floors.get("F6_empathy", 0.0),
                F11_authority=floors.get("F11_authority", 0.0),
                F12_injection=floors.get("F12_injection", 0.0)
            )
        )

# Singleton
stage_444_sync = Stage444Sync()

def execute_stage_444(state: SessionState) -> Tuple[str, SessionState]:
    return stage_444_sync.execute(state)