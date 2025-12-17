"""
vault_manager.py — VAULT-999 Manager for arifOS v37

Enhanced VAULT-999 management with amendment workflow integration per:
- archive/versions/v36_3_omega/v36.3O/canon/VAULT999_ARCHITECTURE_v36.3O.md
- archive/versions/v36_3_omega/v36.3O/canon/VAULT_999_AMENDMENTS_v36.3O.md
- archive/versions/v36_3_omega/v36.3O/spec/phoenix72_amendment_spec_v36.3O.json

Responsibilities:
- Load and expose constitution (L0)
- Provide read-only access to floors and laws
- Coordinate safe amendments via Phoenix-72 (with safety constraints)
- Maintain amendment history with signatures

Author: arifOS Project
Version: v37
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

# Import existing Vault999 for backwards compatibility
from .vault999 import Vault999, VaultConfig, VaultInitializationError, amendment_timestamp


logger = logging.getLogger(__name__)


# =============================================================================
# AMENDMENT DATA STRUCTURES
# =============================================================================

AmendmentStatus = Literal["PROPOSED", "UNDER_REVIEW", "SEALED", "REVOKED", "EXPIRED"]


@dataclass
class SafetyConstraints:
    """Safety constraints for Phoenix-72 amendments."""
    max_delta: float = 0.05  # |ΔF| ≤ 0.05 per cycle (TODO(Arif): confirm)
    cooldown_hours: int = 24  # TODO(Arif): confirm cooldown window
    min_evidence_entries: int = 3

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_delta": self.max_delta,
            "cooldown_hours": self.cooldown_hours,
            "min_evidence_entries": self.min_evidence_entries,
        }


@dataclass
class AmendmentEvidence:
    """Evidence supporting an amendment proposal."""
    ledger_hashes: List[str] = field(default_factory=list)
    scar_ids: List[str] = field(default_factory=list)
    external_refs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ledger_hashes": self.ledger_hashes,
            "scar_ids": self.scar_ids,
            "external_refs": self.external_refs,
        }


@dataclass
class AmendmentRecord:
    """
    A Phoenix-72 amendment record per phoenix72_amendment_spec_v36.3O.json.

    Invariants:
    - amendment_id must be unique
    - Finalized amendments require phoenix72_signature
    - delta_value must respect safety_constraints.max_delta
    """
    amendment_id: str
    epoch: str
    status: AmendmentStatus
    target_floor: str
    target_field: str
    old_value: Any
    new_value: Any
    delta_value: float
    rationale: str
    evidence: AmendmentEvidence
    safety_constraints: SafetyConstraints
    proposed_at: str
    proposed_by: str
    phoenix72_cycle_id: Optional[str] = None
    phoenix72_signature: Optional[str] = None
    sealed_at: Optional[str] = None
    revoked_at: Optional[str] = None
    revocation_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "amendment_id": self.amendment_id,
            "epoch": self.epoch,
            "status": self.status,
            "target_floor": self.target_floor,
            "target_field": self.target_field,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "delta_value": self.delta_value,
            "rationale": self.rationale,
            "evidence": self.evidence.to_dict(),
            "safety_constraints": self.safety_constraints.to_dict(),
            "proposed_at": self.proposed_at,
            "proposed_by": self.proposed_by,
            "phoenix72_cycle_id": self.phoenix72_cycle_id,
            "phoenix72_signature": self.phoenix72_signature,
            "sealed_at": self.sealed_at,
            "revoked_at": self.revoked_at,
            "revocation_reason": self.revocation_reason,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AmendmentRecord":
        evidence = AmendmentEvidence(
            ledger_hashes=data.get("evidence", {}).get("ledger_hashes", []),
            scar_ids=data.get("evidence", {}).get("scar_ids", []),
            external_refs=data.get("evidence", {}).get("external_refs", []),
        )
        constraints = SafetyConstraints(
            max_delta=data.get("safety_constraints", {}).get("max_delta", 0.05),
            cooldown_hours=data.get("safety_constraints", {}).get("cooldown_hours", 24),
            min_evidence_entries=data.get("safety_constraints", {}).get("min_evidence_entries", 3),
        )
        return cls(
            amendment_id=data.get("amendment_id", ""),
            epoch=data.get("epoch", "v37"),
            status=data.get("status", "PROPOSED"),
            target_floor=data.get("target_floor", ""),
            target_field=data.get("target_field", ""),
            old_value=data.get("old_value"),
            new_value=data.get("new_value"),
            delta_value=data.get("delta_value", 0.0),
            rationale=data.get("rationale", ""),
            evidence=evidence,
            safety_constraints=constraints,
            proposed_at=data.get("proposed_at", ""),
            proposed_by=data.get("proposed_by", ""),
            phoenix72_cycle_id=data.get("phoenix72_cycle_id"),
            phoenix72_signature=data.get("phoenix72_signature"),
            sealed_at=data.get("sealed_at"),
            revoked_at=data.get("revoked_at"),
            revocation_reason=data.get("revocation_reason"),
        )


# =============================================================================
# VAULT MANAGER
# =============================================================================

@dataclass
class VaultManagerConfig:
    """Configuration for VaultManager."""
    vault_path: Path = Path("runtime/vault_999/constitution.json")
    amendments_path: Path = Path("runtime/vault_999/amendments.jsonl")
    safety_constraints: SafetyConstraints = field(default_factory=SafetyConstraints)


class VaultManager:
    """
    Enhanced VAULT-999 manager for v37 with Phoenix-72 amendment workflow.

    Extends the base Vault999 with:
    - Structured amendment records per phoenix72_amendment_spec_v36.3O.json
    - Safety constraint enforcement (|ΔF| ≤ 0.05)
    - Amendment history with signatures
    - Cooldown window tracking

    Usage:
        manager = VaultManager()
        floors = manager.get_floors()

        # Propose an amendment (only Phoenix-72 can finalize)
        record = manager.propose_amendment(
            target_floor="F1",
            target_field="truth_min",
            new_value=0.995,
            rationale="Tighten truth floor based on recent failures",
            evidence=AmendmentEvidence(ledger_hashes=["abc123", "def456"]),
        )

        # Finalize (requires Phoenix-72 signature)
        manager.finalize_amendment(record.amendment_id, phoenix72_signature="...")
    """

    def __init__(self, config: Optional[VaultManagerConfig] = None):
        self.config = config or VaultManagerConfig()

        # Initialize underlying vault
        vault_config = VaultConfig(vault_path=self.config.vault_path)
        self._vault = Vault999(vault_config)

        # Amendment history (in-memory cache)
        self._amendments: Dict[str, AmendmentRecord] = {}
        self._load_amendments()

    # =========================================================================
    # AMENDMENT HISTORY
    # =========================================================================

    def _load_amendments(self) -> None:
        """Load amendment history from JSONL file."""
        path = self.config.amendments_path
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            return

        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    record = AmendmentRecord.from_dict(data)
                    self._amendments[record.amendment_id] = record
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"Failed to load amendment: {e}")

    def _save_amendment(self, record: AmendmentRecord) -> None:
        """Append an amendment record to the JSONL file."""
        path = self.config.amendments_path
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")

    # =========================================================================
    # PUBLIC API (delegated to base Vault999)
    # =========================================================================

    def get_constitution(self) -> Dict[str, Any]:
        """Return the full constitution dict."""
        return self._vault.get_constitution()

    def get_floors(self) -> Dict[str, Any]:
        """Return floors object (thresholds & flags)."""
        return self._vault.get_floors()

    def get_physics(self) -> Dict[str, Any]:
        """Return physics object (ΔΩΨ settings)."""
        return self._vault.get_physics()

    def get_laws(self, status: Optional[str] = "ACTIVE") -> List[Dict[str, Any]]:
        """Return list of laws."""
        return self._vault.get_laws(status)

    def list_amendments(self) -> List[AmendmentRecord]:
        """Return all amendments."""
        return list(self._amendments.values())

    def get_amendment(self, amendment_id: str) -> Optional[AmendmentRecord]:
        """Get a specific amendment by ID."""
        return self._amendments.get(amendment_id)

    # =========================================================================
    # AMENDMENT WORKFLOW (Phoenix-72 Integration)
    # =========================================================================

    def propose_amendment(
        self,
        target_floor: str,
        target_field: str,
        new_value: Any,
        rationale: str,
        evidence: AmendmentEvidence,
        proposed_by: str = "Phoenix72",
    ) -> Tuple[bool, AmendmentRecord, List[str]]:
        """
        Propose a new amendment.

        This does NOT apply the amendment - only the Phoenix-72 controller
        can finalize and apply amendments via finalize_amendment().

        Args:
            target_floor: Floor ID (F1-F9)
            target_field: Field to modify (e.g., "truth_min")
            new_value: New value for the field
            rationale: Reason for the amendment
            evidence: Evidence supporting the amendment
            proposed_by: Proposer identity

        Returns:
            Tuple of (success, AmendmentRecord, list_of_validation_errors)
        """
        errors: List[str] = []

        # Get current value
        floors = self.get_floors()
        old_value = floors.get(target_field)

        if old_value is None:
            errors.append(f"Target field '{target_field}' not found in floors")
            # Create a stub record for error case
            record = AmendmentRecord(
                amendment_id=f"INVALID-{datetime.now(timezone.utc).timestamp():.0f}",
                epoch="v37",
                status="PROPOSED",
                target_floor=target_floor,
                target_field=target_field,
                old_value=None,
                new_value=new_value,
                delta_value=0.0,
                rationale=rationale,
                evidence=evidence,
                safety_constraints=self.config.safety_constraints,
                proposed_at=datetime.now(timezone.utc).isoformat(),
                proposed_by=proposed_by,
            )
            return (False, record, errors)

        # Compute delta
        try:
            delta_value = abs(float(new_value) - float(old_value))
        except (ValueError, TypeError):
            delta_value = 1.0 if new_value != old_value else 0.0

        # Safety constraint: |ΔF| ≤ max_delta
        if delta_value > self.config.safety_constraints.max_delta:
            errors.append(
                f"Delta {delta_value:.4f} exceeds safety cap "
                f"{self.config.safety_constraints.max_delta}"
            )

        # Evidence requirement
        total_evidence = (
            len(evidence.ledger_hashes) +
            len(evidence.scar_ids) +
            len(evidence.external_refs)
        )
        if total_evidence < self.config.safety_constraints.min_evidence_entries:
            errors.append(
                f"Insufficient evidence: {total_evidence} < "
                f"{self.config.safety_constraints.min_evidence_entries} required"
            )

        # Check cooldown
        cooldown_error = self._check_cooldown(target_field)
        if cooldown_error:
            errors.append(cooldown_error)

        # Generate amendment ID
        ts = datetime.now(timezone.utc).timestamp()
        content = f"{target_floor}:{target_field}:{new_value}:{ts}"
        amendment_id = f"AMEND-{hashlib.sha256(content.encode()).hexdigest()[:12]}"

        record = AmendmentRecord(
            amendment_id=amendment_id,
            epoch="v37",
            status="PROPOSED",
            target_floor=target_floor,
            target_field=target_field,
            old_value=old_value,
            new_value=new_value,
            delta_value=delta_value,
            rationale=rationale,
            evidence=evidence,
            safety_constraints=self.config.safety_constraints,
            proposed_at=datetime.now(timezone.utc).isoformat(),
            proposed_by=proposed_by,
        )

        # Store in memory
        self._amendments[amendment_id] = record

        # Persist (even with errors - for audit trail)
        self._save_amendment(record)

        return (len(errors) == 0, record, errors)

    def _check_cooldown(self, target_field: str) -> Optional[str]:
        """Check if the target field is still in cooldown from a recent amendment."""
        cooldown_hours = self.config.safety_constraints.cooldown_hours
        cutoff = datetime.now(timezone.utc).timestamp() - (cooldown_hours * 3600)

        for record in self._amendments.values():
            if record.target_field != target_field:
                continue
            if record.status != "SEALED":
                continue

            try:
                sealed_ts = datetime.fromisoformat(
                    record.sealed_at.replace("Z", "+00:00")
                ).timestamp() if record.sealed_at else 0
            except (ValueError, AttributeError):
                continue

            if sealed_ts > cutoff:
                hours_remaining = (sealed_ts + (cooldown_hours * 3600) - datetime.now(timezone.utc).timestamp()) / 3600
                return (
                    f"Field '{target_field}' is in cooldown. "
                    f"Last amendment sealed at {record.sealed_at}. "
                    f"{hours_remaining:.1f} hours remaining."
                )

        return None

    def finalize_amendment(
        self,
        amendment_id: str,
        phoenix72_signature: str,
        phoenix72_cycle_id: Optional[str] = None,
    ) -> Tuple[bool, List[str]]:
        """
        Finalize and apply an amendment.

        This is the ONLY path to modify constitutional floors.
        Must be called by Phoenix-72 controller with a valid signature.

        Args:
            amendment_id: ID of the amendment to finalize
            phoenix72_signature: Signature from Phoenix-72
            phoenix72_cycle_id: Optional cycle ID

        Returns:
            Tuple of (success, list_of_errors)
        """
        errors: List[str] = []

        record = self._amendments.get(amendment_id)
        if record is None:
            return (False, [f"Amendment not found: {amendment_id}"])

        if record.status != "PROPOSED":
            return (False, [f"Amendment status is {record.status}, expected PROPOSED"])

        if not phoenix72_signature:
            return (False, ["Phoenix-72 signature is required"])

        # Apply the change
        try:
            self._vault.update_floors(
                new_floors={**self.get_floors(), record.target_field: record.new_value},
                phoenix_id=amendment_id,
            )
        except Exception as e:
            return (False, [f"Failed to apply amendment: {e}"])

        # Update record
        record.status = "SEALED"
        record.phoenix72_signature = phoenix72_signature
        record.phoenix72_cycle_id = phoenix72_cycle_id
        record.sealed_at = datetime.now(timezone.utc).isoformat()

        # Persist updated record
        self._save_amendment(record)

        logger.info(f"Amendment {amendment_id} finalized: {record.target_field} = {record.new_value}")

        return (True, [])

    def revoke_amendment(
        self,
        amendment_id: str,
        reason: str,
        phoenix72_signature: str,
    ) -> Tuple[bool, List[str]]:
        """
        Revoke a proposed amendment before it's finalized.

        Args:
            amendment_id: ID of the amendment to revoke
            reason: Reason for revocation
            phoenix72_signature: Signature from Phoenix-72

        Returns:
            Tuple of (success, list_of_errors)
        """
        record = self._amendments.get(amendment_id)
        if record is None:
            return (False, [f"Amendment not found: {amendment_id}"])

        if record.status not in ("PROPOSED", "UNDER_REVIEW"):
            return (False, [f"Cannot revoke amendment with status {record.status}"])

        record.status = "REVOKED"
        record.revoked_at = datetime.now(timezone.utc).isoformat()
        record.revocation_reason = reason
        record.phoenix72_signature = phoenix72_signature

        self._save_amendment(record)

        logger.info(f"Amendment {amendment_id} revoked: {reason}")

        return (True, [])


# =============================================================================
# PUBLIC EXPORTS
# =============================================================================

__all__ = [
    # Config
    "VaultManagerConfig",
    # Data structures
    "AmendmentStatus",
    "SafetyConstraints",
    "AmendmentEvidence",
    "AmendmentRecord",
    # Manager
    "VaultManager",
    # Re-exports from vault999
    "Vault999",
    "VaultConfig",
    "VaultInitializationError",
]
