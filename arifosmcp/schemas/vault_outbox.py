"""
vault_outbox.py — VAULT999 Outbox Pattern (D2)

═══════════════════════════════════════════════════════════
FORGED: 2026-07-13 — Arif's D2 directive
PURPOSE: Never call the VAULT writer directly from session
         shutdown hook. Use an outbox with transactional
         semantics so ordinary session accounting never
         depends on sovereign signing availability.
═══════════════════════════════════════════════════════════

The current doctrine is too broad if it says every session
end needs a sovereign VAULT999 seal. Three closure levels:

  SESSION_OBSERVED       — Session existed but not fully governed
  SESSION_CLOSED         — Governed session completed normally
  SESSION_SOVEREIGN_SEALED — Contains explicit F13 approval

The outbox decouples session closure from VAULT availability:

  vault_outbox:
    event_id, session_id, receipt_class, payload_hash,
    required_capability, idempotency_key, status, attempts

  States:
    PENDING → CLAIMED → APPENDED → VERIFIED
                ↓
           FAILED_RETRYABLE → HOLD

DITEMPA BUKAN DIBERI — The outbox is forged, not given.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# OUTBOX STATE
# ═══════════════════════════════════════════════════════════════════════════════


class OutboxStatus(StrEnum):
    """Lifecycle state of a vault_outbox entry."""

    PENDING = "PENDING"  # Created, not yet claimed by writer
    CLAIMED = "CLAIMED"  # Writer has claimed this entry (claimed_at, claimed_by set)
    APPENDED = "APPENDED"  # Successfully appended to VAULT999
    VERIFIED = "VERIFIED"  # Chain head verified after append
    FAILED_RETRYABLE = "FAILED_RETRYABLE"  # Transient failure, will retry
    HOLD = "HOLD"  # Permanent failure or constitutional hold
    VOID = "VOID"  # Cancelled/voided — will never be appended


class ReceiptClass(StrEnum):
    """What kind of receipt does this outbox entry represent?"""

    SESSION_OBSERVED = "SESSION_OBSERVED"  # Session existed, no governance
    SESSION_CLOSED = "SESSION_CLOSED"  # Governed session, standard closure
    SESSION_SOVEREIGN_SEALED = "SESSION_SOVEREIGN_SEALED"  # F13-ratified
    CONSTITUTIONAL = "CONSTITUTIONAL"  # Floor violation/adherence
    ROUTINE = "ROUTINE"  # Standard operational receipt
    NONE = "NONE"


class SessionClosureState(StrEnum):
    """Session closure states — D2 three-level model.

    A session should not be kept artificially active because
    VAULT is unavailable. Close its operational authority,
    but mark audit closure pending.

    CLOSING                       — Shutdown initiated
    CLOSED_PENDING_RECEIPT        — Operational authority closed,
                                    waiting for outbox → VAULT
    CLOSED_SEALED                 — Full closure, VAULT receipt verified
    CLOSED_UNSEALED               — Closed without VAULT seal
                                    (SESSION_OBSERVED class only)
    CLOSURE_HOLD                  — Closure blocked (constitutional issue)
    """

    CLOSING = "CLOSING"
    CLOSED_PENDING_RECEIPT = "CLOSED_PENDING_RECEIPT"
    CLOSED_SEALED = "CLOSED_SEALED"
    CLOSED_UNSEALED = "CLOSED_UNSEALED"
    CLOSURE_HOLD = "CLOSURE_HOLD"


# ═══════════════════════════════════════════════════════════════════════════════
# OUTBOX ENTRY
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class VaultOutboxEntry:
    """
    A single outbox entry representing work to be done for VAULT999.

    Never call VAULT writer directly from the session shutdown hook.
    Always write to this outbox and let the outbox consumer handle
    the actual append.

    States:
      PENDING → CLAIMED → APPENDED → VERIFIED
                  ↓
             FAILED_RETRYABLE → HOLD
    """

    # ── Identity ──
    event_id: str  # UUIDv7 — unique outbox event
    session_id: str  # Which session this belongs to

    # ── Classification ──
    receipt_class: ReceiptClass
    payload_hash: str  # SHA-256 of the actual payload (never inline)
    required_capability: str  # e.g. "vault.append.session_closure"
    idempotency_key: str  # Deterministic key for dedup

    # ── Status ──
    status: OutboxStatus = OutboxStatus.PENDING
    attempts: int = 0
    max_attempts: int = 3

    # ── Timestamps ──
    created_at: str = ""
    claimed_at: str | None = None
    appended_at: str | None = None
    verified_at: str | None = None

    # ── Claim metadata ──
    claimed_by: str | None = None  # Which outbox consumer claimed this

    # ── Failure tracking ──
    last_error: str | None = None
    last_error_at: str | None = None

    # ── Result ──
    vault_seal_id: str | None = None  # VAULT999 seal hash after append
    vault_receipt_hash: str | None = None  # Full receipt hash
    chain_head_hash: str | None = None  # Chain head after verification

    # ── Audit ──
    outbox_hash: str = ""  # SHA-256 of all fields

    def __post_init__(self) -> None:
        """Set defaults and compute outbox hash."""
        now = datetime.now(UTC)
        if not self.created_at:
            self.created_at = now.isoformat()
        if not self.outbox_hash:
            self.outbox_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Deterministic hash of outbox entry."""
        import hashlib

        canonical = {
            "event_id": self.event_id,
            "session_id": self.session_id,
            "receipt_class": self.receipt_class.value,
            "payload_hash": self.payload_hash,
            "required_capability": self.required_capability,
            "idempotency_key": self.idempotency_key,
            "status": self.status.value,
            "attempts": self.attempts,
        }
        return hashlib.sha256(json.dumps(canonical, sort_keys=True).encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        """Serialise to dict for storage."""
        return {
            "event_id": self.event_id,
            "session_id": self.session_id,
            "receipt_class": self.receipt_class.value,
            "payload_hash": self.payload_hash,
            "required_capability": self.required_capability,
            "idempotency_key": self.idempotency_key,
            "status": self.status.value,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "created_at": self.created_at,
            "claimed_at": self.claimed_at,
            "appended_at": self.appended_at,
            "verified_at": self.verified_at,
            "claimed_by": self.claimed_by,
            "last_error": self.last_error,
            "last_error_at": self.last_error_at,
            "vault_seal_id": self.vault_seal_id,
            "vault_receipt_hash": self.vault_receipt_hash,
            "chain_head_hash": self.chain_head_hash,
            "outbox_hash": self.outbox_hash,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VaultOutboxEntry:
        """Deserialise from dict."""
        return cls(
            event_id=data["event_id"],
            session_id=data["session_id"],
            receipt_class=ReceiptClass(data["receipt_class"]),
            payload_hash=data["payload_hash"],
            required_capability=data["required_capability"],
            idempotency_key=data["idempotency_key"],
            status=OutboxStatus(data.get("status", "PENDING")),
            attempts=data.get("attempts", 0),
            max_attempts=data.get("max_attempts", 3),
            created_at=data.get("created_at", ""),
            claimed_at=data.get("claimed_at"),
            appended_at=data.get("appended_at"),
            verified_at=data.get("verified_at"),
            claimed_by=data.get("claimed_by"),
            last_error=data.get("last_error"),
            last_error_at=data.get("last_error_at"),
            vault_seal_id=data.get("vault_seal_id"),
            vault_receipt_hash=data.get("vault_receipt_hash"),
            chain_head_hash=data.get("chain_head_hash"),
            outbox_hash=data.get("outbox_hash", ""),
        )


# ═══════════════════════════════════════════════════════════════════════════════
# VAULT OUTBOX — persistent outbox
# ═══════════════════════════════════════════════════════════════════════════════


class VaultOutbox:
    """
    Persistent outbox for VAULT999 append operations.

    File-based JSONL storage. Each entry is one line.
    Thread-safe at the file level (append-only).
    """

    def __init__(self, outbox_dir: str | Path = "/var/arifos/vault_outbox"):
        self.outbox_dir = Path(outbox_dir)
        self.outbox_dir.mkdir(parents=True, exist_ok=True)
        self._entries: dict[str, VaultOutboxEntry] = {}
        self._modified: bool = False

        # Index file — fast lookup without scanning all JSONL
        self._index_path = self.outbox_dir / "index.json"
        self._outbox_path = self.outbox_dir / "outbox.jsonl"
        self._load_index()

    def _load_index(self) -> None:
        """Load index from disk."""
        if self._index_path.exists():
            try:
                with open(self._index_path) as f:
                    data = json.load(f)
                    for event_id, entry_data in data.items():
                        self._entries[event_id] = VaultOutboxEntry.from_dict(entry_data)
            except (json.JSONDecodeError, KeyError):
                # Index corrupted — rebuild from JSONL
                self._rebuild_from_jsonl()

    def _rebuild_from_jsonl(self) -> None:
        """Rebuild index from the JSONL outbox file."""
        self._entries = {}
        if not self._outbox_path.exists():
            return
        with open(self._outbox_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        entry = VaultOutboxEntry.from_dict(data)
                        self._entries[entry.event_id] = entry
                    except (json.JSONDecodeError, KeyError):
                        continue
        self._save_index()

    def _save_index(self) -> None:
        """Persist index to disk."""
        with open(self._index_path, "w") as f:
            json.dump(
                {eid: entry.to_dict() for eid, entry in self._entries.items()},
                f,
                indent=2,
            )

    def _append_jsonl(self, entry: VaultOutboxEntry) -> None:
        """Append a single entry to the JSONL file (append-only)."""
        with open(self._outbox_path, "a") as f:
            f.write(json.dumps(entry.to_dict()) + "\n")

    def enqueue(
        self,
        session_id: str,
        receipt_class: ReceiptClass,
        payload_hash: str,
        required_capability: str,
        *,
        idempotency_key: str | None = None,
    ) -> VaultOutboxEntry:
        """
        Enqueue a new outbox entry.

        Args:
            session_id: Session that produced this receipt
            receipt_class: SESSION_OBSERVED | SESSION_CLOSED | SESSION_SOVEREIGN_SEALED
            payload_hash: SHA-256 of the receipt payload (never inline)
            required_capability: e.g. "vault.append.session_closure"
            idempotency_key: Optional — auto-generated if absent

        Returns:
            The created VaultOutboxEntry (status=PENDING)
        """
        event_id = str(uuid4())
        key = idempotency_key or f"{session_id}:{receipt_class.value}:{payload_hash[:8]}"

        # Idempotency check — skip if identical key already exists
        for existing in self._entries.values():
            if existing.idempotency_key == key and existing.status not in (
                OutboxStatus.FAILED_RETRYABLE,
                OutboxStatus.VOID,
            ):
                logger.info(f"VaultOutbox: idempotency hit for {key} — returning existing entry")
                return existing

        entry = VaultOutboxEntry(
            event_id=event_id,
            session_id=session_id,
            receipt_class=receipt_class,
            payload_hash=payload_hash,
            required_capability=required_capability,
            idempotency_key=key,
        )
        self._entries[event_id] = entry
        self._append_jsonl(entry)
        self._save_index()
        logger.info(
            f"VaultOutbox: enqueued {event_id} [{receipt_class.value}] for session {session_id}"
        )
        return entry

    def claim_next(self, claimer: str = "outbox_consumer") -> VaultOutboxEntry | None:
        """
        Claim the next PENDING entry for processing.

        Atomically marks it CLAIMED with timestamp and claimer identity.
        Returns None if no PENDING entries.
        """
        for entry in self._entries.values():
            if entry.status == OutboxStatus.PENDING:
                entry.status = OutboxStatus.CLAIMED
                entry.claimed_at = datetime.now(UTC).isoformat()
                entry.claimed_by = claimer
                entry.attempts += 1
                self._modified = True
                self._save_index()
                logger.info(f"VaultOutbox: claimed {entry.event_id} by {claimer}")
                return entry
        return None

    def mark_appended(
        self,
        event_id: str,
        vault_seal_id: str,
        vault_receipt_hash: str,
    ) -> None:
        """Mark an entry as APPENDED to VAULT999."""
        entry = self._entries.get(event_id)
        if not entry:
            logger.warning(f"VaultOutbox: unknown event {event_id}")
            return
        entry.status = OutboxStatus.APPENDED
        entry.appended_at = datetime.now(UTC).isoformat()
        entry.vault_seal_id = vault_seal_id
        entry.vault_receipt_hash = vault_receipt_hash
        self._save_index()
        # Append update line to JSONL
        self._append_jsonl(entry)

    def mark_verified(self, event_id: str, chain_head_hash: str) -> None:
        """Mark an entry as VERIFIED after chain head check."""
        entry = self._entries.get(event_id)
        if not entry:
            return
        entry.status = OutboxStatus.VERIFIED
        entry.verified_at = datetime.now(UTC).isoformat()
        entry.chain_head_hash = chain_head_hash
        self._save_index()

    def mark_failed(self, event_id: str, error: str) -> None:
        """Mark an entry as FAILED_RETRYABLE or HOLD based on attempt count.
        Auto-increments attempts on each failure."""
        entry = self._entries.get(event_id)
        if not entry:
            return
        entry.attempts += 1
        entry.last_error = error
        entry.last_error_at = datetime.now(UTC).isoformat()
        if entry.attempts >= entry.max_attempts:
            entry.status = OutboxStatus.HOLD
            logger.error(f"VaultOutbox: HOLD {event_id} after {entry.attempts} attempts: {error}")
        else:
            entry.status = OutboxStatus.FAILED_RETRYABLE
            logger.warning(
                f"VaultOutbox: FAILED_RETRYABLE {event_id} "
                f"(attempt {entry.attempts}/{entry.max_attempts}): {error}"
            )
        self._save_index()

    def mark_void(self, event_id: str, reason: str) -> None:
        """Void an entry — will never be appended."""
        entry = self._entries.get(event_id)
        if not entry:
            return
        entry.status = OutboxStatus.VOID
        entry.last_error = reason
        entry.last_error_at = datetime.now(UTC).isoformat()
        self._save_index()

    def get_pending_count(self) -> int:
        """Count entries still needing processing."""
        return sum(
            1
            for e in self._entries.values()
            if e.status in (OutboxStatus.PENDING, OutboxStatus.FAILED_RETRYABLE)
        )

    def get_by_session(self, session_id: str) -> list[VaultOutboxEntry]:
        """Get all entries for a session."""
        return [e for e in self._entries.values() if e.session_id == session_id]

    def get_by_status(self, status: OutboxStatus) -> list[VaultOutboxEntry]:
        """Get all entries with a given status."""
        return [e for e in self._entries.values() if e.status == status]

    def flush(self) -> None:
        """Force persist index to disk."""
        if self._modified:
            self._save_index()
            self._modified = False


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION CLOSURE — the session-leveL closure state
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class SessionClosure:
    """
    Session closure metadata — tracks what happened when a session ended.

    The three closure levels:
      SESSION_OBSERVED       — Session existed but was not fully governed.
                               Receipt signed by session service, not sovereign.
      SESSION_CLOSED         — Governed session completed normally.
                               Bound session capability signed the receipt.
      SESSION_SOVEREIGN_SEALED — Contains explicit sovereign approval or
                               decision. Verified F13 key signed the receipt.
    """

    # ── Identity ──
    session_id: str
    closure_state: SessionClosureState

    # ── Classification ──
    receipt_class: ReceiptClass
    outbox_event_id: str | None = None  # Link to vault_outbox
    cooling_ledger_ref: str | None = None  # Link to cooling ledger

    # ── Hashes ──
    manifest_hash: str = ""  # SHA-256 of frozen session manifest
    final_artifact_hash: str = ""  # SHA-256 of all artifacts
    context_hash: str = ""  # SHA-256 of final context

    # ── Analysis ──
    rsi_entropy: float = 0.0  # RSI / entropy measurement
    cooling_analysis: str = ""  # Cooling analysis summary

    # ── Timing ──
    session_started_at: str = ""
    session_closed_at: str = ""

    # ── Receipt ──
    receipt_signed_by: str = ""  # Service signer or F13 key

    # ── Writing ──
    written_to_supabase: bool = False
    outbox_appended: bool = False
    chain_head_verified: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "closure_state": self.closure_state.value,
            "receipt_class": self.receipt_class.value,
            "outbox_event_id": self.outbox_event_id,
            "cooling_ledger_ref": self.cooling_ledger_ref,
            "manifest_hash": self.manifest_hash,
            "final_artifact_hash": self.final_artifact_hash,
            "context_hash": self.context_hash,
            "rsi_entropy": self.rsi_entropy,
            "cooling_analysis": self.cooling_analysis,
            "session_started_at": self.session_started_at,
            "session_closed_at": self.session_closed_at,
            "receipt_signed_by": self.receipt_signed_by,
            "written_to_supabase": self.written_to_supabase,
            "outbox_appended": self.outbox_appended,
            "chain_head_verified": self.chain_head_verified,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# OUTBOX CONSUMER — processes outbox entries toward VAULT999
# ═══════════════════════════════════════════════════════════════════════════════


class VaultOutboxConsumer:
    """
    Consumes vault_outbox entries and writes them to VAULT999.

    This is the ONLY component that calls VAULT append.
    No session shutdown hook calls VAULT directly.
    """

    def __init__(
        self,
        outbox: VaultOutbox,
        vault_writer: object | None = None,
        cooling_ledger: object | None = None,
    ):
        self.outbox = outbox
        self.vault_writer = vault_writer  # VAULT999 writer interface
        self.cooling_ledger = cooling_ledger

    def process_next(self) -> str | None:
        """
        Process the next PENDING outbox entry.

        Returns: event_id if processed, None if nothing pending.

        Flow:
          1. Claim next PENDING entry
          2. Validate required_capability against available credentials
          3. Write to VAULT999 via vault_writer
          4. Mark APPENDED with seal_id and receipt hash
          5. Verify chain head
          6. Mark VERIFIED
          7. Write cooling ledger reference
        """
        entry = self.outbox.claim_next()
        if not entry:
            return None

        try:
            # Step 3: Write to VAULT999
            if not self.vault_writer:
                self.outbox.mark_failed(entry.event_id, "No vault_writer configured")
                return entry.event_id

            result = self._write_to_vault(entry)
            if not result:
                self.outbox.mark_failed(entry.event_id, "VAULT write returned no result")
                return entry.event_id

            seal_id, receipt_hash = result
            self.outbox.mark_appended(entry.event_id, seal_id, receipt_hash)

            # Step 5: Verify chain head
            chain_head = self._verify_chain_head()
            if chain_head:
                self.outbox.mark_verified(entry.event_id, chain_head)

            # Step 7: Cooling ledger
            if self.cooling_ledger:
                self._write_cooling_ledger(entry, seal_id)

            logger.info(f"VaultOutboxConsumer: processed {entry.event_id} → VAULT seal {seal_id}")
            return entry.event_id

        except Exception as e:
            self.outbox.mark_failed(entry.event_id, str(e))
            return entry.event_id

    def _write_to_vault(self, entry: VaultOutboxEntry) -> tuple[str, str] | None:
        """Write the entry's payload to VAULT999. Abstract — caller provides vault_writer."""
        if hasattr(self.vault_writer, "append"):
            return self.vault_writer.append(
                payload_hash=entry.payload_hash,
                receipt_class=entry.receipt_class.value,
                idempotency_key=entry.idempotency_key,
            )
        return None

    def _verify_chain_head(self) -> str | None:
        """Verify VAULT999 chain head integrity."""
        if hasattr(self.vault_writer, "verify_chain_head"):
            return self.vault_writer.verify_chain_head()
        return None

    def _write_cooling_ledger(self, entry: VaultOutboxEntry, seal_id: str) -> None:
        """Write receipt reference to cooling ledger."""
        if hasattr(self.cooling_ledger, "write"):
            self.cooling_ledger.write(
                {
                    "event_id": entry.event_id,
                    "session_id": entry.session_id,
                    "receipt_class": entry.receipt_class.value,
                    "seal_id": seal_id,
                    "created_at": entry.created_at,
                    "type": "vault_outbox_receipt",
                }
            )
