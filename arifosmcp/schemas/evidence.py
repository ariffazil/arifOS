"""Evidence output schema — 222_FETCH (arif_evidence_fetch)"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EvidenceResult(BaseModel):
    url: str | None = None
    content: str = ""
    status: int = 200
    archived: bool = False
    archive_id: str | None = None
    query: str | None = None
    results: list[Any] = Field(default_factory=list)
    verified: bool = False
    note: str | None = None


class EvidenceOutput(BaseModel):
    status: str = "OK"
    tool: str = "arif_evidence_fetch"
    result: EvidenceResult = Field(default_factory=EvidenceResult)
    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: str | None = None
    actor_id: str | None = None
    session_id: str | None = None
    delta_S: float = 0.0
    nine_signal: dict[str, Any] = Field(default_factory=dict)
    output_policy: str = "DOMAIN_SEAL"
    reasons: list[str] = Field(default_factory=list)
    model_config = {"extra": "allow"}
