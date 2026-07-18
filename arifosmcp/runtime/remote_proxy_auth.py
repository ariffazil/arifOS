"""
remote_proxy_auth.py — Lightweight L11 gate for Path-B organ proxies

IRR-DIP / hollow-handoff follow-on (2026-07-09):

Path A (gated):  MCP → arif_route → constitutional_gate → bridge → organ
Path B (bypass): MCP → wealth_*/well_*/geox_* proxy → organ (was unauthenticated)

This module closes Path B at the **proxy layer only**:
  require a valid session_id (validate_session) without full constitutional mediation.

Not a full F1–F13 gate. Not execution authorization. Session presence + validity only.
Mitigates free compute / reconnaissance / DoS via unauthenticated proxy surface.

Env:
  ARIFOS_REMOTE_PROXY_AUTH=true|false  (default true)

DITEMPA BUKAN DIBERI — Forged 2026-07-09
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger("arifosmcp.remote_proxy_auth")

# Auth keys stripped from kwargs before organ forward (never organ-native)
_AUTH_ARG_KEYS = frozenset(
    {
        "session_id",
        "actor_id",
        "_envelope",
        "authority_token",
        "actor_signature",
    }
)


def remote_proxy_auth_enabled() -> bool:
    """Kill-switch: default ON. Set ARIFOS_REMOTE_PROXY_AUTH=false to disable."""
    return os.getenv("ARIFOS_REMOTE_PROXY_AUTH", "true").lower() in (
        "true",
        "1",
        "yes",
        "on",
    )


def extract_proxy_auth(
    arguments: dict[str, Any] | None = None,
    *,
    headers: dict[str, str] | None = None,
) -> tuple[str | None, str | None]:
    """
    Resolve session_id / actor_id from call arguments, envelope, or MCP headers.

    Order (session_id):
      1. arguments.session_id
      2. arguments._envelope.session_id
      3. headers mcp-session-id / x-mcp-session-id
      No process environment or previous invocation is consulted.
    """
    args = dict(arguments or {})
    session_id = args.get("session_id")
    actor_id = args.get("actor_id")

    env_payload = args.get("_envelope")
    if isinstance(env_payload, dict):
        session_id = session_id or env_payload.get("session_id")
        actor_id = actor_id or env_payload.get("actor_id")

    if headers:
        # Header keys may be mixed-case depending on ASGI stack
        lower = {str(k).lower(): v for k, v in headers.items() if v is not None}
        session_id = (
            session_id
            or lower.get("mcp-session-id")
            or lower.get("x-mcp-session-id")
            or lower.get("x-arifos-session-id")
        )
        actor_id = actor_id or lower.get("x-arifos-actor-id") or lower.get("x-actor-id")

    if session_id is not None:
        session_id = str(session_id).strip() or None
    if actor_id is not None:
        actor_id = str(actor_id).strip() or None
    return session_id, actor_id


def strip_auth_args(arguments: dict[str, Any] | None) -> dict[str, Any]:
    """Return organ-forward args without auth/envelope keys."""
    if not arguments:
        return {}
    return {k: v for k, v in arguments.items() if k not in _AUTH_ARG_KEYS}


def require_remote_proxy_session(
    *,
    tool_name: str,
    organ: str,
    arguments: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    Lightweight Path-B gate.

    Returns:
      {
        "ok": bool,
        "session_id": str|None,
        "actor_id": str|None,
        "reason": str,
        "code": "OK"|"DISABLED"|"SESSION_REQUIRED"|"SESSION_INVALID",
        "forward_args": dict,   # kwargs safe to send to organ
        "auth": dict,           # raw validate_session payload when run
      }
    """
    forward_args = strip_auth_args(arguments)

    if not remote_proxy_auth_enabled():
        return {
            "ok": True,
            "session_id": session_id,
            "actor_id": actor_id,
            "reason": "remote proxy auth disabled (ARIFOS_REMOTE_PROXY_AUTH=false)",
            "code": "DISABLED",
            "forward_args": forward_args if arguments is not None else {},
            "auth": {},
        }

    sid, aid = extract_proxy_auth(arguments, headers=headers)
    if session_id:
        sid = session_id
    if actor_id:
        aid = actor_id

    # Prefer L11 validator (explicit SCT/session; no implicit inheritance)
    try:
        from arifosmcp.runtime.session_auth import validate_session

        auth = validate_session(sid, aid)
    except Exception as exc:
        logger.warning(
            "remote_proxy_auth: validate_session failed tool=%s organ=%s: %s",
            tool_name,
            organ,
            exc,
        )
        return {
            "ok": False,
            "session_id": sid,
            "actor_id": aid,
            "reason": f"REMOTE_PROXY_AUTH: session validator error: {exc}",
            "code": "SESSION_INVALID",
            "forward_args": forward_args,
            "auth": {"error": str(exc)},
        }

    if not auth.get("valid"):
        reason = auth.get("reason") or "L11 AUTH failed"
        code = "SESSION_REQUIRED" if not sid and "missing" in str(reason).lower() else "SESSION_INVALID"
        if not sid:
            code = "SESSION_REQUIRED"
            reason = (
                f"REMOTE_PROXY_AUTH: session_id required for organ proxy "
                f"{organ}.{tool_name} (Path B). Call arif_init first, then pass session_id."
            )
        else:
            reason = f"REMOTE_PROXY_AUTH: {reason}"

        logger.info(
            "remote_proxy_auth DENY organ=%s tool=%s code=%s sid=%s",
            organ,
            tool_name,
            code,
            (sid or "")[:16],
        )
        return {
            "ok": False,
            "session_id": sid,
            "actor_id": aid or auth.get("actor_id"),
            "reason": reason,
            "code": code,
            "forward_args": forward_args,
            "auth": auth,
        }

    logger.debug(
        "remote_proxy_auth ALLOW organ=%s tool=%s actor=%s",
        organ,
        tool_name,
        auth.get("actor_id"),
    )
    return {
        "ok": True,
        "session_id": sid or (auth.get("session") or {}).get("session_id"),
        "actor_id": auth.get("actor_id") or aid,
        "reason": "REMOTE_PROXY_AUTH: session valid",
        "code": "OK",
        "forward_args": forward_args,
        "auth": auth,
    }


def deny_payload(
    gate: dict[str, Any],
    *,
    organ: str,
    tool_name: str,
) -> dict[str, Any]:
    """Structured HOLD-shaped payload for proxy denial (not a kernel verdict)."""
    return {
        "status": "HOLD",
        "verdict": "HOLD",
        "code": gate.get("code", "SESSION_INVALID"),
        "reason": gate.get("reason"),
        "organ": organ,
        "tool": tool_name,
        "gate": "remote_proxy_auth",
        "path": "B",
        "execution_authorized": False,
        "caller_verified": False,
        "null_coercion_result": False,
        "next_probe": "arif_init(mode='init') then retry with session_id",
        "session_id": gate.get("session_id"),
        "actor_id": gate.get("actor_id"),
    }


def inject_session_params(input_schema: dict[str, Any] | None) -> dict[str, Any]:
    """
    Advertise session_id / actor_id on proxied organ tools so clients know
    Path B requires them. Does not make them JSON-schema required (env bootstrap
    still allowed via validate_session), but descriptions mark them as required
    for unauthenticated callers.
    """
    schema = dict(input_schema or {"type": "object", "properties": {}})
    props = dict(schema.get("properties") or {})
    props.setdefault(
        "session_id",
        {
            "type": "string",
            "description": (
                "Explicit arifOS session_id from arif_init (REQUIRED for organ proxy Path B)."
            ),
        },
    )
    props.setdefault(
        "actor_id",
        {
            "type": "string",
            "description": "Optional actor_id bound to the session.",
        },
    )
    schema["properties"] = props
    schema.setdefault("type", "object")
    # Require session_id at schema level for discovery honesty
    req = list(schema.get("required") or [])
    if "session_id" not in req:
        req.append("session_id")
    schema["required"] = req
    return schema
