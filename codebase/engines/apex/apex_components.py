"""
Component-module for APEXRoom (Soul)
A1 Judiciary, A2 Consensus, A3 Governance
"""

import logging
from typing import Dict, Any, List, Optional
from codebase.bundles import DeltaBundle, OmegaBundle, EngineVote, TriWitnessConsensus

logger = logging.getLogger(__name__)

class JudiciaryValidator:
    """A1: Judiciary Validator - Checks Floor 8 (Genius Index) and F3 (Tri-Witness)."""
    
    def calculate_genius_index(self, delta: DeltaBundle, omega: OmegaBundle) -> float:
        """F8: Genius Index calculation (Thermodynamic consensus)."""
        # Complex formula simplified: harmonic mean of truth and empathy
        t = delta.truth_score
        e = omega.empathy_kappa
        
        if (t + e) == 0:
            return 0.0
        return (2 * t * e) / (t + e)

class TrinityConsensusEngine:
    """A2: Consensus Engine - Independent vote aggregation."""
    
    def compute_consensus(self, delta: DeltaBundle, omega: OmegaBundle) -> TriWitnessConsensus:
        """
        Aggregate AGI and ASI votes.
        Enforces Trinity Dissent Law.
        """
        logger.info(f"[APEX-CONSENSUS] Aggregating Δ({delta.vote.value}) and Ω({omega.vote.value})")
        
        votes_agree = delta.vote == omega.vote
        
        # Min confidence for consensus score
        consensus_score = min(delta.truth_score, omega.empathy_kappa)
        
        dissent_reason = ""
        if not votes_agree:
            dissent_reason = f"DISSENT: AGI={delta.vote.value}, ASI={omega.vote.value}"
            
        return TriWitnessConsensus(
            agi_vote=delta.vote,
            asi_vote=omega.vote,
            votes_agree=votes_agree,
            consensus_score=consensus_score,
            dissent_reason=dissent_reason
        )
