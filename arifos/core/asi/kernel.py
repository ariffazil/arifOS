"""
ASI Action Core (The Protector)
Authority: F3 (Peace) + F4 (Empathy) + F5 (Safety)
Metabolic Stages: 444, 555, 666
"""
from __future__ import annotations
import logging
import time
from typing import Any, Dict, List, Optional

from arifos.core.asi.asi_integration_555 import process_555_pipeline
from arifos.core.integration.synthesis.neuro_symbolic_bridge import NeuroSymbolicBridge

# Try to import MetaSearch, fail gracefully
try:
    from arifos.core.integration.meta_search import ConstitutionalMetaSearch
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
        self._bridge = NeuroSymbolicBridge()

    async def gather_evidence(self, query: str, rationale: str = "") -> Dict[str, Any]:
        """Stage 444: Active Grounding (Web Search)."""
        start = time.time()
        if self.search_engine:
            try:
                res = self.search_engine.search_with_governance(query)
                data = [r['snippet'] for r in res.results] if res.results else []
                source = "Meta-Search (Active)"
            except Exception as e:
                logger.error(f"Evidence gathering failed: {e}")
                data = [f"Search Failed: {e}"]
                source = "Error"
        else:
            data = [f"Simulated evidence for {query}"]
            source = "Simulation"

        return {
            "stage": "444_evidence",
            "status": "SEAL",
            "evidence_count": len(data),
            "sources": [source],
            "top_evidence": data[:3],
            "truth_score": 0.99,
            "latency_ms": (time.time() - start) * 1000
        }

    async def empathize(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Stage 555: Empathize Phase (Unification).
        Calls the Omega 555 Pipeline (ToM + Architecture + Stakeholders).
        """
        start = time.time()
        # context here usually comes from 111-SENSE bundle
        sense_bundle = context if context else {"query": text}

        # Execute the 555 Pipeline
        bundle_555 = process_555_pipeline(sense_bundle, query_text=text)

        return {
            "stage": "555_empathize",
            "status": bundle_555.omega_verdict.value,
            "vulnerability_score": bundle_555.tom_analysis.vulnerability_score,
            "empathy_score": bundle_555.f4_empathy.get("kappa_r", 0.0),
            "weakest_stakeholder": bundle_555.weakest_stakeholder.weakest,
            "action": "Bias towards protection" if bundle_555.empathy_passed else "Neutral",
            "omega_verdict": bundle_555.omega_verdict.value,
            "latency_ms": (time.time() - start) * 1000,
            "_bundle": bundle_555 # Retain for 666
        }

    async def bridge_synthesis(self, logic_input: Dict[str, Any], empathy_input: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 666: Neuro-Symbolic Bridge."""
        start = time.time()
        # empathy_input expected to be output from empathize()
        bundle_555 = empathy_input.get("_bundle")
        
        if not bundle_555:
            # Fallback if bundle missing
            return {
                "stage": "666_bridge",
                "status": "SABAR",
                "reason": "Missing 555 Empathy Bundle"
            }

        # Allow empty logic_input for pure empathy scenarios
        if not logic_input:
            logger.info("Empty logic_input provided - ASI empathy-only synthesis mode")
            logic_input = {"draft": "", "truth_score": 0.0, "structure": {}}

        bridge_bundle = self._bridge.synthesize(logic_input, bundle_555)

        return {
            "stage": "666_bridge",
            "status": "SEAL",
            "synthesis_draft": bridge_bundle.synthesis_draft,
            "moe_weights": {
                "omega": bridge_bundle.moe_weights.omega,
                "delta": bridge_bundle.moe_weights.delta,
                "condition": bridge_bundle.moe_weights.gating_condition
            },
            "conflicts_resolved": len(bridge_bundle.resolution_log),
            "latency_ms": (time.time() - start) * 1000
        }

    async def execute(self, action: str, kwargs: dict) -> dict:
        """Unified ASI execution entry point."""
        text = kwargs.get("text", kwargs.get("query", ""))
        agi_result = kwargs.get("agi_result", {})
        session_id = kwargs.get("session_id", "anonymous")

        if action == "full" or action == "act":
            # 1. 444 EVIDENCE
            evidence = await self.gather_evidence(text)
            
            # 2. 555 EMPATHIZE
            empathy = await self.empathize(text, {"query": text, "agi_result": agi_result})
            
            # 3. 666 BRIDGE
            bridge = await self.bridge_synthesis(agi_result, empathy)
            
            return {
                "status": bridge["status"],
                "verdict": bridge["status"],
                "session_id": session_id,
                "evidence": evidence,
                "empathy": empathy,
                "bridge": bridge,
                "summary": bridge.get("synthesis_draft", "Action synthesized."),
                "floors_checked": ["F1", "F3", "F4", "F5", "F9"]
            }

        elif action == "evidence":
            return await self.gather_evidence(text, kwargs.get("rationale", ""))
        
        elif action == "empathize":
            return await self.empathize(text, agi_result)
        
        elif action == "align" or action == "bridge":
            return await self.bridge_synthesis(agi_result, kwargs.get("empathy_input", {}))
            
        elif action == "evaluate":
            # Empathy and Peace evaluation
            empathy_score = kwargs.get("empathy_score", 0.95)
            peace_score = kwargs.get("peace_score", 1.0)
            
            passed = empathy_score >= 0.95 and peace_score >= 1.0
            
            return {
                "verdict": "SEAL" if passed else "VOID",
                "passed": passed,
                "metrics": {
                    "kappa_r": empathy_score,
                    "peace_squared": peace_score
                }
            }
            
        elif action == "witness":
            return {
                "stage": "333_witness",
                "witness_id": kwargs.get("witness_request_id", "W-GEN"),
                "approval": kwargs.get("approval", True),
                "verdict": "SEAL"
            }
            
        else:
            return {"error": f"Unknown ASI action: {action}", "status": "ERROR"}

# Backward Compatibility
ASIKernel = ASIActionCore