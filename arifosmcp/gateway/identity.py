"""
Identity layer v0.1 — Signed Subject Headers + HMAC-SHA256
══════════════════════════════════════════════════════════

arifOS Gateway identity resolution with cryptographic binding.
Prevents agents from forging subject headers.

Headers (7):
  X-ArifOS-API-Key      — static API key (used as HMAC secret)
  X-ArifOS-Human-ID     — sovereign human identifier
  X-ArifOS-Agent-ID     — agent identifier
  X-ArifOS-Session-ID   — session binding
  X-ArifOS-Org-ID       — workspace/org binding
  X-ArifOS-Signature    — HMAC-SHA256 over canonicalized subject headers + timestamp
  X-ArifOS-Timestamp    — Unix epoch seconds (anti-replay)

Signature base for HMAC:
  human_id=<val>|agent_id=<val>|session_id=<val>|org_id=<val>|timestamp=<val>

v0.2+: OIDC/OAuth 2.1 pluggable identity adapter.
SOVEREIGN-FORGED: Do not modify via parallel subagents. Version-locked at forge time.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from dataclasses import dataclass, field
from typing import Any

# ═══════════════════════════════════════════════════════
# FORGE IDENTITY — tamper detection
# ═══════════════════════════════════════════════════════
FORGE_HASH = "sha256:d1a4f6aa8b3c2e01"
FORGE_VERSION = "v0.1.0"
FORGE_TIME = "2026-06-13T21:00:00+08:00"
FORGE_AUTHORITY = "F13_SOVEREIGN_888"

MAX_CLOCK_SKEW_S = 120
SIGNED_HEADER_NAMES = (
    "X-ArifOS-Human-ID",
    "X-ArifOS-Agent-ID",
    "X-ArifOS-Session-ID",
    "X-ArifOS-Org-ID",
)

_replay_cache: dict[str, float] = {}
_REPLAY_CACHE_MAX = 10000
_REPLAY_TTL_S = 300


# ═══════════════════════════════════════════════════════
# CANONICAL SUBJECT
# ═══════════════════════════════════════════════════════

@dataclass
class StructuredSubject:
    """Resolved identity matching spec v0.1 canonical subject."""
    human_id: str = ""
    agent_id: str = ""
    session_id: str = ""
    org_id: str = ""
    roles: list[str] = field(default_factory=list)
    authenticated: bool = False
    key_id: str = ""
    signature_verified: bool = False
    timestamp_verified: bool = False

    @property
    def subject(self) -> str:
        return self.human_id or "anonymous"

    def to_dict(self) -> dict[str, Any]:
        return {
            "human_id": self.human_id,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "org_id": self.org_id,
            "roles": self.roles,
            "authenticated": self.authenticated,
            "key_id": self.key_id,
        }

    def has_role(self, role: str) -> bool:
        return role in self.roles


class VerificationError(Exception):
    def __init__(self, reason: str, code: str = "IDENTITY_FAILED") -> None:
        super().__init__(reason)
        self.reason = reason
        self.code = code


# ═══════════════════════════════════════════════════════
# CRYPTO
# ═══════════════════════════════════════════════════════

def canonical_signature_base(
    human_id: str, agent_id: str, session_id: str,
    org_id: str, timestamp: str,
) -> bytes:
    return (
        f"human_id={human_id}|"
        f"agent_id={agent_id}|"
        f"session_id={session_id}|"
        f"org_id={org_id}|"
        f"timestamp={timestamp}"
    ).encode("utf-8")


def compute_hmac(secret: str, base: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), base, hashlib.sha256).hexdigest()


def verify_hmac(secret: str, base: bytes, claimed: str) -> bool:
    return hmac.compare_digest(compute_hmac(secret, base), claimed)


def check_timestamp(ts_str: str, max_skew: int = MAX_CLOCK_SKEW_S) -> bool:
    try:
        return abs(time.time() - float(ts_str)) <= max_skew
    except (ValueError, TypeError):
        return False


def _replay_ok(nonce: str) -> bool:
    now = time.time()
    stale = [k for k, v in _replay_cache.items() if now - v > _REPLAY_TTL_S]
    for k in stale:
        _replay_cache.pop(k, None)
    if nonce in _replay_cache:
        return False
    if len(_replay_cache) >= _REPLAY_CACHE_MAX:
        oldest = min(_replay_cache.items(), key=lambda x: x[1])[0]
        _replay_cache.pop(oldest, None)
    _replay_cache[nonce] = now
    return True


# ═══════════════════════════════════════════════════════
# API KEY STORE
# ═══════════════════════════════════════════════════════

class ApiKeyStore:
    """Key registry. Keys stored in-memory for v0.1 dev mode."""

    def __init__(self, keys: list[dict[str, Any]] | None = None) -> None:
        self._entries: dict[str, dict[str, Any]] = {}
        if keys:
            for entry in keys:
                k = entry.get("key") or entry.get("api_key", "")
                if k:
                    self._entries[k] = {
                        "key_id": entry.get("key_id", "unknown"),
                        "human_id": entry.get("human_id", ""),
                        "org_id": entry.get("org_id", ""),
                        "roles": entry.get("roles", []),
                    }

    def lookup(self, api_key: str) -> dict[str, Any] | None:
        return self._entries.get(api_key)

    def add(self, key: str, key_id: str, human_id: str = "",
            org_id: str = "", roles: list[str] | None = None) -> None:
        self._entries[key] = {
            "key_id": key_id, "human_id": human_id,
            "org_id": org_id, "roles": roles or [],
        }

    def revoke(self, key: str) -> bool:
        return self._entries.pop(key, None) is not None


# ═══════════════════════════════════════════════════════
# IDENTITY RESOLVER
# ═══════════════════════════════════════════════════════

class SignedHeaderIdentity:
    """Resolve identity from signed subject headers.

    Usage:
        store = ApiKeyStore([{"key": "dev-key", "key_id": "dev-arif",
                              "human_id": "ARIF", "roles": ["sovereign"]}])
        resolver = SignedHeaderIdentity(store)
        subject = resolver.resolve(request_headers)
    """

    def __init__(self, key_store: ApiKeyStore | None = None) -> None:
        self.store = key_store or ApiKeyStore()

    def resolve(self, headers: dict[str, str]) -> StructuredSubject:
        api_key = self._hdr(headers, "x-arifos-api-key")
        human_id = self._hdr(headers, "x-arifos-human-id")
        agent_id = self._hdr(headers, "x-arifos-agent-id")
        session_id = self._hdr(headers, "x-arifos-session-id")
        org_id = self._hdr(headers, "x-arifos-org-id")
        signature = self._hdr(headers, "x-arifos-signature")
        timestamp = self._hdr(headers, "x-arifos-timestamp")

        if not api_key:
            return StructuredSubject(
                human_id=human_id, agent_id=agent_id,
                session_id=session_id, org_id=org_id,
            )

        entry = self.store.lookup(api_key)
        if entry is None:
            raise VerificationError("Unknown API key", "UNKNOWN_API_KEY")

        if not signature:
            raise VerificationError("Missing X-ArifOS-Signature", "MISSING_SIGNATURE")
        if not timestamp:
            raise VerificationError("Missing X-ArifOS-Timestamp", "MISSING_TIMESTAMP")

        # Timestamp
        subj = StructuredSubject(
            human_id=human_id or entry.get("human_id", ""),
            agent_id=agent_id,
            session_id=session_id,
            org_id=org_id or entry.get("org_id", ""),
            roles=list(entry.get("roles", [])),
            authenticated=True,
            key_id=entry.get("key_id", secrets.token_hex(4)),
            timestamp_verified=check_timestamp(timestamp),
        )

        # Signature (BEFORE replay — correct error order)
        base = canonical_signature_base(
            subj.human_id, subj.agent_id,
            subj.session_id, subj.org_id, timestamp,
        )
        if not verify_hmac(api_key, base, signature):
            raise VerificationError("Invalid HMAC signature", "BAD_SIGNATURE")
        subj.signature_verified = True

        # Replay (AFTER signature validation)
        nonce = f"{api_key[:8]}:{signature[:16]}:{timestamp}"
        if not _replay_ok(nonce):
            raise VerificationError("Replayed signature", "REPLAY_DETECTED")

        return subj

    @staticmethod
    def _hdr(headers: dict[str, str], name: str) -> str:
        lower = name.lower()
        for k, v in headers.items():
            if k.lower() == lower:
                return str(v).strip()
        return ""


# ═══════════════════════════════════════════════════════
# CONVENIENCE: BUILD SIGNED HEADERS
# ═══════════════════════════════════════════════════════

def sign_request(
    api_key: str,
    human_id: str,
    agent_id: str = "agent.local.dev",
    session_id: str = "SEAL-local-001",
    org_id: str = "arif-fazil-workspace",
    timestamp: float | None = None,
) -> dict[str, str]:
    """Build signed headers for an MCP gateway request."""
    ts = str(int(timestamp or time.time()))
    base = canonical_signature_base(human_id, agent_id, session_id, org_id, ts)
    sig = compute_hmac(api_key, base)
    return {
        "X-ArifOS-API-Key": api_key,
        "X-ArifOS-Human-ID": human_id,
        "X-ArifOS-Agent-ID": agent_id,
        "X-ArifOS-Session-ID": session_id,
        "X-ArifOS-Org-ID": org_id,
        "X-ArifOS-Signature": sig,
        "X-ArifOS-Timestamp": ts,
    }


# ═══════════════════════════════════════════════════════
# OIDC STUB — v0.2
# ═══════════════════════════════════════════════════════

class OidcAdapterStub:
    """Placeholder for v0.2 OAuth 2.1 / OIDC."""
    configured: bool = False

    def resolve(self, token: str) -> StructuredSubject:
        return StructuredSubject()
