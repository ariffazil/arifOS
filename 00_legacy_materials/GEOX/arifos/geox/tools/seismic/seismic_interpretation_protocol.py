"""
SeismicInterpretationProtocol — Interpretation Workflow with ToAC Checkpoints
DITEMPA BUKAN DIBERI

Formal protocol for seismic interpretation ensuring:
  - ToAC compliance at each step
  - Explicit bias auditing
  - Transform chain documentation
  - Human override points

This protocol implements the full Bond et al. (2007) anti-bias workflow
as a state machine with checkpoints.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal
from enum import Enum, auto
import uuid


class ProtocolState(Enum):
    """States in the interpretation protocol."""

    INITIALIZED = auto()
    INPUT_VALIDATED = auto()
    ATTRIBUTES_COMPUTED = auto()
    BIAS_AUDITED = auto()
    INTERPRETATION_GENERATED = auto()
    ALTERNATIVES_DOCUMENTED = auto()
    CONTRAST_ASSESSED = auto()
    COMPLETE = auto()
    REJECTED = auto()


@dataclass
class InterpretationStep:
    """A single step in the interpretation protocol."""

    step_number: int
    step_name: str
    description: str

    # Execution
    status: Literal["PENDING", "IN_PROGRESS", "COMPLETE", "FAILED", "SKIPPED"]
    result: Any | None = None

    # Governance
    checkpoint_passed: bool = False
    override_available: bool = True

    # Documentation
    execution_time_ms: float | None = None
    notes: list[str] = field(default_factory=list)


@dataclass
class InterpretationCheckpoint:
    """A governance checkpoint in the interpretation protocol."""

    checkpoint_id: str
    step_number: int

    # Checkpoint criteria
    criteria: list[str]  # What must be satisfied to pass

    # Assessment
    passed: bool = False
    violations: list[str] = field(default_factory=list)

    # Override
    override_available: bool = True
    overridden: bool = False
    override_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "step_number": self.step_number,
            "criteria": self.criteria,
            "passed": self.passed,
            "violations": self.violations,
            "overridden": self.overridden,
        }


class SeismicInterpretationProtocol:
    """
    Formal protocol for ToAC-governed seismic interpretation.

    The protocol proceeds through states with mandatory checkpoints:

    1. INITIALIZED → INPUT_VALIDATED
       Checkpoint: Verify SEG-Y source (not raster)

    2. INPUT_VALIDATED → ATTRIBUTES_COMPUTED
       Checkpoint: Confirm physical attributes computed before visualization

    3. ATTRIBUTES_COMPUTED → BIAS_AUDITED
       Checkpoint: Run Bond et al. bias audit

    4. BIAS_AUDITED → INTERPRETATION_GENERATED
       Checkpoint: Document confidence and uncertainty

    5. INTERPRETATION_GENERATED → ALTERNATIVES_DOCUMENTED
       Checkpoint: Minimum 3 alternative interpretations documented

    6. ALTERNATIVES_DOCUMENTED → CONTRAST_ASSESSED
       Checkpoint: Verify anomalous contrast ratio within bounds

    7. CONTRAST_ASSESSED → COMPLETE or REJECTED
       Final verdict based on checkpoint results
    """

    def __init__(self, protocol_id: str | None = None):
        self.protocol_id = protocol_id or f"GEOX-PROTO-{uuid.uuid4().hex[:8].upper()}"
        self.state = ProtocolState.INITIALIZED

        self.steps: list[InterpretationStep] = []
        self.checkpoints: list[InterpretationCheckpoint] = []
        self.current_step = 0

        self._init_steps()

    def _init_steps(self) -> None:
        """Initialize the protocol steps."""
        self.steps = [
            InterpretationStep(
                step_number=1,
                step_name="INPUT_VALIDATION",
                description="Validate input source type and quality",
                status="PENDING",
            ),
            InterpretationStep(
                step_number=2,
                step_name="ATTRIBUTE_COMPUTATION",
                description="Compute physical attributes before any visualization",
                status="PENDING",
            ),
            InterpretationStep(
                step_number=3,
                step_name="BIAS_AUDIT",
                description="Run Bond et al. (2007) anti-bias audit",
                status="PENDING",
            ),
            InterpretationStep(
                step_number=4,
                step_name="INTERPRETATION_GENERATION",
                description="Generate interpretation from physical attributes",
                status="PENDING",
            ),
            InterpretationStep(
                step_number=5,
                step_name="ALTERNATIVE_DOCUMENTATION",
                description="Document minimum 3 alternative interpretations",
                status="PENDING",
            ),
            InterpretationStep(
                step_number=6,
                step_name="CONTRAST_ASSESSMENT",
                description="Assess anomalous contrast ratio and conflation risk",
                status="PENDING",
            ),
            InterpretationStep(
                step_number=7,
                step_name="FINAL_VERDICT",
                description="Render final GEOX verdict",
                status="PENDING",
            ),
        ]

        self.checkpoints = [
            InterpretationCheckpoint(
                checkpoint_id=f"{self.protocol_id}-CP1",
                step_number=1,
                criteria=[
                    "Input is SEG-Y format (not raster/image)",
                    "Trace headers are readable",
                    "Data dimensions are valid",
                ],
            ),
            InterpretationCheckpoint(
                checkpoint_id=f"{self.protocol_id}-CP2",
                step_number=2,
                criteria=[
                    "At least 2 physical attributes computed",
                    "Attributes have uncertainty estimates",
                    "Computation chain is documented",
                ],
            ),
            InterpretationCheckpoint(
                checkpoint_id=f"{self.protocol_id}-CP3",
                step_number=3,
                criteria=[
                    "Anchoring bias audit completed",
                    "Confirmation bias audit completed",
                    "Data quality bias audit completed",
                ],
            ),
            InterpretationCheckpoint(
                checkpoint_id=f"{self.protocol_id}-CP4",
                step_number=4,
                criteria=[
                    "Interpretation based on physical attributes",
                    "Confidence is quantified (F7 Humility)",
                    "Uncertainty is documented",
                ],
            ),
            InterpretationCheckpoint(
                checkpoint_id=f"{self.protocol_id}-CP5",
                step_number=5,
                criteria=[
                    "Minimum 3 alternatives documented",
                    "Alternatives are geologically plausible",
                    "Anchoring mitigation is explicit",
                ],
            ),
            InterpretationCheckpoint(
                checkpoint_id=f"{self.protocol_id}-CP6",
                step_number=6,
                criteria=[
                    "Anomalous contrast ratio < 2.0",
                    "Transform chain is fully documented",
                    "No circular references detected",
                ],
            ),
            InterpretationCheckpoint(
                checkpoint_id=f"{self.protocol_id}-CP7",
                step_number=7,
                criteria=[
                    "All prior checkpoints passed or overridden",
                    "Final verdict is documented",
                    "Human override opportunity provided",
                ],
            ),
        ]

    def get_current_step(self) -> InterpretationStep | None:
        """Get the current protocol step."""
        if 0 <= self.current_step < len(self.steps):
            return self.steps[self.current_step]
        return None

    def get_current_checkpoint(self) -> InterpretationCheckpoint | None:
        """Get the checkpoint for the current step."""
        if 0 <= self.current_step < len(self.checkpoints):
            return self.checkpoints[self.current_step]
        return None

    def execute_step(
        self,
        step_result: Any,
        checkpoint_passed: bool = False,
        notes: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Execute the current step and advance to next.

        Args:
            step_result: Result from executing this step
            checkpoint_passed: Whether the checkpoint criteria were met
            notes: Additional notes about execution

        Returns:
            Protocol status after this step
        """
        step = self.get_current_step()
        checkpoint = self.get_current_checkpoint()

        if step is None:
            return self.get_status()

        # Update step
        step.status = "COMPLETE"
        step.result = step_result
        if notes:
            step.notes.extend(notes)
        step.checkpoint_passed = checkpoint_passed

        # Update checkpoint
        if checkpoint:
            checkpoint.passed = checkpoint_passed

        # Advance state
        self._advance_state()

        return self.get_status()

    def _advance_state(self) -> None:
        """Advance to next state based on current checkpoint."""
        checkpoint = self.get_current_checkpoint()

        if checkpoint and not checkpoint.passed and not checkpoint.overridden:
            # Failed checkpoint without override
            self.state = ProtocolState.REJECTED
            return

        # Advance step
        self.current_step += 1

        # Update state
        state_map = {
            0: ProtocolState.INITIALIZED,
            1: ProtocolState.INPUT_VALIDATED,
            2: ProtocolState.ATTRIBUTES_COMPUTED,
            3: ProtocolState.BIAS_AUDITED,
            4: ProtocolState.INTERPRETATION_GENERATED,
            5: ProtocolState.ALTERNATIVES_DOCUMENTED,
            6: ProtocolState.CONTRAST_ASSESSED,
            7: ProtocolState.COMPLETE,
        }

        self.state = state_map.get(self.current_step, ProtocolState.COMPLETE)

    def override_checkpoint(self, reason: str) -> dict[str, Any]:
        """
        Override the current checkpoint.

        F13 SOVEREIGN: Human override of any checkpoint.
        """
        checkpoint = self.get_current_checkpoint()

        if checkpoint is None:
            raise ValueError("No active checkpoint to override")

        if not checkpoint.override_available:
            raise ValueError("This checkpoint cannot be overridden")

        checkpoint.overridden = True
        checkpoint.override_reason = reason
        checkpoint.passed = True  # Mark as passed via override

        self._advance_state()

        return self.get_status()

    def get_status(self) -> dict[str, Any]:
        """Get current protocol status."""
        current_step = self.get_current_step()
        current_checkpoint = self.get_current_checkpoint()

        return {
            "protocol_id": self.protocol_id,
            "state": self.state.name,
            "current_step": self.current_step,
            "total_steps": len(self.steps),
            "step_name": current_step.step_name if current_step else None,
            "checkpoint_id": (current_checkpoint.checkpoint_id if current_checkpoint else None),
            "checkpoint_passed": (current_checkpoint.passed if current_checkpoint else None),
            "can_override": (
                current_checkpoint.override_available if current_checkpoint else False
            ),
            "steps_completed": sum(1 for s in self.steps if s.status == "COMPLETE"),
            "checkpoints_passed": sum(1 for c in self.checkpoints if c.passed),
            "is_complete": self.state in (ProtocolState.COMPLETE, ProtocolState.REJECTED),
            "is_rejected": self.state == ProtocolState.REJECTED,
        }

    def get_full_report(self) -> dict[str, Any]:
        """Get full protocol execution report."""
        return {
            "protocol_id": self.protocol_id,
            "final_state": self.state.name,
            "steps": [
                {
                    "number": s.step_number,
                    "name": s.step_name,
                    "status": s.status,
                    "checkpoint_passed": s.checkpoint_passed,
                    "notes": s.notes,
                }
                for s in self.steps
            ],
            "checkpoints": [c.to_dict() for c in self.checkpoints],
            "summary": {
                "total_steps": len(self.steps),
                "completed": sum(1 for s in self.steps if s.status == "COMPLETE"),
                "checkpoints_passed": sum(1 for c in self.checkpoints if c.passed),
                "checkpoints_overridden": sum(1 for c in self.checkpoints if c.overridden),
                "success": self.state == ProtocolState.COMPLETE,
            },
        }
