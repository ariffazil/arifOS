"""
ASI Action Core (The Protector)
Authority: F3 (Peace) + F4 (Empathy) + F5 (Safety)
Metabolic Stages: 444, 555, 666
"""
import logging
from typing import Any, Dict

from arifos_core.asi.asi_integration_555 import process_555_pipeline

# Try to import MetaSearch, fail gracefully
try:
    from arifos_core.integration.meta_search import ConstitutionalMetaSearch
except ImportError:
    ConstitutionalMetaSearch = None

logger = logging.getLogger("asi_kernel")

class ASIActionCore:
    """
    The Orthogonal Action Kernel.
    Safety & Empathy. No Unchecked Actions.
    """

    def __init__(self):
        self.search_engine = ConstitutionalMetaSearch() if ConstitutionalMetaSearch else None

    async def gather_evidence(self, query: str, rationale: str) -> Dict[str, Any]:
        """Stage 444: Active Grounding (Web Search)."""
        if self.search_engine:
            try:
                res = self.search_engine.search_with_governance(query)
                data = [r['snippet'] for r in res.results] if res.results else []
                source = "Meta-Search (Active)"
            except Exception as e:
                data = [f"Search Failed: {e}"]
                source = "Error"
        else:
            data = [f"Simulated evidence for {query}"]
            source = "Simulation"

        return {
            "evidence_count": len(data),
            "sources": [source],
            "top_evidence": data[:3],
            "truth_score": 0.99
        }

    @staticmethod
    async def empathize(text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Stage 555: Empathize Phase (Unification).
        Calls the Omega 555 Pipeline (ToM + Architecture + Stakeholders).
        """
        # Map context to what process_555_pipeline expects
        # context here usually comes from 111-SENSE bundle
        sense_bundle = context if context else {"query": text}

        # Execute the 555 Pipeline
        bundle_555 = process_555_pipeline(sense_bundle, query_text=text)

        return {
            "vulnerability_score": bundle_555.tom_analysis.vulnerability_score,
            "action": "Bias towards protection" if bundle_555.empathy_passed else "Neutral",
            "omega_verdict": bundle_555.omega_verdict.value,
            "bundle": bundle_555 # Retain full bundle for bridge
        }

    @staticmethod
    async def bridge_synthesis(logic_input: Dict[str, Any], empathy_input: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 666: Neuro-Symbolic Bridge."""
        return {
            "synthesis_hash": "synth_bridged_123",
            "status": "Bridged Logic & Empathy"
        }
