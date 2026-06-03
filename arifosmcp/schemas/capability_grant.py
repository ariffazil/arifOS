"""
Capability Grant — Secret Gateway Schema
═══════════════════════════════════════════════════════════════════════════════

Agents request capabilities, never raw secrets.
The gateway maps capability → provider → secret → execution.

Hard rules:
  - agent_visible_secret is always FALSE.
  - No new tool may call os.getenv("API_KEY") directly.
  - All secret access routes through capability_gateway.resolve().

DITEMPA BUKAN DIBERI — Jurisdiction before intelligence.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class CapabilityProvider(StrEnum):
    """Supported secret providers."""

    COMPOSIO = "composio"
    GITHUB = "github"
    OPENAI = "openai"
    MINIMAX = "minimax"
    BRAVE = "brave"
    TAVILY = "tavily"
    EXA = "exa"
    FIRECRAWL = "firecrawl"
    JINA = "jina"
    SUPABASE = "supabase"
    POSTGRES = "postgres"
    REDIS = "redis"
    QDRANT = "qdrant"
    TELEGRAM = "telegram"
    CUSTOM = "custom"


class CapabilityScope(StrEnum):
    """Standard capability scopes."""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


class CapabilityGrant(BaseModel):
    """
    A granted capability — what an agent is allowed to do, not what it can see.

    The agent never sees the raw secret. It sees:
      CAPABILITY_GRANTED: gmail.fetch_emails

    The gateway resolves:
      gmail.fetch_emails → Composio slug → OAuth token → execute
    """

    capability: str = Field(description="Capability name, e.g. 'gmail.fetch_emails'")
    provider: CapabilityProvider = Field(description="Which provider holds the secret")
    scope: list[str] = Field(default_factory=list, description="Allowed scopes")
    secret_location: str = Field(description="Gateway-internal secret path, e.g. 'gateway://composio/gmail/arif'")
    agent_visible_secret: bool = Field(
        default=False,
        description="HARD DEFAULT FALSE. Agent must never see raw secrets.",
    )
    expires_at: datetime | None = Field(default=None, description="Capability expiry")
    actor_id: str = Field(description="Who this grant is for")
    session_id: str | None = Field(default=None, description="Session binding")

    @field_validator("agent_visible_secret", mode="before")
    @classmethod
    def _force_invisible(cls, v: Any) -> bool:
        """F13-enforced: agents never see raw secrets."""
        if v is True:
            raise ValueError(
                "agent_visible_secret cannot be true — agents must never see raw secrets"
            )
        return False

    def is_expired(self) -> bool:
        """True if this grant has expired."""
        if not self.expires_at:
            return False
        return datetime.now(UTC) > self.expires_at

    def allows_scope(self, scope: str) -> bool:
        """True if the requested scope is granted."""
        if not self.scope:
            return False
        return scope in self.scope or CapabilityScope.ADMIN.value in self.scope

    def to_agent_view(self) -> dict[str, Any]:
        """What the agent sees — capability name only, no secret location."""
        return {
            "capability": self.capability,
            "provider": self.provider.value,
            "scope": self.scope,
            "granted": True,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


class CapabilityRequest(BaseModel):
    """An agent's request for a capability."""

    capability: str = Field(description="Requested capability")
    scope: list[str] = Field(default_factory=list, description="Requested scopes")
    reason: str | None = Field(default=None, description="Why this capability is needed")
    actor_id: str = Field(description="Who is requesting")
    session_id: str | None = Field(default=None, description="Session binding")
