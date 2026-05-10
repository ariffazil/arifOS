"""
arifOS MCP Resources — Tool Self-Model, Witness Log, Domain Boundaries
═══════════════════════════════════════════════════════════════════════════════════════

Exposes embodied tool intelligence as MCP resources:

- arifos://tools/self-model          — The agent's tool body
- arifos://tools/permissions        — Current permission state
- arifos://tools/composition-matrix  — Tool composition safety
- arifos://witness/log              — Audit trail
- arifos://witness/stats            — Witness log statistics
- arifos://boundaries/domain        — Domain policy for each MCP organ

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
from typing import Any

from fastmcp import FastMCP

# ── Tool Self-Model Resource ────────────────────────────────────────────────────


def get_tool_self_model_resource() -> dict[str, Any]:
    """
    MCP resource: arifos://tools/self-model

    Returns the agent's complete runtime self-model of its own tools.
    This is what the agent queries before every tool call.
    """
    from arifosmcp.core.tool_self_model import get_tool_self_model

    model = get_tool_self_model()
    summary = model.summary()
    tools = []

    for entry in model.list_all():
        tools.append(
            {
                "tool_id": entry.manifest.tool_id,
                "tool_name": entry.manifest.tool_name,
                "domain": entry.manifest.domain,
                "risk_tier": entry.manifest.risk_tier,
                "reversibility": entry.manifest.reversibility,
                "blast_radius": entry.manifest.blast_radius.value,
                "last_used": entry.last_used,
                "use_count": entry.use_count,
                "failure_count": entry.failure_count,
                "has_permission_gap": entry.has_permission_gap,
                "permission_gap": entry.permission_gap,
                "is_safe_to_execute": entry.is_safe_to_execute,
                "capabilities": [
                    {"name": c.name, "description": c.description}
                    for c in entry.manifest.capabilities
                ],
                "limitations": [
                    {"name": lim.name, "description": lim.description}
                    for lim in entry.manifest.limitations
                ],
                "safe_compose_with": entry.manifest.safe_compose_with,
                "dangerous_compose_with": entry.manifest.dangerous_compose_with,
            }
        )

    return {
        "uri": "arifos://tools/self-model",
        "mime_type": "application/json",
        "body": {
            "summary": summary,
            "tools": tools,
        },
    }


def get_tool_permissions_resource() -> dict[str, Any]:
    """
    MCP resource: arifos://tools/permissions

    Returns the agent's current permission state.
    """
    from arifosmcp.core.tool_self_model import get_tool_self_model

    model = get_tool_self_model()

    executable = [e for e in model.list_all() if e.is_safe_to_execute]
    blocked = [e for e in model.list_all() if not e.is_safe_to_execute]

    return {
        "uri": "arifos://tools/permissions",
        "mime_type": "application/json",
        "body": {
            "agent_permissions": sorted(model._agent_permissions),
            "executable_count": len(executable),
            "blocked_count": len(blocked),
            "executable_tools": [e.manifest.tool_id for e in executable],
            "blocked_tools": [
                {
                    "tool_id": e.manifest.tool_id,
                    "reason": (
                        "permission_gap" if e.has_permission_gap else "failure_count_exceeded"
                    ),
                    "gap": e.permission_gap if e.has_permission_gap else [],
                }
                for e in blocked
            ],
        },
    }


def get_tool_composition_resource() -> dict[str, Any]:
    """
    MCP resource: arifos://tools/composition-matrix

    Returns the tool composition safety matrix.
    """
    from arifosmcp.core.tool_self_model import get_tool_self_model

    model = get_tool_self_model()
    compositions = []

    for entry in model.list_all():
        tool_id = entry.manifest.tool_id
        for other_id in model.list_all():
            if other_id.manifest.tool_id == tool_id:
                continue
            is_safe, reason = model.check_composition(tool_id, other_id.manifest.tool_id)
            compositions.append(
                {
                    "before": tool_id,
                    "after": other_id.manifest.tool_id,
                    "safe": is_safe,
                    "reason": reason,
                }
            )

    return {
        "uri": "arifos://tools/composition-matrix",
        "mime_type": "application/json",
        "body": {
            "compositions": compositions,
            "dangerous_count": sum(1 for c in compositions if not c["safe"]),
            "safe_count": sum(1 for c in compositions if c["safe"]),
        },
    }


# ── Witness Log Resource ─────────────────────────────────────────────────────


def get_witness_log_resource(
    session_id: str | None = None,
    tool_id: str | None = None,
    status: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    """
    MCP resource: arifos://witness/log

    Returns recent witness records with optional filtering.
    """
    from arifosmcp.core.witness_log import get_witness_log

    log = get_witness_log()
    records = log.query(
        session_id=session_id,
        tool_id=tool_id,
        status=status,
        limit=limit,
    )

    return {
        "uri": "arifos://witness/log",
        "mime_type": "application/json",
        "body": {
            "records": [
                {
                    "record_id": r.record_id,
                    "chain_id": r.chain_id,
                    "timestamp": r.timestamp,
                    "tool_id": r.tool_id,
                    "actor_id": r.actor_id,
                    "session_id": r.session_id,
                    "domain": r.domain,
                    "risk_tier": r.risk_tier,
                    "reversibility": r.reversibility,
                    "status": r.status,
                    "confidence": r.confidence,
                    "authority_verified": r.authority_verified,
                    "latency_ms": r.latency_ms,
                    "input_hash": r.input_hash,
                    "reasoning_summary": r.reasoning_summary,
                    "error": r.error,
                    "next_action": r.next_action,
                }
                for r in records
            ],
            "chain_tip": log.get_chain_tip(),
        },
    }


def get_witness_stats_resource() -> dict[str, Any]:
    """
    MCP resource: arifos://witness/stats

    Returns witness log statistics.
    """
    from arifosmcp.core.witness_log import get_witness_log

    log = get_witness_log()
    stats = log.stats()
    chain_valid, chain_message = log.verify_chain()

    return {
        "uri": "arifos://witness/stats",
        "mime_type": "application/json",
        "body": {
            **stats,
            "chain_verified": chain_valid,
            "chain_message": chain_message,
        },
    }


# ── Domain Boundary Policy ────────────────────────────────────────────────────


DOMAIN_BOUNDARY_POLICY = {
    "AOS": {
        "name": "arifOS Governance Body",
        "sensors": [
            "actor_identity",
            "session_state",
            "authority_level",
            "request_intent",
            "risk_tier",
            "reversibility",
            "uncertainty",
            "tool_availability",
            "injection_attempts",
            "domain_being_invoked",
        ],
        "actuators": [
            "approve_route",
            "hold_route",
            "void_unsafe_action",
            "require_authentication",
            "escalate_to_arif",
            "issue_domain_seal",
            "classify_risk",
            "generate_audit_record",
            "enforce_veto",
            "limit_tool_scope",
            "freeze_execution",
        ],
        "must_not": [
            "directly perform domain actions unless explicitly routed",
            "impersonate WELL",
            "impersonate WEALTH",
            "impersonate GEOX",
            "make health recommendations",
            "execute financial operations",
            "approve physical-world clearances",
        ],
        "hard_gate": "Human sovereignty — Arif is final judge",
    },
    "WELL": {
        "name": "Human Wellness Body",
        "sensors": [
            "stress_level",
            "fatigue_signals",
            "sleep_context",
            "emotional_load",
            "health_statements",
            "urgency",
            "self_harm_risk",
            "medical_uncertainty",
            "readiness_for_action",
            "human_burden",
            "overexertion_patterns",
        ],
        "actuators": [
            "suggest_rest",
            "suggest_reflection",
            "classify_readiness",
            "recommend_non_medical_wellness",
            "escalate_medical_emergency",
            "warn_about_overload",
            "produce_human_centered_plans",
            "set_soft_limits",
            "recommend_pause",
            "support_emotional_regulation",
        ],
        "must_not": [
            "diagnose",
            "prescribe_medication",
            "replace_clinician_judgment",
            "encourage_dangerous_physical_actions",
            "minimize_crisis_signals",
            "manipulate_emotions",
            "claim_certainty_about_health",
        ],
        "hard_gate": "Medical/emergency boundary — clinician referral required",
        "reflexes": {
            "distress_high": "reduce complexity",
            "fatigue_high": "recommend pause",
            "self_harm_risk": "emergency escalation",
            "medical_uncertainty": "clinician referral",
            "human_readiness_low": "no aggressive execution",
        },
    },
    "WEALTH": {
        "name": "Economic / Resource Body",
        "sensors": [
            "financial_objective",
            "time_horizon",
            "risk_tolerance",
            "liquidity",
            "debt",
            "cash_flow",
            "opportunity_cost",
            "concentration_risk",
            "incentives",
            "externalities",
            "fraud_signals",
            "authority_to_act",
            "jurisdiction",
            "ethical_risk",
        ],
        "actuators": [
            "analyze_scenarios",
            "compare_tradeoffs",
            "generate_budgets",
            "model_risk",
            "detect_scams",
            "produce_investment_education",
            "recommend_questions",
            "flag_uncertainty",
            "generate_decision_memos",
            "require_human_approval",
        ],
        "must_not": [
            "execute_trades",
            "move_money",
            "sign_contracts",
            "guarantee_returns",
            "give_reckless_investment_advice",
            "hide_risk",
            "optimize_profit_against_human_dignity",
            "bypass_regulatory_constraints",
        ],
        "hard_gate": "No money movement without explicit Arif approval",
        "reflexes": {
            "irreversible_financial": "require Arif approval",
            "high_risk_investment": "show downside first",
            "scam_pattern": "warn and freeze",
            "uncertainty_high": "scenario analysis only",
            "conflict_of_interest": "disclose",
        },
    },
    "GEOX": {
        "name": "Earth / Physical Reality Body",
        "sensors": [
            "location",
            "coordinates",
            "maps",
            "geological_context",
            "remote_sensing_data",
            "seismic_data",
            "subsurface_data",
            "terrain",
            "hazards",
            "environmental_risk",
            "infrastructure_proximity",
            "spatial_uncertainty",
            "temporal_change",
            "physical_constraints",
            "data_resolution",
            "confidence_envelope",
        ],
        "actuators": [
            "interpret_geospatial_data",
            "generate_maps",
            "classify_hazards",
            "compare_geological_scenarios",
            "model_uncertainty",
            "flag_missing_data",
            "recommend_survey_needs",
            "produce_technical_notes",
            "detect_physical_impossibility",
            "route_high_risk_findings_for_human_review",
        ],
        "must_not": [
            "issue_final_safety_clearance",
            "approve_drilling_construction_field_operation",
            "override_human_geoscientist_judgment",
            "claim_certainty_beyond_data",
            "hide_uncertainty",
            "act_on_low_resolution_as_high_resolution",
            "make_irreversible_field_recommendations_without_review",
        ],
        "hard_gate": "No physical-world clearance without human geoscientist review",
        "reflexes": {
            "location_uncertainty_high": "no precise claim",
            "hazard_possible": "flag early",
            "data_resolution_insufficient": "mark confidence low",
            "physical_action_implied": "require human review",
            "environmental_harm_possible": "escalate",
        },
    },
}


def get_domain_boundaries_resource() -> dict[str, Any]:
    """
    MCP resource: arifos://boundaries/domain

    Returns domain boundary policy for each MCP organ.
    """
    return {
        "uri": "arifos://boundaries/domain",
        "mime_type": "application/json",
        "body": DOMAIN_BOUNDARY_POLICY,
    }


# ── FastMCP Resource Registration ───────────────────────────────────────────


def register_embodied_resources(mcp: FastMCP) -> list[str]:
    """Register embodied tool intelligence resources on the given FastMCP server."""
    registered: list[str] = []

    @mcp.resource(
        "arifos://tools/self-model/{view}",
        description=(
            "The agent's complete runtime self-model of its own tools. "
            "Returns every registered tool with capabilities, limitations, "
            "risk tier, blast radius, permission gaps, and composition rules."
        ),
    )
    async def get_self_model(view: str = "full") -> str:
        return json.dumps(get_tool_self_model_resource()["body"], indent=2)

    registered.append("arifos://tools/self-model/{view}")

    @mcp.resource(
        "arifos://tools/permissions/{scope}",
        description=(
            "Current permission state: which tools are executable vs blocked, "
            "agent permissions held, and permission gap analysis."
        ),
    )
    async def get_permissions(scope: str = "all") -> str:
        return json.dumps(get_tool_permissions_resource()["body"], indent=2)

    registered.append("arifos://tools/permissions/{scope}")

    @mcp.resource(
        "arifos://tools/composition-matrix/{format}",
        description=(
            "Tool composition safety matrix. Returns safe/dangerous pairings "
            "for every registered tool combination."
        ),
    )
    async def get_composition_matrix(format: str = "json") -> str:
        return json.dumps(get_tool_composition_resource()["body"], indent=2)

    registered.append("arifos://tools/composition-matrix/{format}")

    @mcp.resource(
        "arifos://witness/log/{filter}",
        description=(
            "Recent witness log records with optional filtering by session, tool, or status. "
            "Query parameters: session_id, tool_id, status, limit."
        ),
    )
    async def get_witness_log(
        filter: str = "latest",
        session_id: str | None = None,
        tool_id: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> str:
        return json.dumps(
            get_witness_log_resource(
                session_id=session_id,
                tool_id=tool_id,
                status=status,
                limit=limit,
            )["body"],
            indent=2,
        )

    registered.append("arifos://witness/log/{filter}")

    @mcp.resource(
        "arifos://witness/stats/{period}",
        description=(
            "Witness log statistics: total records, seal/hold/void rates, "
            "chain verification status, and domain breakdown."
        ),
    )
    async def get_witness_stats(period: str = "all") -> str:
        return json.dumps(get_witness_stats_resource()["body"], indent=2)

    registered.append("arifos://witness/stats/{period}")

    @mcp.resource(
        "arifos://boundaries/domain/{domain_id}",
        description=(
            "Domain boundary policy for each MCP organ (AOS, WELL, WEALTH, GEOX). "
            "Sensors, actuators, must_not list, hard gates, and reflexes."
        ),
    )
    async def get_domain_boundaries(domain_id: str = "all") -> str:
        return json.dumps(get_domain_boundaries_resource()["body"], indent=2)

    registered.append("arifos://boundaries/domain/{domain_id}")

    return registered


# ── Unified resource registry ───────────────────────────────────────────────

RESOURCE_HANDLERS = {
    "arifos://tools/self-model": get_tool_self_model_resource,
    "arifos://tools/permissions": get_tool_permissions_resource,
    "arifos://tools/composition-matrix": get_tool_composition_resource,
    "arifos://witness/log": get_witness_log_resource,
    "arifos://witness/stats": get_witness_stats_resource,
    "arifos://boundaries/domain": get_domain_boundaries_resource,
}


def handle_resource(uri: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Handle an MCP resource request.

    Usage:
        resource = handle_resource("arifos://tools/self-model")
        resource = handle_resource("arifos://witness/log", {"session_id": "sess_abc123"})
    """
    handler = RESOURCE_HANDLERS.get(uri)
    if handler is None:
        return {
            "uri": uri,
            "error": f"Unknown resource: {uri}",
            "available": list(RESOURCE_HANDLERS.keys()),
        }

    try:
        result = handler() if params is None else handler(**params)
        return result
    except TypeError:
        # Handler doesn't accept those params
        return {
            "uri": uri,
            "error": f"Resource does not accept those parameters: {params}",
        }
    except Exception as e:
        return {
            "uri": uri,
            "error": str(e),
        }


__all__ = [
    "get_tool_self_model_resource",
    "get_tool_permissions_resource",
    "get_tool_composition_resource",
    "get_witness_log_resource",
    "get_witness_stats_resource",
    "get_domain_boundaries_resource",
    "DOMAIN_BOUNDARY_POLICY",
    "RESOURCE_HANDLERS",
    "handle_resource",
]
