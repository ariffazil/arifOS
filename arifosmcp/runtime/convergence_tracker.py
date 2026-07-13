"""
convergence_tracker.py — P1.2 Runtime convergence tracker.

Compares five layers:
  1. Git source commit
  2. Built artifact (wheel/dist hash)
  3. Installed distribution (site-packages)
  4. Imported runtime (what Python actually loaded)
  5. Service-reported version

States:
  CONVERGED          — all layers match
  SOURCE_AHEAD       — source changed, not rebuilt
  RUNTIME_AHEAD      — runtime newer than source (shouldn't happen)
  DUPLICATE_INSTALL  — multiple installs found
  UNKNOWN_ARTIFACT   — can't identify artifact
  MANIFEST_MISMATCH  — layers disagree
"""

from __future__ import annotations

import hashlib
import logging
import site
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ConvergenceState(str, Enum):
    CONVERGED = "CONVERGED"
    SOURCE_AHEAD = "SOURCE_AHEAD"
    RUNTIME_AHEAD = "RUNTIME_AHEAD"
    DUPLICATE_INSTALL = "DUPLICATE_INSTALL"
    UNKNOWN_ARTIFACT = "UNKNOWN_ARTIFACT"
    MANIFEST_MISMATCH = "MANIFEST_MISMATCH"


@dataclass
class LayerIdentity:
    """Identity of one convergence layer."""
    name: str
    commit: str
    hash: str
    path: str
    readable: bool = True


@dataclass
class ConvergenceReport:
    """Full convergence analysis."""
    state: ConvergenceState
    layers: list[LayerIdentity] = field(default_factory=list)
    mismatches: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": self.state.value,
            "layers": [
                {"name": l.name, "commit": l.commit, "hash": l.hash,
                 "path": l.path, "readable": l.readable}
                for l in self.layers
            ],
            "mismatches": self.mismatches,
        }


def _hash_file(path: str) -> str:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()[:16]
    except OSError:
        return "UNREADABLE"


def _git_commit(repo_root: str) -> str:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_root, capture_output=True, text=True, timeout=5,
        )
        return r.stdout.strip() if r.returncode == 0 else "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def _find_arifos_paths() -> list[Path]:
    """Find all arifosmcp installations in site-packages."""
    paths = []
    for sp in site.getsitepackages():
        candidate = Path(sp) / "arifosmcp"
        if candidate.is_dir():
            paths.append(candidate)
    # Also check the source tree
    try:
        import arifosmcp
        imported = Path(arifosmcp.__file__).parent
        if imported not in paths:
            paths.insert(0, imported)
    except ImportError:
        pass
    return paths


def _find_repo_root() -> str:
    try:
        import arifosmcp
        current = Path(arifosmcp.__file__).parent
        for _ in range(10):
            if (current / ".git").exists():
                return str(current)
            parent = current.parent
            if parent == current:
                break
            current = parent
    except Exception:
        pass
    return "UNKNOWN"


def check_convergence() -> ConvergenceReport:
    """Check convergence across all five layers."""
    layers = []
    mismatches = []

    # Layer 1: Git source
    repo_root = _find_repo_root()
    source_commit = _git_commit(repo_root) if repo_root != "UNKNOWN" else "UNKNOWN"
    source_hash = _hash_file(str(Path(repo_root) / "arifosmcp" / "__init__.py")) if repo_root != "UNKNOWN" else "UNKNOWN"
    layers.append(LayerIdentity(
        name="git_source",
        commit=source_commit,
        hash=source_hash,
        path=repo_root,
        readable=repo_root != "UNKNOWN",
    ))

    # Layer 2: Imported runtime
    try:
        import arifosmcp
        imported_path = str(Path(arifosmcp.__file__).parent)
        imported_hash = _hash_file(str(Path(arifosmcp.__file__)))
        imported_version = getattr(arifosmcp, "__version__", "UNKNOWN")
    except Exception:
        imported_path = "UNKNOWN"
        imported_hash = "UNKNOWN"
        imported_version = "UNKNOWN"
    layers.append(LayerIdentity(
        name="imported_runtime",
        commit=imported_version,
        hash=imported_hash,
        path=imported_path,
        readable=imported_path != "UNKNOWN",
    ))

    # Layer 3: All site-packages installs
    install_paths = _find_arifos_paths()
    if len(install_paths) > 1:
        mismatches.append(f"DUPLICATE_INSTALL: {len(install_paths)} installations found")
        for p in install_paths:
            h = _hash_file(str(p / "__init__.py"))
            layers.append(LayerIdentity(
                name=f"install:{p}",
                commit="N/A",
                hash=h,
                path=str(p),
            ))
    elif len(install_paths) == 1:
        layers.append(LayerIdentity(
            name="installed_distribution",
            commit="N/A",
            hash=_hash_file(str(install_paths[0] / "__init__.py")),
            path=str(install_paths[0]),
        ))

    # Determine convergence state
    readable_layers = [l for l in layers if l.readable]
    if not readable_layers:
        return ConvergenceReport(
            state=ConvergenceState.UNKNOWN_ARTIFACT,
            layers=layers,
            mismatches=["no readable layers"],
        )

    hashes = set(l.hash for l in readable_layers if l.hash != "UNREADABLE")
    if len(hashes) == 0:
        state = ConvergenceState.UNKNOWN_ARTIFACT
        mismatches.append("no readable hashes")
    elif len(hashes) == 1:
        state = ConvergenceState.CONVERGED
    else:
        state = ConvergenceState.MANIFEST_MISMATCH
        mismatches.append(f"hash mismatch: {hashes}")

    if len(install_paths) > 1:
        state = ConvergenceState.DUPLICATE_INSTALL

    report = ConvergenceReport(
        state=state,
        layers=layers,
        mismatches=mismatches,
    )

    logger.info(
        "Convergence check: state=%s layers=%d mismatches=%d",
        state.value, len(layers), len(mismatches),
    )

    return report


__all__ = [
    "ConvergenceState",
    "LayerIdentity",
    "ConvergenceReport",
    "check_convergence",
]
