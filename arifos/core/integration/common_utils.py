"""
common_utils.py — Shared utilities for arifOS v38 integration layer

Provides shared helper functions used across multiple integration modules
to reduce code duplication while preserving semantic clarity.

Key Functions:
- compute_integration_evidence_hash(): Unified evidence hash computation

Core Principle:
Consolidate repetitive utility code without obscuring the audit trail or
merging semantically distinct floor checks.

Author: arifOS Project
Version: v38.0
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Import base function from audit layer
from ..memory.audit import compute_evidence_hash as _compute_evidence_hash_base


# =============================================================================
# SHARED EVIDENCE HASH COMPUTATION
# =============================================================================

def compute_integration_evidence_hash(
    verdict: str,
    content: Dict[str, Any],
    floor_scores: Dict[str, float],
    evidence_sources: Optional[List[str]] = None,
    timestamp: Optional[str] = None,
) -> str:
    """
    Compute evidence hash for integration layer.

    This is the unified implementation used across judge, seal, and scars
    integration modules. It wraps the base compute_evidence_hash from audit.py
    and adds content-specific uniqueness.

    Args:
        verdict: The verdict (SEAL, VOID, SABAR, etc.)
        content: Content being written
        floor_scores: Floor scores (F1-F9)
        evidence_sources: Optional evidence sources
        timestamp: Optional timestamp (defaults to now)

    Returns:
        SHA-256 hash combining base evidence hash + content hash

    Note:
        This function is shared to eliminate duplication, but each integration
        module still maintains semantic clarity about when/why it's called.
    """
    ts = timestamp or datetime.now(timezone.utc).isoformat()

    # Convert floor_scores to floor_checks format expected by audit layer
    floor_checks = [
        {"floor": k, "score": v, "passed": True}
        for k, v in floor_scores.items()
    ]

    # Add content hash for uniqueness across different content
    content_hash = hashlib.sha256(
        json.dumps(content, sort_keys=True, default=str).encode()
    ).hexdigest()[:16]

    # Get base hash from audit layer
    base_hash = _compute_evidence_hash_base(
        floor_checks=floor_checks,
        verdict=verdict,
        timestamp=ts,
    )

    # Combine base hash with content hash for uniqueness
    combined = f"{base_hash}:{content_hash}"
    return hashlib.sha256(combined.encode()).hexdigest()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "compute_integration_evidence_hash",
]
