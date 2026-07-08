"""
actor.py — Who is performing the action.

The actor carries the sovereign identity. Every Decision that
crosses the kernel boundary is traceable to an Actor.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Actor(BaseModel):
    """
    The acting entity — human, agent, or system.

    Every prethink call requires an actor. The actor's authority
    determines what leases they can hold, what floors apply, and
    what blast-radius they can cause.
    """

    actor_id: str
    actor_type: Literal["sovereign", "agent", "system", "external"] = "agent"
    session_id: str | None = None
    lease_id: str | None = None
    trust_tier: Literal["OWNER", "TRUSTED", "PROBATION", "UNTRUSTED"] = "TRUSTED"
    metadata: dict[str, str] = Field(default_factory=dict)

    def is_sovereign(self) -> bool:
        return self.actor_type == "sovereign"

    def is_trusted(self) -> bool:
        return self.trust_tier in ("OWNER", "TRUSTED")
