# -*- coding: utf-8 -*-
"""
metabolizer.py - Pipeline State Machine for E2E Testing

Authority: arifOS v49 Constitutional Pipeline
Purpose: Minimal state machine for tracking pipeline stage progression (000→999)

This is a lightweight wrapper for E2E testing. Full production orchestration
uses arifos/system/pipeline.py and arifos/orchestrator/.
"""

from typing import List, Optional


class StageSequenceError(Exception):
    """Raised when invalid stage transition is attempted."""
    pass


class ConstitutionalViolationError(Exception):
    """Raised when constitutional floors fail at stage 888."""
    pass


class Metabolizer:
    """
    Minimal pipeline state machine for testing.

    Tracks progression through 11 stages (000→999) and enforces sequential order.
    """

    # Valid stage transitions (simplified for E2E testing)
    VALID_STAGES = [0, 111, 222, 333, 444, 555, 666, 777, 888, 889, 999]

    def __init__(self):
        """Initialize metabolizer with no active stage."""
        self.current_stage: int = -1  # Not initialized yet
        self.stage_history: List[int] = []
        self.sealed: bool = False

    def initialize(self):
        """Initialize pipeline at stage 000."""
        self.current_stage = 0
        self.stage_history = [0]
        self.sealed = False

    def transition_to(self, stage: int):
        """
        Transition to next stage in pipeline.

        Args:
            stage: Target stage number (111, 222, ..., 999)

        Raises:
            StageSequenceError: If stage transition is invalid
        """
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

    def rollback(self):
        """Rollback to previous stage (F1 Amanah reversibility)."""
        if len(self.stage_history) > 1:
            self.stage_history.pop()
            self.current_stage = self.stage_history[-1]
        else:
            self.reset()
