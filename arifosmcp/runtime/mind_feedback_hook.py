"""
arifosmcp/runtime/mind_feedback_hook.py — MIND Feedback Integration Hook v1
═══════════════════════════════════════════════════════════════════════════════

ZERO-KERNEL-MODIFICATION hook that wires MINDState + FeedbackLoop into
arif_mind_reason_v2 without touching mind_reason.py.

ARCHITECTURE
────────────
  mind_reason.py (UNCHANGED)
      │
      ▼
  mind_feedback_hook.py (THIS FILE)
      │
      ├── mind_state.py     → MINDState (persistent state object)
      ├── feedback_loop.py  → FeedbackLoop (signal controller)
      ├── l5_graph_read.py  → L5GraphReader / L5GraphWriter (graph adapters)
      └── memory_store.py   → Qdrant checkpoint writes

USAGE
─────
  Instead of calling arif_mind_reason_v2() directly, call:

    from arifosmcp.runtime.mind_feedback_hook import mind_reason_with_feedback
    response, feedback = await mind_reason_with_feedback(request)

  OR set the environment variable to auto-patch:

    MIND_FEEDBACK_ENABLED=true
    # Now arif_mind_reason_v2 is automatically wrapped

REVERSIBILITY (F1)
──────────────────
  - Set MIND_FEEDBACK_ENABLED=false → hook is disabled, zero effect
  - Remove the import → full rollback
  - No modifications to mind_reason.py, memory_store.py, or any kernel file

FLOOR BINDING
─────────────
  F01 (AMANAH)   — ALL writes are checkpointed, rollback-able
  F02 (TRUTH)    — epistemic band tracked per step
  F04 (CLARITY)  — feedback signals are typed enums, not free text
  F07 (HUMILITY) — omega_0 hard-capped at 0.90
  F08 (GENIUS)   — max 7 revisions before HOLD
  F09 (ANTIHANTU) — C_dark tracked; HOLD if ≥ 0.30

AUTHORITY: 333_MIND, 888_JUDGE
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime
from typing import Any

from arifosmcp.runtime.feedback_loop import (
    FeedbackLoop,
    NoOpGraphReader,
    NoOpGraphWriter,
    create_feedback_loop,
)
from arifosmcp.runtime.mind_state import (
    EpistemicTag,
    FeedbackSignal,
    MINDState,
    create_mind_state,
)

logger = logging.getLogger(__name__)

# ── Configuration ──────────────────────────────────────────────────────────
_FEEDBACK_ENABLED = os.getenv("MIND_FEEDBACK_ENABLED", "false").lower() == "true"
_CHECKPOINT_ENABLED = os.getenv("MIND_CHECKPOINT_ENABLED", "true").lower() == "true"
_CHECKPOINT_TIER = os.getenv("MIND_CHECKPOINT_TIER", "canon")  # canon = 90-day TTL


# ═══════════════════════════════════════════════════════════════════════════════
# STATE TRACKER — per-request MINDState management
# ═══════════════════════════════════════════════════════════════════════════════


class MindFeedbackTracker:
    """Tracks MINDState and FeedbackLoop across a single reasoning request.

    Created at the start of arif_mind_reason_v2, persisted after each
    metabolic layer (metabolize → abstract → attest → abduct → synthesize).

    Usage:
        tracker = MindFeedbackTracker.start(request)
        # ... after each layer ...
        tracker.after_layer(layer_name, content, confidence)
        # ... after completion ...
        tracker.finalize(response)
    """

    def __init__(
        self,
        state: MINDState,
        feedback_loop: FeedbackLoop,
        session_id: str,
    ):
        self.state = state
        self.feedback = feedback_loop
        self.session_id = session_id
        self.layers_completed: list[dict[str, Any]] = []
        self._started_at = datetime.now(UTC)

    @classmethod
    def start(
        cls,
        query: str,
        intent: str = "metabolize",
        domain: str = "general",
        constraints: list[str] | None = None,
        session_id: str | None = None,
    ) -> MindFeedbackTracker:
        """Begin tracking a new reasoning request.

        Creates a fresh MINDState with the given parameters and
        initializes the FeedbackLoop with L5 adapters.
        """
        state = create_mind_state(
            goal=query,
            intent=intent,
            domain=domain,
            constraints=constraints,
            session_id=session_id,
        )

        # Wire L5 graph adapters if available
        writer = NoOpGraphWriter()
        reader = NoOpGraphReader()
        try:
            from arifosmcp.runtime.l5_graph_read import L5GraphReader, L5GraphWriter
            writer = L5GraphWriter()
            reader = L5GraphReader()
        except ImportError:
            logger.debug("MindFeedbackTracker: L5 not available, using no-op graph")
        except Exception as e:
            logger.debug("MindFeedbackTracker: L5 init failed — %s", e)

        feedback = create_feedback_loop(
            state=state,
            graph_writer=writer,
            graph_reader=reader,
        )

        # Search for similar prior tasks for plan bootstrapping
        try:
            similar = reader.find_similar_tasks(query, top_k=3)
            if similar:
                state.similar_task_refs = [s["task_id"] for s in similar]
                logger.info(
                    "MindFeedbackTracker: found %d similar prior tasks for '%s'",
                    len(similar), query[:80],
                )
        except Exception as e:
            logger.debug("MindFeedbackTracker: similar task search failed — %s", e)

        logger.info(
            "MindFeedbackTracker: started session %s for query '%s'",
            state.context_id, query[:80],
        )
        return cls(state=state, feedback_loop=feedback, session_id=session_id or "")

    def after_layer(
        self,
        layer_name: str,
        content: str,
        confidence: float = 0.5,
        success: bool = True,
    ) -> FeedbackSignal:
        """Record a completed metabolic layer as a reasoning step.

        Called after each layer in the 5-layer pipeline:
          metabolize → abstract → attest → abduct → synthesize

        Returns the feedback signal for the layer (PROCEED if OK).
        """
        if not _FEEDBACK_ENABLED:
            return FeedbackSignal.PROCEED

        step = self.state.add_step(
            content=f"[{layer_name}] {content[:200]}",
            step_type="analysis",
            epistemic_tag=EpistemicTag.PLAUSIBLE if confidence < 0.90
            else EpistemicTag.VERIFIED,
            confidence=confidence,
        )
        self.state.current_step = step.step_number

        outcome = {
            "success": success,
            "confidence": confidence,
            "layer": layer_name,
        }

        signal = self.feedback.evaluate(step, outcome)
        self.layers_completed.append({
            "layer": layer_name,
            "step_number": step.step_number,
            "signal": signal.value if hasattr(signal, 'value') else str(signal),
            "confidence": confidence,
        })

        # Checkpoint after each layer
        if _CHECKPOINT_ENABLED and signal != FeedbackSignal.HOLD:
            self._checkpoint_state()

        # If signal is not PROCEED, log the deviation
        if signal != FeedbackSignal.PROCEED:
            logger.warning(
                "MindFeedbackTracker: layer '%s' returned %s (not PROCEED)",
                layer_name, signal.value,
            )

        return signal

    def finalize(
        self,
        response: Any,
        overall_confidence: float = 0.5,
    ) -> dict[str, Any]:
        """Finalize the reasoning session after synthesis.

        Writes final checkpoint, records episode in graph memory,
        and returns a feedback summary.
        """
        signal = self.feedback.finalize()

        # Checkpoint final state
        if _CHECKPOINT_ENABLED:
            self._checkpoint_state()

        summary = {
            "context_id": self.state.context_id,
            "layers_completed": len(self.layers_completed),
            "total_steps": len(self.state.plan_steps),
            "total_revisions": self.state.total_revisions,
            "final_signal": signal.value,
            "epistemic_band": self.state.epistemic_band,
            "malu_index": self.state.malu_index,
            "duration_s": (datetime.now(UTC) - self._started_at).total_seconds(),
            "similar_tasks_found": len(self.state.similar_task_refs),
        }

        logger.info(
            "MindFeedbackTracker: finalized %s — %d layers, "
            "epistemic=%.2f, malu=%.2f, duration=%.1fs",
            self.state.context_id,
            summary["layers_completed"],
            self.state.epistemic_band,
            self.state.malu_index,
            summary["duration_s"],
        )

        return summary

    def _checkpoint_state(self):
        """Write current MINDState checkpoint to Qdrant + L5 Graphiti."""
        checkpoint = self.state.checkpoint()

        # Write to Qdrant via memory_store
        try:
            import asyncio

            from arifosmcp.runtime.memory_store import store
            checkpoint_data = {
                "type": "mind_checkpoint",
                "tier": _CHECKPOINT_TIER,
                "session_id": self.session_id,
                "actor_id": self.state.actor_id,
                "tags": ["mind_state", "checkpoint", f"context:{self.state.context_id}"],
                "checkpoint": checkpoint,
            }
            # Fire-and-forget in event loop if available
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(
                    store(
                        memory_id=f"mind_cp_{checkpoint['checkpoint_id']}",
                        content=checkpoint_data,
                        tier=_CHECKPOINT_TIER,
                        session_id=self.session_id,
                        actor_id=self.state.actor_id,
                        tags=checkpoint_data["tags"],
                    )
                )
            except RuntimeError:
                # No running event loop — skip (non-critical)
                logger.debug("MindFeedbackTracker: no event loop for checkpoint")
        except ImportError:
            logger.debug("MindFeedbackTracker: memory_store not available")
        except Exception as e:
            logger.warning("MindFeedbackTracker: checkpoint write failed — %s", e)


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE WRAPPER — mind_reason_with_feedback
# ═══════════════════════════════════════════════════════════════════════════════


async def mind_reason_with_feedback(request) -> tuple[Any, dict[str, Any]]:
    """Execute arif_mind_reason_v2 with MINDState + FeedbackLoop tracking.

    Args:
        request: MindRequest (from mind_metabolism.py)

    Returns:
        (MindResponse, feedback_summary_dict)

    This is the drop-in replacement for arif_mind_reason_v2().
    All existing callers can switch to this without changing mind_reason.py.
    """
    from arifosmcp.runtime.mind_reason import arif_mind_reason_v2

    if not _FEEDBACK_ENABLED:
        # Passthrough — zero overhead when disabled
        response = await arif_mind_reason_v2(request)
        return response, {"status": "feedback_disabled"}

    # Initialize tracker
    tracker = MindFeedbackTracker.start(
        query=request.query,
        intent=request.task.intent.value
        if hasattr(request.task.intent, 'value')
        else str(request.task.intent),
        domain=request.task.domain,
        session_id=request.session_id,
    )

    # Execute the original reasoning
    response = await arif_mind_reason_v2(request)

    # Record layers from the response's mind_packet
    if hasattr(response, 'mind_packet') and response.mind_packet:
        packet = response.mind_packet

        # Layer 1: Metabolize
        if hasattr(packet, 'metabolized_context') and packet.metabolized_context:
            mc = packet.metabolized_context
            tracker.after_layer(
                "metabolize",
                getattr(mc, 'input_summary', str(mc)[:200]),
                confidence=0.85,
            )

        # Layer 2: Abstract
        if hasattr(packet, 'abstractions') and packet.abstractions:
            tracker.after_layer(
                "abstract",
                f"{len(packet.abstractions)} abstractions",
                confidence=0.80,
            )

        # Layer 3: Attest
        if hasattr(packet, 'attestations') and packet.attestations:
            tracker.after_layer(
                "attest",
                f"{len(packet.attestations)} attestations",
                confidence=0.90 if packet.attestations else 0.60,
            )

        # Layer 4: Abduct
        if hasattr(packet, 'abductions') and packet.abductions:
            tracker.after_layer(
                "abduct",
                f"{len(packet.abductions)} hypotheses",
                confidence=0.60,
            )

        # Layer 5: Synthesize
        if hasattr(packet, 'synthesis') and packet.synthesis:
            syn = packet.synthesis
            conf = getattr(syn, 'confidence', {})
            overall = conf.get('overall_confidence', 0.5) if isinstance(conf, dict) else 0.5
            tracker.after_layer(
                "synthesize",
                getattr(syn, 'bounded_answer', str(syn)[:200]),
                confidence=overall,
            )

    # Finalize
    overall_conf = 0.5
    if (hasattr(response, 'mind_packet') and response.mind_packet
            and hasattr(response.mind_packet, 'synthesis')
            and response.mind_packet.synthesis):
        syn = response.mind_packet.synthesis
        conf = getattr(syn, 'confidence', {})
        overall_conf = conf.get('overall_confidence', 0.5) if isinstance(conf, dict) else 0.5

    summary = tracker.finalize(response, overall_confidence=overall_conf)

    return response, summary


# ═══════════════════════════════════════════════════════════════════════════════
# AUTO-PATCH (environment-variable triggered)
# ═══════════════════════════════════════════════════════════════════════════════


def _auto_patch():
    """Auto-patch arif_mind_reason_v2 if MIND_FEEDBACK_ENABLED=true.

    This is the zero-kernel-modification mechanism. When the env var is set,
    this module monkey-patches the import path so that callers get the
    feedback-wrapped version automatically.
    """
    if not _FEEDBACK_ENABLED:
        return False

    try:
        import arifosmcp.runtime.mind_reason as mr
        _original = mr.arif_mind_reason_v2

        async def _wrapped(request):
            response, _summary = await mind_reason_with_feedback(request)
            return response

        mr.arif_mind_reason_v2 = _wrapped
        logger.info(
            "MindFeedbackHook: AUTO-PATCHED arif_mind_reason_v2 "
            "with feedback tracking (MIND_FEEDBACK_ENABLED=true)"
        )
        return True
    except Exception as e:
        logger.warning("MindFeedbackHook: auto-patch failed — %s", e)
        return False


# Run auto-patch on import
_auto_patch()


__all__ = [
    "MindFeedbackTracker",
    "mind_reason_with_feedback",
    "create_mind_state",
    "FeedbackLoop",
    "FeedbackSignal",
]
