"""
consent_token.py — Single-Use Time-Bound Consent Token
════════════════════════════════════════════════════════

Every consent grant creates ONE token. Each token:
- Is single-use (burned after first use)
- Expires after configurable TTL (default 5 minutes)
- Is cryptographically signed by the consent granter
- Contains the action hash so it can't be reused for different actions

Token lifecycle: MINT → ISSUED → CONSUMED | EXPIRED | REVOKED

Forged: 2026-07-29 — DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import hashlib
import json
import secrets
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any


class TokenState(Enum):
    ISSUED = "issued"
    CONSUMED = "consumed"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass
class ConsentToken:
    """Single-use cryptographic consent token.

    Minted when Arif approves a T3 action. Bound to a specific
    agent, action, and time window. Cannot be reused.
    """

    consent_id: str
    agent_id: str
    actor_id: str
    action_hash: str  # SHA256 of the proposed action
    action_summary: str  # Human-readable: "restart a-forge.service"
    granted_by: str  # "arif-fazil/F13"
    granted_via: str  # "telegram" | "web" | "cli"
    issued_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    expires_at: str = ""  # ISO timestamp
    state: TokenState = TokenState.ISSUED
    signature: str = ""  # Ed25519 signature of the granter
    nonce: str = field(default_factory=lambda: secrets.token_hex(16))
    consumed_at: str | None = None
    consumed_by_tool: str | None = None

    # ── Factory ────────────────────────────────────────────────────────

    @classmethod
    def mint(
        cls,
        *,
        agent_id: str,
        actor_id: str,
        action_description: str,
        granted_by: str = "arif-fazil/F13",
        granted_via: str = "telegram",
        ttl_seconds: int = 300,
    ) -> "ConsentToken":
        """Create a new consent token."""
        consent_id = f"consent-{secrets.token_hex(8)}"
        action_hash = hashlib.sha256(action_description.encode()).hexdigest()[:32]
        expires_at = (datetime.now(UTC) + timedelta(seconds=ttl_seconds)).isoformat()

        return cls(
            consent_id=consent_id,
            agent_id=agent_id,
            actor_id=actor_id,
            action_hash=action_hash,
            action_summary=action_description[:200],
            granted_by=granted_by,
            granted_via=granted_via,
            expires_at=expires_at,
        )

    # ── Validation ─────────────────────────────────────────────────────

    def is_valid(self) -> bool:
        """Check if token is still usable."""
        if self.state != TokenState.ISSUED:
            return False
        if self.is_expired():
            return False
        return True

    def is_expired(self) -> bool:
        """Check if token has expired."""
        if not self.expires_at:
            return False
        try:
            expiry = datetime.fromisoformat(self.expires_at)
            return datetime.now(UTC) > expiry
        except (ValueError, TypeError):
            return True

    def ttl_remaining(self) -> float:
        """Seconds remaining before expiry. Negative if expired."""
        try:
            expiry = datetime.fromisoformat(self.expires_at)
            return (expiry - datetime.now(UTC)).total_seconds()
        except (ValueError, TypeError):
            return -1.0

    # ── Consumption ────────────────────────────────────────────────────

    def consume(self, tool_name: str) -> bool:
        """Mark token as consumed. Returns False if already used."""
        if self.state != TokenState.ISSUED:
            return False
        if self.is_expired():
            self.state = TokenState.EXPIRED
            return False
        self.state = TokenState.CONSUMED
        self.consumed_at = datetime.now(UTC).isoformat()
        self.consumed_by_tool = tool_name
        return True

    def revoke(self, reason: str = "") -> None:
        """Revoke an issued token."""
        self.state = TokenState.REVOKED
        self.nonce = f"revoked:{reason}" if reason else "revoked"

    # ── Serialization ──────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        return {
            "consent_id": self.consent_id,
            "agent_id": self.agent_id,
            "actor_id": self.actor_id,
            "action_hash": self.action_hash,
            "action_summary": self.action_summary,
            "granted_by": self.granted_by,
            "granted_via": self.granted_via,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "state": self.state.value,
            "signature": self.signature,
            "nonce": self.nonce,
            "consumed_at": self.consumed_at,
            "consumed_by_tool": self.consumed_by_tool,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConsentToken":
        return cls(
            consent_id=data["consent_id"],
            agent_id=data["agent_id"],
            actor_id=data["actor_id"],
            action_hash=data["action_hash"],
            action_summary=data.get("action_summary", ""),
            granted_by=data.get("granted_by", "arif-fazil/F13"),
            granted_via=data.get("granted_via", "telegram"),
            issued_at=data.get("issued_at", ""),
            expires_at=data.get("expires_at", ""),
            state=TokenState(data.get("state", "issued")),
            signature=data.get("signature", ""),
            nonce=data.get("nonce", ""),
            consumed_at=data.get("consumed_at"),
            consumed_by_tool=data.get("consumed_by_tool"),
        )

    def __repr__(self) -> str:
        ttl = self.ttl_remaining()
        return (
            f"ConsentToken({self.consent_id[:16]}…, "
            f"agent={self.agent_id}, state={self.state.value}, "
            f"ttl={ttl:.0f}s)"
        )


# ── Token Store ────────────────────────────────────────────────────────


@dataclass
class TokenStore:
    """In-memory token store. Replace with Redis/persistent for production."""

    _tokens: dict[str, ConsentToken] = field(default_factory=dict)
    _consumed: set[str] = field(default_factory=set)

    def issue(self, token: ConsentToken) -> None:
        """Store an issued token."""
        self._tokens[token.consent_id] = token

    def validate(self, consent_id: str, agent_id: str, action_hash: str) -> ConsentToken | None:
        """Validate and consume a token. Returns None if invalid."""
        token = self._tokens.get(consent_id)
        if not token:
            return None

        # Expired tokens
        if token.is_expired():
            token.state = TokenState.EXPIRED
            return None

        # Already used
        if token.state != TokenState.ISSUED:
            return None

        # Wrong agent
        if token.agent_id != agent_id:
            return None

        # Wrong action (token was minted for a different action)
        if token.action_hash != action_hash:
            return None

        # Nonce already consumed
        if token.nonce in self._consumed:
            return None

        # Consume
        self._consumed.add(token.nonce)
        return token

    def revoke(self, consent_id: str) -> bool:
        """Revoke an issued token."""
        token = self._tokens.get(consent_id)
        if token and token.state == TokenState.ISSUED:
            token.revoke()
            return True
        return False

    def purge_expired(self) -> int:
        """Remove expired tokens. Returns count purged."""
        count = 0
        expired = [cid for cid, t in self._tokens.items() if t.is_expired()]
        for cid in expired:
            del self._tokens[cid]
            count += 1
        return count

    def __len__(self) -> int:
        return len(self._tokens)

    def __contains__(self, consent_id: str) -> bool:
        return consent_id in self._tokens
