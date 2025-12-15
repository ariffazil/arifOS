"""
well_file_care.py - @WELL File Care Module (Universal Migration Tool)

@WELL extends its care domain to file system operations.
Domain: File relocation, structure healing, governed migrations

Version: v42.0.0
Status: PRODUCTION
Alignment: arifOS v42 Architecture Blueprint

Core responsibilities:
- F1 Amanah enforcement for file operations (reversibility, audit trail)
- Structure integrity validation
- Protected file safety (.git, LICENSE, etc.)
- Cross-platform migration support (Claude, Copilot, ChatGPT, Gemini)

This module extends @WELL's care domain:
@WELL (File Care) -> governed file operations with F1 Amanah compliance

DITEMPA BUKAN DIBERI - Forged, not given
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# -----------------------------------------------------------------------------
# Constants (v42 Architecture Aligned)
# -----------------------------------------------------------------------------


class WellConstants:
    """Configuration constants for @WELL File Care."""

    # Version tracking
    VERSION = "42.0.0"
    CODENAME = "WELL_FILE_CARE"

    # Protected files that should NEVER be moved/deleted
    PROTECTED_FILES = frozenset([
        ".git",
        ".gitignore",
        ".gitattributes",
        "LICENSE",
        "LICENSE.md",
        "README.md",
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        ".env",
        ".env.local",
        "CHANGELOG.md",
        "CLAUDE.md",
        "AGENTS.md",
    ])

    # Protected directories (never delete, careful with moves)
    PROTECTED_DIRS = frozenset([
        ".git",
        ".github",
        ".vscode",
        ".claude",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
        "vault_999",
        "cooling_ledger",
    ])

    # Valid layer prefixes (v42 architecture)
    VALID_LAYERS = frozenset([
        "L1_THEORY",
        "L2_GOVERNANCE",
        "L3_KERNEL",
        "L4_MCP",
        "L5_CLI",
        "L6_SEALION",
        "L7_DEMOS",
    ])

    # Audit log file
    AUDIT_LOG = "well_audit_trail.jsonl"
    SNAPSHOT_DIR = ".well_snapshots"

    # Max operations before requiring confirmation
    MAX_BATCH_SIZE = 10


# -----------------------------------------------------------------------------
# Enums
# -----------------------------------------------------------------------------


class WellOperationType(Enum):
    """Types of file care operations."""
    RELOCATE = "relocate"
    DUPLICATE = "duplicate"
    RETIRE = "retire"
    HEAL = "heal"
    VERIFY = "verify"
    UNDO = "undo"


class WellOperationStatus(Enum):
    """Status of a file care operation."""
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"  # Protected file
    SKIPPED = "skipped"  # Already exists


# -----------------------------------------------------------------------------
# Data Classes
# -----------------------------------------------------------------------------


@dataclass
class WellAuditEntry:
    """Single audit trail entry for file operations."""

    operation_id: str
    operation_type: WellOperationType
    source_path: str
    target_path: Optional[str]
    checksum_before: str
    checksum_after: Optional[str]
    status: WellOperationStatus
    timestamp: str
    reversible: bool
    backup_path: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for JSONL logging."""
        return {
            "operation_id": self.operation_id,
            "operation_type": self.operation_type.value,
            "source_path": self.source_path,
            "target_path": self.target_path,
            "checksum_before": self.checksum_before,
            "checksum_after": self.checksum_after,
            "status": self.status.value,
            "timestamp": self.timestamp,
            "reversible": self.reversible,
            "backup_path": self.backup_path,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


@dataclass
class WellHealthReport:
    """Health check result for repository structure."""

    is_healthy: bool
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    file_count: int = 0
    directory_count: int = 0
    layer_status: Dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for API response."""
        return {
            "is_healthy": self.is_healthy,
            "issues": self.issues,
            "warnings": self.warnings,
            "suggestions": self.suggestions,
            "file_count": self.file_count,
            "directory_count": self.directory_count,
            "layer_status": self.layer_status,
        }


@dataclass
class WellOperationResult:
    """Result of a single file operation."""

    success: bool
    operation_type: WellOperationType
    source_path: str
    target_path: Optional[str] = None
    message: str = ""
    audit_entry: Optional[WellAuditEntry] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for API response."""
        return {
            "success": self.success,
            "operation_type": self.operation_type.value,
            "source_path": self.source_path,
            "target_path": self.target_path,
            "message": self.message,
            "audit_entry": self.audit_entry.to_dict() if self.audit_entry else None,
        }


# -----------------------------------------------------------------------------
# Core @WELL File Care Class
# -----------------------------------------------------------------------------


class WellFileCare:
    """
    @WELL File Care - Universal Migration Tool

    Provides governed file operations with:
    - F1 Amanah compliance (audit trail, reversibility)
    - Protected file safety
    - Checksum verification
    - Cross-platform support

    Usage:
        well = WellFileCare(repo_root="/path/to/arifOS")
        result = well.relocate("old/path.py", "new/path.py")
        if not result.success:
            well.undo_last()
    """

    def __init__(
        self,
        repo_root: Optional[str] = None,
        audit_log_path: Optional[str] = None,
    ):
        """
        Initialize @WELL File Care.

        Args:
            repo_root: Root directory of the repository
            audit_log_path: Path to audit log (default: {repo_root}/well_audit_trail.jsonl)
        """
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
        self.audit_log_path = Path(audit_log_path) if audit_log_path else (
            self.repo_root / WellConstants.AUDIT_LOG
        )
        self.snapshot_dir = self.repo_root / WellConstants.SNAPSHOT_DIR
        self._operation_history: List[WellAuditEntry] = []

    # -------------------------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------------------------

    @staticmethod
    def compute_checksum(file_path: Path) -> str:
        """Compute SHA-256 checksum of a file."""
        if not file_path.exists() or file_path.is_dir():
            return "DIRECTORY" if file_path.is_dir() else "NOT_FOUND"

        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except (OSError, IOError) as e:
            return f"ERROR:{e}"

    @staticmethod
    def generate_operation_id() -> str:
        """Generate unique operation ID."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        return f"WELL_{timestamp}"

    @staticmethod
    def get_timestamp() -> str:
        """Get ISO format timestamp."""
        return datetime.now(timezone.utc).isoformat()

    def is_protected(self, path: Path) -> Tuple[bool, str]:
        """
        Check if a path is protected.

        Returns:
            Tuple of (is_protected, reason)
        """
        name = path.name

        # Check protected files
        if name in WellConstants.PROTECTED_FILES:
            return True, f"Protected file: {name}"

        # Check protected directories
        for part in path.parts:
            if part in WellConstants.PROTECTED_DIRS:
                return True, f"Protected directory: {part}"

        return False, ""

    def resolve_path(self, path: str) -> Path:
        """Resolve a path relative to repo root."""
        p = Path(path)
        if p.is_absolute():
            return p
        return self.repo_root / p

    # -------------------------------------------------------------------------
    # Audit Trail Methods
    # -------------------------------------------------------------------------

    def _log_audit(self, entry: WellAuditEntry) -> None:
        """Write audit entry to JSONL log."""
        self._operation_history.append(entry)

        try:
            with open(self.audit_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry.to_dict()) + "\n")
        except (OSError, IOError) as e:
            # Log failure but don't block operation
            print(f"[WELL] Warning: Failed to write audit log: {e}")

    def get_audit_history(self, limit: int = 100) -> List[WellAuditEntry]:
        """Get recent audit history."""
        return self._operation_history[-limit:]

    def load_audit_history(self) -> List[WellAuditEntry]:
        """Load audit history from JSONL file."""
        history = []
        if not self.audit_log_path.exists():
            return history

        try:
            with open(self.audit_log_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        entry = WellAuditEntry(
                            operation_id=data["operation_id"],
                            operation_type=WellOperationType(data["operation_type"]),
                            source_path=data["source_path"],
                            target_path=data.get("target_path"),
                            checksum_before=data["checksum_before"],
                            checksum_after=data.get("checksum_after"),
                            status=WellOperationStatus(data["status"]),
                            timestamp=data["timestamp"],
                            reversible=data["reversible"],
                            backup_path=data.get("backup_path"),
                            error_message=data.get("error_message"),
                            metadata=data.get("metadata", {}),
                        )
                        history.append(entry)
        except (OSError, IOError, json.JSONDecodeError) as e:
            print(f"[WELL] Warning: Failed to load audit history: {e}")

        self._operation_history = history
        return history

    # -------------------------------------------------------------------------
    # Health Check Methods
    # -------------------------------------------------------------------------

    def check_health(self) -> WellHealthReport:
        """
        Check repository structure health.

        Returns:
            WellHealthReport with issues, warnings, and suggestions
        """
        report = WellHealthReport(is_healthy=True)

        # Check if repo root exists
        if not self.repo_root.exists():
            report.is_healthy = False
            report.issues.append(f"Repository root not found: {self.repo_root}")
            return report

        # Check v42 layer directories
        for layer in WellConstants.VALID_LAYERS:
            layer_path = self.repo_root / layer
            report.layer_status[layer] = layer_path.exists()
            if not layer_path.exists():
                report.warnings.append(f"Layer directory missing: {layer}")

        # Count files and directories
        for item in self.repo_root.rglob("*"):
            if item.is_file():
                report.file_count += 1
            elif item.is_dir():
                report.directory_count += 1

        # Check for common issues
        # 1. Files in root that should be in layers
        root_py_files = list(self.repo_root.glob("*.py"))
        if root_py_files:
            for f in root_py_files:
                if f.name not in ("setup.py", "conftest.py"):
                    report.warnings.append(f"Python file in root: {f.name}")

        # 2. Check arifos_core structure (if exists)
        arifos_core = self.repo_root / "arifos_core"
        if arifos_core.exists():
            # Count top-level files (should be minimal after reorganization)
            top_level_files = [
                f for f in arifos_core.glob("*.py")
                if f.name != "__init__.py"
            ]
            if len(top_level_files) > 10:
                report.warnings.append(
                    f"arifos_core has {len(top_level_files)} top-level files "
                    "(consider reorganization)"
                )
                report.suggestions.append(
                    "Run Phase 2 reorganization to move files to concern-based subdirs"
                )

        # 3. Check for backup/temp files
        backup_patterns = ["*.bak", "*.tmp", "*.swp", "*~"]
        for pattern in backup_patterns:
            backup_files = list(self.repo_root.rglob(pattern))
            if backup_files:
                report.warnings.append(
                    f"Found {len(backup_files)} {pattern} files"
                )

        # Set health status
        if report.issues:
            report.is_healthy = False
        elif len(report.warnings) > 5:
            report.is_healthy = False

        return report

    def list_files(
        self,
        path: str = ".",
        pattern: str = "*",
        recursive: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        List files in a directory.

        Args:
            path: Directory path (relative to repo root)
            pattern: Glob pattern to filter files
            recursive: Whether to recurse into subdirectories

        Returns:
            List of file info dictionaries
        """
        target = self.resolve_path(path)
        if not target.exists():
            return []

        files = []
        glob_func = target.rglob if recursive else target.glob

        for item in glob_func(pattern):
            info = {
                "path": str(item.relative_to(self.repo_root)),
                "name": item.name,
                "is_dir": item.is_dir(),
                "size": item.stat().st_size if item.is_file() else 0,
                "modified": datetime.fromtimestamp(
                    item.stat().st_mtime
                ).isoformat(),
            }
            if item.is_file():
                info["checksum"] = self.compute_checksum(item)[:16] + "..."

            is_protected, reason = self.is_protected(item)
            info["protected"] = is_protected
            if is_protected:
                info["protection_reason"] = reason

            files.append(info)

        return sorted(files, key=lambda x: (not x["is_dir"], x["path"]))

    # -------------------------------------------------------------------------
    # Core File Operations (F1 Amanah Compliant)
    # -------------------------------------------------------------------------

    def relocate(
        self,
        source: str,
        target: str,
        create_backup: bool = True,
    ) -> WellOperationResult:
        """
        Relocate (move) a file with full audit trail.

        Args:
            source: Source file path
            target: Target file path
            create_backup: Whether to create a backup (default: True)

        Returns:
            WellOperationResult
        """
        source_path = self.resolve_path(source)
        target_path = self.resolve_path(target)

        # Check if source exists
        if not source_path.exists():
            return WellOperationResult(
                success=False,
                operation_type=WellOperationType.RELOCATE,
                source_path=source,
                message=f"Source not found: {source}",
            )

        # Check protection
        is_protected, reason = self.is_protected(source_path)
        if is_protected:
            audit_entry = WellAuditEntry(
                operation_id=self.generate_operation_id(),
                operation_type=WellOperationType.RELOCATE,
                source_path=source,
                target_path=target,
                checksum_before=self.compute_checksum(source_path),
                checksum_after=None,
                status=WellOperationStatus.BLOCKED,
                timestamp=self.get_timestamp(),
                reversible=False,
                error_message=reason,
            )
            self._log_audit(audit_entry)
            return WellOperationResult(
                success=False,
                operation_type=WellOperationType.RELOCATE,
                source_path=source,
                target_path=target,
                message=f"BLOCKED: {reason}",
                audit_entry=audit_entry,
            )

        # Check if target already exists
        if target_path.exists():
            return WellOperationResult(
                success=False,
                operation_type=WellOperationType.RELOCATE,
                source_path=source,
                target_path=target,
                message=f"Target already exists: {target}",
            )

        # Compute checksum before
        checksum_before = self.compute_checksum(source_path)

        # Create backup if requested
        backup_path = None
        if create_backup:
            self.snapshot_dir.mkdir(parents=True, exist_ok=True)
            backup_name = f"{source_path.name}.{self.generate_operation_id()}"
            backup_path = self.snapshot_dir / backup_name
            try:
                if source_path.is_dir():
                    shutil.copytree(source_path, backup_path)
                else:
                    shutil.copy2(source_path, backup_path)
            except (OSError, IOError) as e:
                return WellOperationResult(
                    success=False,
                    operation_type=WellOperationType.RELOCATE,
                    source_path=source,
                    message=f"Failed to create backup: {e}",
                )

        # Create target directory if needed
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Perform move
        try:
            shutil.move(str(source_path), str(target_path))
        except (OSError, IOError, shutil.Error) as e:
            # Restore from backup if move failed
            if backup_path and backup_path.exists():
                if source_path.is_dir():
                    shutil.copytree(backup_path, source_path)
                else:
                    shutil.copy2(backup_path, source_path)
            return WellOperationResult(
                success=False,
                operation_type=WellOperationType.RELOCATE,
                source_path=source,
                target_path=target,
                message=f"Move failed: {e}",
            )

        # Compute checksum after
        checksum_after = self.compute_checksum(target_path)

        # Verify integrity
        if checksum_before != checksum_after and checksum_before != "DIRECTORY":
            # Integrity failure - restore
            if backup_path and backup_path.exists():
                shutil.move(str(target_path), str(source_path))
            return WellOperationResult(
                success=False,
                operation_type=WellOperationType.RELOCATE,
                source_path=source,
                target_path=target,
                message="Integrity check failed: checksum mismatch",
            )

        # Log audit entry
        audit_entry = WellAuditEntry(
            operation_id=self.generate_operation_id(),
            operation_type=WellOperationType.RELOCATE,
            source_path=source,
            target_path=target,
            checksum_before=checksum_before,
            checksum_after=checksum_after,
            status=WellOperationStatus.SUCCESS,
            timestamp=self.get_timestamp(),
            reversible=True,
            backup_path=str(backup_path) if backup_path else None,
        )
        self._log_audit(audit_entry)

        return WellOperationResult(
            success=True,
            operation_type=WellOperationType.RELOCATE,
            source_path=source,
            target_path=target,
            message=f"Relocated: {source} -> {target}",
            audit_entry=audit_entry,
        )

    def duplicate(
        self,
        source: str,
        target: str,
    ) -> WellOperationResult:
        """
        Duplicate (copy) a file with audit trail.

        Args:
            source: Source file path
            target: Target file path

        Returns:
            WellOperationResult
        """
        source_path = self.resolve_path(source)
        target_path = self.resolve_path(target)

        # Check if source exists
        if not source_path.exists():
            return WellOperationResult(
                success=False,
                operation_type=WellOperationType.DUPLICATE,
                source_path=source,
                message=f"Source not found: {source}",
            )

        # Check if target already exists
        if target_path.exists():
            return WellOperationResult(
                success=False,
                operation_type=WellOperationType.DUPLICATE,
                source_path=source,
                target_path=target,
                message=f"Target already exists: {target}",
            )

        # Compute checksum before
        checksum_before = self.compute_checksum(source_path)

        # Create target directory if needed
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Perform copy
        try:
            if source_path.is_dir():
                shutil.copytree(source_path, target_path)
            else:
                shutil.copy2(source_path, target_path)
        except (OSError, IOError, shutil.Error) as e:
            return WellOperationResult(
                success=False,
                operation_type=WellOperationType.DUPLICATE,
                source_path=source,
                target_path=target,
                message=f"Copy failed: {e}",
            )

        # Compute checksum after
        checksum_after = self.compute_checksum(target_path)

        # Verify integrity
        if checksum_before != checksum_after and checksum_before != "DIRECTORY":
            # Integrity failure - remove target
            if target_path.is_dir():
                shutil.rmtree(target_path)
            else:
                target_path.unlink()
            return WellOperationResult(
                success=False,
                operation_type=WellOperationType.DUPLICATE,
                source_path=source,
                target_path=target,
                message="Integrity check failed: checksum mismatch",
            )

        # Log audit entry
        audit_entry = WellAuditEntry(
            operation_id=self.generate_operation_id(),
            operation_type=WellOperationType.DUPLICATE,
            source_path=source,
            target_path=target,
            checksum_before=checksum_before,
            checksum_after=checksum_after,
            status=WellOperationStatus.SUCCESS,
            timestamp=self.get_timestamp(),
            reversible=True,  # Can delete the duplicate
        )
        self._log_audit(audit_entry)

        return WellOperationResult(
            success=True,
            operation_type=WellOperationType.DUPLICATE,
            source_path=source,
            target_path=target,
            message=f"Duplicated: {source} -> {target}",
            audit_entry=audit_entry,
        )

    def retire(
        self,
        path: str,
        archive_dir: str = "archive",
    ) -> WellOperationResult:
        """
        Retire (archive) a file instead of deleting it.

        Args:
            path: File path to retire
            archive_dir: Archive directory (default: "archive")

        Returns:
            WellOperationResult
        """
        source_path = self.resolve_path(path)

        # Check if source exists
        if not source_path.exists():
            return WellOperationResult(
                success=False,
                operation_type=WellOperationType.RETIRE,
                source_path=path,
                message=f"Source not found: {path}",
            )

        # Check protection
        is_protected, reason = self.is_protected(source_path)
        if is_protected:
            return WellOperationResult(
                success=False,
                operation_type=WellOperationType.RETIRE,
                source_path=path,
                message=f"BLOCKED: {reason}",
            )

        # Create archive path with timestamp
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        archive_path = self.repo_root / archive_dir / f"{source_path.name}_{timestamp}"

        # Use relocate for the actual move
        return self.relocate(path, str(archive_path.relative_to(self.repo_root)))

    def undo_last(self) -> WellOperationResult:
        """
        Undo the last reversible operation.

        Returns:
            WellOperationResult
        """
        # Find last reversible operation
        if not self._operation_history:
            self.load_audit_history()

        reversible_ops = [
            e for e in self._operation_history
            if e.reversible and e.status == WellOperationStatus.SUCCESS
        ]

        if not reversible_ops:
            return WellOperationResult(
                success=False,
                operation_type=WellOperationType.UNDO,
                source_path="",
                message="No reversible operations found",
            )

        last_op = reversible_ops[-1]

        # Perform undo based on operation type
        if last_op.operation_type == WellOperationType.RELOCATE:
            # Move back from target to source
            if last_op.target_path:
                result = self.relocate(
                    last_op.target_path,
                    last_op.source_path,
                    create_backup=False,
                )
                if result.success:
                    result.message = f"Undone: {last_op.target_path} -> {last_op.source_path}"
                return result

        elif last_op.operation_type == WellOperationType.DUPLICATE:
            # Delete the duplicate
            target_path = self.resolve_path(last_op.target_path) if last_op.target_path else None
            if target_path and target_path.exists():
                try:
                    if target_path.is_dir():
                        shutil.rmtree(target_path)
                    else:
                        target_path.unlink()
                    return WellOperationResult(
                        success=True,
                        operation_type=WellOperationType.UNDO,
                        source_path=last_op.target_path or "",
                        message=f"Undone duplicate: deleted {last_op.target_path}",
                    )
                except (OSError, IOError) as e:
                    return WellOperationResult(
                        success=False,
                        operation_type=WellOperationType.UNDO,
                        source_path=last_op.target_path or "",
                        message=f"Failed to undo: {e}",
                    )

        return WellOperationResult(
            success=False,
            operation_type=WellOperationType.UNDO,
            source_path=last_op.source_path,
            message=f"Cannot undo operation type: {last_op.operation_type.value}",
        )

    # -------------------------------------------------------------------------
    # Batch Operations (888_HOLD for large batches)
    # -------------------------------------------------------------------------

    def batch_relocate(
        self,
        operations: List[Dict[str, str]],
        dry_run: bool = False,
    ) -> List[WellOperationResult]:
        """
        Batch relocate files.

        Args:
            operations: List of {"source": "...", "target": "..."} dicts
            dry_run: If True, validate but don't execute

        Returns:
            List of WellOperationResult
        """
        results = []

        # Check batch size (888_HOLD trigger)
        if len(operations) > WellConstants.MAX_BATCH_SIZE:
            results.append(WellOperationResult(
                success=False,
                operation_type=WellOperationType.RELOCATE,
                source_path="BATCH",
                message=f"888_HOLD: Batch size {len(operations)} exceeds limit "
                        f"{WellConstants.MAX_BATCH_SIZE}. Requires explicit confirmation.",
            ))
            return results

        for op in operations:
            source = op.get("source", "")
            target = op.get("target", "")

            if dry_run:
                source_path = self.resolve_path(source)
                is_protected, reason = self.is_protected(source_path)
                results.append(WellOperationResult(
                    success=not is_protected and source_path.exists(),
                    operation_type=WellOperationType.RELOCATE,
                    source_path=source,
                    target_path=target,
                    message=f"DRY_RUN: {'BLOCKED: ' + reason if is_protected else 'OK'}",
                ))
            else:
                results.append(self.relocate(source, target))

        return results

    # -------------------------------------------------------------------------
    # Structure Healing
    # -------------------------------------------------------------------------

    def heal_structure(
        self,
        create_missing_layers: bool = True,
    ) -> WellHealthReport:
        """
        Heal repository structure by creating missing directories.

        Args:
            create_missing_layers: Whether to create missing L1-L7 directories

        Returns:
            WellHealthReport with actions taken
        """
        report = self.check_health()

        if create_missing_layers:
            for layer in WellConstants.VALID_LAYERS:
                if not report.layer_status.get(layer, False):
                    layer_path = self.repo_root / layer
                    layer_path.mkdir(parents=True, exist_ok=True)
                    report.suggestions.append(f"Created layer directory: {layer}")
                    report.layer_status[layer] = True

        # Re-check health
        report.is_healthy = all(report.layer_status.values()) and not report.issues
        return report

    # -------------------------------------------------------------------------
    # Snapshot Management
    # -------------------------------------------------------------------------

    def save_snapshot(self, name: str = "") -> str:
        """
        Save a full snapshot of the repository structure (metadata only).

        Args:
            name: Optional snapshot name

        Returns:
            Snapshot filename
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        snapshot_name = f"snapshot_{name}_{timestamp}.json" if name else f"snapshot_{timestamp}.json"

        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        snapshot_path = self.snapshot_dir / snapshot_name

        # Collect file metadata
        files = []
        for item in self.repo_root.rglob("*"):
            if ".well_snapshots" in str(item):
                continue
            if item.is_file():
                files.append({
                    "path": str(item.relative_to(self.repo_root)),
                    "checksum": self.compute_checksum(item),
                    "size": item.stat().st_size,
                    "modified": item.stat().st_mtime,
                })

        snapshot = {
            "name": name,
            "timestamp": self.get_timestamp(),
            "repo_root": str(self.repo_root),
            "file_count": len(files),
            "files": files,
        }

        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2)

        return snapshot_name


# -----------------------------------------------------------------------------
# Convenience Functions (Pipeline Integration)
# -----------------------------------------------------------------------------


def create_well_file_care(repo_root: Optional[str] = None) -> WellFileCare:
    """
    Factory function to create WellFileCare instance.

    Usage:
        from arifos_core.waw.well_file_care import create_well_file_care
        well = create_well_file_care()
        result = well.check_health()
    """
    return WellFileCare(repo_root=repo_root)


__all__ = [
    # Constants
    "WellConstants",
    # Enums
    "WellOperationType",
    "WellOperationStatus",
    # Data Classes
    "WellAuditEntry",
    "WellHealthReport",
    "WellOperationResult",
    # Main Class
    "WellFileCare",
    # Factory
    "create_well_file_care",
]
