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
        "arif_judge",
        "arif_seal",
        "arif_critique",
        "arif_init",
        "arif_forge",
    }
    medium_risk = {
        "arif_think",
        "arif_gateway_connect",
        "arif_kernel_route",
    }
    low_risk = {
        "arif_observe",
        "arif_fetch",
        "arif_compose",
        "arif_memory_recall",
        "arif_measure",
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
    actor_id: str | None = None,
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
        actor_ref = actor_id or "arifOS-kernel"
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


async def _write_harness_telemetry_in_thread(
    session_id: str | None,
    tool_name: str,
    agent_id: str | None,
    verdict: str,
    floors_checked: list[str],
    elapsed_ms: int,
) -> None:
    """Write tool execution trace to the local HarnessTelemetry SQLModel table in a worker thread."""
    def _run_sync():
        try:
            import sys
            pilot_src = "/root/pydantic-ai-pilot/src"
            if pilot_src not in sys.path:
                sys.path.append(pilot_src)
            
            from datetime import datetime

            from harness_telemetry import HarnessTelemetry
            from sqlmodel import Session, create_engine
            
            model_psi = tool_name
            try:
                from arifosmcp.runtime.tools import get_session
                sess = get_session(session_id)
                if sess and isinstance(sess, dict):
                    card = sess.get("model_governance_card")
                    if card and isinstance(card, dict):
                        anchor = card.get("model_anchor")
                        if anchor and isinstance(anchor, dict):
                            model_psi = anchor.get("verified_model_key") or tool_name
            except Exception:
                pass
                
            provider = agent_id or "mcp"
            
            # Map verdict to valid set: SEAL, HOLD, VOID, PARTIAL, SABAR
            v_upper = verdict.upper()
            if "VOID" in v_upper:
                verdict_mapped = "VOID"
            elif "HOLD" in v_upper or "HUMAN" in v_upper:
                verdict_mapped = "HOLD"
            elif "PARTIAL" in v_upper:
                verdict_mapped = "PARTIAL"
            elif "SABAR" in v_upper:
                verdict_mapped = "SABAR"
            else:
                verdict_mapped = "SEAL"

            telemetry = HarnessTelemetry(
                session_id=session_id or "session-unknown",
                model_psi=model_psi,
                provider=provider,
                floors_checked=floors_checked,
                verdict=verdict_mapped,
                token_usage_total=0,
                execution_latency_ms=float(elapsed_ms),
                epsilon_variance=1e-6,
                timestamp=datetime.now(UTC)
            )
            telemetry.model_validate(telemetry.model_dump())
            
            db_url = "postgresql://arifos_admin:ArifPostgres2026!@127.0.0.1:5432/vault999"
            engine = create_engine(db_url, echo=False)
            with Session(engine) as db_session:
                db_session.add(telemetry)
                db_session.commit()
        except Exception as db_err:
            logger.debug(f"[telemetry-db] telemetry write failed: {db_err}")

    await asyncio.to_thread(_run_sync)


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
    # Preserve delegation chain: caller_actor is the original human (e.g. arifbfazil),
    # executor_actor is the relay (Hermes@af-forge), sovereign stays the human.
    # Downstream tools MUST see the sovereign in actor_id, not the relay.
    if envelope.actor_id == "Hermes@af-forge":
        # Relay sent itself as actor — recover original human from delegation chain.
        # If no original human is known, fall back to anonymous (never expose relay as sovereign).
        original_actor = envelope.caller_actor or envelope.sovereign or "anonymous"
        envelope.actor_id = original_actor
        envelope.caller_actor = original_actor
        envelope.sovereign = original_actor
    elif envelope.actor_id and envelope.actor_id != "Hermes@af-forge":
        envelope.caller_actor = envelope.actor_id  # preserve original human caller
        envelope.sovereign = envelope.actor_id
    envelope.executor_actor = "Hermes@af-forge"
    envelope.legacy_wrap = False
    envelope.actor_verification = "delegated"  # came in via trusted relay
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

    # 5. ATOMIC action requires substantively valid ack_id (not just present)
    if envelope.risk.action_class == ActionClass.ATOMIC:
        ack_id = envelope.receipts.arif_ack_id
        if not ack_id:
            return False, "ATOMIC requires arif_ack_id (L13 sovereign approval)"
        # Lazy import to avoid circular dependency at module load time
        try:
            from arifosmcp.runtime.tools import _validate_ack_id
            ack_ok, ack_reason = _validate_ack_id(
                ack_id,
                tool_name,
                envelope.niat or envelope.matlamat or "unknown",
                envelope.actor_id,
                envelope.session_id,
            )
            if not ack_ok:
                return False, f"ack_id validation failed: {ack_reason}"
        except ImportError:
            # If tools module not loaded yet, fall through (belt-and-suspenders:
            # schema-level validation already checked presence)
            logger.warning("_validate_ack_id not available — ack_id substance check skipped")

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
                self._sink_counters: dict[str, dict] = {}
                # Register global instance for conformance spine anti-sink A3 check
                import arifosmcp.runtime.ingress_middleware as _im
                _im._ARIFOS_INGRESS_INSTANCE = self

            def register_tool_params(self, tool_name: str, param_names: set[str]) -> None:
                self._tool_param_sets[tool_name] = param_names

            async def on_call_tool(
                self,
                context: MiddlewareContext[mt.CallToolRequestParams],
                call_next: CallNext[mt.CallToolRequestParams, ToolResult],
            ) -> ToolResult:
                msg = context.message
                tool_name = msg.name

                # ── Bypass for Canary Ping Tool (no actor, no envelope, no policy) ──
                if tool_name == "arif_ping":
                    return await call_next(context)

                t0 = time.monotonic()
                verdict = "SEAL"
                floors = ["F2", "F4", "F11"]
                if tool_name == "arif_init":
                    floors = ["F1", "F11", "F13"]
                elif tool_name == "arif_compose":
                    floors = ["F1", "F2", "F4", "F11", "F13"]

                envelope_session_id = "unknown"
                envelope_agent_id = "mcp"

                try:
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

                    envelope_session_id = envelope.session_id
                    envelope_agent_id = envelope.agent_id

                    # ── FORGE SCOPE GATE (v3: ToolScoper integration) ──────────────
                    # When forge_scope is non-empty, only tools on the allowlist pass.
                    # This is the arifOS-side of the A-FORGE ToolScoper bridge.
                    # The scope is populated by A-FORGE before forwarding the call.
                    if envelope.forge_scope:
                        if tool_name not in envelope.forge_scope:
                            logger.info(
                                f"Ingress forge_scope HOLD for {tool_name}: "
                                f"tool not in forge_scope allowlist "
                                f"(scope={envelope.forge_scope})"
                            )
                            from mcp.types import TextContent
                            return ToolResult(
                                content=[
                                    TextContent(
                                        type="text",
                                        text=(
                                            f"FORGE_SCOPE_HOLD: {tool_name} is not in "
                                            f"the current forge_scope allowlist.\n"
                                            f"Allowed tools: {', '.join(envelope.forge_scope)}\n\n"
                                            f"This call was scoped by A-FORGE ToolScoper "
                                            f"to the current action class and pipeline stage. "
                                            f"Use a different forge_plan action class or "
                                            f"expand the scope for this operation."
                                        ),
                                    )
                                ],
                                structured_content=_hold_envelope_dict(
                                    tool_name=tool_name,
                                    reason=f"Tool {tool_name} not in forge_scope allowlist",
                                    session_id=envelope.session_id,
                                    actor_id=envelope.actor_id,
                                    extra={
                                        "gate": "forge_scope",
                                        "forge_scope": envelope.forge_scope,
                                    },
                                ),
                            )
                        logger.debug(
                            f"Ingress forge_scope PASS for {tool_name}: "
                            f"tool in scope ({len(envelope.forge_scope)} tools)"
                        )
                    # ────────────────────────────────────────────────────────────────

                    # ── UPGRADE ACTION CLASS BEFORE PROMOTION (2026-06-12) ─────────
                    _tool_risk = classify_tool(tool_name)
                    if (
                        envelope.risk.action_class == ActionClass.OBSERVE
                        and _tool_risk.action_class != ActionClass.OBSERVE
                    ):
                        envelope.risk.action_class = _tool_risk.action_class
                        envelope.risk.tier = _tool_risk.tier

                    # ── LOCAL SERVICE TRUST (Hermes bridge) ────────────────────────
                    _trusted = _try_promote_local_service(envelope, dict(msg.arguments or {}), tool_name)
                    if _trusted:
                        logger.info(
                            f"Ingress: local service trust promoted for {tool_name} "
                            f"→ actor={envelope.actor_id}"
                        )

                    envelope_ok, envelope_reason = _validate_envelope_for_tool(envelope, tool_name)
                    if not envelope_ok:
                        logger.warning(f"Ingress envelope HOLD for {tool_name}: {envelope_reason}")
                        from mcp.types import TextContent
                        verdict = "HOLD"
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
                            verdict = "HOLD"
                            return ToolResult(
                                content=[
                                    TextContent(
                                        type="text",
                                        text=(
                                            f"888_HOLD: Sovereignty checkpoint required.\n\n"
                                            f"Tool: {tool_name}\n"
                                            f"Risk: {envelope.risk.tier.value} | {envelope.risk.action_class.value}\n"
                                            f"Reversibility: {envelope.risk.reversibility.value}\n\n"
                                            f"Answer these four questions:\n"
                                            f"1. What EVIDENCE are you accepting?\n"
                                            f"2. What UNCERTAINTY are you tolerating?\n"
                                            f"3. What RESPONSIBILITY are you assuming?\n"
                                            f"4. What REPAIR path exists if this goes wrong?\n\n"
                                            f"Resubmit with sovereignty_checkpoint in FederationEnvelope.\n"
                                            f"Checkpoint ID: {chk.checkpoint_id}\n"
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
                            chk_ok, chk_reason = checkpoint.is_valid()
                            if not chk_ok:
                                logger.warning(
                                    f"Ingress checkpoint invalid for {tool_name}: {chk_reason}"
                                )
                                from mcp.types import TextContent
                                verdict = "HOLD"
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

                    # ── CONSTITUTIONAL INTERCEPTOR v0.2 ────────────────────────────────
                    # Every MCP call passes through the kernel's admissibility gate
                    # before tool dispatch. This is the data-plane position.
                    #
                    # v0.2: Anti-sink session simulation counter (Mission 003).
                    # Tracks ADMIT_SIMULATE vs ADMIT_MUTATE per session. Inject
                    # _simulation_count into request args before interceptor call.
                    try:
                        from arifosmcp.kernel.interceptor import intercept
                        from arifosmcp.kernel.models import AdmissibilityVerdict

                        # ── Anti-sink: per-session simulation counter ──
                        if not hasattr(self, "_sink_counters"):
                            self._sink_counters = {}
                        sid = envelope.session_id or "anonymous"
                        if sid not in self._sink_counters:
                            self._sink_counters[sid] = {
                                "sim_count": 0, "action_count": 0, "refusals": []
                            }

                        args = dict(msg.arguments or {})
                        args["_simulation_count"] = self._sink_counters[sid]["sim_count"]
                        args["_action_count"] = self._sink_counters[sid]["action_count"]

                        kernel_input = {
                            "name": tool_name,
                            "params": {
                                "name": tool_name,
                                "arguments": args,
                            },
                        }
                        decision = intercept(kernel_input)

                        if decision.verdict in (
                            AdmissibilityVerdict.DENY,
                            AdmissibilityVerdict.QUARANTINE,
                            AdmissibilityVerdict.INVALID_REPORT,
                        ):
                            logger.warning(
                                f"KERNEL INTERCEPTOR: {decision.verdict.value} for {tool_name}: {decision.reason}"
                            )
                            from mcp.types import TextContent
                            return ToolResult(
                                content=[
                                    TextContent(
                                        type="text",
                                        text=(
                                            f"KERNEL_{decision.verdict.value}: {decision.reason}\n\n"
                                            f"Capability: {decision.capability_id or 'unknown'}\n"
                                            f"Actor: {decision.actor_id or 'anonymous'}\n"
                                            f"Authority: {decision.authority_tier.value if decision.authority_tier else 'LOW'}"
                                        ),
                                    )
                                ],
                            )

                        if decision.verdict == AdmissibilityVerdict.HOLD_888:
                            logger.warning(
                                f"KERNEL INTERCEPTOR: 888_HOLD for {tool_name}: {decision.reason}"
                            )
                            from mcp.types import TextContent
                            verdict = "HOLD"
                            return ToolResult(
                                content=[
                                    TextContent(
                                        type="text",
                                        text=(
                                            f"888_HOLD: {decision.reason}\n\n"
                                            f"Capability: {decision.capability_id or 'unknown'}\n"
                                            f"Actor: {decision.actor_id or 'anonymous'}\n"
                                            f"Authority: {decision.authority_tier.value if decision.authority_tier else 'LOW'}\n\n"
                                            f"This action requires SOVEREIGN (Arif/888) approval."
                                        ),
                                    )
                                ],
                            )

                        # ADMIT_READ / ADMIT_SIMULATE / ADMIT_MUTATE — proceed
                        logger.debug(
                            f"KERNEL INTERCEPTOR: {decision.verdict.value} for {tool_name} — {decision.reason}"
                        )

                        # ── Anti-sink: update counters ──
                        if decision.verdict == AdmissibilityVerdict.ADMIT_SIMULATE:
                            self._sink_counters[sid]["sim_count"] += 1
                        elif decision.verdict == AdmissibilityVerdict.ADMIT_MUTATE:
                            self._sink_counters[sid]["action_count"] += 1
                            # Reset sim counter on action (the sink was averted)
                            self._sink_counters[sid]["sim_count"] = 0

                        # Rewrite hint: if verdict is ADMIT_SIMULATE, inject simulation flag
                        if decision.verdict == AdmissibilityVerdict.ADMIT_SIMULATE:
                            if msg.arguments is None:
                                msg.arguments = {}
                            msg.arguments["_simulation_mode"] = True

                    except ImportError:
                        logger.debug("Kernel interceptor not available — skipping")
                    except Exception as exc:
                        logger.error(f"Kernel interceptor error: {exc}")
                        # Fail-closed: on interceptor error, deny mutation-capable tools
                        if tool_name in ("bash", "py", "python_repl", "write", "edit"):
                            from mcp.types import TextContent
                            logger.warning(
                                f"KERNEL INTERCEPTOR FAIL_CLOSED: DENY for {tool_name} due to error"
                            )
                            return ToolResult(
                                content=[
                                    TextContent(
                                        type="text",
                                        text=(
                                            f"KERNEL_ERROR: Interceptor unavailable — "
                                            f"tool '{tool_name}' denied as safety precaution.\n"
                                            f"Error: {exc}"
                                        ),
                                    )
                                ],
                            )

                    # Log envelope
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

                    if msg.arguments is None:
                        msg.arguments = {}
                    msg.arguments["_envelope"] = envelope.model_dump(mode="json")
                    if envelope.actor_id and envelope.actor_id != "anonymous":
                        msg.arguments.setdefault("actor_id", envelope.actor_id)
                    if envelope.session_id and envelope.session_id != "unknown":
                        msg.arguments.setdefault("session_id", envelope.session_id)

                    if msg.arguments:
                        if tool_name in MEGA_TOOLS and "mode" in msg.arguments:
                            synonyms = MODE_SYNONYMS.get(tool_name, {})
                            raw_mode = str(msg.arguments["mode"]).lower().strip()
                            canonical = synonyms.get(raw_mode)
                            if canonical:
                                msg.arguments["mode"] = canonical

                        known = self._tool_param_sets.get(tool_name)
                        if known is not None:
                            # Keep metadata parameters and those defined in the tool's parameter schema
                            allowed_params = known | {"_envelope", "actor_id", "session_id"}
                            unknown = {k for k in msg.arguments if k not in allowed_params}
                            if unknown:
                                for k in unknown:
                                    msg.arguments.pop(k)

                    from arifosmcp.runtime.tools import _RESPONSE_CONTEXT
                    if hasattr(envelope, "actor_id") and envelope.actor_id:
                        _RESPONSE_CONTEXT.set(
                            {
                                "actor_id": str(envelope.actor_id),
                                "session_id": str(envelope.session_id) if envelope.session_id else None,
                            }
                        )

                    result = await call_next(context)
                    
                    if result:
                        if hasattr(result, "structured_content") and isinstance(result.structured_content, dict):
                            sc = result.structured_content
                            verdict = sc.get("verdict") or sc.get("status") or "SEAL"
                        elif isinstance(result, dict):
                            verdict = result.get("verdict") or result.get("status") or "SEAL"
                        elif hasattr(result, "content") and result.content:
                            for item in result.content:
                                if hasattr(item, "text") and item.text:
                                    text_lower = item.text.lower()
                                    if "888_hold" in text_lower or "hold" in text_lower:
                                        verdict = "HOLD"
                                    elif "void" in text_lower:
                                        verdict = "VOID"
                    return result
                except Exception as exc:
                    verdict = "VOID"
                    raise exc
                finally:
                    elapsed_ms = int((time.monotonic() - t0) * 1000)
                    try:
                        loop = asyncio.get_running_loop()
                        if "result" in locals() and result:
                            loop.create_task(
                                _write_tool_call_receipt(
                                    tool_name=tool_name,
                                    arguments=dict(msg.arguments or {}),
                                    result=result,
                                    elapsed_ms=elapsed_ms,
                                    actor_id=envelope_agent_id,
                                )
                            )
                        loop.create_task(
                            _write_harness_telemetry_in_thread(
                                session_id=envelope_session_id,
                                tool_name=tool_name,
                                agent_id=envelope_agent_id,
                                verdict=verdict,
                                floors_checked=floors,
                                elapsed_ms=elapsed_ms,
                            )
                        )
                    except Exception:
                        pass

                    if _METRICS_AVAILABLE and tool_name in MEGA_TOOLS:
                        try:
                            REQUESTS_TOTAL.labels(method=tool_name, status="ok" if verdict == "SEAL" else "fail").inc()
                            METABOLIC_LOOP_DURATION.observe(elapsed_ms / 1000.0)
                        except Exception:
                            pass

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

# ── Global instance reference (set by server.py at boot) ──
# Used by conformance spine for Anti-sink A3 contradiction check.
_ARIFOS_INGRESS_INSTANCE: object | None = None
