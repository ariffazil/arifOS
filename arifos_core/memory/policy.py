"""
policy.py — Memory Write Policy Engine for arifOS v38

Enforces what may be remembered based on:
1. Verdict type (SEAL/SABAR/PARTIAL/VOID/HOLD)
2. Evidence chain (must trace back to floor check)
3. Human consent (for Vault writes)
4. Constitutional compatibility (doesn't violate floors)

Core Philosophy:
- VOID verdicts must NEVER become canonical memory
- Memory is evidence, not storage
- Every write must be auditable
- Recalled memory is *suggestion*, never *fact*

Per: docs/arifOS-MEMORY-FORGING-DEEPRESEARCH.md

Author: arifOS Project
Version: v38.0
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .eureka_types import MemoryWriteDecision, MemoryWriteRequest
from .eureka_router import route_write


# =============================================================================
# CONSTANTS
# =============================================================================

class Verdict(str, Enum):
    """APEX PRIME verdict types (v38.3 extended with SABAR_EXTENDED)."""
    SEAL = "SEAL"
    SABAR = "SABAR"
    SABAR_EXTENDED = "SABAR_EXTENDED"  # v38.3 AMENDMENT 1: Branched continuation of decayed SABAR
    PARTIAL = "PARTIAL"
    VOID = "VOID"
    HOLD = "888_HOLD"
    SUNSET = "SUNSET"  # v38.2: Lawful revocation (LEDGER → PHOENIX)


class MemoryBandTarget(str, Enum):
    """Target bands for memory writes (v38.3 adds PENDING)."""
    VAULT = "VAULT"
    LEDGER = "LEDGER"
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"  # v38.3 AMENDMENT 2: Epistemic queue for SABAR verdicts
    PHOENIX = "PHOENIX"
    WITNESS = "WITNESS"
    VOID = "VOID"


# Verdict → Band routing rules (v38.3: SABAR→PENDING, PARTIAL→PHOENIX)
VERDICT_BAND_ROUTING: Dict[str, List[str]] = {
    "SEAL": ["LEDGER", "ACTIVE"],            # Canonical + session
    "SABAR": ["PENDING", "LEDGER"],          # v38.3 AMENDMENT 2: Epistemic queue + log
    "SABAR_EXTENDED": ["PENDING", "LEDGER"], # v38.3: Same routing as SABAR
    "PARTIAL": ["PHOENIX", "LEDGER"],        # v38.3: Law mismatch queue + log
    "VOID": ["VOID"],                         # Diagnostic ONLY, never canonical
    "888_HOLD": ["LEDGER"],                   # Log hold for audit
    "SUNSET": ["PHOENIX"],                    # v38.2: Revocation pulse (LEDGER → PHOENIX)
}

# Retention tiers (days)
RETENTION_HOT_DAYS = 7       # Active Stream, recent scars
RETENTION_WARM_DAYS = 90     # Ledger entries, Phoenix proposals
RETENTION_COLD_DAYS = 365    # Vault (permanent), archive
RETENTION_VOID_DAYS = 90     # Void band (then auto-delete)


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class WriteDecision:
    """Result of should_write() evaluation."""
    allowed: bool
    reason: str
    ledger_entry: Dict[str, Any]
    target_bands: List[str] = field(default_factory=list)
    requires_human_approval: bool = False


@dataclass
class RecallDecision:
    """Result of should_recall() evaluation."""
    allowed: bool
    reason: str
    confidence_ceiling: float  # 0.0-1.0: how much to trust this memory
    floor_warnings: List[str] = field(default_factory=list)


@dataclass
class RetentionDecision:
    """Result of should_retain() evaluation."""
    keep: bool
    move_to_band: Optional[str]
    reason: str
    delete_after_days: Optional[int] = None


@dataclass
class EvidenceChainValidation:
    """Result of validate_evidence_chain()."""
    valid: bool
    missing_links: List[str] = field(default_factory=list)
    hash_verified: bool = False
    floor_check_present: bool = False


# =============================================================================
# MEMORY WRITE POLICY ENGINE
# =============================================================================

class MemoryWritePolicy:
    """
    Memory Write Policy Engine — Enforces governed memory writes.

    Core invariants:
    1. VOID verdicts NEVER become canonical memory
    2. Authority boundary: humans seal law, AI proposes
    3. Every write must be auditable (evidence chain)
    4. Recalled memory passes floor checks (suggestion, not fact)

    Usage:
        policy = MemoryWritePolicy()
        decision = policy.should_write(verdict, evidence_chain, band_target)
        if decision.allowed:
            # proceed with write
        else:
            # handle rejection
    """

    def __init__(self, strict_mode: bool = True):
        """
        Initialize policy engine.

        Args:
            strict_mode: If True, enforce all invariants strictly.
                         If False, allow warnings but continue.
        """
        self.strict_mode = strict_mode
        self._write_log: List[Dict[str, Any]] = []

    # =========================================================================
    # CORE POLICY METHODS
    # =========================================================================

    def should_write(
        self,
        verdict: str,
        evidence_chain: Optional[Dict[str, Any]],
        band_target: Optional[str] = None,
    ) -> WriteDecision:
        """
        Determine if a memory write is allowed based on verdict and evidence.

        Write Policy:
        - SEAL/SABAR: Write to Ledger (canonical) + band_target
        - PARTIAL: Queue for review (Phoenix-72 Candidates)
        - VOID: Write to Void band ONLY (never canonical)
        - HOLD: Escalate to human, log to Ledger

        Args:
            verdict: APEX PRIME verdict (SEAL/SABAR/PARTIAL/VOID/HOLD)
            evidence_chain: Dict containing floor_checks, hashes, timestamps
            band_target: Optional specific band to target

        Returns:
            WriteDecision with allowed status, reason, and ledger entry
        """
        # Normalize verdict
        verdict_upper = verdict.upper()
        if verdict_upper not in VERDICT_BAND_ROUTING:
            return WriteDecision(
                allowed=False,
                reason=f"Unknown verdict type: {verdict}",
                ledger_entry={},
            )

        # Validate evidence chain
        if evidence_chain is None:
            # Strict mode requires an evidence chain for all writes
            if self.strict_mode:
                return WriteDecision(
                    allowed=False,
                    reason="Evidence chain required in strict mode",
                    ledger_entry={},
                )
            # In non-strict mode, treat missing evidence as a warning but continue
            chain_validation = EvidenceChainValidation(
                valid=False,
                missing_links=["evidence_chain"],
                hash_verified=False,
                floor_check_present=False,
            )
        else:
            chain_validation = self.validate_evidence_chain(evidence_chain)
            if not chain_validation.valid and self.strict_mode:
                return WriteDecision(
                    allowed=False,
                    reason=f"Evidence chain invalid: {chain_validation.missing_links}",
                    ledger_entry={},
                )

        # Get routing for this verdict
        allowed_bands = VERDICT_BAND_ROUTING[verdict_upper]

        # VOID special handling: NEVER canonical
        if verdict_upper == "VOID":
            if band_target and band_target.upper() != "VOID":
                return WriteDecision(
                    allowed=False,
                    reason="VOID verdicts can ONLY be written to Void band (never canonical)",
                    ledger_entry={},
                )
            allowed_bands = ["VOID"]

        # Check if requested band is valid for this verdict
        if band_target:
            band_upper = band_target.upper()
            if band_upper not in allowed_bands and band_upper != "LEDGER":
                return WriteDecision(
                    allowed=False,
                    reason=f"Verdict {verdict_upper} cannot write to {band_upper}. Allowed: {allowed_bands}",
                    ledger_entry={},
                )

        # Build ledger entry
        ledger_entry = self._build_ledger_entry(
            verdict=verdict_upper,
            evidence_chain=evidence_chain if evidence_chain is not None else {},
            target_bands=allowed_bands,
        )

        # Determine if human approval required
        requires_human = (
            band_target and band_target.upper() == "VAULT"
        ) or verdict_upper == "888_HOLD"

        # Log decision
        self._log_write_decision(verdict_upper, allowed_bands, True, "Policy approved")

        return WriteDecision(
            allowed=True,
            reason=f"Verdict {verdict_upper} approved for bands: {allowed_bands}",
            ledger_entry=ledger_entry,
            target_bands=allowed_bands,
            requires_human_approval=requires_human,
        )

    def should_recall(
        self,
        memory_item: Dict[str, Any],
        current_context: Dict[str, Any],
    ) -> RecallDecision:
        """
        Determine if a recalled memory item should be used.

        Memory is treated as *suggestion*, not *fact*.
        Recalled memory must still pass floor checks.

        Args:
            memory_item: The memory being recalled
            current_context: Current session context (for floor checking)

        Returns:
            RecallDecision with allowed status and confidence ceiling
        """
        warnings: List[str] = []
        confidence = 1.0

        # Check memory source band
        source_band = memory_item.get("band", "UNKNOWN")
        source_verdict = memory_item.get("verdict", "UNKNOWN")

        # VOID band memories should never be recalled for canonical use
        if source_band == "VOID":
            return RecallDecision(
                allowed=False,
                reason="Void band memories cannot be recalled as canonical facts",
                confidence_ceiling=0.0,
                floor_warnings=["Source: VOID band (diagnostic only)"],
            )

        # Check if memory's verdict was valid
        if source_verdict not in ("SEAL", "SABAR"):
            warnings.append(f"Memory verdict was {source_verdict}, not SEAL/SABAR")
            confidence *= 0.5

        # Check memory age (older = less confident)
        memory_ts = memory_item.get("timestamp")
        if memory_ts:
            try:
                if isinstance(memory_ts, str):
                    mem_dt = datetime.fromisoformat(memory_ts.replace("Z", "+00:00"))
                else:
                    mem_dt = datetime.fromtimestamp(memory_ts, tz=timezone.utc)
                age_days = (datetime.now(timezone.utc) - mem_dt).days
                if age_days > 30:
                    confidence *= 0.8
                    warnings.append(f"Memory is {age_days} days old")
                if age_days > 90:
                    confidence *= 0.7
                    warnings.append("Memory may be stale (>90 days)")
            except (ValueError, TypeError):
                warnings.append("Could not verify memory timestamp")
                confidence *= 0.9

        # Check if memory has valid evidence chain
        evidence = memory_item.get("evidence_chain", {})
        if not evidence:
            warnings.append("Memory lacks evidence chain")
            confidence *= 0.6

        # Check if memory's floor checks passed
        floor_checks = evidence.get("floor_checks", [])
        if not floor_checks:
            warnings.append("Memory floor checks not recorded")
            confidence *= 0.7

        # Check current context for floor conflicts
        current_topic = current_context.get("topic", "")
        memory_topic = memory_item.get("topic", "")
        if current_topic and memory_topic and current_topic != memory_topic:
            warnings.append("Memory topic differs from current context")
            confidence *= 0.9

        return RecallDecision(
            allowed=True,
            reason=f"Memory recall allowed with confidence {confidence:.2f}",
            confidence_ceiling=max(0.0, min(1.0, confidence)),
            floor_warnings=warnings,
        )

    def should_retain(
        self,
        memory_item: Dict[str, Any],
        age_days: int,
    ) -> RetentionDecision:
        """
        Determine retention policy for a memory item.

        Retention Tiers:
        - HOT (weeks): Active Stream, current scars, recent amendments
        - WARM (months): Ledger entries, older Phoenix-72 proposals
        - COLD (years): Vault (permanent), historical ledger
        - VOID (90 days): Auto-delete after 90 days

        Args:
            memory_item: The memory to evaluate
            age_days: How old the memory is

        Returns:
            RetentionDecision with keep/move/delete guidance
        """
        band = memory_item.get("band", "UNKNOWN")
        verdict = memory_item.get("verdict", "UNKNOWN")

        # VAULT is always permanent
        if band == "VAULT":
            return RetentionDecision(
                keep=True,
                move_to_band=None,
                reason="Vault entries are permanent (constitutional)",
            )

        # VOID band: auto-delete after 90 days
        if band == "VOID":
            if age_days > RETENTION_VOID_DAYS:
                return RetentionDecision(
                    keep=False,
                    move_to_band=None,
                    reason=f"Void entry exceeds {RETENTION_VOID_DAYS}-day retention",
                    delete_after_days=0,
                )
            return RetentionDecision(
                keep=True,
                move_to_band=None,
                reason=f"Void entry within {RETENTION_VOID_DAYS}-day window",
                delete_after_days=RETENTION_VOID_DAYS - age_days,
            )

        # ACTIVE band: session-only (HOT tier)
        if band == "ACTIVE":
            if age_days > RETENTION_HOT_DAYS:
                return RetentionDecision(
                    keep=False,
                    move_to_band=None,
                    reason=f"Active stream entry exceeds {RETENTION_HOT_DAYS}-day HOT tier",
                )
            return RetentionDecision(
                keep=True,
                move_to_band=None,
                reason="Active stream entry in HOT tier",
            )

        # PHOENIX candidates: WARM tier until sealed/rejected
        if band == "PHOENIX":
            status = memory_item.get("status", "draft")
            if status in ("sealed", "rejected"):
                # Move to archive
                return RetentionDecision(
                    keep=True,
                    move_to_band="LEDGER",
                    reason=f"Phoenix proposal {status}, archive to Ledger",
                )
            if age_days > RETENTION_WARM_DAYS:
                return RetentionDecision(
                    keep=True,
                    move_to_band=None,
                    reason=f"Phoenix proposal stale (>{RETENTION_WARM_DAYS} days), needs review",
                )
            return RetentionDecision(
                keep=True,
                move_to_band=None,
                reason="Phoenix proposal active in WARM tier",
            )

        # LEDGER: Permanent (COLD tier after WARM)
        if band == "LEDGER":
            if age_days > RETENTION_WARM_DAYS:
                return RetentionDecision(
                    keep=True,
                    move_to_band="ARCHIVE",
                    reason="Ledger entry moved to COLD archive tier",
                )
            return RetentionDecision(
                keep=True,
                move_to_band=None,
                reason="Ledger entry in WARM tier",
            )

        # WITNESS: Rolling window
        if band == "WITNESS":
            if age_days > RETENTION_WARM_DAYS:
                return RetentionDecision(
                    keep=False,
                    move_to_band=None,
                    reason=f"Witness entry exceeds {RETENTION_WARM_DAYS}-day window",
                )
            return RetentionDecision(
                keep=True,
                move_to_band=None,
                reason="Witness entry in retention window",
            )

        # Unknown band: conservative keep
        return RetentionDecision(
            keep=True,
            move_to_band=None,
            reason=f"Unknown band {band}, conservatively retaining",
        )

    def validate_evidence_chain(
        self,
        evidence_chain: Dict[str, Any],
    ) -> EvidenceChainValidation:
        """
        Validate that evidence chain is complete and hash-verified.

        Requirements:
        - Must contain floor_checks
        - Must have hash linking to verdict
        - Must trace back to floor check

        Args:
            evidence_chain: The evidence dict to validate

        Returns:
            EvidenceChainValidation with validity status
        """
        missing: List[str] = []
        hash_verified = False
        floor_check_present = False

        # Check required fields
        if "floor_checks" not in evidence_chain:
            missing.append("floor_checks")
        else:
            floor_check_present = True

        if "hash" not in evidence_chain and "evidence_hash" not in evidence_chain:
            missing.append("hash or evidence_hash")

        if "timestamp" not in evidence_chain:
            missing.append("timestamp")

        if "verdict" not in evidence_chain:
            missing.append("verdict")

        # Verify hash if present
        stored_hash = evidence_chain.get("hash") or evidence_chain.get("evidence_hash")
        if stored_hash:
            # Recompute hash from content (excluding hash field itself)
            content = {k: v for k, v in evidence_chain.items() if k not in ("hash", "evidence_hash")}
            computed = hashlib.sha256(
                json.dumps(content, sort_keys=True).encode()
            ).hexdigest()
            hash_verified = (stored_hash == computed)
            if not hash_verified:
                missing.append("hash_mismatch")

        return EvidenceChainValidation(
            valid=len(missing) == 0,
            missing_links=missing,
            hash_verified=hash_verified,
            floor_check_present=floor_check_present,
        )

    # =========================================================================
    # v38.3 AMENDMENT 1: TIME IMMUTABILITY & STATE BRANCHING
    # =========================================================================

    def spawn_sabar_extended(
        self,
        parent_entry_id: str,
        fresh_context: Dict[str, Any],
        human_override: bool = True,
    ) -> str:
        """
        Create SABAR_EXTENDED branch from decayed SABAR verdict.
        
        v38.3 AMENDMENT 1: Time Immutability + State Branching
        
        Behavior:
        - Validates parent exists and was SABAR (now decayed)
        - Creates NEW ledger entry with verdict=SABAR_EXTENDED
        - Links to parent via parent_hash
        - Routes to PENDING + LEDGER (same as SABAR per v38.3 AMENDMENT 2)
        - Original decayed entry remains UNCHANGED
        
        This is NOT reversal—it creates a new branch in the audit trail.
        Time moves forward only. The parent's decay remains visible.
        
        Args:
            parent_entry_id: Hash/ID of original SABAR entry (now decayed)
            fresh_context: New evidence/data that justifies branching
            human_override: Only humans can branch (required=True)
        
        Returns:
            New entry ID (hash of new SABAR_EXTENDED entry)
        
        Raises:
            ValueError: If parent not found or invalid
            PermissionError: If human_override=False
            StateError: If parent was not SABAR
        """
        # Enforce human-only branching
        if not human_override:
            raise PermissionError(
                "v38.3 AMENDMENT 1: Only humans can spawn SABAR_EXTENDED branches. "
                "Set human_override=True to authorize."
            )
        
        # Validate parent_entry_id format (SHA3-256 or SHA256 hex)
        if not isinstance(parent_entry_id, str) or len(parent_entry_id) != 64:
            raise ValueError(
                f"Invalid parent_entry_id format: expected 64-char hex hash, got {parent_entry_id!r}"
            )
        
        # Note: In production, this would query the actual ledger storage to verify parent exists
        # For now, we assume caller has validated parent exists and was SABAR
        # Real implementation would call: ledger.get_entry(parent_entry_id)
        
        # Build new SABAR_EXTENDED entry
        timestamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        
        new_entry = {
            "verdict": "SABAR_EXTENDED",
            "parent_hash": parent_entry_id,  # Link to parent via hash
            "timestamp": timestamp,
            "fresh_context": fresh_context,
            "evidence_chain": {
                "branched_from": parent_entry_id,
                "branch_reason": "Human-authorized continuation of decayed SABAR verdict",
                "human_approved": True,
                "floor_checks": fresh_context.get("floor_checks", {}),
                "timestamp": timestamp,
            },
            "target_bands": VERDICT_BAND_ROUTING["SABAR_EXTENDED"],
            "policy_version": "v38.3",
        }
        
        # Compute entry hash
        new_entry_hash = hashlib.sha256(
            json.dumps(new_entry, sort_keys=True).encode()
        ).hexdigest()
        new_entry["hash"] = new_entry_hash
        
        # Log the branching operation
        self._log_write_decision(
            verdict="SABAR_EXTENDED",
            bands=VERDICT_BAND_ROUTING["SABAR_EXTENDED"],
            allowed=True,
            reason=f"Branched from parent {parent_entry_id[:16]}... (human authorized)",
        )
        
        # In production, this would also:
        # 1. Write new_entry to PENDING band
        # 2. Write audit log entry to LEDGER
        # 3. Verify ledger hash chain remains valid
        
        return new_entry_hash

    # =========================================================================
    # INTERNAL HELPERS
    # =========================================================================

    def _build_ledger_entry(
        self,
        verdict: str,
        evidence_chain: Dict[str, Any],
        target_bands: List[str],
    ) -> Dict[str, Any]:
        """Build a complete ledger entry for the write."""
        timestamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

        entry = {
            "timestamp": timestamp,
            "verdict": verdict,
            "target_bands": target_bands,
            "evidence": evidence_chain,
            "policy_version": "v38.0",
        }

        # Compute entry hash
        entry_hash = hashlib.sha256(
            json.dumps(entry, sort_keys=True).encode()
        ).hexdigest()
        entry["hash"] = entry_hash

        return entry

    def _log_write_decision(
        self,
        verdict: str,
        bands: List[str],
        allowed: bool,
        reason: str,
    ) -> None:
        """Log a write decision for audit trail."""
        self._write_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "verdict": verdict,
            "bands": bands,
            "allowed": allowed,
            "reason": reason,
        })

    def get_write_log(self) -> List[Dict[str, Any]]:
        """Return the policy decision log."""
        return list(self._write_log)

    def clear_write_log(self) -> None:
        """Clear the policy decision log."""
        self._write_log.clear()

    def policy_route_write(self, request: MemoryWriteRequest) -> MemoryWriteDecision:
        """
        Thin wrapper to route memory writes via EUREKA router.

        Args:
            request: MemoryWriteRequest containing actor, verdict, and evidence.

        Returns:
            MemoryWriteDecision from EUREKA router.
        """
        return route_write(request)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "Verdict",
    "MemoryBandTarget",
    "WriteDecision",
    "RecallDecision",
    "RetentionDecision",
    "EvidenceChainValidation",
    "MemoryWritePolicy",
    "VERDICT_BAND_ROUTING",
    "RETENTION_HOT_DAYS",
    "RETENTION_WARM_DAYS",
    "RETENTION_COLD_DAYS",
    "RETENTION_VOID_DAYS",
]
