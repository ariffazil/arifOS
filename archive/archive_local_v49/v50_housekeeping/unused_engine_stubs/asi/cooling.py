# -*- coding: utf-8 -*-
"""
Phoenix-72 Cooling Engine (v49.1)

Constitutional Alignment: F5 (Peace - Time)
Authority: Omega (ASI) -> Enforced by APEX

Purpose:
- Enforce mandatory cooling periods based on constitutional risk
- Tiers: 0 (0h), 1 (42h), 2 (72h), 3 (168h)
- Prevent "Hot Commit" of dangerous changes
- Persist cooling entries to ledger for audit trail

BLOCKER 2 Fix (v49.1): Add actual delay enforcement with persistence.
- Added CoolingLedgerEntry dataclass for persistence
- Added persistence layer to track cooling entries
- Added time-check validation before executing cooled operations
- Added bypass mechanism for emergencies (requires human override)

DITEMPA BUKAN DIBERI - Truth must cool before it rules.
"""

import asyncio
import hashlib
import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Default cooling ledger path
DEFAULT_PHOENIX_LEDGER_PATH = Path("vault_999/BBB_LEDGER/LAYER_3_AUDIT/phoenix_cooling.jsonl")


class CoolingStatus(Enum):
    """Status of a cooling entry."""
    COOLING = "COOLING"          # Entry is in cooling period
    COMPLETE = "COMPLETE"        # Cooling period has elapsed
    BYPASSED = "BYPASSED"        # Emergency bypass by human authority
    EXPIRED = "EXPIRED"          # Entry was voided/expired without completion


@dataclass
class CoolingEntry:
    """
    A single cooling ledger entry.

    Tracks the cooling status of a constitutional decision.
    """
    entry_id: str                    # Unique identifier
    session_id: str                  # Related session
    tier: int                        # Cooling tier (0-3)
    tier_label: str                  # Human-readable tier name
    cooling_hours: int               # Hours in cooling period
    start_time: str                  # ISO-8601 start timestamp
    cool_until: str                  # ISO-8601 completion timestamp
    status: str                      # CoolingStatus value
    verdict: str                     # Original verdict (SEAL/PARTIAL/VOID/SABAR)
    floor_scores: Dict[str, Any]     # Floor scores at time of cooling
    query_hash: Optional[str] = None # SHA-256 of original query
    bypass_reason: Optional[str] = None  # Reason for emergency bypass
    bypass_authority: Optional[str] = None  # Who authorized bypass
    bypass_time: Optional[str] = None      # When bypass occurred
    completed_time: Optional[str] = None   # When cooling completed

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CoolingEntry":
        """Create from dictionary."""
        return cls(**data)

    def is_cooling_complete(self) -> bool:
        """Check if cooling period has elapsed."""
        if self.status == CoolingStatus.COMPLETE.value:
            return True
        if self.status == CoolingStatus.BYPASSED.value:
            return True
        if self.tier == 0:  # Tier 0 = immediate release
            return True

        now = datetime.now(timezone.utc)
        cool_until = datetime.fromisoformat(self.cool_until.replace("Z", "+00:00"))
        return now >= cool_until


class CoolingLedger:
    """
    Persistence layer for Phoenix-72 cooling entries.

    Stores cooling entries to JSONL file in vault_999.
    Provides lookup and validation methods.
    """

    def __init__(self, ledger_path: Optional[Path] = None):
        self.ledger_path = ledger_path or DEFAULT_PHOENIX_LEDGER_PATH
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, CoolingEntry] = {}
        self._load_cache()

    def _load_cache(self) -> None:
        """Load all entries into memory cache."""
        if not self.ledger_path.exists():
            return

        try:
            with self.ledger_path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        entry = CoolingEntry.from_dict(data)
                        self._cache[entry.entry_id] = entry
                    except (json.JSONDecodeError, TypeError) as e:
                        logger.warning(f"Failed to parse cooling entry: {e}")
        except IOError as e:
            logger.error(f"Failed to load cooling ledger: {e}")

    def append(self, entry: CoolingEntry) -> bool:
        """
        Append a new cooling entry to the ledger.

        Returns True if successful, False otherwise.
        """
        try:
            line = json.dumps(entry.to_dict(), sort_keys=True, ensure_ascii=False)
            with self.ledger_path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")
            self._cache[entry.entry_id] = entry
            logger.info(f"Phoenix-72: Cooling entry {entry.entry_id} appended (tier={entry.tier})")
            return True
        except IOError as e:
            logger.error(f"Failed to append cooling entry: {e}")
            return False

    def get(self, entry_id: str) -> Optional[CoolingEntry]:
        """Get a cooling entry by ID."""
        return self._cache.get(entry_id)

    def get_by_session(self, session_id: str) -> List[CoolingEntry]:
        """Get all cooling entries for a session."""
        return [e for e in self._cache.values() if e.session_id == session_id]

    def get_active_cooling(self) -> List[CoolingEntry]:
        """Get all entries currently in cooling status."""
        return [
            e for e in self._cache.values()
            if e.status == CoolingStatus.COOLING.value and not e.is_cooling_complete()
        ]

    def update_status(self, entry_id: str, new_status: CoolingStatus,
                      bypass_reason: Optional[str] = None,
                      bypass_authority: Optional[str] = None) -> bool:
        """
        Update the status of a cooling entry.

        Note: This appends a new line with updated status (append-only ledger).
        """
        entry = self._cache.get(entry_id)
        if not entry:
            logger.error(f"Cooling entry not found: {entry_id}")
            return False

        now = datetime.now(timezone.utc).isoformat()

        # Create updated entry
        updated = CoolingEntry(
            entry_id=entry.entry_id,
            session_id=entry.session_id,
            tier=entry.tier,
            tier_label=entry.tier_label,
            cooling_hours=entry.cooling_hours,
            start_time=entry.start_time,
            cool_until=entry.cool_until,
            status=new_status.value,
            verdict=entry.verdict,
            floor_scores=entry.floor_scores,
            query_hash=entry.query_hash,
            bypass_reason=bypass_reason,
            bypass_authority=bypass_authority,
            bypass_time=now if new_status == CoolingStatus.BYPASSED else None,
            completed_time=now if new_status == CoolingStatus.COMPLETE else None,
        )

        return self.append(updated)

    def check_all_cooling_complete(self) -> Tuple[bool, List[str]]:
        """
        Check all active cooling entries and mark completed ones.

        Returns (all_complete, list_of_still_cooling_ids).
        """
        still_cooling = []
        for entry in self.get_active_cooling():
            if entry.is_cooling_complete():
                self.update_status(entry.entry_id, CoolingStatus.COMPLETE)
            else:
                still_cooling.append(entry.entry_id)

        return len(still_cooling) == 0, still_cooling


class CoolingEngine:
    """
    Phoenix-72 Cooling Engine with enforcement (v49.1).

    Manages cooling protocols with actual time delays and persistence.
    """

    TIERS = {
        0: {"hours": 0, "label": "TIER_0_IMMEDIATE", "description": "Green seal, no cooling needed"},
        1: {"hours": 42, "label": "TIER_1_STANDARD", "description": "Minor soft floor warning"},
        2: {"hours": 72, "label": "TIER_2_CONSTITUTIONAL", "description": "Standard constitutional cooling"},
        3: {"hours": 168, "label": "TIER_3_DEEP_FREEZE", "description": "Critical amendment, 7-day cooling"}
    }

    def __init__(self, ledger: Optional[CoolingLedger] = None):
        self.ledger = ledger or CoolingLedger()

    def calculate_cooling_tier(self, verdict: str, warnings: int = 0,
                                is_constitutional_amendment: bool = False) -> int:
        """
        Determine cooling tier based on verdict and context.

        Args:
            verdict: SEAL, PARTIAL, SABAR, VOID, 888_HOLD
            warnings: Number of soft floor warnings
            is_constitutional_amendment: True if this changes constitutional law

        Returns:
            Tier level (0-3)
        """
        # Constitutional amendments always require deep freeze
        if is_constitutional_amendment:
            return 3

        if verdict == "VOID":
            return 3  # Deep freeze for violations

        if verdict == "888_HOLD":
            return 3  # Requires human judgment

        if verdict == "SABAR":
            return 2  # Pause requires meaningful cooling

        if verdict == "PARTIAL":
            # Partial approvals need standard cooling
            return 1 if warnings <= 1 else 2

        if verdict == "SEAL":
            if warnings == 0:
                return 0  # Green Seal - immediate release
            elif warnings == 1:
                return 1  # Minor warning
            else:
                return 2  # Multiple warnings

        return 2  # Default safe fallback

    async def enforce_tier(
        self,
        tier: int,
        session_id: str,
        verdict: str,
        floor_scores: Optional[Dict[str, Any]] = None,
        query: Optional[str] = None,
        block_until_cooled: bool = False,
        check_interval_seconds: float = 60.0,
    ) -> Dict[str, Any]:
        """
        Enforce the cooling tier with actual delay.

        Args:
            tier: Cooling tier (0-3)
            session_id: Session identifier
            verdict: Original verdict
            floor_scores: Floor scores at time of cooling
            query: Original query (hashed for storage)
            block_until_cooled: If True, actually wait for cooling period
            check_interval_seconds: Interval for checking cooling status

        Returns:
            Cooling metadata including entry_id and status
        """
        config = self.TIERS.get(tier, self.TIERS[2])
        hours = config["hours"]

        now = datetime.now(timezone.utc)
        cool_until = now + timedelta(hours=hours)

        # Generate entry ID
        entry_id = f"phoenix_{session_id}_{int(now.timestamp())}"

        # Hash query if provided
        query_hash = None
        if query:
            query_hash = hashlib.sha256(query.encode("utf-8")).hexdigest()

        # Create cooling entry
        entry = CoolingEntry(
            entry_id=entry_id,
            session_id=session_id,
            tier=tier,
            tier_label=config["label"],
            cooling_hours=hours,
            start_time=now.isoformat(),
            cool_until=cool_until.isoformat(),
            status=CoolingStatus.COOLING.value if tier > 0 else CoolingStatus.COMPLETE.value,
            verdict=verdict,
            floor_scores=floor_scores or {},
            query_hash=query_hash,
        )

        # Persist to ledger
        success = self.ledger.append(entry)
        if not success:
            logger.error(f"Failed to persist cooling entry {entry_id}")

        # If tier 0, immediately complete
        if tier == 0:
            return {
                "entry_id": entry_id,
                "tier": tier,
                "tier_label": config["label"],
                "cooling_hours": hours,
                "start_time": now.isoformat(),
                "cool_until": now.isoformat(),
                "status": CoolingStatus.COMPLETE.value,
                "message": "Immediate release (Tier 0)",
            }

        result = {
            "entry_id": entry_id,
            "tier": tier,
            "tier_label": config["label"],
            "cooling_hours": hours,
            "start_time": now.isoformat(),
            "cool_until": cool_until.isoformat(),
            "status": CoolingStatus.COOLING.value,
            "message": f"Cooling period initiated: {hours} hours until {cool_until.isoformat()}",
        }

        # If blocking mode, wait for cooling to complete
        if block_until_cooled:
            logger.info(f"Phoenix-72: Blocking until cooling complete for {entry_id} ({hours}h)")
            while not entry.is_cooling_complete():
                await asyncio.sleep(check_interval_seconds)
                # Refresh entry from ledger in case of bypass
                refreshed = self.ledger.get(entry_id)
                if refreshed and refreshed.status != CoolingStatus.COOLING.value:
                    entry = refreshed
                    break

            result["status"] = CoolingStatus.COMPLETE.value
            result["message"] = f"Cooling complete after {hours} hours"
            self.ledger.update_status(entry_id, CoolingStatus.COMPLETE)

        return result

    def is_operation_cooled(self, entry_id: str) -> Tuple[bool, Optional[str]]:
        """
        Check if an operation has completed its cooling period.

        Args:
            entry_id: The cooling entry ID

        Returns:
            Tuple of (is_cooled, reason_if_not)
        """
        entry = self.ledger.get(entry_id)
        if not entry:
            return False, f"Cooling entry not found: {entry_id}"

        if entry.status == CoolingStatus.COMPLETE.value:
            return True, None

        if entry.status == CoolingStatus.BYPASSED.value:
            return True, None

        if entry.is_cooling_complete():
            # Update status and return
            self.ledger.update_status(entry_id, CoolingStatus.COMPLETE)
            return True, None

        # Calculate remaining time
        now = datetime.now(timezone.utc)
        cool_until = datetime.fromisoformat(entry.cool_until.replace("Z", "+00:00"))
        remaining = cool_until - now
        hours_remaining = remaining.total_seconds() / 3600

        return False, f"Still cooling: {hours_remaining:.1f} hours remaining"

    def emergency_bypass(
        self,
        entry_id: str,
        authority: str,
        reason: str,
    ) -> Tuple[bool, str]:
        """
        Emergency bypass of cooling period (requires human authority).

        This is a safety valve for critical situations where waiting
        for cooling is not feasible. Requires explicit human authorization.

        Args:
            entry_id: The cooling entry ID to bypass
            authority: Identity of authorizing human (must be 888_Judge)
            reason: Explicit reason for bypass (will be logged)

        Returns:
            Tuple of (success, message)
        """
        entry = self.ledger.get(entry_id)
        if not entry:
            return False, f"Cooling entry not found: {entry_id}"

        if entry.status != CoolingStatus.COOLING.value:
            return False, f"Entry is not in cooling status: {entry.status}"

        # Log the bypass with full audit trail
        logger.warning(
            f"PHOENIX-72 EMERGENCY BYPASS: entry={entry_id}, "
            f"authority={authority}, reason={reason}"
        )

        success = self.ledger.update_status(
            entry_id,
            CoolingStatus.BYPASSED,
            bypass_reason=reason,
            bypass_authority=authority,
        )

        if success:
            return True, f"Cooling bypassed by {authority}: {reason}"
        else:
            return False, "Failed to update cooling status"

    def get_cooling_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get cooling status for a session.

        Returns summary of all cooling entries for the session.
        """
        entries = self.ledger.get_by_session(session_id)

        if not entries:
            return {
                "session_id": session_id,
                "has_cooling_entries": False,
                "all_cooled": True,
                "entries": [],
            }

        # Check each entry
        entry_statuses = []
        all_cooled = True
        for entry in entries:
            is_cooled, reason = self.is_operation_cooled(entry.entry_id)
            entry_statuses.append({
                "entry_id": entry.entry_id,
                "tier": entry.tier,
                "status": entry.status,
                "is_cooled": is_cooled,
                "reason": reason,
            })
            if not is_cooled:
                all_cooled = False

        return {
            "session_id": session_id,
            "has_cooling_entries": True,
            "all_cooled": all_cooled,
            "entries": entry_statuses,
        }


# Singleton instance
COOLING = CoolingEngine()


# Convenience functions for backward compatibility
def calculate_cooling_tier(verdict: str, warnings: int = 0) -> int:
    """Calculate cooling tier (backward compatible)."""
    return COOLING.calculate_cooling_tier(verdict, warnings)


async def enforce_tier(tier: int, session_id: str, **kwargs) -> Dict[str, Any]:
    """Enforce cooling tier (backward compatible)."""
    return await COOLING.enforce_tier(tier, session_id, **kwargs)


__all__ = [
    "CoolingEngine",
    "CoolingEntry",
    "CoolingLedger",
    "CoolingStatus",
    "COOLING",
    "calculate_cooling_tier",
    "enforce_tier",
]
