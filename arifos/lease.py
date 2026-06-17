"""
lease.py — Bounded authority for actions.

A lease scopes what an actor can do, for how long, with what
blast-radius. The kernel issues leases via prethink; pretool
verifies them.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Literal

from pydantic import BaseModel, Field


class Lease(BaseModel):
    """
    A bounded authority lease.

    Leases are issued by the kernel after prethink returns ALLOW.
    They scope what actions the actor can take, with what tools,
    until when. Leases expire (TTL) and can be revoked (F13).
    """

    lease_id: str
    actor_id: str
    session_id: str
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    permitted_actions: list[str] = Field(default_factory=list)
    permitted_tools: list[str] = Field(default_factory=list)
    max_blast_radius: str = "LOCAL"
    is_revocable: bool = True
    human_ack_required: bool = False
    metadata: dict[str, str] = Field(default_factory=dict)

    def is_expired(self, now: datetime | None = None) -> bool:
        now = now or datetime.utcnow()
        return now >= self.expires_at

    def covers_action(self, action: str) -> bool:
        if not self.permitted_actions:
            return False  # empty = no actions permitted
        return action in self.permitted_actions or "*" in self.permitted_actions

    def covers_tool(self, tool_name: str) -> bool:
        if not self.permitted_tools:
            return False
        return tool_name in self.permitted_tools or "*" in self.permitted_tools

    @classmethod
    def default_ttl(cls, minutes: int = 30) -> timedelta:
        return timedelta(minutes=minutes)
