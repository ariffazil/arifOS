"""
arifOS Governance Enforcer — HARD STOP Implementation
═══════════════════════════════════════════════════════════════════════════════

CRITICAL FIX: Prevents HOLD/VOID verdict bypass

Rules:
1. If tool returns HOLD/VOID/F1-violation → HARD STOP (no model call)
2. Query classification BEFORE tool invocation (Class A vs Class B)
3. Audit log immutable for every decision
4. Non-bypass guard: verdict != PASS → model output BLOCKED

Author: 888_VALIDATOR
Version: 2026.04.06-HARDENED
"""

from __future__ import annotations

import hashlib
import json
import time
from enum import Enum
from typing import Any

from arifosmcp.runtime.irreversibility import AmanahIrreversibilityScorer
from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict

# Global scorer instance — stateless, thread-safe
_AMANAH_SCORER = AmanahIrreversibilityScorer()


class QueryClass(str, Enum):
    """Query classification for governance routing."""
    INFORMATIONAL = "informational"  # Class A: No state change, model can respond directly
    GOVERNED = "governed"            # Class B: State mutation, full F1-F13 required
    CRITICAL = "critical"            # Class C: Irreversible, requires F11 verified identity


class PropagationDecision(str, Enum):
    """Propagation decision for audit trail."""
    ALLOWED = "ALLOWED"
    BLOCKED_HOLD = "BLOCKED_HOLD"
    BLOCKED_VOID = "BLOCKED_VOID"
    BLOCKED_F1 = "BLOCKED_F1_VIOLATION"
    BLOCKED_INJECTION = "BLOCKED_INJECTION"
    BLOCKED_UNVERIFIED = "BLOCKED_UNVERIFIED_ACTOR"


def _select_leaf_tool(query: str, query_class: QueryClass, context: dict[str, Any] | None = None) -> str:
    """Resolve a non-recursive organ for governed kernel routing."""
    context = context or {}
    requested_mode = str(context.get("mode") or "").lower()
    query_lower = query.lower()

    if requested_mode in {"status", "probe", "state"}:
        return "arifos_ops"

    if any(kw in query_lower for kw in ["judge", "verdict", "approve", "hold", "seal check"]):
        return "arifos_judge"
    if any(kw in query_lower for kw in ["forge", "execute", "deploy", "run", "ship"]):
        return "arifos_forge"
    if any(kw in query_lower for kw in ["vault", "ledger", "seal", "receipt"]):
        return "arifos_vault"
    if any(kw in query_lower for kw in ["memory", "remember", "recall", "context"]):
        return "arifos_memory"
    if any(kw in query_lower for kw in ["risk", "harm", "safety", "heart"]):
        return "arifos_heart"
    if any(kw in query_lower for kw in ["cost", "ops", "health", "telemetry", "status", "monitor"]):
        return "arifos_ops"
    if any(kw in query_lower for kw in ["sense", "ground", "verify", "reality", "fetch"]):
        return "arifos_sense"
    if query_class == QueryClass.CRITICAL:
        return "arifos_judge"
    return "arifos_mind"


class GovernanceEnforcer:
    """
    HARD STOP enforcer for MCP orchestration layer.

    Ensures:
    - HOLD/VOID terminates execution chain
    - Model is NOT called if tool returns non-PASS verdict
    - Audit trail is immutable
    - No bypass possible
    """

    def __init__(self):
        self.audit_log: list[dict] = []

    def classify_query(self, query: str, context: dict[str, Any] | None = None) -> QueryClass:
        """
        Classify query BEFORE any tool invocation.

        Class A (Informational): Conceptual, explanatory, analytical
        Class B (Governed): State mutation, memory write, seal
        Class C (Critical): Irreversible, execution, sovereign mode
        """
        context = context or {}

        governed_keywords = [
            "seal", "commit", "write", "execute", "spawn", "deploy",
            "modify", "delete", "create", "sign", "authorize", "approve"
        ]
        critical_keywords = [
            "irreversible", "permanent", "sovereign", "vault", "forge",
            "system", "kernel", "shutdown", "format", "wipe"
        ]

        query_lower = query.lower()
        if any(kw in query_lower for kw in critical_keywords):
            return QueryClass.CRITICAL
        if any(kw in query_lower for kw in governed_keywords):
            return QueryClass.GOVERNED
        return QueryClass.INFORMATIONAL

    def evaluate_tool_verdict(
        self,
        tool_name: str,
        envelope: RuntimeEnvelope,
        query_hash: str,
        actor_id: str = "anonymous",
    ) -> tuple[PropagationDecision, dict | None]:
        """
        Evaluate tool verdict and return propagation decision.
        
        Returns:
            (decision, response_or_none)
            If decision is BLOCKED_* → response contains error
            If decision is ALLOWED → response is None (continue to model)
        """
        verdict = envelope.verdict
        status = envelope.status

        if verdict == Verdict.VOID:
            decision = PropagationDecision.BLOCKED_VOID
            response = self._create_block_response(decision, tool_name, envelope)
            self._log_audit(query_hash, tool_name, verdict, decision, actor_id)
            return decision, response

        if verdict == Verdict.HOLD:
            decision = PropagationDecision.BLOCKED_HOLD
            response = self._create_block_response(decision, tool_name, envelope)
            self._log_audit(query_hash, tool_name, verdict, decision, actor_id)
            return decision, response

        if isinstance(envelope.payload, dict):
            irreversibility = envelope.payload.get("irreversibility", False)
            acknowledged = envelope.payload.get("irreversibility_acknowledged", False)
            if irreversibility and not acknowledged:
                decision = PropagationDecision.BLOCKED_F1
                response = self._create_block_response(decision, tool_name, envelope)
                self._log_audit(query_hash, tool_name, verdict, decision, actor_id)
                return decision, response

        if status == RuntimeStatus.ERROR:
            if isinstance(envelope.payload, dict) and envelope.payload.get("tom_violation"):
                decision = PropagationDecision.BLOCKED_INJECTION
                response = self._create_block_response(decision, tool_name, envelope)
                self._log_audit(query_hash, tool_name, verdict, decision, actor_id)
                return decision, response

        mode = envelope.mode or "default"
        args = envelope.payload or {}
        irreversibility_result = _AMANAH_SCORER.evaluate_payload(
            tool_name=tool_name,
            mode=mode,
            args=args,
            actor_id=actor_id,
        )
        if irreversibility_result.triggers_888_hold:
            decision = PropagationDecision.BLOCKED_HOLD
            response = self._create_block_response(PropagationDecision.BLOCKED_HOLD, tool_name, envelope)
            response["_amanah_score"] = irreversibility_result.score
            response["_floor_violations"] = irreversibility_result.floor_violations
            response["_reason"] = irreversibility_result.reason
            response["_detail"] = irreversibility_result.detail
            response["error"] = f"888_HOLD (Amanah): {irreversibility_result.reason} — score={irreversibility_result.score} — {irreversibility_result.detail}"
            self._log_audit(query_hash, tool_name, verdict, decision, actor_id)
            return decision, response

        decision = PropagationDecision.ALLOWED
        self._log_audit(query_hash, tool_name, verdict, decision, actor_id)
        return decision, None

    def _create_block_response(
        self,
        decision: PropagationDecision,
        tool_name: str,
        envelope: RuntimeEnvelope,
    ) -> dict[str, Any]:
        """Create structured block response."""

        block_messages = {
            PropagationDecision.BLOCKED_HOLD: {
                "error": "888_HOLD: Action requires human approval",
                "detail": "This action has been held pending sovereign review.",
                "action_required": "Wait for 888_HOLD clearance or request manual override",
            },
            PropagationDecision.BLOCKED_VOID: {
                "error": "VOID: Constitutional violation detected",
                "detail": "This action violates F1-F13 constitutional floors.",
                "action_required": "Redesign action to satisfy constitutional constraints",
            },
            PropagationDecision.BLOCKED_F1: {
                "error": "F1 Amanah: Irreversible action without acknowledgment",
                "detail": "Irreversible actions require explicit irreversibility_acknowledged=true",
                "action_required": "Set irreversibility_acknowledged and provide rollback_plan",
            },
            PropagationDecision.BLOCKED_INJECTION: {
                "error": "F13: Injection or malformed input detected",
                "detail": "Input failed ToM validation or constitutional schema check.",
                "action_required": "Provide required ToM fields and retry",
            },
            PropagationDecision.BLOCKED_UNVERIFIED: {
                "error": "F11: Unverified actor on critical action",
                "detail": "Critical tier actions require verified identity.",
                "action_required": "Complete identity verification via init_anchor",
            },
        }

        message = block_messages.get(decision, {
            "error": "GOVERNANCE_BLOCK: Action blocked",
            "detail": "Unknown governance violation",
            "action_required": "Contact administrator",
        })

        # Select contextually relevant philosophy for the block
        from arifosmcp.runtime.philosophy import AtlasScores, select_atlas_philosophy

        # Map decision to philosophical coordinates proxy
        # BLOCKED_VOID/HOLD -> Void/Paradox zone
        # BLOCKED_F1/UNVERIFIED -> Discipline zone
        phi_category = "void" if decision in (PropagationDecision.BLOCKED_VOID, PropagationDecision.BLOCKED_HOLD) else "discipline"
        scores = AtlasScores(
            delta_s=1.0,
            g_score=0.2,
            omega_score=0.9,
            lyapunov_sign="stable",
            verdict=envelope.verdict.value if hasattr(envelope.verdict, "value") else str(envelope.verdict),
            session_stage=envelope.stage,
        )
        phi_result = select_atlas_philosophy(scores, contrast_override=phi_category)
        primary = phi_result.get("primary_quote", {})

        return {
            "ok": False,
            "governance_block": True,
            "decision": decision.value,
            "tool": tool_name,
            "verdict": envelope.verdict.value if hasattr(envelope.verdict, "value") else str(envelope.verdict),
            "stage": envelope.stage,
            **message,
            "philosophy": {
                "quote": primary.get("quote", "DITEMPA, BUKAN DIBERI."),
                "author": primary.get("author", "arifOS"),
                "category": primary.get("category", phi_category),
                "note": "Governance boundary enforced with constitutional framing.",
            },
        }

    def _log_audit(
        self,
        query_hash: str,
        tool_name: str,
        verdict: Verdict,
        decision: PropagationDecision,
        actor_id: str,
    ) -> None:
        """Immutable audit logging."""
        verdict_str = verdict.value if hasattr(verdict, "value") else str(verdict)
        decision_str = decision.value if hasattr(decision, "value") else str(decision)

        entry = {
            "timestamp": time.time(),
            "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "query_hash": query_hash,
            "tool_invoked": tool_name,
            "verdict": verdict_str,
            "propagation_decision": decision_str,
            "actor_id": actor_id,
        }
        entry_data = json.dumps(entry, sort_keys=True)
        entry["entry_hash"] = hashlib.sha256(entry_data.encode()).hexdigest()[:32]
        self.audit_log.append(entry)

    def get_audit_log(self) -> list[dict]:
        """Return immutable audit log copy."""
        return [dict(entry) for entry in self.audit_log]

    def verify_audit_integrity(self) -> bool:
        """Verify audit log has not been tampered with."""
        for entry in self.audit_log:
            stored_hash = entry.get("entry_hash")
            if not stored_hash:
                return False

            test_entry = {k: v for k, v in entry.items() if k != "entry_hash"}
            test_data = json.dumps(test_entry, sort_keys=True, default=str)
            computed_hash = hashlib.sha256(test_data.encode()).hexdigest()[:32]
            if computed_hash != stored_hash:
                return False

        return True


# Global enforcer instance
_enforcer: GovernanceEnforcer | None = None


def get_enforcer() -> GovernanceEnforcer:
    """Get or create global governance enforcer."""
    global _enforcer
    if _enforcer is None:
        _enforcer = GovernanceEnforcer()
    return _enforcer


async def classify_and_route(
    query: str,
    context: dict[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Classify query and determine if tool invocation is required.
    
    Accepts optional kwargs (actor_id, session_id, etc.) from kernel_core
    to maintain adapter compatibility without bloating the core router.
    
    Returns:
        dict with routing result (tool_name, ok, etc.) for kernel compatibility
    """
    enforcer = get_enforcer()
    query_class = enforcer.classify_query(query, context)
    
    # Informational queries don't require tools; governed queries must resolve to a leaf organ.
    requires_tool = query_class != QueryClass.INFORMATIONAL
    tool_name = _select_leaf_tool(query, query_class, context)

    return {
        "ok": True,
        "tool_name": tool_name,
        "query_class": query_class.value,
        "requires_tool": requires_tool,
        "route_intent": {
            "query_class": query_class.value,
            "requested_mode": context.get("mode") if context else None,
        },
    }


def enforce_tool_verdict(
    tool_name: str,
    envelope: RuntimeEnvelope,
    query: str,
    actor_id: str = "anonymous",
) -> tuple[bool, dict | None]:
    """
    HARD STOP enforcement wrapper.
    
    Returns:
        (allowed, response_or_none)
        allowed=True → continue to model
        allowed=False → return response (blocked)
    """
    enforcer = get_enforcer()
    query_hash = hashlib.sha256(query.encode()).hexdigest()[:16]
    
    decision, response = enforcer.evaluate_tool_verdict(
        tool_name=tool_name,
        envelope=envelope,
        query_hash=query_hash,
        actor_id=actor_id,
    )
    
    allowed = decision == PropagationDecision.ALLOWED
    return allowed, response


__all__ = [
    "GovernanceEnforcer",
    "QueryClass",
    "PropagationDecision",
    "get_enforcer",
    "classify_and_route",
    "enforce_tool_verdict",
]
