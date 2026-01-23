# -*- coding: utf-8 -*-
"""
Memory Tower - EUREKA Sieve & TTL (v49.1)

Constitutional Alignment: F4 (Clarity - Entropy Reduction)
Authority: Vault (999)

Purpose:
- Filter memory storage based on Novelty (Genius) and Consensus (Tri-Witness)
- Assign storage bands L0-L5 with appropriate TTLs
- Prevent entropy buildup (Digital Hoarding)
- Persist entries with automatic TTL cleanup (v49.1)

HIGH 2 Fix (v49.1): Add persistence layer for memory entries.
- Store entries to JSONL files in vault_999/AAA_MEMORY/
- Implement TTL cleanup job that purges expired entries
- Add background task or manual cleanup trigger
- Track entry metadata (band, timestamp, TTL, content_hash)

DITEMPA BUKAN DIBERI - Memory sieved, not hoarded.
"""

import asyncio
import hashlib
import json
import logging
import os
import threading
from datetime import datetime, timedelta, timezone
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Default memory vault path
DEFAULT_MEMORY_PATH = Path("vault_999/AAA_MEMORY")


@dataclass
class MemoryEntry:
    """
    A single memory entry with TTL metadata.
    """
    entry_id: str                    # Unique identifier
    session_id: str                  # Related session
    memory_band: str                 # L0-L5 band assignment
    content_hash: str                # SHA-256 of content
    content: str                     # The actual content (for L0-L4)
    timestamp: str                   # ISO-8601 creation timestamp
    ttl_days: Optional[int]          # None = permanent
    expiry: Optional[str]            # ISO-8601 expiry timestamp or "PERMANENT"
    novelty_score: float             # How new/insightful (0-1)
    consensus_score: float           # Tri-witness agreement (0-1)
    verdict: str                     # Original verdict
    metadata: Dict[str, Any]         # Additional metadata

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntry":
        """Create from dictionary."""
        return cls(**data)

    def is_expired(self) -> bool:
        """Check if entry has expired based on TTL."""
        if self.ttl_days is None or self.expiry == "PERMANENT":
            return False

        now = datetime.now(timezone.utc)
        try:
            expiry_dt = datetime.fromisoformat(self.expiry.replace("Z", "+00:00"))
            return now >= expiry_dt
        except (ValueError, AttributeError):
            return False


class MemoryBandStore:
    """
    Persistence layer for a single memory band.

    Stores entries to JSONL file and provides lookup/cleanup.
    """

    def __init__(self, band_name: str, base_path: Optional[Path] = None):
        self.band_name = band_name
        self.base_path = base_path or DEFAULT_MEMORY_PATH
        self.file_path = self.base_path / f"{band_name}_BAND" / "entries.jsonl"
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, MemoryEntry] = {}
        self._load_cache()

    def _load_cache(self) -> None:
        """Load all entries into memory cache."""
        if not self.file_path.exists():
            return

        try:
            with self.file_path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        entry = MemoryEntry.from_dict(data)
                        # Only cache non-expired entries
                        if not entry.is_expired():
                            self._cache[entry.entry_id] = entry
                    except (json.JSONDecodeError, TypeError) as e:
                        logger.warning(f"Failed to parse memory entry: {e}")
        except IOError as e:
            logger.error(f"Failed to load memory band {self.band_name}: {e}")

    def append(self, entry: MemoryEntry) -> bool:
        """
        Append a new memory entry.

        Returns True if successful.
        """
        try:
            line = json.dumps(entry.to_dict(), sort_keys=True, ensure_ascii=False)
            with self.file_path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")
            self._cache[entry.entry_id] = entry
            logger.debug(f"Memory: Entry {entry.entry_id} stored in {self.band_name}")
            return True
        except IOError as e:
            logger.error(f"Failed to append memory entry: {e}")
            return False

    def get(self, entry_id: str) -> Optional[MemoryEntry]:
        """Get entry by ID (returns None if expired)."""
        entry = self._cache.get(entry_id)
        if entry and entry.is_expired():
            return None
        return entry

    def get_by_session(self, session_id: str) -> List[MemoryEntry]:
        """Get all non-expired entries for a session."""
        return [
            e for e in self._cache.values()
            if e.session_id == session_id and not e.is_expired()
        ]

    def get_all_active(self) -> List[MemoryEntry]:
        """Get all non-expired entries."""
        return [e for e in self._cache.values() if not e.is_expired()]

    def get_expired(self) -> List[MemoryEntry]:
        """Get all expired entries."""
        return [e for e in self._cache.values() if e.is_expired()]

    def cleanup_expired(self) -> Tuple[int, int]:
        """
        Remove expired entries from cache and rewrite file.

        Returns (removed_count, remaining_count).
        """
        expired = self.get_expired()
        if not expired:
            return 0, len(self._cache)

        # Remove from cache
        for entry in expired:
            del self._cache[entry.entry_id]

        # Rewrite file with only active entries
        try:
            active = self.get_all_active()
            with self.file_path.open("w", encoding="utf-8") as f:
                for entry in active:
                    line = json.dumps(entry.to_dict(), sort_keys=True, ensure_ascii=False)
                    f.write(line + "\n")

            logger.info(f"Memory cleanup {self.band_name}: removed {len(expired)}, remaining {len(active)}")
            return len(expired), len(active)
        except IOError as e:
            logger.error(f"Failed to cleanup memory band {self.band_name}: {e}")
            return 0, len(self._cache)


class EurekaSieve:
    """
    EUREKA Sieve for memory tiering with persistence (v49.1).

    Implements the EUREKA Sieve for memory tiering.
    """

    # Band definitions with TTL
    BANDS = {
        "L0_GENESIS": {"ttl_days": None, "desc": "Immutable Canon", "store_content": False},
        "L1_ARCHIVE": {"ttl_days": None, "desc": "Permanent Storage", "store_content": True},
        "L2_WITNESS": {"ttl_days": 90, "desc": "Verified Facts (90 days)", "store_content": True},
        "L3_REFLECT": {"ttl_days": 30, "desc": "Reflective buffer (30 days)", "store_content": True},
        "L4_SESSION": {"ttl_days": 7, "desc": "Session Context (7 days)", "store_content": True},
        "L5_VOID": {"ttl_days": 1, "desc": "Ephemeral/Trash (24h)", "store_content": False},
    }

    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or DEFAULT_MEMORY_PATH
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Initialize band stores
        self._stores: Dict[str, MemoryBandStore] = {}
        for band_name in self.BANDS.keys():
            self._stores[band_name] = MemoryBandStore(band_name, self.base_path)

        # Cleanup lock
        self._cleanup_lock = threading.Lock()

    def assess_ttl(
        self,
        novelty_score: float,
        tri_witness_consensus: float,
        verdict: str,
        constitutional_pass: bool
    ) -> Dict[str, Any]:
        """
        Assess memory TTL and Band based on input metrics.

        Args:
            novelty_score: 0.0-1.0 (How new/insightful is this?)
            tri_witness_consensus: 0.0-1.0 (Agreement level)
            verdict: SEAL, PARTIAL, VOID, etc.
            constitutional_pass: True/False

        Returns:
            Dict with memory_band, ttl_days, expiry_date
        """
        # Rule 1: Constitutional Failures -> L5 VOID
        if not constitutional_pass or verdict == "VOID":
            band = "L5_VOID"

        # Rule 2: High Stakes / Sealed / High Consensus -> L1 ARCHIVE
        elif verdict == "SEAL" and tri_witness_consensus > 0.98:
            band = "L1_ARCHIVE"

        # Rule 3: High Novelty or Moderate Consensus -> L2 WITNESS
        elif novelty_score > 0.8 or tri_witness_consensus > 0.90:
            band = "L2_WITNESS"

        # Rule 4: Moderate Novelty -> L3 REFLECT
        elif novelty_score > 0.5:
            band = "L3_REFLECT"

        # Rule 5: Standard Interaction -> L4 SESSION
        else:
            band = "L4_SESSION"

        # Calculate expiry
        ttl_days = self.BANDS[band]["ttl_days"]
        if ttl_days is None:
            expiry = "PERMANENT"
        else:
            expiry = (datetime.now(timezone.utc) + timedelta(days=ttl_days)).isoformat()

        return {
            "memory_band": band,
            "description": self.BANDS[band]["desc"],
            "ttl_days": ttl_days,
            "expiry": expiry,
            "metrics": {
                "novelty": novelty_score,
                "consensus": tri_witness_consensus,
                "verdict": verdict
            }
        }

    def store_memory(
        self,
        session_id: str,
        content: str,
        novelty_score: float,
        tri_witness_consensus: float,
        verdict: str,
        constitutional_pass: bool,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Store a memory entry with automatic band assignment.

        v49.1: Now actually persists to disk with TTL tracking.

        Args:
            session_id: Session identifier
            content: The content to store
            novelty_score: Novelty metric (0-1)
            tri_witness_consensus: Consensus metric (0-1)
            verdict: Original verdict
            constitutional_pass: Whether constitutional checks passed
            metadata: Additional metadata

        Returns:
            Dict with entry_id, band, and storage status
        """
        # Assess TTL and band
        assessment = self.assess_ttl(
            novelty_score, tri_witness_consensus, verdict, constitutional_pass
        )
        band = assessment["memory_band"]

        # Don't store L0_GENESIS (immutable canon) or L5_VOID (ephemeral)
        if not self.BANDS[band]["store_content"]:
            return {
                "stored": False,
                "reason": f"Band {band} does not store content",
                "assessment": assessment,
            }

        # Generate entry
        now = datetime.now(timezone.utc)
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        entry_id = f"mem_{session_id}_{content_hash[:8]}_{int(now.timestamp())}"

        entry = MemoryEntry(
            entry_id=entry_id,
            session_id=session_id,
            memory_band=band,
            content_hash=content_hash,
            content=content,
            timestamp=now.isoformat(),
            ttl_days=assessment["ttl_days"],
            expiry=assessment["expiry"],
            novelty_score=novelty_score,
            consensus_score=tri_witness_consensus,
            verdict=verdict,
            metadata=metadata or {},
        )

        # Store to band
        store = self._stores[band]
        success = store.append(entry)

        logger.info(f"Memory stored: entry_id={entry_id}, band={band}, success={success}")

        return {
            "stored": success,
            "entry_id": entry_id,
            "memory_band": band,
            "ttl_days": assessment["ttl_days"],
            "expiry": assessment["expiry"],
            "content_hash": content_hash,
            "assessment": assessment,
        }

    def recall_memory(self, entry_id: str) -> Optional[MemoryEntry]:
        """
        Recall a memory entry by ID.

        Searches all bands for the entry.
        """
        for store in self._stores.values():
            entry = store.get(entry_id)
            if entry:
                return entry
        return None

    def recall_session_memories(self, session_id: str) -> List[MemoryEntry]:
        """
        Recall all memories for a session.

        Returns non-expired entries from all bands.
        """
        memories = []
        for store in self._stores.values():
            memories.extend(store.get_by_session(session_id))
        return memories

    def cleanup_expired(self) -> Dict[str, Tuple[int, int]]:
        """
        Clean up expired entries across all bands.

        Returns dict of band_name -> (removed_count, remaining_count).
        """
        with self._cleanup_lock:
            results = {}
            for band_name, store in self._stores.items():
                removed, remaining = store.cleanup_expired()
                results[band_name] = (removed, remaining)

            total_removed = sum(r[0] for r in results.values())
            total_remaining = sum(r[1] for r in results.values())
            logger.info(f"Memory cleanup complete: removed {total_removed}, remaining {total_remaining}")

            return results

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics across all bands.
        """
        stats = {
            "bands": {},
            "total_entries": 0,
            "total_expired": 0,
        }

        for band_name, store in self._stores.items():
            active = len(store.get_all_active())
            expired = len(store.get_expired())
            stats["bands"][band_name] = {
                "active": active,
                "expired": expired,
                "ttl_days": self.BANDS[band_name]["ttl_days"],
            }
            stats["total_entries"] += active
            stats["total_expired"] += expired

        return stats


class MemoryCleanupJob:
    """
    Background job for memory TTL cleanup.

    Can be run as a periodic task or manually triggered.
    """

    def __init__(self, sieve: EurekaSieve, interval_hours: float = 1.0):
        self.sieve = sieve
        self.interval_hours = interval_hours
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def run_once(self) -> Dict[str, Tuple[int, int]]:
        """Run cleanup once and return results."""
        return self.sieve.cleanup_expired()

    async def run_periodic(self) -> None:
        """Run cleanup periodically in background."""
        self._running = True
        logger.info(f"Memory cleanup job started (interval: {self.interval_hours}h)")

        while self._running:
            try:
                await self.run_once()
            except Exception as e:
                logger.error(f"Memory cleanup failed: {e}")

            # Wait for next interval
            await asyncio.sleep(self.interval_hours * 3600)

    def start(self) -> None:
        """Start the background cleanup job."""
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self.run_periodic())

    def stop(self) -> None:
        """Stop the background cleanup job."""
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()


# Singleton instances
EUREKA_SIEVE = EurekaSieve()
MEMORY_CLEANUP_JOB = MemoryCleanupJob(EUREKA_SIEVE)


# Convenience functions for backward compatibility
def assess_ttl(
    novelty_score: float,
    tri_witness_consensus: float,
    verdict: str,
    constitutional_pass: bool
) -> Dict[str, Any]:
    """Assess memory TTL (backward compatible)."""
    return EUREKA_SIEVE.assess_ttl(
        novelty_score, tri_witness_consensus, verdict, constitutional_pass
    )


def store_memory(
    session_id: str,
    content: str,
    novelty_score: float,
    tri_witness_consensus: float,
    verdict: str,
    constitutional_pass: bool,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Store memory entry (v49.1)."""
    return EUREKA_SIEVE.store_memory(
        session_id, content, novelty_score, tri_witness_consensus,
        verdict, constitutional_pass, metadata
    )


def recall_memory(entry_id: str) -> Optional[MemoryEntry]:
    """Recall memory entry by ID (v49.1)."""
    return EUREKA_SIEVE.recall_memory(entry_id)


def cleanup_expired() -> Dict[str, Tuple[int, int]]:
    """Clean up expired memory entries (v49.1)."""
    return EUREKA_SIEVE.cleanup_expired()


__all__ = [
    "EurekaSieve",
    "MemoryEntry",
    "MemoryBandStore",
    "MemoryCleanupJob",
    "EUREKA_SIEVE",
    "MEMORY_CLEANUP_JOB",
    "assess_ttl",
    "store_memory",
    "recall_memory",
    "cleanup_expired",
]
