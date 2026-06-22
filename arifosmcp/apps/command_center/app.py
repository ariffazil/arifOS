"""arifOS Command Center MCP App.

One cockpit. Separate chambers. Judge above action.

Architecture:
- FastMCPApp ("arifOS Command Center") owns the UI + app-scoped backend tools.
- Only command_center() is a visible UI entry point for the model.
- v0.2 wires all tools to the real arifOS canonical backends (888_JUDGE, 999_VAULT,
  010_FORGE, 666_GATEWAY, 777_OPS). No simulation.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import asyncio
import inspect
import os
import threading

from fastmcp import FastMCP
from fastmcp.apps import FastMCPApp
from mcp.types import ToolAnnotations

from arifosmcp.apps.command_center.forge_app import governed_forge_execute
from arifosmcp.apps.command_center.governance import (
    classify_risk,
    hash_preview,
    judge_candidate,
)
from arifosmcp.apps.command_center.interceptor import governance_guard
from arifosmcp.apps.command_center.judge_app import governed_judge_deliberate
from arifosmcp.apps.command_center.models import (
    ForgeDryRun,
    GatewayHandshake,
    JudgeVerdict,
    OpsVitals,
    SessionStatus,
    VaultDrySeal,
    VaultEntry,
    VaultList,
)
from arifosmcp.apps.command_center.state import get_state
from arifosmcp.apps.command_center.vault_audit import get_vault_audit
from arifosmcp.apps.command_center.vault_chain import append_vault_record
from arifosmcp.runtime.tools import (
    _CANONICAL_HANDLERS,
    _SESSION_STORE,
)

try:
    from prefab_ui.actions import SetState
    from prefab_ui.actions.mcp import CallTool
    from prefab_ui.app import PrefabApp
    from prefab_ui.components import (
        Badge,
        Button,
        Card,
        CardContent,
        CardHeader,
        CardTitle,
        Column,
        Heading,
        Input,
        Metric,
        Row,
        Separator,
        Tab,
        Tabs,
        Text,
        Textarea,
    )

    PREFAB_UI_AVAILABLE = True
except ImportError:
    SetState = None
    CallTool = None
    PrefabApp = None
    Badge = None
    Button = None
    Card = None
    CardContent = None
    CardHeader = None
    CardTitle = None
    Column = None
    Heading = None
    Input = None
    Metric = None
    Row = None
    Separator = None
    Tab = None
    Tabs = None
    Text = None
    Textarea = None
    PREFAB_UI_AVAILABLE = False

# Evaluation mode: when True, tools use simulated governance responses.
# When False (production/App Store), tools proxy to real canonical backends.
EVALUATION_MODE = os.environ.get("ARIFOS_EVALUATION_MODE", "false").lower() in (
    "true",
    "1",
    "yes",
)

# Evaluation mode: when True, tools use simulated governance responses.
# When False (production/App Store), tools proxy to real canonical backends.
EVALUATION_MODE = os.environ.get("ARIFOS_EVALUATION_MODE", "false").lower() in (
    "true",
    "1",
    "yes",
)

# ---------------------------------------------------------------------------
# Governance helpers
# ---------------------------------------------------------------------------


def _get_live_session() -> dict:
    """Pull live session state from the Command Center registry or arifOS runtime."""
    # Priority 1: Command Center local session registry (v0.2+ session continuity)
    state = get_state()
    local = state.get_session()
    if local:
        return {
            "session_id": local.session_id,
            "actor_id": local.actor_id,
            "declared_name": local.declared_name,
            "intent": local.intent,
            "token": local.token,
            "floor_audit": local.floor_audit,
            "created_at": local.created_at,
            "expires_at": local.expires_at,
        }

    # Priority 2: arifOS canonical persistent session store
    try:
        # Get the most recently created session as a heuristic if no active ID
        sessions = _SESSION_STORE.values()
        if sessions:
            # Sort by created_at desc
            sorted_sessions = sorted(sessions, key=lambda x: x.get("created_at", ""), reverse=True)
            return sorted_sessions[0]
    except Exception:
        pass

    return {}


def _kernel_status() -> dict:
    """Get kernel routing status."""
    try:
        handler = _CANONICAL_HANDLERS.get("arif_kernel_route")
        return _invoke_handler(handler, mode="status", actor_id="arif")
    except Exception:
        return {}


def _kernel_telemetry() -> dict:
    """Get kernel thermodynamic telemetry."""
    try:
        handler = _CANONICAL_HANDLERS.get("arif_kernel_route")
        return _invoke_handler(handler, mode="telemetry", actor_id="arif")
    except Exception:
        return {}


def _await_sync(awaitable):
    """Resolve coroutine results from sync FastMCP app tools."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(awaitable)

    box: dict[str, object] = {}

    def runner() -> None:
        try:
            box["result"] = asyncio.run(awaitable)
        except BaseException as exc:  # pragma: no cover - defensive thread bridge
            box["error"] = exc

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()
    thread.join()
    if "error" in box:
        raise box["error"]  # type: ignore[misc]
    return box.get("result")


def _invoke_handler(handler, **kwargs) -> dict:
    if handler is None:
        return {"result": {}, "status": "HOLD", "meta": {"reason": "handler_not_found"}}
    result = handler(**kwargs)
    if inspect.isawaitable(result):
        result = _await_sync(result)
    return result if isinstance(result, dict) else {"result": result}


def _route_action(target: str, task: str) -> dict:
    """Route an action intent through 444_KERNEL. Returns routing decision."""
    try:
        handler = _CANONICAL_HANDLERS.get("arif_kernel_route")
        return _invoke_handler(handler, mode="route", target=target, task=task, actor_id="arif")
    except Exception as e:
        return {"result": {}, "status": "HOLD", "meta": {"reason": str(e)}}


# ---------------------------------------------------------------------------
# Safety constants — red-team hardening
# ---------------------------------------------------------------------------
MAX_MANIFEST_LENGTH = 10_000  # 10KB
MAX_CANDIDATE_LENGTH = 10_000  # 10KB
MAX_PAYLOAD_LENGTH = 10_000  # 10KB
MAX_AGENT_NAME_LENGTH = 256


def _truncate(text: str, max_len: int) -> str:
    """Safely truncate text with an ellipsis indicator."""
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


# ---------------------------------------------------------------------------
# App definition
# ---------------------------------------------------------------------------
command_center_app = FastMCPApp("arifOS Command Center")

# ---------------------------------------------------------------------------
# Backend tools — app-scoped, not general model-facing actions
# ---------------------------------------------------------------------------


@command_center_app.tool()
def arif_cc_sense_observe(mode: str = "vitals", query: str | None = None) -> dict:
    """Use this when refreshing the reality sensing panel.

    Proxies to 111_SENSE backend for reality grounding and observation.
    """
    state = get_state()
    state.reality_checks += 1

    handler = _CANONICAL_HANDLERS.get("arif_observe")
    return _invoke_handler(handler, mode=mode, query=query, actor_id="arif")


@command_center_app.tool()
def arif_cc_evidence_fetch(url: str, query: str | None = None) -> dict:
    """Use this when the user wants to fetch evidence from a URL.

    Proxies to 222_FETCH backend for evidence-preserving ingestion.
    """
    state = get_state()
    state.fetch_calls += 1
    handler = _CANONICAL_HANDLERS.get("arif_fetch")
    return _invoke_handler(handler, url=url, query=query, actor_id="arif")


@command_center_app.tool()
def arif_cc_mind_reason(query: str, mode: str = "reason") -> dict:
    """Use this when the user wants to perform constitutional reasoning.

    Proxies to 333_MIND backend for symbolic reasoning.
    """
    state = get_state()
    state.reason_calls += 1
    handler = _CANONICAL_HANDLERS.get("arif_think")
    return _invoke_handler(handler, query=query, mode=mode, actor_id="arif")


@command_center_app.tool()
def arif_cc_heart_critique(target: str, mode: str = "critique") -> dict:
    """Use this when the user wants an ethical risk assessment.

    Proxies to 666_HEART backend for ethical critique.
    """
    state = get_state()
    state.critique_calls += 1
    handler = _CANONICAL_HANDLERS.get("arif_critique")
    return _invoke_handler(handler, target=target, mode=mode, actor_id="arif")


@command_center_app.tool()
def arif_cc_reply_compose(message: str, style: str = "formal") -> dict:
    """Use this when the user wants to compose a governed response.

    Proxies to 444_REPLY backend for response composition.
    """
    state = get_state()
    state.reply_compositions += 1
    handler = _CANONICAL_HANDLERS.get("arif_compose")
    return _invoke_handler(handler, message=message, style=style, actor_id="arif")


@command_center_app.tool()
def arif_cc_memory_recall(query: str, mode: str = "recall") -> dict:
    """Use this when the user wants to access associative memory.

    Proxies to 555_MEMORY backend for context retrieval.
    """
    state = get_state()
    state.memory_recalls += 1
    handler = _CANONICAL_HANDLERS.get("arif_memory_recall")
    return _invoke_handler(handler, query=query, mode=mode, actor_id="arif")


@command_center_app.tool()
def arif_cc_session_status() -> dict:
    """Use this when refreshing the constitutional session panel.

    Returns live governance state from the arifOS kernel: session ID, actor ID,
    constitution hash, stage, lane, plan state, latest verdict, required next
    tool, and blocked reason. Read-only diagnostic.

    Do not use for creating new sessions — use arif_init instead.
    """
    state = get_state()
    state.session_count += 1

    local = state.get_session()
    if local:
        return SessionStatus(
            session_id=local.session_id,
            actor_id=local.actor_id,
            constitution_id="arifos-constitution-v2026.04.26",
            stage="000",
            lane="AGI",
            sealed=False,
            authority="human_judge_required_for_consequential_actions",
            plan_state="draft",
            token=local.token,
            floor_audit=local.floor_audit,
            created_at=local.created_at,
            expires_at=local.expires_at,
        ).model_dump()

    if EVALUATION_MODE:
        return SessionStatus(
            session_id="eval-session",
            actor_id="arif",
            stage="000",
            lane="AGI",
            sealed=False,
            authority="human_judge_required_for_consequential_actions",
            plan_state="draft",
        ).model_dump()

    live = _get_live_session()
    kstatus = _kernel_status()
    ktelemetry = _kernel_telemetry()

    result_status = kstatus.get("result", {})
    result_telemetry = ktelemetry.get("result", {})

    session_id = live.get("session_id", live.get("id", "uninitialized"))
    actor_id = live.get("actor_id", "anonymous")
    stage = live.get("stage", result_status.get("stage", "000"))
    lane = live.get("lane", "AGI")
    plan_id = live.get("plan_id", None)
    plan_state = live.get("caller_state", "draft")
    authority = live.get(
        "authority_level",
        live.get("authority", "human_judge_required_for_consequential_actions"),
    )
    latest_verdict = live.get("latest_verdict", None)
    judge_state_hash = live.get("judge_state_hash", None)
    sealed = live.get("sealed", False)

    # Phase 2: Determine required next tool from plan state
    required_next = None
    blocked_reason = None
    if plan_state == "draft":
        required_next = "arif_kernel_route"
        blocked_reason = None
    elif plan_state == "planned":
        required_next = "arif_judge"
    elif plan_state == "judge_reviewed":
        required_next = "arif_measure"
    elif plan_state == "approved":
        required_next = "arif_forge"
    elif plan_state == "executed":
        required_next = "arif_seal"
    elif plan_state == "blocked":
        blocked_reason = live.get("blocked_reason", "Plan blocked by governance gate")
        required_next = None

    constitution_id = live.get("constitution_id", "arifos-constitution-v2026.04.26")
    g_score = result_telemetry.get("g_score", ktelemetry.get("g_score", 0.0))
    delta_s = result_telemetry.get("delta_S", ktelemetry.get("delta_S", 0.0))

    return SessionStatus(
        session_id=str(session_id),
        actor_id=str(actor_id),
        constitution_id=str(constitution_id),
        stage=str(stage),
        lane=str(lane),
        sealed=bool(sealed),
        authority=str(authority),
        plan_id=str(plan_id) if plan_id else None,
        plan_state=str(plan_state),
        latest_verdict=str(latest_verdict) if latest_verdict else None,
        judge_state_hash=str(judge_state_hash) if judge_state_hash else None,
        required_next_tool=required_next,
        blocked_reason=str(blocked_reason) if blocked_reason else None,
        g_score=float(g_score),
        delta_s=float(delta_s),
    ).model_dump()


@command_center_app.tool()
def arif_cc_ops_vitals() -> dict:
    """Use this when refreshing the thermodynamic health panel.

    Returns genius score (G), entropy delta (ΔS), human impact load (Ω),
    and paradox tension (Ψ). Read-only diagnostic from real 777_OPS backend.

    Do not use for actual system monitoring outside the Command Center.
    """
    if EVALUATION_MODE:
        state = get_state()
        state.ops_reads += 1
        return OpsVitals().model_dump()

    result = _invoke_handler(_CANONICAL_HANDLERS.get("arif_measure"), mode="vitals")
    return OpsVitals(
        g_score=result.g_score,
        delta_S=result.delta_S,
        omega=result.omega,
        psi_le=result.psi_le,
        status=result.meta.get("status", "OK"),
    ).model_dump()


@command_center_app.tool()
def arif_cc_judge_action(candidate: str) -> dict:
    """Use this when the user submits an action for constitutional review.

    Routes through 444_KERNEL, then calls governed_judge_deliberate which:
      1. Validates session + identity
      2. Calls real 888_JUDGE backend for F1-L13 verdict
      3. Advances the session lifecycle (draft→planned→judged→approved/blocked)
      4. Appends the verdict to VAULT999 hash chain

    Returns: SEAL (approved), SABAR (conditional), HOLD (paused), or VOID (rejected).

    Parameters:
        candidate: Plain-text description of the proposed action.
            Example: "restart the production database" or "deploy v2.3".

    Do not use for final execution — this only returns a verdict.
    """
    state = get_state()
    state.judge_calls += 1
    if not isinstance(candidate, str):
        candidate = str(candidate) if candidate is not None else ""
    candidate = _truncate(candidate.strip(), MAX_CANDIDATE_LENGTH)

    # Phase 2: Route through kernel first
    routing = _route_action(target="arif_judge", task=candidate)
    routing_result = routing.get("result", {})
    routing_path = routing_result.get("path", ["init", "sense", "judge"])

    if EVALUATION_MODE:
        result = judge_candidate(candidate)
        return JudgeVerdict(
            routing_path=routing_path,
            required_next_tool="arif_measure",
            **result,
        ).model_dump()

    # Use governed_judge_deliberate: calls 888_JUDGE + lifecycle advance + vault append
    live = _get_live_session()
    session_id = live.get("session_id", "uninitialized")
    plan_id = live.get("plan_id")
    plan_state = live.get("caller_state", "draft")

    result = governed_judge_deliberate(
        candidate=candidate,
        actor_id="arif",
        session_id=session_id,
        plan_id=plan_id,
        plan_state=plan_state,
    )

    # Map to JudgeVerdict shape
    verdict_code = result.get("verdict", "HOLD")
    risk_tier = result.get("risk_tier", "high")
    human_required = result.get("human_decision_required", verdict_code != "SEAL")

    risk_tier_map = {
        "low": "low",
        "medium": "medium",
        "high": "high",
        "critical": "critical",
    }
    risk_tier = risk_tier_map.get(risk_tier, "high")

    return JudgeVerdict(
        verdict=verdict_code,
        risk_tier=risk_tier,
        human_decision_required=human_required,
        reason=result.get("reason", ""),
        allowed_next=result.get("allowed_next", []),
        forbidden_next=result.get("forbidden_next", []),
        routing_path=routing_path,
        required_next_tool=result.get("required_next_tool"),
    ).model_dump()


@command_center_app.tool()
def arif_cc_forge_dry_run(manifest: str) -> dict:
    """Use this when the user wants to simulate a forge execution.

    Routes through 444_KERNEL, then calls the real 010_FORGE backend in dry_run mode.
    Phase 4 enforcement: requires approved_plan_id + judge_state_hash before execution
    is permitted. Returns a reversibility classification and required verdict.

    Parameters:
        manifest: JSON manifest or plain-text description of the proposed
            build/deploy operation.
            Example: '{"mode": "deploy", "service": "arifosmcp"}'.

    Do not use for real builds without a SEAL verdict and approved plan.
    """
    state = get_state()
    state.forge_dry_runs += 1
    manifest = _truncate(manifest, MAX_MANIFEST_LENGTH)

    # Phase 2: Route through kernel first
    routing = _route_action(target="arif_forge", task=manifest)
    routing_result = routing.get("result", {})
    routing_path = routing_result.get("path", ["init", "sense", "mind"])

    if EVALUATION_MODE:
        risk = classify_risk(manifest)
        reversibility = "uncertain" if risk in {"high", "critical"} else "reversible"
        return ForgeDryRun(
            routing_path=routing_path,
            mode="dry_run",
            would_execute=False,
            manifest_summary=manifest[:120] + ("..." if len(manifest) > 120 else ""),
            reversibility=reversibility,
            required_verdict="SEAL",
            status="simulated",
            plan_state="draft",
        ).model_dump()

    # Phase 4: Enforcement gates via governed_forge_execute
    live = _get_live_session()
    session_id = live.get("session_id", "uninitialized")
    plan_id = live.get("plan_id")
    plan_state = live.get("caller_state", "draft")
    judge_state_hash = live.get("judge_state_hash")
    approved_plan_id = live.get("approved_plan_id")
    judge_verdict = live.get("latest_verdict")

    forge_result = governed_forge_execute(
        manifest=manifest,
        actor_id="arif",
        session_id=session_id,
        plan_id=plan_id,
        judge_verdict=judge_verdict,
        judge_state_hash=judge_state_hash,
        approved_plan_id=approved_plan_id,
        plan_state=plan_state,
        mode="dry_run",
    )

    forge_out = forge_result.get("forge_result") or {}
    status_map = {
        "allowed": "routed",
        "executed": "executed",
        "blocked": "blocked",
        "hold": "hold",
    }
    return ForgeDryRun(
        routing_path=routing_path,
        mode="dry_run",
        would_execute=forge_out.get("would_execute", False),
        manifest_summary=manifest[:120] + ("..." if len(manifest) > 120 else ""),
        reversibility=forge_out.get("reversibility", "uncertain"),
        required_verdict="SEAL",
        status=status_map.get(forge_result.get("status", ""), "hold"),
        plan_id=plan_id,
        plan_state=plan_state,
        judge_state_hash=judge_state_hash,
        approved_plan_id=approved_plan_id,
        blocked_reason=(
            forge_result.get("reason") if forge_result.get("status") != "allowed" else None
        ),
    ).model_dump()


@command_center_app.tool()
def arif_cc_gateway_handshake(target_agent: str) -> dict:
    """Use this when the user wants to initiate a cross-agent A2A handshake.

    Calls the real 666_GATEWAY backend to perform a constitutional handshake
    with the target federation agent. Returns rogue-agent protection status.

    Parameters:
        target_agent: Canonical agent name to handshake with.
            Example: "geox-mcp", "wealth-mcp", "a-forge".

    Do not use for actual A2A mesh routing — the gateway handles that.
    """
    state = get_state()
    state.gateway_handshakes += 1
    if not isinstance(target_agent, str):
        target_agent = str(target_agent) if target_agent is not None else ""
    target_agent = _truncate(target_agent.strip(), MAX_AGENT_NAME_LENGTH)

    # Phase 2: Route through kernel first
    routing = _route_action(target="arif_gateway_connect", task=target_agent)
    routing_result = routing.get("result", {})
    routing_path = routing_result.get("path", ["init", "sense", "mind"])

    if EVALUATION_MODE:
        return GatewayHandshake(
            target_agent=target_agent,
            handshake="simulated",
            constitution_hash_required=True,
            rogue_agent_protection=True,
            status="pending_trust_verification",
            routing_path=routing_path,
        ).model_dump()

    result = _invoke_handler(
        _CANONICAL_HANDLERS.get("arif_gateway_connect"),
        mode="handshake",
        target_agent=target_agent,
        actor_id="arif",
    )
    handshake_ok = result.get("result", {}).get("handshake", "unknown")
    return GatewayHandshake(
        target_agent=target_agent,
        handshake=handshake_ok,
        constitution_hash_required=True,
        rogue_agent_protection=True,
        status="verified" if handshake_ok == "OK" else "pending_trust_verification",
        routing_path=routing_path,
    ).model_dump()


@command_center_app.tool()
def arif_cc_vault_list() -> dict:
    """Use this when refreshing the vault audit panel.

    Reads the real VAULT999 ledger. Returns the last 10 entries with hash-chain
    verification. Read-only. Uses vault_audit.get_vault_audit internally.

    Do not use for retrieving real sealed events — this is the canonical read path.
    """
    if EVALUATION_MODE:
        from arifosmcp.apps.command_center.mock_kernel import (
            MOCK_VAULT_ENTRIES,
        )  # noqa: F401

        return VaultList(entries=MOCK_VAULT_ENTRIES).model_dump()

    audit = get_vault_audit(limit=20)
    entries = [
        VaultEntry(
            id=e.get("entry_id", "unknown"),
            type=e.get("type", "seal"),
            permanent=e.get("permanent", False),
            note=e.get("note", "")[:80],
            timestamp=e.get("timestamp", ""),
            prev_hash=e.get("prev_hash", ""),
        )
        for e in audit.get("entries", [])
    ]
    return VaultList(
        entries=entries,
        total_count=audit.get("total", 0),
        chain_valid=audit.get("chain_valid", False),
    ).model_dump()


@command_center_app.tool()
def arif_cc_vault_dry_seal(payload: str) -> dict:
    """Use this when the user wants to preview a vault seal.

    Routes through 444_KERNEL, then calls the real 999_VAULT backend in dry_run mode.
    Phase 4 enforcement: requires approved_plan_id + judge_state_hash before dry_seal
    is permitted. The payload is not written to the ledger until mode=permanent.

    Parameters:
        payload: JSON event payload to seal.
            Example: '{"session_id": "SEAL-abc", "action": "deploy", "actor": "arif"}'.

    Do not use for permanent seals without explicit human acknowledgment.
    """
    state = get_state()
    state.vault_dry_seals += 1
    if not isinstance(payload, str):
        payload = str(payload) if payload is not None else ""
    payload = _truncate(payload, MAX_PAYLOAD_LENGTH)

    # Phase 2: Route through kernel first
    routing = _route_action(target="arif_seal", task=payload)
    routing_result = routing.get("result", {})
    routing_path = routing_result.get("path", ["init", "sense", "mind"])

    if EVALUATION_MODE:
        return VaultDrySeal(
            routing_path=routing_path,
            mode="dry_seal",
            permanent=False,
            payload_hash_preview=hash_preview(payload),
            status="not_written",
            plan_state="draft",
        ).model_dump()

    # Phase 4: Enforcement gates
    live = _get_live_session()
    plan_id = live.get("plan_id")
    plan_state = live.get("caller_state", "draft")
    judge_state_hash = live.get("judge_state_hash")
    approved_plan_id = live.get("approved_plan_id")

    # Phase 4 enforcement via interceptor
    check = governance_guard(
        action="vault_dry_seal",
        actor_id="arif",
        session_id=live.get("session_id", "uninitialized"),
        payload={"payload": payload},
        plan_state=plan_state,
        judge_state_hash=judge_state_hash,
        approved_plan_id=approved_plan_id,
    )
    if check["status"] != "allowed":
        return VaultDrySeal(
            routing_path=routing_path,
            mode="dry_seal",
            permanent=False,
            payload_hash_preview="__blocked__",
            status=f"enforcement_gate:{check['gate']}",
            plan_id=plan_id,
            plan_state=plan_state,
            judge_state_hash=judge_state_hash,
            approved_plan_id=approved_plan_id,
            blocked_reason=check["reason"],
        ).model_dump()

    # Use real vault_chain for hash preview
    try:
        vault_record = append_vault_record(
            entry_type="vault_dry_seal_preview",
            payload={"payload": payload, "session_id": live.get("session_id", "")},
            permanent=False,
            note=f"dry_seal_preview session={live.get('session_id', '?')}",
            actor_id="arif",
        )
        hash_preview_out = vault_record["payload_hash"]
    except Exception:
        hash_preview_out = hash_preview(payload)

    return VaultDrySeal(
        routing_path=routing_path,
        mode="dry_seal",
        permanent=False,
        payload_hash_preview=hash_preview_out,
        status="preview_generated",
        plan_id=plan_id,
        plan_state=plan_state,
        judge_state_hash=judge_state_hash,
        approved_plan_id=approved_plan_id,
    ).model_dump()


_READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)
_DRY_RUN = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)


@command_center_app.tool(name="session_status")
def session_status() -> dict:
    return arif_cc_session_status()


@command_center_app.tool(name="ops_vitals")
def ops_vitals() -> dict:
    return arif_cc_ops_vitals()


@command_center_app.tool(name="judge_action")
def judge_action(candidate: str) -> dict:
    return arif_cc_judge_action(candidate)


@command_center_app.tool(name="forge_dry_run")
def forge_dry_run(manifest: str) -> dict:
    return arif_cc_forge_dry_run(manifest)


@command_center_app.tool(name="gateway_handshake")
def gateway_handshake(target_agent: str) -> dict:
    return arif_cc_gateway_handshake(target_agent)


@command_center_app.tool(name="vault_list")
def vault_list() -> dict:
    return arif_cc_vault_list()


@command_center_app.tool(name="vault_dry_seal")
def vault_dry_seal(payload: str) -> dict:
    return arif_cc_vault_dry_seal(payload)


_TOOL_ANNOTATIONS = {
    "arif_cc_session_status": _READ_ONLY,
    "arif_cc_ops_vitals": _READ_ONLY,
    "arif_cc_judge_action": _READ_ONLY,
    "arif_cc_forge_dry_run": _DRY_RUN,
    "arif_cc_gateway_handshake": _DRY_RUN,
    "arif_cc_vault_list": _READ_ONLY,
    "arif_cc_vault_dry_seal": _DRY_RUN,
    "session_status": _READ_ONLY,
    "ops_vitals": _READ_ONLY,
    "judge_action": _READ_ONLY,
    "forge_dry_run": _DRY_RUN,
    "gateway_handshake": _DRY_RUN,
    "vault_list": _READ_ONLY,
    "vault_dry_seal": _DRY_RUN,
}

for _key, _comp in command_center_app._local._components.items():
    if _key.startswith("tool:"):
        _name = getattr(_comp, "name", None)
        if _name in _TOOL_ANNOTATIONS:
            _comp.annotations = _TOOL_ANNOTATIONS[_name]


# ---------------------------------------------------------------------------
# Visible UI entry point
# ---------------------------------------------------------------------------


@command_center_app.ui(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False,
    }
)
def command_center() -> PrefabApp:
    """Use this when the user wants to open the arifOS Command Center.

    This is the governed cockpit for constitutional AI operations across the
    arifOS federation (arifOS, A-FORGE, GEOX, WEALTH). It provides tabs for
    session status, thermodynamic vitals, constitutional judgment (888 Judge),
    forge dry-run simulation (010 Forge), cross-agent gateway handshake
    (666 Gateway), and vault audit (999 Vault).

    Do not use for direct tool execution — use the specific canonical tool
    (e.g., arif_judge, arif_measure) when the user asks for
    a single action outside the cockpit context.
    """

    # ── Session Continuity (Eureka 6+7) ─────────────────────────────────────
    # Initialize or recover a constitutional session on every UI open.
    state = get_state()
    sess = state.get_session()
    if sess is None:
        sess = state.init_session(
            actor_id="anonymous",
            intent="arifOS Command Center session",
        )

    # Pre-populate UI state from session anchor
    session_defaults = {
        "session_actor": sess.actor_id,
        "session_constitution": "arifos-constitution-v2026.04.26",
        "session_stage": "000",
        "session_lane": "AGI",
        "session_sealed": "false",
        "session_authority": "human_judge_required_for_consequential_actions",
    }

    # Header
    header = Column(
        children=[
            Heading(content="arifOS Command Center", level=1),
            Text(
                content="One cockpit. Separate chambers. Judge above action.",
                italic=True,
            ),
            Row(
                children=[
                    Badge(
                        label="v0.3 LIVE — 444/888/777/999/010/666 GOVERNANCE",
                        variant="success",
                    ),
                    Badge(label="F1 Amanah Active", variant="success"),
                ],
                gap=2,
            ),
            Separator(spacing=2),
        ],
        gap=2,
    )

    # ---------- Session Tab ----------
    session_tab = Tab(
        title="Session",
        value="session",
        children=[
            Card(
                children=[
                    CardHeader(
                        children=[CardTitle(content="Constitutional Session")],
                    ),
                    CardContent(
                        children=[
                            Column(
                                children=[
                                    Text(content="Actor: {{ session_actor }}", bold=True),
                                    Text(
                                        content="Constitution: {{ session_constitution }}",
                                        bold=True,
                                    ),
                                    Text(content="Stage: {{ session_stage }}", bold=True),
                                    Text(content="Lane: {{ session_lane }}", bold=True),
                                    Text(
                                        content="Authority: {{ session_authority }}",
                                        bold=True,
                                    ),
                                    Badge(
                                        label="{{ session_sealed }}",
                                        variant="{{ session_sealed == 'true' ? 'success' : 'secondary' }}",  # noqa: E501
                                    ),
                                    Button(
                                        label="Refresh Session",
                                        variant="outline",
                                        on_click=CallTool(
                                            "session_status",
                                            on_success=[
                                                SetState(
                                                    "session_actor",
                                                    "{{ $result.actor_id }}",
                                                ),
                                                SetState(
                                                    "session_constitution",
                                                    "{{ $result.constitution_id }}",
                                                ),
                                                SetState(
                                                    "session_stage",
                                                    "{{ $result.stage }}",
                                                ),
                                                SetState("session_lane", "{{ $result.lane }}"),
                                                SetState(
                                                    "session_sealed",
                                                    "{{ $result.sealed }}",
                                                ),
                                                SetState(
                                                    "session_authority",
                                                    "{{ $result.authority }}",
                                                ),
                                            ],
                                        ),
                                    ),
                                ],
                                gap=2,
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

    sense_tab = Tab(
        title="Sense",
        value="sense",
        children=[
            Card(
                children=[
                    CardHeader(children=[CardTitle(content="111_SENSE: Reality Grounding")]),
                    CardContent(
                        children=[
                            Column(
                                children=[
                                    Text(content="Live reality observation results:"),
                                    Text(content="{{ sense_result }}", italic=True),
                                    Button(
                                        label="Refresh Sense",
                                        variant="outline",
                                        on_click=CallTool(
                                            "arif_cc_sense_observe",
                                            args={"mode": "vitals"},
                                            on_success=[SetState("sense_result", "{{ $result }}")],
                                        ),
                                    ),
                                ],
                                gap=2,
                            )
                        ]
                    ),
                ]
            )
        ],
    )

    mind_tab = Tab(
        title="Mind",
        value="mind",
        children=[
            Card(
                children=[
                    CardHeader(children=[CardTitle(content="333_MIND: Symbolic Reasoning")]),
                    CardContent(
                        children=[
                            Column(
                                children=[
                                    Text(content="Reasoning trace:"),
                                    Text(content="{{ mind_result }}", italic=True),
                                    Input(
                                        label="Query",
                                        on_change=SetState("mind_query", "{{ $value }}"),
                                    ),
                                    Button(
                                        label="Reason",
                                        variant="outline",
                                        on_click=CallTool(
                                            "arif_cc_mind_reason",
                                            args={"query": "{{ mind_query }}"},
                                            on_success=[SetState("mind_result", "{{ $result }}")],
                                        ),
                                    ),
                                ],
                                gap=2,
                            )
                        ]
                    ),
                ]
            )
        ],
    )

    heart_tab = Tab(
        title="Heart",
        value="heart",
        children=[
            Card(
                children=[
                    CardHeader(children=[CardTitle(content="666_HEART: Ethical Critique")]),
                    CardContent(
                        children=[
                            Column(
                                children=[
                                    Text(content="Ethical risk scorecard:"),
                                    Text(content="{{ heart_result }}", italic=True),
                                    Input(
                                        label="Target",
                                        on_change=SetState("heart_target", "{{ $value }}"),
                                    ),
                                    Button(
                                        label="Critique",
                                        variant="outline",
                                        on_click=CallTool(
                                            "arif_cc_heart_critique",
                                            args={"target": "{{ heart_target }}"},
                                            on_success=[SetState("heart_result", "{{ $result }}")],
                                        ),
                                    ),
                                ],
                                gap=2,
                            )
                        ]
                    ),
                ]
            )
        ],
    )

    memory_tab = Tab(
        title="Memory",
        value="memory",
        children=[
            Card(
                children=[
                    CardHeader(children=[CardTitle(content="555_MEMORY: Associative Recall")]),
                    CardContent(
                        children=[
                            Column(
                                children=[
                                    Text(content="Retrieved context:"),
                                    Text(content="{{ memory_result }}", italic=True),
                                    Input(
                                        label="Search",
                                        on_change=SetState("memory_query", "{{ $value }}"),
                                    ),
                                    Button(
                                        label="Recall",
                                        variant="outline",
                                        on_click=CallTool(
                                            "arif_cc_memory_recall",
                                            args={"query": "{{ memory_query }}"},
                                            on_success=[SetState("memory_result", "{{ $result }}")],
                                        ),
                                    ),
                                ],
                                gap=2,
                            )
                        ]
                    ),
                ]
            )
        ],
    )

    fetch_tab = Tab(
        title="Fetch",
        value="fetch",
        children=[
            Card(
                children=[
                    CardHeader(children=[CardTitle(content="222_FETCH: Evidence Ingestion")]),
                    CardContent(
                        children=[
                            Column(
                                children=[
                                    Text(content="Last fetch result:"),
                                    Text(content="{{ fetch_result }}", italic=True),
                                    Input(
                                        label="URL",
                                        value="https://arif-fazil.com",
                                        on_change=SetState("fetch_url", "{{ $value }}"),
                                    ),
                                    Button(
                                        label="Fetch Evidence",
                                        variant="outline",
                                        on_click=CallTool(
                                            "arif_cc_evidence_fetch",
                                            args={"url": "{{ fetch_url }}"},
                                            on_success=[SetState("fetch_result", "{{ $result }}")],
                                        ),
                                    ),
                                ],
                                gap=2,
                            )
                        ]
                    ),
                ]
            )
        ],
    )

    # ---------- Ops Tab ----------
    ops_tab = Tab(
        title="Ops",
        value="ops",
        children=[
            Card(
                children=[
                    CardHeader(
                        children=[CardTitle(content="Thermodynamic Vitals")],
                    ),
                    CardContent(
                        children=[
                            Column(
                                children=[
                                    Row(
                                        children=[
                                            Metric(
                                                label="G Score",
                                                value="{{ ops_g }}",
                                                description="Genius coefficient",
                                            ),
                                            Metric(
                                                label="ΔS",
                                                value="{{ ops_delta_s }}",
                                                description="Entropy delta",
                                            ),
                                            Metric(
                                                label="Ω",
                                                value="{{ ops_omega }}",
                                                description="Human impact load",
                                            ),
                                            Metric(
                                                label="Ψ",
                                                value="{{ ops_psi }}",
                                                description="Paradox tension",
                                            ),
                                        ],
                                        gap=4,
                                    ),
                                    Badge(
                                        label="Status: {{ ops_status }}",
                                        variant="{{ ops_status == 'stable' ? 'success' : 'destructive' }}",  # noqa: E501
                                    ),
                                    Button(
                                        label="Refresh Vitals",
                                        variant="outline",
                                        on_click=CallTool(
                                            "ops_vitals",
                                            on_success=[
                                                SetState("ops_g", "{{ $result.g_score }}"),
                                                SetState(
                                                    "ops_delta_s",
                                                    "{{ $result.delta_S }}",
                                                ),
                                                SetState("ops_omega", "{{ $result.omega }}"),
                                                SetState("ops_psi", "{{ $result.psi_le }}"),
                                                SetState("ops_status", "{{ $result.status }}"),
                                            ],
                                        ),
                                    ),
                                ],
                                gap=2,
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

    # ---------- Judge Tab ----------
    judge_tab = Tab(
        title="Judge",
        value="judge",
        children=[
            Card(
                children=[
                    CardHeader(
                        children=[CardTitle(content="888 Judge — Constitutional Review")],
                    ),
                    CardContent(
                        children=[
                            Column(
                                children=[
                                    Text(
                                        content="Describe the candidate action for constitutional review:"  # noqa: E501
                                    ),
                                    Input(
                                        name="judge_candidate",
                                        placeholder="e.g., restart the production database",
                                    ),
                                    Button(
                                        label="Review Action",
                                        variant="secondary",
                                        on_click=CallTool(
                                            "judge_action",
                                            arguments={"candidate": "{{ judge_candidate }}"},
                                            on_success=[
                                                SetState(
                                                    "judge_verdict",
                                                    "{{ $result.verdict }}",
                                                ),
                                                SetState(
                                                    "judge_risk",
                                                    "{{ $result.risk_tier }}",
                                                ),
                                                SetState(
                                                    "judge_reason",
                                                    "{{ $result.reason }}",
                                                ),
                                                SetState(
                                                    "judge_human",
                                                    "{{ $result.human_decision_required }}",
                                                ),
                                            ],
                                        ),
                                    ),
                                    Separator(),
                                    Text(content="Verdict:", bold=True),
                                    Badge(
                                        label="{{ judge_verdict }}",
                                        variant="{{ judge_verdict == 'SEAL' ? 'success' : (judge_verdict == 'SABAR' ? 'warning' : 'destructive') }}",  # noqa: E501
                                    ),
                                    Text(content="Risk Tier: {{ judge_risk }}", bold=True),
                                    Text(
                                        content="Reason: {{ judge_reason }}",
                                        italic=True,
                                    ),
                                    Badge(
                                        label="{{ judge_human == 'true' ? 'Human Decision REQUIRED' : 'No human decision required' }}",  # noqa: E501
                                        variant="{{ judge_human == 'true' ? 'destructive' : 'secondary' }}",  # noqa: E501
                                    ),
                                ],
                                gap=2,
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

    # ---------- Forge Tab ----------
    forge_tab = Tab(
        title="Forge",
        value="forge",
        children=[
            Card(
                children=[
                    CardHeader(
                        children=[CardTitle(content="010 Forge — Metabolic Execution")],
                    ),
                    CardContent(
                        children=[
                            Column(
                                children=[
                                    Badge(label="DRY RUN ONLY", variant="warning"),
                                    Badge(
                                        label="No files changed. No deployment performed.",
                                        variant="secondary",
                                    ),
                                    Textarea(
                                        name="forge_manifest",
                                        placeholder="Paste manifest JSON or description here...",
                                        rows=4,
                                    ),
                                    Button(
                                        label="Dry Run Forge",
                                        variant="outline",
                                        on_click=CallTool(
                                            "forge_dry_run",
                                            arguments={"manifest": "{{ forge_manifest }}"},
                                            on_success=[
                                                SetState("forge_mode", "{{ $result.mode }}"),
                                                SetState(
                                                    "forge_summary",
                                                    "{{ $result.manifest_summary }}",
                                                ),
                                                SetState(
                                                    "forge_reversibility",
                                                    "{{ $result.reversibility }}",
                                                ),
                                                SetState(
                                                    "forge_status",
                                                    "{{ $result.status }}",
                                                ),
                                            ],
                                        ),
                                    ),
                                    Separator(),
                                    Text(content="Mode: {{ forge_mode }}", bold=True),
                                    Text(
                                        content="Summary: {{ forge_summary }}",
                                        italic=True,
                                    ),
                                    Text(
                                        content="Reversibility: {{ forge_reversibility }}",
                                        bold=True,
                                    ),
                                    Badge(
                                        label="Status: {{ forge_status }}",
                                        variant="{{ forge_status == 'simulated' ? 'success' : 'default' }}",  # noqa: E501
                                    ),
                                ],
                                gap=2,
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

    # ---------- Gateway Tab ----------
    gateway_tab = Tab(
        title="Gateway",
        value="gateway",
        children=[
            Card(
                children=[
                    CardHeader(
                        children=[CardTitle(content="666 Gateway — A2A Mesh")],
                    ),
                    CardContent(
                        children=[
                            Column(
                                children=[
                                    Text(content="Target agent for constitutional handshake:"),
                                    Input(
                                        name="gateway_target",
                                        placeholder="e.g., geox-mcp, wealth-mcp, a-forge",
                                    ),
                                    Button(
                                        label="Simulate Handshake",
                                        variant="outline",
                                        on_click=CallTool(
                                            "gateway_handshake",
                                            arguments={"target_agent": "{{ gateway_target }}"},
                                            on_success=[
                                                SetState(
                                                    "gw_target",
                                                    "{{ $result.target_agent }}",
                                                ),
                                                SetState("gw_status", "{{ $result.status }}"),
                                                SetState(
                                                    "gw_hash_req",
                                                    "{{ $result.constitution_hash_required }}",
                                                ),
                                                SetState(
                                                    "gw_rogue",
                                                    "{{ $result.rogue_agent_protection }}",
                                                ),
                                            ],
                                        ),
                                    ),
                                    Separator(),
                                    Text(content="Target: {{ gw_target }}", bold=True),
                                    Text(content="Status: {{ gw_status }}", italic=True),
                                    Badge(
                                        label="Hash Required: {{ gw_hash_req }}",
                                        variant="{{ gw_hash_req == 'true' ? 'success' : 'warning' }}",  # noqa: E501
                                    ),
                                    Badge(
                                        label="Rogue Protection: {{ gw_rogue }}",
                                        variant="{{ gw_rogue == 'true' ? 'success' : 'warning' }}",
                                    ),
                                ],
                                gap=2,
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

    # ---------- Vault Tab ----------
    vault_tab = Tab(
        title="Vault",
        value="vault",
        children=[
            Card(
                children=[
                    CardHeader(
                        children=[CardTitle(content="999 Vault — Immutable Ledger")],
                    ),
                    CardContent(
                        children=[
                            Column(
                                children=[
                                    Badge(
                                        label="Dry seal only. No permanent ledger write.",
                                        variant="warning",
                                    ),
                                    Button(
                                        label="List Mock Vault",
                                        variant="outline",
                                        on_click=CallTool(
                                            "vault_list",
                                            on_success=[
                                                SetState(
                                                    "vault_entries_json",
                                                    "{{ $result.entries }}",
                                                ),
                                            ],
                                        ),
                                    ),
                                    Text(
                                        content="Mock Entries (raw): {{ vault_entries_json }}",
                                        code=True,
                                    ),
                                    Separator(),
                                    Text(content="Payload to dry-seal:"),
                                    Textarea(
                                        name="vault_payload",
                                        placeholder="Enter payload to hash and preview...",
                                        rows=3,
                                    ),
                                    Button(
                                        label="Dry Seal",
                                        variant="secondary",
                                        on_click=CallTool(
                                            "vault_dry_seal",
                                            arguments={"payload": "{{ vault_payload }}"},
                                            on_success=[
                                                SetState("seal_mode", "{{ $result.mode }}"),
                                                SetState(
                                                    "seal_hash",
                                                    "{{ $result.payload_hash_preview }}",
                                                ),
                                                SetState(
                                                    "seal_permanent",
                                                    "{{ $result.permanent }}",
                                                ),
                                                SetState(
                                                    "seal_status",
                                                    "{{ $result.status }}",
                                                ),
                                            ],
                                        ),
                                    ),
                                    Separator(),
                                    Text(content="Mode: {{ seal_mode }}", bold=True),
                                    Text(
                                        content="Hash Preview: {{ seal_hash }}",
                                        code=True,
                                    ),
                                    Badge(
                                        label="Permanent: {{ seal_permanent }}",
                                        variant="{{ seal_permanent == 'true' ? 'destructive' : 'success' }}",  # noqa: E501
                                    ),
                                    Text(content="Status: {{ seal_status }}", italic=True),
                                ],
                                gap=2,
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

    # Main tabs container
    chambers = Tabs(
        value="session",
        children=[
            session_tab,
            sense_tab,
            fetch_tab,
            mind_tab,
            heart_tab,
            memory_tab,
            ops_tab,
            judge_tab,
            forge_tab,
            gateway_tab,
            vault_tab,
        ],
    )

    return PrefabApp(
        title="arifOS Command Center",
        view=Column(
            children=[header, chambers],
            gap=4,
        ),
        state={
            # Session defaults (populated from constitutional session anchor)
            **session_defaults,
            # Ops defaults
            "ops_g": "—",
            "ops_delta_s": "—",
            "ops_omega": "—",
            "ops_psi": "—",
            "ops_status": "—",
            # Judge defaults
            "judge_verdict": "—",
            "judge_risk": "—",
            "judge_reason": "—",
            "judge_human": "false",
            # Forge defaults
            "forge_mode": "—",
            "forge_summary": "—",
            "forge_reversibility": "—",
            "forge_status": "—",
            # Gateway defaults
            "gw_target": "—",
            "gw_status": "—",
            "gw_hash_req": "false",
            "gw_rogue": "false",
            # Vault defaults
            "vault_entries_json": "[]",
            "seal_mode": "—",
            "seal_hash": "—",
            "seal_permanent": "false",
            "seal_status": "—",
            # New tool states
            "sense_result": "—",
            "fetch_result": "—",
            "mind_result": "—",
            "heart_result": "—",
            "reply_result": "—",
            "memory_result": "—",
        },
    )


# Patch widget domain for ChatGPT MCP Apps sandbox compliance
for _key, _comp in command_center_app._local._components.items():
    if _key.startswith("tool:") and getattr(_comp, "name", None) == "command_center":
        _comp.meta.setdefault("ui", {})["domain"] = "https://arifosmcp.arif-fazil.com"
        break


def _register(mcp: FastMCP) -> None:
    """Mount arifOS Command Center onto the platform FastMCP server."""
    mcp.add_provider(command_center_app)
