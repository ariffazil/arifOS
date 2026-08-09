"""
request_trust.py — Trust class of the inbound HTTP request (STAB-2026-08-09)

Gödel / vault7 trust push:
  Auto-signing with server keys for actor names is ONLY safe when the caller
  is a true local process (loopback, unproxied). Public traffic via Cloudflare
  still hits 127.0.0.1 on the VPS — without this gate, knowing "OPENCLAW"
  is enough to get elevated authority.

Trust classes:
  LOCAL_LOOPBACK — client is 127.0.0.1/::1 and no proxy headers
  PROXIED        — has CF-Connecting-IP / X-Forwarded-For / X-Real-IP
  UNKNOWN        — no request context (stdio / tests) — conservative

Env:
  ARIFOS_TRUST_AUTO_SIGN=1  — allow auto-sign only when LOCAL_LOOPBACK (default 1)
  ARIFOS_TRUST_AUTO_SIGN=0  — never auto-sign / never name-elevate operators

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import logging
import os
from contextvars import ContextVar
from typing import Any

logger = logging.getLogger(__name__)

_TRUST: ContextVar[str] = ContextVar("arifos_request_trust", default="UNKNOWN")
_PEER: ContextVar[str] = ContextVar("arifos_request_peer", default="")

_LOCAL_HOSTS = frozenset({"127.0.0.1", "::1", "localhost", "testclient", ""})


def set_request_trust(*, peer: str = "", proxied: bool = False) -> None:
    peer_n = (peer or "").split("%")[0].strip().lower()
    _PEER.set(peer_n)
    if proxied:
        _TRUST.set("PROXIED")
    elif peer_n in _LOCAL_HOSTS or peer_n.startswith("127."):
        _TRUST.set("LOCAL_LOOPBACK")
    else:
        _TRUST.set("PROXIED")  # non-local peer treated as external


def get_request_trust() -> str:
    return _TRUST.get()


def get_request_peer() -> str:
    return _PEER.get()


def is_true_local_loopback() -> bool:
    """True only for unproxied loopback — safe for host-key auto-sign."""
    return get_request_trust() == "LOCAL_LOOPBACK"


def auto_sign_allowed() -> bool:
    """May the kernel sign challenges with on-disk keys for actor names?"""
    flag = os.getenv("ARIFOS_TRUST_AUTO_SIGN", "1").strip().lower()
    if flag in ("0", "false", "no", "off"):
        return False
    # Tests / stdio with no HTTP context: allow only if explicitly opted in
    if get_request_trust() == "UNKNOWN":
        return os.getenv("ARIFOS_TRUST_AUTO_SIGN_UNKNOWN", "0").strip().lower() in (
            "1",
            "true",
            "yes",
        )
    return is_true_local_loopback()


def trust_snapshot() -> dict[str, Any]:
    return {
        "request_trust": get_request_trust(),
        "peer": get_request_peer(),
        "auto_sign_allowed": auto_sign_allowed(),
        "true_local_loopback": is_true_local_loopback(),
    }
