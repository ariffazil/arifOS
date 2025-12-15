"""
kernel.py — arifOS v38.2 Constitutional Kernel

Implements time-governed entropy management:
1. check_entropy_rot(packet) — Applies scheduler pulses (SABAR→PARTIAL, PARTIAL→VOID)
2. route_memory() — Routes verdicts to bands with entropy rot applied first
3. SUNSET handling — Lawful revocation (LEDGER → PHOENIX)

Per: spec/arifos_v38_2.yaml
Canon: canon/000_ARIFOS_CANON_v35Omega.md §§6–8

Invariant TIME-1: "Time is a Constitutional Force. Entropy Rot is automatic."
- No SABAR may persist indefinitely; it must either be repaired or escalated.
- No PARTIAL may drift forever; after Phoenix-72 (72h) it must resolve or decay.
- SUNSET provides a lawful path to revoke previously sealed truths.

Author: arifOS Project
Version: v38.2
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# v42: memory is at arifos_core/memory/
from ..memory.policy import Verdict, VERDICT_BAND_ROUTING


# =============================================================================
# v38.2 SCHEDULER CONSTANTS (per spec/arifos_v38_2.yaml)
# =============================================================================

# SABAR_TIMEOUT: After 24 hours, SABAR escalates to PARTIAL
SABAR_TIMEOUT_HOURS: int = 24

# PHOENIX_LIMIT: After 72 hours, PARTIAL decays to VOID (entropy dump)
PHOENIX_LIMIT_HOURS: int = 72


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class VerdictPacket:
    """
    A verdict packet with timestamp for entropy rot calculation.

    Attributes:
        verdict: The current APEX PRIME verdict
        timestamp: When the verdict was issued (ISO format or datetime)
        reference_id: Optional ID linking to original ledger entry (for SUNSET)
        evidence_chain: Evidence supporting the verdict
        metadata: Additional packet metadata
    """
    verdict: str
    timestamp: str  # ISO format timestamp
    reference_id: Optional[str] = None
    evidence_chain: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_age_hours(self) -> float:
        """Calculate age in hours from timestamp to now."""
        try:
            if isinstance(self.timestamp, str):
                ts = datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))
            else:
                ts = self.timestamp
            now = datetime.now(timezone.utc)
            delta = now - ts
            return delta.total_seconds() / 3600.0
        except (ValueError, TypeError):
            # If timestamp is invalid, return 0 (no decay)
            return 0.0


@dataclass
class EntropyRotResult:
    """Result of entropy rot check."""
    original_verdict: str
    final_verdict: str
    rotted: bool
    reason: str
    age_hours: float


@dataclass
class MemoryRouteResult:
    """Result of memory routing with entropy rot applied."""
    verdict: str
    target_bands: List[str]
    entropy_rot_applied: bool
    rot_reason: Optional[str] = None
    sunset_executed: bool = False
    revoked_entry_id: Optional[str] = None


# =============================================================================
# CORE FUNCTIONS
# =============================================================================

def check_entropy_rot(packet: VerdictPacket) -> EntropyRotResult:
    """
    Apply time-governed entropy decay to unresolved verdicts.

    Per spec/arifos_v38_2.yaml::scheduler:
    - If verdict == SABAR and age > 24h → escalate to PARTIAL
    - If verdict == PARTIAL and age > 72h → decay to VOID

    This function does NOT:
    - Alter SEAL, VOID, or 888_HOLD verdicts
    - Produce SUNSET verdicts (SUNSET is policy-triggered, not time-triggered)

    Args:
        packet: VerdictPacket with verdict and timestamp

    Returns:
        EntropyRotResult with original/final verdict and decay info
    """
    verdict_upper = packet.verdict.upper()
    age_hours = packet.get_age_hours()

    # Only SABAR and PARTIAL are subject to entropy rot
    # SEAL, VOID, 888_HOLD, SUNSET remain unchanged
    if verdict_upper not in ("SABAR", "PARTIAL"):
        return EntropyRotResult(
            original_verdict=verdict_upper,
            final_verdict=verdict_upper,
            rotted=False,
            reason="Verdict not subject to entropy rot",
            age_hours=age_hours,
        )

    # SABAR → PARTIAL after 24 hours (SABAR_TIMEOUT)
    if verdict_upper == "SABAR" and age_hours > SABAR_TIMEOUT_HOURS:
        return EntropyRotResult(
            original_verdict="SABAR",
            final_verdict="PARTIAL",
            rotted=True,
            reason=f"SABAR_TIMEOUT: {age_hours:.1f}h > {SABAR_TIMEOUT_HOURS}h → escalate to PARTIAL",
            age_hours=age_hours,
        )

    # PARTIAL → VOID after 72 hours (PHOENIX_LIMIT)
    if verdict_upper == "PARTIAL" and age_hours > PHOENIX_LIMIT_HOURS:
        return EntropyRotResult(
            original_verdict="PARTIAL",
            final_verdict="VOID",
            rotted=True,
            reason=f"PHOENIX_LIMIT: {age_hours:.1f}h > {PHOENIX_LIMIT_HOURS}h → decay to VOID",
            age_hours=age_hours,
        )

    # No decay yet
    return EntropyRotResult(
        original_verdict=verdict_upper,
        final_verdict=verdict_upper,
        rotted=False,
        reason=f"Within time limit ({age_hours:.1f}h)",
        age_hours=age_hours,
    )


def route_memory(
    packet: VerdictPacket,
    apply_entropy_rot: bool = True,
) -> MemoryRouteResult:
    """
    Route verdict to memory bands with entropy rot applied first.

    This function:
    1. Applies check_entropy_rot() if apply_entropy_rot=True
    2. Uses the (possibly-updated) verdict for band routing
    3. Handles SUNSET specially: moves reference from LEDGER → PHOENIX

    Args:
        packet: VerdictPacket with verdict, timestamp, and optional reference_id
        apply_entropy_rot: Whether to apply entropy decay (default True)

    Returns:
        MemoryRouteResult with final verdict and target bands
    """
    verdict = packet.verdict.upper()
    rot_reason = None
    entropy_rot_applied = False

    # Step 1: Apply entropy rot (if enabled)
    if apply_entropy_rot:
        rot_result = check_entropy_rot(packet)
        if rot_result.rotted:
            verdict = rot_result.final_verdict
            rot_reason = rot_result.reason
            entropy_rot_applied = True

    # Step 2: Handle SUNSET revocation
    sunset_executed = False
    revoked_entry_id = None

    if verdict == "SUNSET":
        # SUNSET is a revocation pulse: LEDGER → PHOENIX
        # The reference_id indicates which ledger entry is being revoked
        target_bands = VERDICT_BAND_ROUTING.get("SUNSET", ["PHOENIX"])

        if packet.reference_id:
            revoked_entry_id = packet.reference_id
            sunset_executed = True

        return MemoryRouteResult(
            verdict=verdict,
            target_bands=target_bands,
            entropy_rot_applied=entropy_rot_applied,
            rot_reason=rot_reason,
            sunset_executed=sunset_executed,
            revoked_entry_id=revoked_entry_id,
        )

    # Step 3: Standard verdict routing
    target_bands = VERDICT_BAND_ROUTING.get(verdict, ["LEDGER"])

    # VOID verdicts ONLY go to VOID band (INV-1 enforcement)
    if verdict == "VOID":
        target_bands = ["VOID"]

    return MemoryRouteResult(
        verdict=verdict,
        target_bands=target_bands,
        entropy_rot_applied=entropy_rot_applied,
        rot_reason=rot_reason,
        sunset_executed=False,
        revoked_entry_id=None,
    )


# =============================================================================
# SUNSET EXECUTOR
# =============================================================================

def execute_sunset(
    reference_id: str,
    ledger_band: Any,  # CoolingLedgerBand
    phoenix_band: Any,  # PhoenixCandidatesBand
    reason: str = "Reality changed; truth expired",
) -> Tuple[bool, str]:
    """
    Execute a SUNSET revocation: move entry from LEDGER → PHOENIX.

    SUNSET is the lawful mechanism to un-seal previously canonical memory
    when external reality changes. The evidence chain is preserved.

    Args:
        reference_id: The entry_id to revoke from LEDGER
        ledger_band: The LEDGER band instance
        phoenix_band: The PHOENIX band instance
        reason: Reason for revocation

    Returns:
        Tuple of (success: bool, message: str)
    """
    # Find entry in ledger
    query_result = ledger_band.query(
        filter_fn=lambda e: e.entry_id == reference_id,
        limit=1,
    )

    if not query_result.entries:
        return False, f"Entry {reference_id} not found in LEDGER"

    original_entry = query_result.entries[0]

    # Write to PHOENIX with SUNSET metadata
    phoenix_result = phoenix_band.write(
        content={
            "revoked_from": "LEDGER",
            "original_entry_id": reference_id,
            "original_content": original_entry.content,
            "original_verdict": original_entry.verdict,
            "original_timestamp": original_entry.timestamp,
            "revocation_reason": reason,
        },
        writer_id="SUNSET_EXECUTOR",
        verdict="SUNSET",
        evidence_hash=original_entry.evidence_hash,
        metadata={
            "sunset_type": "revocation",
            "original_hash": original_entry.hash,
            "status": "awaiting_review",
        },
    )

    if not phoenix_result.success:
        return False, f"Failed to write to PHOENIX: {phoenix_result.error}"

    # Mark original entry as revoked (via metadata update if mutable)
    # Note: LEDGER is append-only, so we log the revocation rather than modify
    # The PHOENIX entry serves as the revocation record

    return True, f"SUNSET executed: {reference_id} moved to PHOENIX ({phoenix_result.entry_id})"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "SABAR_TIMEOUT_HOURS",
    "PHOENIX_LIMIT_HOURS",
    # Data classes
    "VerdictPacket",
    "EntropyRotResult",
    "MemoryRouteResult",
    # Functions
    "check_entropy_rot",
    "route_memory",
    "execute_sunset",
]
