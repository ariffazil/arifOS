"""Shared runtime state for arifOS Command Center — v0.2 Session Continuity.

Extracted from archive: _archived/root_runtime_pre_migration/sessions.py
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from threading import RLock
from typing import Any

from arifosmcp.apps.command_center.identities import (
    canonicalize_identity_claim,
    is_protected_sovereign_id,
    validate_sovereign_proof,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
_SESSION_TTL_SECONDS = max(300, int(os.getenv("ARIFOS_SESSION_TTL_SECONDS", "86400")))


def _get_signing_secret() -> bytes:
    """Retrieve secret key for session signing."""
    secret = os.getenv("ARIFOS_SESSION_SECRET")
    if not secret:
        secret_file = os.getenv("ARIFOS_SESSION_SECRET_FILE")
        if secret_file and os.path.exists(secret_file):
            try:
                with open(secret_file) as f:
                    secret = f.read().strip()
            except Exception:
                secret = "fallback-ephemeral-secret"  # pragma: allowlist secret
        else:
            secret = "fallback-ephemeral-secret"  # pragma: allowlist secret
    return secret.encode()


# ---------------------------------------------------------------------------
# Session data structures
# ---------------------------------------------------------------------------


@dataclass
class SessionAnchor:
    """Constitutional session identity — extracted from SESSION_ANCHOR_SCHEMA."""

    session_id: str
    actor_id: str
    declared_name: str = ""
    intent: str = ""
    token: str = ""
    floor_audit: dict[str, bool] = field(default_factory=dict)
    created_at: str = ""
    expires_at: str = ""


@dataclass
class RuntimeState:
    """Ephemeral state container with session registry."""

    # Counters (backward compatible)
    session_count: int = 0
    judge_calls: int = 0
    forge_dry_runs: int = 0
    gateway_handshakes: int = 0
    vault_dry_seals: int = 0
    ops_reads: int = 0
    reality_checks: int = 0
    fetch_calls: int = 0
    reason_calls: int = 0
    critique_calls: int = 0
    reply_compositions: int = 0
    memory_recalls: int = 0

    # v0.2: Session registry
    _sessions: dict[str, SessionAnchor] = field(default_factory=dict)
    _actor_session_map: dict[str, str] = field(default_factory=dict)
    _active_session_id: str | None = None
    _lock: RLock = field(default_factory=RLock)

    # Intentionally no secrets, no credentials, no persistent data.

    # -----------------------------------------------------------------------
    # Session lifecycle
    # -----------------------------------------------------------------------

    def init_session(
        self,
        actor_id: str = "anonymous",
        declared_name: str = "",
        intent: str = "",
        proof: dict | str | None = None,
    ) -> SessionAnchor:
        """Initialize a constitutional session with identity binding."""
        with self._lock:
            # Canonicalize identity claim
            canonical = canonicalize_identity_claim(actor_id) or actor_id

            # Protected ID check
            if is_protected_sovereign_id(canonical):
                if not validate_sovereign_proof(canonical, proof):
                    raise PermissionError(
                        f"F11/F13: Protected sovereign ID '{canonical}' requires valid proof."
                    )

            session_id = f"sess_{uuid.uuid4().hex[:16]}"
            now = datetime.now(UTC)
            expires = now + timedelta(seconds=_SESSION_TTL_SECONDS)

            anchor = SessionAnchor(
                session_id=session_id,
                actor_id=canonical,
                declared_name=declared_name or canonical,
                intent=intent or "arifOS Command Center session",
                token=self._sign_session_payload(
                    {
                        "session_id": session_id,
                        "actor_id": canonical,
                        "iat": now.isoformat(),
                        "exp": expires.isoformat(),
                    }
                ),
                floor_audit={"F1": True, "F2": True, "F9": True, "F13": True},
                created_at=now.isoformat(),
                expires_at=expires.isoformat(),
            )

            self._sessions[session_id] = anchor
            self._actor_session_map[canonical] = session_id
            self._active_session_id = session_id
            self.session_count += 1
            return anchor

    def get_session(self, session_id: str | None = None) -> SessionAnchor | None:
        """Retrieve session by ID, or active session if None."""
        with self._lock:
            sid = session_id or self._active_session_id
            if not sid:
                return None
            return self._sessions.get(sid)

    def verify_session_token(self, token: str) -> dict[str, Any] | None:
        """Verify and decode a signed session token."""
        try:
            if "." not in token:
                return None
            b64_payload, sig = token.split(".", 1)
            expected_sig = hmac.new(
                _get_signing_secret(), b64_payload.encode(), hashlib.sha256
            ).hexdigest()[:16]
            if not hmac.compare_digest(sig, expected_sig):
                return None

            missing_padding = len(b64_payload) % 4
            if missing_padding:
                b64_payload += "=" * (4 - missing_padding)

            payload = json.loads(base64.urlsafe_b64decode(b64_payload).decode())
            exp = datetime.fromisoformat(payload["exp"])
            if datetime.now(UTC) > exp:
                return None
            return payload
        except Exception:
            return None

    def set_active_session(self, session_id: str) -> bool:
        """Set the active session ID."""
        with self._lock:
            if session_id in self._sessions:
                self._active_session_id = session_id
                return True
            return False

    def list_sessions(self) -> list[SessionAnchor]:
        """List all active sessions."""
        with self._lock:
            return list(self._sessions.values())

    def _sign_session_payload(self, payload: dict[str, Any]) -> str:
        """Generate a signed base64 token for distributed continuity."""
        dump = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        b64_payload = base64.urlsafe_b64encode(dump.encode()).decode().rstrip("=")
        sig = hmac.new(_get_signing_secret(), b64_payload.encode(), hashlib.sha256).hexdigest()[:16]
        return f"{b64_payload}.{sig}"


# Global singleton for v0.2. In production this would be injected via lifespan.
_state: RuntimeState = RuntimeState()


def get_state() -> RuntimeState:
    """Return the current runtime state."""
    return _state


def reset_state() -> None:
    """Reset runtime state. Used in tests."""
    global _state
    _state = RuntimeState()
