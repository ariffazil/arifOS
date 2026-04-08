"""
arifosmcp/runtime/tools.py --- arifOS MCP Sovereign Core --- 11 Canonical Tools

11 canonical tools, clean implementation, MCP-standard compliant.
Supports the Metabolic Surface (init, sense, mind, heart, judge, memory, vault, math, kernel, code, architect).

DITEMPA BUKAN DIBERI --- Forged, Not Given
"""

from __future__ import annotations

import logging
from typing import Any

from arifosmcp.runtime.continuity_contract import seal_runtime_envelope
from arifosmcp.capability_map import CANONICAL_TOOL_HANDLERS

# RuntimeEnvelope is a dict type for tool outputs
RuntimeEnvelope = dict[str, Any]

from fastmcp import FastMCP

from arifosmcp.runtime.megaTools import (
    agi_mind as agi_mind,
    apex_judge as apex_judge,
    arifOS_kernel as arifOS_kernel,
    asi_heart as asi_heart,
    engineering_memory as engineering_memory,
    init_anchor as init_anchor,
    math_estimator as math_estimator,
    physics_reality as physics_reality,
    vault_ledger as vault_ledger,
    code_engine as code_engine,
    architect_registry as architect_registry,
)

# Legacy aliases for direct import (v2 compatibility)
init_anchor = init_anchor
physics_reality = physics_reality
agi_mind = agi_mind
asi_heart = asi_heart
apex_judge = apex_judge
engineering_memory = engineering_memory
vault_ledger = vault_ledger
math_estimator = math_estimator
arifOS_kernel = arifOS_kernel

logger = logging.getLogger(__name__)


# ===============================================================================
# INTERNAL HELPERS
# ===============================================================================


def _make_f12_block_envelope(
    injection_score: float, threats: list[str], session_id: str | None
) -> Any:
    """Return a VOID RuntimeEnvelope blocking an F12 injection attempt."""
    from arifosmcp.runtime.models import RuntimeEnvelope as _RE
    from arifosmcp.runtime.models import RuntimeStatus, Verdict

    return _RE(
        ok=False,
        tool="arifos_init",
        canonical_tool_name="arifos_init",
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


def _stamp_platform(envelope: Any, platform: str) -> None:
    """Stamp platform_context onto envelope in-place (F1-safe: no-op if field absent)."""
    if hasattr(envelope, "platform_context"):
        envelope.platform_context = platform
    if hasattr(envelope, "policy") and isinstance(envelope.policy, dict):
        envelope.policy["platform_context"] = platform
    elif hasattr(envelope, "policy") and envelope.policy is None:
        envelope.policy = {"platform_context": platform}


# ===============================================================================
# V2 TOOL IMPLEMENTATIONS (METABOLIC)
# ===============================================================================


async def arifos_init(
    actor_id: str | None = None,
    intent: str | None = None,
    declared_name: str | None = None,
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    allow_execution: bool = False,
    debug: bool = False,
    platform: str = "unknown",
    mode: str = "init",
) -> RuntimeEnvelope:
    """Initialize constitutional session OR perform kernel syscall."""
    effective_mode = mode if mode in ("probe", "revoke", "refresh", "state", "status") else "init"
    envelope = await init_anchor(
        mode=effective_mode,
        payload={"actor_id": actor_id, "intent": intent, "declared_name": declared_name},
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        allow_execution=allow_execution,
        debug=debug,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos_init", session_id=session_id)


async def arifos_sense(
    query: str | None = None,
    mode: str = "governed",
    session_id: str | None = None,
    dry_run: bool = True,
    platform: str = "unknown",
) -> RuntimeEnvelope:
    """Constitutional Identity Sensing --- delegates to physics_reality."""
    envelope = await physics_reality(
        query=query or "",
        mode=mode,
        session_id=session_id,
        dry_run=dry_run,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos_sense", session_id=session_id)


async def arifos_mind(
    query: str | None = None,
    context: dict[str, Any] | None = None,
    session_id: str | None = None,
    dry_run: bool = True,
    platform: str = "unknown",
) -> RuntimeEnvelope:
    """Structured reasoning typed cognitive pipeline --- delegates to agi_mind."""
    envelope = await agi_mind(
        query=query or "",
        context=context or {},
        session_id=session_id,
        dry_run=dry_run,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos_mind", session_id=session_id)


async def arifos_heart(
    query: str | None = None,
    risk_profile: dict[str, Any] | None = None,
    session_id: str | None = None,
    dry_run: bool = True,
    platform: str = "unknown",
) -> RuntimeEnvelope:
    """Constitutional Safety Check --- delegates to asi_heart."""
    envelope = await asi_heart(
        query=query or "",
        risk_profile=risk_profile or {},
        session_id=session_id,
        dry_run=dry_run,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos_heart", session_id=session_id)


async def arifos_judge(
    query: str | None = None,
    evidence_bundle: dict[str, Any] | None = None,
    session_id: str | None = None,
    dry_run: bool = True,
    platform: str = "unknown",
) -> RuntimeEnvelope:
    """Final constitutional evaluation --- delegates to apex_judge."""
    envelope = await apex_judge(
        query=query or "",
        evidence_bundle=evidence_bundle or {},
        session_id=session_id,
        dry_run=dry_run,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos_judge", session_id=session_id)


async def arifos_memory(
    query: str | None = None,
    mode: str = "retrieve",
    session_id: str | None = None,
    platform: str = "unknown",
) -> RuntimeEnvelope:
    """Retrieve governed memory --- delegates to engineering_memory."""
    envelope = await engineering_memory(
        query=query or "",
        mode=mode,
        session_id=session_id,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos_memory", session_id=session_id)


async def arifos_vault(
    query: str | None = None,
    operation: str = "audit",
    session_id: str | None = None,
    platform: str = "unknown",
) -> RuntimeEnvelope:
    """Append to immutable constitutional ledger --- delegates to vault_ledger."""
    envelope = await vault_ledger(
        query=query or "",
        operation=operation,
        session_id=session_id,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos_vault", session_id=session_id)


async def arifos_math(
    query: str | None = None,
    mode: str = "estimate",
    session_id: str | None = None,
    platform: str = "unknown",
) -> RuntimeEnvelope:
    """Calculate operation costs and thermodynamics --- delegates to math_estimator."""
    envelope = await math_estimator(
        query=query or "",
        mode=mode,
        session_id=session_id,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos_math", session_id=session_id)


async def arifos_kernel(
    query: str | None = None,
    mode: str = "status",
    session_id: str | None = None,
    platform: str = "unknown",
) -> RuntimeEnvelope:
    """Kernel diagnostics and resource management --- delegates to arifOS_kernel."""
    envelope = await arifOS_kernel(
        query=query or "",
        mode=mode,
        session_id=session_id,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos_kernel", session_id=session_id)


async def arifos_code(
    query: str | None = None,
    session_id: str | None = None,
    platform: str = "unknown",
) -> RuntimeEnvelope:
    """Code generation and analysis --- delegates to code_engine."""
    envelope = await code_engine(
        query=query or "",
        session_id=session_id,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos_code", session_id=session_id)


async def arifos_architect(
    query: str | None = None,
    session_id: str | None = None,
    platform: str = "unknown",
) -> RuntimeEnvelope:
    """Sovereign architectural design --- delegates to architect_registry."""
    envelope = await architect_registry(
        query=query or "",
        session_id=session_id,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos_architect", session_id=session_id)


# ===============================================================================
# REGISTRATION & EXPORTS
# ===============================================================================


def register_tools(mcp: FastMCP) -> list[str]:
    """Register all metabolic tools on the MCP instance and return tool names."""
    tools = [
        arifos_init,
        arifos_sense,
        arifos_mind,
        arifos_heart,
        arifos_judge,
        arifos_memory,
        arifos_vault,
        arifos_math,
        arifos_kernel,
        arifos_code,
        arifos_architect,
    ]
    for t in tools:
        mcp.tool()(t)
    logger.info("Metabolic tools registered on MCP surface.")
    return [t.__name__ for t in tools]


# Legacy Compatibility Aliases (Standardized to Metabolic Surface)
arifos_route = arifos_kernel
arifos_ops = arifos_math
arifos_forge = arifos_vault
arifos_vps_monitor = arifos_kernel

register_v2_tools = register_tools
register_v3_tools = register_tools

__all__ = [
    "arifos_init",
    "arifos_sense",
    "arifos_mind",
    "arifos_heart",
    "arifos_judge",
    "arifos_memory",
    "arifos_vault",
    "arifos_math",
    "arifos_kernel",
    "arifos_code",
    "arifos_architect",
    "arifos_route",
    "arifos_ops",
    "arifos_forge",
    "arifos_vps_monitor",
    "init_anchor",
    "physics_reality",
    "agi_mind",
    "asi_heart",
    "apex_judge",
    "engineering_memory",
    "vault_ledger",
    "math_estimator",
    "arifOS_kernel",
    "code_engine",
    "architect_registry",
    "register_tools",
    "register_v2_tools",
    "register_v3_tools",
    "CANONICAL_TOOL_HANDLERS",
]
