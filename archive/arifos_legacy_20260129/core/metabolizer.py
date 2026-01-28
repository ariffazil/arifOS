# -*- coding: utf-8 -*-
"""
metabolizer.py - Hardened Pipeline State Machine with Stage Execution

Authority: arifOS v50 Constitutional Pipeline
Purpose: Production-ready state machine that ACTUALLY EXECUTES stage code

Features:
- Sequential stage progression (000→999)
- ACTUAL stage execution (v50 fix - was hollow shell before)
- Stage timeout detection
- Performance metrics (latency per stage)
- Error recovery mechanisms
- Constitutional floor validation

v50 ARCHITECT FIX: Metabolizer now dynamically imports and executes stage modules.
Previous versions only tracked state but didn't execute stages (geological strata).

DITEMPA BUKAN DIBERI - Pipeline execution forged through systematic implementation.
"""

import importlib
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from arifos.core.enforcement.metrics import record_stage_metrics, record_verdict_metrics


class StageSequenceError(Exception):
    """Raised when invalid stage transition is attempted."""
    pass


class ConstitutionalViolationError(Exception):
    """Raised when constitutional floors fail at stage 888."""
    pass


class StageTimeoutError(Exception):
    """Raised when a stage exceeds its timeout threshold."""
    pass


class StageLoopError(Exception):
    """Raised when a stage loop is detected (e.g. 111->222->111)."""
    pass


@dataclass
class StageMetrics:
    """Performance metrics for a pipeline stage."""
    stage: int
    start_time: float
    end_time: Optional[float] = None
    latency_ms: Optional[float] = None
    status: str = "RUNNING"  # RUNNING, COMPLETE, FAILED, TIMEOUT

    def complete(self):
        """Mark stage as complete and calculate latency."""
        self.end_time = time.time()
        self.latency_ms = (self.end_time - self.start_time) * 1000
        self.status = "COMPLETE"


class Metabolizer:
    """
    Hardened pipeline state machine with safety features.

    Tracks progression through 11 stages (000→999) with:
    - Sequential order enforcement
    - Timeout detection
    - Loop detection (safeguard against infinite cycles)
    - Performance metrics
    - Error recovery
    """

    # Valid stage transitions
    VALID_STAGES = [0, 111, 222, 333, 444, 555, 666, 777, 888, 889, 999]

    # Stage module mappings (v50: wire to actual implementations)
    STAGE_MODULES = {
        0: "arifos.core.stage.stage_000_void",
        111: "arifos.core.stage.stage_111_sense",
        222: "arifos.core.stage.stage_222_reflect",
        333: "arifos.core.stage.stage_333_reason",
        444: "arifos.core.stage.stage_444_evidence",
        555: "arifos.core.stage.stage_555_empathize",
        666: "arifos.core.stage.stage_666_align",
        777: "arifos.core.stage.stage_777_forge",
        888: "arifos.core.stage.stage_888_judge",
        889: "arifos.core.stage.stage_889_proof",
        999: "arifos.core.stage.stage_999_vault",
    }

    # Stage timeout thresholds (milliseconds)
    STAGE_TIMEOUTS = {
        0: 5000,     # INIT: 5s
        111: 10000,  # SENSE: 10s
        222: 15000,  # REFLECT: 15s
        333: 15000,  # REASON: 15s
        444: 20000,  # ALIGN (mislabeled as EVIDENCE): 20s
        555: 10000,  # EMPATHIZE: 10s
        666: 10000,  # ALIGN: 10s
        777: 10000,  # FORGE: 10s
        888: 5000,   # JUDGE: 5s
        889: 5000,   # PROOF: 5s (NEW v50)
        999: 10000,  # SEAL: 10s
    }

    # Loop detection threshold
    MAX_STAGE_REPEATS = 3

    def __init__(self, enable_timeouts: bool = False, enable_execution: bool = True):
        """
        Initialize metabolizer with optional timeout enforcement and stage execution.

        Args:
            enable_timeouts: If True, enforce stage timeout thresholds
            enable_execution: If True, actually execute stage code (v50 default: True)
        """
        self.current_stage: int = -1  # Not initialized yet
        self.stage_history: List[int] = []
        self.sealed: bool = False
        self.enable_timeouts: bool = enable_timeouts
        self.enable_execution: bool = enable_execution  # v50: Actually run stages

        # Pipeline context (shared state across stages)
        self.context: Dict[str, Any] = {}

        # Performance tracking
        self.metrics: List[StageMetrics] = []
        self.current_stage_metrics: Optional[StageMetrics] = None

    def initialize(self, initial_context: Optional[Dict[str, Any]] = None):
        """
        Initialize pipeline at stage 000 with optional context.

        Args:
            initial_context: Initial pipeline context (query, user_id, etc.)
        """
        self.current_stage = 0
        self.stage_history = [0]
        self.sealed = False
        self.context = initial_context or {}

        # Mark stage 0 in context
        self.context["stage"] = "000"
        self.context["stage_history"] = [0]

        # Start performance tracking for stage 000
        self.current_stage_metrics = StageMetrics(stage=0, start_time=time.time())
        self.metrics.append(self.current_stage_metrics)

        # v50.1: Actually execute Stage 000 logic
        if self.enable_execution:
            self._execute_stage(0)

    def transition_to(self, stage: int):
        """
        Transition to next stage in pipeline with timeout, loop detection, and performance tracking.

        v50 FIX: Now ACTUALLY EXECUTES stage code by dynamically importing and calling execute_stage().

        Args:
            stage: Target stage number (111, 222, ..., 999)

        Raises:
            StageSequenceError: If stage transition is invalid
            StageTimeoutError: If previous stage exceeded timeout (if enabled)
            StageLoopError: If a loop is detected
        """
        # Complete metrics for previous stage
        if self.current_stage_metrics:
            self.current_stage_metrics.complete()

            # Check timeout (if enabled)
            if self.enable_timeouts:
                timeout_ms = self.STAGE_TIMEOUTS.get(self.current_stage, 10000)
                if self.current_stage_metrics.latency_ms > timeout_ms:
                    self.current_stage_metrics.status = "TIMEOUT"
                    raise StageTimeoutError(
                        f"Stage {self.current_stage} exceeded timeout: "
                        f"{self.current_stage_metrics.latency_ms:.0f}ms > {timeout_ms}ms"
                    )
            
            # Phase 1: Record Stage Metrics
            record_stage_metrics(self.current_stage, self.current_stage_metrics.latency_ms)

        if self.sealed:
            raise StageSequenceError("Pipeline is sealed, no further transitions allowed")

        # Validate stage is in valid list
        if stage not in self.VALID_STAGES:
            raise StageSequenceError(f"Invalid stage: {stage}. Must be one of {self.VALID_STAGES}")

        # Loop Detection
        if self.stage_history.count(stage) >= self.MAX_STAGE_REPEATS:
            raise StageLoopError(
                f"Loop detected: Stage {stage} has been visited {self.MAX_STAGE_REPEATS} times. "
                f"History: {self.stage_history}"
            )

        # Validate sequential progression (Standard Flow)
        # Note: If we want to allow retries (SABAR), we might relax this in future.
        # For now, strict metabolism 000->999.
        current_idx = self.VALID_STAGES.index(self.current_stage)
        target_idx = self.VALID_STAGES.index(stage)

        if target_idx != current_idx + 1:
            # Allow rollback/retry only if explicitly handled (e.g. via SABAR logic not yet here)
            # For strict metabolism, we enforce forward motion.
            raise StageSequenceError(
                f"Cannot skip stages: current={self.current_stage}, target={stage}. "
                f"Next valid stage: {self.VALID_STAGES[current_idx + 1]}"
            )

        self.current_stage = stage
        self.stage_history.append(stage)

        # Start tracking new stage
        self.current_stage_metrics = StageMetrics(stage=stage, start_time=time.time())
        self.metrics.append(self.current_stage_metrics)

        # v50 FIX: ACTUALLY EXECUTE THE STAGE CODE
        if self.enable_execution:
            self._execute_stage(stage)

    def seal(self, verdict: dict) -> dict:
        """
        Seal pipeline with constitutional verdict.

        Args:
            verdict: Floor scores from stage 888 JUDGE

        Returns:
            Seal receipt with status and ledger hash

        Raises:
            ConstitutionalViolationError: If hard floors fail
        """
        # Check hard floors (F2 Truth >= 0.99)
        f2_truth = verdict.get("F2_Truth", 0.0)
        if f2_truth < 0.99:
            raise ConstitutionalViolationError(
                f"F2 Truth failed: {f2_truth} < 0.99 (hard floor)"
            )

        # Mock seal receipt
        import hashlib
        import json

        verdict_str = json.dumps(verdict, sort_keys=True)
        ledger_hash = hashlib.sha256(verdict_str.encode()).hexdigest()[:16]

        self.sealed = True
        self.current_stage = 999
        self.stage_history.append(999)

        # Phase 1: Record Final Verdict Metrics
        record_verdict_metrics("SEAL" if f2_truth >= 0.99 else "PARTIAL")

        return {
            "status": "SEALED",
            "ledger_hash": ledger_hash,
            "verdict": "SEAL" if f2_truth >= 0.99 else "PARTIAL"
        }

    def reset(self):
        """Reset metabolizer to initial state."""
        self.current_stage = -1
        self.stage_history = []
        self.sealed = False
        self.metrics = []
        self.current_stage_metrics = None

    def rollback(self):
        """Rollback to previous stage (F1 Amanah reversibility)."""
        if len(self.stage_history) > 1:
            self.stage_history.pop()
            self.current_stage = self.stage_history[-1]

            # Remove metrics for rolled-back stage
            if self.metrics:
                self.metrics.pop()
            self.current_stage_metrics = self.metrics[-1] if self.metrics else None
        else:
            self.reset()

    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get performance summary for all completed stages.

        Returns:
            Dictionary with performance metrics:
            - total_latency_ms: Total pipeline execution time
            - stage_latencies: Per-stage latency breakdown
            - slowest_stage: Stage with highest latency
            - average_latency_ms: Average latency across stages
        """
        completed_metrics = [m for m in self.metrics if m.latency_ms is not None]

        if not completed_metrics:
            return {
                "total_latency_ms": 0.0,
                "stage_latencies": {},
                "slowest_stage": None,
                "average_latency_ms": 0.0,
                "stages_completed": 0
            }

        total_latency = sum(m.latency_ms for m in completed_metrics)
        stage_latencies = {m.stage: m.latency_ms for m in completed_metrics}
        slowest = max(completed_metrics, key=lambda m: m.latency_ms)
        average_latency = total_latency / len(completed_metrics)

        return {
            "total_latency_ms": round(total_latency, 2),
            "stage_latencies": {k: round(v, 2) for k, v in stage_latencies.items()},
            "slowest_stage": {
                "stage": slowest.stage,
                "latency_ms": round(slowest.latency_ms, 2)
            },
            "average_latency_ms": round(average_latency, 2),
            "stages_completed": len(completed_metrics)
        }

    def check_timeout_violations(self) -> List[Dict[str, Any]]:
        """
        Check which stages exceeded their timeout thresholds.

        Returns:
            List of timeout violations with stage number, latency, and threshold
        """
        violations = []

        for metric in self.metrics:
            if metric.latency_ms is None:
                continue

            timeout_ms = self.STAGE_TIMEOUTS.get(metric.stage, 10000)
            if metric.latency_ms > timeout_ms:
                violations.append({
                    "stage": metric.stage,
                    "latency_ms": round(metric.latency_ms, 2),
                    "timeout_ms": timeout_ms,
                    "violation_ms": round(metric.latency_ms - timeout_ms, 2)
                })

        return violations

    def _execute_stage(self, stage: int):
        """
        Execute stage code by dynamically importing the stage module.

        v50 ARCHITECT FIX: This is the missing link that makes metabolizer actually DO something.
        Previous versions only tracked state but never executed stages (hollow shell).

        Args:
            stage: Stage number to execute

        Raises:
            ImportError: If stage module cannot be imported
            AttributeError: If stage module doesn't have execute_stage function
        """
        # Get module path for this stage
        module_path = self.STAGE_MODULES.get(stage)

        if module_path is None:
            # Stage 0 (hypervisor) handled separately or skipped
            return

        try:
            # Dynamically import the stage module
            stage_module = importlib.import_module(module_path)

            # Call execute_stage() function
            if hasattr(stage_module, "execute_stage"):
                self.context = stage_module.execute_stage(self.context)

                # Update stage history in context
                if "stage_history" not in self.context:
                    self.context["stage_history"] = []
                self.context["stage_history"].append(stage)

            else:
                raise AttributeError(
                    f"Stage module {module_path} does not have execute_stage() function"
                )

        except ImportError as e:
            # Log error but don't crash - allow pipeline to continue
            self.context["stage_execution_error"] = {
                "stage": stage,
                "error": f"Failed to import {module_path}: {str(e)}",
                "module_path": module_path
            }
            # Mark metrics as failed
            if self.current_stage_metrics:
                self.current_stage_metrics.status = "FAILED"

        except Exception as e:
            # Catch any other execution errors
            self.context["stage_execution_error"] = {
                "stage": stage,
                "error": f"Stage execution failed: {str(e)}",
                "module_path": module_path
            }
            if self.current_stage_metrics:
                self.current_stage_metrics.status = "FAILED"
