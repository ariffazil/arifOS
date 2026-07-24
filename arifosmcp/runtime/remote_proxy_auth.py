"""
remote_proxy_auth.py — Lightweight L11 gate for Path-B organ proxies

IRR-DIP / hollow-handoff follow-on (2026-07-09):

Path A (gated):  MCP → arif_route → constitutional_gate → bridge → organ
Path B (bypass): MCP → wealth_*/well_*/geox_* proxy → organ (was unauthenticated)

This module closes Path B at the **proxy layer only**:
  require a valid session_id (validate_session) without full constitutional mediation.

Not a full F1–F13 gate. Not execution authorization. Session presence + validity only.
Mitigates free compute / reconnaissance / DoS via unauthenticated proxy surface.

B4 hardening (2026-07-23):
  - ARIFOS_REMOTE_PROXY_AUTH=false is now HARD-DENY (HOLD). The env var no longer
    flips the gate to anonymous ALLOW. Path B disabled = Path B closed.
  - After L11 validation, the kernel constructs a sanitized OBSERVE_ONLY federation
    envelope from validated actor/session/SCT. Caller-supplied auth/envelope fields
    are discarded upstream of organ forward; the organ only sees the kernel envelope.
  - Caller-supplied `session_id`, `actor_id`, `_envelope`, `session_token`,
    `trace_id`, `authority_token`, `actor_signature` are NEVER trusted as
    authoritative — they are extraction hints only. The validated values from
    L11 / SCT are the only source of truth forwarded to organs.

Env:
  ARIFOS_REMOTE_PROXY_AUTH=true|false  (default true)

DITEMPA BUKAN DIBERI — Forged 2026-07-09, hardened 2026-07-23
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

logger = logging.getLogger("arifosmcp.remote_proxy_auth")

# Auth/identity keys stripped from caller kwargs before organ forward.
# These are extraction hints only; the kernel never carries them as forward
# arguments. The validated envelope replaces them.
_AUTH_ARG_KEYS = frozenset(
    {
        "session_id",
        "actor_id",
        "_envelope",
        "authority_token",
        "actor_signature",
        "session_token",
        "trace_id",
    }
)

# Path-B authority cap. Validated actor may hold a higher trust tier in the
# SCT, but the federation envelope sent to organs is OBSERVE_ONLY — Path B
# is reader-side, never mutation-side.
ENVELOPE_AUTHORITY = "OBSERVE_ONLY"
ENVELOPE_VERSION = "1"
ENVELOPE_SOURCE = "arifOS_kernel"


def remote_proxy_auth_enabled() -> bool:
    """Path-B gate enable check. Default ON. Disable with ARIFOS_REMOTE_PROXY_AUTH=false."""
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
) -> tuple[str | None, str | None, str | None]:
    """
    Resolve session_id / actor_id / session_token from call arguments, envelope, or MCP headers.

    Order (session_id):
      1. arguments.session_id
      2. arguments._envelope.session_id
      3. headers mcp-session-id / x-mcp-session-id
      No process environment or previous invocation is consulted.
    """
    args = dict(arguments or {})
    session_id = args.get("session_id")
    actor_id = args.get("actor_id")
    session_token = args.get("session_token")

    env_payload = args.get("_envelope")
    if isinstance(env_payload, dict):
        session_id = session_id or env_payload.get("session_id")
        actor_id = actor_id or env_payload.get("actor_id")
        session_token = session_token or env_payload.get("session_token")

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
        session_token = session_token or lower.get("x-arifos-session-token") or lower.get("x-sct")

    if session_id is not None:
        session_id = str(session_id).strip() or None
    if actor_id is not None:
        actor_id = str(actor_id).strip() or None
    if session_token is not None:
        session_token = str(session_token).strip() or None
    return session_id, actor_id, session_token


def strip_auth_args(arguments: dict[str, Any] | None) -> dict[str, Any]:
    """Return organ-forward args without auth/envelope keys (caller fields discarded)."""
    if not arguments:
        return {}
    return {k: v for k, v in arguments.items() if k not in _AUTH_ARG_KEYS}


def build_federation_envelope(
    *,
    session_id: str | None,
    actor_id: str | None,
    session_token: str | None,
    authority: str = ENVELOPE_AUTHORITY,
    actor_verified: bool = False,
    source: str = ENVELOPE_SOURCE,
    trace_id: str | None = None,
) -> dict[str, Any]:
    """
    Construct a kernel-authored OBSERVE_ONLY federation envelope.

    The envelope is the ONLY auth artifact forwarded to organ tools via
    Path B. Anything caller-supplied in `arguments._envelope` is discarded
    upstream of this function.
    """
    return {
        "session_id": session_id,
        "actor_id": actor_id,
        "session_token": session_token,
        "authority": ENVELOPE_AUTHORITY,
        "actor_verified": bool(actor_verified),
        "source": source,
        "issued_at": int(time.time()),
        "trace_id": trace_id,
        "path": "B",
        "envelope_version": ENVELOPE_VERSION,
    }


def require_remote_proxy_session(
    *,
    tool_name: str,
    organ: str,
    arguments: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """
    Lightweight Path-B gate.

    Returns:
      {
        "ok": bool,
        "session_id": str|None,
        "actor_id": str|None,
        "session_token": str|None,
        "reason": str,
        "code": ("OK"|"DISABLED"|"SESSION_REQUIRED"|"SESSION_INVALID"
                 |"SESSION_MISMATCH"|"VALIDATOR_ERROR"),
        "forward_args": dict,   # sanitized kwargs to send to organ (caller auth discarded)
        "envelope": dict,       # kernel-authored OBSERVE_ONLY envelope (only when ok=True)
        "auth": dict,           # raw validate_session payload when run
      }

    Semantics:
      - ARIFOS_REMOTE_PROXY_AUTH=false → ok=False, code="DISABLED" (HOLD).
        Path B is fully closed; never anonymous ALLOW.
      - Missing session_id → ok=False, code="SESSION_REQUIRED".
      - Actor mismatch / invalid / expired → ok=False, code="SESSION_MISMATCH" or
        "SESSION_INVALID".
      - Valid → ok=True, code="OK", envelope built ONLY from validated fields.
        Caller-supplied _envelope is discarded; organ receives the kernel envelope.
    """
    forward_args = strip_auth_args(arguments)

    # B4: Path B disabled → HOLD, never anonymous ALLOW.
    if not remote_proxy_auth_enabled():
        logger.info(
            "remote_proxy_auth DENY organ=%s tool=%s code=DISABLED reason=path_b_disabled",
            organ,
            tool_name,
        )
        return {
            "ok": False,
            "session_id": session_id,
            "actor_id": actor_id,
            "session_token": session_token,
            "reason": (
                "REMOTE_PROXY_AUTH: Path B disabled by ARIFOS_REMOTE_PROXY_AUTH=false. "
                "Organ proxy is a HOLD — set the env var to true to re-enable."
            ),
            "code": "DISABLED",
            "forward_args": forward_args if arguments is not None else {},
            "envelope": {},
            "auth": {},
        }

    sid, aid, stoken = extract_proxy_auth(arguments, headers=headers)
    if session_id:
        sid = session_id
    if actor_id:
        aid = actor_id
    if session_token:
        stoken = session_token

    # Prefer L11 validator (explicit SCT/session; no implicit inheritance)
    try:
        from arifosmcp.runtime.session_auth import validate_session

        auth = validate_session(sid, aid, session_token=stoken)
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
            "session_token": stoken,
            "reason": f"REMOTE_PROXY_AUTH: session validator error: {exc}",
            "code": "VALIDATOR_ERROR",
            "forward_args": forward_args,
            "envelope": {},
            "auth": {"error": str(exc)},
        }

    if not auth.get("valid"):
        reason = auth.get("reason") or "L11 AUTH failed"
        # Distinguish mismatch from invalid for caller diagnostics.
        if "actor_id mismatch" in str(reason).lower():
            code = "SESSION_MISMATCH"
        elif not sid:
            code = "SESSION_REQUIRED"
        else:
            code = "SESSION_INVALID"
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
            "session_token": stoken,
            "reason": reason,
            "code": code,
            "forward_args": forward_args,
            "envelope": {},
            "auth": auth,
        }

    # Valid: build kernel-authored envelope from validated fields only.
    sess_obj = auth.get("session") or {}
    validated_session_id = sid or auth.get("session_id") or sess_obj.get("session_id")
    validated_actor_id = auth.get("actor_id") or aid
    validated_session_token = auth.get("session_token") or stoken
    actor_verified = bool(auth.get("actor_verified"))

    envelope = build_federation_envelope(
        session_id=validated_session_id,
        actor_id=validated_actor_id,
        session_token=validated_session_token,
        actor_verified=actor_verified,
    )

    logger.debug(
        "remote_proxy_auth ALLOW organ=%s tool=%s actor=%s auth=%s",
        organ,
        tool_name,
        validated_actor_id,
        ENVELOPE_AUTHORITY,
    )
    return {
        "ok": True,
        "session_id": validated_session_id,
        "actor_id": validated_actor_id,
        "session_token": validated_session_token,
        "reason": "REMOTE_PROXY_AUTH: session valid",
        "code": "OK",
        "forward_args": forward_args,
        "envelope": envelope,
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
