"""
bands.py — 6 Memory Bands + Router for arifOS v38

Implements the governed memory band architecture:
1. VaultBand (∞ Immutable) — Constitutional law, sealed amendments
2. CoolingLedgerBand (Append-Only) — Every verdict logged
3. ActiveStreamBand (Ephemeral) — Session context, cleared on exit
4. PhoenixCandidatesBand (Pending) — Proposed amendments before seal
5. WitnessBand (Soft Evidence) — Embeddings, RAG, NOT binding facts
6. VoidBand (Diagnostic) — Rejected outputs, scar analysis

Plus MemoryBandRouter for routing writes to correct bands.

Per: docs/arifOS-MEMORY-FORGING-DEEPRESEARCH.md

Author: arifOS Project
Version: v38.0
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

from .eureka_types import MemoryBand as EurekaMemoryBand
from .eureka_types import MemoryWriteDecision, MemoryWriteRequest
from .eureka_store import AppendOnlyJSONLStore, InMemoryStore


# =============================================================================
# CONSTANTS
# =============================================================================

class BandName(str, Enum):
    """Memory band names (v38.3 adds PENDING)."""
    VAULT = "VAULT"
    LEDGER = "LEDGER"
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"  # v38.3 AMENDMENT 2: Epistemic queue for SABAR
    PHOENIX = "PHOENIX"
    WITNESS = "WITNESS"
    VOID = "VOID"


class RetentionTier(str, Enum):
    """Retention tier classifications."""
    HOT = "HOT"      # weeks
    WARM = "WARM"    # months
    COLD = "COLD"    # years/permanent
    VOID = "VOID"    # 90 days then delete


# Band properties
BAND_PROPERTIES: Dict[str, Dict[str, Any]] = {
    "VAULT": {
        "mutable": False,
        "retention": RetentionTier.COLD,
        "retention_days": None,  # Permanent
        "requires_human_seal": True,
        "canonical": True,
    },
    "LEDGER": {
        "mutable": False,
        "retention": RetentionTier.WARM,
        "retention_days": 365,
        "requires_human_seal": False,
        "canonical": True,
    },
    "ACTIVE": {
        "mutable": True,
        "retention": RetentionTier.HOT,
        "retention_days": 7,
        "requires_human_seal": False,
        "canonical": False,
    },
    "PENDING": {
        "mutable": True,
        "retention": RetentionTier.HOT,
        "retention_days": 7,
        "requires_human_seal": False,
        "canonical": False,
        "description": "v38.3 AMENDMENT 2: Epistemic queue for SABAR verdicts",
    },
    "PHOENIX": {
        "mutable": True,
        "retention": RetentionTier.WARM,
        "retention_days": 90,
        "requires_human_seal": True,  # For sealing
        "canonical": False,  # Until sealed
    },
    "WITNESS": {
        "mutable": True,
        "retention": RetentionTier.WARM,
        "retention_days": 30,
        "requires_human_seal": False,
        "canonical": False,
    },
    "VOID": {
        "mutable": True,
        "retention": RetentionTier.VOID,
        "retention_days": 90,
        "requires_human_seal": False,
        "canonical": False,  # NEVER canonical
    },
}

# Who can write to which band
WRITER_PERMISSIONS: Dict[str, List[str]] = {
    "APEX_PRIME": ["LEDGER", "VOID"],
    "111_SENSE": ["ACTIVE"],
    "222_REFLECT": ["ACTIVE"],
    "333_REASON": ["ACTIVE"],
    "777_FORGE": ["VOID", "ACTIVE"],
    "888_JUDGE": ["VAULT", "PHOENIX", "LEDGER"],
    "PHOENIX_72": ["PHOENIX"],
    "HUMAN": ["VAULT", "PHOENIX", "LEDGER", "ACTIVE"],
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class MemoryEntry:
    """A single memory entry in a band."""
    entry_id: str
    band: str
    content: Dict[str, Any]
    timestamp: str
    writer_id: str = "UNKNOWN"
    verdict: Optional[str] = None
    evidence_hash: Optional[str] = None
    prev_hash: Optional[str] = None
    hash: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "band": self.band,
            "content": self.content,
            "timestamp": self.timestamp,
            "writer_id": self.writer_id,
            "verdict": self.verdict,
            "evidence_hash": self.evidence_hash,
            "prev_hash": self.prev_hash,
            "hash": self.hash,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntry":
        return cls(
            entry_id=data.get("entry_id", str(uuid.uuid4())[:8]),
            band=data.get("band", "UNKNOWN"),
            content=data.get("content", {}),
            timestamp=data.get("timestamp", ""),
            writer_id=data.get("writer_id", "UNKNOWN"),
            verdict=data.get("verdict"),
            evidence_hash=data.get("evidence_hash"),
            prev_hash=data.get("prev_hash"),
            hash=data.get("hash"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class WriteResult:
    """Result of a band write operation."""
    success: bool
    entry_id: Optional[str] = None
    entry_hash: Optional[str] = None
    error: Optional[str] = None


@dataclass
class QueryResult:
    """Result of a band query operation."""
    entries: List[MemoryEntry] = field(default_factory=list)
    total_count: int = 0
    truncated: bool = False


# =============================================================================
# ABSTRACT BASE CLASS
# =============================================================================

class MemoryBand(ABC):
    """
    Abstract base class for memory bands.

    Each band has:
    - name: Band identifier
    - retention_policy: How long entries are kept
    - is_mutable: Whether entries can be modified
    - can_write_direct: Which writers can access
    """

    def __init__(self, name: str, storage_path: Optional[Path] = None):
        self.name = name
        self.properties = BAND_PROPERTIES.get(name, {})
        self.storage_path = storage_path
        self._entries: List[MemoryEntry] = []
        self._last_hash: Optional[str] = None

    @property
    def is_mutable(self) -> bool:
        return bool(self.properties.get("mutable", True))

    @property
    def retention_tier(self) -> RetentionTier:
        tier = self.properties.get("retention", RetentionTier.WARM)
        return tier if isinstance(tier, RetentionTier) else RetentionTier.WARM

    @property
    def retention_days(self) -> Optional[int]:
        days = self.properties.get("retention_days")
        return int(days) if days is not None else None

    @property
    def requires_human_seal(self) -> bool:
        return bool(self.properties.get("requires_human_seal", False))

    @property
    def is_canonical(self) -> bool:
        return bool(self.properties.get("canonical", False))

    @abstractmethod
    def write(
        self,
        content: Dict[str, Any],
        writer_id: str,
        verdict: Optional[str] = None,
        evidence_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> WriteResult:
        """Write an entry to this band."""
        pass

    @abstractmethod
    def query(
        self,
        filter_fn: Optional[Callable[[MemoryEntry], bool]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> QueryResult:
        """Query entries from this band."""
        pass

    def audit_trail(self, entry_id: str) -> List[Dict[str, Any]]:
        """Get audit trail for a specific entry."""
        for entry in self._entries:
            if entry.entry_id == entry_id:
                return [{
                    "entry_id": entry.entry_id,
                    "timestamp": entry.timestamp,
                    "writer_id": entry.writer_id,
                    "hash": entry.hash,
                    "prev_hash": entry.prev_hash,
                }]
        return []

    def _compute_hash(self, entry: MemoryEntry) -> str:
        """Compute SHA-256 hash of entry content."""
        content = {
            "entry_id": entry.entry_id,
            "band": entry.band,
            "content": entry.content,
            "timestamp": entry.timestamp,
            "writer_id": entry.writer_id,
            "verdict": entry.verdict,
            "evidence_hash": entry.evidence_hash,
            "prev_hash": entry.prev_hash,
        }
        return hashlib.sha256(
            json.dumps(content, sort_keys=True).encode()
        ).hexdigest()

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


# =============================================================================
# CONCRETE BAND IMPLEMENTATIONS
# =============================================================================

class VaultBand(MemoryBand):
    """
    VAULT Band — Immutable constitutional memory.

    Properties:
    - Permanent retention (COLD tier)
    - Only 888_Judge (human) can write
    - All writes are historical facts
    - Contains: sealed amendments, canon, decisions
    """

    def __init__(self, storage_path: Optional[Path] = None):
        super().__init__(BandName.VAULT, storage_path)

    def write(
        self,
        content: Dict[str, Any],
        writer_id: str,
        verdict: Optional[str] = None,
        evidence_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> WriteResult:
        # Enforce: only 888_JUDGE or HUMAN can write
        allowed_writers = WRITER_PERMISSIONS.get("888_JUDGE", []) + WRITER_PERMISSIONS.get("HUMAN", [])
        if writer_id not in ("888_JUDGE", "HUMAN") and "VAULT" not in WRITER_PERMISSIONS.get(writer_id, []):
            return WriteResult(
                success=False,
                error=f"Writer {writer_id} not authorized for VAULT band",
            )

        entry = MemoryEntry(
            entry_id=str(uuid.uuid4())[:12],
            band=self.name,
            content=content,
            timestamp=self._now_iso(),
            writer_id=writer_id,
            verdict=verdict,
            evidence_hash=evidence_hash,
            prev_hash=self._last_hash,
            metadata=metadata or {},
        )

        entry.hash = self._compute_hash(entry)
        self._entries.append(entry)
        self._last_hash = entry.hash

        return WriteResult(
            success=True,
            entry_id=entry.entry_id,
            entry_hash=entry.hash,
        )

    def query(
        self,
        filter_fn: Optional[Callable[[MemoryEntry], bool]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> QueryResult:
        entries = self._entries
        if filter_fn:
            entries = [e for e in entries if filter_fn(e)]

        total = len(entries)
        entries = entries[offset:offset + limit]

        return QueryResult(
            entries=entries,
            total_count=total,
            truncated=(offset + limit < total),
        )


class CoolingLedgerBand(MemoryBand):
    """
    COOLING LEDGER Band — Append-only verdict log.

    Properties:
    - Append-only (immutable once written)
    - Hash-chained for integrity
    - APEX PRIME writes every verdict
    - Contains: verdict + metrics + hash + timestamp
    """

    def __init__(self, storage_path: Optional[Path] = None):
        super().__init__(BandName.LEDGER, storage_path)

    def write(
        self,
        content: Dict[str, Any],
        writer_id: str,
        verdict: Optional[str] = None,
        evidence_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> WriteResult:
        # Ledger accepts from APEX_PRIME, 888_JUDGE, HUMAN
        allowed = ["APEX_PRIME", "888_JUDGE", "HUMAN"]
        if writer_id not in allowed:
            return WriteResult(
                success=False,
                error=f"Writer {writer_id} not authorized for LEDGER band",
            )

        entry = MemoryEntry(
            entry_id=str(uuid.uuid4())[:12],
            band=self.name,
            content=content,
            timestamp=self._now_iso(),
            writer_id=writer_id,
            verdict=verdict,
            evidence_hash=evidence_hash,
            prev_hash=self._last_hash,
            metadata=metadata or {},
        )

        entry.hash = self._compute_hash(entry)
        self._entries.append(entry)
        self._last_hash = entry.hash

        return WriteResult(
            success=True,
            entry_id=entry.entry_id,
            entry_hash=entry.hash,
        )

    def query(
        self,
        filter_fn: Optional[Callable[[MemoryEntry], bool]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> QueryResult:
        entries = self._entries
        if filter_fn:
            entries = [e for e in entries if filter_fn(e)]

        total = len(entries)
        entries = entries[offset:offset + limit]

        return QueryResult(
            entries=entries,
            total_count=total,
            truncated=(offset + limit < total),
        )

    def verify_chain(self) -> Tuple[bool, str]:
        """Verify hash chain integrity."""
        prev_hash = None
        for i, entry in enumerate(self._entries):
            # Verify prev_hash links
            if entry.prev_hash != prev_hash:
                return False, f"Entry {i} prev_hash mismatch"

            # Verify entry hash
            computed = self._compute_hash(entry)
            if entry.hash != computed:
                return False, f"Entry {i} hash mismatch"

            prev_hash = entry.hash

        return True, f"Chain verified: {len(self._entries)} entries"


class ActiveStreamBand(MemoryBand):
    """
    ACTIVE STREAM Band — Ephemeral session context.

    Properties:
    - Mutable (session-only)
    - Cleared on exit or timeout
    - 111_SENSE writes context
    - Contains: conversation, session state
    """

    def __init__(self, storage_path: Optional[Path] = None, ttl_seconds: int = 3600):
        super().__init__(BandName.ACTIVE, storage_path)
        self.ttl_seconds = ttl_seconds
        self.session_id = str(uuid.uuid4())[:8]

    def write(
        self,
        content: Dict[str, Any],
        writer_id: str,
        verdict: Optional[str] = None,
        evidence_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> WriteResult:
        # Active accepts from pipeline stages and selected system writers
        allowed = ["111_SENSE", "222_REFLECT", "333_REASON", "777_FORGE", "HUMAN", "888_JUDGE"]
        if writer_id not in allowed:
            return WriteResult(
                success=False,
                error=f"Writer {writer_id} not authorized for ACTIVE band",
            )

        entry = MemoryEntry(
            entry_id=str(uuid.uuid4())[:12],
            band=self.name,
            content=content,
            timestamp=self._now_iso(),
            writer_id=writer_id,
            verdict=verdict,
            evidence_hash=evidence_hash,
            metadata={
                **(metadata or {}),
                "session_id": self.session_id,
                "ttl_seconds": self.ttl_seconds,
            },
        )

        entry.hash = self._compute_hash(entry)
        self._entries.append(entry)

        return WriteResult(
            success=True,
            entry_id=entry.entry_id,
            entry_hash=entry.hash,
        )

    def query(
        self,
        filter_fn: Optional[Callable[[MemoryEntry], bool]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> QueryResult:
        # Filter out expired entries
        now = datetime.now(timezone.utc)
        active_entries = []

        for entry in self._entries:
            try:
                entry_time = datetime.fromisoformat(entry.timestamp.replace("Z", "+00:00"))
                age_seconds = (now - entry_time).total_seconds()
                if age_seconds <= self.ttl_seconds:
                    active_entries.append(entry)
            except (ValueError, TypeError):
                active_entries.append(entry)

        if filter_fn:
            active_entries = [e for e in active_entries if filter_fn(e)]

        total = len(active_entries)
        entries = active_entries[offset:offset + limit]

        return QueryResult(
            entries=entries,
            total_count=total,
            truncated=(offset + limit < total),
        )

    def clear(self) -> int:
        """Clear all entries (session end). Returns count cleared."""
        count = len(self._entries)
        self._entries.clear()
        self.session_id = str(uuid.uuid4())[:8]
        return count


class PendingBand(MemoryBand):
    """
    PENDING Band — Epistemic queue for SABAR verdicts awaiting context.
    
    v38.3 AMENDMENT 2: SABAR/PARTIAL Semantic Separation
    
    Properties:
    - Mutable (entries can be updated with new context)
    - HOT retention (7 days)
    - Auto-retry when new context arrives
    - Time-decay to PARTIAL after 24h if unresolved
    - Does NOT trigger Phoenix-72 pressure by default
    - Human can manually escalate to PHOENIX if needed
    
    Purpose:
    PENDING separates SABAR (epistemic pause - need more time/context) from
    PARTIAL (constitutional mismatch - need law change). This prevents Phoenix-72
    spam for routine SABAR pauses that just need more time or data.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        super().__init__(BandName.PENDING, storage_path)
        self.max_age_hours = 24  # SABAR→PARTIAL decay threshold

    def write(
        self,
        content: Dict[str, Any],
        writer_id: str,
        verdict: Optional[str] = None,
        evidence_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> WriteResult:
        # PENDING accepts SABAR and SABAR_EXTENDED verdicts
        allowed_verdicts = ["SABAR", "SABAR_EXTENDED"]
        if verdict and verdict not in allowed_verdicts:
            return WriteResult(
                success=False,
                error=f"PENDING band only accepts {allowed_verdicts}, got {verdict}",
            )

        base_metadata = metadata or {}
        retry_count = base_metadata.get("retry_count", 0)

        entry = MemoryEntry(
            entry_id=str(uuid.uuid4())[:12],
            band=self.name,
            content=content,
            timestamp=self._now_iso(),
            writer_id=writer_id,
            verdict=verdict,
            evidence_hash=evidence_hash,
            metadata={
                **base_metadata,
                "retry_count": retry_count,
                "status": "pending",
                "decay_at": self._compute_decay_timestamp(),
            },
        )

        entry.hash = self._compute_hash(entry)
        self._entries.append(entry)

        return WriteResult(
            success=True,
            entry_id=entry.entry_id,
            entry_hash=entry.hash,
        )

    def should_retry(self, entry: MemoryEntry) -> bool:
        """Check if entry should be retried with new context."""
        # Logic: Has new context arrived? Has retry limit been reached?
        retry_count = int(entry.metadata.get("retry_count", 0))
        max_retries = 3  # Configurable
        return bool(retry_count < max_retries)

    def should_decay(self, entry: MemoryEntry) -> bool:
        """Check if entry should decay to PARTIAL (age > 24h)."""
        try:
            entry_time = datetime.fromisoformat(entry.timestamp.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            age_hours = (now - entry_time).total_seconds() / 3600
            return age_hours > self.max_age_hours
        except (ValueError, TypeError):
            # If timestamp parsing fails, assume no decay
            return False

    def query(
        self,
        filter_fn: Optional[Callable[[MemoryEntry], bool]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> QueryResult:
        entries = self._entries
        if filter_fn:
            entries = [e for e in entries if filter_fn(e)]

        total = len(entries)
        entries = entries[offset:offset + limit]

        return QueryResult(
            entries=entries,
            total_count=total,
            truncated=(offset + limit < total),
        )

    def _compute_decay_timestamp(self) -> str:
        """Compute when this entry should decay to PARTIAL (24h from now)."""
        now = datetime.now(timezone.utc)
        decay_time = now + timedelta(hours=self.max_age_hours)
        return decay_time.isoformat(timespec="milliseconds").replace("+00:00", "Z")


class PhoenixCandidatesBand(MemoryBand):
    """
    PHOENIX CANDIDATES Band — Pending amendments.

    Properties:
    - Mutable until sealed/rejected
    - Human seal required for finalization
    - 888_Judge writes based on scars
    - Status: draft | awaiting_review | sealed | rejected
    """

    def __init__(self, storage_path: Optional[Path] = None):
        super().__init__(BandName.PHOENIX, storage_path)

    def write(
        self,
        content: Dict[str, Any],
        writer_id: str,
        verdict: Optional[str] = None,
        evidence_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> WriteResult:
        # Phoenix accepts from 888_JUDGE, PHOENIX_72, HUMAN, SUNSET_EXECUTOR (v38.2)
        allowed = ["888_JUDGE", "PHOENIX_72", "HUMAN", "SUNSET_EXECUTOR"]
        if writer_id not in allowed:
            return WriteResult(
                success=False,
                error=f"Writer {writer_id} not authorized for PHOENIX band",
            )

        base_metadata = metadata or {}
        status = base_metadata.get("status", "draft")

        entry = MemoryEntry(
            entry_id=str(uuid.uuid4())[:12],
            band=self.name,
            content=content,
            timestamp=self._now_iso(),
            writer_id=writer_id,
            verdict=verdict,
            evidence_hash=evidence_hash,
            metadata={
                **base_metadata,
                "status": status,
            },
        )

        entry.hash = self._compute_hash(entry)
        self._entries.append(entry)

        return WriteResult(
            success=True,
            entry_id=entry.entry_id,
            entry_hash=entry.hash,
        )

    def query(
        self,
        filter_fn: Optional[Callable[[MemoryEntry], bool]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> QueryResult:
        entries = self._entries
        if filter_fn:
            entries = [e for e in entries if filter_fn(e)]

        total = len(entries)
        entries = entries[offset:offset + limit]

        return QueryResult(
            entries=entries,
            total_count=total,
            truncated=(offset + limit < total),
        )

    def update_status(self, entry_id: str, new_status: str, sealer_id: str) -> bool:
        """Update proposal status (requires human for seal/reject)."""
        valid_statuses = ["draft", "awaiting_review", "sealed", "rejected"]
        if new_status not in valid_statuses:
            return False

        # Sealing/rejection requires human
        if new_status in ("sealed", "rejected") and sealer_id != "HUMAN":
            return False

        for entry in self._entries:
            if entry.entry_id == entry_id:
                entry.metadata["status"] = new_status
                entry.metadata["status_changed_at"] = self._now_iso()
                entry.metadata["status_changed_by"] = sealer_id
                return True

        return False


class WitnessBand(MemoryBand):
    """
    WITNESS Band — Soft evidence (NOT binding facts).

    Properties:
    - Mutable
    - Rolling retention (30 days default)
    - @RIF, @GEOX write embeddings/RAG
    - Contains: embeddings, similarities, soft context
    """

    def __init__(self, storage_path: Optional[Path] = None):
        super().__init__(BandName.WITNESS, storage_path)

    def write(
        self,
        content: Dict[str, Any],
        writer_id: str,
        verdict: Optional[str] = None,
        evidence_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> WriteResult:
        # Witness is relatively open for retrieval systems
        entry = MemoryEntry(
            entry_id=str(uuid.uuid4())[:12],
            band=self.name,
            content=content,
            timestamp=self._now_iso(),
            writer_id=writer_id,
            verdict=verdict,
            evidence_hash=evidence_hash,
            metadata={
                **(metadata or {}),
                "confidence": content.get("confidence", 0.5),
                "source": content.get("source", "unknown"),
            },
        )

        entry.hash = self._compute_hash(entry)
        self._entries.append(entry)

        return WriteResult(
            success=True,
            entry_id=entry.entry_id,
            entry_hash=entry.hash,
        )

    def query(
        self,
        filter_fn: Optional[Callable[[MemoryEntry], bool]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> QueryResult:
        entries = self._entries
        if filter_fn:
            entries = [e for e in entries if filter_fn(e)]

        total = len(entries)
        entries = entries[offset:offset + limit]

        return QueryResult(
            entries=entries,
            total_count=total,
            truncated=(offset + limit < total),
        )


class VoidBandStorage(MemoryBand):
    """
    VOID Band — Diagnostic archive (NEVER canonical).

    Properties:
    - 90-day rolling retention then auto-delete
    - APEX PRIME writes all VOID verdicts
    - For scar analysis only, never for recall
    - Contains: rejected outputs, violations, analysis
    """

    def __init__(self, storage_path: Optional[Path] = None):
        super().__init__(BandName.VOID, storage_path)

    def write(
        self,
        content: Dict[str, Any],
        writer_id: str,
        verdict: Optional[str] = None,
        evidence_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> WriteResult:
        # Void accepts from APEX_PRIME, 777_FORGE
        allowed = ["APEX_PRIME", "777_FORGE", "HUMAN"]
        if writer_id not in allowed:
            return WriteResult(
                success=False,
                error=f"Writer {writer_id} not authorized for VOID band",
            )

        entry = MemoryEntry(
            entry_id=str(uuid.uuid4())[:12],
            band=self.name,
            content=content,
            timestamp=self._now_iso(),
            writer_id=writer_id,
            verdict=verdict or "VOID",  # Default to VOID
            evidence_hash=evidence_hash,
            metadata={
                **(metadata or {}),
                "scar_candidate": True,
                "retention_days": 90,
            },
        )

        entry.hash = self._compute_hash(entry)
        self._entries.append(entry)

        return WriteResult(
            success=True,
            entry_id=entry.entry_id,
            entry_hash=entry.hash,
        )

    def query(
        self,
        filter_fn: Optional[Callable[[MemoryEntry], bool]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> QueryResult:
        entries = self._entries
        if filter_fn:
            entries = [e for e in entries if filter_fn(e)]

        total = len(entries)
        entries = entries[offset:offset + limit]

        return QueryResult(
            entries=entries,
            total_count=total,
            truncated=(offset + limit < total),
        )

    def cleanup_expired(self, retention_days: int = 90) -> int:
        """Remove entries older than retention_days. Returns count deleted."""
        now = datetime.now(timezone.utc)
        original_count = len(self._entries)

        active_entries = []
        for entry in self._entries:
            try:
                entry_time = datetime.fromisoformat(entry.timestamp.replace("Z", "+00:00"))
                age_days = (now - entry_time).days
                if age_days <= retention_days:
                    active_entries.append(entry)
            except (ValueError, TypeError):
                active_entries.append(entry)

        self._entries = active_entries
        return original_count - len(self._entries)


# =============================================================================
# MEMORY BAND ROUTER
# =============================================================================

class MemoryBandRouter:
    """
    Routes writes to correct memory band based on verdict and policy.

    v38.2 Enhancements:
    - Integrates entropy rot via check_entropy_rot() before routing
    - Handles SUNSET verdict for lawful revocation (LEDGER → PHOENIX)
    - Per spec/arifos_v38_2.yaml::invariants.TIME-1

    Responsibilities:
    - Route writes to correct band based on verdict
    - Apply entropy rot to stale SABAR/PARTIAL verdicts
    - Execute SUNSET revocations
    - Enforce band write rules (who can write where)
    - Log all routing decisions for audit
    """

    def __init__(self):
        self.bands: Dict[str, MemoryBand] = {
            BandName.VAULT: VaultBand(),
            BandName.LEDGER: CoolingLedgerBand(),
            BandName.ACTIVE: ActiveStreamBand(),
            BandName.PENDING: PendingBand(),  # v38.3: Epistemic queue for SABAR
            BandName.PHOENIX: PhoenixCandidatesBand(),
            BandName.WITNESS: WitnessBand(),
            BandName.VOID: VoidBandStorage(),
        }
        self._routing_log: List[Dict[str, Any]] = []

    def route_write(
        self,
        verdict: str,
        content: Dict[str, Any],
        writer_id: str,
        target_band: Optional[str] = None,
        evidence_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, WriteResult]:
        """
        Route a write to appropriate band(s) based on verdict.

        Args:
            verdict: APEX PRIME verdict
            content: Content to write
            writer_id: Who is writing
            target_band: Optional specific band override
            evidence_hash: Evidence chain hash
            metadata: Additional metadata

        Returns:
            Dict mapping band names to WriteResults
        """
        results: Dict[str, WriteResult] = {}
        verdict_upper = verdict.upper()

        # Determine target bands
        if target_band:
            target_bands = [target_band.upper()]
        else:
            # Route by verdict
            from .policy import VERDICT_BAND_ROUTING
            target_bands = VERDICT_BAND_ROUTING.get(verdict_upper, ["LEDGER"])

        # VOID verdicts ONLY go to VOID band
        if verdict_upper == "VOID":
            target_bands = ["VOID"]

        # Write to each target band
        for band_name in target_bands:
            band = self.bands.get(band_name)
            if band is None:
                # Log failed routing for unknown band
                results[band_name] = WriteResult(
                    success=False,
                    error=f"Unknown band: {band_name}",
                )
                self._log_routing(
                    verdict=verdict_upper,
                    target_band=band_name,
                    writer_id=writer_id,
                    success=False,
                    entry_id=None,
                )
                continue

            result = band.write(
                content=content,
                writer_id=writer_id,
                verdict=verdict_upper,
                evidence_hash=evidence_hash,
                metadata=metadata,
            )
            results[band_name] = result

            # Log routing decision
            self._log_routing(
                verdict=verdict_upper,
                target_band=band_name,
                writer_id=writer_id,
                success=result.success,
                entry_id=result.entry_id,
            )

        return results

    def write(self, entry: MemoryEntry, band_name: BandName) -> WriteResult:
        """
        Backwards-compatible helper used by older tests.

        Writes a prepared MemoryEntry to the specified band.
        """
        band_key = band_name.value if isinstance(band_name, BandName) else str(band_name)
        band = self.bands.get(band_key)
        if band is None:
            return WriteResult(success=False, error=f"Unknown band: {band_key}")

        result = band.write(
            content=entry.content,
            writer_id=entry.writer_id,
            verdict=entry.verdict,
            evidence_hash=entry.evidence_hash,
            metadata=entry.metadata,
        )

        self._log_routing(
            verdict=entry.verdict or "UNKNOWN",
            target_band=band_key,
            writer_id=entry.writer_id,
            success=result.success,
            entry_id=result.entry_id,
        )

        return result

    def query_band(
        self,
        band_name: str,
        filter_fn: Optional[Callable[[MemoryEntry], bool]] = None,
        limit: int = 100,
    ) -> QueryResult:
        """Query a specific band."""
        band = self.bands.get(band_name.upper())
        if band is None:
            return QueryResult(entries=[], total_count=0)

        return band.query(filter_fn=filter_fn, limit=limit)

    def get_band(self, band_name: str) -> Optional[MemoryBand]:
        """Get a band instance by name."""
        return self.bands.get(band_name.upper())

    def get_routing_log(self) -> List[Dict[str, Any]]:
        """Return routing decision log."""
        return list(self._routing_log)

    def _log_routing(
        self,
        verdict: str,
        target_band: str,
        writer_id: str,
        success: bool,
        entry_id: Optional[str],
    ) -> None:
        """Log a routing decision."""
        self._routing_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "verdict": verdict,
            "target_band": target_band,
            "writer_id": writer_id,
            "success": success,
            "entry_id": entry_id,
        })

    # =========================================================================
    # v38.2 ENTROPY ROT + SUNSET METHODS
    # =========================================================================

    def route_with_entropy_rot(
        self,
        verdict: str,
        content: Dict[str, Any],
        writer_id: str,
        timestamp: str,
        reference_id: Optional[str] = None,
        evidence_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Route a write with entropy rot applied first.

        v38.2 Enhancement: Before routing, applies check_entropy_rot() to
        handle stale SABAR/PARTIAL verdicts per TIME-1 invariant.

        Args:
            verdict: APEX PRIME verdict
            content: Content to write
            writer_id: Who is writing
            timestamp: When verdict was issued (ISO format)
            reference_id: Optional reference for SUNSET revocation
            evidence_hash: Evidence chain hash
            metadata: Additional metadata

        Returns:
            Dict with routing results and entropy rot info
        """
        from ..system.kernel import VerdictPacket, check_entropy_rot

        # Build packet for entropy rot check
        packet = VerdictPacket(
            verdict=verdict,
            timestamp=timestamp,
            reference_id=reference_id,
            evidence_chain={"hash": evidence_hash} if evidence_hash else {},
            metadata=metadata or {},
        )

        # Apply entropy rot
        rot_result = check_entropy_rot(packet)
        final_verdict = rot_result.final_verdict

        # Route with possibly-updated verdict
        write_results = self.route_write(
            verdict=final_verdict,
            content=content,
            writer_id=writer_id,
            target_band=None,
            evidence_hash=evidence_hash,
            metadata={
                **(metadata or {}),
                "entropy_rot_applied": rot_result.rotted,
                "original_verdict": rot_result.original_verdict if rot_result.rotted else None,
                "rot_reason": rot_result.reason if rot_result.rotted else None,
            },
        )

        return {
            "write_results": write_results,
            "entropy_rot": {
                "applied": rot_result.rotted,
                "original_verdict": rot_result.original_verdict,
                "final_verdict": rot_result.final_verdict,
                "reason": rot_result.reason,
                "age_hours": rot_result.age_hours,
            },
        }

    def execute_sunset(
        self,
        reference_id: str,
        reason: str = "Reality changed; truth expired",
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Execute a SUNSET revocation: move entry from LEDGER → PHOENIX.

        SUNSET is the lawful mechanism to un-seal previously canonical memory
        when external reality changes. The evidence chain is preserved.

        Args:
            reference_id: The entry_id to revoke from LEDGER
            reason: Reason for revocation

        Returns:
            Tuple of (success: bool, message: str, phoenix_entry_id: Optional[str])
        """
        ledger_band = self.bands.get(BandName.LEDGER)
        phoenix_band = self.bands.get(BandName.PHOENIX)

        if ledger_band is None or phoenix_band is None:
            return False, "LEDGER or PHOENIX band not available", None

        # Find entry in ledger
        query_result = ledger_band.query(
            filter_fn=lambda e: e.entry_id == reference_id,
            limit=1,
        )

        if not query_result.entries:
            return False, f"Entry {reference_id} not found in LEDGER", None

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
            return False, f"Failed to write to PHOENIX: {phoenix_result.error}", None

        # Log the SUNSET execution
        self._log_routing(
            verdict="SUNSET",
            target_band="PHOENIX",
            writer_id="SUNSET_EXECUTOR",
            success=True,
            entry_id=phoenix_result.entry_id,
        )

        return True, f"SUNSET executed: {reference_id} moved to PHOENIX", phoenix_result.entry_id


# =============================================================================
# PHASE-2 EUREKA ADAPTERS
# =============================================================================

def append_eureka_decision(
    decision: MemoryWriteDecision,
    request: MemoryWriteRequest,
    store: Optional[Any] = None,
):
    """Append a Phase-2 EUREKA routing decision to storage.

    - Uses AppendOnlyJSONLStore by default (`vault_999/ledger/{band}.jsonl`).
    - Supports InMemoryStore for tests.
    - Drops TOOL/forbidden writes when `decision.allowed` is False or action is DROP.
    """
    if not decision.allowed or decision.action != "APPEND":
        return None

    target_band: EurekaMemoryBand = decision.target_band

    # Choose store
    if store is None:
        store = AppendOnlyJSONLStore()

    if isinstance(store, AppendOnlyJSONLStore):
        return store.append(target_band, request, decision)

    if isinstance(store, InMemoryStore):
        store.append(target_band, request, decision)
        return None

    # Fallback: use default append-only store
    default_store = AppendOnlyJSONLStore()
    return default_store.append(target_band, request, decision)

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "BandName",
    "RetentionTier",
    # Data classes
    "MemoryEntry",
    "WriteResult",
    "QueryResult",
    # Base class
    "MemoryBand",
    # Concrete bands
    "VaultBand",
    "CoolingLedgerBand",
    "ActiveStreamBand",
    "PhoenixCandidatesBand",
    "WitnessBand",
    "VoidBandStorage",
    # Router
    "MemoryBandRouter",
    # Phase-2 adapters
    "append_eureka_decision",
    "AppendOnlyJSONLStore",
    "InMemoryStore",
    # Constants
    "BAND_PROPERTIES",
    "WRITER_PERMISSIONS",
]
