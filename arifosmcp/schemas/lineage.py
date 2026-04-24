"""
Shared lineage contracts for irreversible constitutional actions.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class JudgeSealContract(BaseModel):
    """Structured lineage packet emitted by Judge and consumed by Vault/Forge."""

    constitutional_chain_id: str = Field(default="", description="Lineage ID across Judge→Vault→Forge")
    state_hash: str = Field(default="", description="Stable hash of the judge packet")
    session_id: str | None = Field(default=None)
    actor_id: str | None = Field(default=None)
    candidate: str | None = Field(default=None)
    verdict: str = Field(default="HOLD", description="SEAL | SABAR | VOID | HOLD")
    irreversibility_level: str = Field(default="reversible")
    delta_s: float = Field(default=0.0, description="Judge-estimated entropy impact")
    g_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Lineage genius score")
    epistemic_snapshot: dict[str, Any] = Field(default_factory=dict)
    floor_results: dict[str, str] = Field(default_factory=dict)
    timestamp: str | None = Field(default=None)
