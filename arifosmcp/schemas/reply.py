"""Reply output schema — 444r_REPLY (arif_reply_compose)"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ReplyResult(BaseModel):
    message: str | None = None
    formatted: str | None = None
    style: str | None = None
    tone: str | None = None
    citations: list[str] = Field(default_factory=list)
    nudge: str | None = None


class ReplyOutput(BaseModel):
    status: str = "OK"
    tool: str = "arif_reply_compose"
    result: ReplyResult = Field(default_factory=ReplyResult)
    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: str | None = None
    actor_id: str | None = None
    session_id: str | None = None
    delta_S: float = 0.0
    nine_signal: dict[str, Any] = Field(default_factory=dict)
    output_policy: str = "DOMAIN_SEAL"
    reasons: list[str] = Field(default_factory=list)
    model_config = {"extra": "forbid"}
