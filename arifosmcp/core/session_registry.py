"""
arifOS Constitutional Kernel — Session Registry
═══════════════════════════════════════════════

HMAC-bound session management and integrity tracking.
Ensures every action is tied to a valid, tamper-proof session.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import hmac
import os
import time
from dataclasses import dataclass


@dataclass
class SessionState:
    session_id: str
    actor_id: str
    created_at: float
    token: str


class SessionRegistry:
    """
    Cryptographic anchor for session identity.
    """

    def __init__(self, secret: str | None = None):
        self._secret = (
            secret or os.getenv("ARIFOS_INTERNAL_SECRET", "default_secret")
        ).encode()
        self._sessions: dict[str, SessionState] = {}

    def create_session(self, actor_id: str) -> SessionState:
        """Create a new signed session."""
        session_id = hashlib.sha256(f"{actor_id}{time.time()}".encode()).hexdigest()[
            :16
        ]
        token = self._sign_session(session_id, actor_id)

        state = SessionState(
            session_id=session_id,
            actor_id=actor_id,
            created_at=time.time(),
            token=token,
        )
        self._sessions[session_id] = state
        return state

    def verify_session(self, session_id: str, token: str) -> bool:
        """Verify session token integrity."""
        state = self._sessions.get(session_id)
        if not state:
            return False

        expected_token = self._sign_session(session_id, state.actor_id)
        return hmac.compare_digest(token, expected_token)

    def _sign_session(self, session_id: str, actor_id: str) -> str:
        """Generate HMAC signature for session."""
        msg = f"{session_id}:{actor_id}".encode()
        return hmac.new(self._secret, msg, hashlib.sha256).hexdigest()

    def get_actor(self, session_id: str) -> str | None:
        """Retrieve actor_id for a valid session."""
        state = self._sessions.get(session_id)
        return state.actor_id if state else None
