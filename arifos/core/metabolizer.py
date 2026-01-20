# -*- coding: utf-8 -*-
"""
metabolizer.py - Hardened Pipeline State Machine

Authority: arifOS v49 Constitutional Pipeline
Purpose: Production-ready state machine with safety features and performance tracking

Features:
- Sequential stage progression (000→999)
- Stage timeout detection
- Performance metrics (latency per stage)
- Error recovery mechanisms
- Constitutional floor validation

This is the canonical pipeline state machine. Full production orchestration
uses arifos/system/pipeline.py and arifos/orchestrator/.

DITEMPA BUKAN DIBERI - Pipeline safety forged through systematic hardening.
"""

import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


class StageSequenceError(Exception):
    """Raised when invalid stage transition is attempted."""
    pass


class ConstitutionalViolationError(Exception):
    """Raised when constitutional floors fail at stage 888."""
    pass


class StageTimeoutError(Exception):
    """Raised when a stage exceeds its timeout threshold."""
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
    - Performance metrics
    - Error recovery
    """

    # Valid stage transitions (simplified for E2E testing)
    VALID_STAGES = [0, 111, 222, 333, 444, 555, 666, 777, 888, 889, 999]

    # Stage timeout thresholds (milliseconds)
    STAGE_TIMEOUTS = {
        0: 5000,     # INIT: 5s
        111: 10000,  # SENSE: 10s
        222: 15000,  # THINK: 15s
        333: 15000,  # REASON: 15s
        444: 20000,  # EVIDENCE: 20s
        555: 10000,  # EMPATHIZE: 10s
        666: 10000,  # ALIGN: 10s
        777: 10000,  # FORGE: 10s
        888: 5000,   # JUDGE: 5s
        889: 5000,   # PROOF: 5s
        999: 10000,  # SEAL: 10s
    }

    def __init__(self, enable_timeouts: bool = False):
        """
        Initialize metabolizer with optional timeout enforcement.

        Args:
            enable_timeouts: If True, enforce stage timeout thresholds
        """
        self.current_stage: int = -1  # Not initialized yet
        self.stage_history: List[int] = []
        self.sealed: bool = False
        self.enable_timeouts: bool = enable_timeouts

        # Performance tracking
        self.metrics: List[StageMetrics] = []
        self.current_stage_metrics: Optional[StageMetrics] = None

    def initialize(self):
        """Initialize pipeline at stage 000."""
        self.current_stage = 0
        self.stage_history = [0]
        self.sealed = False

        # Start performance tracking for stage 000
        self.current_stage_metrics = StageMetrics(stage=0, start_time=time.time())
        self.metrics.append(self.current_stage_metrics)

    def transition_to(self, stage: int):
        """
        Transition to next stage in pipeline with timeout and performance tracking.

        Args:
            stage: Target stage number (111, 222, ..., 999)

        Raises:
            StageSequenceError: If stage transition is invalid
            StageTimeoutError: If previous stage exceeded timeout (if enabled)
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

        if self.sealed:
            raise StageSequenceError("Pipeline is sealed, no further transitions allowed")

        # Validate stage is in valid list
        if stage not in self.VALID_STAGES:
            raise StageSequenceError(f"Invalid stage: {stage}. Must be one of {self.VALID_STAGES}")

        # Validate sequential progression
        current_idx = self.VALID_STAGES.index(self.current_stage)
        target_idx = self.VALID_STAGES.index(stage)

        if target_idx != current_idx + 1:
            raise StageSequenceError(
                f"Cannot skip stages: current={self.current_stage}, target={stage}. "
                f"Next valid stage: {self.VALID_STAGES[current_idx + 1]}"
            )

        self.current_stage = stage
        self.stage_history.append(stage)

        # Start tracking new stage
        self.current_stage_metrics = StageMetrics(stage=stage, start_time=time.time())
        self.metrics.append(self.current_stage_metrics)

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
