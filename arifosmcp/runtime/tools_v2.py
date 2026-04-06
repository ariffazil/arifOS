"""
arifosmcp/runtime/tools_v2.py — arifOS MCP v2 Sovereign Core Implementation

10 canonical tools, clean implementation, MCP-standard compliant.

The 10th Tool (arifos.forge) is the Delegated Execution Bridge:
  • Requires judge verdict = SEAL
  • Issues signed execution manifest
  • Dispatches to AF-FORGE substrate
  • Preserves separation of powers

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from typing import Any

from arifosmcp.runtime.continuity_contract import seal_runtime_envelope
from arifosmcp.runtime.contracts import (
    RiskTier,
    VerdictCode,
)

# RuntimeEnvelope is a dict type for tool outputs
RuntimeEnvelope = dict[str, Any]
# Philosophy injection removed from tools - happens centrally in _wrap_call()
# to ensure ONLY G★ determines band, never tool identity
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
from fastmcp import FastMCP

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# INTERNAL HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _make_f12_block_envelope(injection_score: float, threats: list[str], session_id: str | None) -> Any:
    """Return a VOID RuntimeEnvelope blocking an F12 injection attempt."""
    from arifosmcp.runtime.models import RuntimeEnvelope as _RE, RuntimeStatus, Verdict
    return _RE(
        ok=False,
        tool="arifos.init",
        canonical_tool_name="arifos.init",
        stage="000_INIT",
        status=RuntimeStatus.ERROR,
        verdict=Verdict.VOID,
        code="F12_INJECTION_BLOCKED",
        detail=f"Prompt injection detected (score={injection_score:.2f}). Request rejected by F12.",
        hint="Remove manipulation patterns from intent and retry with a legitimate request.",
        retryable=False,
        rollback_available=False,
        anchor_state="denied",
        session_id=session_id,
        policy={
            "floors_checked": ["F12"],
            "floors_failed": ["F12"],
            "injection_score": round(injection_score, 4),
            "threats": threats,
            "witness_required": True,
        },
    )


# ═══════════════════════════════════════════════════════════════════════════════
# V2 TOOL IMPLEMENTATIONS
# ═══════════════════════════════════════════════════════════════════════════════

async def arifos_init(
    actor_id: str,
    intent: str,
    declared_name: str | None = None,
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    allow_execution: bool = False,
    debug: bool = False,
) -> RuntimeEnvelope:
    """Initialize constitutional session."""
    # ── F12: Injection Guard ──────────────────────────────────────────────
    from arifosmcp.runtime.webmcp.security import WebInjectionGuard
    _guard = WebInjectionGuard()
    _injection_score, _threats = _guard._scan_text(intent)
    if _injection_score >= 0.85:
        logger.warning(
            "F12 BLOCK: injection detected in arifos.init intent (score=%.2f, threats=%s)",
            _injection_score, _threats,
        )
        return seal_runtime_envelope(
            _make_f12_block_envelope(_injection_score, _threats, session_id),
            "arifos.init",
        )

    envelope = await _mega_init_anchor(
        mode="init",
        payload={"actor_id": actor_id, "intent": intent, "declared_name": declared_name},
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        allow_execution=allow_execution,
        debug=debug,
    )
    # Stamp F12 result into policy so floors_checked is never empty
    if hasattr(envelope, "policy") and isinstance(envelope.policy, dict):
        envelope.policy["floors_checked"] = list(dict.fromkeys(
            ["F12"] + envelope.policy.get("floors_checked", [])
        ))
        envelope.policy["injection_score"] = round(_injection_score, 4)
    elif hasattr(envelope, "policy"):
        envelope.policy = {"floors_checked": ["F12"], "injection_score": round(_injection_score, 4)}
    return seal_runtime_envelope(envelope, "arifos.init")


async def arifos_sense(
    query: str,
    mode: str = "search",
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    debug: bool = False,
) -> RuntimeEnvelope:
    """Ground query in physical reality."""
    envelope = await _mega_physics_reality(
        mode=mode,
        payload={"query": query},
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        debug=debug,
    )
    return seal_runtime_envelope(envelope, "arifos.sense")


async def arifos_mind(
    query: str,
    context: str | None = None,
    mode: str = "reason",
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    debug: bool = False,
) -> RuntimeEnvelope:
    """Structured reasoning with typed cognitive pipeline.

    Runs the constitutional AGI pipeline (sense → mind → heart → judge)
    producing a narrow decision_packet for the operator and a full
    audit_packet for the vault.  Internal richness, external compression.
    """
    from arifosmcp.runtime.arifos_runtime_envelope import run_agi_mind

    # ── Typed pipeline: sense → mind → heart → judge ─────────────────────
    decision_packet, audit_packet = await run_agi_mind(
        raw_input=query,
        session_id=session_id,
        additional_context=context or "",
    )

    # ── Forward enriched payload through mega tool ────────────────────────
    envelope = await _mega_agi_mind(
        mode=mode,
        payload={
            "query": query,
            "context": context,
            "decision_packet": decision_packet,
        },
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        debug=debug,
    )

    # ── Seal and inject typed packets into intelligence_state ─────────────
    sealed = seal_runtime_envelope(envelope, "arifos.mind")
    if isinstance(sealed, dict):
        intel = sealed.setdefault("intelligence_state", {})
        intel["decision_packet"] = decision_packet
        intel["audit_packet"] = audit_packet
        intel["chaos_score"] = audit_packet.get(
            "constitutional_checks", {}
        ).get("chaos_score", 0.0)
        intel["pipeline_trace"] = audit_packet.get("pipeline_trace", [])
    return sealed


async def arifos_route(
    request: str,
    mode: str = "kernel",
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    allow_execution: bool = False,
    debug: bool = False,
) -> RuntimeEnvelope:
    """Route request to correct metabolic lane."""
    envelope = await _mega_arifOS_kernel(
        mode=mode,
        payload={"query": request},
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        allow_execution=allow_execution,
        debug=debug,
    )
    return seal_runtime_envelope(envelope, "arifos.route")


async def arifos_heart(
    content: str,
    mode: str = "critique",
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    debug: bool = False,
) -> RuntimeEnvelope:
    """Safety, dignity, and adversarial critique."""
    envelope = await _mega_asi_heart(
        mode=mode,
        payload={"content": content},
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        debug=debug,
    )
    return seal_runtime_envelope(envelope, "arifos.heart")


async def arifos_ops(
    action: str,
    mode: str = "cost",
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    debug: bool = False,
) -> RuntimeEnvelope:
    """Calculate operation costs and thermodynamics."""
    envelope = await _mega_math_estimator(
        mode=mode,
        payload={"action": action},
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        debug=debug,
    )
    return seal_runtime_envelope(envelope, "arifos.ops")


async def arifos_judge(
    candidate_action: str,
    risk_tier: str = "medium",
    telemetry: dict[str, Any] | None = None,
    session_id: str | None = None,
    dry_run: bool = True,
    debug: bool = False,
) -> RuntimeEnvelope:
    """Final constitutional verdict evaluation."""
    envelope = await _mega_apex_judge(
        mode="judge",
        payload={
            "candidate": candidate_action,
            "risk_tier": risk_tier,
            "telemetry": telemetry,
        },
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        debug=debug,
    )
    return seal_runtime_envelope(envelope, "arifos.judge")


async def arifos_memory(
    query: str,
    mode: str = "vector_query",
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    debug: bool = False,
) -> RuntimeEnvelope:
    """Retrieve governed memory from vector store."""
    envelope = await _mega_engineering_memory(
        mode=mode,
        payload={"query": query},
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        debug=debug,
    )
    return seal_runtime_envelope(envelope, "arifos.memory")


async def arifos_vault(
    verdict: str,
    evidence: str | None = None,
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    debug: bool = False,
) -> RuntimeEnvelope:
    """Append immutable verdict to ledger."""
    envelope = await _mega_vault_ledger(
        mode="seal",
        payload={"verdict": verdict, "evidence": evidence},
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        debug=debug,
    )
    return seal_runtime_envelope(envelope, "arifos.vault")


# ═══════════════════════════════════════════════════════════════════════════════
# V2 TOOL HANDLER REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

# Import the 10th tool (Delegated Execution Bridge)
from arifosmcp.runtime.tools_v2_forge import arifos_forge

V2_TOOL_HANDLERS: dict[str, Any] = {
    "arifos.init": arifos_init,
    "arifos.sense": arifos_sense,
    "arifos.mind": arifos_mind,
    "arifos.route": arifos_route,
    "arifos.heart": arifos_heart,
    "arifos.ops": arifos_ops,
    "arifos.judge": arifos_judge,
    "arifos.memory": arifos_memory,
    "arifos.vault": arifos_vault,
    "arifos.forge": arifos_forge,  # The 10th Tool — Delegated Execution
}


def register_v2_tools(mcp: FastMCP) -> list[str]:
    """Register all v2 tools on the MCP instance."""
    from fastmcp.tools.function_tool import FunctionTool
    from arifosmcp.runtime.tool_specs_v2 import V2_TOOLS

    registered = []
    for spec in V2_TOOLS:
        handler = V2_TOOL_HANDLERS.get(spec.name)
        if not handler:
            logger.warning(f"No handler for v2 tool: {spec.name}")
            continue
        
        ft = FunctionTool.from_function(
            handler,
            name=spec.name,
            description=spec.description,
        )
        ft.parameters = dict(spec.input_schema)
        mcp.add_tool(ft)
        registered.append(spec.name)

    logger.info(f"Registered {len(registered)} v2 tools: {registered}")
    return registered


__all__ = [
    "V2_TOOL_HANDLERS",
    "register_v2_tools",
    "arifos_init",
    "arifos_sense",
    "arifos_mind",
    "arifos_route",
    "arifos_heart",
    "arifos_ops",
    "arifos_judge",
    "arifos_memory",
    "arifos_vault",
]
