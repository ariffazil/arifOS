"""arifosmcp/runtime/tailnet_identity.py — Tailnet identity ingress verification.

(1) TailnetIdentity: the verified peer identity emitted by the tsagent ingress.
(2) verify_signed_identity(): HMAC-SHA256 verification over the identity payload.
(3) TailnetIdentityMiddleware: ASGI middleware that attaches the identity to
    the request state and, in enforce mode, fails closed on actor mismatch.

The ingress (tsagent --mode ingress) whois's every peer on the tailnet, signs
the peer's node/tags/CapMap with a shared key, and forwards to arifOS on
loopback. Only loopback is trusted to present the signed header; a direct
public/Caddy request carries no signature and is left to SCT auth.

Modes (ARIFOS_TAILNET_IDENTITY_MODE):
  observe  — attach + log; never block. Default.
  enforce  — block untrusted/invalid/mismatched signed identities.
  off      — pass through without resolving.

Floors engaged: F1 AMANAH · F2 HAQQ · F11 AUDITABILITY · F12 AUTHORITY
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import ipaddress
import json
import logging
import os
import time
from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastmcp.server.middleware.middleware import Middleware, MiddlewareContext
from starlette.datastructures import MutableHeaders
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

HEADER_IDENTITY = "x-tailnet-identity"
HEADER_SIGNATURE = "x-tailnet-signature"
HEADER_TS = "x-tailnet-ts"
HEADER_ACTOR = "x-arif-actor"

DEFAULT_KEY_FILE = "/etc/arifos/tailnet-ingress.key"
DEFAULT_MAX_SKEW_SECONDS = 120
LOOPBACK_PEERS = frozenset({"127.0.0.1", "::1", "localhost"})
TAILNET_NETWORKS = (
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("fd7a:115c:a1e0::/48"),
)


def _is_trusted_peer(peer: str) -> bool:
    """True for loopback or a Tailscale/Headscale CGNAT address."""
    if peer in LOOPBACK_PEERS:
        return True
    try:
        addr = ipaddress.ip_address(peer)
    except ValueError:
        return False
    return any(addr in network for network in TAILNET_NETWORKS)


@dataclass(frozen=True)
class TailnetIdentity:
    """Verified identity of a tailnet peer."""

    node: str
    tags: tuple[str, ...]
    caps: dict[str, Any]
    user: str | None = None
    declared_actor: str | None = None
    ts: int = 0

    @property
    def short_node(self) -> str:
        return self.node.rstrip(".").split(".", 1)[0].lower()

    def matches_actor(self, actor_id: str | None) -> bool:
        """True when the declared actor is bound to this node or one of its tags."""
        actor = (actor_id or "").strip().lower()
        if not actor:
            return False
        if actor in {self.short_node, self.node.rstrip(".").lower()}:
            return True
        for tag in self.tags:
            suffix = tag.removeprefix("tag:").lower()
            if actor == suffix:
                return True
            if actor.startswith(suffix + "-") or actor.endswith("-" + suffix):
                return True
        return False

    def has_tool(self, tool_name: str) -> bool:
        """True when the arif-fazil.com/cap/mcp grant lists the tool."""
        entries = self.caps.get("arif-fazil.com/cap/mcp") or []
        if not isinstance(entries, list):
            return False
        for entry in entries:
            if isinstance(entry, dict) and tool_name in (entry.get("tools") or []):
                return True
        return False


_current_tailnet_identity: ContextVar[TailnetIdentity | None] = ContextVar(
    "arifos_tailnet_identity", default=None
)


def current_tailnet_identity() -> TailnetIdentity | None:
    """Return the verified identity for the current request context, if any."""
    return _current_tailnet_identity.get()


def _mode() -> str:
    return (os.getenv("ARIFOS_TAILNET_IDENTITY_MODE", "observe") or "observe").strip().lower()


def _key_path() -> Path:
    return Path(os.getenv("ARIFOS_TAILNET_INGRESS_KEY_FILE", DEFAULT_KEY_FILE))


def _load_key() -> bytes | None:
    try:
        key = _key_path().read_bytes().strip()
    except OSError:
        return None
    return key or None


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _canonical(identity_b64: str, ts: str) -> bytes:
    return f"{ts}.{identity_b64}".encode()


def _sign(identity_b64: str, ts: str, key: bytes) -> str:
    return hmac.new(key, _canonical(identity_b64, ts), hashlib.sha256).hexdigest()


def sign_payload(
    payload: dict[str, Any], key: bytes, ts: int | None = None
) -> tuple[str, str, str]:
    """Sign a payload for tests and local probes. Returns (b64, signature, ts)."""
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    b64 = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    ts_str = str(int(time.time()) if ts is None else ts)
    return b64, _sign(b64, ts_str, key), ts_str


def verify_signed_identity(
    identity_b64: str,
    signature: str,
    ts: str,
    key: bytes,
    now: int | None = None,
    max_skew_seconds: int = DEFAULT_MAX_SKEW_SECONDS,
) -> TailnetIdentity | None:
    """Verify the HMAC and return the identity, or None when invalid."""
    try:
        ts_int = int(ts)
    except (TypeError, ValueError):
        return None
    now_int = int(time.time()) if now is None else now
    if abs(now_int - ts_int) > max_skew_seconds:
        return None
    expected = _sign(identity_b64, ts, key)
    if not hmac.compare_digest(expected, (signature or "").strip().lower()):
        return None
    try:
        raw = _b64decode(identity_b64)
        payload = json.loads(raw)
    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    node = str(payload.get("node") or "").strip()
    tags = payload.get("tags") or []
    caps = payload.get("caps") or {}
    if not node or not isinstance(tags, list) or not isinstance(caps, dict):
        return None
    return TailnetIdentity(
        node=node,
        tags=tuple(str(tag) for tag in tags),
        caps=caps,
        user=str(payload.get("user") or "") or None,
        declared_actor=str(payload.get("declared_actor") or "") or None,
        ts=ts_int,
    )


class TailnetIdentityMiddleware:
    """ASGI middleware: verify and attach a signed tailnet peer identity."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        mode = _mode()
        if mode == "off":
            await self.app(scope, receive, send)
            return

        headers = {
            key.decode("latin-1").lower(): value.decode("latin-1")
            for key, value in scope.get("headers", [])
        }
        identity_b64 = headers.get(HEADER_IDENTITY)
        signature = headers.get(HEADER_SIGNATURE)
        ts = headers.get(HEADER_TS)

        # Unsigned requests are the public/Caddy plane. SCT remains the gate.
        if not identity_b64 or not signature or not ts:
            await self.app(scope, receive, send)
            return

        client = scope.get("client") or ("", 0)
        peer = str(client[0]) if client else ""
        # The ingress connects from loopback, but uvicorn's proxy-header
        # rewriting (forwarded_allow_ips=*) reports the original tailnet peer.
        # Accept loopback OR a Tailscale/Headscale CGNAT address; the HMAC
        # below is the actual authentication of the ingress.
        if not _is_trusted_peer(peer):
            logger.warning("tailnet_identity: signed header from untrusted peer=%s", peer)
            if mode == "enforce":
                await self._reject(scope, receive, send, "tailnet_identity_untrusted_peer")
                return

        key = _load_key()
        if key is None:
            logger.warning("tailnet_identity: key file missing: %s", _key_path())
            if mode == "enforce":
                await self._reject(scope, receive, send, "tailnet_identity_unconfigured")
                return
            await self.app(scope, receive, send)
            return

        identity = verify_signed_identity(identity_b64, signature, ts, key)
        if identity is None:
            logger.warning("tailnet_identity: invalid or expired signature peer=%s", peer)
            if mode == "enforce":
                await self._reject(scope, receive, send, "tailnet_identity_invalid")
                return
            await self.app(scope, receive, send)
            return

        state = scope.setdefault("state", {})
        if isinstance(state, dict):
            state["tailnet_identity"] = identity

        declared = headers.get(HEADER_ACTOR) or identity.declared_actor
        if declared and not identity.matches_actor(declared):
            logger.warning(
                "tailnet_identity: actor mismatch node=%s tags=%s declared=%s",
                identity.node,
                identity.tags,
                declared,
            )
            if mode == "enforce":
                await self._reject(scope, receive, send, "tailnet_identity_actor_mismatch")
                return
        else:
            logger.info(
                "tailnet_identity: node=%s tags=%s caps=%s actor=%s",
                identity.node,
                identity.tags,
                sorted(identity.caps),
                declared or "-",
            )

        async def send_with_identity(message: dict) -> None:
            if message.get("type") == "http.response.start":
                response_headers = MutableHeaders(scope=message)
                response_headers["X-Tailnet-Node"] = identity.node
                response_headers["X-Tailnet-Tags"] = ",".join(identity.tags)
            await send(message)

        token = _current_tailnet_identity.set(identity)
        try:
            await self.app(scope, receive, send_with_identity)
        finally:
            _current_tailnet_identity.reset(token)

    @staticmethod
    async def _reject(scope: Scope, receive: Receive, send: Send, reason: str) -> None:
        response = JSONResponse(
            {"ok": False, "error": reason, "verdict": "HOLD"},
            status_code=403,
        )
        await response(scope, receive, send)


class TailnetActorBindingMiddleware(Middleware):
    """FastMCP middleware: bind the tool-call actor_id to the tailnet identity.

    The ASGI TailnetIdentityMiddleware sets a request-scoped contextvar. This
    middleware reads the declared `actor_id` from the `arif_init` (or any tool)
    arguments and compares it to the verified node/tags. Observe mode logs;
    enforce mode raises PermissionError.
    """

    async def on_request(self, context: MiddlewareContext[Any], call_next: Any) -> Any:
        method = getattr(context, "method", "") or ""
        if method != "tools/call":
            return await call_next(context)

        message = getattr(context, "message", None)
        if message is None:
            return await call_next(context)

        tool_name = str(getattr(message, "name", "") or "")
        args = getattr(message, "arguments", None)
        if args is None:
            params = getattr(message, "params", None)
            args = getattr(params, "arguments", None)
        actor_id = str(args.get("actor_id") or "") if isinstance(args, dict) else ""

        identity = current_tailnet_identity()
        if identity is not None and actor_id:
            if not identity.matches_actor(actor_id):
                logger.warning(
                    "tailnet_actor_binding: mismatch tool=%s node=%s tags=%s actor=%s",
                    tool_name,
                    identity.node,
                    identity.tags,
                    actor_id,
                )
                if _mode() == "enforce":
                    raise PermissionError("tailnet actor mismatch")
            else:
                logger.info(
                    "tailnet_actor_binding: match tool=%s node=%s actor=%s",
                    tool_name,
                    identity.node,
                    actor_id,
                )

        # CapMap check: public tools bypass; all other tool calls need the
        # arif-fazil.com/cap/mcp grant to list the tool. Observe logs; enforce
        # raises. This is the "valid ingress but missing capability" path.
        if identity is not None and tool_name and tool_name != "arif_init":
            cap_grant = identity.caps.get("arif-fazil.com/cap/mcp")
            if cap_grant is None:
                logger.warning(
                    "tailnet_capability: no grant tool=%s node=%s",
                    tool_name,
                    identity.node,
                )
                if _mode() == "enforce":
                    raise PermissionError("tailnet capability missing")
            elif not identity.has_tool(tool_name):
                logger.warning(
                    "tailnet_capability: missing tool=%s node=%s caps=%s",
                    tool_name,
                    identity.node,
                    sorted(identity.caps),
                )
                if _mode() == "enforce":
                    raise PermissionError("tailnet capability missing")
            else:
                logger.info(
                    "tailnet_capability: granted tool=%s node=%s",
                    tool_name,
                    identity.node,
                )

        return await call_next(context)
