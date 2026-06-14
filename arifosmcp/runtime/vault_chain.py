"""
arifosmcp/runtime/vault_chain.py
═══════════════════════════════════════════════════════════════════════════════
EUREKA 6: Vault Chain Verifier

Verifies hash chain integrity across VAULT999 entries.

Each entry must contain:
  - id (str)           — unique entry identifier
  - entry_hash (str)   — sha256 hex digest of the entry's content
  - previous_hash (str) — sha256 hex digest of the previous entry,
                          or empty string for the first entry (genesis)
  - signature (str)    — hex-encoded cryptographic signature

Constitutional Floors: F1 (Amanah), F8 (Transparency)

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from typing import Any

# ──────────────────────────────────────────────────────────────────────────────
# Validation helpers
# ──────────────────────────────────────────────────────────────────────────────


def _required_field(entry: dict[str, Any], field: str) -> str | None:
    """
    Return ``entry[field]`` if it is a non-empty string, else ``None``.
    """
    val = entry.get(field)
    if isinstance(val, str) and val:
        return val
    return None


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────


def verify_vault_chain(entries: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    """
    Verify hash chain integrity across VAULT999 entries.

    Walks the list of entries **in order** (index 0 is the genesis / first
    entry). For each entry:

    - ``entry_hash`` must be a non-empty string.
    - ``previous_hash`` of entry[i] must equal ``entry_hash`` of entry[i-1],
      unless i == 0 (first entry), in which case ``previous_hash`` should be
      empty, indicating the genesis entry.
    - ``signature`` must be a non-empty string.

    Parameters
    ----------
    entries : list[dict]
        Ordered list of vault chain entries. Each dict must contain at least:
        - ``id`` (str)
        - ``entry_hash`` (str)
        - ``previous_hash`` (str)
        - ``signature`` (str)

    Returns
    -------
    tuple[bool, list[str]]
        ``(True, [])`` if the entire chain is valid.
        ``(False, [broken_entry_id, ...])`` with the IDs of each broken
        entry if any link fails. An empty chain returns ``(True, [])``
        (trivially valid).
    """
    if not entries:
        return (True, [])

    broken: list[str] = []

    for i, entry in enumerate(entries):
        eid = entry.get("id", f"<entry_{i}>")

        entry_hash = _required_field(entry, "entry_hash")
        previous_hash = _required_field(entry, "previous_hash")
        signature = _required_field(entry, "signature")

        # ── structural field checks ────────────────────────────────────────
        if entry_hash is None:
            broken.append(eid)
            continue
        if signature is None:
            broken.append(eid)
            continue

        # ── genesis entry must have empty (or absent) previous_hash ────────
        if i == 0:
            if previous_hash is not None and previous_hash != "":
                broken.append(eid)
                continue
        else:
            # ── link check: previous_hash == entry_hash of predecessor ──────
            prev = entries[i - 1]
            prev_hash = _required_field(prev, "entry_hash")
            if previous_hash is None or prev_hash is None:
                broken.append(eid)
                continue
            if previous_hash != prev_hash:
                broken.append(eid)
                continue

    if broken:
        return (False, broken)

    return (True, [])
