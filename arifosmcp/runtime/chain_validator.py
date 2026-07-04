"""
Chain Hash Validator — verifies packet chain integrity.
═══════════════════════════════════════════════════════════════════════════════

IRON LAW 3 (CHAIN_OR_VOID): parent_trace_id required or VOID.
IRON LAW 13 (SHADOW_DETECTION): Same parent + different hash → both VOID.

Every packet in the metabolic loop must chain to its parent via SHA-256.
If the chain breaks, the packet is VOID.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


class ChainValidationResult:
    """Result of a chain validation check."""

    def __init__(
        self,
        is_valid: bool,
        reason: str,
        computed_hash: str | None = None,
        expected_hash: str | None = None,
    ) -> None:
        self.is_valid = is_valid
        self.reason = reason
        self.computed_hash = computed_hash
        self.expected_hash = expected_hash

    def __repr__(self) -> str:
        return f"ChainValidationResult(is_valid={self.is_valid}, reason='{self.reason}')"


def compute_chain_hash(parent_hash: str | None, content: dict[str, Any]) -> str:
    """
    Compute SHA-256 chain hash.

    chain_hash = SHA-256(parent_hash + JSON(content))

    For root packets (000_init), parent_hash is None.
    chain_hash = SHA-256(JSON(content))
    """
    content_str = json.dumps(content, sort_keys=True, default=str)
    if parent_hash:
        data = parent_hash + content_str
    else:
        data = content_str
    return hashlib.sha256(data.encode()).hexdigest()


def verify_chain_hash(
    packet: dict[str, Any],
    parent_hash: str | None = None,
) -> ChainValidationResult:
    """
    Verify a packet's chain hash.

    Args:
        packet: The packet dict. Must contain 'content' and optionally 'chain_hash'.
        parent_hash: The parent's chain hash. None for root packets.

    Returns:
        ChainValidationResult with is_valid=True if hash matches.
    """
    declared_hash = packet.get("chain_hash")
    if declared_hash is None:
        return ChainValidationResult(
            is_valid=False,
            reason="IRON LAW 3 VIOLATION: chain_hash missing",
        )

    # Check parent_trace_id (IRON LAW 3)
    parent_trace = packet.get("parent_trace_id")
    stage = packet.get("stage", "")

    # Root packet (000) can have None parent
    if stage == "000":
        if parent_trace is not None:
            return ChainValidationResult(
                is_valid=False,
                reason="Root packet (000) should not have parent_trace_id",
            )
    else:
        if parent_trace is None:
            return ChainValidationResult(
                is_valid=False,
                reason=f"IRON LAW 3 VIOLATION: stage {stage} missing parent_trace_id",
            )

    # Compute expected hash
    content = packet.get("content", {})
    if isinstance(content, str):
        content = json.loads(content)

    expected_hash = compute_chain_hash(parent_hash, content)

    if expected_hash == declared_hash:
        return ChainValidationResult(
            is_valid=True,
            reason="Chain hash verified",
            computed_hash=expected_hash,
            expected_hash=declared_hash,
        )
    else:
        return ChainValidationResult(
            is_valid=False,
            reason=f"IRON LAW 3 VIOLATION: hash mismatch. Expected {expected_hash[:16]}..., got {declared_hash[:16]}...",
            computed_hash=expected_hash,
            expected_hash=declared_hash,
        )


def detect_shadow(
    packets: list[dict[str, Any]],
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """
    IRON LAW 13: Shadow Detection.
    Same parent + different hash → both VOID.

    Returns list of shadow pairs.
    """
    by_parent: dict[str, list[dict[str, Any]]] = {}
    for pkt in packets:
        parent = pkt.get("parent_trace_id", "ROOT")
        by_parent.setdefault(parent, []).append(pkt)

    shadows: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for parent, group in by_parent.items():
        if len(group) < 2:
            continue
        # Check for different hashes with same parent
        for i, a in enumerate(group):
            for b in group[i + 1 :]:
                if a.get("chain_hash") != b.get("chain_hash"):
                    shadows.append((a, b))
    return shadows


class ChainValidator:
    """Validates packet chains and detects shadows."""

    def __init__(self) -> None:
        self._chain: list[dict[str, Any]] = []
        self._last_hash: str | None = None

    def add_packet(self, packet: dict[str, Any]) -> ChainValidationResult:
        """Add a packet to the chain and validate."""
        result = verify_chain_hash(packet, self._last_hash)
        if result.is_valid:
            self._chain.append(packet)
            self._last_hash = packet.get("chain_hash")
        return result

    def verify_integrity(self) -> bool:
        """Verify the entire chain is intact."""
        parent_hash = None
        for pkt in self._chain:
            result = verify_chain_hash(pkt, parent_hash)
            if not result.is_valid:
                return False
            parent_hash = pkt.get("chain_hash")
        return True

    def detect_shadows(self) -> list[tuple[dict[str, Any], dict[str, Any]]]:
        """Check for shadow packets in the chain."""
        return detect_shadow(self._chain)

    @property
    def chain_length(self) -> int:
        return len(self._chain)

    @property
    def tip_hash(self) -> str | None:
        """The hash of the last packet in the chain."""
        return self._last_hash


# Singleton
_validator: ChainValidator | None = None


def get_chain_validator() -> ChainValidator:
    """Get the singleton chain validator."""
    global _validator
    if _validator is None:
        _validator = ChainValidator()
    return _validator


__all__ = [
    "ChainValidator",
    "ChainValidationResult",
    "compute_chain_hash",
    "verify_chain_hash",
    "detect_shadow",
    "get_chain_validator",
]
