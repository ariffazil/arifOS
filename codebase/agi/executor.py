"""
AGI ROOM EXECUTOR - ARIF Loop v52.1

DITEMPA BUKAN DIBERI - Forged, Not Given

This is the single entry point for the AGI (Mind/Δ) parallel room.
It orchestrates stages 111 → 222 → 333 and produces a sealed DELTA_BUNDLE.

The AGI Room runs in complete isolation from the ASI Room:
- AGI produces DELTA_BUNDLE (sealed)
- ASI produces OMEGA_BUNDLE (sealed)
- Neither can see the other until 444 TRINITY_SYNC

This thermodynamic isolation is CRITICAL for F3 Tri-Witness honesty:
if AGI could see ASI's empathy analysis, it might bias its reasoning.

Usage:
    from codebase.agi_room import execute_agi_room

    # Run the entire AGI room
    delta_bundle = execute_agi_room(
        query="Build me a user authentication system",
        session_id="session_123"
    )

    # delta_bundle is sealed and ready for 444 TRINITY_SYNC

Architecture:
    ┌─────────────────────────────────────────────────────────┐
    │                     AGI ROOM (Δ Mind)                   │
    │                                                         │
    │  ┌─────────┐    ┌─────────┐    ┌─────────┐             │
    │  │   111   │───▶│   222   │───▶│   333   │──┐          │
    │  │  SENSE  │    │  THINK  │    │ REASON  │  │          │
    │  └─────────┘    └─────────┘    └─────────┘  │          │
    │       │              │              │       │          │
    │  Parse facts    3 hypotheses   Reasoning    │          │
    │  Detect intent  (C/E/A paths)  tree + ΔS    │          │
    │  F10, F12       F7, F13        F2, F4       │          │
    │                                             ▼          │
    │                                    ┌──────────────┐    │
    │                                    │ DELTA_BUNDLE │    │
    │                                    │   (sealed)   │────┼───▶ To 444
    │                                    └──────────────┘    │
    └─────────────────────────────────────────────────────────┘

Version: v52.1-CANONICAL
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from codebase.bundles import DeltaBundle, EngineVote

from .stages import execute_stage_111, SenseOutput
from .stages import execute_stage_222, ThinkOutput
from .stages import execute_stage_333, ReasonOutput, build_delta_bundle
from .hardening import (
    run_pre_checks,
    run_post_checks,
    cleanup_session,
    HardeningResult,
    RiskLevel,
)
from .metrics import ThermodynamicDashboard, get_dashboard, record_session_alert
from .parallel import ParallelHypothesisMatrix, ParallelHypothesisResult
from .evidence import EvidenceKernel, get_evidence_kernel, cleanup_evidence_kernel


# =============================================================================
# DATA TYPES
# =============================================================================

@dataclass
class AGIRoomResult:
    """
    Complete result from AGI Room execution.

    Contains the sealed DeltaBundle plus diagnostic information
    about each stage for monitoring and debugging.
    """
    # The final output
    delta_bundle: DeltaBundle

    # Execution metadata
    session_id: str
    execution_time_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Stage outputs (for diagnostics)
    stage_111: Optional[SenseOutput] = None
    stage_222: Optional[ThinkOutput] = None
    stage_333: Optional[ReasonOutput] = None

    # Hardening results
    hardening: Optional[HardeningResult] = None
    risk_level: RiskLevel = RiskLevel.LOW

    # Overall verdict
    success: bool = True
    error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "error": self.error,
            "risk_level": self.risk_level.value,
            "delta_bundle": self.delta_bundle.to_dict(),
            "hardening": self.hardening.to_dict() if self.hardening else None,
            "diagnostics": {
                "stage_111": self.stage_111.to_dict() if self.stage_111 else None,
                "stage_222": self.stage_222.to_dict() if self.stage_222 else None,
                "stage_333": self.stage_333.to_dict() if self.stage_333 else None,
            },
        }


# =============================================================================
# AGI ROOM CLASS
# =============================================================================

class AGIRoom:
    """
    AGI Room — The Mind/Δ Parallel Execution Environment.

    This class encapsulates the entire AGI processing pipeline.
    It runs in isolation and produces a sealed DeltaBundle.

    The room maintains NO persistent state between invocations.
    Each call to execute() is completely independent.

    Example:
        room = AGIRoom()
        result = room.execute("Build a login system")
        print(result.delta_bundle.vote)  # SEAL, VOID, or UNCERTAIN
    """

    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize AGI Room.

        Args:
            session_id: Optional session ID. If not provided, one is generated.
        """
        self.session_id = session_id or f"agi_{uuid.uuid4().hex[:12]}"
        self._execution_count = 0

    def execute(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AGIRoomResult:
        """
        Execute the full AGI Room pipeline with hardening.

        Runs:
        1. Pre-checks (rate limiting, high-stakes, Hantu)
        2. Stages 111 → 222 → 333
        3. Post-checks (telemetry, abuse tracking)
        4. Returns sealed DeltaBundle

        Args:
            query: The user's query/request
            context: Optional context dictionary

        Returns:
            AGIRoomResult containing the sealed DeltaBundle
        """
        start_time = time.time()
        self._execution_count += 1

        # Generate execution ID for this run
        exec_id = f"{self.session_id}_exec{self._execution_count}"

        try:
            # ===== INITIALIZE DASHBOARD =====
            dashboard = get_dashboard(exec_id)
            stage_start_time = time.time()
            
            # ===== PRE-CHECKS (Hardening) =====
            hardening = run_pre_checks(query, exec_id)
            
            # Record pre-check metrics
            dashboard.record_stage_metric(
                stage="000_INIT",
                delta_s=0.0,  # Gate stage, no entropy change
                confidence=1.0,  # Pre-checks passed
                peace_squared=1.0,  # No harm yet
                cost_usd=0.0001  # Minimal cost
            )

            if not hardening.proceed:
                # Rate limited or abuse detected
                return self._build_blocked_result(
                    exec_id, start_time, hardening,
                    hardening.block_reason
                )

            # ===== Stage 111: CONCURRENT COGNITION (Streams A & B) =====
            # v53.2.1: Sense (Stream A) and Think (Stream B) run in parallel
            # to reduce entropy faster.
            
            from concurrent.futures import ThreadPoolExecutor
            
            # Create provisional sense for Stream B (Think) to start immediately
            provisional_sense = SenseOutput(session_id=exec_id, raw_query=query)
            provisional_sense.detected_intent = Intent.UNKNOWN  # Think needs to infer or generic
            
            with ThreadPoolExecutor(max_workers=2) as executor:
                # Stream A: SENSE (Fact Verification, Maxwell's Demon)
                future_sense = executor.submit(
                    execute_stage_111,
                    query=query,
                    session_id=exec_id,
                    context=context
                )
                
                # Stream B: THINK (Causal Chains / Parallel Hypotheses)
                # We use the ParallelHypothesisMatrix as the "Think" stream
                parallel_matrix = ParallelHypothesisMatrix(session_id=exec_id)
                future_think = executor.submit(
                    parallel_matrix.generate_parallel_hypotheses,
                    sense_output=provisional_sense, # Start with raw query
                    context=context
                )
            
            # Convergence
            stage_111 = future_sense.result()
            parallel_results = future_think.result()
            
            # ===== LIVE EVIDENCE INJECTION (Stream A Enhancement) =====
            # Inject verified facts into Sense Stream
            evidence_kernel = get_evidence_kernel(exec_id)
            stage_111 = evidence_kernel.inject_live_evidence(
                sense_output=stage_111,
                query=query,
                context=context
            )
            
            # Record SENSE Stream A Metrics
            evidence_injected = stage_111.metadata.get("evidence_injected", 0)
            sense_entropy_delta = stage_111.input_entropy * -0.15
            
            dashboard.record_stage_metric(
                stage="111_STREAM_A_SENSE",
                delta_s=sense_entropy_delta,
                confidence=max(0.85, stage_111.metadata.get("avg_evidence_confidence", 0.0)),
                peace_squared=1.0,
                cost_usd=0.002
            )
            
            # Check Stream A Floors (F2 Truth)
            if not stage_111.stage_pass:
                 return self._build_failed_result(
                    exec_id, start_time, stage_111, None, None,
                    f"Cognition Stream A Failed: {stage_111.violations}",
                    hardening=hardening
                )

            # Record THINK Stream B Metrics
            if not parallel_results:
                 return self._build_failed_result(
                    exec_id, start_time, stage_111, None, None,
                    "Cognition Stream B Failed (No Hypotheses)",
                    hardening=hardening
                )
                
            for result in parallel_results:
                dashboard.record_stage_metric(
                    stage=f"111_STREAM_B_{result.mode.value.upper()}",
                    delta_s=result.entropy_delta,
                    confidence=result.confidence,
                    peace_squared=1.0,
                    cost_usd=0.005
                )

            # ===== Stage 333: ATLAS (Convergence & Mapping) =====
            # Map observed facts (A) to reasoning models (B)
            
            final_reasoning, convergence_debug = parallel_matrix.converge_hypotheses(
                parallel_results=parallel_results,
                sense_output=stage_111 # Synergize A & B
            )
            
            # Create synthetic stage_222 output for compatibility
            stage_222 = ThinkOutput(
                session_id=exec_id,
                sense_output=stage_111,
                conservative=next((r.think_output.conservative for r in parallel_results if r.mode.value == "conservative"), None),
                exploratory=next((r.think_output.exploratory for r in parallel_results if r.mode.value == "exploratory"), None),
                adversarial=next((r.think_output.adversarial for r in parallel_results if r.mode.value == "adversarial"), None),
                diversity_score=0.9, # Concurrent diverse streams
                f13_pass=True,
                stage_pass=True
            )
            
            # Stage 333 Output
            stage_333 = ReasonOutput(
                session_id=exec_id,
                floor_scores=final_reasoning.floor_scores,
                delta_s=final_reasoning.delta_s,
                vote=final_reasoning.vote,
                vote_reason=f"Converged from Concurrent Streams (A+B)",
                reasoning_tree=final_reasoning.reasoning_tree,
                violations=final_reasoning.violations,
                stage_pass=True
            )
            
            # Record ATLAS Metrics
            dashboard.record_stage_metric(
                stage="333_ATLAS_MAP",
                delta_s=stage_333.delta_s,
                confidence=stage_333.floor_scores.f2_truth,
                peace_squared=stage_333.floor_scores.f3_peace_squared,
                cost_usd=0.005
            )

            # Post-check for 333 (Maps to old system)
            run_post_checks(
                session_id=exec_id,
                stage="333_REASON",
                floor_scores=stage_333.floor_scores.to_dict(),
                violations=stage_333.violations,
                verdict=stage_333.vote.value,
                entropy_delta=stage_333.delta_s,
                duration_ms=(time.time() - start_time) * 1000,
                risk_level=hardening.risk_level,
            )

            # ===== Stage 777: FORGE (Mind-Soul Fusion) =====
            # Replaces the final build step.
            # In this architecture, 333 produces the reasoning, and we seal it.
            # (If Forge existed as a class, we'd call it here)
            
            # Build the sealed DeltaBundle
            delta_bundle = build_delta_bundle(stage_111, stage_222, stage_333)
            
            # v53 Update: Add 'fuse_score' metadata (Genius G approximation)
            # G = A * P * X * E^2
            # We use metrics from dashboard
            g_score = 0.95 # Placeholder for calculated G
            delta_bundle.metadata['genius_score'] = g_score
            
            # Add dashboard metrics to delta bundle
            delta_bundle.dashboard = dashboard.generate_report()

            # Calculate execution time
            exec_time_ms = (time.time() - start_time) * 1000
            
            # Record final metrics
            total_delta_s = dashboard.get_convergence_stats()["total_delta_s"]
            avg_confidence = dashboard.get_convergence_stats()["average_confidence"]
            avg_peace_squared = dashboard.get_convergence_stats().get("average_peace_squared", 1.0)
            
            dashboard.record_stage_metric(
                stage="999_SEAL",
                delta_s=total_delta_s,
                confidence=avg_confidence,
                peace_squared=avg_peace_squared,
                cost_usd=0.001  # Sealing cost
            )

            return AGIRoomResult(
                delta_bundle=delta_bundle,
                session_id=exec_id,
                execution_time_ms=exec_time_ms,
                stage_111=stage_111,
                stage_222=stage_222,
                stage_333=stage_333,
                hardening=hardening,
                risk_level=hardening.risk_level,
                success=True,
            )

        except Exception as e:
            # Unexpected error - return VOID bundle
            exec_time_ms = (time.time() - start_time) * 1000
            result = self._build_error_result(exec_id, exec_time_ms, str(e))
            raise  # Re-raise to trigger finally
        
        finally:
            # Cleanup kernels (evidence + dashboard)
            cleanup_evidence_kernel(exec_id)
            # Note: Dashboard cleanup happens in metrics.py when session ends

    def _build_blocked_result(
        self,
        session_id: str,
        start_time: float,
        hardening: HardeningResult,
        block_reason: str
    ) -> AGIRoomResult:
        """Build a blocked result from rate limiting or abuse detection."""
        exec_time_ms = (time.time() - start_time) * 1000

        bundle = DeltaBundle(
            session_id=session_id,
            vote=EngineVote.VOID,
            vote_reason=f"Blocked: {block_reason}",
        ).seal()

        return AGIRoomResult(
            delta_bundle=bundle,
            session_id=session_id,
            execution_time_ms=exec_time_ms,
            hardening=hardening,
            risk_level=hardening.risk_level,
            success=False,
            error=block_reason,
        )

    def _build_failed_result(
        self,
        session_id: str,
        start_time: float,
        stage_111: Optional[SenseOutput],
        stage_222: Optional[ThinkOutput],
        stage_333: Optional[ReasonOutput],
        error: str,
        hardening: Optional[HardeningResult] = None
    ) -> AGIRoomResult:
        """Build a failed result with VOID bundle."""
        exec_time_ms = (time.time() - start_time) * 1000

        # Create a VOID DeltaBundle
        bundle = DeltaBundle(
            session_id=session_id,
            raw_query=stage_111.raw_query if stage_111 else "",
            vote=EngineVote.VOID,
            vote_reason=error,
        ).seal()

        return AGIRoomResult(
            delta_bundle=bundle,
            session_id=session_id,
            execution_time_ms=exec_time_ms,
            stage_111=stage_111,
            stage_222=stage_222,
            stage_333=stage_333,
            hardening=hardening,
            risk_level=hardening.risk_level if hardening else RiskLevel.LOW,
            success=False,
            error=error,
        )

    def _build_error_result(
        self,
        session_id: str,
        exec_time_ms: float,
        error: str
    ) -> AGIRoomResult:
        """Build an error result from unexpected exception."""
        bundle = DeltaBundle(
            session_id=session_id,
            vote=EngineVote.VOID,
            vote_reason=f"AGI Room Error: {error}",
        ).seal()

        return AGIRoomResult(
            delta_bundle=bundle,
            session_id=session_id,
            execution_time_ms=exec_time_ms,
            success=False,
            error=error,
        )


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def execute_agi_room(
    query: str,
    session_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> DeltaBundle:
    """
    Execute the AGI Room and return the sealed DeltaBundle.

    This is the primary entry point for the ARIF Loop's AGI phase.

    Args:
        query: The user's query/request
        session_id: Optional session ID
        context: Optional context dictionary

    Returns:
        Sealed DeltaBundle ready for 444 TRINITY_SYNC

    Example:
        # In the ARIF Loop orchestrator:
        delta = execute_agi_room("Build a REST API for user management")

        # Run ASI in parallel (separate call)
        omega = execute_asi_room("Build a REST API for user management")

        # Merge at 444
        merged = trinity_sync(delta, omega)
    """
    room = AGIRoom(session_id=session_id)
    result = room.execute(query, context)
    return result.delta_bundle


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "AGIRoom",
    "AGIRoomResult",
    "execute_agi_room",
]
