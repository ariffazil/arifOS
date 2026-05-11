"""
AuditLogger — Immutable Audit Trail of All Operations
DITEMPA BUKAN DIBERI

Maintains an append-only audit log of all GEOX operations for:
  - Regulatory compliance
  - Forensic analysis
  - Trust verification
  - Constitutional review

Every tool execution, verdict, and override is logged.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from datetime import datetime
from enum import Enum, auto
import json
import hashlib


class AuditEventType(Enum):
    """Types of audit events."""

    TOOL_EXECUTION = auto()
    VERDICT_RENDERED = auto()
    CHECKPOINT_PASSED = auto()
    CHECKPOINT_FAILED = auto()
    CHECKPOINT_OVERRIDDEN = auto()
    FLOOR_VIOLATION = auto()
    CONFLATION_DETECTED = auto()
    HUMAN_OVERRIDE = auto()
    SYSTEM_ERROR = auto()


@dataclass(frozen=True)
class AuditEntry:
    """
    Single immutable audit entry.

    Once created, cannot be modified (frozen dataclass).
    Hash provides integrity verification.
    """

    timestamp: str
    event_type: str
    operation_id: str
    tool_name: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
    verdict: str | None = None

    # Cryptographic integrity
    previous_hash: str = "0" * 64  # Genesis if first entry
    entry_hash: str = field(default="")

    def __post_init__(self):
        # Calculate hash if not provided
        if not self.entry_hash:
            object.__setattr__(self, "entry_hash", self._calculate_hash())

    def _calculate_hash(self) -> str:
        """Calculate SHA-256 hash of this entry."""
        data = {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "operation_id": self.operation_id,
            "tool_name": self.tool_name,
            "details": self.details,
            "verdict": self.verdict,
            "previous_hash": self.previous_hash,
        }
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def verify_integrity(self) -> bool:
        """Verify this entry's hash matches its contents."""
        return self.entry_hash == self._calculate_hash()

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "operation_id": self.operation_id,
            "tool_name": self.tool_name,
            "verdict": self.verdict,
            "entry_hash": self.entry_hash[:16] + "...",  # Truncated for display
        }


class AuditLogger:
    """
        Append-only audit logger.

        Maintains a chain of audit entries where each entry includes
    the hash of the previous entry, creating a tamper-evident log.
    """

    def __init__(self):
        self._entries: list[AuditEntry] = []
        self._operation_index: dict[str, list[int]] = {}  # op_id -> entry indices

    def _get_previous_hash(self) -> str:
        """Get hash of last entry, or genesis hash."""
        if not self._entries:
            return "0" * 64
        return self._entries[-1].entry_hash

    def log(
        self,
        event_type: AuditEventType | str,
        operation_id: str,
        tool_name: str | None = None,
        details: dict[str, Any] | None = None,
        verdict: str | None = None,
    ) -> AuditEntry:
        """Log a new audit entry."""
        if isinstance(event_type, AuditEventType):
            event_type = event_type.name

        entry = AuditEntry(
            timestamp=datetime.utcnow().isoformat() + "Z",
            event_type=event_type,
            operation_id=operation_id,
            tool_name=tool_name,
            details=details or {},
            verdict=verdict,
            previous_hash=self._get_previous_hash(),
        )

        self._entries.append(entry)

        # Index by operation
        if operation_id not in self._operation_index:
            self._operation_index[operation_id] = []
        self._operation_index[operation_id].append(len(self._entries) - 1)

        return entry

    def get_entries_for_operation(
        self,
        operation_id: str,
    ) -> list[AuditEntry]:
        """Get all entries for a specific operation."""
        indices = self._operation_index.get(operation_id, [])
        return [self._entries[i] for i in indices]

    def get_last_hash(self) -> str:
        """Get the hash of the last entry."""
        if not self._entries:
            return "0" * 64
        return self._entries[-1].entry_hash

    def verify_chain(self) -> tuple[bool, list[str]]:
        """
        Verify integrity of entire audit chain.

        Returns (is_valid, list_of_violations).
        """
        violations = []

        for i, entry in enumerate(self._entries):
            # Verify entry hash
            if not entry.verify_integrity():
                violations.append(f"Entry {i}: hash mismatch")

            # Verify chain linkage (except genesis)
            if i > 0:
                expected_prev_hash = self._entries[i - 1].entry_hash
                if entry.previous_hash != expected_prev_hash:
                    violations.append(f"Entry {i}: previous_hash mismatch (tampering detected)")

        return len(violations) == 0, violations

    def get_statistics(self) -> dict[str, Any]:
        """Get audit log statistics."""
        if not self._entries:
            return {"total_entries": 0}

        event_counts: dict[str, int] = {}
        for entry in self._entries:
            event_counts[entry.event_type] = event_counts.get(entry.event_type, 0) + 1

        return {
            "total_entries": len(self._entries),
            "unique_operations": len(self._operation_index),
            "event_counts": event_counts,
            "chain_integrity": self.verify_chain()[0],
        }

    def export(self) -> list[dict[str, Any]]:
        """Export all entries as list of dicts."""
        return [
            {
                "timestamp": e.timestamp,
                "event_type": e.event_type,
                "operation_id": e.operation_id,
                "tool_name": e.tool_name,
                "details": e.details,
                "verdict": e.verdict,
                "previous_hash": e.previous_hash,
                "entry_hash": e.entry_hash,
            }
            for e in self._entries
        ]


# Global logger instance
_global_logger: AuditLogger | None = None


def get_audit_logger() -> AuditLogger:
    """Get the global audit logger."""
    global _global_logger
    if _global_logger is None:
        _global_logger = AuditLogger()
    return _global_logger
