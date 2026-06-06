"""
core/vault999/redaction.py — P5 Right to Redact

Implements PARADOX_DOCTRINE_V1 Section 6.

Data Tiers:
  T0 PUBLIC       — No restriction
  T1 INTERNAL     — Redact if contains tokens/keys
  T2 CONFIDENTIAL — Auto-redact on detection. Human confirm for full delete.
  T3 SENSITIVE    — Auto-redact. L13 required for any action.
  T4 CRITICAL     — Auto-redact. L13 required. Cannot be fully deleted.

Redaction preserves hash chain integrity.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone


class DataTier:
    PUBLIC = "T0_PUBLIC"
    INTERNAL = "T1_INTERNAL"
    CONFIDENTIAL = "T2_CONFIDENTIAL"
    SENSITIVE = "T3_SENSITIVE"
    CRITICAL = "T4_CRITICAL"


# Patterns that trigger auto-redaction
_SENSITIVE_PATTERNS = [
    re.compile(r"AWS_SECRET_ACCESS_KEY[=:]\s*\S+", re.IGNORECASE),
    re.compile(r"AWS_ACCESS_KEY_ID[=:]\s*\S+", re.IGNORECASE),
    re.compile(r"PRIVATE_KEY[=:]\s*-----BEGIN", re.IGNORECASE),
    re.compile(r"API_KEY[=:]\s*\S+", re.IGNORECASE),
    re.compile(r"PASSWORD[=:]\s*\S+", re.IGNORECASE),
    re.compile(r"TOKEN[=:]\s*\S+", re.IGNORECASE),
    re.compile(r"SECRET[=:]\s*\S+", re.IGNORECASE),
    re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),  # Credit card
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN
]


@dataclass
class RedactionResult:
    was_redacted: bool
    original_hash: str
    redacted_content: str
    redaction_reason: str
    data_tier: str
    redaction_timestamp: str


def classify_data(content: str) -> str:
    """Classify content into T0-T4 based on sensitivity patterns."""
    if not content:
        return DataTier.PUBLIC

    matches = sum(1 for p in _SENSITIVE_PATTERNS if p.search(content))

    if matches >= 3:
        return DataTier.CRITICAL
    if matches == 2:
        return DataTier.SENSITIVE
    if matches == 1:
        return DataTier.CONFIDENTIAL

    # Check for generic tokens/keys
    if re.search(r"[a-zA-Z0-9_-]{20,}", content):
        return DataTier.INTERNAL

    return DataTier.PUBLIC


def redact_entry(
    content: str,
    entry_index: int,
    authority: str = "AUTO",
) -> RedactionResult:
    """
    Redact sensitive content from a VAULT999 entry.

    Returns a RedactionResult with redacted content and audit metadata.
    Original content is hashed (SHA-256) for integrity; content is destroyed.
    """
    tier = classify_data(content)

    if tier == DataTier.PUBLIC:
        return RedactionResult(
            was_redacted=False,
            original_hash=hashlib.sha256(content.encode()).hexdigest(),
            redacted_content=content,
            redaction_reason="T0_PUBLIC — no restriction",
            data_tier=tier,
            redaction_timestamp=datetime.now(timezone.utc).isoformat(),
        )

    # Compute original hash before destruction
    original_hash = hashlib.sha256(content.encode()).hexdigest()

    # Replace sensitive patterns with redaction markers
    redacted = content
    for pattern in _SENSITIVE_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)

    # If still contains long tokens, mask them
    redacted = re.sub(r"[a-zA-Z0-9_-]{20,}", "[REDACTED-TOKEN]", redacted)

    redaction_reason = f"Auto-redact triggered — {tier}"

    return RedactionResult(
        was_redacted=True,
        original_hash=original_hash,
        redacted_content=redacted,
        redaction_reason=redaction_reason,
        data_tier=tier,
        redaction_timestamp=datetime.now(timezone.utc).isoformat(),
    )


def can_fully_delete(tier: str, has_f13_authority: bool) -> bool:
    """
    Determine if full deletion is permitted.

    Rules per PARADOX_DOCTRINE_V1 Section 6:
      - T0-T2: full deletion permitted with L13
      - T3-T4: cannot be fully deleted, only redacted
    """
    if not has_f13_authority:
        return False
    return tier in (DataTier.PUBLIC, DataTier.INTERNAL, DataTier.CONFIDENTIAL)
