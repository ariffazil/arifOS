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
    agi_mind as _mega_agi_mind,
    apex_judge as _mega_apex_judge,
    arifOS_kernel as _mega_arifOS_kernel,
    asi_heart as _mega_asi_heart,
    engineering_memory as _mega_engineering_memory,
    init_anchor as _mega_init_anchor,
    math_estimator as _mega_math_estimator,
    physics_reality as _mega_physics_reality,
    vault_ledger as _mega_vault_ledger,
)

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
    payload: dict[str, Any] | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope:
    """Initialize constitutional session OR perform kernel syscall."""
    effective_mode = mode if mode in ("probe", "revoke", "refresh", "state", "status") else "init"
    envelope = await _mega_init_anchor(
        mode=effective_mode,
        payload={"actor_id": actor_id, "intent": intent, "declared_name": declared_name},
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        allow_execution=allow_execution,
        debug=debug,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos_init")

async def arifos_sense(
    query: str | None = None,
    mode: str = "governed",
    session_id: str | None = None,
    dry_run: bool = True,
    platform: str = "unknown",
    payload: dict[str, Any] | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope:
    """Constitutional Identity Sensing --- delegates to physics_reality."""
    envelope = await _mega_physics_reality(
        query=query or "",
        mode=mode,
        session_id=session_id,
        dry_run=dry_run,
        payload=payload,
        **kwargs,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos_sense")

async def arifos_mind(
    query: str | None = None,
    context: dict[str, Any] | None = None,
    session_id: str | None = None,
    dry_run: bool = True,
    platform: str = "unknown",
    **kwargs: Any,
) -> RuntimeEnvelope:
    """Structured reasoning typed cognitive pipeline --- delegates to mega_agi_mind."""
    envelope = await _mega_agi_mind(
        query=query or "",
        context=context or {},
        session_id=session_id,
        dry_run=dry_run,
        **kwargs,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos_mind")

async def arifos_heart(
    query: str | None = None,
    risk_profile: dict[str, Any] | None = None,
    session_id: str | None = None,
    dry_run: bool = True,
    platform: str = "unknown",
    **kwargs: Any,
) -> RuntimeEnvelope:
    """Constitutional Safety Check --- delegates to mega_asi_heart."""
    envelope = await _mega_asi_heart(
        query=query or "",
        risk_profile=risk_profile or {},
        session_id=session_id,
        dry_run=dry_run,
        **kwargs,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos_heart")

async def arifos_judge(
    query: str | None = None,
    evidence_bundle: dict[str, Any] | None = None,
    session_id: str | None = None,
    dry_run: bool = True,
    platform: str = "unknown",
    **kwargs: Any,
) -> RuntimeEnvelope:
    """Final constitutional evaluation --- delegates to mega_apex_judge."""
    envelope = await _mega_apex_judge(
        query=query or "",
        evidence_bundle=evidence_bundle or {},
        session_id=session_id,
        dry_run=dry_run,
        **kwargs,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos_judge")

async def arifos_memory(
    query: str | None = None,
    mode: str = "retrieve",
    session_id: str | None = None,
    platform: str = "unknown",
    **kwargs: Any,
) -> RuntimeEnvelope:
    """Retrieve governed memory --- delegates to mega_engineering_memory."""
    envelope = await _mega_engineering_memory(
        query=query or "",
        mode=mode,
        session_id=session_id,
        **kwargs,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos_memory")

async def arifos_vault(
    query: str | None = None,
    operation: str = "audit",
    session_id: str | None = None,
    platform: str = "unknown",
    **kwargs: Any,
) -> RuntimeEnvelope:
    """Append to immutable constitutional ledger --- delegates to mega_vault_ledger."""
    envelope = await _mega_vault_ledger(
        query=query or "",
        operation=operation,
        session_id=session_id,
        **kwargs,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos_vault")

async def arifos_math(
    query: str | None = None,
    mode: str = "estimate",
    session_id: str | None = None,
    platform: str = "unknown",
    **kwargs: Any,
) -> RuntimeEnvelope:
    """Calculate operation costs and thermodynamics --- delegates to mega_math_estimator."""
    envelope = await _mega_math_estimator(
        query=query or "",
        mode=mode,
        session_id=session_id,
        **kwargs,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos_math")

async def arifos_kernel(
    query: str | None = None,
    mode: str = "status",
    session_id: str | None = None,
    platform: str = "unknown",
    **kwargs: Any,
) -> RuntimeEnvelope:
    """Kernel diagnostics and resource management --- delegates to mega_arifOS_kernel."""
    envelope = await _mega_arifOS_kernel(
        query=query or "",
        mode=mode,
        session_id=session_id,
        **kwargs,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos_kernel")

# ===============================================================================
# REGISTRATION & EXPORTS
# ===============================================================================

def register_tools(mcp: FastMCP) -> None:
    """Register all metabolic tools on the MCP instance."""
    mcp.tool()(arifos_init)
    mcp.tool()(arifos_sense)
    mcp.tool()(arifos_mind)
    mcp.tool()(arifos_heart)
    mcp.tool()(arifos_judge)
    mcp.tool()(arifos_memory)
    mcp.tool()(arifos_vault)
    mcp.tool()(arifos_math)
    mcp.tool()(arifos_kernel)
    logger.info("Metabolic tools registered on MCP surface.")

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
    "register_tools",
]
