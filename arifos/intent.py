"""
intent.py — What the actor wants to do.

The Intent is the cognition-time declaration. It feeds prethink
and produces a Decision.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from arifos.actor import Actor
from arifos.risk import BlastRadius


class Intent(BaseModel):
    """
    A declared intent. The agent's self-classification of what it
    is about to do.

    Fed to `prethink()`. The kernel returns a Decision that either
    permits, denies, or holds the action.
    """

    action: str  # "edit_file", "delete_file", "publish", etc.
    action_class: str = "OBSERVE"  # ActionClass enum value
    reason: str = ""  # Human-readable explanation
    lane: Literal["OBSERVE", "PLAN", "MUTATE", "EXECUTE"] = "OBSERVE"
    blast_radius: BlastRadius = BlastRadius.NONE
    proposed_tools: list[str] = Field(default_factory=list)
    estimated_tokens: int = 0
    estimated_time_seconds: int = 0
    actor: Actor
    session_id: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)
