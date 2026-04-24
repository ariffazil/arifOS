"""Session output schemas — 000_INIT"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SessionState(BaseModel):
    session_id: str
    actor_id: str | None = None
    created_at: str | None = None
    stage: str = "000"
    lane: str = "AGI"
    entropy_delta: float = 0.0
    sealed: bool = False


class SessionManifest(BaseModel):
    status: str = "OK"
    tool: str = "arif_session_init"
    session: SessionState | None = None
    result: dict[str, Any] = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: str | None = None
