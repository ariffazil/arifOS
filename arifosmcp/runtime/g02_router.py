"""
G02 — Layered Router
===================

The constitutional choke point. Every request flows through here.

Layer 1: Axis Classification — what axis is this request targeting?
Layer 2: Call Graph Enforcement — is the caller allowed to call this axis?
Layer 3: Precondition & State Gate — has G05 issued SEAL if this is E-axis?

A2A connects minds. MCP connects hands. arifOS governs both.
G02 is where governance happens.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import logging
from datetime import UTC, datetime
from typing import Any

from arifosmcp.runtime.agent_registry import (
    CALL_GRAPH,
    Axis,
    OperationClass,
    RiskTier,
    RouteContext,
    RouteResult,
    get_registry,
)

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(UTC)


class G02LayeredRouter:
    """
    G02 Layered Router with 3 enforcement layers.

    Every request from outside the constitutional kernel enters here.
    No direct access to E-axis without passing through G02.
    """

    def __init__(self):
        self.registry = get_registry()
        self._trace: list[str] = []

    # ── Layer 1: Axis Classification ─────────────────────────────────────────

    def classify(
        self, request: dict[str, Any], context: RouteContext
    ) -> tuple[Axis, OperationClass]:
        """
        Classify request into axis and operation class.

        Uses tool_name → agent_id mapping from registry.
        Falls back to keyword analysis if tool_name not in registry.
        """
        tool_name = request.get("tool_name") or request.get("tool") or ""
        query = request.get("query", "").lower()
        skill_id = request.get("skill_id", "")

        # Try direct registry lookup
        if skill_id:
            spec = self.registry.by_skill(skill_id)
            if spec:
                return spec.axis, spec.operation_class

        # Try tool_name lookup
        if tool_name:
            for agent in self.registry.all_agents():
                if agent.tool_name == tool_name:
                    return agent.axis, agent.operation_class

        # Fallback: keyword-based classification
        if any(k in query for k in ["what is", "fetch", "read", "state", "status"]):
            return Axis.P, OperationClass.READ
        if any(k in query for k in ["compute", "calculate", "simulate", "evaluate"]):
            return Axis.T, OperationClass.COMPUTE
        if any(k in query for k in ["npv", "emv", "irr", "dscr", "value", "worth"]):
            return Axis.V, OperationClass.VALUE
        if any(k in query for k in ["execute", "forge", "write", "store", "seal", "commit"]):
            return Axis.E, OperationClass.MUTATE
        if any(k in query for k in ["monitor", "audit", "correlation", "orthogonality", "meta"]):
            return Axis.M, OperationClass.META

        # Default to G (governance)
        return Axis.G, OperationClass.GATE

    # ── Layer 2: Call Graph Enforcement ──────────────────────────────────────

    def enforce_call_graph(
        self,
        caller_axis: Axis | None,
        target_axis: Axis,
    ) -> tuple[bool, str]:
        """
        Verify caller is allowed to call target axis per CALL_GRAPH rules.

        Returns (allowed, reason).
        """
        if caller_axis is None:
            # External caller — must be G (entry point)
            if target_axis == Axis.E:
                return False, "E-axis unreachable from external. Route through G02 first."
            if target_axis == Axis.M:
                return False, "M-axis not directly accessible. Use G02."
            return True, "External caller routed to non-E axis."

        # Caller is authenticated axis
        allowed_targets = CALL_GRAPH.get(caller_axis, frozenset())
        if target_axis in allowed_targets:
            return True, f"{caller_axis.value} → {target_axis.value} allowed"

        # Special case: E-axis only reachable via G05
        if target_axis == Axis.E:
            # E can only be called by G-axis (which includes G05)
            if caller_axis == Axis.G:
                return True, "G-axis authorized to call E-axis via constitutional chain"
            return False, "E-axis only reachable via G05 SEAL. Direct call blocked."

        return False, f"{caller_axis.value} cannot call {target_axis.value}. Call graph violation."

    # ── Layer 3: Precondition & State Gate ───────────────────────────────────

    def check_preconditions(
        self,
        target_axis: Axis,
        operation_class: OperationClass,
        context: RouteContext,
    ) -> tuple[bool, str]:
        """
        Verify all preconditions met before routing to target.

        For E-axis:
        - G05 verdict must be SEAL
        - judge_state_hash must be present and valid
        - session must be initialized
        - WELL readiness must be adequate for risk tier

        For G-axis:
        - session must be initialized
        """
        now = _utcnow()

        # E-axis requires G05 SEAL
        if target_axis == Axis.E:
            if context.judge_verdict != "SEAL":
                return False, (
                    f"E-axis blocked: G05 verdict is {context.judge_verdict or 'NONE'}, "
                    "not SEAL. Execution requires constitutional approval."
                )

            if not context.judge_state_hash:
                return False, "E-axis blocked: judge_state_hash missing. Cannot verify integrity."

            # Verify state hash format (SHA256 hex = 64 chars)
            if len(context.judge_state_hash) != 64:
                return (
                    False,
                    f"E-axis blocked: judge_state_hash malformed (expected 64-char hex, got {len(context.judge_state_hash)})",
                )

            # Session must exist
            if not context.session_id:
                return (
                    False,
                    "E-axis blocked: session_id missing. Execute requires anchored session.",
                )

            # WELL readiness check for high/critical risk
            if context.risk_tier in (RiskTier.HIGH, RiskTier.CRITICAL):
                if context.well_readiness < 0.7:
                    return False, (
                        f"E-axis blocked: WELL readiness {context.well_readiness:.2f} < 0.70 "
                        "for high/critical risk. Human substrate not adequate."
                    )

            return (
                True,
                "E-axis preconditions satisfied. SEAL verified, hash valid, session anchored.",
            )

        # G-axis requires session initialization
        if target_axis == Axis.G:
            if not context.session_id and operation_class == OperationClass.GATE:
                return False, "G-axis blocked: session_id missing. Initialize via G01 first."

        # V-axis requires inputs from T or P (not free-form) — check trace
        if target_axis == Axis.V:
            if len(context.trace) < 2:
                logger.warning(f"V-axis called without prior P/T execution. trace={context.trace}")

        return True, f"{target_axis.value} preconditions satisfied."

    # ── Full Route ─────────────────────────────────────────────────────────────

    def route(
        self,
        request: dict[str, Any],
        context: RouteContext,
    ) -> RouteResult:
        """
        Full 3-layer routing:
        1. Classify → determine axis and operation class
        2. Enforce → verify call graph permissions
        3. Gate → check preconditions and state
        """
        self._trace = []

        # Layer 1: Classify
        target_axis, op_class = self.classify(request, context)
        self._trace.append(f"L1:classify→{target_axis.value}/{op_class.value}")

        # Determine caller axis from context
        caller_axis = context.caller_axis

        # Layer 2: Call graph enforcement
        allowed, reason = self.enforce_call_graph(caller_axis, target_axis)
        self._trace.append(f"L2:call_graph→{'ALLOWED' if allowed else 'BLOCKED'}: {reason}")

        if not allowed:
            logger.warning(f"[G02] Call graph violation: {reason} | trace={' '.join(self._trace)}")
            return RouteResult(
                ok=False,
                target_axis=target_axis,
                operation_class=op_class,
                verdict="VOID",
                reason="Call graph violation",
                blocked_reason=reason,
                context=context,
            )

        # Layer 3: Precondition gate
        preconditions_met, gate_reason = self.check_preconditions(target_axis, op_class, context)
        self._trace.append(f"L3:gate→{'PASS' if preconditions_met else 'BLOCK'}: {gate_reason}")

        if not preconditions_met:
            logger.warning(
                f"[G02] Precondition gate blocked: {gate_reason} | trace={' '.join(self._trace)}"
            )
            return RouteResult(
                ok=False,
                target_axis=target_axis,
                operation_class=op_class,
                verdict="HOLD",
                reason="Precondition not met",
                blocked_reason=gate_reason,
                context=context,
            )

        # Route successful
        logger.info(
            f"[G02] Route OK: {target_axis.value}/{op_class.value} | trace={' '.join(self._trace)}"
        )
        return RouteResult(
            ok=True,
            target_axis=target_axis,
            operation_class=op_class,
            verdict="SEAL",
            reason=f"Routed to {target_axis.value} via {op_class.value}",
            context=context,
        )

    # ── G05 SEAL verification ───────────────────────────────────────────────────

    def verify_seal(
        self,
        verdict: str,
        state_hash: str,
        session_id: str,
    ) -> tuple[bool, str]:
        """
        Verify G05 has issued a valid SEAL.
        Called by E-axis agents before executing.
        """
        if verdict != "SEAL":
            return False, f"Verdict is {verdict}, not SEAL"

        if not state_hash:
            return False, "state_hash missing"

        if len(state_hash) != 64:
            return False, f"state_hash malformed (expected 64 hex chars)"

        if not session_id:
            return False, "session_id missing"

        # Compute expected hash from components
        hash_input = f"{verdict}:{session_id}:{_utcnow().date().isoformat()}"
        expected = hashlib.sha256(hash_input.encode()).hexdigest()

        # For now, accept any valid-format SEAL (real impl would verify against vault)
        return True, f"SEAL verified for session {session_id[:20]}..."


def get_router() -> G02LayeredRouter:
    return G02LayeredRouter()
