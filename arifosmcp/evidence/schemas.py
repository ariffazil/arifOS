"""
arifosmcp/evidence/schemas.py — Evidence Receipt Schemas
════════════════════════════════════════════════════════

Pydantic models for F-WEB evidence receipts, aligned to the blueprint:
https://arifOS.github.io/arifOS/FWEB-Retrieval-Framework/

DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EvidenceLevel(str, Enum):
    """Deterministic evidence level (L0-L5). Computed from receipt fields."""

    L0 = "L0"  # Offline only
    L1 = "L1"  # Search snippets
    L2 = "L2"  # URL ingest
    L3 = "L3"  # Multi-source verification
    L4 = "L4"  # Browser-grade inspection
    L5 = "L5"  # Exhaustive deep research


class VoidClassification(str, Enum):
    """Missing data taxonomy (MCAR/MAR/MNAR)."""

    MCAR = "MCAR"  # Missing Completely at Random
    MAR = "MAR"  # Missing at Random
    MNAR = "MNAR"  # Missing Not at Random


class RiskFlag(str, Enum):
    """Security risk flags detected during ingestion."""

    PROMPT_INJECTION = "prompt_injection"
    SSRF_ATTEMPT = "ssrf_attempt"
    SCHEME_BLOCKED = "scheme_blocked"
    REDIRECT_ABUSE = "redirect_abuse"
    SIZE_LIMIT_EXCEEDED = "size_limit_exceeded"
    PRIVATE_IP_ACCESS = "private_ip_access"
    DANGEROUS_DOMAIN = "dangerous_domain"
    INSTRUCTION_EMBEDDED = "instruction_embedded"


class ClaimTriple(BaseModel):
    """Atomic claim extracted from source content."""

    subject: str
    predicate: str
    obj: str
    claim_type: str = "fact"  # fact | interpretation | prediction
    support_span: str | None = None  # Quote or text span supporting claim
    source_hash: str | None = None


class SourceContent(BaseModel):
    """Ingested source with raw + sanitized content."""

    source_hash: str
    url: str
    content_hash: str
    raw_content: str = ""
    sanitized_markdown: str = ""
    mime_type: str = "text/html"
    fetch_status: int = 200
    fetched_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    content_length: int = 0
    claims: list[ClaimTriple] = Field(default_factory=list)
    risk_flags: list[RiskFlag] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class EvidenceReceipt(BaseModel):
    """
    F-WEB Evidence Receipt aligned to 15-parameter doctrine.

    Every external query durably logs all 15 parameters ensuring total
    observability. max_evidence_level is deterministic — NOT self-claimed.
    """

    receipt_id: str = Field(default_factory=lambda: f"receipt://web/{uuid.uuid4().hex[:12]}")
    tool: str = "arif_fetch"
    mode: str = "fetch"
    provider: str = "minimax_bridge"
    bridge: str = "mcp_http_sse"
    timestamp_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    session_id: str | None = None
    actor_id: str | None = None

    # Payload logging (params 6-7)
    query_sent: str = ""
    payload_sent_known: bool = True
    payload_sent: str | None = None
    payload_inferred: str | None = None

    # Result metadata (params 8-10)
    result_type: str = "markdown_blob"
    urls_returned: int = 0
    urls_ingested: int = 0

    # Verification depth (params 11-14)
    independent_sources_compared: int = 0
    rendered_inspection: bool = False
    pdf_inspection: bool = False
    screenshot_inspection: bool = False

    # L5 flags (params 11-14)
    deep_research_plan_completed: bool = False
    contradiction_audit_completed: bool = False
    void_report_completed: bool = False

    # Security (param 14)
    risk_flags: list[RiskFlag] = Field(default_factory=list)

    # Evidence level (param 13)
    max_evidence_level: EvidenceLevel = EvidenceLevel.L0
    claimed_evidence_level: EvidenceLevel | None = None

    # Output governance
    void: list[str] = Field(default_factory=list)
    human_judgment_required: bool = False
    validator_verdict: str = "SEAL"

    # Source hashes
    source_hashes: list[str] = Field(default_factory=list)

    # Computed trust
    confidence_label: str = "LOW"

    def compute_max_evidence_level(self) -> EvidenceLevel:
        """
        Deterministic evidence level calculator.
        This is the core F-WEB theorem: evidence level is proven, not claimed.
        """
        if (
            self.deep_research_plan_completed
            and self.contradiction_audit_completed
            and self.void_report_completed
            and self.independent_sources_compared >= 2
        ):
            return EvidenceLevel.L5

        if (
            self.rendered_inspection
            or self.pdf_inspection
            or self.screenshot_inspection
        ):
            return EvidenceLevel.L4

        if self.independent_sources_compared >= 2:
            return EvidenceLevel.L3

        if self.urls_ingested >= 1:
            return EvidenceLevel.L2

        if self.urls_returned >= 1:
            return EvidenceLevel.L1

        return EvidenceLevel.L0

    def validate_sufficiency(self, claimed_level: EvidenceLevel) -> tuple[str, EvidenceLevel]:
        """
        Judge sufficiency: compare claimed vs proven evidence level.

        Returns (verdict, calculated_level).
        verdict: SEAL | HOLD | VOID
        """
        calculated = self.compute_max_evidence_level()

        level_order = {
            EvidenceLevel.L0: 0,
            EvidenceLevel.L1: 1,
            EvidenceLevel.L2: 2,
            EvidenceLevel.L3: 3,
            EvidenceLevel.L4: 4,
            EvidenceLevel.L5: 5,
        }

        if len(self.risk_flags) > 0:
            return ("VOID", calculated)

        if level_order.get(claimed_level, 0) > level_order.get(calculated, 0):
            return ("HOLD", calculated)

        return ("SEAL", calculated)


class ContrastReport(BaseModel):
    """Cross-source conflict matrix for L3+ verification."""

    contrast_id: str = Field(default_factory=lambda: f"contrast://{uuid.uuid4().hex[:12]}")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    sources: list[str] = Field(default_factory=list)  # source_hashes
    claims_compared: int = 0

    # Conflict analysis
    agreements: list[dict[str, Any]] = Field(default_factory=list)
    contradictions: list[dict[str, Any]] = Field(default_factory=list)
    unresolved: list[dict[str, Any]] = Field(default_factory=list)

    # Summary
    confidence_label: str = "UNCERTAIN"
    evidence_level: EvidenceLevel = EvidenceLevel.L3
    human_review_required: bool = False


class VoidReport(BaseModel):
    """Missing data taxonomy report (MCAR/MAR/MNAR)."""

    void_id: str = Field(default_factory=lambda: f"void://{uuid.uuid4().hex[:12]}")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_hashes: list[str] = Field(default_factory=list)

    # Missing data analysis
    missing_fields: list[str] = Field(default_factory=list)
    void_classification: VoidClassification = VoidClassification.MCAR
    correction_factors: dict[str, float] = Field(default_factory=dict)

    # Findings
    impact_assessment: str = ""
    recommendations: list[str] = Field(default_factory=list)
    evidence_level: EvidenceLevel = EvidenceLevel.L2
