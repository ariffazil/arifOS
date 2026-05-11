"""Vault Audit — arifOS Command Center v0.3.

Canonical read path for VAULT999 ledger.
Reads from /root/VAULT999/outcomes.jsonl, returns entries newest-first.

Supports:
  - Full ledger scan (last N entries)
  - Chain integrity verification
  - Entry filtering by type, actor, app

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from arifosmcp.apps.command_center.vault_chain import (
    _VAULT_PATH,
    read_vault_entries,
    verify_chain,
)


def get_vault_audit(
    limit: int = 20,
    entry_type: str | None = None,
    actor_id: str | None = None,
    app: str | None = None,
    include_payload: bool = False,
) -> dict[str, Any]:
    """Return the last N vault entries with optional filters.

    Args:
        limit: Maximum entries to return (default 20).
        entry_type: Filter by entry type (e.g. "judge_verdict", "forge_execution").
        actor_id: Filter by actor ID.
        app: Filter by source app.
        include_payload: If True, include full payload dict (default False).

    Returns:
        {
            "entries": list[dict],
            "total": int,
            "filtered": bool,
            "chain_valid": bool,
            "entries_checked": int,
            "breaks": list[str],
        }
    """
    all_entries = read_vault_entries(limit=500)  # read extra to allow filtering
    filtered = all_entries

    if entry_type:
        filtered = [e for e in filtered if e.get("type") == entry_type]
    if actor_id:
        filtered = [e for e in filtered if e.get("actor_id") == actor_id]
    if app:
        filtered = [e for e in filtered if e.get("app") == app]

    # Trim to limit
    entries = filtered[-limit:]

    # Strip payload unless explicitly requested
    if not include_payload:
        entries = [{k: v for k, v in e.items() if k != "payload"} for e in entries]

    # Chain verification
    chain_report = verify_chain()

    return {
        "entries": entries,
        "total": len(all_entries),
        "filtered": bool(entry_type or actor_id or app),
        "chain_valid": chain_report["valid"],
        "entries_checked": chain_report["entries_checked"],
        "chain_breaks": chain_report["breaks"],
    }


def get_vault_summary() -> dict[str, Any]:
    """Return a one-page vault health summary."""
    chain_report = verify_chain()
    all_entries = read_vault_entries(limit=1000)

    # Count by type
    type_counts: dict[str, int] = {}
    for e in all_entries:
        t = e.get("type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1

    # Count by actor
    actor_counts: dict[str, int] = {}
    for e in all_entries:
        a = e.get("actor_id", "unknown")
        actor_counts[a] = actor_counts.get(a, 0) + 1

    # Latest entry
    latest = all_entries[-1] if all_entries else None

    return {
        "vault_path": _VAULT_PATH,
        "total_entries": len(all_entries),
        "chain_valid": chain_report["valid"],
        "entries_checked": chain_report["entries_checked"],
        "chain_breaks": chain_report["breaks"],
        "counts_by_type": type_counts,
        "counts_by_actor": actor_counts,
        "latest_entry_id": latest.get("entry_id") if latest else None,
        "latest_timestamp": latest.get("timestamp") if latest else None,
    }


def export_vault_bundle(format: str = "jsonl") -> dict[str, Any]:
    """Export the full vault ledger as a bundle.

    For JSON format, returns all entries as a list.
    For jsonl, returns the raw file path.
    """
    all_entries = read_vault_entries(limit=100000)
    chain_report = verify_chain()

    if format == "json":
        return {
            "format": "json",
            "chain_valid": chain_report["valid"],
            "entries_checked": chain_report["entries_checked"],
            "chain_breaks": chain_report["breaks"],
            "entries": all_entries,
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }
    else:
        return {
            "format": "jsonl",
            "path": _VAULT_PATH,
            "chain_valid": chain_report["valid"],
            "entries_checked": chain_report["entries_checked"],
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }
