# -*- coding: utf-8 -*-
"""
Orthogonal Executor - Parallel AGI||ASI Execution (Phase 8.5)

Constitutional Alignment: F8 (Genius - Quantum Execution)
Authority: Delta (Architect)

Purpose:
- Execute AGI (Mind) and ASI (Heart) in parallel ("quantum superposition")
- Reduce latency (Target: <250ms)
- Aggregate partial results ("particles") for APEX collapse
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

@dataclass
class QuantumParticle:
    """Represents a partial result from a parallel execution thread."""
    server: str
    verdict: str
    floor_scores: Dict[str, Any]
    latency_ms: float
    timestamp: datetime
    data: Dict[str, Any]

@dataclass
class QuantumState:
    """Represents the superposition state before APEX collapse."""
    agi_particle: Optional[QuantumParticle] = None
    asi_particle: Optional[QuantumParticle] = None
    apex_particle: Optional[QuantumParticle] = None
    final_verdict: str = "VOID"
    measurement_time: Optional[datetime] = None

class OrthogonalExecutor:
    """
    Orchestrates parallel execution of constitutional agents.
    """

    def __init__(self, agi_url: str = "http://agi_server:9001", asi_url: str = "http://asi_server:9002"):
        self.agi_url = agi_url
        self.asi_url = asi_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def execute_parallel(self, query: str, context: Dict[str, Any]) -> QuantumState:
        """
        Execute AGI and ASI in parallel.

        Args:
            query: User query
            context: Session context

        Returns:
            QuantumState containing particles and collapsed verdict
        """
        start_time = time.time()

        # Define tasks
        agi_task = self._execute_agi(query, context)
        asi_task = self._execute_asi(query, context)

        # Execute in parallel (Superposition)
        results = await asyncio.gather(agi_task, asi_task, return_exceptions=True)

        agi_result = results[0]
        asi_result = results[1]

        # Process results
        state = QuantumState()
        state.measurement_time = datetime.now()

        # Handle AGI result
        if isinstance(agi_result, Exception):
            logger.error(f"AGI execution failed: {agi_result}")
            state.agi_particle = QuantumParticle(
                server="AGI", verdict="VOID", floor_scores={},
                latency_ms=0, timestamp=datetime.now(), data={"error": str(agi_result)}
            )
        else:
            state.agi_particle = QuantumParticle(
                server="AGI",
                verdict=agi_result.get("verdict", "VOID"),
                floor_scores=agi_result.get("floor_scores", {}),
                latency_ms=agi_result.get("latency_ms", 0),
                timestamp=datetime.now(),
                data=agi_result
            )

        # Handle ASI result
        if isinstance(asi_result, Exception):
            logger.error(f"ASI execution failed: {asi_result}")
            state.asi_particle = QuantumParticle(
                server="ASI", verdict="VOID", floor_scores={},
                latency_ms=0, timestamp=datetime.now(), data={"error": str(asi_result)}
            )
        else:
            state.asi_particle = QuantumParticle(
                server="ASI",
                verdict=asi_result.get("verdict", "VOID"),
                floor_scores=asi_result.get("floor_scores", {}),
                latency_ms=asi_result.get("latency_ms", 0),
                timestamp=datetime.now(),
                data=asi_result
            )

        # Collapse Wavefunction (Simple Logic for Proof of Concept)
        # If either fails (VOID), the whole system fails.
        # Ideally, this happens in APEX, but we pre-calculate for efficiency.
        if state.agi_particle.verdict == "SEAL" and state.asi_particle.verdict == "SEAL":
            state.final_verdict = "SEAL"
        else:
            state.final_verdict = "PARTIAL" # Fallback Logic

        # Create APEX particle (virtual)
        state.apex_particle = QuantumParticle(
            server="APEX",
            verdict=state.final_verdict,
            floor_scores={}, # Aggregated later
            latency_ms=(time.time() - start_time) * 1000,
            timestamp=datetime.now(),
            data={"mode": "orthogonal_collapse"}
        )

        return state

    async def _execute_agi(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Call AGI Server (111->...->333)."""
        response = await self.client.post(
            f"{self.agi_url}/process",
            json={
                "session_id": context.get("session_id", "orthogonal_session"),
                "query": query,
                "stage": "111_SENSE", # Start of AGI chain
                "context": context,
                "floor_scores": {}
            }
        )
        response.raise_for_status()
        return response.json()

    async def _execute_asi(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Call ASI Server (555->...->666)."""
        response = await self.client.post(
            f"{self.asi_url}/process",
            json={
                "session_id": context.get("session_id", "orthogonal_session"),
                "query": query,
                "stage": "555_EMPATHY", # Start of ASI chain
                "context": context,
                "floor_scores": {}
            }
        )
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self.client.aclose()
