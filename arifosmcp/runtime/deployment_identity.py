"""
canonical_identity — ONE source for deployment identity (P1-5, repair-2026-11-01).

The D1 audit saw six identity surfaces that never agree (registry 1!2026.10.11,
server.json 1!2026.10.17, serverInfo kanon-<wallclock>+024ff90, canon.version
2026.10.30-024ff90, deployed 024ff90 vs repo HEAD, PyPI healthy/13-13/8 tools)
and drift=false only because drift_scope=binary_build_stamps.

This module resolves identity ONCE and every surface renders from it:
  - deployed stamp   — the same stamp chain deploy scripts write
                       (ARIFOS_IDENTITY_STAMP overrides for tests)
  - canonical repo    — the SOURCE checkout (/root/arifOS), read via
                       ARIFOS_IDENTITY_REPO_ROOT (tests inject fixtures);
                       independent of where arifosmcp was imported from
                       (fixes: live kernel in site-packages got repo=null)
  - build date        — STABLE stamp mtime (the old generator used
                        datetime.now(), so serverInfo's version mutated daily)
  - gap + reachability — rev-list counts both ways + branch-reachability of the
                        stamp (measured 2026-11-01: stamp 024ff9005 is an ORPHAN
                        of a pre-rewrite history line; main equivalent is
                        2ba6627eb, identical author/time/subject; divergence
                        from merge-base 63cf8e46c (2026-04-23) = 4666/4660)
  - drift            — widened: identity_drift = (repo vs deployed out of sync)
                        OR (deployed stamp unreachable from any branch).

Fail-soft by contract: any probe failure yields None/UNKNOWN and never raises —
identity must never wedge the kernel.
DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import datetime as _dt
import logging
import os
import subprocess  # nosec B404 — bounded git probes, fixed arg list
from pathlib import Path
from typing import Any

logger = logging.getLogger("arifosmcp.runtime.deployment_identity")

DEFAULT_REPO_ROOT = "/root/arifOS"
DEFAULT_STAMP_CHAIN = (
    "/opt/arifos/releases/deployed-commit",
    "/opt/arifos/app/.git_commit",
    "/root/arifOS/.git_commit",
)

_CACHE: dict[str, Any] | None = None


def _env_path(name: str, default: str) -> str:
    return os.getenv(name, "").strip() or default


def _read_stamp(stamp_path: str | None) -> tuple[str | None, str | None]:
    """Return (full_commit, path_used) from the deploy stamp chain."""
    if stamp_path:
        chain = (stamp_path,)
    else:
        env_override = os.getenv("ARIFOS_IDENTITY_STAMP", "").strip()
        chain = (env_override,) if env_override else DEFAULT_STAMP_CHAIN
    for path in chain:
        try:
            if path and os.path.exists(path):
                content = Path(path).read_text().strip()
                if len(content) >= 7:
                    return content, path
        except OSError:
            logger.warning("stamp unreadable: %s", path, exc_info=True)
    return None, None


def _git(repo: str, *args: str, timeout: int = 8) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "-C", repo, *args],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if proc.returncode == 0:
            return proc.stdout.strip()
        return None
    except Exception:  # noqa: BLE001 — identity must never raise
        return None


def canonical_identity(
    *,
    repo_root: str | None = None,
    stamp_path: str | None = None,
    use_cache: bool = True,
) -> dict[str, Any]:
    """Return the canonical deployment identity (single source for all surfaces)."""
    global _CACHE
    if use_cache and _CACHE is not None and repo_root is None and stamp_path is None:
        return dict(_CACHE)

    repo = repo_root or _env_path("ARIFOS_IDENTITY_REPO_ROOT", DEFAULT_REPO_ROOT)

    deployed_full, stamp_used = _read_stamp(stamp_path)
    deployed = (deployed_full or "")[:7] or "unknown"

    # Stable build date — stamp mtime, never the wall clock.
    build_date = "unknown"
    if stamp_used:
        try:
            mtime = Path(stamp_used).stat().st_mtime
            build_date = _dt.datetime.fromtimestamp(mtime, _dt.UTC).strftime("%Y-%m-%d")
        except OSError:
            build_date = "unknown"

    version = (
        f"kanon-{build_date.replace('-', '.')}+{deployed}"
        if build_date != "unknown" and deployed != "unknown"
        else "kanon-unknown"
    )

    # Canonical SOURCE repo HEAD (independent of the import location).
    repo_head_full = None
    if repo and Path(repo).exists():
        head = _git(repo, "rev-parse", "HEAD")
        if head and len(head) >= 7:
            repo_head_full = head
    repo_head = (repo_head_full or "")[:7] or None

    # Gap counts (both directions) — the honest size of HEAD-vs-deployed.
    gap: dict[str, Any] = {
        "repo_ahead_of_deployed": None,
        "deployed_ahead_of_repo": None,
    }
    if deployed != "unknown" and repo and Path(repo).exists():
        ahead = _git(repo, "rev-list", "--count", f"{deployed}..HEAD")
        behind = _git(repo, "rev-list", "--count", f"HEAD..{deployed}")
        try:
            gap["repo_ahead_of_deployed"] = int(ahead) if ahead is not None else None
        except ValueError:
            gap["repo_ahead_of_deployed"] = None
        try:
            gap["deployed_ahead_of_repo"] = int(behind) if behind is not None else None
        except ValueError:
            gap["deployed_ahead_of_repo"] = None

    # Reachability: is the stamp commit on ANY branch (local or remote)?
    deployed_reachable: bool | None = None
    if deployed != "unknown" and repo and Path(repo).exists():
        contains = _git(repo, "branch", "-a", "--contains", deployed, timeout=12)
        if contains is not None:
            deployed_reachable = any(
                line.strip() for line in contains.splitlines() if line.strip()
            )

    in_sync: bool | None = None
    if deployed != "unknown" and repo_head:
        in_sync = deployed == repo_head

    reasons: list[str] = []
    if in_sync is False:
        reasons.append("repo_head_vs_deployed: source checkout is not at the deployed stamp")
    if deployed_reachable is False:
        reasons.append(
            "stamp_reachability: deployed commit is unreachable from any branch "
            "(pre-rewrite history line — same author/time/subject exists on main)"
        )
    identity_drift = bool(reasons)

    identity: dict[str, Any] = {
        "deployed_commit": deployed_full,
        "deployed_commit_short": deployed,
        "stamp_path": stamp_used,
        "stamp_mtime_utc_date": build_date,
        "build_date": build_date,
        "version": version,
        "repo_root": repo if repo and Path(repo).exists() else None,
        "repo_head_commit": repo_head,
        "repo_head_commit_full": repo_head_full,
        "repo_gap": gap,
        "deployed_reachable": deployed_reachable,
        "source": "arifosmcp.runtime.deployment_identity.canonical_identity",
        "drift": {
            "scope": "binary_build_stamps+repo_head_vs_deployed+stamp_reachability",
            "in_sync": in_sync,
            "identity_drift": identity_drift,
            "reasons": reasons,
        },
    }

    if use_cache and repo_root is None and stamp_path is None:
        _CACHE = dict(identity)
    return identity


def refresh() -> dict[str, Any]:
    """Drop the process-lifetime cache and recompute (deploy/rebase probes)."""
    global _CACHE
    _CACHE = None
    return canonical_identity()
