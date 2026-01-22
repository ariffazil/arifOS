"""
retention.py — Memory Retention Manager for arifOS v38

Manages memory lifecycle across Hot/Warm/Cold tiers:
- HOT (weeks): Active Stream, current scars, recent amendments
- WARM (months): Ledger entries, older Phoenix-72 proposals
- COLD (years): Vault (permanent), historical ledger
- VOID (90 days): Auto-delete after 90 days

Core Philosophy:
Prevents memory bloat, keeps system responsive, maintains
historical record without drowning in noise.

Per: docs/arifOS-MEMORY-FORGING-DEEPRESEARCH.md

Author: arifOS Project
Version: v38.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import json
import shutil


# =============================================================================
# CONSTANTS
# =============================================================================

class RetentionTier(str, Enum):
    """Memory retention tiers."""
    HOT = "HOT"      # weeks
    WARM = "WARM"    # months
    COLD = "COLD"    # years/permanent
    VOID = "VOID"    # 90 days


# Default retention periods (in days)
DEFAULT_RETENTION_DAYS = {
    RetentionTier.HOT: 7,
    RetentionTier.WARM: 90,
    RetentionTier.COLD: None,  # Permanent
    RetentionTier.VOID: 90,
}

# Band → Tier mapping
BAND_TIER_MAP = {
    "VAULT": RetentionTier.COLD,
    "LEDGER": RetentionTier.WARM,
    "ACTIVE": RetentionTier.HOT,
    "PHOENIX": RetentionTier.WARM,
    "WITNESS": RetentionTier.WARM,
    "VOID": RetentionTier.VOID,
}

# Transition rules: source_band → [allowed_targets]
BAND_TRANSITIONS = {
    "ACTIVE": ["LEDGER"],        # Session → Archive
    "PHOENIX": ["VAULT", "LEDGER"],  # Proposal → Canon or Archive
    "LEDGER": ["ARCHIVE"],       # Recent → Historical
    "WITNESS": [],               # No promotion, just deletion
    "VOID": [],                  # No promotion, just deletion
    "VAULT": [],                 # Permanent, no transition
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class RetentionConfig:
    """Configuration for retention manager."""
    hot_days: int = 7
    warm_days: int = 90
    void_days: int = 90
    auto_cleanup_enabled: bool = True
    archive_path: Optional[Path] = None


@dataclass
class RetentionAction:
    """A single retention action to take."""
    action_type: str  # "KEEP", "MOVE", "DELETE", "ARCHIVE"
    entry_id: str
    from_band: str
    to_band: Optional[str]
    reason: str
    age_days: int


@dataclass
class RetentionReport:
    """Report from retention policy application."""
    timestamp: str
    total_entries_scanned: int
    entries_to_keep: List[RetentionAction] = field(default_factory=list)
    entries_to_move: List[RetentionAction] = field(default_factory=list)
    entries_to_delete: List[RetentionAction] = field(default_factory=list)
    entries_to_archive: List[RetentionAction] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class BandStatus:
    """Status of a memory band."""
    band_name: str
    entry_count: int
    size_bytes: int
    oldest_entry_timestamp: Optional[str]
    newest_entry_timestamp: Optional[str]
    tier: RetentionTier
    retention_days: Optional[int]
    estimated_cleanup_count: int = 0


# =============================================================================
# MEMORY RETENTION MANAGER
# =============================================================================

class MemoryRetentionManager:
    """
    Manages memory retention across bands and tiers.

    Responsibilities:
    - Apply retention policies based on age and band
    - Move entries between bands (Hot → Warm → Cold)
    - Auto-cleanup Void band (90-day rolling)
    - Report band status and forecasts

    Usage:
        config = RetentionConfig(hot_days=7, warm_days=90, void_days=90)
        manager = MemoryRetentionManager(config)
        report = manager.apply_retention_policy(router)
    """

    def __init__(self, config: Optional[RetentionConfig] = None):
        """
        Initialize retention manager.

        Args:
            config: Optional retention configuration
        """
        self.config = config or RetentionConfig()
        self._action_log: List[RetentionAction] = []

    # =========================================================================
    # CORE RETENTION METHODS
    # =========================================================================

    def apply_retention_policy(
        self,
        entries: List[Dict[str, Any]],
    ) -> RetentionReport:
        """
        Apply retention policy to a list of entries.

        Evaluates each entry and determines whether to:
        - KEEP: Entry within retention window
        - MOVE: Entry should transition to different band
        - DELETE: Entry exceeds retention and should be removed
        - ARCHIVE: Entry should be archived (Cold tier)

        Args:
            entries: List of memory entries to evaluate

        Returns:
            RetentionReport with categorized actions
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        now = datetime.now(timezone.utc)

        report = RetentionReport(
            timestamp=timestamp,
            total_entries_scanned=len(entries),
        )

        for entry in entries:
            try:
                action = self._evaluate_entry(entry, now)
                self._action_log.append(action)

                if action.action_type == "KEEP":
                    report.entries_to_keep.append(action)
                elif action.action_type == "MOVE":
                    report.entries_to_move.append(action)
                elif action.action_type == "DELETE":
                    report.entries_to_delete.append(action)
                elif action.action_type == "ARCHIVE":
                    report.entries_to_archive.append(action)

            except Exception as e:
                report.errors.append(f"Error evaluating entry {entry.get('entry_id', 'unknown')}: {e}")

        return report

    def _evaluate_entry(
        self,
        entry: Dict[str, Any],
        now: datetime,
    ) -> RetentionAction:
        """Evaluate a single entry and return the appropriate action."""
        entry_id = entry.get("entry_id", "unknown")
        band = entry.get("band", "UNKNOWN")
        timestamp_str = entry.get("timestamp", "")

        # Parse entry age
        age_days = self._compute_age_days(timestamp_str, now)

        # Get tier and retention for this band
        tier = BAND_TIER_MAP.get(band, RetentionTier.WARM)
        retention_days = self._get_retention_days(tier)

        # VAULT is always permanent
        if band == "VAULT":
            return RetentionAction(
                action_type="KEEP",
                entry_id=entry_id,
                from_band=band,
                to_band=None,
                reason="Vault entries are permanent",
                age_days=age_days,
            )

        # VOID: Delete after retention period
        if band == "VOID":
            if age_days > self.config.void_days:
                return RetentionAction(
                    action_type="DELETE",
                    entry_id=entry_id,
                    from_band=band,
                    to_band=None,
                    reason=f"Void entry exceeds {self.config.void_days}-day retention ({age_days} days old)",
                    age_days=age_days,
                )
            return RetentionAction(
                action_type="KEEP",
                entry_id=entry_id,
                from_band=band,
                to_band=None,
                reason=f"Void entry within {self.config.void_days}-day window ({age_days} days old)",
                age_days=age_days,
            )

        # ACTIVE: Delete after HOT period (session-only)
        if band == "ACTIVE":
            if age_days > self.config.hot_days:
                return RetentionAction(
                    action_type="DELETE",
                    entry_id=entry_id,
                    from_band=band,
                    to_band=None,
                    reason=f"Active stream entry exceeds {self.config.hot_days}-day HOT tier ({age_days} days old)",
                    age_days=age_days,
                )
            return RetentionAction(
                action_type="KEEP",
                entry_id=entry_id,
                from_band=band,
                to_band=None,
                reason=f"Active stream entry in HOT tier ({age_days} days old)",
                age_days=age_days,
            )

        # PHOENIX: Handle based on status
        if band == "PHOENIX":
            status = entry.get("metadata", {}).get("status", "draft")
            if status in ("sealed", "rejected"):
                # Sealed → VAULT, Rejected → LEDGER (archive)
                target = "VAULT" if status == "sealed" else "LEDGER"
                return RetentionAction(
                    action_type="MOVE",
                    entry_id=entry_id,
                    from_band=band,
                    to_band=target,
                    reason=f"Phoenix proposal {status}, moving to {target}",
                    age_days=age_days,
                )
            if age_days > self.config.warm_days:
                return RetentionAction(
                    action_type="KEEP",  # Flag for review but don't auto-delete
                    entry_id=entry_id,
                    from_band=band,
                    to_band=None,
                    reason=f"Phoenix proposal stale (>{self.config.warm_days} days), needs human review",
                    age_days=age_days,
                )
            return RetentionAction(
                action_type="KEEP",
                entry_id=entry_id,
                from_band=band,
                to_band=None,
                reason=f"Phoenix proposal active in WARM tier ({age_days} days old)",
                age_days=age_days,
            )

        # LEDGER: Archive after WARM period
        if band == "LEDGER":
            if age_days > self.config.warm_days:
                return RetentionAction(
                    action_type="ARCHIVE",
                    entry_id=entry_id,
                    from_band=band,
                    to_band="ARCHIVE",
                    reason=f"Ledger entry moving to COLD archive ({age_days} days old)",
                    age_days=age_days,
                )
            return RetentionAction(
                action_type="KEEP",
                entry_id=entry_id,
                from_band=band,
                to_band=None,
                reason=f"Ledger entry in WARM tier ({age_days} days old)",
                age_days=age_days,
            )

        # WITNESS: Rolling window
        if band == "WITNESS":
            witness_retention = 30  # Default 30 days for witness
            if age_days > witness_retention:
                return RetentionAction(
                    action_type="DELETE",
                    entry_id=entry_id,
                    from_band=band,
                    to_band=None,
                    reason=f"Witness entry exceeds {witness_retention}-day window ({age_days} days old)",
                    age_days=age_days,
                )
            return RetentionAction(
                action_type="KEEP",
                entry_id=entry_id,
                from_band=band,
                to_band=None,
                reason=f"Witness entry in retention window ({age_days} days old)",
                age_days=age_days,
            )

        # Default: keep
        return RetentionAction(
            action_type="KEEP",
            entry_id=entry_id,
            from_band=band,
            to_band=None,
            reason=f"Unknown band {band}, conservatively retaining ({age_days} days old)",
            age_days=age_days,
        )

    def move_entry_to_band(
        self,
        entry: Dict[str, Any],
        from_band: str,
        to_band: str,
    ) -> Tuple[bool, str]:
        """
        Move an entry from one band to another.

        Args:
            entry: The entry to move
            from_band: Source band
            to_band: Target band

        Returns:
            Tuple of (success, reason)
        """
        # Validate transition is allowed
        allowed_targets = BAND_TRANSITIONS.get(from_band, [])
        if to_band not in allowed_targets:
            return False, f"Transition from {from_band} to {to_band} not allowed. Allowed: {allowed_targets}"

        # Log the move
        self._action_log.append(RetentionAction(
            action_type="MOVE",
            entry_id=entry.get("entry_id", "unknown"),
            from_band=from_band,
            to_band=to_band,
            reason=f"Manual move from {from_band} to {to_band}",
            age_days=0,
        ))

        return True, f"Entry moved from {from_band} to {to_band}"

    def auto_cleanup_void_band(
        self,
        void_entries: List[Dict[str, Any]],
    ) -> Tuple[int, List[str]]:
        """
        Clean up Void band entries older than retention period.

        Args:
            void_entries: List of Void band entries

        Returns:
            Tuple of (count_deleted, list_of_deleted_ids)
        """
        now = datetime.now(timezone.utc)
        deleted_ids: List[str] = []

        for entry in void_entries:
            age_days = self._compute_age_days(entry.get("timestamp", ""), now)
            if age_days > self.config.void_days:
                entry_id = entry.get("entry_id", "unknown")
                deleted_ids.append(entry_id)

                self._action_log.append(RetentionAction(
                    action_type="DELETE",
                    entry_id=entry_id,
                    from_band="VOID",
                    to_band=None,
                    reason=f"Auto-cleanup: Void entry {age_days} days old > {self.config.void_days}",
                    age_days=age_days,
                ))

        return len(deleted_ids), deleted_ids

    def get_band_status(
        self,
        band_name: str,
        entries: List[Dict[str, Any]],
    ) -> BandStatus:
        """
        Get status information for a band.

        Args:
            band_name: Name of the band
            entries: Entries in the band

        Returns:
            BandStatus with band information
        """
        tier = BAND_TIER_MAP.get(band_name, RetentionTier.WARM)
        retention_days = self._get_retention_days(tier)

        # Compute statistics
        entry_count = len(entries)
        size_bytes = sum(len(json.dumps(e)) for e in entries)

        # Find oldest/newest
        oldest: Optional[str] = None
        newest: Optional[str] = None
        now = datetime.now(timezone.utc)
        cleanup_count = 0

        for entry in entries:
            ts = entry.get("timestamp", "")
            if ts:
                if oldest is None or ts < oldest:
                    oldest = ts
                if newest is None or ts > newest:
                    newest = ts

            # Count entries that would be cleaned up
            if retention_days is not None:
                age_days = self._compute_age_days(ts, now)
                if age_days > retention_days:
                    cleanup_count += 1

        return BandStatus(
            band_name=band_name,
            entry_count=entry_count,
            size_bytes=size_bytes,
            oldest_entry_timestamp=oldest,
            newest_entry_timestamp=newest,
            tier=tier,
            retention_days=retention_days,
            estimated_cleanup_count=cleanup_count,
        )

    def manual_promotion(
        self,
        entry: Dict[str, Any],
        target_band: str,
        justification: str,
    ) -> Tuple[bool, str]:
        """
        Manually promote an entry to a different band.

        Args:
            entry: Entry to promote
            target_band: Target band
            justification: Reason for promotion

        Returns:
            Tuple of (success, reason)
        """
        from_band = entry.get("band", "UNKNOWN")
        entry_id = entry.get("entry_id", "unknown")

        # Validate transition
        allowed_targets = BAND_TRANSITIONS.get(from_band, [])
        if target_band not in allowed_targets:
            return False, f"Cannot promote from {from_band} to {target_band}. Allowed: {allowed_targets}"

        # Log promotion
        self._action_log.append(RetentionAction(
            action_type="MOVE",
            entry_id=entry_id,
            from_band=from_band,
            to_band=target_band,
            reason=f"Manual promotion: {justification}",
            age_days=0,
        ))

        return True, f"Entry {entry_id} promoted from {from_band} to {target_band}"

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _compute_age_days(self, timestamp_str: str, now: datetime) -> int:
        """Compute age in days from timestamp string."""
        if not timestamp_str:
            return 0

        try:
            if isinstance(timestamp_str, str):
                entry_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            else:
                entry_time = datetime.fromtimestamp(float(timestamp_str), tz=timezone.utc)
            return (now - entry_time).days
        except (ValueError, TypeError):
            return 0

    def _get_retention_days(self, tier: RetentionTier) -> Optional[int]:
        """Get retention days for a tier."""
        if tier == RetentionTier.HOT:
            return self.config.hot_days
        elif tier == RetentionTier.WARM:
            return self.config.warm_days
        elif tier == RetentionTier.VOID:
            return self.config.void_days
        elif tier == RetentionTier.COLD:
            return None  # Permanent
        return None

    def get_action_log(self) -> List[RetentionAction]:
        """Return the action log."""
        return list(self._action_log)

    def clear_action_log(self) -> None:
        """Clear the action log."""
        self._action_log.clear()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def compute_entry_age_days(timestamp_str: str) -> int:
    """Compute age of an entry in days."""
    now = datetime.now(timezone.utc)
    if not timestamp_str:
        return 0

    try:
        entry_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        return (now - entry_time).days
    except (ValueError, TypeError):
        return 0


def should_delete_void_entry(entry: Dict[str, Any], retention_days: int = 90) -> bool:
    """Quick check if a Void entry should be deleted."""
    ts = entry.get("timestamp", "")
    age_days = compute_entry_age_days(ts)
    return age_days > retention_days


def get_tier_for_band(band_name: str) -> RetentionTier:
    """Get the retention tier for a band."""
    return BAND_TIER_MAP.get(band_name, RetentionTier.WARM)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "RetentionTier",
    # Data classes
    "RetentionConfig",
    "RetentionAction",
    "RetentionReport",
    "BandStatus",
    # Main class
    "MemoryRetentionManager",
    # Convenience functions
    "compute_entry_age_days",
    "should_delete_void_entry",
    "get_tier_for_band",
    # Constants
    "DEFAULT_RETENTION_DAYS",
    "BAND_TIER_MAP",
    "BAND_TRANSITIONS",
]
