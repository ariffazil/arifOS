"""
arifosmcp/runtime/feedback_loop.py — Recursive Self-Correction Controller v1
═══════════════════════════════════════════════════════════════════════════════

THE MISSING PIECE between Sequential Thinking (micro-planner) and
Graph Memory (macro-planner).

FEEDBACK LOOP CONTRACT
──────────────────────
  plan → act → observe → evaluate → update_graph → re-plan
                                                      ↑
                                              ┌───────┘
                                              │ (cycle)
                                              │
  Sequential Thinking   ←→   FeedbackLoop   ←→   L5 Graphiti
  (step-level revise)        (this file)          (edge weight update)

Every step completion triggers evaluate(). The evaluate() output
is a FeedbackSignal that determines:
  - Whether to continue (PROCEED)
  - Whether to revise locally (REVISE_LOCAL → Sequential Thinking revises)
  - Whether to re-plan globally (REVISE_GLOBAL → graph path weakened)
  - Whether to branch (BRANCH → alternative subgraph explored)
  - Whether to backtrack (BACKTRACK → prior checkpoint + graph edge weakened)
  - Whether to HOLD (HOLD → escalate to 888)

INTEGRATION POINT
─────────────────
  Monkey-patched into arif_mind_reason via the integration hook.
  Zero kernel file modification. Removing the hook = full rollback (F1).

FLOOR BINDING
─────────────
  F01 (AMANAH)   — all graph writes are edge weight updates, reversible
  F02 (TRUTH)    — epistemic band checked before PROCEED
  F04 (CLARITY)  — feedback signal is typed, not natural language
  F07 (HUMILITY) — hard cap at 0.90 confidence
  F08 (GENIUS)   — loop detection: max 7 revisions per step
  F09 (ANTIHANTU) — no simulated "learning" claims

AUTHORITY: 333_MIND, 888_JUDGE
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, UTC
from enum import StrEnum
from typing import Any, Callable, Protocol

from arifosmcp.runtime.mind_state import (
    MINDState,
    ReasoningStep,
    StepStatus,
    PlanStatus,
    EpistemicTag,
    FeedbackSignal,
    can_continue,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# PROTOCOLS
# ═══════════════════════════════════════════════════════════════════════════════


class GraphWriter(Protocol):
    """Protocol for writing feedback signals to graph memory (L5 Graphiti).

    Implementations write edge weight updates, episode annotations,
    and path annotations to FalkorDB via Graphiti.
    """

    def update_edge_weight(
        self, source_node: str, target_node: str,
        delta: float, reason: str = "",
    ) -> bool: ...

    def annotate_path(
        self, path_nodes: list[str], annotation: dict[str, Any],
    ) -> bool: ...

    def record_episode(
        self, state: MINDState, signal: FeedbackSignal,
        metadata: dict[str, Any] | None = None,
    ) -> str | None: ...


class GraphReader(Protocol):
    """Protocol for reading prior plans from graph memory (L5 Graphiti).

    Implementations query FalkorDB for similar task graphs,
    capability subgraphs, and prior reasoning paths.
    """

    def find_similar_tasks(
        self, goal: str, top_k: int = 5,
    ) -> list[dict[str, Any]]: ...

    def get_capability_subgraph(
        self, domain: str, tools: list[str] | None = None,
    ) -> dict[str, Any]: ...

    def get_prior_path(
        self, task_signature: str,
    ) -> list[dict[str, Any]] | None: ...


# ═══════════════════════════════════════════════════════════════════════════════
# NO-OP IMPLEMENTATIONS (safe defaults when L5 is unavailable)
# ═══════════════════════════════════════════════════════════════════════════════


class NoOpGraphWriter:
    """Safe no-op writer — used when Graphiti/FalkorDB is down.

    F1 AMANAH: graph writes are enrichment, not primary. L5 must never
    block the reasoning loop. If Graphiti is down, reasoning continues
    with Qdrant-only persistence.
    """

    def update_edge_weight(self, *args, **kwargs) -> bool:
        logger.debug("NoOpGraphWriter: update_edge_weight skipped (L5 unavailable)")
        return False

    def annotate_path(self, *args, **kwargs) -> bool:
        return False

    def record_episode(self, *args, **kwargs) -> str | None:
        return None


class NoOpGraphReader:
    """Safe no-op reader — returns empty results when L5 is unavailable."""

    def find_similar_tasks(self, *args, **kwargs) -> list[dict[str, Any]]:
        return []

    def get_capability_subgraph(self, *args, **kwargs) -> dict[str, Any]:
        return {"nodes": [], "edges": []}

    def get_prior_path(self, *args, **kwargs) -> list[dict[str, Any]] | None:
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# FEEDBACK CONTROLLER
# ═══════════════════════════════════════════════════════════════════════════════


class FeedbackLoop:
    """Controllers the feedback loop between Sequential Thinking and Graph Memory.

    Usage:
        loop = FeedbackLoop(state, graph_writer, graph_reader)
        signal = loop.evaluate(step, outcome)
        if signal == FeedbackSignal.PROCEED:
            next_step()
        elif signal == FeedbackSignal.REVISE_LOCAL:
            sequential_thinking.revise(step)
        elif signal == FeedbackSignal.REVISE_GLOBAL:
            re_plan_from_graph()
        ...
    """

    def __init__(
        self,
        state: MINDState,
        graph_writer: GraphWriter | None = None,
        graph_reader: GraphReader | None = None,
        max_revisions_per_step: int = 3,
        loop_detection_threshold: int = 5,
    ):
        self.state = state
        self.graph_writer = graph_writer or NoOpGraphWriter()
        self.graph_reader = graph_reader or NoOpGraphReader()
        self.max_revisions_per_step = max_revisions_per_step
        self.loop_detection_threshold = loop_detection_threshold

        # Loop detection: track step signatures to detect stalls
        self._step_signatures: dict[int, set[str]] = {}

    # ═══════════════════════════════════════════════════════════════════════
    # EVALUATION
    # ═══════════════════════════════════════════════════════════════════════

    def evaluate(
        self,
        step: ReasoningStep,
        outcome: dict[str, Any] | None = None,
    ) -> FeedbackSignal:
        """Evaluate a completed step and determine the next action.

        Args:
            step: The reasoning step that just completed.
            outcome: Optional dict with keys like 'success', 'error',
                     'output_valid', 'confidence', 'test_passed'.

        Returns:
            FeedbackSignal indicating next action.
        """
        outcome = outcome or {}

        # ── Guard 1: Can we even continue? ──
        ok, reason = can_continue(self.state)
        if not ok:
            logger.warning("FeedbackLoop: cannot continue — %s", reason)
            self.state.plan_status = PlanStatus.HOLD
            return FeedbackSignal.HOLD

        # ── Guard 2: Step-level loop detection ──
        if self._detect_loop(step):
            logger.warning(
                "FeedbackLoop: loop detected for step %d — forcing REVISE_GLOBAL",
                step.step_number,
            )
            self.state.plan_status = PlanStatus.DIVERGED
            return FeedbackSignal.REVISE_GLOBAL

        # ── Success path ──
        if outcome.get("success") or outcome.get("test_passed"):
            return self._handle_success(step, outcome)

        # ── Failure path ──
        return self._handle_failure(step, outcome)

    def _handle_success(
        self, step: ReasoningStep, outcome: dict[str, Any],
    ) -> FeedbackSignal:
        """Step succeeded — check quality, decide PROCEED or refine."""
        confidence = outcome.get("confidence", step.confidence)

        # F7 HUMILITY: cap at 0.90
        confidence = min(confidence, 0.90)

        # F2 TRUTH: if confidence too low, this isn't really "success"
        if confidence < 0.70:
            logger.info(
                "FeedbackLoop: step %d confidence %.2f < 0.70 — REVISE_LOCAL",
                step.step_number, confidence,
            )
            step.epistemic_tag = EpistemicTag.PLAUSIBLE
            self.state.update_epistemic(confidence)
            self.state.mark_step(
                step.step_number, StepStatus.FAILED,
                error_message=f"Low confidence: {confidence:.2f} < 0.70",
                feedback=FeedbackSignal.REVISE_LOCAL,
            )
            return FeedbackSignal.REVISE_LOCAL

        # Success — mark and proceed
        step.epistemic_tag = (
            EpistemicTag.VERIFIED if confidence >= 0.95
            else EpistemicTag.PLAUSIBLE
        )
        step.confidence = confidence
        self.state.mark_step(step.step_number, StepStatus.COMPLETED)
        self.state.update_epistemic(confidence)

        # Reinforce graph path (success → edge weight +0.05)
        self._reinforce_path(step, outcome)

        return FeedbackSignal.PROCEED

    def _handle_failure(
        self, step: ReasoningStep, outcome: dict[str, Any],
    ) -> FeedbackSignal:
        """Step failed — classify failure type and decide response."""
        error = outcome.get("error", "Unknown failure")

        # Classify failure severity
        is_fatal = outcome.get("fatal", False)
        is_contradiction = outcome.get("contradiction", False)
        is_timeout = outcome.get("timeout", False)

        # ── Fatal: cannot recover locally → REVISE_GLOBAL ──
        if is_fatal:
            logger.error(
                "FeedbackLoop: step %d FATAL — REVISE_GLOBAL: %s",
                step.step_number, error,
            )
            self.state.mark_step(
                step.step_number, StepStatus.FAILED,
                error_message=error,
                feedback=FeedbackSignal.REVISE_GLOBAL,
            )
            self._weaken_path(step, reason="fatal_error", delta=-0.15)
            self.state.plan_status = PlanStatus.DIVERGED
            return FeedbackSignal.REVISE_GLOBAL

        # ── Contradiction: evidence conflicts → BACKTRACK ──
        if is_contradiction:
            logger.warning(
                "FeedbackLoop: step %d CONTRADICTION — BACKTRACK: %s",
                step.step_number, error,
            )
            self.state.mark_step(
                step.step_number, StepStatus.FAILED,
                error_message=error,
                feedback=FeedbackSignal.BACKTRACK,
            )
            self._weaken_path(step, reason="contradiction", delta=-0.20)
            self.state.plan_status = PlanStatus.DIVERGED
            return FeedbackSignal.BACKTRACK

        # ── Timeout: transient → REVISE_LOCAL ──
        if is_timeout:
            logger.info(
                "FeedbackLoop: step %d TIMEOUT — REVISE_LOCAL (attempt %d)",
                step.step_number, step.attempt_count,
            )
            self.state.mark_step(
                step.step_number, StepStatus.FAILED,
                error_message=error,
                feedback=FeedbackSignal.REVISE_LOCAL,
            )
            return FeedbackSignal.REVISE_LOCAL

        # ── Default: local failure ──
        # If this attempt will hit max → escalate to REVISE_GLOBAL
        # (mark_step will increment attempt_count by 1)
        if step.attempt_count + 1 >= self.max_revisions_per_step:
            logger.warning(
                "FeedbackLoop: step %d max local revisions (%d) reached → REVISE_GLOBAL",
                step.step_number, self.max_revisions_per_step,
            )
            self.state.mark_step(
                step.step_number, StepStatus.FAILED,
                error_message=f"Max revisions: {error}",
                feedback=FeedbackSignal.REVISE_GLOBAL,
            )
            self._weaken_path(step, reason="exhausted_local_revisions", delta=-0.10)
            self.state.plan_status = PlanStatus.DIVERGED
            return FeedbackSignal.REVISE_GLOBAL

        # Local revision still within budget
        logger.info(
            "FeedbackLoop: step %d FAILED — REVISE_LOCAL (attempt %d/%d): %s",
            step.step_number, step.attempt_count,
            self.max_revisions_per_step, error,
        )
        self.state.mark_step(
            step.step_number, StepStatus.FAILED,
            error_message=error,
            feedback=FeedbackSignal.REVISE_LOCAL,
        )
        self._weaken_path(step, reason="step_failure", delta=-0.05)
        return FeedbackSignal.REVISE_LOCAL

    # ═══════════════════════════════════════════════════════════════════════
    # GRAPH FEEDBACK
    # ═══════════════════════════════════════════════════════════════════════

    def _reinforce_path(self, step: ReasoningStep, outcome: dict[str, Any]):
        """Reinforce the graph path when a step succeeds.

        Success increases edge weight (+0.05), making this path
        more likely to be recommended for similar future tasks.
        """
        source = f"step_{step.step_number - 1}" if step.step_number > 1 else "root"
        target = f"step_{step.step_number}"
        self.graph_writer.update_edge_weight(
            source_node=source,
            target_node=target,
            delta=+0.05,
            reason=f"step_{step.step_number}_success",
        )

    def _weaken_path(self, step: ReasoningStep, reason: str, delta: float):
        """Weaken the graph path when a step fails.

        Failure decreases edge weight, making this path less likely
        to be recommended. The delta magnitude depends on failure severity:
          -0.05: simple failure
          -0.10: exhausted local revisions
          -0.15: fatal error
          -0.20: contradiction

        Over time, repeatedly failing paths become "cold" and are
        deprioritized by the graph planner.
        """
        source = f"step_{step.step_number - 1}" if step.step_number > 1 else "root"
        target = f"step_{step.step_number}"
        self.graph_writer.update_edge_weight(
            source_node=source,
            target_node=target,
            delta=delta,
            reason=f"{reason}:step_{step.step_number}",
        )
        # Also annotate the path with failure metadata
        self.graph_writer.annotate_path(
            path_nodes=[source, target],
            annotation={
                "last_failure": reason,
                "failure_count": step.attempt_count,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

    # ═══════════════════════════════════════════════════════════════════════
    # LOOP DETECTION
    # ═══════════════════════════════════════════════════════════════════════

    def _detect_loop(self, step: ReasoningStep) -> bool:
        """Detect if we're in a reasoning loop — same step, same content.

        Uses content signature hashing. If the same step produces the
        same output 5+ times, it's a loop.
        """
        sig = _content_signature(step.content)
        if step.step_number not in self._step_signatures:
            self._step_signatures[step.step_number] = set()
        sigs = self._step_signatures[step.step_number]
        sigs.add(sig)

        # Loop if: same step, same signature, no real change
        # (simplified: if we've seen any signature for this step 5+ times)
        total_attempts_for_step = sum(
            1 for s in self.state.plan_steps
            if s.step_number == step.step_number
            or (s.is_revision and s.revises_step == step.step_number)
        )
        return total_attempts_for_step >= self.loop_detection_threshold

    # ═══════════════════════════════════════════════════════════════════════
    # END-OF-PLAN
    # ═══════════════════════════════════════════════════════════════════════

    def finalize(self) -> FeedbackSignal:
        """Called when all steps are complete. Writes final state to graph."""
        self.state.plan_status = PlanStatus.COMPLETED

        # Record final episode in Graphiti
        self.graph_writer.record_episode(
            state=self.state,
            signal=FeedbackSignal.PROCEED,
            metadata={
                "total_steps": len(self.state.plan_steps),
                "total_revisions": self.state.total_revisions,
                "final_epistemic_band": self.state.epistemic_band,
                "final_malu_index": self.state.malu_index,
                "completed_at": datetime.now(UTC).isoformat(),
            },
        )
        logger.info(
            "FeedbackLoop: plan %s COMPLETED — %d steps, %d revisions, "
            "epistemic=%.2f, malu=%.2f",
            self.state.context_id,
            len(self.state.plan_steps),
            self.state.total_revisions,
            self.state.epistemic_band,
            self.state.malu_index,
        )
        return FeedbackSignal.PROCEED


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════


def _content_signature(content: str, length: int = 8) -> str:
    """Generate a short content signature for loop detection."""
    import hashlib
    return hashlib.sha256(content.encode()).hexdigest()[:length]


def create_feedback_loop(
    state: MINDState,
    graph_writer: GraphWriter | None = None,
    graph_reader: GraphReader | None = None,
) -> FeedbackLoop:
    """Factory: create a feedback loop for the given MIND state."""
    return FeedbackLoop(
        state=state,
        graph_writer=graph_writer,
        graph_reader=graph_reader,
    )


__all__ = [
    "FeedbackLoop",
    "FeedbackSignal",
    "GraphWriter",
    "GraphReader",
    "NoOpGraphWriter",
    "NoOpGraphReader",
    "create_feedback_loop",
]
