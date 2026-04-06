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
    actor_id: str,
    intent: str,
    declared_name: str | None = None,
    session_id: str | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope:
    """Start a governed session and bind the initial telemetry seed."""
    envelope = await _mega_init_anchor(
        mode="init",
        payload={"actor_id": actor_id, "intent": intent, "declared_name": declared_name},
        session_id=session_id,
        **kwargs,
    )
    return seal_runtime_envelope(envelope, "init_session_anchor")


async def get_tool_registry(
    mode: str = "list",
    uri: str | None = None,
    session_id: str | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope:
    """Discover arifOS tool graph, modes, and model capabilities."""
    envelope = await _mega_architect_registry(
        mode=mode,
        payload={"uri": uri},
        session_id=session_id,
        **kwargs,
    )
    return seal_runtime_envelope(envelope, "get_tool_registry")


async def sense_reality(
    query: str,
    operation: str = "search",
    session_id: str | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope:
    """Time grounding, evidence checks, and reality state verification."""
    envelope = await _mega_physics_reality(
        mode=operation,
        payload={"query": query},
        session_id=session_id,
        **kwargs,
    )
    return seal_runtime_envelope(envelope, "sense_reality")


async def reason_synthesis(
    query: str,
    context: str | None = None,
    mode: str = "reason",
    session_id: str | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope:
    """Multi-source synthesis and structured first-principles reasoning."""
    envelope = await _mega_agi_mind(
        mode=mode,
        payload={"query": query, "context": context},
        session_id=session_id,
        **kwargs,
    )
    return seal_runtime_envelope(envelope, "reason_synthesis")


async def critique_safety(
    content: str,
    mode: str = "critique",
    session_id: str | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope:
    """Safety, dignity, and adversarial critique of content or proposals."""
    envelope = await _mega_asi_heart(
        mode=mode,
        payload={"content": content},
        session_id=session_id,
        **kwargs,
    )
    return seal_runtime_envelope(envelope, "critique_safety")


async def route_execution(
    query: str,
    session_id: str | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope:
    """Route request to the correct metabolic lane or tool family."""
    envelope = await _mega_arifOS_kernel(
        mode="kernel",
        payload={"query": query},
        session_id=session_id,
        **kwargs,
    )
    return seal_runtime_envelope(envelope, "route_execution")


async def load_memory_context(
    query: str,
    mode: str = "vector_query",
    session_id: str | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope:
    """Retrieve governed memory and engineering context from vector store."""
    envelope = await _mega_engineering_memory(
        mode=mode,
        payload={"query": query},
        session_id=session_id,
        **kwargs,
    )
    return seal_runtime_envelope(envelope, "load_memory_context")


async def estimate_ops(
    action_description: str,
    mode: str = "cost",
    session_id: str | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope:
    """Calculate operation costs, thermodynamics, capacity, and timing."""
    envelope = await _mega_math_estimator(
        mode=mode,
        payload={"action": action_description},
        session_id=session_id,
        **kwargs,
    )
    return seal_runtime_envelope(envelope, "estimate_ops")


async def judge_verdict(
    candidate_action: str,
    risk_tier: RiskTier = RiskTier.MEDIUM,
    telemetry: dict[str, Any] | None = None,
    session_id: str | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope:
    """Final constitutional verdict evaluation and hold logic enforcement."""
    envelope = await _mega_apex_judge(
        mode="judge",
        payload={
            "candidate": candidate_action,
            "risk_tier": risk_tier,
            "telemetry": telemetry,
        },
        session_id=session_id,
        **kwargs,
    )
    return seal_runtime_envelope(envelope, "judge_verdict")


async def record_vault_entry(
    verdict: str,
    evidence: str,
    session_id: str | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope:
    """Append immutable verdict record to the Merkle-hashed ledger."""
    envelope = await _mega_vault_ledger(
        mode="seal",
        payload={"verdict": verdict, "evidence": evidence},
        session_id=session_id,
        **kwargs,
    )
    return seal_runtime_envelope(envelope, "record_vault_entry")


async def execute_vps_task(
    command: str,
    session_id: str | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope:
    """Redirect or dispatch execution tasks to the sovereign VPS executor."""
    envelope = await _mega_code_engine(
        mode="fs", # Default to fs for safety if no mode provided
        payload={"command": command},
        session_id=session_id,
        **kwargs,
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

from arifosmcp.runtime.chatgpt_integration.apps_sdk_tools import render_vault_seal

FINAL_TOOL_IMPLEMENTATIONS = {
    "init_session_anchor": init_session_anchor,
    "get_tool_registry": get_tool_registry,
    "sense_reality": sense_reality,
    "reason_synthesis": reason_synthesis,
    "critique_safety": critique_safety,
    "route_execution": route_execution,
    "load_memory_context": load_memory_context,
    "estimate_ops": estimate_ops,
    "judge_verdict": judge_verdict,
    "record_vault_entry": record_vault_entry,
    "execute_vps_task": execute_vps_task,
    # ChatGPT subset
    "get_constitutional_health": get_constitutional_health,
    "render_vault_seal": render_vault_seal,
    "list_recent_verdicts": list_recent_verdicts,
}

# Legacy names kept for internal routing and backward compat
LEGACY_COMPAT_MAP = {
    "init_anchor": init_session_anchor,
    "arifOS_kernel": route_execution,
    "apex_soul": judge_verdict,
    "apex_judge": judge_verdict,
    "vault_ledger": record_vault_entry,
    "agi_mind": reason_synthesis,
    "asi_heart": critique_safety,
    "engineering_memory": load_memory_context,
    "physics_reality": sense_reality,
    "math_estimator": estimate_ops,
    "code_engine": execute_vps_task,
    "architect_registry": get_tool_registry,
}

ALL_TOOL_IMPLEMENTATIONS = {**FINAL_TOOL_IMPLEMENTATIONS, **LEGACY_COMPAT_MAP}


def register_tools(mcp: FastMCP) -> None:
    """Wire the functional arifOS tools onto *mcp*."""
    import inspect
    from fastmcp.tools.function_tool import FunctionTool
    from arifosmcp.runtime.tool_specs import PUBLIC_TOOL_SPECS, CHATGPT_APP_TOOL_NAMES

    # 1. Register Functional Mega-Tools
    for spec in PUBLIC_TOOL_SPECS:
        handler = FINAL_TOOL_IMPLEMENTATIONS.get(spec.name)
        if not handler:
            continue
            
        ft = FunctionTool.from_function(
            handler,
            name=spec.name,
            description=spec.description,
        )
        # Use schema from spec
        ft.parameters = dict(spec.input_schema)
        mcp.add_tool(ft)
        
    # 2. Register ChatGPT App specific tools
    for name in CHATGPT_APP_TOOL_NAMES:
        handler = FINAL_TOOL_IMPLEMENTATIONS.get(name)
        if not handler:
            continue
        mcp.add_tool(handler)

    logger.info(f"Registered {len(mcp._mcp_server.list_tools())} tools (functional surface)")


__all__ = [
    "FINAL_TOOL_IMPLEMENTATIONS",
    "LEGACY_COMPAT_MAP",
    "ALL_TOOL_IMPLEMENTATIONS",
    "register_tools",
]
