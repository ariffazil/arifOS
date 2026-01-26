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
    from canonical_core.agi_room import execute_agi_room

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

from canonical_core.bundles import DeltaBundle, EngineVote

from .stage_111_sense import execute_stage_111, SenseOutput
from .stage_222_think import execute_stage_222, ThinkOutput
from .stage_333_reason import execute_stage_333, ReasonOutput, build_delta_bundle
from .hardening import (
    run_pre_checks,
    run_post_checks,
    cleanup_session,
    HardeningResult,
    RiskLevel,
)


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
            # ===== PRE-CHECKS (Hardening) =====
            hardening = run_pre_checks(query, exec_id)

            if not hardening.proceed:
                # Rate limited or abuse detected
                return self._build_blocked_result(
                    exec_id, start_time, hardening,
                    hardening.block_reason
                )

            # ===== Stage 111: SENSE =====
            stage_111 = execute_stage_111(
                query=query,
                session_id=exec_id,
                context=context
            )

            # Post-check for 111
            run_post_checks(
                session_id=exec_id,
                stage="111_SENSE",
                floor_scores={"F10": 1.0 if stage_111.f10_ontology_pass else 0.0,
                              "F12": 1.0 - stage_111.f12_injection_risk},
                violations=stage_111.violations,
                verdict="PASS" if stage_111.stage_pass else "FAIL",
                entropy_delta=stage_111.input_entropy,
                duration_ms=hardening.check_duration_ms,
                risk_level=hardening.risk_level,
            )

            # If SENSE fails hard (F10/F12), short-circuit
            if not stage_111.stage_pass:
                return self._build_failed_result(
                    exec_id, start_time, stage_111, None, None,
                    f"Stage 111 failed: {stage_111.violations}",
                    hardening=hardening
                )

            # ===== Stage 222: THINK =====
            stage_222 = execute_stage_222(
                sense_output=stage_111,
                session_id=exec_id,
                context=context
            )

            # Post-check for 222
            run_post_checks(
                session_id=exec_id,
                stage="222_THINK",
                floor_scores={"F7": stage_222.hypotheses[0].confidence if stage_222.hypotheses else 0.0,
                              "F13": stage_222.diversity_score},
                violations=stage_222.violations,
                verdict="PASS" if stage_222.stage_pass else "FAIL",
                entropy_delta=0.0,
                duration_ms=(time.time() - start_time) * 1000,
                risk_level=hardening.risk_level,
            )

            # If THINK fails hard, short-circuit
            if not stage_222.stage_pass:
                return self._build_failed_result(
                    exec_id, start_time, stage_111, stage_222, None,
                    f"Stage 222 failed: {stage_222.violations}",
                    hardening=hardening
                )

            # ===== Stage 333: REASON =====
            stage_333 = execute_stage_333(
                sense_output=stage_111,
                think_output=stage_222,
                session_id=exec_id
            )

            # Post-check for 333
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

            # Build the sealed DeltaBundle
            delta_bundle = build_delta_bundle(stage_111, stage_222, stage_333)

            # Calculate execution time
            exec_time_ms = (time.time() - start_time) * 1000

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
            return self._build_error_result(exec_id, exec_time_ms, str(e))

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
