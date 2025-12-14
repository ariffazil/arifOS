"""
fag.py - File Access Governance (FAG) for arifOS v41

Constitutional filesystem wrapper enforcing 9 floors on file I/O.

Key Features:
- Root-jailed access (F1 Amanah)
- Read-only by default (F5 Peace²)
- Secret pattern blocking (F9 C_dark)
- Symlink resolution and traversal prevention
- Cooling Ledger integration
- MCP-ready interface

Usage:
    from arifos_core.fag import FAG
    
    fag = FAG(root="/project", read_only=True)
    result = fag.read("src/main.py")
    
    if result.verdict == "SEAL":
        print(result.content)
    else:
        print(f"Access denied: {result.reason}")

Constitutional Floors Enforced:
- F1 Amanah: Root jail, reversible, within mandate
- F2 Truth: Only real, readable files
- F4 DeltaS: Reject binary/unreadable content
- F5 Peace²: Read-only, non-destructive
- F7 Omega0: Return verdict + uncertainty, never assume success
- F8 G: Log all access to Cooling Ledger
- F9 C_dark: Block secrets, credentials, forbidden patterns

Version: v41.0.0-alpha
Status: EXPERIMENTAL (requires Phoenix-72 approval for production)
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional, List, Dict, Any

from .APEX_PRIME import ApexVerdict
from .ledger import log_cooling_entry
from .metrics import Metrics


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
    ):
        """
        Initialize FAG with root jail and configuration.
        
        Args:
            root: Root directory for jailed access (F1 Amanah)
            read_only: If True, only read operations allowed (F5 Peace²)
            enable_ledger: If True, log all access to Cooling Ledger (F8 G)
            job_id: Session identifier for ledger entries
        """
        self.root = Path(root).resolve()
        self.read_only = read_only
        self.enable_ledger = enable_ledger
        self.job_id = job_id
        
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
        return self._seal_result(
            path=str(target.relative_to(self.root)),
            content=content,
            size=len(content),
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
        
        if self.enable_ledger:
            self._log_to_ledger(result)
        
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
        metrics = Metrics(
            truth=result.floor_scores.get("F2_truth", 0.99),
            delta_s=result.floor_scores.get("F4_delta_s", 0.0),
            amanah=result.floor_scores.get("F1_amanah", 1.0) >= 1.0,
            peace_squared=result.floor_scores.get("F5_peace_sq", 1.0),
            omega_0=result.floor_scores.get("F7_omega0", 0.04),
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
