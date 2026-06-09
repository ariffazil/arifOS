"""
arifos_route_query — Mandatory Pre-Retrieval Gate Handler.

This is the 14th canonical tool in the arifOS surface. Every agent
MUST call this before any search/discovery/retrieval tool call.

Architecture:
  arifos_route_query → RoutePolicyEngine.decide() → RouteDecision
    ↓
  Agent receives routing plan → executes tool calls per plan
    ↓
  Guard middleware (routes/guard.py) blocks search tools without prior route

Deterministic. No LLM call. F2 TRUTH: no fabrication. F4 CLARITY: structured output.

DITEMPA BUKAN DIBERI — Routing is policy, not vibes.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field

from .route_policy import RoutePolicyEngine, get_route_policy_engine, reset_route_policy_engine
from .route_audit import log_route_decision

logger = logging.getLogger(__name__)


# ── I/O Schema (Pydantic v2) ───────────────────────────────────────────────


class RouteQueryInput(BaseModel):
    """Input schema for arifos_route_query. Matches Copilot spec."""
    query: str = Field(
        ...,
        description="The user's natural language query. Will be classified for routing.",
    )
    mode: str | None = Field(
        default=None,
        description="Explicit mode override: 'exploit', 'explore', or 'hybrid'. "
                    "If None, deterministic rules determine the lane.",
    )
    session_id: str | None = Field(
        default=None,
        description="Current governed session ID from arif_session_init.",
    )
    actor_id: str | None = Field(
        default=None,
        description="Actor identifier for audit trail.",
    )
    max_exploit_results: int | None = Field(
        default=None,
        description="Override max results for exploit lane.",
    )
    max_explore_results: int | None = Field(
        default=None,
        description="Override max results for explore lane.",
    )
    require_contradiction: bool = Field(
        default=False,
        description="If True, mandates at least 1 contradiction doc in results.",
    )
    auth_context: dict[str, Any] | None = Field(
        default=None,
        description="Identity + entitlement context for ACL filtering.",
    )


class RouteQueryOutput(BaseModel):
    """Output schema for arifos_route_query. The routing plan."""
    lane: str = Field(..., description="Determined lane: exploit | explore | hybrid")
    reason: str = Field(..., description="Why this lane was chosen (rule trace)")
    target_tools: list[str] = Field(
        default_factory=list,
        description="Tools to invoke for this query, in priority order.",
    )
    constraints: dict[str, Any] = Field(
        default_factory=dict,
        description="Hard constraints for tool execution: contradiction quota, budgets.",
    )
    budget: dict[str, Any] = Field(
        default_factory=dict,
        description="Per-lane budget: remaining results and tokens.",
    )
    audit: dict[str, Any] = Field(
        default_factory=dict,
        description="F11 audit trail for this routing decision.",
    )
    next_action: str = Field(
        default="proceed",
        description="Recommended next step: proceed | caution | hold",
    )
    governance: dict[str, Any] = Field(
        default_factory=dict,
        description="Floor compliance status for this routing decision.",
    )


# ── Handler ────────────────────────────────────────────────────────────────


async def arifos_route_query(
    query: str,
    mode: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    max_exploit_results: int | None = None,
    max_explore_results: int | None = None,
    require_contradiction: bool = False,
    auth_context: dict[str, Any] | None = None,
    _envelope: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Route a natural language query to the correct retrieval lane.

    Call this BEFORE any search/discovery tool. Returns a routing plan
    with target tools, constraints, and budget allocation.

    F2 TRUTH: Deterministic rules, no LLM call. F4 CLARITY: Structured output.
    F11 AUDITABILITY: Every decision logged.
    """
    engine = get_route_policy_engine()
    sid = session_id or (_envelope or {}).get("session_id", "unknown")
    aid = actor_id or (_envelope or {}).get("actor_id", "unknown")

    # Override budget if specified
    if max_exploit_results is not None:
        engine._session_budget.exploit.max_results = max_exploit_results
    if max_explore_results is not None:
        engine._session_budget.explore.max_results = max_explore_results

    # Hard requirement: contradiction docs
    if require_contradiction:
        engine._session_budget.min_contradiction_docs = max(
            engine._session_budget.min_contradiction_docs, 1
        )

    # Make deterministic routing decision
    decision = engine.decide(
        query=query,
        session_id=sid,
        actor_id=aid,
        explicit_mode=mode,
        auth_context=auth_context,
    )

    # Log to audit trail (F11)
    floors_checked = ["F1", "F2", "F4", "F7", "F11", "F13"]
    auth_verified = bool(auth_context and auth_context.get("identity_verified"))
    log_route_decision(
        decision=decision,
        query=query,
        floors_checked=floors_checked,
        auth_verified=auth_verified,
        entitlement=auth_context.get("entitlement", "unknown") if auth_context else "unknown",
        agent_name=aid,
    )

    # Determine next_action
    if decision.audit.error:
        next_action = "caution"
    elif decision.audit.fallback_used:
        next_action = "caution"
    elif not decision.constraints.get("contradiction_quota_met", True):
        next_action = "proceed"  # Still proceed, but constraint is noted
    else:
        next_action = "proceed"

    return {
        "lane": decision.lane.value,
        "reason": decision.reason.value,
        "target_tools": decision.target_tools,
        "constraints": decision.constraints,
        "budget": {
            "exploit": {
                "remaining_results": decision.audit.budget_exploit_results,
                "max_results": max_exploit_results or engine.config.max_exploit_results,
            },
            "explore": {
                "remaining_results": decision.audit.budget_explore_results,
                "max_results": max_explore_results or engine.config.max_explore_results,
            },
            "session_explore_ratio": decision.audit.session_explore_ratio,
            "contradiction_quota_met": decision.audit.contradiction_quota_met,
        },
        "audit": {
            "query_hash": decision.audit.query_hash,
            "latency_ms": decision.audit.latency_ms,
            "timestamp": decision.audit.timestamp,
            "floors_checked": floors_checked,
            "exploration_triggered": decision.audit.exploration_triggered,
        },
        "next_action": next_action,
        "governance": {
            "floors_active": floors_checked,
            "decision_binding": "advisory",
            "reversible": True,
            "delta_S": 0.0,
            "verdict": "SEAL" if not decision.audit.error else "CAUTION",
        },
    }


# ── Session Management ─────────────────────────────────────────────────────


def reset_route_session() -> dict[str, Any]:
    """Reset the route policy engine for a new session."""
    reset_route_policy_engine()
    return {"status": "reset", "message": "Route policy engine reset for new session."}


def get_route_status() -> dict[str, Any]:
    """Get current route policy engine status."""
    engine = get_route_policy_engine()
    budget = engine.session_budget
    return {
        "exploit_remaining": budget.exploit.remaining_results,
        "explore_remaining": budget.explore.remaining_results,
        "session_explore_ratio": budget.explore_ratio,
        "session_contradiction_count": budget._session_contradiction_count,
        "contradiction_quota_met": budget.contradiction_quota_met,
        "explore_quota_met": budget.explore_quota_met,
    }
