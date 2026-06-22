"""Evidence output schema — 222_FETCH (arif_fetch)

Chapter 6 Upgrade: CertaintyCap enforces epistemic humility.
No component may claim more certainty than its evidence receipt.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class CertaintyCap(StrEnum):
    """
    Epistemic certainty ceiling.

    OBSERVED    → can say "verified"
    DERIVED     → can say "calculated"
    INTERPRETED → can say "likely"
    SPECULATIVE → can say "possible"
    MYTHIC      → can say "symbolically framed"
    """

    OBSERVED = "verified"
    DERIVED = "calculated"
    INTERPRETED = "likely"
    SPECULATIVE = "possible"
    MYTHIC = "symbolically_framed"


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
    tool: str = "arif_fetch"
    result: EvidenceResult = Field(default_factory=EvidenceResult)
    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: str | None = None
    actor_id: str | None = None
    session_id: str | None = None
    delta_S: float = 0.0
    nine_signal: dict[str, Any] = Field(default_factory=dict)
    output_policy: str = "DOMAIN_SEAL"
    reasons: list[str] = Field(default_factory=list)
    # Chapter 6 Upgrade: epistemic certainty cap
    certainty_cap: CertaintyCap = Field(
        default=CertaintyCap.SPECULATIVE,
        description="Maximum certainty this evidence claim is allowed to express",
    )
    claim_state: str = Field(
        default="UNKNOWN",
        description="OBSERVED | DERIVED | INTERPRETED | SPECULATIVE | MYTHIC",
    )
    model_config = {"extra": "forbid"}
