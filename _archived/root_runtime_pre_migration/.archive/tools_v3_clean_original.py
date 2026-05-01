"""
arifosmcp/runtime/tools_v3_clean.py — Clean 3-Tier Interface
═══════════════════════════════════════════════════════════════════════════════

Implements the operator-clarity input/output model.

Key changes from v2:
- Input: Small, explicit (actor, intent, risk, session, options)
- Output: Fixed blocks (execution, governance, operator, context, error, debug)
- Three views: Operator (default), System (verbose), Forensic (debug)

Usage:
    from arifosmcp.runtime.tools_v3_clean import arifos_init_clean
    
    result = await arifos_init_clean(
        actor="arif",
        intent="Start new session",
        risk="low",
        session="arif-session-001",
        options={"verbose": False}
    )
    
    # result is now a clean dict, not RuntimeEnvelope
    print(result["execution"]["ok"])  # True/False
    print(result["operator"]["summary"])  # Plain language summary
"""

from __future__ import annotations

from typing import Any

from arifosmcp.runtime.continuity_contract import seal_runtime_envelope
from arifosmcp.runtime.megaTools import (
    agi_mind as _mega_agi_mind,
)
from arifosmcp.runtime.megaTools import (
    apex_judge as _mega_apex_judge,
)
from arifosmcp.runtime.megaTools import (
    arifOS_kernel as _mega_arifOS_kernel,
)
from arifosmcp.runtime.megaTools import (
    asi_heart as _mega_asi_heart,
)
from arifosmcp.runtime.megaTools import (
    engineering_memory as _mega_engineering_memory,
)
from arifosmcp.runtime.megaTools import (
    init_anchor as _mega_init_anchor,
)
from arifosmcp.runtime.megaTools import (
    math_estimator as _mega_math_estimator,
)
from arifosmcp.runtime.megaTools import (
    physics_reality as _mega_physics_reality,
)
from arifosmcp.runtime.megaTools import (
    vault_ledger as _mega_vault_ledger,
)
from arifosmcp.runtime.schemas_v2_clean import CleanInput, QueryOptions

# ═══════════════════════════════════════════════════════════════════════════════
# CLEAN INPUT WRAPPER
# ═══════════════════════════════════════════════════════════════════════════════

def _build_options(options: dict[str, Any] | None) -> QueryOptions:
    """Build QueryOptions from dict."""
    if options is None:
        return QueryOptions()
    return QueryOptions(
        verbose=options.get("verbose", False),
        debug=options.get("debug", False),
        include=options.get("include", []),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CLEAN TOOL IMPLEMENTATIONS
# ═══════════════════════════════════════════════════════════════════════════════

async def arifos_init_clean(
    actor: str = "anonymous",
    intent: str = "",
    risk: str = "low",
    session: str | None = None,
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Clean interface for arifos.init.
    
    Input:
        actor: Who is initiating (replaces actor_id + declared_name)
        intent: What they want to accomplish
        risk: low | medium | high | critical (replaces risk_tier)
        session: Session identifier (replaces session_id)
        options: {verbose: bool, debug: bool}
    
    Output:
        Clean dict with fixed blocks: execution, governance, operator, context, error
    """
    query_opts = _build_options(options)
    
    envelope = await _mega_init_anchor(
        mode="init",
        payload={
            "actor_id": actor,
            "intent": intent,
            "declared_name": actor,  # Collapsed
        },
        session_id=session,
        risk_tier=risk,  # Renamed internally
        dry_run=True,
        debug=query_opts.debug,
    )
    
    # Return clean formatted output
    return seal_runtime_envelope(
        envelope=envelope,
        tool_id="arifos.init",
        output_options={"verbose": query_opts.verbose, "debug": query_opts.debug},
    )


async def arifos_sense_clean(
    query: str,
    mode: str = "search",
    risk: str = "low",
    session: str | None = None,
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Clean interface for arifos.sense.
    
    Input:
        query: What to ground in reality
        mode: search | ingest | compass | atlas | time
        risk: low | medium | high | critical
        session: Session identifier
        options: {verbose: bool, debug: bool}
    """
    query_opts = _build_options(options)
    
    envelope = await _mega_physics_reality(
        mode=mode,
        payload={"query": query},
        session_id=session,
        risk_tier=risk,
        dry_run=True,
        debug=query_opts.debug,
    )
    
    return seal_runtime_envelope(
        envelope=envelope,
        tool_id="arifos.sense",
        output_options={"verbose": query_opts.verbose, "debug": query_opts.debug},
    )


async def arifos_mind_clean(
    query: str,
    context: str | None = None,
    mode: str = "reason",
    risk: str = "low",
    session: str | None = None,
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Clean interface for arifos.mind.
    
    Input:
        query: Task or question to reason about
        context: Additional context (optional)
        mode: reason | reflect | forge
        risk: low | medium | high | critical
        session: Session identifier
        options: {verbose: bool, debug: bool}
    """
    query_opts = _build_options(options)
    
    envelope = await _mega_agi_mind(
        mode=mode,
        payload={"query": query, "context": context},
        session_id=session,
        risk_tier=risk,
        dry_run=True,
        debug=query_opts.debug,
    )
    
    return seal_runtime_envelope(
        envelope=envelope,
        tool_id="arifos.mind",
        output_options={"verbose": query_opts.verbose, "debug": query_opts.debug},
    )


async def arifos_heart_clean(
    content: str,
    mode: str = "critique",
    risk: str = "low",
    session: str | None = None,
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Clean interface for arifos.heart.
    
    Input:
        content: Content or proposal to critique
        mode: critique | simulate
        risk: low | medium | high | critical
        session: Session identifier
        options: {verbose: bool, debug: bool}
    """
    query_opts = _build_options(options)
    
    envelope = await _mega_asi_heart(
        mode=mode,
        payload={"content": content},
        session_id=session,
        risk_tier=risk,
        dry_run=True,
        debug=query_opts.debug,
    )
    
    return seal_runtime_envelope(
        envelope=envelope,
        tool_id="arifos.heart",
        output_options={"verbose": query_opts.verbose, "debug": query_opts.debug},
    )


async def arifos_judge_clean(
    candidate_action: str,
    risk: str = "medium",
    telemetry: dict[str, Any] | None = None,
    session: str | None = None,
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Clean interface for arifos.judge.
    
    Input:
        candidate_action: Action to judge
        risk: low | medium | high | critical
        telemetry: Optional telemetry data
        session: Session identifier
        options: {verbose: bool, debug: bool}
    """
    query_opts = _build_options(options)
    
    envelope = await _mega_apex_judge(
        mode="judge",
        payload={
            "candidate": candidate_action,
            "risk_tier": risk,
            "telemetry": telemetry,
        },
        session_id=session,
        risk_tier=risk,
        dry_run=True,
        debug=query_opts.debug,
    )
    
    return seal_runtime_envelope(
        envelope=envelope,
        tool_id="arifos.judge",
        output_options={"verbose": query_opts.verbose, "debug": query_opts.debug},
    )


async def arifos_route_clean(
    request: str,
    mode: str = "kernel",
    risk: str = "medium",
    session: str | None = None,
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Clean interface for arifos.route.
    
    Input:
        request: Request to route
        mode: kernel | status
        risk: low | medium | high | critical
        session: Session identifier
        options: {verbose: bool, debug: bool}
    """
    query_opts = _build_options(options)
    
    envelope = await _mega_arifOS_kernel(
        mode=mode,
        payload={"query": request},
        session_id=session,
        risk_tier=risk,
        dry_run=True,
        debug=query_opts.debug,
    )
    
    return seal_runtime_envelope(
        envelope=envelope,
        tool_id="arifos.route",
        output_options={"verbose": query_opts.verbose, "debug": query_opts.debug},
    )


async def arifos_ops_clean(
    action: str,
    mode: str = "cost",
    risk: str = "medium",
    session: str | None = None,
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Clean interface for arifos.ops.
    
    Input:
        action: Action to estimate costs for
        mode: cost | health | vitals | entropy
        risk: low | medium | high | critical
        session: Session identifier
        options: {verbose: bool, debug: bool}
    """
    query_opts = _build_options(options)
    
    envelope = await _mega_math_estimator(
        mode=mode,
        payload={"action": action},
        session_id=session,
        risk_tier=risk,
        dry_run=True,
        debug=query_opts.debug,
    )
    
    return seal_runtime_envelope(
        envelope=envelope,
        tool_id="arifos.ops",
        output_options={"verbose": query_opts.verbose, "debug": query_opts.debug},
    )


async def arifos_memory_clean(
    query: str,
    mode: str = "vector_query",
    risk: str = "medium",
    session: str | None = None,
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Clean interface for arifos.memory.
    
    Input:
        query: Memory query
        mode: vector_query | vector_store | engineer | query
        risk: low | medium | high | critical
        session: Session identifier
        options: {verbose: bool, debug: bool}
    """
    query_opts = _build_options(options)
    
    envelope = await _mega_engineering_memory(
        mode=mode,
        payload={"query": query},
        session_id=session,
        risk_tier=risk,
        dry_run=True,
        debug=query_opts.debug,
    )
    
    return seal_runtime_envelope(
        envelope=envelope,
        tool_id="arifos.memory",
        output_options={"verbose": query_opts.verbose, "debug": query_opts.debug},
    )


async def arifos_vault_clean(
    verdict: str,
    evidence: str | None = None,
    risk: str = "medium",
    session: str | None = None,
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Clean interface for arifos.vault.
    
    Input:
        verdict: SEAL | PARTIAL | VOID | HOLD
        evidence: Evidence summary
        risk: low | medium | high | critical
        session: Session identifier
        options: {verbose: bool, debug: bool}
    """
    query_opts = _build_options(options)
    
    envelope = await _mega_vault_ledger(
        mode="seal",
        payload={"verdict": verdict, "evidence": evidence},
        session_id=session,
        risk_tier=risk,
        dry_run=True,
        debug=query_opts.debug,
    )
    
    return seal_runtime_envelope(
        envelope=envelope,
        tool_id="arifos.vault",
        output_options={"verbose": query_opts.verbose, "debug": query_opts.debug},
    )


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    "arifos_init_clean",
    "arifos_sense_clean",
    "arifos_mind_clean",
    "arifos_heart_clean",
    "arifos_judge_clean",
    "arifos_route_clean",
    "arifos_ops_clean",
    "arifos_memory_clean",
    "arifos_vault_clean",
    "QueryOptions",
    "CleanInput",
]
