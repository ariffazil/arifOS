"""
arifosmcp/runtime/tools.py — arifOS Functional Tool Surface

Canonical tool surface for arifOS MCP.
Implements functional-verb tool names as shims over mega-tools.

Functional Tools:
  init_session_anchor  → Established identity
  get_tool_registry    → Discovery
  sense_reality        → Grounding
  reason_synthesis     → Synthesis
  critique_safety      → Red-teaming
  route_execution      → Metabolic conductor
  load_memory_context  → Vector retrieval
  estimate_ops         → Quantitative vitals
  judge_verdict        → Constitutional verdict
  record_vault_entry   → Immutable sealing
  execute_vps_task     → Code execution

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from arifosmcp.runtime.continuity_contract import seal_runtime_envelope
from arifosmcp.runtime.contracts import (
    ConstitutionalHealthView,
    RiskTier,
    TelemetryEnvelope,
    VerdictCode,
    VerdictRecord,
)
from arifosmcp.runtime.megaTools import (
    agi_mind as _mega_agi_mind,
    apex_judge as _mega_apex_judge,
    architect_registry as _mega_architect_registry,
    arifOS_kernel as _mega_arifOS_kernel,
    asi_heart as _mega_asi_heart,
    code_engine as _mega_code_engine,
    engineering_memory as _mega_engineering_memory,
    init_anchor as _mega_init_anchor,
    math_estimator as _mega_math_estimator,
    physics_reality as _mega_physics_reality,
    vault_ledger as _mega_vault_ledger,
)
from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus
from arifosmcp.runtime.rest_routes import _build_governance_status_payload
from fastmcp import FastMCP

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# FUNCTIONAL TOOL SHIMS
# ═══════════════════════════════════════════════════════════════════════════════

async def init_session_anchor(
    mode: str = "init",
    payload: dict[str, Any] | None = None,
    actor_id: str | None = None,
    intent: str | None = None,
    declared_name: str | None = None,
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    allow_execution: bool = False,
    debug: bool = False,
) -> RuntimeEnvelope:
    """Start a governed session and bind the initial telemetry seed."""
    envelope = await _mega_init_anchor(
        mode=mode,
        payload=payload or {"actor_id": actor_id, "intent": intent, "declared_name": declared_name},
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        allow_execution=allow_execution,
        debug=debug,
    )
    return seal_runtime_envelope(envelope, "init_session_anchor")


async def get_tool_registry(
    mode: str = "list",
    payload: dict[str, Any] | None = None,
    uri: str | None = None,
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    debug: bool = False,
) -> RuntimeEnvelope:
    """Discover arifOS tool graph, modes, and model capabilities."""
    envelope = await _mega_architect_registry(
        mode=mode,
        payload=payload or {"uri": uri},
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        debug=debug,
    )
    return seal_runtime_envelope(envelope, "get_tool_registry")


async def sense_reality(
    mode: str = "search",
    payload: dict[str, Any] | None = None,
    query: str | None = None,
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    debug: bool = False,
) -> RuntimeEnvelope:
    """Time grounding, evidence checks, and reality state verification."""
    envelope = await _mega_physics_reality(
        mode=mode,
        payload=payload or {"query": query},
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        debug=debug,
    )
    return seal_runtime_envelope(envelope, "sense_reality")


async def reason_synthesis(
    mode: str = "reason",
    payload: dict[str, Any] | None = None,
    query: str | None = None,
    context: str | None = None,
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    debug: bool = False,
) -> RuntimeEnvelope:
    """Multi-source synthesis and structured first-principles reasoning."""
    envelope = await _mega_agi_mind(
        mode=mode,
        payload=payload or {"query": query, "context": context},
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        debug=debug,
    )
    return seal_runtime_envelope(envelope, "reason_synthesis")


async def critique_safety(
    mode: str = "critique",
    payload: dict[str, Any] | None = None,
    content: str | None = None,
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    debug: bool = False,
) -> RuntimeEnvelope:
    """Safety, dignity, and adversarial critique of content or proposals."""
    envelope = await _mega_asi_heart(
        mode=mode,
        payload=payload or {"content": content},
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        debug=debug,
    )
    return seal_runtime_envelope(envelope, "critique_safety")


async def route_execution(
    mode: str = "kernel",
    payload: dict[str, Any] | None = None,
    query: str | None = None,
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    allow_execution: bool = False,
    debug: bool = False,
) -> RuntimeEnvelope:
    """Route request to the correct metabolic lane or tool family."""
    envelope = await _mega_arifOS_kernel(
        mode=mode,
        payload=payload or {"query": query},
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        allow_execution=allow_execution,
        debug=debug,
    )
    return seal_runtime_envelope(envelope, "route_execution")


async def load_memory_context(
    mode: str = "vector_query",
    payload: dict[str, Any] | None = None,
    query: str | None = None,
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    debug: bool = False,
) -> RuntimeEnvelope:
    """Retrieve governed memory and engineering context from vector store."""
    envelope = await _mega_engineering_memory(
        mode=mode,
        payload=payload or {"query": query},
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        debug=debug,
    )
    return seal_runtime_envelope(envelope, "load_memory_context")


async def estimate_ops(
    mode: str = "cost",
    payload: dict[str, Any] | None = None,
    action_description: str | None = None,
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    debug: bool = False,
) -> RuntimeEnvelope:
    """Calculate operation costs, thermodynamics, capacity, and timing."""
    envelope = await _mega_math_estimator(
        mode=mode,
        payload=payload or {"action": action_description},
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        debug=debug,
    )
    return seal_runtime_envelope(envelope, "estimate_ops")


async def judge_verdict(
    mode: str = "judge",
    payload: dict[str, Any] | None = None,
    candidate_action: str | None = None,
    risk_tier: str = "medium",
    telemetry: dict[str, Any] | None = None,
    session_id: str | None = None,
    dry_run: bool = True,
    debug: bool = False,
) -> RuntimeEnvelope:
    """Final constitutional verdict evaluation and hold logic enforcement."""
    envelope = await _mega_apex_judge(
        mode=mode,
        payload=payload or {
            "candidate": candidate_action,
            "risk_tier": risk_tier,
            "telemetry": telemetry,
        },
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        debug=debug,
    )
    return seal_runtime_envelope(envelope, "judge_verdict")


async def record_vault_entry(
    mode: str = "seal",
    payload: dict[str, Any] | None = None,
    verdict: str | None = None,
    evidence: str | None = None,
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    debug: bool = False,
) -> RuntimeEnvelope:
    """Append immutable verdict record to the Merkle-hashed ledger."""
    envelope = await _mega_vault_ledger(
        mode=mode,
        payload=payload or {"verdict": verdict, "evidence": evidence},
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        debug=debug,
    )
    return seal_runtime_envelope(envelope, "record_vault_entry")


async def execute_vps_task(
    mode: str = "fs",
    payload: dict[str, Any] | None = None,
    command: str | None = None,
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    allow_execution: bool = False,
    debug: bool = False,
) -> RuntimeEnvelope:
    """Redirect or dispatch execution tasks to the sovereign VPS executor."""
    envelope = await _mega_code_engine(
        mode=mode,
        payload=payload or {"command": command},
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        allow_execution=allow_execution,
        debug=debug,
    )
    return seal_runtime_envelope(envelope, "execute_vps_task")


# ═══════════════════════════════════════════════════════════════════════════════
# CHATGPT APPS SUBSET
# ═══════════════════════════════════════════════════════════════════════════════

async def get_constitutional_health(session_id: str = "global") -> ConstitutionalHealthView:
    """Read-only constitutional health snapshot for ChatGPT Apps."""
    status = _build_governance_status_payload()
    telemetry_data = status.get("telemetry", {})
    
    telemetry = TelemetryEnvelope(
        session_id=session_id,
        timestamp=status.get("timestamp", datetime.now(timezone.utc).isoformat()),
        tau_truth=telemetry_data.get("confidence", 0.99), # Map confidence to tau for health view
        omega_0=telemetry_data.get("omega", 0.04),
        delta_s=telemetry_data.get("dS", -0.35),
        peace2=telemetry_data.get("peace2", 1.04),
        kappa_r=telemetry_data.get("kappa_r", 0.97),
        tri_witness=0.95, # Default
        psi_le=telemetry_data.get("psi_le", 1.09),
        verdict_hint=VerdictCode.SEAL if status.get("verdict") == "SEAL" else VerdictCode.PARTIAL
    )
    
    return ConstitutionalHealthView(
        session_id=session_id,
        status="HEALTHY" if telemetry.tau_truth >= 0.9 else "DEGRADED",
        floors_active=13,
        telemetry=telemetry,
        widget_uri="ui://arifos/vault-seal-widget.html"
    )


async def render_vault_seal_shim(seal_data: dict[str, Any]) -> dict[str, Any]:
    """Shim for render_vault_seal."""
    from arifosmcp.runtime.chatgpt_integration.apps_sdk_tools import render_vault_seal
    return await render_vault_seal(seal_data)


async def list_recent_verdicts(limit: int = 5) -> list[VerdictRecord]:
    """Read-only summary of recent constitutional verdicts."""
    try:
        from arifosmcp.runtime.resources import arifos_vault_recent
        raw_res = arifos_vault_recent()
        import json
        data = json.loads(raw_res)
        recent = data.get("recent_verdicts", [])
        # In a real impl, we'd map these to VerdictRecord models
        return recent[:limit]
    except Exception:
        return []


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRATION
# ═══════════════════════════════════════════════════════════════════════════════

# Map CANONICAL names (from tool_specs.py) to wrapper functions
CANONICAL_TOOL_HANDLERS = {
    "init_anchor": init_session_anchor,
    "architect_registry": get_tool_registry,
    "physics_reality": sense_reality,
    "agi_mind": reason_synthesis,
    "asi_heart": critique_safety,
    "arifOS_kernel": route_execution,
    "engineering_memory": load_memory_context,
    "math_estimator": estimate_ops,
    "apex_soul": judge_verdict,
    "vault_ledger": record_vault_entry,
    "code_engine": execute_vps_task,
}

# Backward-compat aliases — for REST routing only, NOT registered as MCP tools
LEGACY_ALIASES: dict[str, str] = {}


def register_tools(mcp: FastMCP) -> None:
    """Register exactly 11 canonical mega-tools. No aliases, no ChatGPT extras."""
    from fastmcp.tools.function_tool import FunctionTool
    from arifosmcp.runtime.tool_specs import PUBLIC_TOOL_SPECS

    registered = []
    for spec in PUBLIC_TOOL_SPECS:
        handler = CANONICAL_TOOL_HANDLERS.get(spec.name)
        if not handler:
            logger.warning(f"No handler for canonical tool: {spec.name}")
            continue
        ft = FunctionTool.from_function(handler, name=spec.name, description=spec.description)
        ft.parameters = dict(spec.input_schema)
        mcp.add_tool(ft)
        registered.append(spec.name)

    logger.info(f"Registered {len(registered)} tools: {registered}")


# Backward-compat alias — server.py and tests may import either name
FINAL_TOOL_IMPLEMENTATIONS = CANONICAL_TOOL_HANDLERS
ALL_TOOL_IMPLEMENTATIONS = CANONICAL_TOOL_HANDLERS

__all__ = [
    "CANONICAL_TOOL_HANDLERS",
    "FINAL_TOOL_IMPLEMENTATIONS",
    "ALL_TOOL_IMPLEMENTATIONS",
    "LEGACY_ALIASES",
    "register_tools",
]
