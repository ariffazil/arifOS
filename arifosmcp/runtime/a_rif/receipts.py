"""
arifosmcp/runtime/a_rif/receipts.py — Evidence Receipt Builder
══════════════════════════════════════════════════════════════

Constructs SourceCards and EvidenceReceipts from fetch results.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime

from arifosmcp.runtime.a_rif.models import EvidenceLevel, EvidenceReceipt, SourceCard

__all__ = ["build_source_card", "build_evidence_receipt"]


def build_source_card(
    url: str,
    raw_content: str,
    fetch_status: int,
    risk_flags: list[str] | None = None,
) -> SourceCard:
    """Build a SourceCard from fetched content."""
    content_hash = hashlib.sha256(raw_content.encode()).hexdigest()[:16] if raw_content else ""
    level = EvidenceLevel.L2 if raw_content and not risk_flags else EvidenceLevel.L0
    if risk_flags and "PROMPT_INJECTION_DETECTED" in risk_flags:
        level = EvidenceLevel.L0

    return SourceCard(
        url=url,
        hash=content_hash,
        retrieved_at=datetime.now(UTC).isoformat(),
        status=fetch_status,
        content_type="text/html",
        risk_flags=risk_flags or [],
        evidence_level=level,
    )


def build_evidence_receipt(
    mode: str,
    provider: str,
    urls_returned: int,
    urls_ingested: int,
    max_evidence_level: EvidenceLevel,
    risk_flags: list[str] | None = None,
    source_card: SourceCard | None = None,
) -> EvidenceReceipt:
    """Build an EvidenceReceipt from fetch/search metadata."""
    return EvidenceReceipt(
        provider=provider,
        bridge="mcp_http_sse",
        urls_returned=urls_returned,
        urls_ingested=urls_ingested,
        independent_sources_compared=0,
        max_evidence_level=max_evidence_level,
        void_flags=[],
        risk_flags=risk_flags or [],
    )
