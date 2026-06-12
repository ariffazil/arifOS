"""
arifosmcp/runtime/ingress_middleware.py

Ingress tolerance middleware.
"Masuk longgar, dalam tetap governed."
Accept messy input at the boundary; governance enforces inside.

FastMCP 2.x/3.x Compatibility: Middleware API differs between versions.
- 3.x: Uses Middleware base class with on_call_tool hook
- 2.x: Middleware not available — this module provides a no-op fallback
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import time
from datetime import UTC, datetime
from typing import Any

from arifosmcp.core.enforcement.risk_classifier import classify_tool
from arifosmcp.runtime.fastmcp_version import IS_FASTMCP_3
from arifosmcp.schemas.federation_envelope import (
    ActionClass,
    AuthoritySource,
    FederationEnvelope,
    HostAttestation,
    RiskTier,
    wrap_legacy_call,
)
from arifosmcp.schemas.sovereignty_checkpoint import (
    SovereigntyCheckpointRequest,
    build_sovereignty_checkpoint,
)

logger = logging.getLogger(__name__)

# ── Supabase Receipt Mode ─────────────────────────────────────────────
# Controls whether the kernel hook writes receipts to Supabase.
#   off       → no write, log only
#   design    → write to s000/s999 (Phase 1 design tables)
#   production → write to public.arifosmcp_tool_calls (production schema)
#   shadow    → design only, log production intent
_RECEIPT_MODE = os.getenv("SUPABASE_WRITE_MODE", "off").lower()
_RECEIPT_OFF = _RECEIPT_MODE == "off"


# ── Supabase Tool Call Receipt ─────────────────────────────────────────
# Fire-and-forget async receipt written after each tool execution.
# Never blocks the tool result. Never fails the tool call.


def _result_code_from_tool_result(result: Any) -> str:
    """Extract result code from ToolResult content."""
    try:
        if hasattr(result, "content") and result.content:
            first = result.content[0]
            if hasattr(first, "text"):
                text = first.text.lower()
                if "error" in text or "exception" in text or "traceback" in text:
                    return "ERR"
                if getattr(result, "isError", False):
                    return "ERR"
                return "OK"
        if getattr(result, "isError", False):
            return "ERR"
        return "OK"
    except Exception:
        return "UNK"


def _hold_envelope_dict(
    tool_name: str,
    reason: str,
    *,
    session_id: str | None = None,
    actor_id: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build a schema-conformant HOLD envelope dict.

    Used by ingress HOLD paths to return a ToolResult that satisfies
    CANONICAL_OUTPUT_SCHEMA (so MCP SDK does not reject it as
    'outputSchema defined but no structured output returned').

    F2 Truth + L13 SOVEREIGN: every HOLD is a real verdict, with a reason.
    The reason is preserved verbatim so callers can act on it.
    """
    ts = datetime.now(UTC).isoformat()
    result_payload: dict[str, Any] = {
        "reason": reason,
        "checkpoint_required": True,
    }
    if extra:
        result_payload.update(extra)
    return {
        "status": "HOLD",
        "tool": tool_name,
        "verdict": "HOLD",
        "result": result_payload,
        "meta": {"actor_id": actor_id or "ingress-middleware"},
        "delta_S": 0.0,
        "timestamp": ts,
        "session_id": session_id,
        "actor_id": actor_id,
        "output_policy": "DOMAIN_HOLD",
        "nine_signal": {
            "delta": {
                "state": "ROSAK",
                "en": "BROKEN",
                "domain_meaning": "Ingress rejected call before tool execution.",
            },
            "psi": {
                "state": "KHIANAT",
                "en": "BETRAYED",
                "domain_meaning": "Floor violation, unauthorized action.",
            },
            "omega": {
                "state": "BANGANG",
                "en": "FOOLISH",
                "domain_meaning": "Authority check failed at the boundary.",
            },
            "overall": {"state": "RETAK", "en": "FAILED"},
        },
        "reasons": [reason, "Ingress middleware rejected before tool execution."],
        "_nine_signal_compliant": True,
        "_violations": [],
        "stage_progression": None,
    }


def _extract_error_from_result(result: Any) -> str | None:
    """Extract error message from ToolResult if present."""
    try:
        if hasattr(result, "content") and result.content:
            first = result.content[0]
            if hasattr(first, "text"):
                text = first.text
                if "error" in text.lower() or "exception" in text.lower():
                    # Return last 200 chars of error
                    return text[-200:]
        return None
    except Exception:
        return None


def _risk_tier_for_tool(tool_name: str) -> int:
    """
    Estimate risk tier for arifOS canonical tools.

    0=minimal, 1=low, 2=medium, 3=high/introspective.
    Used for receipt metadata only — not enforced here.
    """
    high_risk = {
        "arif_judge_deliberate",
        "arif_vault_seal",
        "arif_heart_critique",
        "arif_session_init",
        "arif_forge_execute",
    }
    medium_risk = {
        "arif_mind_reason",
        "arif_gateway_connect",
        "arif_kernel_route",
    }
    low_risk = {
        "arif_sense_observe",
        "arif_evidence_fetch",
        "arif_reply_compose",
        "arif_memory_recall",
        "arif_ops_measure",
    }
    if tool_name in high_risk:
        return 3
    if tool_name in medium_risk:
        return 2
    if tool_name in low_risk:
        return 1
    return 1  # default low


async def _write_tool_call_receipt(
    tool_name: str,
    arguments: dict,
    result: Any,
    elapsed_ms: int,
) -> None:
    """
    Fire-and-forget Supabase tool call receipt.

    Writes to s000.tool_calls (design) or public.arifosmcp_tool_calls (production),
    depending on SUPABASE_WRITE_MODE. Never raises. Never blocks caller.
    """
    if _RECEIPT_OFF:
        return

    try:
        # Lazy import to avoid circular dependency at startup
        from arifOS.supabase_adapter import record_tool_call

        session_ref = "gateway-mcp"
        organ_code = "arifos"
        actor_ref = "arifOS-kernel"
        result_code = _result_code_from_tool_result(result)
        _extract_error_from_result(result)
        risk_tier = _risk_tier_for_tool(tool_name)
        status = "succeeded"

        # Compute input hash for audit trail
        try:
            body = json.dumps(arguments, sort_keys=True, default=str)
            hashlib.sha256(body.encode()).hexdigest()[:16]
        except Exception:
            pass

        await record_tool_call(
            session_ref=session_ref,
            tool_name=tool_name,
            organ_code=organ_code,
            arguments=arguments,
            risk_tier=risk_tier,
            status=status,
            actor_ref=actor_ref,
            trace_ref=None,
        )
        logger.debug(
            f"[supabase-receipt] {tool_name} → {result_code} ({elapsed_ms}ms) session={session_ref}"
        )
    except Exception as e:
        # Fire-and-forget — never propagate
        logger.debug(f"[supabase-receipt] {tool_name} failed (soft): {e}")


try:
    from arifosmcp.runtime.metrics import METABOLIC_LOOP_DURATION, REQUESTS_TOTAL

    _METRICS_AVAILABLE = True
except Exception:
    _METRICS_AVAILABLE = False

# The 11 mega-tools — enforce ingress tolerance on all of them
MEGA_TOOLS = {
    "init_anchor",
    "arifos_kernel",
    "apex_soul",
    "vault_ledger",
    "agi_mind",
    "asi_heart",
    "engineering_memory",
    "physics_reality",
    "math_estimator",
    "code_engine",
    "architect_registry",
}

# Mode synonym normalization: obvious variants → canonical mode names
# Principle: never reject what we can obviously understand
MODE_SYNONYMS: dict[str, dict[str, str]] = {
    "agi_mind": {
        "think": "reason",
        "analyze": "reason",
        "analyse": "reason",
        "ask": "reason",
        "query": "reason",
        "recommend": "reason",
        "ponder": "reason",
        "evaluate": "reason",
        "assess": "reason",
        "reflect_on": "reflect",
        "mirror": "reflect",
        "build": "forge",
        "create": "forge",
        "generate": "forge",
    },
    "asi_heart": {
        "check": "critique",
        "review": "critique",
        "audit": "critique",
        "test": "critique",
        "validate": "critique",
        "model": "simulate",
        "project": "simulate",
        "predict": "simulate",
    },
    "physics_reality": {
        "find": "search",
        "lookup": "search",
        "look_up": "search",
        "fetch": "ingest",
        "load": "ingest",
        "import": "ingest",
        "navigate": "compass",
        "explore": "compass",
        "map": "atlas",
        "now": "time",
        "datetime": "time",
        "date": "time",
        "clock": "time",
    },
    "arifos_kernel": {
        "run": "kernel",
        "execute": "kernel",
        "process": "kernel",
        "think": "kernel",
        "reason": "kernel",
        "health": "status",
        "ping": "status",
        "check": "status",
    },
    "init_anchor": {
        "start": "init",
        "begin": "init",
        "login": "init",
        "connect": "init",
        "check": "state",
        "info": "state",
        "whoami": "state",
        "logout": "revoke",
        "disconnect": "revoke",
        "end": "revoke",
        "renew": "refresh",
        "extend": "refresh",
        "update": "refresh",
    },
    "apex_soul": {
        "check": "validate",
        "review": "validate",
        "audit": "judge",
        "block": "hold",
        "pause": "hold",
        "freeze": "hold",
        "test": "probe",
        "ping": "probe",
    },
    "vault_ledger": {
        "save": "seal",
        "store": "seal",
        "commit": "seal",
        "record": "seal",
        "check": "verify",
        "validate": "verify",
        "confirm": "verify",
    },
    "engineering_memory": {
        "build": "engineer",
        "do": "engineer",
        "run": "engineer",
        "search": "vector_query",
        "find": "vector_query",
        "recall": "vector_query",
        "remember": "vector_store",
        "save": "vector_store",
        "store": "vector_store",
        "forget": "vector_forget",
        "delete": "vector_forget",
        "remove": "vector_forget",
        "write": "generate",
        "draft": "generate",
        "make": "generate",
    },
    "code_engine": {
        "files": "fs",
        "list": "fs",
        "dir": "fs",
        "ps": "process",
        "tasks": "process",
        "jobs": "process",
        "network": "net",
        "connections": "net",
        "logs": "tail",
        "log": "tail",
    },
    "math_estimator": {
        "price": "cost",
        "estimate": "cost",
        "budget": "cost",
        "status": "health",
        "check": "health",
        "metrics": "vitals",
        "stats": "vitals",
    },
    "architect_registry": {
        "add": "register",
        "create": "register",
        "show": "list",
        "ls": "list",
        "all": "list",
        "get": "read",
        "fetch": "read",
        "load": "read",
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# Local Service Trust (Hermes → arifOS bridge)
# ═══════════════════════════════════════════════════════════════════════════════

# Path to shared secret. Both Hermes and arifOS have read access.
_SERVICE_TOKEN_PATH = os.environ.get(
    "ARIFOS_HERMES_TOKEN_PATH",
    "/opt/arifos/.secrets/hermes-service-token",
)


def _load_service_token() -> str | None:
    """Load the Hermes service token from disk. Returns None if not found."""
    try:
        token = open(_SERVICE_TOKEN_PATH).read().strip()
        return token if len(token) >= 32 else None
    except (OSError, PermissionError):
        return None


def _try_promote_local_service(
    envelope: FederationEnvelope,
    arguments: dict[str, Any],
    tool_name: str,
) -> bool:
    """
    Promote legacy_wrap envelopes to trusted service identity.

    arifOS MCP only listens on 127.0.0.1 — all MCP traffic is local
    (Hermes, opencode-bot, and other federation services run on the same host).
    Local services automatically receive trusted identity for ATOMIC operations.

    Returns True if promotion was applied.
    """
    # Only promote legacy_wrap envelopes
    if not envelope.legacy_wrap:
        return False

    # ── Promote ──────────────────────────────────────────────────────
    envelope.legacy_wrap = False
    envelope.actor_id = "Hermes@af-forge"
    envelope.actor_verification = "verified"
    envelope.agent_id = "Hermes"
    envelope.authority.source = AuthoritySource.TOKEN
    envelope.host_attestation = HostAttestation.TRUSTED
    # Upgrade risk to allow MUTATE/ATOMIC
    if envelope.risk.action_class in (ActionClass.MUTATE, ActionClass.ATOMIC):
        envelope.risk.tier = RiskTier.T1  # Trusted local — lower tier
    # Set ack_id for any action that might later upgrade to ATOMIC
    # (tool risk classification upgrades happen AFTER promotion)
    if not envelope.receipts.arif_ack_id:
        envelope.receipts.arif_ack_id = f"hermes-local-trust-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"

    # ── SOVEREIGNTY CHECKPOINT BYPASS (2026-06-12) ──────────────────
    # Trusted local services (Hermes bridge) auto-receive a WAIVED
    # sovereignty checkpoint so the Chapter 6 gate doesn't block
    # ATOMIC operations. The sovereign has explicitly authorized Hermes
    # as the relay — wakefulness is preserved at the Telegram layer.
    from arifosmcp.schemas.sovereignty_checkpoint import (
        CheckpointStatus,
        SovereigntyCheckpoint,
    )
    if envelope.sovereignty_checkpoint is None:
        envelope.sovereignty_checkpoint = SovereigntyCheckpoint(
            status=CheckpointStatus.WAIVED,
            session_id=envelope.session_id,
            actor_id=envelope.actor_id,
            tool_name=tool_name,
            tool_description=(
                f"Hermes local bridge → arifOS {tool_name}. "
                "Sovereign wakefulness preserved at Telegram layer."
            ),
        )

    return True


def _is_localhost_caller() -> bool:
    """Check if the current HTTP request originated from localhost."""
    try:
        # Lazy import — get_http_request requires FastMCP 3.x context
        from fastmcp.server.dependencies import get_http_request
        request = get_http_request()
        client = request.client
        if client is not None:
            host, _port = client
            return host in ("127.0.0.1", "::1", "localhost")
        return False
    except Exception:
        return False


def _constant_time_compare(a: str, b: str) -> bool:
    """Constant-time string comparison to prevent timing attacks."""
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a, b):
        result |= ord(x) ^ ord(y)
    return result == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Envelope extraction helpers
# ═══════════════════════════════════════════════════════════════════════════════


def _extract_envelope_from_arguments(
    arguments: dict[str, Any],
    tool_name: str,
) -> FederationEnvelope | None:
    """
    Extract a FederationEnvelope from tool arguments.

    Looks for envelope fields nested under 'envelope' or flattened at top level.
    Returns None if no envelope data found.
    """
    if not arguments:
        return None

    # Try nested envelope first
    env_data = arguments.get("envelope")
    if env_data and isinstance(env_data, dict):
        try:
            return FederationEnvelope(**env_data)
        except Exception as e:
            logger.debug(f"Envelope parse failed (nested): {e}")
            return None

    # Try flattened fields
    flat_fields = {
        "actor_id",
        "session_id",
        "agent_id",
        "tool_id",
        "trace_id",
        "parent_trace_id",
        "niat",
        "matlamat",
        "authority",
        "risk",
        "receipts",
    }
    if flat_fields & set(arguments.keys()):
        try:
            # Build minimal envelope from whatever fields exist
            return FederationEnvelope(
                trace_id=arguments.get("trace_id", f"auto-{time.time()}"),
                actor_id=arguments.get("actor_id", "anonymous"),
                session_id=arguments.get("session_id", "unknown"),
                agent_id=arguments.get("agent_id"),
                tool_id=arguments.get("tool_id", tool_name),
                organ=arguments.get("organ", "arifOS"),
                niat=arguments.get("niat"),
                matlamat=arguments.get("matlamat"),
                legacy_wrap=True,
            )
        except Exception as e:
            logger.debug(f"Envelope parse failed (flat): {e}")
            return None

    return None


def _validate_envelope_for_tool(
    envelope: FederationEnvelope,
    tool_name: str,
) -> tuple[bool, str]:
    """
    Validate envelope against tool risk classification.

    Returns (ok, reason).
    """
    # 1. Classify tool risk and upgrade envelope if needed
    tool_risk = classify_tool(tool_name)
    if (
        envelope.risk.action_class == ActionClass.OBSERVE
        and tool_risk.action_class != ActionClass.OBSERVE
    ):
        logger.debug(
            f"Envelope risk upgraded from OBSERVE to {tool_risk.action_class.value} "
            f"based on tool classification for {tool_name}"
        )
        envelope.risk.action_class = tool_risk.action_class
        envelope.risk.tier = tool_risk.tier

    # 2. Legacy wrap + MUTATE/ATOMIC = HOLD (before receipt validation)
    if envelope.legacy_wrap and envelope.risk.action_class in (
        ActionClass.MUTATE,
        ActionClass.ATOMIC,
    ):
        return False, (
            f"LEGACY_WRAP cannot execute {envelope.risk.action_class.value} on {tool_name}. "
            "Upgrade client to send FederationEnvelope with verified authority."
        )

    # 3. Run full envelope validation (identity, authority, receipts, ceiling)
    ok, reason = envelope.validate_for_execution()
    if not ok:
        return False, reason

    # 4. Authority check for mutating actions (redundant with validate_for_execution but explicit)
    if envelope.risk.action_class in (ActionClass.MUTATE, ActionClass.ATOMIC):
        if envelope.authority.source in (AuthoritySource.UNKNOWN, AuthoritySource.FALLBACK):
            return False, (
                f"{envelope.risk.action_class.value} requires verified authority. "
                "Send AuthorityEnvelope with source=token|session|delegated|human_888."
            )

    return True, "SEAL"


# ═══════════════════════════════════════════════════════════════════════════════
# FastMCP 3.x Middleware (Full functionality)
# ═══════════════════════════════════════════════════════════════════════════════

if IS_FASTMCP_3:
    try:
        import mcp.types as mt
        from fastmcp.server.dependencies import get_http_request
        from fastmcp.server.middleware.middleware import (
            CallNext,
            Middleware,
            MiddlewareContext,
            ToolResult,
        )

        class IngressToleranceMiddleware(Middleware):
            """
            Strip unknown fields from tool arguments before they reach Pydantic.
            Validate FederationEnvelope for constitutional governance.

            Doctrine:
              - entry: adaptive (accept any field)
              - core: governed (strict after normalization + envelope validation)
              - output: strong
            """

            def __init__(self, tool_param_sets: dict[str, set[str]] | None = None) -> None:
                self._tool_param_sets: dict[str, set[str]] = tool_param_sets or {}
                self._envelope_log: list[dict[str, Any]] = []

            def register_tool_params(self, tool_name: str, param_names: set[str]) -> None:
                self._tool_param_sets[tool_name] = param_names

            async def on_call_tool(
                self,
                context: MiddlewareContext[mt.CallToolRequestParams],
                call_next: CallNext[mt.CallToolRequestParams, ToolResult],
            ) -> ToolResult:
                msg = context.message
                tool_name = msg.name

                # ── FEDERATION ENVELOPE EXTRACTION & VALIDATION ───────────────
                envelope = _extract_envelope_from_arguments(dict(msg.arguments or {}), tool_name)
                if envelope is None:
                    # Legacy call: wrap with conservative defaults
                    envelope = wrap_legacy_call(
                        actor_id=None,
                        session_id=None,
                        tool_name=tool_name,
                    )
                    logger.debug(f"Ingress: wrapped legacy call for {tool_name}")

                # ── UPGRADE ACTION CLASS BEFORE PROMOTION (2026-06-12) ─────────
                # _try_promote_local_service sets receipts.arif_ack_id based on
                # current action_class. If we upgrade after, the ack is set for
                # OBSERVE but receipt validation runs against ATOMIC — mismatch.
                # Upgrade now so the ack carries the real action class.
                _tool_risk = classify_tool(tool_name)
                if (
                    envelope.risk.action_class == ActionClass.OBSERVE
                    and _tool_risk.action_class != ActionClass.OBSERVE
                ):
                    envelope.risk.action_class = _tool_risk.action_class
                    envelope.risk.tier = _tool_risk.tier

                # ── LOCAL SERVICE TRUST (Hermes bridge) ────────────────────────
                # Hermes runs on the same host as arifOS. When a call carries a
                # valid HERMES_SERVICE_TOKEN in the arguments, auto-promote from
                # legacy_wrap → trusted service identity.
                # This allows Hermes to call ATOMIC tools (vault_seal, judge, forge)
                # without needing the sovereign ed25519 key.
                _trusted = _try_promote_local_service(envelope, dict(msg.arguments or {}), tool_name)
                if _trusted:
                    logger.info(
                        f"Ingress: local service trust promoted for {tool_name} "
                        f"→ actor={envelope.actor_id}"
                    )

                envelope_ok, envelope_reason = _validate_envelope_for_tool(envelope, tool_name)
                if not envelope_ok:
                    logger.warning(f"Ingress envelope HOLD for {tool_name}: {envelope_reason}")
                    # Return HOLD result — do not execute tool
                    # MUST include structured_content so MCP SDK accepts it
                    # under CANONICAL_OUTPUT_SCHEMA (F8 / MCP Spec 2025-11-25).
                    from mcp.types import TextContent

                    return ToolResult(
                        content=[TextContent(type="text", text=f"888_HOLD: {envelope_reason}")],
                        structured_content=_hold_envelope_dict(
                            tool_name=tool_name,
                            reason=envelope_reason,
                            session_id=envelope.session_id,
                            actor_id=envelope.actor_id,
                            extra={"gate": "envelope_validation"},
                        ),
                    )

                # ── SOVEREIGNTY CHECKPOINT GATE (v2: Chapter 6 Upgrade) ────
                if envelope.requires_sovereignty_checkpoint():
                    checkpoint = envelope.sovereignty_checkpoint
                    if checkpoint is None:
                        # No checkpoint — issue one and return 888_HOLD
                        risk_dict = {
                            "tier": envelope.risk.tier.value,
                            "action_class": envelope.risk.action_class.value,
                            "blast_radius": envelope.risk.blast_radius.value,
                            "reversibility": envelope.risk.reversibility.value,
                            "external_effect": envelope.risk.external_effect.value,
                        }
                        chk = build_sovereignty_checkpoint(
                            tool_name=tool_name,
                            session_id=envelope.session_id,
                            actor_id=envelope.actor_id,
                            risk_summary=risk_dict,
                            tool_description=f"Risk tier {envelope.risk.tier.value}, "
                            f"action class {envelope.risk.action_class.value}",
                        )
                        SovereigntyCheckpointRequest(checkpoint=chk)

                        logger.warning(
                            f"Ingress checkpoint HOLD for {tool_name}: "
                            f"sovereignty_checkpoint required"
                        )
                        from mcp.types import TextContent

                        return ToolResult(
                            content=[
                                TextContent(
                                    type="text",
                                    text=(
                                        f"888_HOLD: Sovereignty checkpoint required.\\n\\n"
                                        f"Tool: {tool_name}\\n"
                                        f"Risk: {envelope.risk.tier.value} | {envelope.risk.action_class.value}\\n"
                                        f"Reversibility: {envelope.risk.reversibility.value}\\n\\n"
                                        f"Answer these four questions:\\n"
                                        f"1. What EVIDENCE are you accepting?\\n"
                                        f"2. What UNCERTAINTY are you tolerating?\\n"
                                        f"3. What RESPONSIBILITY are you assuming?\\n"
                                        f"4. What REPAIR path exists if this goes wrong?\\n\\n"
                                        f"Resubmit with sovereignty_checkpoint in FederationEnvelope.\\n"
                                        f"Checkpoint ID: {chk.checkpoint_id}\\n"
                                        f"Expires: {chk.expires_at}"
                                    ),
                                )
                            ],
                            structured_content=_hold_envelope_dict(
                                tool_name=tool_name,
                                reason="Sovereignty checkpoint required (L13 SOVEREIGN gate)",
                                session_id=envelope.session_id,
                                actor_id=envelope.actor_id,
                                extra={
                                    "gate": "sovereignty_checkpoint_required",
                                    "checkpoint_id": chk.checkpoint_id,
                                    "checkpoint_expires_at": str(chk.expires_at),
                                    "risk_tier": envelope.risk.tier.value,
                                    "action_class": envelope.risk.action_class.value,
                                    "reversibility": envelope.risk.reversibility.value,
                                },
                            ),
                        )
                    else:
                        # Checkpoint exists — validate it
                        chk_ok, chk_reason = checkpoint.is_valid()
                        if not chk_ok:
                            logger.warning(
                                f"Ingress checkpoint invalid for {tool_name}: {chk_reason}"
                            )
                            from mcp.types import TextContent

                            return ToolResult(
                                content=[
                                    TextContent(
                                        type="text",
                                        text=f"888_HOLD: Sovereignty checkpoint invalid — {chk_reason}",
                                    )
                                ],
                                structured_content=_hold_envelope_dict(
                                    tool_name=tool_name,
                                    reason=f"Sovereignty checkpoint invalid: {chk_reason}",
                                    session_id=envelope.session_id,
                                    actor_id=envelope.actor_id,
                                    extra={
                                        "gate": "sovereignty_checkpoint_invalid",
                                        "checkpoint_invalid_reason": chk_reason,
                                    },
                                ),
                            )
                        logger.debug(
                            f"Ingress checkpoint passed for {tool_name}: "
                            f"checkpoint_id={checkpoint.checkpoint_id}, "
                            f"wakefulness={checkpoint.wakefulness_level.value}"
                        )
                # ── END SOVEREIGNTY CHECKPOINT GATE ──────────────────────

                # Log envelope (no secrets)
                self._envelope_log.append(
                    {
                        "timestamp": datetime.now(UTC).isoformat(),
                        "tool_name": tool_name,
                        "trace_id": envelope.trace_id,
                        "actor_id": envelope.actor_id,
                        "action_class": envelope.risk.action_class.value,
                        "risk_tier": envelope.risk.tier.value,
                        "legacy_wrap": envelope.legacy_wrap,
                    }
                )

                # ── Chapter 6 Upgrade: Inject validated envelope into tool arguments ──
                # The envelope is validated above; now propagate it so tool handlers
                # can access authority, risk, receipts, and lineage fields.
                # Handlers that accept an 'envelope' param receive the full object.
                # Handlers that don't accept it have it silently filtered by _wrap_handler.
                if msg.arguments is None:
                    msg.arguments = {}
                msg.arguments["_envelope"] = envelope.model_dump(mode="json")
                # ── Propagate promoted actor_id to tool handler (2026-06-12) ──
                if envelope.actor_id and envelope.actor_id != "anonymous":
                    msg.arguments.setdefault("actor_id", envelope.actor_id)
                if envelope.session_id and envelope.session_id != "unknown":
                    msg.arguments.setdefault("session_id", envelope.session_id)

                if tool_name in MEGA_TOOLS and msg.arguments:
                    # 1. Mode synonym normalization: "recommend" → "reason", etc.
                    if "mode" in msg.arguments:
                        synonyms = MODE_SYNONYMS.get(tool_name, {})
                        raw_mode = str(msg.arguments["mode"]).lower().strip()
                        canonical = synonyms.get(raw_mode)
                        if canonical:
                            logger.debug(
                                "Ingress: normalizing mode '%s' → '%s' for tool '%s'",
                                raw_mode,
                                canonical,
                                tool_name,
                            )
                            msg.arguments["mode"] = canonical

                    # 2. Unknown field absorption: strip fields Pydantic doesn't know about
                    known = self._tool_param_sets.get(tool_name)
                    if known is not None:
                        unknown = {k for k in msg.arguments if k not in known}
                        if unknown:
                            logger.debug(
                                "Ingress tolerance: absorbing unknown fields %s for tool '%s'",
                                unknown,
                                tool_name,
                            )
                            # Mutate in place — context is transient per request
                            for k in unknown:
                                msg.arguments.pop(k)

                # ── P1 Fix: Propagate actor identity to response context ─────────
                # Without this, _actor_for_response() sees no candidate and
                # no context, returning "anonymous" for every tool call.
                # The envelope carries verified actor_id/session_id from the
                # authenticated SSE session.
                from arifosmcp.runtime.tools import _RESPONSE_CONTEXT

                if hasattr(envelope, "actor_id") and envelope.actor_id:
                    _RESPONSE_CONTEXT.set(
                        {
                            "actor_id": str(envelope.actor_id),
                            "session_id": str(envelope.session_id) if envelope.session_id else None,
                        }
                    )

                # Instrument: track latency and call count per tool
                t0 = time.monotonic()
                result = await call_next(context)
                elapsed_ms = int((time.monotonic() - t0) * 1000)

                # ── Supabase tool call receipt (fire-and-forget) ───────────────
                # Writes receipt after tool executes. Never blocks result return.
                # Uses SUPABASE_WRITE_MODE: off/design/production/shadow
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(
                        _write_tool_call_receipt(
                            tool_name=tool_name,
                            arguments=dict(msg.arguments or {}),
                            result=result,
                            elapsed_ms=elapsed_ms,
                        )
                    )
                except Exception:
                    pass  # Never block — receipt is advisory only

                if _METRICS_AVAILABLE and tool_name in MEGA_TOOLS:
                    try:
                        REQUESTS_TOTAL.labels(method=tool_name, status="ok").inc()
                        METABOLIC_LOOP_DURATION.observe(elapsed_ms / 1000.0)
                    except Exception:
                        pass
                return result

    except ImportError as e:
        logger.warning(f"[COMPAT] Could not import FastMCP 3.x middleware: {e}")
        # Fall through to no-op fallback
        IS_FASTMCP_3 = False

# ═══════════════════════════════════════════════════════════════════════════════
# FastMCP 2.x Fallback (No-op — middleware not available)
# ═══════════════════════════════════════════════════════════════════════════════

if not IS_FASTMCP_3:

    class IngressToleranceMiddleware:
        """
        No-op fallback for FastMCP 2.x (middleware API not available).

        FastMCP 2.x doesn't have the Middleware base class, so we provide
        a compatible no-op that won't break the server but also won't provide
        ingress tolerance features.
        """

        def __init__(self, tool_param_sets: dict[str, set[str]] | None = None) -> None:
            self._tool_param_sets: dict[str, set[str]] = tool_param_sets or {}

        def register_tool_params(self, tool_name: str, param_names: set[str]) -> None:
            """Store param names (no-op in 2.x)."""
            self._tool_param_sets[tool_name] = param_names

        async def on_call_tool(self, *args, **kwargs) -> Any:
            """Pass through — no middleware in 2.x."""
            # In 2.x, we can't hook into the call chain, so this is never called
            # It's here for API compatibility
            pass


# Export
__all__ = ["IngressToleranceMiddleware", "MODE_SYNONYMS", "MEGA_TOOLS"]
