"""
arifosmcp/runtime/convergence.py — 333_MIND mode=converge
═════════════════════════════════════════════════════════════

Drives arif_think in a recursive loop until marginal gain → 0.
Collapse = best current answer under available evidence, not final truth.

The loop:
  1. REASON → capture state (confidence, evidence_hash, synthesis)
  2. COMPARE → marginal gain against prior state
  3. DETECT → Gödel lock, strange loop, evidence plateau
  4. DECIDE → collapse if gain < threshold for N consecutive iterations

One class. One loop. Five parameters. No new MCP tool.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any

from arifosmcp.schemas.mind_metabolism import ConvergenceReport, ConvergenceStep
from arifosmcp.tools.reason import arif_think as _reason

logger = logging.getLogger(__name__)


class ConvergenceController:
    """
    Recursive convergence loop driver for arif_think.

    Parameters:
        max_iterations:  Hard cap (default 5). Prevents infinite loops.
        min_delta:       Minimum marginal gain to continue (default 0.02).
        patience:        Consecutive below-threshold steps before collapse (default 2).

    Each iteration:
        1. Calls arif_think(mode='reason') with refined query
        2. Captures state: confidence, evidence_hash, claim_state, synthesis
        3. Computes marginal gain vs prior state
        4. Checks Gödel lock / strange loop / evidence plateau
        5. Decides: continue or collapse

    Collapse reasons:
        marginal_gain_below_threshold  — convergence achieved
        godel_lock_hit                 — self-reference detected, HOLD
        max_iterations_reached         — hard cap, best answer returned
        evidence_plateau               — same evidence, no new ground
    """

    def __init__(
        self,
        max_iterations: int = 5,
        min_delta: float = 0.02,
        patience: int = 2,
    ):
        self.max_iterations = max(max_iterations, 2)
        self.min_delta = max(min_delta, 0.01)
        self.patience = max(patience, 1)
        self.history: list[ConvergenceStep] = []
        self.godel_detected = False
        self.loop_risk = 0.0

    async def converge(
        self,
        query: str,
        actor_id: str | None = None,
        context: dict | None = None,
    ) -> ConvergenceReport:
        """
        Run the convergence loop. Returns a ConvergenceReport with
        collapsed answer, iteration history, and collapse reason.

        This is the ONLY public method. Everything else is internal.
        """
        current_query = query
        self.history = []
        self.godel_detected = False
        self.loop_risk = 0.0
        below_threshold_count = 0

        for i in range(self.max_iterations):
            # ── 1. REASON ─────────────────────────────────────────────────
            try:
                result = _reason(
                    mode="reason",
                    query=current_query,
                    actor_id=actor_id,
                    context=context,
                )
            except Exception as e:
                logger.warning(f"converge iteration {i} failed: {e}")
                return self._emit_collapse(
                    reason="reasoning_error",
                    error=str(e),
                    iterations=i,
                )

            # ── 2. CAPTURE STATE ──────────────────────────────────────────
            state = self._capture_state(result, i, current_query)
            self.history.append(state)

            # ── 3. COMPARE MARGINAL GAIN ──────────────────────────────────
            prior = self.history[-2] if len(self.history) >= 2 else None
            gain = self._marginal_gain(state, prior)

            # ── 4. DETECT LOCKS ───────────────────────────────────────────
            self.godel_detected = self._detect_godel_lock(state)
            self.loop_risk = self._compute_loop_risk(state)
            evidence_plateau = self._detect_evidence_plateau(state)

            # ── 5. DECIDE ─────────────────────────────────────────────────
            # Gödel lock → immediate HOLD collapse
            if self.godel_detected:
                return self._emit_collapse(
                    reason="godel_lock_hit",
                    current_state=state,
                    gain=gain,
                    iterations=i + 1,
                )

            # Evidence plateau → collapse (no new ground)
            if evidence_plateau:
                return self._emit_collapse(
                    reason="evidence_plateau",
                    current_state=state,
                    gain=gain,
                    iterations=i + 1,
                )

            # Marginal gain below threshold → count patience
            if gain < self.min_delta:
                below_threshold_count += 1
                if below_threshold_count >= self.patience:
                    return self._emit_collapse(
                        reason="marginal_gain_below_threshold",
                        current_state=state,
                        gain=gain,
                        iterations=i + 1,
                    )
            else:
                below_threshold_count = 0  # reset on improvement

            # ── 6. REFINE QUERY FOR NEXT ITERATION ────────────────────────
            current_query = self._refine_query(state, current_query)

        # ── MAX ITERATIONS REACHED ────────────────────────────────────────
        return self._emit_collapse(
            reason="max_iterations_reached",
            current_state=self.history[-1] if self.history else None,
            gain=0.0,
            iterations=self.max_iterations,
        )

    # ── Internal helpers ─────────────────────────────────────────────────

    def _capture_state(self, result: Any, iteration: int, query: str) -> ConvergenceStep:
        """Extract state snapshot from an arif_think result."""
        # Result may be Synthesis (Pydantic) or dict or wrapped
        if hasattr(result, "model_dump"):
            result = result.model_dump()
        elif hasattr(result, "dict"):
            result = result.dict()

        # Navigate through _ok wrapper: result may be at result.result
        payload = result
        if isinstance(result, dict):
            payload = result.get("result", result)
            if isinstance(payload, dict) and "result" in payload:
                payload = payload["result"]  # double-wrapped

        # Extract reasoning_output (new ZEN layer) or flat fields (legacy)
        reasoning = {}
        if isinstance(payload, dict):
            reasoning = payload.get("reasoning_output", payload)

        confidence = 0.5
        if isinstance(reasoning.get("confidence"), dict):
            confidence = float(reasoning["confidence"].get("overall", 0.5))

        claim_state = str(reasoning.get("claim_state", "UNKNOWN")).upper()
        synthesis = reasoning.get("synthesis", "")

        # Compute evidence hash from all sources
        evidence_raw = {
            "evidence": reasoning.get("evidence_used", []),
            "inferences": reasoning.get("inferences", []),
            "counterarguments": reasoning.get("counterarguments", []),
            "missing": reasoning.get("missing_evidence", []),
        }
        evidence_hash = hashlib.sha256(str(evidence_raw).encode()).hexdigest()[:12]

        return ConvergenceStep(
            iteration=iteration,
            query=query,
            confidence=confidence,
            claim_state=claim_state,
            synthesis=str(synthesis)[:500] if synthesis else "",
            evidence_hash=evidence_hash,
            metadata={"loop_risk": self.loop_risk},
        )

    def _marginal_gain(self, current: ConvergenceStep, prior: ConvergenceStep | None) -> float:
        """Compute marginal gain between two consecutive iterations."""
        if prior is None:
            return 1.0  # first iteration always gains

        # Confidence delta
        delta = current.confidence - prior.confidence

        # Penalize: no new evidence (same evidence hash)
        if current.evidence_hash == prior.evidence_hash:
            delta *= 0.5

        # Penalize: no change in claim_state
        if current.claim_state == prior.claim_state:
            delta *= 0.8

        # Penalize: identical synthesis
        if current.synthesis and current.synthesis == prior.synthesis:
            delta *= 0.3

        return max(0.0, round(delta, 4))

    def _detect_godel_lock(self, state: ConvergenceStep) -> bool:
        """
        Gödel lock: system cannot verify its own authority from inside.

        Triggers when query asks arif_think to verify itself.
        """
        q = state.query.lower()
        self_ref_patterns = [
            ("verify", "arif_think", "authority"),
            ("can", "arif_think", "trust"),
            ("is", "arif_think", "correct"),
            ("self", "verify", "arif_think"),
            ("arif_think", "prove", "itself"),
            ("does", "arif_think", "work", "correctly"),
        ]
        for pattern in self_ref_patterns:
            if all(term in q for term in pattern):
                logger.info(f"Gödel lock triggered: {pattern}")
                return True
        return False

    def _compute_loop_risk(self, state: ConvergenceStep) -> float:
        """
        Compute loop risk score (0.0-1.0).

        Risk factors:
        - Low confidence → higher risk (LLM uncertainty)
        - High iteration count → diminishing returns
        - SYNTHESIS_ABSENT → risk of hallucinated certainty
        """
        risk = 0.0

        # Low confidence = high risk
        if state.confidence < 0.3:
            risk += 0.4
        elif state.confidence < 0.5:
            risk += 0.2

        # High iteration count
        if state.iteration > 3:
            risk += 0.2
        elif state.iteration > 2:
            risk += 0.1

        # Unknown claim state
        if state.claim_state in ("UNKNOWN", "UNSUPPORTED"):
            risk += 0.3

        return min(1.0, round(risk, 2))

    def _detect_evidence_plateau(self, state: ConvergenceStep) -> bool:
        """
        Detect evidence plateau: same evidence hash repeated across iterations.

        If the last N consecutive iterations all share the same evidence_hash
        AND confidence hasn't improved significantly, there's no new ground.
        N = min(patience, len(history)).
        """
        if len(self.history) < 1:
            return False
        recent = (
            self.history[-(self.patience) :] if len(self.history) >= self.patience else self.history
        )
        # All recent entries must have the SAME evidence hash as the current state
        if not all(prev.evidence_hash == state.evidence_hash for prev in recent):
            return False
        # Also check: confidence hasn't improved by more than threshold
        # Use round to avoid floating-point drift (0.52 - 0.50 = 0.020000000000000018)
        steps = recent + [state]
        confidences = [s.confidence for s in steps]
        delta = round(max(confidences) - min(confidences), 4)
        if delta <= self.min_delta:
            return True
        return False

    def _refine_query(self, state: ConvergenceStep, original_query: str) -> str:
        """
        Refine the query for the next iteration based on what's still unknown.

        If synthesis mentions unknowns, ask about them.
        Otherwise, ask for a critique of the current answer.
        """
        if state.synthesis and (
            "unknown" in state.synthesis.lower() or "uncertain" in state.synthesis.lower()
        ):
            return f"{original_query} — focus on resolving the remaining unknowns"
        return f"{original_query} — critique and verify the current answer"

    def _emit_collapse(
        self,
        reason: str,
        current_state: ConvergenceStep | None = None,
        gain: float = 0.0,
        iterations: int = 0,
        error: str | None = None,
    ) -> ConvergenceReport:
        """Build the final ConvergenceReport."""
        confidence_path = [s.confidence for s in self.history]
        evidence_hashes = [s.evidence_hash for s in self.history]

        report = ConvergenceReport(
            iterations=iterations,
            collapsed=True,
            collapse_reason=reason,
            marginal_gain=gain,
            threshold=self.min_delta,
            patience_used=self.patience,
            godel_lock_detected=self.godel_detected,
            loop_risk=self.loop_risk,
            confidence_path=confidence_path,
            evidence_hashes=evidence_hashes,
            final_state=current_state,
            history=self.history,
            error=error,
        )

        # Log the collapse for audit
        logger.info(
            f"converge collapsed: reason={reason} "
            f"iterations={iterations} gain={gain:.4f} "
            f"risk={self.loop_risk} godel={self.godel_detected}"
        )

        return report
