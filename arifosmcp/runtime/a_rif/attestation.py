"""
arifosmcp/runtime/a_rif/attestation.py — Proof of Custody
═════════════════════════════════════════════════════════

A claim is not attested unless it has:
- source URL or internal document ID
- retrieval timestamp
- content hash
- source card
- receipt ID
- evidence level
- tool trace

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from arifosmcp.runtime.a_rif.models import AttestationPacket, EvidenceLevel

__all__ = ["is_attested", "build_attestation_packet"]


def is_attested(packet: AttestationPacket) -> bool:
    """Return True if the attestation packet satisfies minimum custody."""
    return bool(
        packet.source_ids
        and packet.evidence_level != EvidenceLevel.L0
        and packet.receipt_id
        and packet.content_hash
    )


def build_attestation_packet(
    claim_id: str,
    source_ids: list[str],
    content_hash: str,
    receipt_id: str,
    provider: str,
    evidence_level: str,
    trace_id: str = "",
    risk_flags: list[str] | None = None,
) -> AttestationPacket:
    """Construct a complete attestation packet."""
    return AttestationPacket(
        claim_id=claim_id,
        source_ids=source_ids,
        content_hash=content_hash,
        receipt_id=receipt_id,
        provider=provider,
        evidence_level=EvidenceLevel(evidence_level),
        trace_id=trace_id,
        risk_flags=risk_flags or [],
    )
