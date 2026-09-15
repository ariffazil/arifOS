"""
arifosmcp/canon.py
==================

FHS canon-plane resolver — single owner of `/etc/arifos/canon` resolution.

Repo tree owns semantic creation (what may exist); the canon package owns
ratified authority at deploy time (what is law on this host). This module is
the ONLY code that maps between them:

    dev:     no ARIFOS_CANON_DIR → repo-relative fallback (unchanged behavior)
    prod:    ARIFOS_CANON_DIR=/etc/arifos/canon (systemd drop-in 02-fhs-canon)
             → canon file wins when present; repo file never silently shadows

Canon file set (see deploy-release.sh Step 5.6, the sole canon writer):
    canon-release.json                     — manifest: version, per-file hashes
    sovereignty.charter.json               — sovereignty charter
    charter/kernel.charter.yaml            — kernel charter
    memory-admissibility-policy.yaml       — SRO v1 read-gate policy

Generated projections (tools_sot.yaml, capability_registry.json) are NOT canon
files — their source of truth is code (constitutional_map.py, arifosmcp/abi/).
The deploy manifest records their hashes for attestation only.

DITEMPA BUKAN DIBERI Ⓒ 2026-09-16 FHS formalization.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

CANON_DIR_ENV = "ARIFOS_CANON_DIR"
CANON_MANIFEST_NAME = "canon-release.json"


def canon_dir() -> Path | None:
    """Active canon directory, or None in dev (no /etc deployment)."""
    env = os.environ.get(CANON_DIR_ENV, "").strip()
    if not env:
        return None
    p = Path(env)
    return p if p.is_dir() else None


def canon_aware_path(canon_name: str, repo_fallback: Path) -> Path:
    """Resolve a canon-grade file: /etc canon wins when present.

    Explicit env overrides of the *consumer* (e.g. MEMORY_ADMISSIBILITY_POLICY)
    keep their existing higher precedence — call this only for the default
    leg of that resolution chain.
    """
    cdir = canon_dir()
    if cdir is not None:
        candidate = cdir / canon_name
        if candidate.is_file():
            return candidate
    return repo_fallback


def canon_manifest() -> dict[str, Any] | None:
    """Load canon-release.json from the active canon dir, or None."""
    cdir = canon_dir()
    if cdir is None:
        return None
    manifest_path = cdir / CANON_MANIFEST_NAME
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _manifest_hash(manifest: dict[str, Any]) -> str:
    raw = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(raw.encode()).hexdigest()


def canon_attestation() -> dict[str, Any]:
    """Compact canon state for /health — report-only, never flips drift.

    A canon mismatch is surfaced, not weaponized: flipping `drift` on /etc
    lag would wedge the kernel during canon-only ratifications. Escalation
    to enforcement is a separate F13 decision.
    """
    cdir = canon_dir()
    if cdir is None:
        return {"source": "repo-fallback", "active": False}
    manifest = canon_manifest()
    if manifest is None:
        return {
            "source": str(cdir),
            "active": True,
            "manifest": "MISSING_OR_UNPARSEABLE",
        }
    files = manifest.get("files")
    file_count = len(files) if isinstance(files, list) else 0
    verified = 0
    if isinstance(files, list):
        for entry in files:
            if not isinstance(entry, dict):
                continue
            name = entry.get("name")
            digest = str(entry.get("sha256", "")).removeprefix("sha256:")
            fp = cdir / str(name)
            if name and digest and fp.is_file():
                try:
                    if hashlib.sha256(fp.read_bytes()).hexdigest() == digest:
                        verified += 1
                except OSError:
                    pass
    return {
        "source": str(cdir),
        "active": True,
        "version": manifest.get("canon_version", "unknown"),
        "ratified_by": manifest.get("ratified_by", "unknown"),
        "manifest_hash": _manifest_hash(manifest),
        "files": file_count,
        "files_verified": verified,
        "integrity": "ok" if verified == file_count and file_count > 0 else "MISMATCH",
    }
