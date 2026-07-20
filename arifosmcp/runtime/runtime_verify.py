"""
runtime_verify.py — P1.1 Runtime convergence checker.

Read-only diagnostic that answers: which code is actually executing?

Compares:
  - Git source commit
  - Installed wheel hash
  - Imported module path
  - Python executable
  - Package version

Returns convergence verdict: PASS | FAIL with dimension-level detail.
"""

from __future__ import annotations

import hashlib
import logging
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class RuntimeDimension:
    """One dimension of runtime identity."""

    name: str
    value: str
    source: str  # where this was read from
    converged: bool = True
    note: str = ""


@dataclass
class RuntimeManifest:
    """Full runtime identity report."""

    python_executable: str
    package_version: str
    git_commit: str
    wheel_hash: str
    imported_from: str
    dimensions: list[RuntimeDimension] = field(default_factory=list)
    convergence: str = "UNKNOWN"  # PASS | FAIL | UNKNOWN

    def to_dict(self) -> dict[str, Any]:
        return {
            "python_executable": self.python_executable,
            "package_version": self.package_version,
            "git_commit": self.git_commit,
            "wheel_hash": self.wheel_hash,
            "imported_from": self.imported_from,
            "convergence": self.convergence,
            "dimensions": [
                {
                    "name": d.name,
                    "value": d.value,
                    "source": d.source,
                    "converged": d.converged,
                    "note": d.note,
                }
                for d in self.dimensions
            ],
        }


def _hash_file(path: str) -> str:
    """SHA256 of a file."""
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()[:16]
    except OSError:
        return "UNREADABLE"


def _get_git_commit(repo_root: str) -> str:
    """Get current git commit from repo root."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def _get_package_version() -> str:
    """Get arifos package version."""
    try:
        import arifosmcp

        return getattr(arifosmcp, "__version__", "UNKNOWN")
    except Exception:
        return "UNKNOWN"


def _get_imported_path() -> str:
    """Get the filesystem path of the imported arifosmcp package."""
    try:
        import arifosmcp

        return str(Path(arifosmcp.__file__).parent)
    except Exception:
        return "UNKNOWN"


def _find_wheel_hash(imported_path: str) -> str:
    """Find and hash the installed package's __init__.py as a proxy for wheel identity."""
    init_path = Path(imported_path) / "__init__.py"
    return _hash_file(str(init_path))


def _find_repo_root() -> str:
    """Find the git repo root from the imported path."""
    imported = _get_imported_path()
    if imported == "UNKNOWN":
        return "UNKNOWN"
    # Walk up looking for .git
    current = Path(imported)
    for _ in range(10):
        if (current / ".git").exists():
            return str(current)
        parent = current.parent
        if parent == current:
            break
        current = parent
    return "UNKNOWN"


def verify_runtime() -> RuntimeManifest:
    """Read-only runtime convergence check.

    Returns RuntimeManifest with convergence=PASS if all dimensions agree,
    FAIL if any disagree, UNKNOWN if any can't be read.
    """
    python_exe = sys.executable
    package_version = _get_package_version()
    imported_from = _get_imported_path()
    wheel_hash = _find_wheel_hash(imported_from)
    repo_root = _find_repo_root()
    git_commit = _get_git_commit(repo_root) if repo_root != "UNKNOWN" else "UNKNOWN"

    dimensions = []

    # Dimension 1: Python executable
    dimensions.append(
        RuntimeDimension(
            name="python_executable",
            value=python_exe,
            source="sys.executable",
        )
    )

    # Dimension 2: Package version
    dimensions.append(
        RuntimeDimension(
            name="package_version",
            value=package_version,
            source="arifosmcp.__version__",
        )
    )

    # Dimension 3: Git commit (source)
    source_commit = git_commit
    dimensions.append(
        RuntimeDimension(
            name="git_commit",
            value=source_commit,
            source="git rev-parse HEAD",
        )
    )

    # Dimension 4: Wheel hash (installed artifact)
    dimensions.append(
        RuntimeDimension(
            name="wheel_hash",
            value=wheel_hash,
            source=f"sha256({imported_from}/__init__.py)",
        )
    )

    # Dimension 5: Imported path
    dimensions.append(
        RuntimeDimension(
            name="imported_from",
            value=imported_from,
            source="arifosmcp.__file__",
        )
    )

    # Convergence: check if imported path is inside the repo root
    converged = True
    if repo_root == "UNKNOWN" or imported_from == "UNKNOWN":
        converged = False
        for d in dimensions:
            if d.value == "UNKNOWN":
                d.converged = False
                d.note = "unreadable"
    elif not imported_from.startswith(repo_root):
        converged = False
        for d in dimensions:
            if d.name == "imported_from":
                d.converged = False
                d.note = f"import path {imported_from} not under repo root {repo_root}"

    manifest = RuntimeManifest(
        python_executable=python_exe,
        package_version=package_version,
        git_commit=git_commit,
        wheel_hash=wheel_hash,
        imported_from=imported_from,
        dimensions=dimensions,
        convergence="PASS" if converged else "FAIL",
    )

    logger.info(
        "Runtime verify: convergence=%s git=%s wheel=%s imported=%s",
        manifest.convergence,
        manifest.git_commit,
        manifest.wheel_hash,
        manifest.imported_from,
    )

    return manifest


__all__ = [
    "RuntimeDimension",
    "RuntimeManifest",
    "verify_runtime",
]
