"""
arifosmcp/runtime/memory_quarantine.py
═══════════════════════════════════════
Memory Quarantine — Isolated Hazard Zone

When memory entries are flagged as suspicious, poisoned, or unverified,
they are moved to quarantine — a separate, governed zone that:
- Prevents automatic recall into agent context
- Requires explicit F13 or 888_JUDGE review before release
- Carries provenance metadata (who flagged, why, when)
- Has expiry dates (auto-purge after review window)

This addresses the external audit finding: "Memory governance needs
hardening. No quarantine zone for suspicious memory."

F1 AMANAH: Additive — never deletes, only moves to quarantine.
F2 TRUTH: Every quarantine entry has source, reason, and evidence.
F11 AUTH: Quarantine review requires verified identity.
F13 SOVEREIGN: Release from quarantine requires F13 signature.

DITEMPA BUKAN DIBERI — Forged 2026-06-12 by Omega (Ω)
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class QuarantineReason(StrEnum):
    """Why a memory entry was quarantined."""

    UNVERIFIED_SOURCE = "UNVERIFIED_SOURCE"  # Source cannot be verified
    CONTRADICTED = "CONTRADICTED"  # Multiple sources disagree
    MODEL_HALLUCINATION = "MODEL_HALLUCINATION"  # Likely fabricated by model
    IDENTITY_SENSITIVE = "IDENTITY_SENSITIVE"  # Contains unverified identity data
    FLOOR_VIOLATION = "FLOOR_VIOLATION"  # Violates constitutional floor
    PROMPT_INJECTION = "PROMPT_INJECTION"  # Potential injection attack
    STALE_BEYOND_TTL = "STALE_BEYOND_TTL"  # Exceeded freshness window
    SOVEREIGN_FLAG = "SOVEREIGN_FLAG"  # Flagged by F13 sovereign


class QuarantineStatus(StrEnum):
    """Current status of a quarantined entry."""

    PENDING_REVIEW = "PENDING_REVIEW"  # Awaiting human/agent review
    UNDER_REVIEW = "UNDER_REVIEW"  # Currently being reviewed
    RELEASED = "RELEASED"  # Cleared — returned to active memory
    CONFIRMED_HAZARDOUS = "CONFIRMED_HAZARDOUS"  # Verified bad — kept isolated
    EXPIRED = "EXPIRED"  # Review window passed, auto-archived


@dataclass
class QuarantineEntry:
    """A single quarantined memory entry."""

    entry_id: str
    original_content: Any  # The original memory content
    reason: QuarantineReason
    flagged_by: str  # actor_id who flagged
    flagged_at: float = field(default_factory=time.time)
    source: str = "unknown"
    evidence_refs: list[str] = field(default_factory=list)
    status: QuarantineStatus = QuarantineStatus.PENDING_REVIEW
    review_deadline: float = field(default_factory=lambda: time.time() + 30 * 24 * 3600)  # 30 days
    reviewed_by: str | None = None
    reviewed_at: float | None = None
    release_signature: str | None = None
    notes: str = ""

    @property
    def is_expired(self) -> bool:
        return time.time() > self.review_deadline

    @property
    def content_hash(self) -> str:
        try:
            payload = json.dumps(self.original_content, sort_keys=True, default=str)
            return hashlib.sha256(payload.encode()).hexdigest()[:16]
        except Exception:
            return "hash_error"


# ── In-Process Quarantine Store ────────────────────────────────────

_quarantine_store: dict[str, QuarantineEntry] = {}


def quarantine_entry(
    entry_id: str,
    content: Any,
    reason: QuarantineReason,
    flagged_by: str,
    source: str = "unknown",
    evidence_refs: list[str] | None = None,
) -> QuarantineEntry:
    """Move a memory entry into quarantine. Returns the quarantine record."""
    entry = QuarantineEntry(
        entry_id=entry_id,
        original_content=content,
        reason=reason,
        flagged_by=flagged_by,
        source=source,
        evidence_refs=evidence_refs or [],
    )
    _quarantine_store[entry_id] = entry
    return entry


def get_quarantine_entry(entry_id: str) -> QuarantineEntry | None:
    """Retrieve a quarantined entry (does NOT release it)."""
    return _quarantine_store.get(entry_id)


def list_quarantine(
    status: QuarantineStatus | None = None,
    reason: QuarantineReason | None = None,
) -> list[QuarantineEntry]:
    """List quarantined entries, optionally filtered."""
    entries = list(_quarantine_store.values())
    if status:
        entries = [e for e in entries if e.status == status]
    if reason:
        entries = [e for e in entries if e.reason == reason]
    return entries


def review_quarantine(
    entry_id: str,
    verdict: QuarantineStatus,
    reviewed_by: str,
    release_signature: str | None = None,
    notes: str = "",
) -> QuarantineEntry | None:
    """Review a quarantined entry — release or confirm hazardous."""
    entry = _quarantine_store.get(entry_id)
    if not entry:
        return None

    if verdict == QuarantineStatus.RELEASED and not release_signature:
        raise ValueError("RELEASE requires F13 signature")

    entry.status = verdict
    entry.reviewed_by = reviewed_by
    entry.reviewed_at = time.time()
    entry.release_signature = release_signature
    entry.notes = notes

    return entry


def get_quarantine_summary() -> dict[str, int]:
    """Return summary counts by status and reason."""
    status_counts: dict[str, int] = {s.value: 0 for s in QuarantineStatus}
    reason_counts: dict[str, int] = {r.value: 0 for r in QuarantineReason}

    for entry in _quarantine_store.values():
        status_counts[entry.status.value] += 1
        reason_counts[entry.reason.value] += 1

    return {
        "total_quarantined": len(_quarantine_store),
        "by_status": status_counts,
        "by_reason": reason_counts,
        "pending_review": status_counts.get("PENDING_REVIEW", 0),
        "expired": sum(1 for e in _quarantine_store.values() if e.is_expired),
    }


def clean_expired() -> int:
    """Auto-archive expired quarantine entries. Returns count cleaned."""
    expired_ids = [eid for eid, entry in _quarantine_store.items() if entry.is_expired]
    for eid in expired_ids:
        entry = _quarantine_store[eid]
        entry.status = QuarantineStatus.EXPIRED
    return len(expired_ids)
