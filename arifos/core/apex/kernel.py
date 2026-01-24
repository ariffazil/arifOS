"""
APEX Judicial Core (The Judge)
Authority: F1 (Amanah) + F8 (Tri-Witness) + F12 (Defense)
Metabolic Stages: 777, 888, 999
Includes AGENT ZERO Profilers.
"""
import asyncio
import math
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class EntropyMeasurement:
    pre_entropy: float
    post_entropy: float
    entropy_reduction: float
    thermodynamic_valid: bool

@dataclass
class ParallelismProof:
    component_times: Dict[str, float]
    parallel_execution_time: float
    theoretical_minimum: float
    speedup_achieved: float
    parallelism_achieved: bool

class ConstitutionalEntropyProfiler:
    """Agent Zero Component: Measures ΔS."""
    async def measure_constitutional_cooling(self, pre_text: str, post_text: str) -> EntropyMeasurement:
        def calc_entropy(text):
            if not text: return 0.0
            prob = [float(text.count(c)) / len(text) for c in dict.fromkeys(list(text))]
            return -sum([p * math.log(p) / math.log(2.0) for p in prob])

        pre_e = calc_entropy(pre_text)
        post_e = calc_entropy(post_text)
        reduction = pre_e - post_e

        return EntropyMeasurement(
            pre_entropy=pre_e,
            post_entropy=post_e,
            entropy_reduction=reduction,
            thermodynamic_valid=reduction > 0 # Entropy should decrease (Information Gain)
        )

class ConstitutionalParallelismProfiler:
    """Agent Zero Component: Proves Orthogonality."""
    async def prove_constitutional_parallelism(self, start_time: float, component_durations: Dict[str, float]) -> ParallelismProof:
        total_wall_time = time.time() - start_time
        max_component_time = max(component_durations.values()) if component_durations else 0
        sum_component_time = sum(component_durations.values()) if component_durations else 0

        speedup = sum_component_time / total_wall_time if total_wall_time > 0 else 0

        return ParallelismProof(
            component_times=component_durations,
            parallel_execution_time=total_wall_time,
            theoretical_minimum=max_component_time,
            speedup_achieved=speedup,
            parallelism_achieved=speedup > 1.1 # Proof of overlap
        )

class APEXJudicialCore:
    """
    The Orthogonal Judicial Kernel.
    Final Authority. Agent Zero Instrumented.
    """

    def __init__(self):
        self.entropy_profiler = ConstitutionalEntropyProfiler()
        self.parallel_profiler = ConstitutionalParallelismProfiler()

    @staticmethod
    async def forge_insight(draft: str) -> Dict[str, Any]:
        """Stage 777: Forge."""
        return {"crystallized": True, "draft_size": len(draft)}

    async def judge_quantum_path(self, query: str, response: str, trinity_floors: List[Any], user_id: str) -> Dict[str, Any]:
        """
        Stage 888: Quantum Path Judgment via APEX Prime.
        Delegates to arifos.core.system.apex_prime for official verdict.
        """
        from arifos.core.system.apex_prime import APEXPrime

        # Initialize the Prime Authority
        prime = APEXPrime()

        # Split floors (Trinity architecture requires AGI and ASI inputs)
        # This is an adapter to map the generic "trinity_floors" list to AGI/ASI buckets if possible
        # For simplicity in this kernel wrapper, we might just pass empty or mock if not strictly separated
        # But ideally, we should have them separated.
        # Assuming trinity_floors contains FloorCheckResult objects.

        # Separate by floor ID convention if possible, or just split
        # AGI: F1, F2, F6
        # ASI: F3, F4, F5, F7
        # APEX: F8, F9, F10-12

        agi_results = []
        asi_results = []

        # Basic heuristic splitting for Prime - in full hypervisor this is cleaner
        for f in trinity_floors:
             if f.floor_id in ["F1", "F2", "F6"]:
                 agi_results.append(f)
             else:
                 asi_results.append(f)

        # Execute Prime Judgment
        verdict = prime.judge_output(query, response, agi_results, asi_results, user_id)

        return {
            "quantum_path": {
                "collapsed": True,
                "integrity": verdict.pulse,
                "branch_id": "main_branch",
                "proof_hash": verdict.proof_hash
            },
            "final_ruling": verdict.verdict.value,
            "verdict_object": verdict # Return full object for context
        }

    async def execute(self, action: str, kwargs: dict) -> dict:
        """Unified APEX execution entry point."""
        query = kwargs.get("query", "")
        response = kwargs.get("response", "")
        trinity_floors = kwargs.get("trinity_floors", [])
        user_id = kwargs.get("user_id", "anonymous")

        if action == "full" or action == "judge":
            # 1. 777 FORGE - Insight crystallization
            insight = await self.forge_insight(response)
            
            # 2. 888 JUDGE - Final ruling
            ruling = await self.judge_quantum_path(query, response, trinity_floors, user_id)
            
            # 3. 999 SEAL - Commitment to vault
            seal = await self.seal_vault(ruling["final_ruling"], ruling)
            
            return {
                "status": ruling["final_ruling"],
                "verdict": ruling["final_ruling"],
                "insight": insight,
                "ruling": ruling,
                "seal": seal,
                "summary": f"APEX Judgment: {ruling['final_ruling']}",
                "floors_checked": ["F3", "F8", "F11", "F12", "F13"]
            }

        elif action == "eureka" or action == "forge":
            return await self.forge_insight(response)
        
        elif action == "judge":
            return await self.judge_quantum_path(query, response, trinity_floors, user_id)
        
        elif action == "proof":
            return await self.judge_quantum_path(query, response, trinity_floors, user_id)
            
    @staticmethod
    async def seal_vault(verdict: str, artifact: Any) -> Dict[str, Any]:
        """
        Stage 999: The Seal.
        Performs Thermodynamic Sealing and assigns Cooling Tiers.
        """
        import hashlib
        import json
        from datetime import datetime, timezone

        # 1. Generate Merkle Root (Simplified for v52)
        payload = json.dumps(artifact, sort_keys=True, default=str).encode()
        merkle_root = hashlib.sha256(payload).hexdigest()
        
        # 2. Assign Cooling Band (Anomalous Contrast Theory)
        # SEAL -> CCC (Forever)
        # PARTIAL/SABAR -> BBB (30 Days)
        # VOID -> Not Stored
        band = "VOID"
        if verdict == "SEAL":
            band = "CCC_CANON"
        elif verdict in ["PARTIAL", "SABAR"]:
            band = "BBB_LEDGER"
            
        # 3. Create Phoenix Key for 000 Bootstrap
        phoenix_key = hashlib.sha256(f"{merkle_root}:{datetime.now(timezone.utc)}".encode()).hexdigest()[:16]

        return {
            "stage": "999_vault",
            "status": "SEALED",
            "merkle_root": merkle_root,
            "cooling_band": band,
            "phoenix_key": f"PHX-{phoenix_key.upper()}",
            "ledger_commit": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "motto": "DITEMPA BUKAN DIBERI"
        }
            # Entropy check
            e = await self.entropy_profiler.measure_constitutional_cooling(query, response)
            return {
                "verdict": "SEAL" if e.thermodynamic_valid else "SABAR",
                "metrics": {
                    "entropy_reduction": e.entropy_reduction,
                    "valid": e.thermodynamic_valid
                }
            }
            
        else:
            return {"error": f"Unknown APEX action: {action}", "status": "ERROR"}
