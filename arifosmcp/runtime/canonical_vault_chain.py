"""
canonical_vault_chain.py — F-004 VAULT REPLAY INTEGRITY

Single chain model for VAULT999 constitutional seals:
  append → durable receipt → verify (hash + link) → replay (genesis→head)

Invariant:
  Every sealed consequence must be independently verifiable and
  deterministically replayable from genesis to head, with no silent gaps.

Doctrine:
  - Historical gaps are classified, never rewritten.
  - Head pointer is DERIVED from chain tail (cache only).
  - One envelope, one path, one sequence allocator.
  - Negative tests assert exact failure classes.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import threading
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

# ── Paths (single canonical namespace) ────────────────────────────

DEFAULT_VAULT_DIR = Path(
    os.environ.get(
        "ARIFOS_CANONICAL_VAULT_DIR",
        "/root/.local/share/arifos/vault999",
    )
)
CHAIN_FILENAME = "seal_chain.jsonl"
HEAD_FILENAME = "seal_chain_head.json"
ALLOC_FILENAME = "seal_seq_allocator.json"
LOCK_FILENAME = "seal_chain.append.lock"

# Epoch marker: receipts after this boundary must use full envelope.
# Historical lines before first CANONICAL epoch seal are classified HISTORICAL_*.
CANONICAL_EPOCH_ID = "F004-CANONICAL-2026-07-17"

GENESIS_PREV_HASH = "genesis"


class GapClass(StrEnum):
    """Exact failure / discontinuity classes — never silent."""

    HISTORICAL_LINK_GAP = "HISTORICAL_LINK_GAP"
    HISTORICAL_CORRUPT_LINE = "HISTORICAL_CORRUPT_LINE"
    HISTORICAL_MISSING_FIELDS = "HISTORICAL_MISSING_FIELDS"
    HASH_MISMATCH = "HASH_MISMATCH"
    CHAIN_BREAK = "CHAIN_BREAK"
    DUPLICATE_RECEIPT = "DUPLICATE_RECEIPT"
    SEQUENCE_COLLISION = "SEQUENCE_COLLISION"
    EPOCH_RESET = "EPOCH_RESET"
    SIGNATURE_FAIL = "SIGNATURE_FAIL"
    WRONG_KEY = "WRONG_KEY"
    TRUNCATED_TAIL = "TRUNCATED_TAIL"
    EMPTY_OK = "EMPTY_OK"


class VerifyStatus(StrEnum):
    VERIFIED = "verified"
    GAPS_FOUND = "gaps-found"
    NO_CHAIN = "no-chain"
    ERROR = "error"


# ── Envelope ─────────────────────────────────────────────────────

# Fields that participate in receipt_hash (canonical, sorted JSON).
_HASH_FIELDS = (
    "sequence",
    "previous_hash",
    "timestamp",
    "actor_id",
    "session_id",
    "trace_id",
    "operation_id",
    "tool_name",
    "input_hash",
    "authority_state",
    "decision_reference",
    "result_hash",
    "reversibility",
    "software_release",
    "epoch_id",
)


@dataclass
class ReceiptEnvelope:
    """Constitutional minimum record. Domain payload rides as result_hash only."""

    receipt_id: str
    sequence: int
    previous_hash: str
    receipt_hash: str
    timestamp: str
    actor_id: str
    actor_verification: dict[str, Any]
    session_id: str
    trace_id: str
    operation_id: str
    tool_name: str
    input_hash: str
    authority_state: str
    decision_reference: str
    result_hash: str
    reversibility: str
    software_release: str
    signature: str
    epoch_id: str = CANONICAL_EPOCH_ID
    # Wire aliases for observatory / legacy readers
    seq: int | None = None
    prev_hash: str | None = None
    this_hash: str | None = None
    actor: str | None = None
    verdict: str = "SEAL"

    def __post_init__(self) -> None:
        if self.seq is None:
            self.seq = self.sequence
        if self.prev_hash is None:
            self.prev_hash = self.previous_hash
        if self.this_hash is None:
            self.this_hash = self.receipt_hash
        if self.actor is None:
            self.actor = self.actor_id

    def to_wire(self) -> dict[str, Any]:
        d = asdict(self)
        # Keep both canonical and legacy keys for dual readers.
        return d


def _now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _sha256_hex(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return "sha256:" + hashlib.sha256(data).hexdigest()


def compute_receipt_hash(fields: dict[str, Any]) -> str:
    """Deterministic receipt hash over the constitutional envelope body."""
    body = {k: fields.get(k) for k in _HASH_FIELDS if k != "receipt_hash"}
    # previous_hash is included; receipt_hash is the output.
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), default=str)
    return _sha256_hex(canonical)


def normalize_hash(value: Any) -> str | None:
    """Normalize hash strings for comparison (strip whitespace, allow bare hex)."""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    return s


def hashes_equal(a: Any, b: Any) -> bool:
    """Compare hashes with prefix tolerance (sha256:hex vs bare hex)."""
    na, nb = normalize_hash(a), normalize_hash(b)
    if na is None or nb is None:
        return False
    if na == nb:
        return True
    # strip sha256: for bare compare
    def bare(x: str) -> str:
        return x[7:] if x.startswith("sha256:") else x

    return bare(na) == bare(nb)


# ── Path helpers ─────────────────────────────────────────────────


@dataclass
class VaultPaths:
    vault_dir: Path

    @property
    def chain(self) -> Path:
        return self.vault_dir / CHAIN_FILENAME

    @property
    def head(self) -> Path:
        return self.vault_dir / HEAD_FILENAME

    @property
    def allocator(self) -> Path:
        return self.vault_dir / ALLOC_FILENAME

    @property
    def lock(self) -> Path:
        return self.vault_dir / LOCK_FILENAME


def paths_for(vault_dir: Path | str | None = None) -> VaultPaths:
    return VaultPaths(Path(vault_dir) if vault_dir else DEFAULT_VAULT_DIR)


# ── File lock ────────────────────────────────────────────────────

_thread_lock = threading.RLock()


class _FileLock:
    def __init__(self, lock_path: Path) -> None:
        self.lock_path = lock_path
        self._fh: Any = None

    def __enter__(self) -> _FileLock:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = open(self.lock_path, "a+", encoding="utf-8")  # noqa: SIM115
        fcntl.flock(self._fh.fileno(), fcntl.LOCK_EX)
        return self

    def __exit__(self, *args: Any) -> None:
        if self._fh is not None:
            try:
                fcntl.flock(self._fh.fileno(), fcntl.LOCK_UN)
            finally:
                self._fh.close()
                self._fh = None


# ── Parse / walk ─────────────────────────────────────────────────


@dataclass
class ParsedLine:
    line_no: int
    raw: str
    entry: dict[str, Any] | None
    corrupt: bool
    corrupt_reason: str | None = None


def parse_chain_lines(chain_path: Path) -> list[ParsedLine]:
    if not chain_path.exists():
        return []
    out: list[ParsedLine] = []
    with open(chain_path, encoding="utf-8", errors="replace") as fh:
        for line_no, line in enumerate(fh, start=1):
            raw = line.rstrip("\n")
            s = raw.strip()
            if not s:
                continue
            if not s.startswith("{"):
                out.append(
                    ParsedLine(
                        line_no=line_no,
                        raw=raw,
                        entry=None,
                        corrupt=True,
                        corrupt_reason="non_json_prefix",
                    )
                )
                continue
            try:
                parsed = json.loads(s)
            except json.JSONDecodeError as exc:
                out.append(
                    ParsedLine(
                        line_no=line_no,
                        raw=raw,
                        entry=None,
                        corrupt=True,
                        corrupt_reason=f"json_decode:{exc}",
                    )
                )
                continue
            if not isinstance(parsed, dict):
                out.append(
                    ParsedLine(
                        line_no=line_no,
                        raw=raw,
                        entry=None,
                        corrupt=True,
                        corrupt_reason="non_dict",
                    )
                )
                continue
            out.append(ParsedLine(line_no=line_no, raw=raw, entry=parsed, corrupt=False))
    return out


def entry_this_hash(entry: dict[str, Any]) -> str | None:
    return normalize_hash(
        entry.get("this_hash")
        or entry.get("receipt_hash")
        or entry.get("hash")
        or entry.get("seal_hash")
        or entry.get("content_hash")
    )


def entry_prev_hash(entry: dict[str, Any]) -> str | None:
    return normalize_hash(
        entry.get("prev_hash")
        or entry.get("previous_hash")
        or entry.get("previous_id")
        or entry.get("parent_hash")
    )


def entry_sequence(entry: dict[str, Any]) -> Any:
    return entry.get("sequence", entry.get("seq"))


def is_canonical_entry(entry: dict[str, Any]) -> bool:
    """True if entry claims the F-004 canonical envelope."""
    return (
        entry.get("epoch_id") == CANONICAL_EPOCH_ID
        or entry.get("envelope_version") == "f004-v1"
        or (
            "receipt_id" in entry
            and "receipt_hash" in entry
            and "previous_hash" in entry
            and isinstance(entry.get("sequence"), int)
        )
    )


# ── Verify ───────────────────────────────────────────────────────


@dataclass
class GapRecord:
    index: int
    line_no: int
    gap_class: GapClass
    expected_prev: str | None
    got_prev: str | None
    seq: Any = None
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "line_no": self.line_no,
            "gap_class": str(self.gap_class),
            "expected_prev": (str(self.expected_prev)[:64] if self.expected_prev else None),
            "got": (str(self.got_prev)[:64] if self.got_prev else None),
            "seq": self.seq,
            "detail": self.detail,
        }


@dataclass
class VerifyResult:
    verified: bool
    status: VerifyStatus
    entries: int
    corrupt_lines: int
    gaps: list[GapRecord] = field(default_factory=list)
    head_seq: Any = None
    head_hash: str | None = None
    ledger_path: str = ""
    canonical_entries: int = 0
    historical_entries: int = 0
    failure_classes: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "verified": self.verified,
            "status": str(self.status),
            "entries": self.entries,
            "corrupt_lines": self.corrupt_lines,
            "gaps": [g.to_dict() for g in self.gaps[:100]],
            "gap_count": len(self.gaps),
            "head_seq": self.head_seq,
            "head_hash": self.head_hash,
            "ledger_path": self.ledger_path,
            "canonical_entries": self.canonical_entries,
            "historical_entries": self.historical_entries,
            "failure_classes": self.failure_classes,
            # F-004: never claim green when gaps exist
            "chain_verified": self.verified,
        }


def verify_chain(
    vault_dir: Path | str | None = None,
    *,
    scope: str = "full",
) -> VerifyResult:
    """Walk seal_chain.jsonl; classify every discontinuity (never silent).

    scope:
      - full: entire file including historical (production truth)
      - canonical: only F-004 envelope entries (forward chain integrity)
    """
    p = paths_for(vault_dir)
    if not p.chain.exists():
        return VerifyResult(
            verified=True,  # empty genesis is valid
            status=VerifyStatus.NO_CHAIN,
            entries=0,
            corrupt_lines=0,
            ledger_path=str(p.chain),
            failure_classes={GapClass.EMPTY_OK: 1},
        )

    lines = parse_chain_lines(p.chain)
    gaps: list[GapRecord] = []
    classes: dict[str, int] = {}
    prev_hash: str | None = None
    prev_was_canonical = False
    entries = 0
    corrupt = 0
    canonical_n = 0
    historical_n = 0
    seen_ids: set[str] = set()
    seen_seqs: set[Any] = set()
    last_entry: dict[str, Any] | None = None
    parseable_index = -1
    scope_canonical = scope == "canonical"

    for pl in lines:
        if pl.corrupt or pl.entry is None:
            corrupt += 1
            if scope_canonical:
                # corrupt lines outside canonical scope do not fail canonical verify
                continue
            gc = GapClass.HISTORICAL_CORRUPT_LINE
            classes[gc] = classes.get(gc, 0) + 1
            gaps.append(
                GapRecord(
                    index=parseable_index + 1,
                    line_no=pl.line_no,
                    gap_class=gc,
                    expected_prev=prev_hash,
                    got_prev=None,
                    detail=pl.corrupt_reason or "corrupt",
                )
            )
            continue

        entry = pl.entry
        canon = is_canonical_entry(entry)

        if scope_canonical and not canon:
            historical_n += 1
            continue

        parseable_index += 1
        entries += 1
        last_entry = entry
        if canon:
            canonical_n += 1
        else:
            historical_n += 1

        this_h = entry_this_hash(entry)
        prev_h = entry_prev_hash(entry)
        seq = entry_sequence(entry)
        rid = entry.get("receipt_id") or entry.get("id")

        # First canonical entry after historical: prev may be genesis (epoch open) — allowed
        if scope_canonical and prev_hash is None and prev_h and str(prev_h).lower() in (
            "genesis",
            GENESIS_PREV_HASH,
        ):
            # epoch open — not a gap
            pass
        # Duplicate receipt_id — always a real defect
        elif rid and rid in seen_ids:
            gc = GapClass.DUPLICATE_RECEIPT
            classes[gc] = classes.get(gc, 0) + 1
            gaps.append(
                GapRecord(
                    index=parseable_index,
                    line_no=pl.line_no,
                    gap_class=gc,
                    expected_prev=prev_hash,
                    got_prev=prev_h,
                    seq=seq,
                    detail=f"duplicate receipt_id={rid}",
                )
            )
        if rid:
            seen_ids.add(str(rid))

        # Sequence collision: only within CANONICAL epoch.
        # Historical writers reused 1..N across epochs — that is EPOCH_RESET noise, not live collision.
        if isinstance(seq, int) and canon and seq in seen_seqs:
            gc = GapClass.SEQUENCE_COLLISION
            classes[gc] = classes.get(gc, 0) + 1
            gaps.append(
                GapRecord(
                    index=parseable_index,
                    line_no=pl.line_no,
                    gap_class=gc,
                    expected_prev=prev_hash,
                    got_prev=prev_h,
                    seq=seq,
                    detail=f"duplicate sequence={seq}",
                )
            )
        if isinstance(seq, int) and canon:
            seen_seqs.add(seq)

        # Epoch reset: prev_hash claims genesis mid-chain
        if prev_hash is not None and prev_h and str(prev_h).lower() in ("genesis", GENESIS_PREV_HASH):
            # First entry of canonical scope after historical may open with genesis — OK
            if scope_canonical and not prev_was_canonical:
                pass
            else:
                gc = GapClass.EPOCH_RESET if canon else GapClass.HISTORICAL_LINK_GAP
                classes[gc] = classes.get(gc, 0) + 1
                gaps.append(
                    GapRecord(
                        index=parseable_index,
                        line_no=pl.line_no,
                        gap_class=gc,
                        expected_prev=prev_hash,
                        got_prev=prev_h,
                        seq=seq,
                        detail="prev_hash=genesis after non-empty chain",
                    )
                )
        # Chain break: prev_hash does not match previous this_hash
        elif prev_hash is not None and prev_h and not hashes_equal(prev_h, prev_hash):
            if canon and prev_was_canonical:
                gc = GapClass.CHAIN_BREAK
            elif scope_canonical and canon and prev_hash is not None:
                # first link from historical tail into canonical — if not matching, epoch open
                if str(prev_h).lower() in ("genesis", GENESIS_PREV_HASH):
                    gc = None  # type: ignore[assignment]
                else:
                    gc = GapClass.CHAIN_BREAK
            else:
                gc = GapClass.HISTORICAL_LINK_GAP
            if gc is not None:
                classes[gc] = classes.get(gc, 0) + 1
                gaps.append(
                    GapRecord(
                        index=parseable_index,
                        line_no=pl.line_no,
                        gap_class=gc,
                        expected_prev=prev_hash,
                        got_prev=prev_h,
                        seq=seq,
                        detail="prev_hash != prior this_hash",
                    )
                )
        elif prev_hash is not None and not prev_h and not this_h:
            if not scope_canonical:
                gc = GapClass.HISTORICAL_MISSING_FIELDS
                classes[gc] = classes.get(gc, 0) + 1
                gaps.append(
                    GapRecord(
                        index=parseable_index,
                        line_no=pl.line_no,
                        gap_class=gc,
                        expected_prev=prev_hash,
                        got_prev=None,
                        seq=seq,
                        detail="missing prev_hash and this_hash",
                    )
                )

        # Canonical: recompute receipt_hash when body fields present
        if canon and entry.get("receipt_hash") and all(
            k in entry for k in ("sequence", "previous_hash", "timestamp", "actor_id")
        ):
            expected = compute_receipt_hash(entry)
            if not hashes_equal(expected, entry.get("receipt_hash")):
                gc = GapClass.HASH_MISMATCH
                classes[gc] = classes.get(gc, 0) + 1
                gaps.append(
                    GapRecord(
                        index=parseable_index,
                        line_no=pl.line_no,
                        gap_class=gc,
                        expected_prev=expected,
                        got_prev=entry.get("receipt_hash"),
                        seq=seq,
                        detail="recomputed receipt_hash mismatch",
                    )
                )

        if this_h:
            prev_hash = this_h
            prev_was_canonical = canon

    head_seq = entry_sequence(last_entry) if last_entry else None
    head_hash = entry_this_hash(last_entry) if last_entry else None

    # Empty file with only empties → valid genesis
    if entries == 0 and (corrupt == 0 or scope_canonical):
        return VerifyResult(
            verified=True,
            status=VerifyStatus.NO_CHAIN if entries == 0 and corrupt == 0 else VerifyStatus.VERIFIED,
            entries=0,
            corrupt_lines=0 if scope_canonical else corrupt,
            ledger_path=str(p.chain),
            failure_classes={GapClass.EMPTY_OK: 1} if entries == 0 else {},
            canonical_entries=canonical_n,
            historical_entries=historical_n,
        )

    # Green only if zero gaps and at least one entry (or empty ok)
    verified = len(gaps) == 0 and entries > 0
    # Special: empty chain is verified genesis
    if entries == 0 and (corrupt == 0 or scope_canonical):
        verified = True

    status = (
        VerifyStatus.VERIFIED
        if verified
        else (VerifyStatus.GAPS_FOUND if gaps else VerifyStatus.ERROR)
    )

    return VerifyResult(
        verified=verified,
        status=status,
        entries=entries,
        corrupt_lines=0 if scope_canonical else corrupt,
        gaps=gaps,
        head_seq=head_seq,
        head_hash=head_hash,
        ledger_path=str(p.chain),
        canonical_entries=canonical_n,
        historical_entries=historical_n,
        failure_classes=classes,
    )


# ── Replay ───────────────────────────────────────────────────────


@dataclass
class ReplayResult:
    status: str
    entries: int
    returned: int
    skipped_corrupt: int
    head_seq: Any
    head_hash: str | None
    replay: list[dict[str, Any]]
    final_state_hash: str | None
    ledger_path: str
    gaps_declared: int
    boundary: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "entries": self.entries,
            "returned": self.returned,
            "skipped_corrupt": self.skipped_corrupt,
            "head_seq": self.head_seq,
            "head_hash": self.head_hash,
            "replay": self.replay,
            "final_state_hash": self.final_state_hash,
            "ledger_path": self.ledger_path,
            "gaps_declared": self.gaps_declared,
            "boundary": self.boundary,
            "replay_verified": self.status in ("available", "partial"),
        }


def replay_chain(
    vault_dir: Path | str | None = None,
    *,
    limit: int = 50,
    from_seq: int | None = None,
) -> ReplayResult:
    """Deterministic replay: ordered accepted receipts → final head/state.

    Corrupt lines are skipped with count declared (never silent).
    """
    p = paths_for(vault_dir)
    limit = max(1, min(int(limit), 500))
    if not p.chain.exists():
        return ReplayResult(
            status="no-chain",
            entries=0,
            returned=0,
            skipped_corrupt=0,
            head_seq=None,
            head_hash=None,
            replay=[],
            final_state_hash=None,
            ledger_path=str(p.chain),
            gaps_declared=0,
            boundary="empty-genesis",
        )

    lines = parse_chain_lines(p.chain)
    accepted: list[dict[str, Any]] = []
    skipped = 0
    state = hashlib.sha256(b"VAULT999-GENESIS")

    for pl in lines:
        if pl.corrupt or pl.entry is None:
            skipped += 1
            continue
        entry = pl.entry
        seq = entry_sequence(entry)
        if from_seq is not None and isinstance(seq, int) and seq < from_seq:
            continue
        accepted.append(entry)
        # cumulative state = H(state || this_hash || line_no)
        th = entry_this_hash(entry) or ""
        state.update(f"{pl.line_no}:{th}".encode())

    final = "sha256:" + state.hexdigest()
    tail = accepted[-limit:]
    head = accepted[-1] if accepted else None

    # If verify finds gaps, status is partial not green-silent
    v = verify_chain(vault_dir)
    status = "available" if v.verified or (accepted and not v.gaps) else "partial"
    if not accepted and skipped:
        status = "partial"
        boundary = "all-corrupt-or-empty"
    elif not accepted:
        status = "no-chain"
        boundary = "empty-genesis"
    else:
        boundary = None if v.verified else "gaps-declared"

    return ReplayResult(
        status=status,
        entries=len(accepted),
        returned=len(tail),
        skipped_corrupt=skipped,
        head_seq=entry_sequence(head) if head else None,
        head_hash=entry_this_hash(head) if head else None,
        replay=tail,
        final_state_hash=final if accepted else None,
        ledger_path=str(p.chain),
        gaps_declared=len(v.gaps),
        boundary=boundary,
    )


# ── Head (derived) ───────────────────────────────────────────────


def derive_head(vault_dir: Path | str | None = None) -> dict[str, Any]:
    """Head is derived from chain tail — never an independent freestyle seal."""
    p = paths_for(vault_dir)
    lines = parse_chain_lines(p.chain) if p.chain.exists() else []
    last: dict[str, Any] | None = None
    for pl in reversed(lines):
        if not pl.corrupt and pl.entry is not None:
            last = pl.entry
            break

    if last is None:
        head = {
            "seq": 0,
            "sequence": 0,
            "hash": GENESIS_PREV_HASH,
            "receipt_hash": GENESIS_PREV_HASH,
            "epoch": CANONICAL_EPOCH_ID,
            "status": "genesis",
            "derived": True,
        }
    else:
        head = {
            "seq": entry_sequence(last),
            "sequence": entry_sequence(last),
            "hash": entry_this_hash(last),
            "receipt_hash": entry_this_hash(last),
            "receipt_id": last.get("receipt_id") or last.get("id"),
            "actor": last.get("actor_id") or last.get("actor"),
            "timestamp": last.get("timestamp") or last.get("epoch"),
            "epoch_id": last.get("epoch_id"),
            "verdict": last.get("verdict", "SEAL"),
            "derived": True,
            "source": "chain_tail",
        }

    # Cache derived head (overwrite freestyle head — F-004 alignment)
    try:
        p.vault_dir.mkdir(parents=True, exist_ok=True)
        tmp = p.head.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(head, indent=2, default=str) + "\n", encoding="utf-8")
        tmp.replace(p.head)
    except OSError:
        pass

    return head


# ── Sequence allocator ───────────────────────────────────────────


def _read_allocator(p: VaultPaths) -> int:
    if p.allocator.exists():
        try:
            data = json.loads(p.allocator.read_text(encoding="utf-8"))
            return int(data.get("next_seq", 1))
        except Exception:
            pass
    # Bootstrap from chain max integer seq among canonical entries
    max_seq = 0
    if p.chain.exists():
        for pl in parse_chain_lines(p.chain):
            if pl.entry and is_canonical_entry(pl.entry):
                s = entry_sequence(pl.entry)
                if isinstance(s, int) and s > max_seq:
                    max_seq = s
    return max_seq + 1


def _write_allocator(p: VaultPaths, next_seq: int) -> None:
    p.allocator.write_text(
        json.dumps({"next_seq": next_seq, "updated": _now_iso()}, indent=2) + "\n",
        encoding="utf-8",
    )


# ── Append ───────────────────────────────────────────────────────


@dataclass
class AppendResult:
    ok: bool
    receipt: dict[str, Any] | None
    failure_class: str | None = None
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "receipt": self.receipt,
            "receipt_id": (self.receipt or {}).get("receipt_id"),
            "sequence": (self.receipt or {}).get("sequence"),
            "failure_class": self.failure_class,
            "detail": self.detail,
        }


def append_receipt(
    *,
    actor_id: str,
    session_id: str = "",
    trace_id: str = "",
    operation_id: str = "",
    tool_name: str = "",
    input_hash: str = "",
    authority_state: str = "OBSERVE_ONLY",
    decision_reference: str = "",
    result_hash: str = "",
    reversibility: str = "REVERSIBLE",
    software_release: str = "",
    actor_verification: dict[str, Any] | None = None,
    signature: str = "",
    verdict: str = "SEAL",
    vault_dir: Path | str | None = None,
    force_prev_hash: str | None = None,
    force_sequence: int | None = None,
) -> AppendResult:
    """Append one canonical receipt. Concurrent-safe via flock + thread lock."""
    p = paths_for(vault_dir)
    p.vault_dir.mkdir(parents=True, exist_ok=True)

    with _thread_lock, _FileLock(p.lock):
        # Last hash from chain
        prev = GENESIS_PREV_HASH
        if p.chain.exists():
            for pl in reversed(parse_chain_lines(p.chain)):
                if pl.entry and entry_this_hash(pl.entry):
                    prev = entry_this_hash(pl.entry) or GENESIS_PREV_HASH
                    break

        if force_prev_hash is not None:
            prev = force_prev_hash

        seq = force_sequence if force_sequence is not None else _read_allocator(p)

        # Collision check
        if force_sequence is None:
            # ensure allocator advances past any collision
            while True:
                collision = False
                if p.chain.exists():
                    for pl in parse_chain_lines(p.chain):
                        if pl.entry and entry_sequence(pl.entry) == seq and is_canonical_entry(pl.entry):
                            collision = True
                            break
                if not collision:
                    break
                seq += 1

        receipt_id = f"rcpt-{uuid.uuid4().hex[:16]}"
        ts = _now_iso()
        body = {
            "sequence": seq,
            "previous_hash": prev,
            "timestamp": ts,
            "actor_id": actor_id,
            "session_id": session_id or "",
            "trace_id": trace_id or "",
            "operation_id": operation_id or receipt_id,
            "tool_name": tool_name or "",
            "input_hash": input_hash or _sha256_hex(""),
            "authority_state": authority_state,
            "decision_reference": decision_reference or "",
            "result_hash": result_hash or _sha256_hex(""),
            "reversibility": reversibility,
            "software_release": software_release or "",
            "epoch_id": CANONICAL_EPOCH_ID,
        }
        receipt_hash = compute_receipt_hash(body)

        env = ReceiptEnvelope(
            receipt_id=receipt_id,
            sequence=seq,
            previous_hash=prev,
            receipt_hash=receipt_hash,
            timestamp=ts,
            actor_id=actor_id,
            actor_verification=actor_verification
            or {"actor_verified": False, "method": "unsigned"},
            session_id=session_id or "",
            trace_id=trace_id or "",
            operation_id=operation_id or receipt_id,
            tool_name=tool_name or "",
            input_hash=body["input_hash"],
            authority_state=authority_state,
            decision_reference=decision_reference or "",
            result_hash=body["result_hash"],
            reversibility=reversibility,
            software_release=software_release or "",
            signature=signature or "",
            epoch_id=CANONICAL_EPOCH_ID,
            verdict=verdict,
        )
        wire = env.to_wire()
        wire["envelope_version"] = "f004-v1"

        # Append
        with open(p.chain, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(wire, sort_keys=True, default=str) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

        if force_sequence is None:
            _write_allocator(p, seq + 1)
        derive_head(vault_dir)

        return AppendResult(ok=True, receipt=wire)


# ── Heads agreement (writer / verifier / replay / observatory) ───


def heads_agreement(vault_dir: Path | str | None = None) -> dict[str, Any]:
    """Compare writer head, verifier head, replay head, derived head."""
    p = paths_for(vault_dir)
    derived = derive_head(vault_dir)
    v = verify_chain(vault_dir)
    r = replay_chain(vault_dir, limit=1)

    file_head: dict[str, Any] | None = None
    if p.head.exists():
        try:
            file_head = json.loads(p.head.read_text(encoding="utf-8"))
        except Exception as exc:
            file_head = {"error": str(exc)}

    keys = {
        "derived_head": derived.get("hash") or derived.get("receipt_hash"),
        "verifier_head": v.head_hash,
        "replay_head": r.head_hash,
        "file_head": (file_head or {}).get("hash") or (file_head or {}).get("receipt_hash"),
    }
    # Normalize for equality
    norms = {k: normalize_hash(val) for k, val in keys.items()}
    non_null = [n for n in norms.values() if n and n != GENESIS_PREV_HASH]
    agree = len(set(non_null)) <= 1 if non_null else True

    return {
        "agree": agree,
        "heads": keys,
        "normalized": norms,
        "verifier_status": str(v.status),
        "replay_status": r.status,
        "gap_count": len(v.gaps),
        "ledger_path": str(p.chain),
        "canonical_entries": v.canonical_entries,
        "historical_entries": v.historical_entries,
    }


__all__ = [
    "CANONICAL_EPOCH_ID",
    "GapClass",
    "VerifyStatus",
    "ReceiptEnvelope",
    "append_receipt",
    "verify_chain",
    "replay_chain",
    "derive_head",
    "heads_agreement",
    "compute_receipt_hash",
    "paths_for",
]
