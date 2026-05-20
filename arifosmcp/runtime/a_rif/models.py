"""
arifosmcp/runtime/a_rif/models.py — Unified A-RIF Pydantic Models
════════════════════════════════════════════════════════════════

Canonical interface for the Truth Substrate.
All A-RIF modules use these models. Domain implementations may extend
but must satisfy this interface.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class EvidenceLevel(str, Enum):
    """Evidence determinism tier (L0-L6)."""

    L0 = "L0"  # Offline / no result / contaminated
    L1 = "L1"  # Search snippets only
    L2 = "L2"  # One source fetched / inspected
    L3 = "L3"  # Multiple independent sources agree
    L4 = "L4"  # Primary / official source inspected
    L5 = "L5"  # Primary + Corroborated + Archived
    L6 = "L6"  # Reproducible data / direct measurement


class ClaimState(str, Enum):
    """Epistemic state of a claim."""

    HYPOTHESIS = "hypothesis"
    SUPPORTED = "supported"
    VERIFIED = "verified"
    VOID = "void"


class SourceCard(BaseModel):
    """Attestation of a single fetched source."""

    url: str
    hash: str = ""
    retrieved_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    status: int = 0
    content_type: str = "text/html"
    risk_flags: list[str] = Field(default_factory=list)
    evidence_level: EvidenceLevel = EvidenceLevel.L0


class ClaimCard(BaseModel):
    """Atomic claim with evidence binding."""

    claim: str
    claim_type: str = "statement"  # fact | interpretation | prediction
    source_ids: list[str] = Field(default_factory=list)
    evidence_level: EvidenceLevel = EvidenceLevel.L0
    confidence: float = 0.0
    contradiction_state: str = "consistent"
    allowed_language_strength: str = "unknown"
    requires_human_judge: bool = False


class EvidenceReceipt(BaseModel):
    """Proof that an observation was made and stored."""

    receipt_id: str = Field(
        default_factory=lambda: f"receipt://bundle/{uuid.uuid4().hex[:12]}"
    )
    provider: str = "unknown"
    bridge: str = "mcp_http_sse"
    timestamp_utc: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    urls_returned: int = 0
    urls_ingested: int = 0
    independent_sources_compared: int = 0
    max_evidence_level: EvidenceLevel = EvidenceLevel.L0
    claimed_evidence_level: EvidenceLevel | None = None
    void_flags: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)


class AttestationPacket(BaseModel):
    """Proof of custody for a claim."""

    claim_id: str = Field(
        default_factory=lambda: f"claim://{uuid.uuid4().hex[:12]}"
    )
    receipt_id: str = ""
    source_ids: list[str] = Field(default_factory=list)
    content_hash: str = ""
    retrieved_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    provider: str = "unknown"
    evidence_level: EvidenceLevel = EvidenceLevel.L0
    trace_id: str = ""
    risk_flags: list[str] = Field(default_factory=list)

    def is_complete(self) -> bool:
        return bool(
            self.source_ids
            and self.evidence_level != EvidenceLevel.L0
            and self.receipt_id
            and self.content_hash
        )


class AbductiveHypothesis(BaseModel):
    """Best explanation from incomplete evidence — never a final truth."""

    hypothesis: str
    explains: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    falsification_tests: list[str] = Field(default_factory=list)
    status: Literal["hypothesis"] = "hypothesis"
    confidence: float = 0.0


class SearchDecisionReceipt(BaseModel):
    """Record of whether a search was executed or skipped."""

    decision_id: str = Field(
        default_factory=lambda: f"decision://{uuid.uuid4().hex[:12]}"
    )
    query: str = ""
    decision: Literal["search", "skip", "hold"] = "hold"
    w_score: float = 0.0
    reason: str = ""
    timestamp_utc: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class ContradictionReport(BaseModel):
    """Output of a contradiction audit."""

    audit_id: str = Field(
        default_factory=lambda: f"audit://{uuid.uuid4().hex[:12]}"
    )
    status: Literal["CONSISTENT", "CONFLICT", "VOID"] = "VOID"
    conflicts: list[dict[str, Any]] = Field(default_factory=list)
    authority_ranking: str = "unknown"
    recommendation: Literal["HOLD", "MERGE", "SUPERSEDE", "VOID"] = "HOLD"


class EntropyReport(BaseModel):
    """Result of an entropy evaluation."""

    before: float = 0.0
    after: float = 0.0
    delta_s: float = 0.0
    recommendation: Literal["continue", "stop", "void"] = "continue"
    reason: str = ""


class QuarantineResult(BaseModel):
    """Result of a security scan on external content."""

    clean: bool = True
    evidence_level: EvidenceLevel = EvidenceLevel.L0
    risk_flags: list[str] = Field(default_factory=list)
    reason: str = ""
