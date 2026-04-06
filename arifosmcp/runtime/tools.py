"""
arifosmcp/runtime/tools.py — arifOS MCP Tool Surface

THIN DISPATCHER: This module re-exports mega-tools from megaTools/ package.
Each mega-tool is now in its own file for independent auditing and testing.

11 Mega-Tools:
  01_init_anchor       → 000_INIT   (PSI Ψ)
  02_arifOS_kernel     → 444_ROUTER (DELTA/PSI)
  03_apex_judge         → 888_JUDGE  (PSI Ψ)
  04_vault_ledger      → 999_VAULT  (PSI Ψ)
  05_agi_mind          → 333_MIND   (DELTA Δ)
  06_asi_heart         → 666_HEART  (OMEGA Ω)
  07_engineering_memory→ 555_MEMORY (OMEGA Ω)
  08_physics_reality   → 111_SENSE  (DELTA Δ)
  09_math_estimator    → 444_ROUTER (DELTA Δ)
  10_code_engine       → M-3_EXEC   (ALL)
  11_architect_registry→ M-4_ARCH   (DELTA Δ)

Split: 2026-03-28 — tools.py (2153 lines) → megaTools/ (11 × ~100 lines each)
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from arifosmcp.runtime.governance_identities import (
    validate_sovereign_proof,
)
from arifosmcp.runtime.continuity_contract import seal_runtime_envelope
from arifosmcp.runtime.models import (
    CallerContext,
    PersonaId,
    RuntimeEnvelope,
    UserModel,
    UserModelField,
    UserModelSource,
)
from arifosmcp.runtime.public_registry import (
    public_tool_names as _registry_tool_names,
)
from arifosmcp.runtime.public_registry import (
    public_tool_spec_by_name as _registry_tool_spec_by_name,
)
from arifosmcp.runtime.public_registry import (
    public_tool_specs as _registry_tool_specs,
)
from arifosmcp.runtime.schemas import IntentType
from arifosmcp.runtime.tools_internal import (
    apex_judge_dispatch_impl,
    arifos_kernel_impl,
)
from fastmcp import FastMCP
from fastmcp.server.context import Context

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# RE-EXPORT MEGA-TOOLS FROM megaTools/ PACKAGE
# ═══════════════════════════════════════════════════════════════════════════════

try:
    from arifosmcp.memory.shared_memory_mcp import shared_memory_tool
except ImportError:
    shared_memory_tool = None  # type: ignore[assignment]
from arifosmcp.runtime.megaTools import (
    agi_mind as _mega_agi_mind,
)
from arifosmcp.runtime.megaTools import (
    apex_judge as _mega_apex_judge,
)
from arifosmcp.runtime.megaTools import (
    architect_registry as _mega_architect_registry,
)
from arifosmcp.runtime.megaTools import (
    arifOS_kernel as _mega_arifOS_kernel,
)
from arifosmcp.runtime.megaTools import (
    asi_heart as _mega_asi_heart,
)
from arifosmcp.runtime.megaTools import (
    code_engine as _mega_code_engine,
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

init_anchor_impl = _mega_init_anchor
revoke_anchor_state_impl = _mega_init_anchor
get_caller_status_impl = _mega_init_anchor
apex_soul_dispatch_impl = apex_judge_dispatch_impl

# init_000 was purged in sovereign unification — dead code removed

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS (kept in tools.py for utilities)
# ═══════════════════════════════════════════════════════════════════════════════


def _has_valid_proof(payload: dict[str, Any], actor_id: str) -> bool:
    proof = payload.get("auth_token") or payload.get("proof") or payload.get("signature")
    if isinstance(proof, dict):
        return validate_sovereign_proof(actor_id, proof)
    return False


async def init_anchor(
    mode: str | None = None,
    payload: dict[str, Any] | None = None,
    query: str | None = None,
    session_id: str | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope:
    envelope = await init_anchor_impl(
        mode=mode,
        payload=payload,
        query=query,
        session_id=session_id,
        **kwargs,
    )
    return seal_runtime_envelope(
        envelope,
        "init_anchor",
        input_payload=payload or {**kwargs, "query": query, "session_id": session_id, "mode": mode},
        mode=mode,
    )


async def arifOS_kernel(*args: Any, **kwargs: Any) -> RuntimeEnvelope:
    payload = kwargs.get("payload")
    mode = kwargs.get("mode")
    if mode is not None:
        if mode not in {"kernel", "status"}:
            raise ValueError(f"Invalid mode for arifOS_kernel: {mode}")
        if isinstance(payload, dict):
            envelope = await arifos_kernel_impl(
                query=payload.get("query"),
                risk_tier=kwargs.get("risk_tier", "medium"),
                auth_context=kwargs.get("auth_context"),
                dry_run=kwargs.get("dry_run", True),
                allow_execution=kwargs.get("allow_execution", False),
                session_id=payload.get("session_id"),
                ctx=kwargs.get("ctx"),
                intent=payload.get("intent"),
            )
            return seal_runtime_envelope(
                envelope,
                "arifOS_kernel",
                input_payload=payload,
                mode=mode,
            )
    envelope = await _mega_arifOS_kernel(*args, **kwargs)
    return seal_runtime_envelope(
        envelope,
        "arifOS_kernel",
        input_payload=kwargs.get("payload") or kwargs,
        mode=kwargs.get("mode"),
    )


async def forge(*args: Any, **kwargs: Any) -> RuntimeEnvelope:
    spec = kwargs.pop("spec", None)
    if spec is not None and "query" not in kwargs:
        kwargs["query"] = spec
    return await agi_mind(mode="forge", *args, **kwargs)


async def apex_soul(*args: Any, **kwargs: Any) -> RuntimeEnvelope:
    envelope = await _mega_apex_judge(*args, **kwargs)
    return seal_runtime_envelope(
        envelope,
        "apex_soul",
        input_payload=kwargs.get("payload") or kwargs,
        mode=kwargs.get("mode"),
    )


async def vault_ledger(*args: Any, **kwargs: Any) -> RuntimeEnvelope:
    envelope = await _mega_vault_ledger(*args, **kwargs)
    return seal_runtime_envelope(
        envelope,
        "vault_ledger",
        input_payload=kwargs.get("payload") or kwargs,
        mode=kwargs.get("mode"),
    )


async def agi_mind(*args: Any, **kwargs: Any) -> RuntimeEnvelope:
    envelope = await _mega_agi_mind(*args, **kwargs)
    return seal_runtime_envelope(
        envelope,
        "agi_mind",
        input_payload=kwargs.get("payload") or kwargs,
        mode=kwargs.get("mode"),
    )


async def asi_heart(*args: Any, **kwargs: Any) -> RuntimeEnvelope:
    envelope = await _mega_asi_heart(*args, **kwargs)
    return seal_runtime_envelope(
        envelope,
        "asi_heart",
        input_payload=kwargs.get("payload") or kwargs,
        mode=kwargs.get("mode"),
    )


async def engineering_memory(*args: Any, **kwargs: Any) -> RuntimeEnvelope:
    envelope = await _mega_engineering_memory(*args, **kwargs)
    return seal_runtime_envelope(
        envelope,
        "engineering_memory",
        input_payload=kwargs.get("payload") or kwargs,
        mode=kwargs.get("mode"),
    )


async def physics_reality(*args: Any, **kwargs: Any) -> RuntimeEnvelope:
    envelope = await _mega_physics_reality(*args, **kwargs)
    return seal_runtime_envelope(
        envelope,
        "physics_reality",
        input_payload=kwargs.get("payload") or kwargs,
        mode=kwargs.get("mode"),
    )


async def math_estimator(*args: Any, **kwargs: Any) -> RuntimeEnvelope:
    envelope = await _mega_math_estimator(*args, **kwargs)
    return seal_runtime_envelope(
        envelope,
        "math_estimator",
        input_payload=kwargs.get("payload") or kwargs,
        mode=kwargs.get("mode"),
    )


async def code_engine(*args: Any, **kwargs: Any) -> RuntimeEnvelope:
    envelope = await _mega_code_engine(*args, **kwargs)
    return seal_runtime_envelope(
        envelope,
        "code_engine",
        input_payload=kwargs.get("payload") or kwargs,
        mode=kwargs.get("mode"),
    )




def select_governed_philosophy(
    context: str,
    *,
    stage: str,
    verdict: str,
    g_score: float = 1.0,
    failed_floors: list[str] = None,
    session_id: str = "global",
) -> dict[str, Any]:
    from arifosmcp.runtime.philosophy import select_governed_philosophy as _select

    return _select(
        context=context,
        stage=stage,
        verdict=verdict,
        g_score=g_score,
        failed_floors=failed_floors,
        session_id=session_id,
    )


_public_tool_names_fn = _registry_tool_names
_public_tool_specs_fn = _registry_tool_specs
_public_tool_spec_by_name_fn = _registry_tool_spec_by_name
PUBLIC_KERNEL_TOOL_NAME = "arifOS_kernel"
LEGACY_KERNEL_TOOL_NAME = "metabolic_loop_router"

try:
    from core.telemetry import check_adaptation_status, get_current_hysteresis
except Exception:

    def check_adaptation_status() -> dict[str, Any]:
        return {"status": "unavailable"}

    def get_current_hysteresis() -> float:
        return 0.0


try:
    from core.physics.thermodynamics_hardened import get_thermodynamic_report
except Exception:

    def get_thermodynamic_report(session_id: str) -> dict[str, Any]:
        return {"status": "unavailable", "session_id": session_id}


# ═══════════════════════════════════════════════════════════════════════════════
# LEGACY COMPAT TOOLS (kept for backward compatibility)
# ═══════════════════════════════════════════════════════════════════════════════


async def metabolic_loop_router(
    query: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    intent: IntentType = None,
    human_approval: bool = False,
    risk_tier: str = "medium",
    dry_run: bool = True,
    allow_execution: bool = False,
    caller_context: dict | None = None,
    auth_context: dict | None = None,
    ctx: Context | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope:
    return await arifOS_kernel(
        query=query,
        session_id=session_id,
        actor_id=actor_id,
        intent=intent,
        human_approval=human_approval,
        risk_tier=risk_tier,
        dry_run=dry_run,
        allow_execution=allow_execution,
        caller_context=caller_context,
        auth_context=auth_context,
        ctx=ctx,
        **kwargs,
    )


def _build_user_model(
    tool_name: str, stage_value: str, payload: dict[str, Any], envelope_data: dict[str, Any]
) -> UserModel:
    query = str(
        payload.get("query") or payload.get("intent") or payload.get("content") or ""
    ).strip()
    context = str(payload.get("context") or "").strip()
    output_constraints: list[UserModelField] = []
    lowered = f"{query} {context}".lower()
    if "concise" in lowered:
        output_constraints.append(
            UserModelField(value="keep_response_concise", source=UserModelSource.EXPLICIT)
        )
    if envelope_data.get("meta", {}).get("dry_run") or payload.get("dry_run"):
        output_constraints.append(
            UserModelField(
                value="state_that_execution_is_simulated", source=UserModelSource.OBSERVABLE
            )
        )
    return UserModel(
        stated_goal=UserModelField(
            value=query or context or f"{tool_name}:{stage_value}", source=UserModelSource.EXPLICIT
        ),
        output_constraints=output_constraints,
    )


async def arifos_kernel(
    query: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    intent: IntentType = None,
    human_approval: bool = False,
    risk_tier: str = "medium",
    dry_run: bool = True,
    allow_execution: bool = False,
    caller_context: dict | None = None,
    auth_context: dict | None = None,
    ctx: Context | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope:
    return await arifOS_kernel(
        query=query,
        session_id=session_id,
        actor_id=actor_id,
        intent=intent,
        human_approval=human_approval,
        risk_tier=risk_tier,
        dry_run=dry_run,
        allow_execution=allow_execution,
        caller_context=caller_context,
        auth_context=auth_context,
        ctx=ctx,
        **kwargs,
    )


async def check_vital(
    session_id: str | None = None,
    actor_id: str | None = None,
    risk_tier: str = "low",
    dry_run: bool = True,
    auth_context: dict | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope:
    from arifosmcp.runtime.megaTools import math_estimator as impl

    return await impl(
        mode="vitals",
        session_id=session_id,
        actor_id=actor_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        auth_context=auth_context,
        **kwargs,
    )


async def audit_rules(
    session_id: str | None = None,
    actor_id: str | None = None,
    risk_tier: str = "low",
    dry_run: bool = True,
    auth_context: dict | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope:
    from arifosmcp.runtime.megaTools import apex_judge as impl

    return await impl(
        mode="rules",
        session_id=session_id,
        actor_id=actor_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        auth_context=auth_context,
        **kwargs,
    )


async def agi_reason(
    query: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    intent: str = None,
    human_approval: bool = False,
    risk_tier: str = "medium",
    dry_run: bool = True,
    caller_context: dict | None = None,
    auth_context: dict | None = None,
    ctx: Context | None = None,
    constitutional_context: str | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope:
    from arifosmcp.runtime.megaTools import agi_mind as impl

    return await impl(
        mode="reason",
        query=query,
        session_id=session_id,
        actor_id=actor_id,
        intent=intent,
        human_approval=human_approval,
        risk_tier=risk_tier,
        dry_run=dry_run,
        caller_context=caller_context,
        auth_context=auth_context,
        ctx=ctx,
        constitutional_context=constitutional_context,
        **kwargs,
    )


async def agi_reflect(
    query: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    intent: str = None,
    human_approval: bool = False,
    risk_tier: str = "medium",
    dry_run: bool = True,
    caller_context: dict | None = None,
    auth_context: dict | None = None,
    ctx: Context | None = None,
    constitutional_context: str | None = None,
) -> RuntimeEnvelope:
    return await agi_mind(
        mode="reflect",
        query=query,
        session_id=session_id,
        actor_id=actor_id,
        intent=intent,
        human_approval=human_approval,
        risk_tier=risk_tier,
        dry_run=dry_run,
        caller_context=caller_context,
        auth_context=auth_context,
        ctx=ctx,
        constitutional_context=constitutional_context,
    )


async def reason_mind(**kwargs: Any) -> RuntimeEnvelope:
    return await agi_mind(mode="reason", **kwargs)


async def reason_mind_synthesis(**kwargs: Any) -> RuntimeEnvelope:
    return await agi_mind(mode="reason", **kwargs)


async def integrate_analyze_reflect(**kwargs: Any) -> RuntimeEnvelope:
    return await agi_mind(mode="reflect", **kwargs)


async def agi_asi_forge_handler(**kwargs: Any) -> RuntimeEnvelope:
    return await agi_mind(mode="forge", **kwargs)


async def asi_simulate(
    content: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    human_approval: bool = False,
    risk_tier: str = "medium",
    dry_run: bool = True,
    caller_context: dict | None = None,
    auth_context: dict | None = None,
    ctx: Context | None = None,
) -> RuntimeEnvelope:
    return await asi_heart(
        mode="simulate",
        content=content,
        session_id=session_id,
        actor_id=actor_id,
        human_approval=human_approval,
        risk_tier=risk_tier,
        dry_run=dry_run,
        caller_context=caller_context,
        auth_context=auth_context,
        ctx=ctx,
    )


async def asi_critique(
    content: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    human_approval: bool = False,
    risk_tier: str = "medium",
    dry_run: bool = True,
    caller_context: dict | None = None,
    auth_context: dict | None = None,
    ctx: Context | None = None,
) -> RuntimeEnvelope:
    return await asi_heart(
        mode="critique",
        content=content,
        session_id=session_id,
        actor_id=actor_id,
        human_approval=human_approval,
        risk_tier=risk_tier,
        dry_run=dry_run,
        caller_context=caller_context,
        auth_context=auth_context,
        ctx=ctx,
    )


async def apex_judge(
    mode: str = "judge",
    candidate: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    human_approval: bool = False,
    risk_tier: str = "medium",
    dry_run: bool = True,
    caller_context: dict | None = None,
    auth_context: dict | None = None,
    ctx: Context | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope:
    from arifosmcp.runtime.megaTools import apex_judge as impl

    return await impl(
        mode=mode,
        proposal=candidate,
        session_id=session_id,
        actor_id=actor_id,
        human_approval=human_approval,
        risk_tier=risk_tier,
        dry_run=dry_run,
        caller_context=caller_context,
        auth_context=auth_context,
        ctx=ctx,
        **kwargs,
    )


async def vault_seal(
    verdict: str | None = None,
    evidence: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    human_approval: bool = False,
    risk_tier: str = "medium",
    dry_run: bool = True,
    caller_context: dict | None = None,
    auth_context: dict | None = None,
    ctx: Context | None = None,
) -> RuntimeEnvelope:
    return await vault_ledger(
        mode="seal",
        query=verdict,
        session_id=session_id,
        actor_id=actor_id,
        human_approval=human_approval,
        risk_tier=risk_tier,
        dry_run=dry_run,
        caller_context=caller_context,
        auth_context=auth_context,
        ctx=ctx,
    )


async def verify_vault_ledger(
    session_id: str | None = None,
    actor_id: str | None = None,
    full_scan: bool = True,
) -> RuntimeEnvelope:
    return await vault_ledger(
        mode="verify",
        session_id=session_id,
        actor_id=actor_id,
    )


async def reality_compass(
    input: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> RuntimeEnvelope:
    return await physics_reality(
        mode="compass",
        query=input,
        session_id=session_id,
        actor_id=actor_id,
    )


async def search_reality(
    input: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> RuntimeEnvelope:
    return await physics_reality(
        mode="search",
        query=input,
        session_id=session_id,
        actor_id=actor_id,
    )


async def reality_atlas(
    input: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> RuntimeEnvelope:
    return await physics_reality(
        mode="atlas",
        query=input,
        session_id=session_id,
        actor_id=actor_id,
    )


async def ingest_evidence(
    input: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> RuntimeEnvelope:
    return await physics_reality(
        mode="ingest",
        query=input,
        session_id=session_id,
        actor_id=actor_id,
    )


async def system_health(**kwargs: Any) -> RuntimeEnvelope:
    return await math_estimator(mode="health", **kwargs)


async def cost_estimator(**kwargs: Any) -> RuntimeEnvelope:
    return await math_estimator(mode="cost", **kwargs)


async def fs_inspect(**kwargs: Any) -> RuntimeEnvelope:
    return await code_engine(mode="fs", **kwargs)


async def process_list(**kwargs: Any) -> RuntimeEnvelope:
    return await code_engine(mode="process", **kwargs)


async def net_status(**kwargs: Any) -> RuntimeEnvelope:
    return await code_engine(mode="net", **kwargs)


async def log_tail(**kwargs: Any) -> RuntimeEnvelope:
    return await code_engine(mode="tail", **kwargs)


async def trace_replay(**kwargs: Any) -> RuntimeEnvelope:
    return await code_engine(mode="replay", **kwargs)


async def agentzero_engineer(
    task: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    human_approval: bool = False,
    risk_tier: str = "medium",
    dry_run: bool = True,
    caller_context: dict | None = None,
    auth_context: dict | None = None,
    ctx: Context | None = None,
) -> RuntimeEnvelope:
    return await engineering_memory(
        mode="engineer",
        task=task,
        session_id=session_id,
        actor_id=actor_id,
        human_approval=human_approval,
        risk_tier=risk_tier,
        dry_run=dry_run,
        caller_context=caller_context,
        auth_context=auth_context,
        ctx=ctx,
    )


async def agentzero_validate(**kwargs: Any) -> RuntimeEnvelope:
    return await apex_judge(mode="validate", **kwargs)


async def agentzero_armor_scan(**kwargs: Any) -> RuntimeEnvelope:
    return await apex_judge(mode="armor", **kwargs)


async def agentzero_hold_check(**kwargs: Any) -> RuntimeEnvelope:
    return await apex_judge(mode="hold", **kwargs)


async def agentzero_memory_query(**kwargs: Any) -> RuntimeEnvelope:
    return await engineering_memory(mode="query", **kwargs)


async def seal_vault_commit(**kwargs: Any) -> RuntimeEnvelope:
    return await vault_ledger(mode="seal", **kwargs)


async def architect_registry(mode: str = "list", **kwargs: Any) -> RuntimeEnvelope:
    from arifosmcp.runtime.megaTools import architect_registry as impl

    envelope = await impl(mode=mode, **kwargs)
    return seal_runtime_envelope(
        envelope,
        "architect_registry",
        input_payload=kwargs.get("payload") or kwargs,
        mode=mode,
    )


async def compat_probe(mode: str = "audit", **kwargs: Any) -> RuntimeEnvelope:
    from arifosmcp.runtime.megaTools import compat_probe as impl

    return await impl(mode=mode, **kwargs)


# ═══════════════════════════════════════════════════════════════════════════════
# FINAL TOOL IMPLEMENTATIONS MAP
# ═══════════════════════════════════════════════════════════════════════════════

FINAL_TOOL_IMPLEMENTATIONS: dict[str, Callable[..., Any]] = {
    "init_anchor": init_anchor,
    "arifOS_kernel": arifOS_kernel,
    "apex_soul": apex_soul,
    "apex_judge": apex_judge,
    "vault_ledger": vault_ledger,
    "agi_mind": agi_mind,
    "asi_heart": asi_heart,
    "engineering_memory": engineering_memory,
    "physics_reality": physics_reality,
    "math_estimator": math_estimator,
    "code_engine": code_engine,
    "architect_registry": architect_registry,
    "compat_probe": compat_probe,
    # multi-agent shared memory
    "shared_memory": shared_memory_tool,
}

LEGACY_COMPAT_MAP: dict[str, Callable[..., Any]] = {
    "metabolic_loop_router": metabolic_loop_router,
    "arifos_kernel": arifos_kernel,
    "init_anchor_state": init_anchor,
    "revoke_anchor_state": init_anchor,
    "get_caller_status": init_anchor,
    "check_vital": check_vital,
    "audit_rules": audit_rules,
    "agi_reason": agi_reason,
    "agi_reflect": agi_reflect,
    "asi_critique": asi_critique,
    "asi_simulate": asi_simulate,
    "apex_judge": apex_judge,
    "vault_seal": vault_seal,
    "verify_vault_ledger": verify_vault_ledger,
    "reality_compass": reality_compass,
    "reality_atlas": reality_atlas,
    "search_reality": search_reality,
    "ingest_evidence": ingest_evidence,
    "agentzero_engineer": agentzero_engineer,
    "agentzero_validate": agentzero_validate,
    "agentzero_armor_scan": agentzero_armor_scan,
    "agentzero_hold_check": agentzero_hold_check,
    "agentzero_memory_query": agentzero_memory_query,
    "seal_vault_commit": seal_vault_commit,
    "forge": metabolic_loop_router,
    "reason_mind_synthesis": reason_mind_synthesis,
    "agi_asi_forge_handler": agi_asi_forge_handler,
}

ALL_TOOL_IMPLEMENTATIONS = {**FINAL_TOOL_IMPLEMENTATIONS, **LEGACY_COMPAT_MAP}


# ═══════════════════════════════════════════════════════════════════════════════
# LEGACY PAYLOAD BUILDER
# ═══════════════════════════════════════════════════════════════════════════════


def _build_legacy_payload(mega_tool: str, mode: str, values: dict[str, Any]) -> dict[str, Any]:
    payload = {key: value for key, value in values.items() if value is not None}
    if mega_tool == "apex_judge":
        candidate = (
            payload.get("candidate")
            or payload.get("candidate_output")
            or payload.get("input_to_validate")
            or payload.get("content")
            or payload.get("query")
        )
        if candidate is not None:
            payload.setdefault("candidate", candidate)
    elif mega_tool == "asi_heart":
        content = (
            payload.get("content")
            or payload.get("draft_output")
            or payload.get("scenario")
            or payload.get("query")
        )
        if content is not None:
            payload.setdefault("content", content)
    elif mega_tool == "physics_reality":
        input_value = payload.get("input")
        if input_value is None:
            if mode == "ingest":
                input_value = payload.get("url") or payload.get("query") or payload.get("content")
            else:
                input_value = payload.get("query") or payload.get("content") or payload.get("url")
        if input_value is not None:
            payload.setdefault("input", input_value)
    elif mega_tool == "engineering_memory":
        task = payload.get("task") or payload.get("task_description")
        if task is not None:
            payload.setdefault("task", task)
    elif mega_tool == "vault_ledger":
        if payload.get("summary") is not None and payload.get("evidence") is None:
            payload["evidence"] = payload["summary"]
    elif mega_tool == "arifOS_kernel":
        payload.setdefault("query", "")
    return payload


def _build_user_model(
    tool_name: str, stage_value: str, payload: dict[str, Any], envelope_data: dict[str, Any]
) -> UserModel:
    query = str(
        payload.get("query") or payload.get("intent") or payload.get("content") or ""
    ).strip()
    context = str(payload.get("context") or "").strip()
    output_constraints: list[UserModelField] = []
    lowered = f"{query} {context}".lower()
    if "concise" in lowered:
        output_constraints.append(
            UserModelField(value="keep_response_concise", source=UserModelSource.EXPLICIT)
        )
    if envelope_data.get("meta", {}).get("dry_run") or payload.get("dry_run"):
        output_constraints.append(
            UserModelField(
                value="state_that_execution_is_simulated", source=UserModelSource.OBSERVABLE
            )
        )
    return UserModel(
        stated_goal=UserModelField(
            value=query or context or f"{tool_name}:{stage_value}", source=UserModelSource.EXPLICIT
        ),
        output_constraints=output_constraints,
    )


def _resolve_caller_context(
    caller_context: CallerContext | None, requested_persona: str | None
) -> CallerContext:
    base = caller_context or CallerContext()
    if requested_persona:
        try:
            base.persona_id = PersonaId(requested_persona.lower())
        except (ValueError, AttributeError):
            pass
    return base


def _resolve_caller_state(
    session_id: str, authority: Any
) -> tuple[str, list[str], list[dict[str, str]]]:
    """Single source of truth for caller state resolution."""
    from .tools_internal import _resolve_caller_state as _resolve

    return _resolve(session_id, authority)


def _make_registration_shim(handler: Callable[..., Any]) -> Callable[..., Any]:
    """Adapt variadic tool handlers to a FastMCP-compatible signature."""

    async def _shim(
        mode: str | None = None,
        payload: dict[str, Any] | None = None,
        auth_context: dict[str, Any] | None = None,
        caller_context: dict[str, Any] | None = None,
        risk_tier: str = "medium",
        dry_run: bool = True,
        allow_execution: bool = False,
        debug: bool = False,
        request_id: str | None = None,
        timestamp: str | None = None,
        session_id: str | None = None,
        actor_id: str | None = None,
        intent: Any = None,
        declared_name: str | None = None,
        reason: str | None = None,
        human_approval: bool = False,
        query: str | None = None,
        context: str | None = None,
        content: str | None = None,
        input: str | None = None,
        candidate: str | None = None,
        hold_id: str | None = None,
        message: str | None = None,
        raw_input: str | None = None,
        constitutional_context: str | None = None,
        ctx: Context | None = None,
    ) -> Any:
        kwargs: dict[str, Any] = {
            "mode": mode,
            "payload": payload,
            "auth_context": auth_context,
            "caller_context": caller_context,
            "risk_tier": risk_tier,
            "dry_run": dry_run,
            "allow_execution": allow_execution,
            "debug": debug,
            "request_id": request_id,
            "timestamp": timestamp,
            "session_id": session_id,
            "actor_id": actor_id,
            "intent": intent,
            "declared_name": declared_name,
            "reason": reason,
            "human_approval": human_approval,
            "query": query,
            "context": context,
            "content": content,
            "input": input,
            "candidate": candidate,
            "hold_id": hold_id,
            "message": message,
            "raw_input": raw_input,
            "constitutional_context": constitutional_context,
            "ctx": ctx,
        }
        return await handler(**{key: value for key, value in kwargs.items() if value is not None})

    return _shim


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL REGISTRATION
# ═══════════════════════════════════════════════════════════════════════════════


def register_tools(mcp: FastMCP, profile: str = "full") -> None:
    del profile
    import inspect

    from arifosmcp.runtime.ingress_middleware import IngressToleranceMiddleware
    from fastmcp.tools.function_tool import FunctionTool

    specs = {spec.name: spec for spec in _public_tool_specs_fn()}
    tool_param_sets: dict[str, set[str]] = {}
    hidden_public_conflicts = {"apex_judge", "compat_probe"}
    shimmed_tools = {
        "init_anchor",
        "arifOS_kernel",
        "apex_soul",
        "vault_ledger",
        "agi_mind",
        "asi_heart",
        "engineering_memory",
        "physics_reality",
        "math_estimator",
        "code_engine",
        "architect_registry",
        "agi_reason",
    }

    # Register only the 11 canonical mega-tools on the public FastMCP surface.
    # Legacy aliases remain internally callable but are not exposed to MCP clients.
    # Variadic mega-tool wrappers need concrete shims because FunctionTool rejects *args/**kwargs.
    _canonical_names = set(specs.keys())  # derived from PUBLIC_TOOL_SPECS — always exactly 11
    all_public_tools = {k: v for k, v in FINAL_TOOL_IMPLEMENTATIONS.items() if k in _canonical_names}
    for name, handler in all_public_tools.items():
        if name in hidden_public_conflicts:
            continue
        if handler is None:
            continue
        exposed_handler = _make_registration_shim(handler) if name in shimmed_tools else handler
        sig = inspect.signature(exposed_handler)
        if any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()):
            continue  # skip **kwargs handlers
        spec = specs.get(name)
        ft = FunctionTool.from_function(
            exposed_handler,
            name=name,
            description=spec.description if spec else name,
        )
        if spec is not None:
            ft.parameters = dict(spec.input_schema)
        else:
            ft.parameters["additionalProperties"] = True
        tool_param_sets[name] = set(sig.parameters.keys())
        mcp.add_tool(ft)

    # C1 FIX: Instantiate middleware with pre-built param sets, pass instance
    ingress = IngressToleranceMiddleware(tool_param_sets=tool_param_sets)
    mcp.add_middleware(ingress)


__all__ = [
    # P2: Public tool registry exports (backward compat)
    "public_tool_names",
    "public_tool_specs",
    "public_tool_spec_by_name",
    # 11 Mega-Tools
    "init_anchor",
    "arifOS_kernel",
    "apex_soul",
    "apex_judge",
    "vault_ledger",
    "agi_mind",
    "asi_heart",
    "engineering_memory",
    "physics_reality",
    "math_estimator",
    "code_engine",
    "architect_registry",
    # Functional-verb aliases (MCP clean schema 2026-04-06)
    "register_tool_aliases",
    # Legacy compat
    "metabolic_loop_router",
    "arifos_kernel",
    "check_vital",
    "audit_rules",
    "agi_reason",
    "agi_reflect",
    "asi_critique",
    "asi_simulate",
    "apex_judge",
    "vault_seal",
    "verify_vault_ledger",
    "reality_compass",
    "reality_atlas",
    "search_reality",
    "ingest_evidence",
    "agentzero_engineer",
    "agentzero_validate",
    "agentzero_armor_scan",
    "agentzero_hold_check",
    "agentzero_memory_query",
    "seal_vault_commit",
    # Utilities
    "FINAL_TOOL_IMPLEMENTATIONS",
    "LEGACY_COMPAT_MAP",
    "ALL_TOOL_IMPLEMENTATIONS",
    "register_tools",
    "select_governed_philosophy",
    "_has_valid_proof",
    "_build_legacy_payload",
    "_build_user_model",
    "_resolve_caller_context",
    "_resolve_caller_state",
]


# P2: Re-export public registry helpers for backward compat
# These were removed from module-level but are still imported by tests/external code
public_tool_names = _registry_tool_names
public_tool_specs = _registry_tool_specs
public_tool_spec_by_name = _registry_tool_spec_by_name
