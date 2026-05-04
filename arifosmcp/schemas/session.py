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
    actor_signature: str | None = None
    nonce: str | None = None
    signature_verified: bool = False
    constitution_bound: bool = False


class SessionManifest(BaseModel):
    status: str = "OK"
    tool: str = "arif_session_init"
    session: SessionState | None = None
    result: dict[str, Any] = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)
    doctrine: dict[str, Any] | None = None  # DITEMPA BUKAN DIBERI — coded constant
    timestamp: str | None = None
    actor_signature: str | None = None
    nonce: str | None = None
    signature_verified: bool = False
    constitution_bound: bool = False
    invariants_checked: list[str] = Field(default_factory=list)
