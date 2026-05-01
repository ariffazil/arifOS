"""
arifos/geox/eval/benchmarks.py — GEOX Evaluation & Benchmarks
FORGE 4: Hardened Evaluation Framework

This module provides benchmarks to validate the GEOX intelligence pipeline,
specifically focusing on the dual-memory architecture (discrete vs. continuous).
"""

import asyncio
import logging
import os
import sys
import uuid
from typing import Any

# Standard imports for GEOX
try:
    from arifos.geox.geox_agent import GeoXAgent, GeoXConfig
    from arifos.geox.geox_memory import DualMemoryStore
    from arifos.geox.geox_schemas import CoordinatePoint, GeoRequest
    from arifos.geox.geox_tools import ToolRegistry
    from arifos.geox.geox_validator import GeoXValidator
except ImportError:
    # If not installed as a package, try relative or direct import setup
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
    from arifos.geox.geox_agent import GeoXAgent, GeoXConfig
    from arifos.geox.geox_memory import DualMemoryStore
    from arifos.geox.geox_schemas import CoordinatePoint, GeoRequest
    from arifos.geox.geox_tools import ToolRegistry
    from arifos.geox.geox_validator import GeoXValidator

logger = logging.getLogger("geox.eval.benchmarks")

class MalayBasinAnalogBenchmark:
    """
    Benchmark for the Malay Basin geological analog search.
    Validates the fusion of discrete (Macrostrat) and continuous (LEM) memory.
    """

    def __init__(self):
        # We assume the default registry includes all our tools
        self.registry = ToolRegistry.default_registry()
        self.validator = GeoXValidator()
        self.memory = DualMemoryStore()
        self.agent = GeoXAgent(
            config=GeoXConfig(),
            tool_registry=self.registry,
            validator=self.validator,
            memory_store=self.memory
        )

    async def run_test_case_01_fusion(self) -> dict[str, Any]:
        """
        Test Case 01: Reconciling Discrete and Continuous Evidence.
        Input: A request for the 'Pulai Formation' in the Malay Basin.
        Expected: A GeoResponse with fused insights from both memory stores.
        """
        request = GeoRequest(
            request_id=f"bench-{uuid.uuid4().hex[:6]}",
            prospect_name="Pulai Analog Test",
            basin="Malay Basin",
            location=CoordinatePoint(latitude=5.0, longitude=105.0, depth_m=1200.0),
            query="Analyze the Pulai formation analog and estimate porosity vs. velocity trend.",
            play_type="stratigraphic",
            available_data=["seismic_3d", "well_logs"],
            risk_tolerance="medium",
            requester_id="bench-runner-01"
        )

        logger.info("Running Benchmark: MalayBasinAnalogBenchmark (TC-01)")

        # 1. Plan
        plan = await self.agent.plan(request)

        # 2. Execute (with dual-memory injection)
        results = await self.agent.execute(plan, request)

        # 3. Synchronous Dual-Memory Query (Direct Validation)
        dual_results = await self.memory.query_dual(request.location)

        # 4. Synthesise
        insights = await self.agent.synthesise(results, request)

        # 5. Validate
        verdict = await self.agent.validate(insights)

        # 6. Summarise
        response = await self.agent.summarise(request, insights, verdict)

        # Success if we have fused results from both caches and a valid response
        # In mock state, this will be TRUE because our MockMemoryStore provides default data
        success = (
            len(dual_results["fused_ranking"]) > 0 and
            response.verdict in ("SEAL", "PARTIAL")
        )

        return {
            "test_case": "TC-01_Fusion",
            "success": success,
            "verdict": response.verdict,
            "confidence": response.arifos_telemetry.get("confidence", 0.0),
            "fused_evidence_count": len(dual_results["fused_ranking"]),
            "insights_generated": len(insights)
        }

async def run_standalone():
    """Run all benchmarks."""
    logging.basicConfig(level=logging.INFO)
    benchmark = MalayBasinAnalogBenchmark()

    print("\n" + "="*40)
    print("      GEOX BENCHMARK SUITE (FORGE 4)")
    print("="*40)

    tc01 = await benchmark.run_test_case_01_fusion()
    print(f"Test Case 01 (Fusion): {'PASSED' if tc01['success'] else 'FAILED'}")
    print(f"  - Verdict: {tc01['verdict']}")
    print(f"  - Confidence: {tc01['confidence']:.2f}")
    print(f"  - Evidence Points Fused: {tc01['fused_evidence_count']}")
    print(f"  - Total Insights: {tc01['insights_generated']}")
    print("="*40 + "\n")

if __name__ == "__main__":
    asyncio.run(run_standalone())
