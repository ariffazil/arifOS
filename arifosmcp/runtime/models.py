"""
Runtime Pydantic Models
═══════════════════════
"""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class ToolRequest(BaseModel):
    tool: str
    params: dict[str, Any] = Field(default_factory=dict)
    session_id: str | None = None
    actor_id: str | None = None


class ToolResponse(BaseModel):
    tool: str
    status: str  # OK | HOLD | VOID | SEAL
    result: dict[str, Any] = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)
    omega_0: float = 0.0


class Verdict(BaseModel):
    code: str  # SEAL | SABAR | VOID | HOLD
    floor: str | None = None
    reason: str = ""
    authorized_by: str | None = None


class SessionState(BaseModel):
    session_id: str
    actor_id: str | None = None
    stage: str = "000"
    lane: str = "AGI"
    floors_ok: list[str] = Field(default_factory=list)
    floors_fail: list[str] = Field(default_factory=list)
    entropy_delta: float = 0.0
    sealed: bool = False
