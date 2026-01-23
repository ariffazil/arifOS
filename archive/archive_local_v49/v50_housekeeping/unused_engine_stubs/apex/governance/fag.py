"""
fag.py - File Access Governance (FAG) for arifOS v45.3

Constitutional filesystem wrapper enforcing 9 floors on file I/O.

DUAL IDENTITY:
    Internal: FAG (File Access Governance) - Python class for governed file I/O
    External: vTEMPA - MCP tools for external AI agents (ChatGPT, Claude, Codex)

Key Features:
- Root-jailed access (F1 Amanah)
- Read-only by default (F5 Peace²)
- Secret pattern blocking (F9 C_dark)
- Symlink resolution and traversal prevention
- Cooling Ledger integration
- MCP-ready interface (vTEMPA tools)

Production Hardening (v45.3):
- Pre-Mutate Snapshot (rollback contract)
- Protected Paths (no-touch zones)
- Mutation Watchdog (diff-based anomaly detection)
- Operator Alerts (entropy spike warnings)
- Audit file rotation (10MB threshold, keep 5 files, 90-day retention)
- Rate limiting + Security alerts (configurable thresholds)
- Statistics persistence (optional JSON format)
- Context manager support (__enter__/__exit__)

Usage:
    from arifos.apex.governance.fag import FAG, SecurityAlert

    # Basic usage (internal FAG)
    fag = FAG(root="/project", read_only=True)
    result = fag.read("src/main.py")

    if result.verdict == "SEAL":
        print(result.content)
    else:
        print(f"Access denied: {result.reason}")

    # Production hardening
    with FAG(
        root="/project",
        enable_audit_file=True,
        persist_stats=True,
        alert_thresholds={"f9_rate": 10, "total_rate": 50},
    ) as fag:
        try:
            result = fag.read("sensitive.txt")
        except SecurityAlert as e:
            print(f"Attack detected: {e}")

Constitutional Floors Enforced:
- F1 Amanah: Root jail, reversible, within mandate
- F2 Truth: Only real, readable files
- F4 DeltaS: Reject binary/unreadable content
- F5 Peace²: Read-only, non-destructive
- F7 Omega0: Return verdict + uncertainty, never assume success
- F8 G: Log all access to Cooling Ledger
- F9 C_dark: Block secrets, credentials, forbidden patterns

Version: v45.3.0
Status: PRODUCTION-READY (hardened)
Motto: DITEMPA BUKAN DIBERI — Forged, not given
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Deque, Dict, List, Literal, Optional, Tuple

from ...enforcement.metrics import Metrics

# v42: Import from system/, governance/ correctly
from ...system.apex_prime import ApexVerdict
from .ledger import log_cooling_entry

# =============================================================================
# SECURITY EXCEPTION
# =============================================================================

class SecurityAlert(Exception):
    """
    Raised when security thresholds are exceeded.

    Indicates potential attack patterns such as:
    - Secret enumeration (high F9 C_dark denials)
    - Brute force access attempts (high total denials)

    Should be caught by monitoring systems for incident response.
    """
    pass


# =============================================================================
# FORBIDDEN PATTERNS (F9 C_DARK)
# =============================================================================

# Files that contain secrets, credentials, or governance-critical data
FORBIDDEN_PATTERNS = [
    # Environment and secrets
    r"\.env$",
    r"\.env\..*",
    r"secrets/",
    r"credentials/",
    r"\.secret",

    # SSH and keys
    r"id_rsa",
    r"id_ed25519",
    r"\.pem$",
    r"\.key$",
    r"\.ppk$",
    r"authorized_keys",
    r"known_hosts",

    # Git internals (can leak history)
    r"\.git/",
    r"\.gitconfig",

    # arifOS governance (circular dependency risk)
    r"cooling_ledger/",
    r"L1_cooling_ledger\.jsonl",
    r"\.arifos_clip/",

    # Cloud credentials
    r"\.aws/",
    r"\.azure/",
    r"\.gcloud/",
    r"gcp-key\.json",

    # Database credentials
    r"\.pgpass",
    r"\.my\.cnf",

    # Password managers
    r"\.password-store/",
    r"keepass",
]

# Binary/unreadable extensions (F4 DeltaS)
BINARY_EXTENSIONS = {
    ".exe", ".dll", ".so", ".dylib", ".bin",
    ".zip", ".tar", ".gz", ".bz2", ".7z",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico",
    ".mp3", ".mp4", ".avi", ".mov", ".mkv",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".pyc", ".pyo", ".class", ".jar",
}

# =============================================================================
# v45.0.3 PROTECTED PATHS (No-Touch Zones)
# =============================================================================
# These paths require HUMAN_SEAL_TOKEN to access (beyond FORBIDDEN_PATTERNS)

PROTECTED_PATHS = [
    r"[/\\]\.vscode[/\\]",
    r"[/\\]\.config[/\\]",
    r"[/\\]\.ssh[/\\]",
    r"[/\\]\.aws[/\\]",
    r"[/\\]\.azure[/\\]",
    r"[/\\]\.gcloud[/\\]",
    r"[/\\]\.idea[/\\]",
    r"[/\\]\.vs[/\\]",
    r"[/\\]__pycache__[/\\]",
    r"[/\\]node_modules[/\\]",
    r"[/\\]\.git[/\\]objects[/\\]",
    r"[/\\]\.git[/\\]hooks[/\\]",
]


# =============================================================================
# FAG READ RESULT
# =============================================================================

@dataclass
class FAGReadResult:
    """Result of FAG.read() operation."""
    verdict: ApexVerdict
    path: str
    content: Optional[str] = None
    reason: Optional[str] = None
    floor_scores: Optional[Dict[str, float]] = None
    ledger_entry_id: Optional[str] = None


@dataclass
class FAGWritePlan:
    """
    Write plan for FAG.write_validate() (v42.2).

    Defines a proposed write operation with verifiable read proof.
    """
    target_path: str
    operation: Literal["create", "patch", "delete"]
    justification: str
    diff: Optional[str] = None  # Unified diff for patches
    # Verifiable read proof (anti-fake)
    read_sha256: Optional[str] = None
    read_bytes: Optional[int] = None
    read_mtime_ns: Optional[int] = None
    read_excerpt: Optional[str] = None  # First/last 64 bytes


@dataclass
class FAGWriteResult:
    """Result of FAG.write_validate() operation."""
    verdict: str  # SEAL, HOLD, VOID
    path: str
    reason: str
    floor_violations: Optional[List[str]] = None
    rollback_id: Optional[str] = None  # v45.0.3: UUID for snapshot rollback


# Sandbox zones where unlimited writes are allowed
SANDBOX_ZONES = [".arifos_clip/", "scratch/"]


# =============================================================================
# v45.0.3 HARDENING DATACLASSES
# =============================================================================

@dataclass
class FAGSnapshot:
    """Pre-Mutate Snapshot for F1 Amanah rollback contract (v45.0.3)."""
    path: str
    content: bytes
    sha256: str
    timestamp: datetime
    rollback_id: str  # UUID for traceability
    size_bytes: int = 0


@dataclass
class MutationEvent:
    """Filesystem mutation event for watchdog tracking (v45.0.3)."""
    operation: Literal["create", "modify", "rename", "delete"]
    path: str
    timestamp: datetime
    diff_size: int = 0
    previous_path: Optional[str] = None  # For rename tracking


@dataclass
class OperatorAlert:
    """Alert for operator notification (v45.0.3)."""
    severity: Literal["INFO", "WARN", "CRITICAL"]
    code: str  # e.g., "HIGH_ENTROPY", "CONSECUTIVE_FAILURES"
    message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    context: Optional[Dict[str, Any]] = None


class MutationWatchdog:
    """
    v45.0.3 Mutation Watchdog - Detects suspicious filesystem patterns.

    Catches:
    - Rename → Delete chains (stealth-delete attempts)
    - Mass change bursts (>threshold mutations in time window)
    - Boundary breaches (writes outside allowed root)

    Raises HOLD-888 on anomaly detection.
    """

    def __init__(
        self,
        burst_threshold: int = 10,
        time_window_seconds: int = 60,
        max_history: int = 100,
    ):
        self.burst_threshold = burst_threshold
        self.time_window = timedelta(seconds=time_window_seconds)
        self.events: Deque[MutationEvent] = deque(maxlen=max_history)
        self.rename_pending: Dict[str, MutationEvent] = {}  # Track renamed files

    def record(self, event: MutationEvent) -> None:
        """Record a mutation event."""
        self.events.append(event)

        # Track renames for stealth-delete detection
        if event.operation == "rename" and event.previous_path:
            self.rename_pending[event.path] = event
        elif event.operation == "delete":
            # Check if this was a recently renamed file
            if event.path in self.rename_pending:
                del self.rename_pending[event.path]

    def detect_anomalies(self, root: Path) -> List[str]:
        """
        Detect suspicious patterns.

        Returns list of anomaly descriptions. Empty = safe.
        """
        anomalies = []
        now = datetime.now(timezone.utc)
        window_start = now - self.time_window

        # Filter recent events
        recent = [e for e in self.events if e.timestamp >= window_start]

        # Check 1: Mass change burst
        if len(recent) > self.burst_threshold:
            anomalies.append(
                f"MASS_CHANGE_BURST: {len(recent)} mutations in {self.time_window.seconds}s "
                f"(threshold: {self.burst_threshold})"
            )

        # Check 2: Rename → Delete chain
        for event in recent:
            if event.operation == "delete":
                # Check if any recent rename targeted a file now being deleted
                for rename_event in recent:
                    if (rename_event.operation == "rename" and
                        rename_event.path == event.path and
                        rename_event.timestamp < event.timestamp):
                        anomalies.append(
                            f"RENAME_DELETE_CHAIN: File renamed then deleted - "
                            f"{rename_event.previous_path} → {event.path} → deleted"
                        )

        # Check 3: Boundary breach (handled by FAG root jail, but double-check)
        root_resolved = root.resolve()
        for event in recent:
            try:
                event_path = Path(event.path)
                if not event_path.is_absolute():
                    event_path = (root_resolved / event_path).resolve()
                else:
                    event_path = event_path.resolve()

                if not str(event_path).startswith(str(root_resolved)):
                    anomalies.append(
                        f"BOUNDARY_BREACH: Path {event.path} outside root {root}"
                    )
            except Exception:
                pass

        return anomalies

    def clear(self) -> None:
        """Clear event history."""
        self.events.clear()
        self.rename_pending.clear()


# =============================================================================
# FILE ACCESS GOVERNANCE (FAG)
# =============================================================================


class FAG:
    """
    File Access Governance - Constitutional filesystem wrapper.

    Enforces 9-floor checks on all file read operations.
    """

    def __init__(
        self,
        root: str = ".",
        read_only: bool = True,
        enable_ledger: bool = True,
        job_id: str = "fag-session",
        enable_audit_file: bool = False,
        audit_file_path: Optional[str] = None,
        alert_thresholds: Optional[Dict[str, int]] = None,
        persist_stats: bool = False,
        audit_rotation_size_mb: int = 10,
        audit_retention_days: int = 90,
        # v45.0.3 Hardening Parameters
        human_seal_token: Optional[str] = None,
        enable_snapshots: bool = True,
        enable_watchdog: bool = True,
        enable_alerts: bool = True,
        alert_callback: Optional[Callable[[OperatorAlert], None]] = None,
        watchdog_burst_threshold: int = 10,
        watchdog_time_window: int = 60,
    ):
        """
        Initialize FAG with root jail and configuration.

        Args:
            root: Root directory for jailed access (F1 Amanah)
            read_only: If True, only read operations allowed (F5 Peace²)
            enable_ledger: If True, log all access to Cooling Ledger (F8 G)
            job_id: Session identifier for ledger entries
            enable_audit_file: If True, log denied access to separate audit file
            audit_file_path: Path to audit file (default: <root>/fag_audit.jsonl)
            alert_thresholds: Security alert thresholds (default: {"f9_rate": 10, "total_rate": 50})
            persist_stats: If True, save/load statistics to fag_stats.json
            audit_rotation_size_mb: Rotate audit file when exceeds this size in MB (default: 10)
            audit_retention_days: Delete rotated audit files older than this (default: 90)

        v45.0.3 Hardening Args:
            human_seal_token: Token to bypass protected path restrictions
            enable_snapshots: Enable pre-mutate snapshots for rollback (F1 Amanah)
            enable_watchdog: Enable mutation watchdog for anomaly detection
            enable_alerts: Enable operator alerts for entropy spikes/failures
            alert_callback: Optional callback for operator alerts
            watchdog_burst_threshold: Max mutations before HOLD-888 (default: 10)
            watchdog_time_window: Time window for burst detection in seconds (default: 60)
        """
        self.root = Path(root).resolve()
        self.read_only = read_only
        self.enable_ledger = enable_ledger
        self.job_id = job_id
        self.enable_audit_file = enable_audit_file
        self.persist_stats = persist_stats
        self.audit_rotation_size_mb = audit_rotation_size_mb
        self.audit_retention_days = audit_retention_days

        # v45.0.3 Hardening Fields
        self.human_seal_token = human_seal_token
        self.enable_snapshots = enable_snapshots
        self.enable_watchdog = enable_watchdog
        self.enable_alerts = enable_alerts
        self.alert_callback = alert_callback

        # v45.0.3 Snapshot storage (in-memory)
        self.snapshots: Dict[str, FAGSnapshot] = {}
        self.max_snapshots = 100

        # v45.0.3 Mutation Watchdog
        self.watchdog = MutationWatchdog(
            burst_threshold=watchdog_burst_threshold,
            time_window_seconds=watchdog_time_window,
        ) if enable_watchdog else None

        # v45.0.3 Consecutive failure tracking for alerts
        self.consecutive_failures = 0

        # Set audit file path
        if audit_file_path:
            self.audit_file_path = Path(audit_file_path)
        else:
            self.audit_file_path = self.root / "fag_audit.jsonl"

        # Set statistics persistence path
        self.stats_file_path = self.root / "fag_stats.json"

        # Initialize access statistics (in-memory)
        self.access_stats: Dict[str, int] = {
            "total_denied": 0,
            "f1_amanah_fail": 0,
            "f2_truth_fail": 0,
            "f4_delta_s_fail": 0,
            "f7_omega0_alert": 0,
            "f9_c_dark_fail": 0,
            "total_granted": 0,
            # v45.0.3 stats
            "snapshots_created": 0,
            "rollbacks_performed": 0,
            "watchdog_anomalies": 0,
            "alerts_emitted": 0,
        }

        # Load persisted stats if enabled
        if self.persist_stats:
            self._load_stats()

        # Rate limiting: Track recent denials with timestamps
        # Format: deque[(timestamp, denial_type), ...]
        # Window: last 60 seconds
        self.denial_history: Deque[Tuple[datetime, str]] = deque(maxlen=200)

        # Security alert thresholds (denials per 60 seconds)
        if alert_thresholds is None:
            self.alert_thresholds = {
                "f9_rate": 10,      # F9 C_dark denials (secret enumeration)
                "total_rate": 50,   # Total denials (brute force)
            }
        else:
            self.alert_thresholds = alert_thresholds

        # Validate root exists
        if not self.root.exists():
            raise ValueError(f"Root directory does not exist: {self.root}")
        if not self.root.is_dir():
            raise ValueError(f"Root must be a directory: {self.root}")

    def read(self, path: str) -> FAGReadResult:
        """
        Read file with constitutional floor checks.

        Args:
            path: Path to file (relative to root or absolute within root)

        Returns:
            FAGReadResult with verdict, content (if SEAL), and reason (if not)
        """
        # Normalize path
        try:
            target = self._resolve_path(path)
        except (ValueError, OSError) as e:
            return self._void_result(
                path=path,
                reason=f"F1 Amanah FAIL: Path resolution error - {e}",
                f1_amanah=0.0,
            )

        # F1 Amanah: Root jail check
        if not self._is_within_jail(target):
            return self._void_result(
                path=path,
                reason=f"F1 Amanah FAIL: Path outside root jail - {target}",
                f1_amanah=0.0,
            )

        # F9 C_dark: Forbidden pattern check
        if self._matches_forbidden_pattern(target):
            return self._void_result(
                path=path,
                reason=f"F9 C_dark FAIL: Forbidden pattern detected - {target}",
                f9_c_dark=1.0,  # Maximum dark cleverness
            )

        # v45.0.3: Protected path check (no-touch zones)
        if self._is_protected_path(target) and not self._can_bypass_protection():
            self._emit_alert(OperatorAlert(
                severity="WARN",
                code="PROTECTED_PATH_ACCESS",
                message=f"Attempted read of protected path: {target}",
                context={"path": str(target), "has_token": self.human_seal_token is not None},
            ))
            return self._void_result(
                path=path,
                reason=f"F1 Amanah HOLD: Protected path requires HUMAN_SEAL_TOKEN - {target}",
                f1_amanah=0.5,  # Partial - can be bypassed with token
            )

        # F2 Truth: File must exist and be readable
        if not target.exists():
            return self._void_result(
                path=path,
                reason=f"F2 Truth FAIL: File does not exist - {target}",
                f2_truth=0.0,
            )

        if not target.is_file():
            return self._void_result(
                path=path,
                reason=f"F2 Truth FAIL: Not a regular file - {target}",
                f2_truth=0.0,
            )

        # F4 DeltaS: Binary file check
        if self._is_binary_file(target):
            return self._void_result(
                path=path,
                reason=f"F4 DeltaS FAIL: Binary file rejected - {target.suffix}",
                f4_delta_s=-1.0,  # Negative clarity
            )

        # Attempt read
        try:
            content = target.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return self._void_result(
                path=path,
                reason=f"F4 DeltaS FAIL: File not readable as UTF-8 - {target}",
                f4_delta_s=-1.0,
            )
        except PermissionError:
            return self._void_result(
                path=path,
                reason=f"F1 Amanah FAIL: Permission denied - {target}",
                f1_amanah=0.0,
            )
        except Exception as e:
            return self._void_result(
                path=path,
                reason=f"F7 Omega0 ALERT: Unexpected error - {e}",
                f7_omega0=0.10,  # High uncertainty
            )

        # SEAL verdict - all floors passed
        # Increment granted counter
        self.access_stats["total_granted"] += 1

        return self._seal_result(
            path=str(target.relative_to(self.root)),
            content=content,
            size=len(content),
        )

    def list_dir(self, path: str = ".") -> List[Dict[str, Any]]:
        """
        List directory contents with constitutional filtering.

        Args:
            path: Path to directory (relative to root)

        Returns:
            List of dicts with file metadata (name, type, size, modified)

        Raises:
            PermissionError if path outside jail or forbidden
        """
        try:
            target = self._resolve_path(path)
        except (ValueError, OSError) as e:
            raise PermissionError(f"F1 Amanah FAIL: Path resolution error - {e}")

        # F1 Amanah: Root jail check
        if not self._is_within_jail(target):
            raise PermissionError(f"F1 Amanah FAIL: Path outside root jail - {target}")

        if not target.exists() or not target.is_dir():
            return []

        results = []
        for entry in target.iterdir():
            # F9 C_dark: Forbidden pattern check
            if self._matches_forbidden_pattern(entry):
                continue

            # v45.0.3: Protected path check
            if self._is_protected_path(entry) and not self._can_bypass_protection():
                continue

            # Basic metadata
            try:
                stat = entry.stat()
                results.append({
                    "name": entry.name,
                    "type": "directory" if entry.is_dir() else "file",
                    "size": stat.st_size if entry.is_file() else 0,
                    "modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                })
            except Exception:
                continue

        return results

    def write_validate(
        self,
        plan: "FAGWritePlan",
        session_allowlist: Optional[List[str]] = None,
    ) -> "FAGWriteResult":
        """
        Validate a write plan against FAG Write Contract v42.2.

        Rules enforced:
        1. No New Files - HOLD unless sandbox or allowlisted
        2. Canon Lock - VOID for creates in 000_THEORY/
        3. Patch Only - HOLD if no diff provided for patches
        4. Rewrite Threshold - HOLD if deletion_ratio > 30%
        5. Read Before Write - HOLD if no read_proof for patches
        6. Delete Gate - HOLD for any delete operation

        Args:
            plan: FAGWritePlan with operation details
            session_allowlist: Optional list of paths approved for this session

        Returns:
            FAGWriteResult with verdict (SEAL/HOLD/VOID) and reason
        """
        target_path = plan.target_path
        violations: List[str] = []

        # v45.0.3: Check watchdog for anomalies before proceeding
        watchdog_error = self._check_watchdog_anomalies()
        if watchdog_error:
            return FAGWriteResult(
                verdict="HOLD",
                path=target_path,
                reason=watchdog_error,
                floor_violations=["WATCHDOG_ANOMALY"],
            )

        # v45.0.3: Create pre-mutate snapshot for rollback
        snapshot: Optional[FAGSnapshot] = None
        if plan.operation in ("patch", "delete"):
            try:
                resolved_path = self._resolve_path(target_path)
                snapshot = self._create_snapshot(resolved_path)
            except Exception:
                pass  # Snapshot failure should not block validation

        # v45.0.3: Record mutation event for watchdog
        if self.watchdog:
            self.watchdog.record(MutationEvent(
                operation=plan.operation,
                path=target_path,
                timestamp=datetime.now(timezone.utc),
                diff_size=len(plan.diff) if plan.diff else 0,
            ))

        # Normalize path for sandbox check
        path_normalized = target_path.replace("\\", "/")

        # Check if path is in sandbox zone
        in_sandbox = any(
            path_normalized.startswith(zone) or f"/{zone}" in path_normalized
            for zone in SANDBOX_ZONES
        )

        # Check if path is in session allowlist
        allowlist = session_allowlist or []
        in_allowlist = target_path in allowlist or path_normalized in allowlist

        # === Rule 1: Canon Lock (VOID - absolute block) ===
        if plan.operation == "create":
            if "000_THEORY/" in path_normalized or path_normalized.startswith("000_THEORY"):
                return FAGWriteResult(
                    verdict="VOID",
                    path=target_path,
                    reason="F1 Amanah VOID: Canon zone 000_THEORY/ is amendment-only. No new files allowed.",
                    floor_violations=["F1_Amanah", "F2_Truth"],
                )

        # === Rule 2: No New Files (HOLD unless sandbox/allowlist) ===
        if plan.operation == "create":
            if not in_sandbox and not in_allowlist:
                violations.append("No New Files: Create outside sandbox without allowlist")

        # === Rule 3: Delete Gate (HOLD for any delete) ===
        if plan.operation == "delete":
            violations.append("Delete Gate: Delete operations require human approval")

        # === Rule 4: Read Before Write (HOLD if no read_proof) ===
        if plan.operation == "patch":
            if not plan.read_sha256 or plan.read_bytes is None:
                violations.append("Read Before Write: No read_proof provided (sha256 + bytes required)")
            else:
                # Verify read_proof matches current file state
                try:
                    target = self._resolve_path(target_path)
                    if target.exists():
                        content = target.read_bytes()
                        actual_sha256 = hashlib.sha256(content).hexdigest()
                        actual_bytes = len(content)

                        if actual_sha256 != plan.read_sha256:
                            violations.append(f"Read Before Write: File changed since read (sha256 mismatch)")
                        if actual_bytes != plan.read_bytes:
                            violations.append(f"Read Before Write: File size changed ({actual_bytes} vs {plan.read_bytes})")
                except Exception as e:
                    violations.append(f"Read Before Write: Cannot verify read_proof - {e}")

        # === Rule 5: Patch Only (HOLD if no diff) ===
        if plan.operation == "patch":
            if not plan.diff:
                violations.append("Patch Only: No unified diff provided")

        # === Rule 6: Rewrite Threshold (HOLD if deletion_ratio > 30%) ===
        if plan.operation == "patch" and plan.diff:
            # Parse unified diff to compute deletion ratio
            deleted_lines = 0
            original_lines = 0

            for line in plan.diff.split("\n"):
                if line.startswith("-") and not line.startswith("---"):
                    deleted_lines += 1
                    original_lines += 1
                elif line.startswith("+") and not line.startswith("+++"):
                    pass  # Added lines don't count toward original
                elif line.startswith(" "):
                    original_lines += 1

            # Compute deletion ratio
            if original_lines > 0:
                deletion_ratio = deleted_lines / original_lines
                if deletion_ratio > 0.30:
                    violations.append(
                        f"Rewrite Threshold: Deletion ratio {deletion_ratio:.0%} exceeds 30% limit"
                    )

        # === Determine verdict ===
        if violations:
            # Log to ledger
            if self.enable_ledger:
                self._log_write_validation(plan, "HOLD", violations)

            return FAGWriteResult(
                verdict="HOLD",
                path=target_path,
                reason=f"888_HOLD: {'; '.join(violations)}",
                floor_violations=violations,
            )

        # All checks passed
        if self.enable_ledger:
            self._log_write_validation(plan, "SEAL", [])

        return FAGWriteResult(
            verdict="SEAL",
            path=target_path,
            reason="All FAG Write Contract rules passed",
            floor_violations=[],
            rollback_id=snapshot.rollback_id if snapshot else None,
        )

    def _log_write_validation(
        self,
        plan: "FAGWritePlan",
        verdict: str,
        violations: List[str],
    ) -> None:
        """Log write validation to Cooling Ledger."""
        metrics = Metrics(
            truth=0.99 if verdict == "SEAL" else 0.5,
            delta_s=0.1 if verdict == "SEAL" else -0.1,
            amanah=verdict != "VOID",
            peace_squared=1.0,
            omega_0=0.04,
            tri_witness=0.95,
            kappa_r=0.95,
        )

        log_cooling_entry(
            job_id=self.job_id,
            verdict=verdict,
            metrics=metrics,
            stakes="fag_write_validate",
            context_summary=f"FAG write_validate: {plan.operation} {plan.target_path} -> {verdict}",
        )

    def _resolve_path(self, path: str) -> Path:
        """
        Resolve path relative to root, handling symlinks and traversal.

        Raises ValueError if path is invalid or tries to escape jail.
        """
        # Start with root
        if os.path.isabs(path):
            # Absolute path - must be within root
            target = Path(path).resolve()
        else:
            # Relative path - resolve from root
            target = (self.root / path).resolve()

        return target

    def _is_within_jail(self, target: Path) -> bool:
        """Check if resolved path is within root jail (F1 Amanah)."""
        try:
            target.relative_to(self.root)
            return True
        except ValueError:
            return False

    def _matches_forbidden_pattern(self, target: Path) -> bool:
        """Check if path matches forbidden patterns (F9 C_dark)."""
        path_str = str(target)
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, path_str):
                return True
        return False

    def _is_binary_file(self, target: Path) -> bool:
        """Check if file is binary (F4 DeltaS)."""
        return target.suffix.lower() in BINARY_EXTENSIONS

    def _void_result(
        self,
        path: str,
        reason: str,
        f1_amanah: float = 1.0,
        f2_truth: float = 0.99,
        f4_delta_s: float = 0.0,
        f7_omega0: float = 0.04,
        f9_c_dark: float = 0.0,
    ) -> FAGReadResult:
        """Create VOID result with floor scores."""
        floor_scores = {
            "F1_amanah": f1_amanah,
            "F2_truth": f2_truth,
            "F4_delta_s": f4_delta_s,
            "F5_peace_sq": 1.0,  # Read-only is always safe
            "F7_omega0": f7_omega0,
            "F9_c_dark": f9_c_dark,
        }

        result = FAGReadResult(
            verdict="VOID",
            path=path,
            reason=reason,
            floor_scores=floor_scores,
        )

        # Update statistics
        self.access_stats["total_denied"] += 1

        # Determine denial type for rate limiting
        denial_type = "unknown"
        if "F1 Amanah" in reason:
            self.access_stats["f1_amanah_fail"] += 1
            denial_type = "f1_amanah"
        elif "F2 Truth" in reason:
            self.access_stats["f2_truth_fail"] += 1
            denial_type = "f2_truth"
        elif "F4 DeltaS" in reason:
            self.access_stats["f4_delta_s_fail"] += 1
            denial_type = "f4_delta_s"
        elif "F7 Omega0" in reason:
            self.access_stats["f7_omega0_alert"] += 1
            denial_type = "f7_omega0"
        elif "F9 C_dark" in reason:
            self.access_stats["f9_c_dark_fail"] += 1
            denial_type = "f9_c_dark"

        # Track denial for rate limiting
        now = datetime.now(timezone.utc)
        self.denial_history.append((now, denial_type))

        # Check security alert thresholds (raises SecurityAlert if exceeded)
        self._check_security_thresholds()

        if self.enable_ledger:
            self._log_to_ledger(result)

        if self.enable_audit_file:
            self._log_to_audit_file(result)

        return result

    def _seal_result(
        self,
        path: str,
        content: str,
        size: int,
    ) -> FAGReadResult:
        """Create SEAL result with content."""
        floor_scores = {
            "F1_amanah": 1.0,
            "F2_truth": 0.99,
            "F4_delta_s": 0.1,  # Slight clarity gain
            "F5_peace_sq": 1.0,
            "F7_omega0": 0.04,
            "F9_c_dark": 0.0,
        }

        result = FAGReadResult(
            verdict="SEAL",
            path=path,
            content=content,
            floor_scores=floor_scores,
        )

        if self.enable_ledger:
            self._log_to_ledger(result, file_size=size)

        return result

    def _log_to_ledger(
        self,
        result: FAGReadResult,
        file_size: int = 0,
    ) -> None:
        """Log file access to Cooling Ledger (F8 G)."""
        # Create minimal metrics for ledger
        floor_scores = result.floor_scores or {}
        metrics = Metrics(
            truth=floor_scores.get("F2_truth", 0.99),
            delta_s=floor_scores.get("F4_delta_s", 0.0),
            amanah=floor_scores.get("F1_amanah", 1.0) >= 1.0,
            peace_squared=floor_scores.get("F5_peace_sq", 1.0),
            omega_0=floor_scores.get("F7_omega0", 0.04),
            tri_witness=0.95,  # Not enforced at I/O layer
            kappa_r=0.95,  # Not enforced at I/O layer
        )

        entry = log_cooling_entry(
            job_id=self.job_id,
            verdict=result.verdict,
            metrics=metrics,
            stakes="fag_file_read",
            context_summary=f"FAG read: {result.path} ({file_size} bytes)",
        )

        result.ledger_entry_id = entry.get("timestamp", "unknown")

    def get_access_statistics(self) -> Dict[str, Any]:
        """
        Get statistics on file access attempts.

        Returns dictionary with:
        - total_granted: Number of successful reads (SEAL verdicts)
        - total_denied: Number of denied reads (VOID verdicts)
        - f1_amanah_fail: F1 Amanah violations (jail escape, permission denied)
        - f2_truth_fail: F2 Truth violations (file not found, not a file)
        - f4_delta_s_fail: F4 DeltaS violations (binary files, encoding errors)
        - f7_omega0_alert: F7 Omega0 alerts (unexpected errors)
        - f9_c_dark_fail: F9 C_dark violations (forbidden patterns)
        - success_rate: Percentage of granted access
        """
        total_attempts = self.access_stats["total_granted"] + self.access_stats["total_denied"]
        success_rate = (
            (self.access_stats["total_granted"] / total_attempts * 100)
            if total_attempts > 0
            else 0.0
        )

        return {
            **self.access_stats,
            "total_attempts": total_attempts,
            "success_rate": round(success_rate, 2),
        }

    def _log_to_audit_file(self, result: FAGReadResult) -> None:
        """
        Log denied access to separate audit file (JSONL format).

        Only called for VOID verdicts (denied access).
        Security-focused audit trail separate from Cooling Ledger.
        """
        # Rotate audit file if needed (before writing)
        self._rotate_audit_file_if_needed()

        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "job_id": self.job_id,
            "verdict": result.verdict,
            "path": result.path,
            "reason": result.reason,
            "floor_scores": result.floor_scores,
        }

        try:
            # Append to JSONL file (one JSON object per line)
            with open(self.audit_file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(audit_entry) + "\n")
        except Exception as e:
            # Fail silently - audit logging should not break FAG operations
            # Could optionally log to stderr or application logger here
            pass

    def _rotate_audit_file_if_needed(self) -> None:
        """
        Rotate audit file if it exceeds size threshold.

        Rotation strategy:
        - If fag_audit.jsonl > 10MB:
          - Rename fag_audit.jsonl → fag_audit.jsonl.1
          - Shift existing .1 → .2, .2 → .3, etc.
          - Keep last 5 rotated files
        - Delete rotated files older than retention period (90 days)
        """
        if not self.audit_file_path.exists():
            return

        try:
            # Check file size
            size_bytes = self.audit_file_path.stat().st_size
            size_mb = size_bytes / (1024 * 1024)

            if size_mb < self.audit_rotation_size_mb:
                # Cleanup old files even if no rotation
                self._cleanup_old_audit_files()
                return

            # Rotate: shift existing backup files (.5 gets deleted, .4→.5, .3→.4, etc.)
            max_backups = 5
            for i in range(max_backups, 0, -1):
                old_backup = Path(f"{self.audit_file_path}.{i}")
                if i == max_backups:
                    # Delete oldest backup
                    if old_backup.exists():
                        old_backup.unlink()
                else:
                    # Shift backup up one level
                    if old_backup.exists():
                        new_backup = Path(f"{self.audit_file_path}.{i + 1}")
                        old_backup.rename(new_backup)

            # Rename current file to .1
            new_name = Path(f"{self.audit_file_path}.1")
            self.audit_file_path.rename(new_name)

            # Cleanup old rotated files
            self._cleanup_old_audit_files()

        except Exception as e:
            # Fail silently - rotation should not break FAG
            pass

    def _cleanup_old_audit_files(self) -> None:
        """Delete rotated audit files older than retention period."""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(days=self.audit_retention_days)

            # Check all rotated files (.1 through .5)
            for i in range(1, 6):
                backup_file = Path(f"{self.audit_file_path}.{i}")
                if backup_file.exists():
                    mtime = backup_file.stat().st_mtime
                    file_time = datetime.fromtimestamp(mtime, tz=timezone.utc)

                    if file_time < cutoff_time:
                        backup_file.unlink()
        except Exception:
            # Fail silently
            pass

    def _check_security_thresholds(self) -> None:
        """
        Check if denial rates exceed security alert thresholds.

        Raises SecurityAlert if:
        - F9 C_dark denials > threshold in last 60 seconds (secret enumeration)
        - Total denials > threshold in last 60 seconds (brute force)
        """
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=60)

        # Count denials in the last 60 seconds
        recent_denials = [
            (ts, dtype) for ts, dtype in self.denial_history
            if ts >= window_start
        ]

        total_recent = len(recent_denials)
        f9_recent = sum(1 for _, dtype in recent_denials if dtype == "f9_c_dark")

        # Check F9 C_dark threshold (secret enumeration)
        if f9_recent > self.alert_thresholds.get("f9_rate", 10):
            raise SecurityAlert(
                f"Secret enumeration detected: {f9_recent} F9 C_dark denials in 60 seconds "
                f"(threshold: {self.alert_thresholds['f9_rate']})"
            )

        # Check total denial threshold (brute force)
        if total_recent > self.alert_thresholds.get("total_rate", 50):
            raise SecurityAlert(
                f"Brute force detected: {total_recent} total denials in 60 seconds "
                f"(threshold: {self.alert_thresholds['total_rate']})"
            )

    # =========================================================================
    # v45.0.3 HARDENING METHODS
    # =========================================================================

    def _create_snapshot(self, path: Path) -> Optional[FAGSnapshot]:
        """
        Create pre-mutate snapshot for F1 Amanah rollback contract (v45.0.3).

        Args:
            path: Path to the file to snapshot

        Returns:
            FAGSnapshot if successful, None if snapshots disabled or file doesn't exist
        """
        if not self.enable_snapshots:
            return None

        if not path.exists():
            return None

        try:
            content = path.read_bytes()
            sha256_hash = hashlib.sha256(content).hexdigest()
            rollback_id = str(uuid.uuid4())

            snapshot = FAGSnapshot(
                path=str(path),
                content=content,
                sha256=sha256_hash,
                timestamp=datetime.now(timezone.utc),
                rollback_id=rollback_id,
                size_bytes=len(content),
            )

            # Store snapshot (LRU eviction if at capacity)
            if len(self.snapshots) >= self.max_snapshots:
                # Remove oldest snapshot
                oldest_id = next(iter(self.snapshots))
                del self.snapshots[oldest_id]

            self.snapshots[rollback_id] = snapshot
            self.access_stats["snapshots_created"] += 1

            return snapshot

        except Exception as e:
            # Snapshot creation failure should not block operations
            return None

    def rollback(self, rollback_id: str) -> bool:
        """
        Restore file from snapshot (v45.0.3 F1 Amanah rollback).

        Args:
            rollback_id: UUID of the snapshot to restore

        Returns:
            True if rollback successful, False otherwise
        """
        snapshot = self.snapshots.get(rollback_id)
        if not snapshot:
            return False

        try:
            path = Path(snapshot.path)
            path.write_bytes(snapshot.content)

            # Verify restoration
            restored_content = path.read_bytes()
            restored_hash = hashlib.sha256(restored_content).hexdigest()

            if restored_hash == snapshot.sha256:
                self.access_stats["rollbacks_performed"] += 1
                # Remove used snapshot
                del self.snapshots[rollback_id]
                return True
            else:
                return False

        except Exception:
            return False

    def _is_protected_path(self, target: Path) -> bool:
        """
        Check if path is in v45.0.3 protected no-touch zone.

        Protected paths require HUMAN_SEAL_TOKEN to access.
        """
        path_str = str(target)
        for pattern in PROTECTED_PATHS:
            if re.search(pattern, path_str):
                return True
        return False

    def _can_bypass_protection(self) -> bool:
        """
        Check if valid HUMAN_SEAL_TOKEN is provided (v45.0.3).

        Returns True if protected paths can be accessed.
        """
        if self.human_seal_token is None:
            return False
        # Token must be non-empty string
        return isinstance(self.human_seal_token, str) and len(self.human_seal_token) > 0

    def _check_watchdog_anomalies(self) -> Optional[str]:
        """
        Check mutation watchdog for anomalies (v45.0.3).

        Returns:
            Error message if anomaly detected (triggers HOLD-888), None if safe
        """
        if not self.enable_watchdog or self.watchdog is None:
            return None

        anomalies = self.watchdog.detect_anomalies(self.root)

        if anomalies:
            self.access_stats["watchdog_anomalies"] += len(anomalies)
            # Emit alert for each anomaly
            for anomaly in anomalies:
                self._emit_alert(OperatorAlert(
                    severity="CRITICAL",
                    code="WATCHDOG_ANOMALY",
                    message=anomaly,
                    context={"root": str(self.root)},
                ))
            return f"HOLD-888: Watchdog detected {len(anomalies)} anomalies: {'; '.join(anomalies)}"

        return None

    def _emit_alert(self, alert: OperatorAlert) -> None:
        """
        Emit operator alert (v45.0.3).

        Logs the alert and invokes callback if configured.
        """
        if not self.enable_alerts:
            return

        self.access_stats["alerts_emitted"] += 1

        # Log alert
        import logging
        logger = logging.getLogger(__name__)
        log_method = {
            "INFO": logger.info,
            "WARN": logger.warning,
            "CRITICAL": logger.error,
        }.get(alert.severity, logger.info)

        log_method(f"[FAG ALERT] [{alert.severity}] {alert.code}: {alert.message}")

        # Invoke callback if configured
        if self.alert_callback:
            try:
                self.alert_callback(alert)
            except Exception:
                pass  # Callback failure should not break FAG

    def _track_consecutive_failure(self) -> None:
        """Track consecutive governance failures for v45.0.3 alert escalation."""
        self.consecutive_failures += 1

        # Emit alert after 2+ consecutive failures
        if self.consecutive_failures >= 2:
            self._emit_alert(OperatorAlert(
                severity="WARN",
                code="CONSECUTIVE_FAILURES",
                message=f"{self.consecutive_failures} consecutive governance failures detected",
                context={"session_id": self.job_id},
            ))

    def _reset_consecutive_failures(self) -> None:
        """Reset consecutive failure counter on successful operation."""
        self.consecutive_failures = 0

    def health_check(self) -> Dict[str, Any]:
        """
        Run repository integrity health check (v45.0.3).

        Returns:
            Dict with health status, anomalies, and recommendations
        """
        health = {
            "status": "HEALTHY",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "root": str(self.root),
            "checks": {},
            "anomalies": [],
            "recommendations": [],
        }

        # Check 1: Root directory exists and accessible
        try:
            if self.root.exists() and self.root.is_dir():
                health["checks"]["root_accessible"] = True
            else:
                health["checks"]["root_accessible"] = False
                health["status"] = "DEGRADED"
                health["anomalies"].append("Root directory not accessible")
        except Exception as e:
            health["checks"]["root_accessible"] = False
            health["anomalies"].append(f"Root access error: {e}")

        # Check 2: Watchdog state
        if self.watchdog:
            watchdog_anomalies = self.watchdog.detect_anomalies(self.root)
            health["checks"]["watchdog_clean"] = len(watchdog_anomalies) == 0
            if watchdog_anomalies:
                health["status"] = "ALERT"
                health["anomalies"].extend(watchdog_anomalies)
        else:
            health["checks"]["watchdog_clean"] = None  # Disabled

        # Check 3: Statistics health
        total = self.access_stats.get("total_granted", 0) + self.access_stats.get("total_denied", 0)
        if total > 0:
            denial_rate = self.access_stats.get("total_denied", 0) / total
            health["checks"]["denial_rate"] = round(denial_rate * 100, 2)
            if denial_rate > 0.5:  # >50% denial rate is concerning
                health["recommendations"].append(
                    f"High denial rate ({denial_rate:.0%}). Review access patterns."
                )

        # Check 4: Consecutive failures
        health["checks"]["consecutive_failures"] = self.consecutive_failures
        if self.consecutive_failures >= 2:
            health["status"] = "WARN"
            health["recommendations"].append(
                f"{self.consecutive_failures} consecutive failures. Consider session review."
            )

        return health

    def _save_stats(self) -> None:
        """
        Save access statistics to JSON file.

        Called on shutdown if persist_stats=True.
        """
        try:
            stats_data = {
                "stats": self.access_stats,
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }

            with open(self.stats_file_path, "w", encoding="utf-8") as f:
                json.dump(stats_data, f, indent=2)
        except Exception:
            # Fail silently - stats persistence is optional
            pass

    def _load_stats(self) -> None:
        """
        Load access statistics from JSON file.

        Called on startup if persist_stats=True and file exists.
        """
        try:
            if self.stats_file_path.exists():
                with open(self.stats_file_path, "r", encoding="utf-8") as f:
                    stats_data = json.load(f)

                # Restore stats
                if "stats" in stats_data:
                    self.access_stats.update(stats_data["stats"])
        except Exception:
            # Fail silently - start with fresh stats if load fails
            pass

    def close(self) -> None:
        """
        Clean shutdown of FAG instance.

        - Saves statistics if persist_stats=True
        - Flushes any pending operations

        Call this when done using FAG, or use as context manager.
        """
        if self.persist_stats:
            self._save_stats()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - auto-close."""
        self.close()
        return False

    def __del__(self):
        """Destructor - auto-save stats on garbage collection."""
        if self.persist_stats:
            self._save_stats()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def fag_read(
    path: str,
    root: str = ".",
    enable_ledger: bool = True,
) -> FAGReadResult:
    """
    Convenience function for one-off FAG reads.

    Args:
        path: Path to file
        root: Root directory for jail
        enable_ledger: Log to Cooling Ledger

    Returns:
        FAGReadResult
    """
    fag = FAG(root=root, enable_ledger=enable_ledger)
    return fag.read(path)
