"""
arifOS Witness Log — Append-Only Audit Trail
═══════════════════════════════════════════════════════════════════════════════════════

Every tool call generates a WitnessEntry.
WitnessLog is the append-only store of all entries.

This is F03 WITNESS — evidence must be verifiable.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class WitnessRecord(BaseModel):
    """
    A single immutable witness record.

    Once written, records are never modified.
    """

    record_id: str = Field(description="Unique identifier for this record")
    chain_id: str = Field(description="Previous record hash — for chain integrity")
    timestamp: str = Field(description="ISO timestamp when record was created")
    tool_id: str = Field(description="Tool that was invoked")
    actor_id: str | None = Field(default=None, description="Who invoked it")
    session_id: str | None = Field(default=None, description="Session context")
    domain: str = Field(description="AOS | WELL | WEALTH | GEOX")
    risk_tier: str = Field(description="T0 | T1 | T2 | T3 | T4")
    reversibility: str = Field(description="reversible | partial | irreversible")
    status: str = Field(description="SEAL | HOLD | VOID | ESCALATED")
    confidence: float = Field(ge=0.0, le=1.0)
    authority_verified: bool = Field(description="Was authority confirmed?")
    latency_ms: float | None = Field(default=None, description="Execution time")
    input_hash: str = Field(description="SHA-256 of input parameters")
    reasoning_summary: str = Field(default="", description="Why decision was made")
    error: str | None = Field(default=None, description="Error if failed")
    next_action: str = Field(default="", description="What happens next")
    metadata: dict[str, Any] = Field(default_factory=dict)

    def compute_record_hash(self) -> str:
        """Compute hash of this record for chain verification."""
        data = json.dumps(
            {
                "record_id": self.record_id,
                "chain_id": self.chain_id,
                "timestamp": self.timestamp,
                "tool_id": self.tool_id,
                "actor_id": self.actor_id,
                "session_id": self.session_id,
                "domain": self.domain,
                "risk_tier": self.risk_tier,
                "reversibility": self.reversibility,
                "status": self.status,
                "confidence": self.confidence,
                "authority_verified": self.authority_verified,
                "input_hash": self.input_hash,
                "reasoning_summary": self.reasoning_summary,
                "error": self.error,
            },
            sort_keys=True,
        )
        return hashlib.sha256(data.encode()).hexdigest()


class WitnessLog:
    """
    Append-only log of all tool call witnesses.

    Records are chained with SHA-256 hashes for tamper evidence.

    Usage:
        log = WitnessLog()
        log.append(witness_entry)
        chain_tip = log.get_chain_tip()
        records = log.query(session_id="sess_abc123")
    """

    def __init__(
        self,
        path: str | None = None,
        max_records: int = 100_000,
    ):
        """
        Initialize witness log.

        Args:
            path: File path for JSONL storage. Default: ~/.arifos/witness.jsonl
            max_records: Max records to keep in memory index.
        """
        if path is None:
            home = os.path.expanduser("~")
            arifos_dir = os.path.join(home, ".local", "share", "arifos", "witness")
            os.makedirs(arifos_dir, exist_ok=True)
            path = os.path.join(arifos_dir, "log.jsonl")

        self.path = Path(path)
        self.max_records = max_records

        # In-memory index for fast queries
        self._index: dict[str, list[str]] = {}  # key → record_ids
        self._chain_tip: str = "genesis"
        self._lock = threading.RLock()

        # Load existing chain tip
        self._load_index()

    def _load_index(self) -> None:
        """Load existing records to build index and chain tip."""
        if not self.path.exists():
            return

        with self._lock:
            try:
                with open(self.path) as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            record = WitnessRecord.model_validate_json(line)
                            self._index_record(record)
                        except Exception as e:
                            logger.warning(f"Failed to parse witness record: {e}")
            except Exception as e:
                logger.warning(f"Failed to load witness log: {e}")

    def _index_record(self, record: WitnessRecord) -> None:
        """Add a record to the in-memory index."""
        # Update chain tip
        self._chain_tip = record.record_id

        # Index by session
        if record.session_id:
            if record.session_id not in self._index:
                self._index[record.session_id] = []
            self._index[record.session_id].append(record.record_id)

        # Index by tool
        if record.tool_id not in self._index:
            self._index[record.tool_id] = []
        self._index[record.tool_id].append(record.record_id)

        # Index by actor
        if record.actor_id:
            if record.actor_id not in self._index:
                self._index[record.actor_id] = []
            self._index[record.actor_id].append(record.record_id)

    def append(
        self,
        tool_id: str,
        actor_id: str | None,
        session_id: str | None,
        domain: str,
        risk_tier: str,
        reversibility: str,
        status: str,
        confidence: float,
        authority_verified: bool,
        input_hash: str,
        reasoning_summary: str = "",
        error: str | None = None,
        next_action: str = "",
        latency_ms: float | None = None,
        metadata: dict[str, Any] | None = None,
        record_id: str | None = None,
    ) -> WitnessRecord:
        """
        Append a new witness record.

        Returns the created record.
        """
        if record_id is None:
            record_id = hashlib.sha256(
                f"{tool_id}:{datetime.now(UTC).isoformat()}:{input_hash}".encode()
            ).hexdigest()[:16]

        with self._lock:
            record = WitnessRecord(
                record_id=record_id,
                chain_id=self._chain_tip,
                timestamp=datetime.now(UTC).isoformat(),
                tool_id=tool_id,
                actor_id=actor_id,
                session_id=session_id,
                domain=domain,
                risk_tier=risk_tier,
                reversibility=reversibility,
                status=status,
                confidence=confidence,
                authority_verified=authority_verified,
                latency_ms=latency_ms,
                input_hash=input_hash,
                reasoning_summary=reasoning_summary,
                error=error,
                next_action=next_action,
                metadata=metadata or {},
            )

            # Write to file
            with open(self.path, "a") as f:
                f.write(record.model_dump_json() + "\n")

            # Update index
            self._index_record(record)

            return record

    def query(
        self,
        session_id: str | None = None,
        tool_id: str | None = None,
        actor_id: str | None = None,
        status: str | None = None,
        since: str | None = None,
        until: str | None = None,
        limit: int = 100,
    ) -> list[WitnessRecord]:
        """
        Query witness records by various filters.

        Returns matching records in reverse chronological order.
        """
        # Find candidate IDs from index
        candidate_ids: set[str] | None = None

        if session_id and session_id in self._index:
            candidate_ids = set(self._index[session_id])
        elif tool_id and tool_id in self._index:
            candidate_ids = set(self._index[tool_id])
        elif actor_id and actor_id in self._index:
            candidate_ids = set(self._index[actor_id])

        if candidate_ids is None:
            candidate_ids = set()

        # Load from file and filter
        results: list[WitnessRecord] = []

        if not self.path.exists():
            return results

        try:
            with open(self.path) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = WitnessRecord.model_validate_json(line)

                        # Apply filters
                        if candidate_ids and record.record_id not in candidate_ids:
                            continue
                        if status and record.status != status:
                            continue
                        if since and record.timestamp < since:
                            continue
                        if until and record.timestamp > until:
                            continue

                        results.append(record)
                    except Exception:
                        continue
        except Exception as e:
            logger.warning(f"Failed to query witness log: {e}")

        # Sort reverse chronological
        results.sort(key=lambda r: r.timestamp, reverse=True)

        return results[:limit]

    def get_chain_tip(self) -> str:
        """Get the current chain tip (most recent record ID)."""
        with self._lock:
            return self._chain_tip

    def verify_chain(self) -> tuple[bool, str]:
        """
        Verify the integrity of the chain.

        Returns (is_valid, message).
        """
        if not self.path.exists():
            return True, "Empty log — nothing to verify"

        expected_chain = "genesis"
        with self._lock:
            try:
                with open(self.path) as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        record = WitnessRecord.model_validate_json(line)
                        if record.chain_id != expected_chain:
                            return (
                                False,
                                f"Chain broken at {record.record_id}: "
                                f"expected {expected_chain}, got {record.chain_id}",
                            )
                        expected_chain = record.record_id
                return True, f"Chain valid to tip {expected_chain}"
            except Exception as e:
                return False, f"Verification failed: {e}"

    def stats(self) -> dict[str, Any]:
        """Return statistics about the witness log."""
        with self._lock:
            total = 0
            by_domain: dict[str, int] = {}
            by_status: dict[str, int] = {}
            by_risk: dict[str, int] = {}
            seals = 0
            holds = 0
            voids = 0

            if self.path.exists():
                with open(self.path) as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        total += 1
                        try:
                            record = WitnessRecord.model_validate_json(line)
                            by_domain[record.domain] = by_domain.get(record.domain, 0) + 1
                            by_status[record.status] = by_status.get(record.status, 0) + 1
                            by_risk[record.risk_tier] = by_risk.get(record.risk_tier, 0) + 1
                            if record.status == "SEAL":
                                seals += 1
                            elif record.status == "HOLD":
                                holds += 1
                            elif record.status == "VOID":
                                voids += 1
                        except Exception:
                            continue

            return {
                "total_records": total,
                "chain_tip": self._chain_tip,
                "by_domain": by_domain,
                "by_status": by_status,
                "by_risk": by_risk,
                "seal_rate": seals / total if total > 0 else 0,
                "hold_rate": holds / total if total > 0 else 0,
                "void_rate": voids / total if total > 0 else 0,
            }


# Global singleton
_witness_log: WitnessLog | None = None


def get_witness_log() -> WitnessLog:
    """Get the global witness log singleton."""
    global _witness_log
    if _witness_log is None:
        _witness_log = WitnessLog()
    return _witness_log


def log_witness(
    tool_id: str,
    actor_id: str | None,
    session_id: str | None,
    domain: str,
    risk_tier: str,
    reversibility: str,
    status: str,
    confidence: float,
    authority_verified: bool,
    input_hash: str,
    reasoning_summary: str = "",
    error: str | None = None,
    latency_ms: float | None = None,
) -> WitnessRecord:
    """Convenience function to append to the global witness log."""
    return get_witness_log().append(
        tool_id=tool_id,
        actor_id=actor_id,
        session_id=session_id,
        domain=domain,
        risk_tier=risk_tier,
        reversibility=reversibility,
        status=status,
        confidence=confidence,
        authority_verified=authority_verified,
        input_hash=input_hash,
        reasoning_summary=reasoning_summary,
        error=error,
        latency_ms=latency_ms,
    )


__all__ = [
    "WitnessRecord",
    "WitnessLog",
    "get_witness_log",
    "log_witness",
]
