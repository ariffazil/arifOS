"""
scar_manager.py — Scar and Witness Management for arifOS v37

Implements scar lifecycle per:
- archive/versions/v36_3_omega/v36.3O/canon/SCARS_PHOENIX_HEALING_v36.3O.md
- archive/versions/v36_3_omega/v36.3O/spec/scar_record_spec_v36.3O.json

Key concepts:
- WITNESS: Unsigned local observations (for early warning, R&D)
- SCAR: Signed canonical negative constraints (can affect verdicts)

Lifecycle: OBSERVATION → PROPOSAL → SEALING → MONITORING → HEALING/DEPRECATION

Invariants:
- Only canonical scars (signed) can affect SEAL/VOID decisions
- Witness entries must NOT directly constrain user-facing behavior
- Healed scars remain in history, just removed from active enforcement

Author: arifOS Project
Version: v37
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple

# Reuse embedding functions from existing scars.py
from .scars import (
    stub_embed,
    cosine_similarity,
    generate_scar_id,
)


logger = logging.getLogger(__name__)


# =============================================================================
# TYPES
# =============================================================================

ScarKind = Literal["WITNESS", "SCAR"]
SeverityLevel = Literal["S1", "S2", "S3", "S4"]
ScarStatus = Literal["PROPOSED", "SEALED", "HEALED", "DEPRECATED"]

# Severity weights per canon
SEVERITY_WEIGHTS: Dict[SeverityLevel, float] = {
    "S1": 1.0,
    "S2": 2.0,
    "S3": 4.0,
    "S4": 8.0,
}


# =============================================================================
# SCAR/WITNESS RECORDS
# =============================================================================

@dataclass
class ScarEvidence:
    """Evidence supporting a scar."""
    ledger_hashes: List[str] = field(default_factory=list)
    external_refs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ledger_hashes": self.ledger_hashes,
            "external_refs": self.external_refs,
        }


@dataclass
class WitnessRecord:
    """
    An unsigned witness observation (local scope).

    Witnesses are for early warning and internal R&D.
    They cannot directly constrain user-facing behavior.
    """
    witness_id: str
    pattern_text: str
    pattern_hash: str
    severity: SeverityLevel
    floors: List[str]
    created_at: str
    created_by: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.pattern_hash:
            self.pattern_hash = hashlib.sha256(self.pattern_text.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "witness_id": self.witness_id,
            "kind": "WITNESS",
            "pattern_text": self.pattern_text,
            "pattern_hash": self.pattern_hash,
            "severity": self.severity,
            "floors": self.floors,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WitnessRecord":
        return cls(
            witness_id=data.get("witness_id", ""),
            pattern_text=data.get("pattern_text", ""),
            pattern_hash=data.get("pattern_hash", ""),
            severity=data.get("severity", "S2"),
            floors=data.get("floors", []),
            created_at=data.get("created_at", ""),
            created_by=data.get("created_by", ""),
            metadata=data.get("metadata", {}),
        )


@dataclass
class ScarRecord:
    """
    A canonical scar (signed negative constraint).

    Scars can affect SEAL/VOID decisions and Phoenix-72 pressure.
    """
    scar_id: str
    pattern_text: str
    pattern_hash: str
    severity: SeverityLevel
    floors: List[str]
    epochs: List[str]
    evidence: ScarEvidence
    phoenix_proposal_ids: List[str]
    status: ScarStatus
    signature: str  # Required for canonical scars
    created_at: str
    created_by: str
    sealed_by: Optional[str] = None
    updated_at: Optional[str] = None
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.pattern_hash:
            self.pattern_hash = hashlib.sha256(self.pattern_text.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scar_id": self.scar_id,
            "kind": "SCAR",
            "pattern_text": self.pattern_text,
            "pattern_hash": self.pattern_hash,
            "severity": self.severity,
            "floors": self.floors,
            "epochs": self.epochs,
            "evidence": self.evidence.to_dict(),
            "phoenix_proposal_ids": self.phoenix_proposal_ids,
            "status": self.status,
            "signature": self.signature,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "sealed_by": self.sealed_by,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScarRecord":
        evidence = ScarEvidence(
            ledger_hashes=data.get("evidence", {}).get("ledger_hashes", []),
            external_refs=data.get("evidence", {}).get("external_refs", []),
        )
        return cls(
            scar_id=data.get("scar_id", ""),
            pattern_text=data.get("pattern_text", ""),
            pattern_hash=data.get("pattern_hash", ""),
            severity=data.get("severity", "S2"),
            floors=data.get("floors", []),
            epochs=data.get("epochs", ["v37"]),
            evidence=evidence,
            phoenix_proposal_ids=data.get("phoenix_proposal_ids", []),
            status=data.get("status", "PROPOSED"),
            signature=data.get("signature", ""),
            created_at=data.get("created_at", ""),
            created_by=data.get("created_by", ""),
            sealed_by=data.get("sealed_by"),
            updated_at=data.get("updated_at"),
            metadata=data.get("metadata", {}),
        )

    def get_pressure_weight(self) -> float:
        """Get severity-based pressure weight for Phoenix-72."""
        return SEVERITY_WEIGHTS.get(self.severity, 1.0)


# =============================================================================
# SCAR MANAGER
# =============================================================================

@dataclass
class ScarManagerConfig:
    """Configuration for ScarManager."""
    witness_index_path: Path = Path("runtime/vault_999/witnesses.jsonl")
    scar_index_path: Path = Path("runtime/vault_999/scars.jsonl")
    embed_fn: Callable[[str], List[float]] = stub_embed
    similarity_threshold: float = 0.7


class ScarManager:
    """
    Manages witness and scar indices per SCARS_PHOENIX_HEALING canon.

    Key features:
    - Separate witness (unsigned) and scar (signed) indices
    - Embedding-based similarity search
    - Severity-weighted pressure calculation for Phoenix-72
    - Healing/deprecation workflow

    Usage:
        manager = ScarManager()

        # Create a witness observation
        witness = manager.observe_pattern(
            pattern_text="suspicious pattern detected",
            severity="S2",
            floors=["F1", "F6"],
        )

        # Promote witness to canonical scar (requires signature)
        scar = manager.seal_scar(
            witness_id=witness.witness_id,
            signature="...",
            sealed_by="Phoenix72",
        )

        # Query for similar patterns
        matches = manager.find_similar_scars("suspicious pattern", top_k=5)

        # Calculate pressure for a floor
        pressure = manager.compute_floor_pressure("F1")
    """

    def __init__(self, config: Optional[ScarManagerConfig] = None):
        self.config = config or ScarManagerConfig()

        # In-memory indices
        self._witnesses: Dict[str, WitnessRecord] = {}
        self._scars: Dict[str, ScarRecord] = {}

        # Load from disk
        self._load_witnesses()
        self._load_scars()

    # =========================================================================
    # PERSISTENCE
    # =========================================================================

    def _load_witnesses(self) -> None:
        """Load witness index from JSONL."""
        path = self.config.witness_index_path
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
                    record = WitnessRecord.from_dict(data)
                    self._witnesses[record.witness_id] = record
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"Failed to load witness: {e}")

    def _load_scars(self) -> None:
        """Load scar index from JSONL."""
        path = self.config.scar_index_path
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
                    record = ScarRecord.from_dict(data)
                    self._scars[record.scar_id] = record
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"Failed to load scar: {e}")

    def _save_witness(self, record: WitnessRecord) -> None:
        """Append a witness record to JSONL."""
        path = self.config.witness_index_path
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")

    def _save_scar(self, record: ScarRecord) -> None:
        """Append a scar record to JSONL."""
        path = self.config.scar_index_path
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")

    # =========================================================================
    # WITNESS OPERATIONS
    # =========================================================================

    def observe_pattern(
        self,
        pattern_text: str,
        severity: SeverityLevel,
        floors: List[str],
        created_by: str = "runtime",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> WitnessRecord:
        """
        Create a new witness observation.

        Witnesses are unsigned and cannot affect verdicts.
        """
        ts = datetime.now(timezone.utc).isoformat()
        witness_id = f"WIT-{generate_scar_id(pattern_text, time.time())}"

        record = WitnessRecord(
            witness_id=witness_id,
            pattern_text=pattern_text,
            pattern_hash="",  # Computed in __post_init__
            severity=severity,
            floors=floors,
            created_at=ts,
            created_by=created_by,
            metadata=metadata or {},
        )

        # Compute embedding
        record.embedding = self.config.embed_fn(pattern_text)

        # Store
        self._witnesses[witness_id] = record
        self._save_witness(record)

        logger.info(f"Observed witness: {witness_id}")
        return record

    def get_witness(self, witness_id: str) -> Optional[WitnessRecord]:
        """Get a witness by ID."""
        return self._witnesses.get(witness_id)

    def list_witnesses(self, floor: Optional[str] = None) -> List[WitnessRecord]:
        """List all witnesses, optionally filtered by floor."""
        if floor is None:
            return list(self._witnesses.values())
        return [w for w in self._witnesses.values() if floor in w.floors]

    # =========================================================================
    # SCAR OPERATIONS
    # =========================================================================

    def seal_scar(
        self,
        witness_id: str,
        signature: str,
        sealed_by: str,
        evidence: Optional[ScarEvidence] = None,
        phoenix_proposal_ids: Optional[List[str]] = None,
    ) -> Tuple[bool, Optional[ScarRecord], Optional[str]]:
        """
        Promote a witness to a canonical scar.

        Requires a signature from Phoenix-72 or human authority.

        Returns:
            Tuple of (success, ScarRecord or None, error message or None)
        """
        if not signature:
            return (False, None, "Signature is required to seal a scar")

        witness = self._witnesses.get(witness_id)
        if witness is None:
            return (False, None, f"Witness not found: {witness_id}")

        ts = datetime.now(timezone.utc).isoformat()
        scar_id = f"SCAR-{generate_scar_id(witness.pattern_text, time.time())}"

        record = ScarRecord(
            scar_id=scar_id,
            pattern_text=witness.pattern_text,
            pattern_hash=witness.pattern_hash,
            severity=witness.severity,
            floors=witness.floors,
            epochs=["v37"],
            evidence=evidence or ScarEvidence(),
            phoenix_proposal_ids=phoenix_proposal_ids or [],
            status="SEALED",
            signature=signature,
            created_at=witness.created_at,
            created_by=witness.created_by,
            sealed_by=sealed_by,
            updated_at=ts,
            embedding=witness.embedding,
            metadata=witness.metadata,
        )

        # Store
        self._scars[scar_id] = record
        self._save_scar(record)

        logger.info(f"Sealed scar: {scar_id} from witness {witness_id}")
        return (True, record, None)

    def create_scar_direct(
        self,
        pattern_text: str,
        severity: SeverityLevel,
        floors: List[str],
        signature: str,
        created_by: str,
        sealed_by: str,
        evidence: Optional[ScarEvidence] = None,
        phoenix_proposal_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Optional[ScarRecord], Optional[str]]:
        """
        Create a canonical scar directly (without witness phase).

        Requires a signature.
        """
        if not signature:
            return (False, None, "Signature is required to create a scar")

        ts = datetime.now(timezone.utc).isoformat()
        scar_id = f"SCAR-{generate_scar_id(pattern_text, time.time())}"

        record = ScarRecord(
            scar_id=scar_id,
            pattern_text=pattern_text,
            pattern_hash="",  # Computed in __post_init__
            severity=severity,
            floors=floors,
            epochs=["v37"],
            evidence=evidence or ScarEvidence(),
            phoenix_proposal_ids=phoenix_proposal_ids or [],
            status="SEALED",
            signature=signature,
            created_at=ts,
            created_by=created_by,
            sealed_by=sealed_by,
            updated_at=ts,
            metadata=metadata or {},
        )

        # Compute embedding
        record.embedding = self.config.embed_fn(pattern_text)

        # Store
        self._scars[scar_id] = record
        self._save_scar(record)

        logger.info(f"Created scar directly: {scar_id}")
        return (True, record, None)

    def get_scar(self, scar_id: str) -> Optional[ScarRecord]:
        """Get a scar by ID."""
        return self._scars.get(scar_id)

    def list_scars(
        self,
        floor: Optional[str] = None,
        status: Optional[ScarStatus] = None,
    ) -> List[ScarRecord]:
        """List all scars, optionally filtered by floor and/or status."""
        result = list(self._scars.values())

        if floor is not None:
            result = [s for s in result if floor in s.floors]

        if status is not None:
            result = [s for s in result if s.status == status]

        return result

    def list_active_scars(self, floor: Optional[str] = None) -> List[ScarRecord]:
        """List only SEALED (active) scars."""
        return self.list_scars(floor=floor, status="SEALED")

    # =========================================================================
    # HEALING/DEPRECATION
    # =========================================================================

    def heal_scar(
        self,
        scar_id: str,
        signature: str,
        reason: str = "",
    ) -> Tuple[bool, Optional[str]]:
        """
        Mark a scar as HEALED.

        Healed scars remain in history but are removed from active enforcement.
        """
        if not signature:
            return (False, "Signature is required to heal a scar")

        scar = self._scars.get(scar_id)
        if scar is None:
            return (False, f"Scar not found: {scar_id}")

        if scar.status != "SEALED":
            return (False, f"Cannot heal scar with status {scar.status}")

        scar.status = "HEALED"
        scar.updated_at = datetime.now(timezone.utc).isoformat()
        scar.metadata["healed_reason"] = reason
        scar.metadata["healed_signature"] = signature

        self._save_scar(scar)
        logger.info(f"Healed scar: {scar_id}")
        return (True, None)

    def deprecate_scar(
        self,
        scar_id: str,
        signature: str,
        reason: str = "",
    ) -> Tuple[bool, Optional[str]]:
        """
        Mark a scar as DEPRECATED.

        Deprecated scars are completely removed from enforcement.
        """
        if not signature:
            return (False, "Signature is required to deprecate a scar")

        scar = self._scars.get(scar_id)
        if scar is None:
            return (False, f"Scar not found: {scar_id}")

        scar.status = "DEPRECATED"
        scar.updated_at = datetime.now(timezone.utc).isoformat()
        scar.metadata["deprecated_reason"] = reason
        scar.metadata["deprecated_signature"] = signature

        self._save_scar(scar)
        logger.info(f"Deprecated scar: {scar_id}")
        return (True, None)

    # =========================================================================
    # SIMILARITY SEARCH
    # =========================================================================

    def find_similar_scars(
        self,
        query: str,
        top_k: int = 5,
        threshold: Optional[float] = None,
        include_healed: bool = False,
    ) -> List[Tuple[ScarRecord, float]]:
        """
        Find scars similar to the query text.

        Returns list of (ScarRecord, similarity_score) tuples.
        """
        threshold = threshold or self.config.similarity_threshold
        query_embedding = self.config.embed_fn(query)

        results: List[Tuple[ScarRecord, float]] = []

        for scar in self._scars.values():
            # Skip non-active unless include_healed
            if not include_healed and scar.status not in ("SEALED",):
                continue

            if scar.embedding is None:
                continue

            sim = cosine_similarity(query_embedding, scar.embedding)
            if sim >= threshold:
                results.append((scar, sim))

        # Sort by similarity descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def find_similar_witnesses(
        self,
        query: str,
        top_k: int = 5,
        threshold: Optional[float] = None,
    ) -> List[Tuple[WitnessRecord, float]]:
        """
        Find witnesses similar to the query text.
        """
        threshold = threshold or self.config.similarity_threshold
        query_embedding = self.config.embed_fn(query)

        results: List[Tuple[WitnessRecord, float]] = []

        for witness in self._witnesses.values():
            if witness.embedding is None:
                continue

            sim = cosine_similarity(query_embedding, witness.embedding)
            if sim >= threshold:
                results.append((witness, sim))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    # =========================================================================
    # PHOENIX-72 PRESSURE
    # =========================================================================

    def compute_floor_pressure(self, floor: str) -> float:
        """
        Compute total scar pressure for a floor.

        Formula from canon:
            S_severity(F) = sum(severity_weight(scar) for scar in scars_affecting(F))
        """
        total = 0.0

        for scar in self._scars.values():
            if scar.status != "SEALED":
                continue
            if floor not in scar.floors:
                continue
            total += scar.get_pressure_weight()

        return total

    def get_all_floor_pressures(self) -> Dict[str, float]:
        """Compute pressure for all floors."""
        floors = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"]
        return {f: self.compute_floor_pressure(f) for f in floors}


# =============================================================================
# PUBLIC EXPORTS
# =============================================================================

__all__ = [
    # Types
    "ScarKind",
    "SeverityLevel",
    "ScarStatus",
    "SEVERITY_WEIGHTS",
    # Records
    "ScarEvidence",
    "WitnessRecord",
    "ScarRecord",
    # Manager
    "ScarManagerConfig",
    "ScarManager",
]
