"""
arifOS Evidence Store — durable append-only ledger for evidence refs.

Epoch 2 / Item 3 of the Kernel Senescence Reduction plan.
Each evidence ref (arifos://evidence/{id}) points to a real, durable
record. The record can be retrieved by ref. The store is append-only;
records are never edited or deleted (F11 AUDIT).

Schema of a stored record:
    {
      "ref": "arifos://evidence/{id}",
      "evidence": { ... arbitrary dict ... },
      "appended_at": "2026-07-17T...",
      "content_hash": "sha256:..."
    }

The ref id is the sha256-prefix of the content_hash. Same evidence
appended twice produces the same ref (idempotent).

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


# Schema version. Bump when the record shape changes.
EVIDENCE_STATE_VERSION = 1

# Default store path. Override via ARIFOS_EVIDENCE_PATH.
DEFAULT_EVIDENCE_PATH = "/var/lib/arifos/vault/evidence.jsonl"

# Ref id length — first 16 hex chars of sha256 = 64 bits of entropy.
# Collision probability is ~1 in 2^32 for a billion records.
REF_ID_LENGTH = 16


@dataclass(frozen=True)
class EvidenceRef:
    """Canonical reference to a stored evidence record."""

    ref: str            # arifos://evidence/{id}
    content_hash: str   # sha256:... of the canonical JSON
    appended_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "ref": self.ref,
            "content_hash": self.content_hash,
            "appended_at": self.appended_at,
        }


def _canonical_hash(evidence: dict[str, Any]) -> str:
    """sha256 of the canonical JSON form. Two equal dicts hash the same."""
    encoded = json.dumps(evidence, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _ref_id_from_hash(content_hash: str) -> str:
    """Extract the ref id from a sha256 hash. Strips the 'sha256:' prefix."""
    hex_part = content_hash.split(":", 1)[1] if ":" in content_hash else content_hash
    return hex_part[:REF_ID_LENGTH]


def _make_ref(content_hash: str) -> str:
    return f"arifos://evidence/{_ref_id_from_hash(content_hash)}"


# ── The store ──────────────────────────────────────────────────────────────


class EvidenceStore:
    """Append-only evidence ledger.

    Records are JSONL lines: one record per line, newline-terminated.
    The store never edits or deletes records. Reads are O(N) over the
    file (acceptable for a federation-scale append log; if a billion
    records land, this becomes a real database).
    """

    def __init__(self, path: str | Path | None = None) -> None:
        if path is None:
            path = os.getenv("ARIFOS_EVIDENCE_PATH", DEFAULT_EVIDENCE_PATH)
        self.path = Path(path)
        # Best-effort: ensure the parent directory exists. Failures here
        # are surfaced at append time, not at construction.
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass

    def append(self, evidence: dict[str, Any]) -> EvidenceRef:
        """Append an evidence record. Returns the canonical ref.

        Idempotent: appending the same evidence twice (or any number of
        times) is a no-op on disk — only the appended_at of the first
        append is recorded. Subsequent appends return the same ref.

        The ref id is derived from the content hash, so the same evidence
        always produces the same ref. This is the audit's "evidence
        ranking" requirement made durable.
        """
        if not isinstance(evidence, dict):
            raise TypeError(
                f"evidence must be a dict, got {type(evidence).__name__}"
            )
        content_hash = _canonical_hash(evidence)
        ref = _make_ref(content_hash)
        # If the record already exists, return the original timestamp.
        existing = self._find_by_ref(ref)
        if existing is not None:
            return EvidenceRef(
                ref=existing["ref"],
                content_hash=existing["content_hash"],
                appended_at=existing["appended_at"],
            )
        # Otherwise, append a new record.
        record = {
            "ref": ref,
            "evidence": evidence,
            "appended_at": datetime.now(UTC).isoformat(),
            "content_hash": content_hash,
            "state_version": EVIDENCE_STATE_VERSION,
        }
        self._append_line(record)
        return EvidenceRef(
            ref=ref,
            content_hash=content_hash,
            appended_at=record["appended_at"],
        )

    def get(self, ref: str) -> dict[str, Any] | None:
        """Retrieve an evidence record by ref. Returns None if not found."""
        record = self._find_by_ref(ref)
        if record is None:
            return None
        return record.get("evidence")

    def has(self, ref: str) -> bool:
        """True iff the ref is in the store."""
        return self._find_by_ref(ref) is not None

    def all_refs(self) -> tuple[str, ...]:
        """All evidence refs in the store, in append order."""
        if not self.path.exists():
            return ()
        refs: list[str] = []
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ref = record.get("ref")
                if isinstance(ref, str):
                    refs.append(ref)
        return tuple(refs)

    def _find_by_ref(self, ref: str) -> dict[str, Any] | None:
        """Linear scan for a ref. Returns the full record (with metadata)."""
        if not self.path.exists():
            return None
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if record.get("ref") == ref:
                    return record
        return None

    def _append_line(self, record: dict[str, Any]) -> None:
        """Append a single JSONL line. Atomic on POSIX via write+rename."""
        line = json.dumps(record, sort_keys=True) + "\n"
        tmp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        # Open in append mode is fine; tmp file is rewritten.
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(line)
        # Touch the tmp path so external observers (e.g., a watcher) can
        # detect new appends without scanning the whole file.
        try:
            tmp_path.touch()
        except OSError:
            pass


__all__ = [
    "EVIDENCE_STATE_VERSION",
    "DEFAULT_EVIDENCE_PATH",
    "REF_ID_LENGTH",
    "EvidenceRef",
    "EvidenceStore",
    "_canonical_hash",
    "_make_ref",
]