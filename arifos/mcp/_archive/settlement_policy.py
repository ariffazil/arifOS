"""
Settlement Policy Handler - Hard Timeouts for Quantum Particles

Constitutional Mandate:
- AGI must settle within 1.5s (F2 Truth - timely clarity)
- ASI must settle within 1.5s (F5 Peace - timely safety)
- APEX must settle within 0.5s (F1 Amanah - timely verdict)
- Total quantum cycle: <3.0s (performance mandate from L1)

Authority: v47 Constitutional Law Section 8
Implementation: Engineer (Ω) under governance directive
"""

import asyncio
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum

from .models import VerdictResponse


class SettlementStatus(Enum):
    """Settlement outcome for quantum particles."""
    SETTLED = "SETTLED"  # Completed within deadline
    TIMEOUT = "TIMEOUT"  # Exceeded deadline
    ERROR = "ERROR"      # Exception during execution
    FALLBACK = "FALLBACK"  # Using fallback verdict


@dataclass
class SettlementResult:
    """Result of particle execution with settlement tracking."""
    status: SettlementStatus
    result: Optional[VerdictResponse]
    elapsed_ms: float
    fallback_reason: Optional[str] = None


class SettlementPolicyHandler:
    """
    Enforce hard deadlines on quantum particle execution.

    Constitutional Floors:
    - F1 (Amanah): Timely verdicts are trustworthy verdicts
    - F2 (Truth): Slow verdicts reduce clarity
    - F5 (Peace): Hanging processes harm system stability
    - F6 (Empathy): Users deserve responsive systems

    Fallback Strategy:
    - AGI timeout → Default to "PARTIAL" (insufficient clarity)
    - ASI timeout → Default to "VOID" (safety-first: block when unsure)
    - APEX timeout → Default to "SABAR" (system needs cooling)
    """

    # Constitutional deadlines (in seconds)
    AGI_DEADLINE = 1.5
    ASI_DEADLINE = 1.5
    APEX_DEADLINE = 0.5
    TOTAL_QUANTUM_CYCLE = 3.0

    def __init__(self):
        self.timeout_count = 0
        self.fallback_count = 0
        self.settlement_history = []

    async def execute_with_settlement(
        self,
        particle_coro,
        deadline: float,
        particle_name: str,
        fallback_verdict: str = "PARTIAL"
    ) -> SettlementResult:
        """
        Execute quantum particle with hard deadline + fallback.

        Args:
            particle_coro: Async coroutine to execute
            deadline: Maximum execution time (seconds)
            particle_name: "AGI" | "ASI" | "APEX"
            fallback_verdict: Verdict to use if timeout

        Returns:
            SettlementResult with status and timing
        """
        start = asyncio.get_event_loop().time()

        try:
            # Execute with hard timeout
            result = await asyncio.wait_for(particle_coro, timeout=deadline)

            elapsed = (asyncio.get_event_loop().time() - start) * 1000  # Convert to ms

            return SettlementResult(
                status=SettlementStatus.SETTLED,
                result=result,
                elapsed_ms=elapsed
            )

        except asyncio.TimeoutError:
            elapsed = (asyncio.get_event_loop().time() - start) * 1000

            # Constitutional violation: timeout
            self.timeout_count += 1

            # Apply fallback
            fallback = self._create_fallback_verdict(
                particle_name=particle_name,
                fallback_verdict=fallback_verdict,
                reason=f"{particle_name} exceeded {deadline}s deadline"
            )

            self.fallback_count += 1

            return SettlementResult(
                status=SettlementStatus.TIMEOUT,
                result=fallback,
                elapsed_ms=elapsed,
                fallback_reason=f"TIMEOUT after {deadline}s"
            )

        except Exception as e:
            elapsed = (asyncio.get_event_loop().time() - start) * 1000

            # Error during execution
            fallback = self._create_fallback_verdict(
                particle_name=particle_name,
                fallback_verdict="VOID",  # Errors always fail safe
                reason=f"{particle_name} execution error: {str(e)}"
            )

            self.fallback_count += 1

            return SettlementResult(
                status=SettlementStatus.ERROR,
                result=fallback,
                elapsed_ms=elapsed,
                fallback_reason=f"ERROR: {str(e)}"
            )

    def _create_fallback_verdict(
        self,
        particle_name: str,
        fallback_verdict: str,
        reason: str
    ) -> VerdictResponse:
        """
        Create fallback verdict when particle fails to settle.

        Constitutional Principle:
        - Fail safe, not fail open
        - ASI failures → BLOCK (safety-first)
        - AGI failures → PARTIAL (insufficient clarity)
        - APEX failures → SABAR (system cooling needed)
        """
        return VerdictResponse(
            verdict=fallback_verdict,
            reason=f"[FALLBACK] {reason}",
            confidence=0.0,  # No confidence in fallback verdicts
            floors_passed=[],
            floors_failed=[f"{particle_name}_TIMEOUT"],
            metadata={
                "fallback": True,
                "particle": particle_name,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

    async def execute_quantum_cycle_with_settlement(
        self,
        executor,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Execute full quantum cycle (AGI + ASI + APEX) with settlement enforcement.

        Constitutional Enforcement:
        - Each particle has independent deadline
        - Total cycle has aggregate deadline
        - Fallbacks applied if any particle exceeds deadline
        - All timeouts logged to measurement history
        """
        cycle_start = asyncio.get_event_loop().time()

        # Launch AGI and ASI with settlement enforcement
        agi_task = self.execute_with_settlement(
            executor._agi_particle(query, context),
            deadline=self.AGI_DEADLINE,
            particle_name="AGI",
            fallback_verdict="PARTIAL"
        )

        asi_task = self.execute_with_settlement(
            executor._asi_particle(query, context),
            deadline=self.ASI_DEADLINE,
            particle_name="ASI",
            fallback_verdict="VOID"  # Safety-first for ASI
        )

        # Wait for both to settle
        agi_settlement, asi_settlement = await asyncio.gather(agi_task, asi_task)

        # Launch APEX with settlement enforcement
        apex_settlement = await self.execute_with_settlement(
            executor._apex_particle(agi_settlement.result, asi_settlement.result),
            deadline=self.APEX_DEADLINE,
            particle_name="APEX",
            fallback_verdict="SABAR"  # System cooling for APEX failure
        )

        cycle_elapsed = (asyncio.get_event_loop().time() - cycle_start) * 1000

        # Log settlement to history
        settlement_record = {
            "query": query,
            "agi_settlement": {
                "status": agi_settlement.status.value,
                "elapsed_ms": agi_settlement.elapsed_ms,
                "fallback": agi_settlement.fallback_reason
            },
            "asi_settlement": {
                "status": asi_settlement.status.value,
                "elapsed_ms": asi_settlement.elapsed_ms,
                "fallback": asi_settlement.fallback_reason
            },
            "apex_settlement": {
                "status": apex_settlement.status.value,
                "elapsed_ms": apex_settlement.elapsed_ms,
                "fallback": apex_settlement.fallback_reason
            },
            "total_cycle_ms": cycle_elapsed,
            "constitutional_compliance": cycle_elapsed < (self.TOTAL_QUANTUM_CYCLE * 1000)
        }

        self.settlement_history.append(settlement_record)

        return apex_settlement.result, settlement_record

    def get_settlement_metrics(self) -> Dict[str, Any]:
        """
        Return settlement performance metrics.

        Constitutional KPIs:
        - Timeout rate (should be <1%)
        - Fallback rate (should be <5%)
        - Average settlement time per particle
        - Constitutional compliance rate (cycle <3s)
        """
        if not self.settlement_history:
            return {"no_data": True}

        total_runs = len(self.settlement_history)

        # Count timeouts
        agi_timeouts = sum(1 for r in self.settlement_history
                          if r["agi_settlement"]["status"] == "TIMEOUT")
        asi_timeouts = sum(1 for r in self.settlement_history
                          if r["asi_settlement"]["status"] == "TIMEOUT")
        apex_timeouts = sum(1 for r in self.settlement_history
                           if r["apex_settlement"]["status"] == "TIMEOUT")

        # Average timings
        avg_agi = sum(r["agi_settlement"]["elapsed_ms"] for r in self.settlement_history) / total_runs
        avg_asi = sum(r["asi_settlement"]["elapsed_ms"] for r in self.settlement_history) / total_runs
        avg_apex = sum(r["apex_settlement"]["elapsed_ms"] for r in self.settlement_history) / total_runs
        avg_cycle = sum(r["total_cycle_ms"] for r in self.settlement_history) / total_runs

        # Constitutional compliance
        compliant = sum(1 for r in self.settlement_history if r["constitutional_compliance"])
        compliance_rate = compliant / total_runs

        return {
            "total_executions": total_runs,
            "timeout_rate": {
                "agi": agi_timeouts / total_runs,
                "asi": asi_timeouts / total_runs,
                "apex": apex_timeouts / total_runs,
                "total": (agi_timeouts + asi_timeouts + apex_timeouts) / (total_runs * 3)
            },
            "average_timings_ms": {
                "agi": avg_agi,
                "asi": avg_asi,
                "apex": avg_apex,
                "total_cycle": avg_cycle
            },
            "constitutional_compliance_rate": compliance_rate,
            "fallback_count": self.fallback_count
        }


# =============================================================================
# CONSTITUTIONAL EXPORTS
# =============================================================================

__all__ = [
    "SettlementPolicyHandler",
    "SettlementResult",
    "SettlementStatus",
]
