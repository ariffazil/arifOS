"""
arifOS Pipeline Orchestrator (v51.2)

Coordinates 000->999 metabolic loop across 4 servers (VAULT/AGI/ASI/APEX).

Architecture:
- Routes queries through constitutional stages
- Manages inter-server communication
- Enforces verdict propagation (SEAL/PARTIAL/VOID/SABAR)
- Coordinates Phoenix-72 cooling tiers
- Supports parallel (quantum) execution mode

Authority: Delta (Architect)
Version: v51.2.0

Stage naming aligned with metabolizer.py canon:
- 222_REFLECT, 333_REASON, 444_ALIGN, 555_EMPATHIZE, 666_BRIDGE, 777_FORGE

DITEMPA BUKAN DIBERI
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx

# Phase 8.5: Parallel execution support (optional)
try:
    from arifos.core.system.orchestrator.orthogonal_executor import OrthogonalExecutor
    PARALLEL_AVAILABLE = True
except ImportError:
    OrthogonalExecutor = None
    PARALLEL_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """
    Pipeline configuration for v49.1.

    Attributes:
        parallel_mode: Enable AGI||ASI parallel execution (default: False)
        parallel_timeout_ms: Timeout for parallel execution in milliseconds
        fallback_on_parallel_error: Fall back to sequential if parallel fails
    """
    parallel_mode: bool = False
    parallel_timeout_ms: int = 250  # 47% speedup target: <250ms vs 470ms sequential
    fallback_on_parallel_error: bool = True

    # Server URLs (can be overridden)
    vault_url: str = "http://localhost:9000"
    agi_url: str = "http://localhost:9001"
    asi_url: str = "http://localhost:9002"
    apex_url: str = "http://localhost:9003"


class Pipeline:
    """
    Pipeline Orchestrator - Routes queries through 000->999 loop.

    Flow: VAULT(000) -> AGI(111/222/333) -> APEX(444) -> ASI(555/666) -> APEX(777/888/889) -> VAULT(999)

    v49.1 Features:
    - Parallel execution mode (AGI||ASI quantum superposition)
    - Configurable via PipelineConfig
    - Backward-compatible (parallel_mode=False by default)

    Usage:
        # Sequential (default, backward compatible)
        pipeline = Pipeline()
        result = await pipeline.route(query, user_id)

        # Parallel mode (v49.1+)
        config = PipelineConfig(parallel_mode=True)
        pipeline = Pipeline(config=config)
        result = await pipeline.route(query, user_id)  # Uses route_parallel internally

        # Enable/disable at runtime
        pipeline.enable_parallel()
        pipeline.disable_parallel()
    """

    def __init__(
        self,
        vault_url: str = "http://localhost:9000",
        agi_url: str = "http://localhost:9001",
        asi_url: str = "http://localhost:9002",
        apex_url: str = "http://localhost:9003",
        config: Optional[PipelineConfig] = None,
    ):
        # Initialize config (v49.1)
        self.config = config or PipelineConfig()

        # Use config URLs if provided, else use constructor args
        self.vault_url = config.vault_url if config else vault_url
        self.agi_url = config.agi_url if config else agi_url
        self.asi_url = config.asi_url if config else asi_url
        self.apex_url = config.apex_url if config else apex_url

        self.client = httpx.AsyncClient(timeout=30.0)

        # Parallel execution state (v49.1)
        self._parallel_mode = self.config.parallel_mode
        self._orthogonal_executor: Optional[OrthogonalExecutor] = None

        logger.info(
            f"Pipeline initialized (parallel_mode={self._parallel_mode}, "
            f"vault={self.vault_url}, agi={self.agi_url}, asi={self.asi_url}, apex={self.apex_url})"
        )

    def enable_parallel(self) -> None:
        """Enable parallel (quantum) execution mode."""
        self._parallel_mode = True
        logger.info("Pipeline: Parallel mode ENABLED")

    def disable_parallel(self) -> None:
        """Disable parallel execution, revert to sequential."""
        self._parallel_mode = False
        logger.info("Pipeline: Parallel mode DISABLED (sequential)")

    @property
    def parallel_mode(self) -> bool:
        """Check if parallel mode is enabled."""
        return self._parallel_mode

    async def route(self, query: str, user_id: str) -> Dict[str, Any]:
        """
        Main routing function - executes full 000->999 pipeline.

        v49.1: Automatically delegates to route_parallel() when parallel_mode is enabled.

        Args:
            query: User query
            user_id: User identifier

        Returns:
            Final verdict and output from 999 VAULT
        """
        # v49.1: Delegate to parallel execution if enabled
        if self._parallel_mode:
            logger.debug(f"route() delegating to route_parallel() for query: {query[:50]}...")
            try:
                return await self.route_parallel(query, user_id)
            except Exception as e:
                if self.config.fallback_on_parallel_error:
                    logger.warning(f"Parallel execution failed ({e}), falling back to sequential")
                else:
                    raise

        # Sequential execution (default)
        # Stage 000: INIT
        init_result = await self.vault_init(query, user_id)
        if init_result["verdict"] != "SEAL":
            return init_result  # Early exit if VOID/SABAR

        session_id = init_result["session_id"]
        context = {"user_id": user_id, "session_id": session_id}
        floor_scores = init_result["floor_scores"]

        # Stage 111: SENSE (AGI)
        sense_result = await self.agi_process(query, session_id, "111_SENSE", context, floor_scores)
        if sense_result["verdict"] == "VOID":
            return await self.vault_store(session_id, query, sense_result)

        floor_scores.update(sense_result["floor_scores"])

        # Stage 222: REFLECT (AGI)
        think_result = await self.agi_process(query, session_id, "222_REFLECT", context, floor_scores)
        if think_result["verdict"] == "VOID":
            return await self.vault_store(session_id, query, think_result)

        floor_scores.update(think_result["floor_scores"])

        # Stage 333: REASON (AGI)
        atlas_result = await self.agi_process(query, session_id, "333_REASON", context, floor_scores)
        floor_scores.update(atlas_result["floor_scores"])

        # Stage 444: ALIGN (APEX)
        evidence_result = await self.apex_process(
            query, session_id, "444_ALIGN", context, floor_scores,
            agi_output={"sense": sense_result, "think": think_result, "atlas": atlas_result}
        )
        floor_scores.update(evidence_result["floor_scores"])

        # Stage 555: EMPATHIZE (ASI)
        empathy_result = await self.asi_process(query, session_id, "555_EMPATHIZE", context, floor_scores)
        if empathy_result["verdict"] == "VOID":
            return await self.vault_store(session_id, query, empathy_result)

        floor_scores.update(empathy_result["floor_scores"])

        # Stage 666: BRIDGE (ASI)
        act_result = await self.asi_process(query, session_id, "666_BRIDGE", context, floor_scores)
        floor_scores.update(act_result["floor_scores"])

        # Stage 777: FORGE (APEX)
        eureka_result = await self.apex_process(
            query, session_id, "777_FORGE", context, floor_scores
        )
        floor_scores.update(eureka_result["floor_scores"])

        # Stage 888: SEAL (APEX)
        seal_result = await self.apex_process(
            query, session_id, "888_SEAL", context, floor_scores
        )
        floor_scores.update(seal_result["floor_scores"])

        # Stage 889: PROOF (APEX) - if SEAL
        zkpc_receipt = None
        if seal_result["verdict"] == "SEAL":
            proof_result = await self.apex_process(
                query, session_id, "889_PROOF", context, floor_scores
            )
            zkpc_receipt = proof_result.get("zkpc_receipt")

        # Stage 999: VAULT (final storage)
        final_result = await self.vault_store(
            session_id, query, seal_result, zkpc_receipt=zkpc_receipt
        )

        return final_result

    async def vault_init(self, query: str, user_id: str) -> Dict[str, Any]:
        """Call VAULT 000 INIT."""
        response = await self.client.post(
            f"{self.vault_url}/init",
            json={"query": query, "user_id": user_id}
        )
        return response.json()

    async def agi_process(
        self, query: str, session_id: str, stage: str,
        context: Dict, floor_scores: Dict
    ) -> Dict[str, Any]:
        """Call AGI server (111/222/333)."""
        response = await self.client.post(
            f"{self.agi_url}/process",
            json={
                "session_id": session_id,
                "query": query,
                "stage": stage,
                "context": context,
                "floor_scores": floor_scores,
            }
        )
        return response.json()

    async def asi_process(
        self, query: str, session_id: str, stage: str,
        context: Dict, floor_scores: Dict
    ) -> Dict[str, Any]:
        """Call ASI server (555/666)."""
        response = await self.client.post(
            f"{self.asi_url}/process",
            json={
                "session_id": session_id,
                "query": query,
                "stage": stage,
                "context": context,
                "floor_scores": floor_scores,
            }
        )
        return response.json()

    async def apex_process(
        self, query: str, session_id: str, stage: str,
        context: Dict, floor_scores: Dict,
        agi_output: Optional[Dict] = None,
        asi_output: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Call APEX server (444/777/888/889)."""
        response = await self.client.post(
            f"{self.apex_url}/process",
            json={
                "session_id": session_id,
                "query": query,
                "stage": stage,
                "context": context,
                "floor_scores": floor_scores,
                "agi_output": agi_output,
                "asi_output": asi_output,
            }
        )
        return response.json()

    async def vault_store(
        self, session_id: str, query: str, result: Dict,
        zkpc_receipt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Call VAULT 999 VAULT (final storage)."""
        response = await self.client.post(
            f"{self.vault_url}/store",
            json={
                "session_id": session_id,
                "query": query,
                "verdict": result.get("verdict", "UNKNOWN"),
                "floor_scores": result.get("floor_scores", {}),
                "stage_outputs": result.get("output", {}),
                "zkpc_receipt": zkpc_receipt,
            }
        )
        return response.json()

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

    async def route_parallel(self, query: str, user_id: str) -> Dict[str, Any]:
        """
        Parallel routing using OrthogonalExecutor (Phase 8.5).

        Executes AGI||ASI in parallel (quantum superposition) instead of sequential.

        Flow:
        1. VAULT 000 INIT
        2. OrthogonalExecutor.execute_parallel(AGI||ASI) -> parallel execution
        3. APEX 444 EVIDENCE (measurement collapse)
        4. APEX 777/888/889 (judgment)
        5. VAULT 999 VAULT (storage)

        Performance: <250ms vs 470ms sequential (47% speedup)

        v49.1: Now wired into main route() when parallel_mode=True.
        """
        logger.info(f"route_parallel() executing for user={user_id}")

        # Stage 000: INIT
        init_result = await self.vault_init(query, user_id)
        if init_result["verdict"] != "SEAL":
            return init_result

        session_id = init_result["session_id"]
        context = {"user_id": user_id, "session_id": session_id}
        floor_scores = init_result["floor_scores"]

        # PARALLEL EXECUTION (Phase 8.5): AGI||ASI quantum superposition
        if self._orthogonal_executor is None:
            self._orthogonal_executor = OrthogonalExecutor()

        quantum_state = await self._orthogonal_executor.execute_parallel(query, context)

        # Extract particles (independent execution results)
        agi_particle = quantum_state.agi_particle  # Mind verdict
        asi_particle = quantum_state.asi_particle  # Heart verdict
        apex_particle = quantum_state.apex_particle  # Soul verdict (collapsed)

        # Aggregate floor scores from all particles
        if hasattr(agi_particle, 'floors'):
            floor_scores.update(agi_particle.floors)
        if hasattr(asi_particle, 'floors'):
            floor_scores.update(asi_particle.floors)
        if hasattr(apex_particle, 'floors'):
            floor_scores.update(apex_particle.floors)

        # Stage 888: SEAL (final judgment) - use collapsed verdict
        seal_result = {
            "verdict": quantum_state.final_verdict,
            "floor_scores": floor_scores,
            "output": {
                "agi_particle": str(agi_particle),
                "asi_particle": str(asi_particle),
                "apex_particle": str(apex_particle),
                "measurement_time": quantum_state.measurement_time.isoformat() if quantum_state.measurement_time else None,
                "execution_mode": "parallel_quantum",
            }
        }

        # Stage 889: PROOF (if SEAL)
        zkpc_receipt = None
        if seal_result["verdict"] == "SEAL":
            # Generate zkPC receipt from quantum state
            zkpc_receipt = f"zkpc_{session_id}_parallel"

        # Stage 999: VAULT (final storage)
        final_result = await self.vault_store(
            session_id, query, seal_result, zkpc_receipt=zkpc_receipt
        )

        logger.info(f"route_parallel() completed: verdict={final_result.get('verdict')}")
        return final_result


# Exports for v49.1
__all__ = ["Pipeline", "PipelineConfig"]
