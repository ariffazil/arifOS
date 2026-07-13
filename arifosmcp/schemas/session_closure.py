"""
session_closure.py — Session Closure Pipeline (D2)

═══════════════════════════════════════════════════════════
FORGED: 2026-07-13 — Arif's D2 directive
PURPOSE: Separate session closure into three distinct levels,
         decouple from VAULT999 availability via outbox pattern,
         and prevent ordinary session accounting from depending
         on sovereign signing.

THREE CLOSURE LEVELS:

  SESSION_OBSERVED
    Session existed but was not fully governed.
    Receipt signed by session service, NOT sovereign.
    Closure state: CLOSED_UNSEALED

  SESSION_CLOSED
    Governed session completed normally.
    Bound session capability signed the receipt.
    Closure state: CLOSED_PENDING_RECEIPT → CLOSED_SEALED

  SESSION_SOVEREIGN_SEALED
    Contains explicit sovereign approval or decision.
    Verified F13 key signed the receipt.
    Closure state: CLOSED_PENDING_RECEIPT → CLOSED_SEALED

SESSION-CLOSE PIPELINE:

  Session ending
    ↓
  Freeze session manifest
    ↓
  Compute outcome, artifact and context hashes
    ↓
  Run RSI / entropy / cooling analysis
    ↓
  Write operational state to Supabase
    ↓
  Create session-closure receipt
    ↓
  VAULT999 outbox ⇠ (NEVER direct vault call)
    ↓
  Transactional append via outbox consumer
    ↓
  Verify chain head
    ↓
  Mark session CLOSED_SEALED
    ↓
  Cooling ledger receives receipt reference

Never keep a session artificially active because VAULT is
unavailable. Close its operational authority, but mark
audit closure pending.

DITEMPA BUKAN DIBERI — Closure is forged, not given.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from .vault_outbox import (
    OutboxStatus,
    ReceiptClass,
    SessionClosureState,
    SessionClosure,
    VaultOutbox,
    VaultOutboxEntry,
    VaultOutboxConsumer,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION MANIFEST — frozen snapshot at closure time
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class SessionManifest:
    """
    Frozen snapshot of a session at closure time.

    Once frozen, this manifest is immutable. Its hash serves as
    the payload_hash for vault_outbox entries.
    """

    # ── Identity ──
    session_id: str
    actor_id: str
    identity_band: str  # OBSERVER | OPERATOR_CLAIMED | OPERATOR_SIGNED | SOVEREIGN

    # ── Session metadata ──
    started_at: str
    ended_at: str = ""
    duration_seconds: float = 0.0

    # ── Activity ──
    tool_calls: int = 0
    unique_tools: list[str] = field(default_factory=list)
    judge_verdicts: list[str] = field(default_factory=list)

    # ── Hashes ──
    artifact_hash: str = ""  # SHA-256 of all artifacts produced
    context_hash: str = ""  # SHA-256 of final context
    outcome_hash: str = ""  # SHA-256 of outcome summary

    # ── RSI / entropy ──
    rsi_entropy: float = 0.0
    cooling_analysis: str = ""

    # ── Binding ──
    manifest_hash: str = ""

    def freeze(self) -> None:
        """Freeze the manifest — compute timestamps and hashes."""
        started = datetime.fromisoformat(self.started_at) if self.started_at else datetime.now(UTC)
        self.ended_at = datetime.now(UTC).isoformat()
        self.duration_seconds = (datetime.now(UTC) - started).total_seconds()

        # Compute manifest hash
        canonical = {
            "session_id": self.session_id,
            "actor_id": self.actor_id,
            "identity_band": self.identity_band,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "tool_calls": self.tool_calls,
            "unique_tools": self.unique_tools,
            "judge_verdicts": self.judge_verdicts,
            "artifact_hash": self.artifact_hash,
            "context_hash": self.context_hash,
            "outcome_hash": self.outcome_hash,
        }
        h = hashlib.sha256(
            json.dumps(canonical, sort_keys=True).encode()
        ).hexdigest()
        self.manifest_hash = h[:32]

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "actor_id": self.actor_id,
            "identity_band": self.identity_band,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "duration_seconds": self.duration_seconds,
            "tool_calls": self.tool_calls,
            "unique_tools": self.unique_tools,
            "judge_verdicts": self.judge_verdicts,
            "artifact_hash": self.artifact_hash,
            "context_hash": self.context_hash,
            "outcome_hash": self.outcome_hash,
            "rsi_entropy": self.rsi_entropy,
            "cooling_analysis": self.cooling_analysis,
            "manifest_hash": self.manifest_hash,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# DETERMINE CLOSURE LEVEL — classification logic
# ═══════════════════════════════════════════════════════════════════════════════


def determine_closure_level(
    manifest: SessionManifest,
    *,
    has_sovereign_seal: bool = False,
    has_governance_action: bool = False,
) -> tuple[ReceiptClass, SessionClosureState]:
    """
    Determine the closure level based on session activity.

    Args:
        manifest: Frozen session manifest
        has_sovereign_seal: True if session contains F13-ratified seals
        has_governance_action: True if session used arif_judge or arif_seal

    Returns:
        (receipt_class, initial_closure_state)
    """
    if has_sovereign_seal:
        return (
            ReceiptClass.SESSION_SOVEREIGN_SEALED,
            SessionClosureState.CLOSING,
        )

    if has_governance_action:
        return (
            ReceiptClass.SESSION_CLOSED,
            SessionClosureState.CLOSING,
        )

    return (
        ReceiptClass.SESSION_OBSERVED,
        SessionClosureState.CLOSING,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SERVICE SIGNER — signs session receipts at different authority levels
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class ServiceSigner:
    """
    Signs session closure receipts.

    Three signer levels matching the three closure levels:

    SESSION_OBSERVED       → session_service_signer (no crypto required)
    SESSION_CLOSED         → bound_session_signer   (session capability)
    SESSION_SOVEREIGN_SEALED → f13_sovereign_signer  (verified F13 key)
    """

    session_service_signer: str = "session_service:v1"
    bound_session_signer: str = "session_bound:v1"
    f13_sovereign_signer: str = ""

    def sign(
        self, receipt_class: ReceiptClass, manifest_hash: str
    ) -> str:
        """
        Return the signer identity for this receipt class.

        In Phase 1, returns the signer name as a string.
        Phase 2+ will return an Ed25519 signature.
        """
        if receipt_class == ReceiptClass.SESSION_SOVEREIGN_SEALED:
            if not self.f13_sovereign_signer:
                logger.warning(
                    "F13 sovereign signer not configured — "
                    "falling back to bound_session_signer"
                )
                return f"{self.bound_session_signer}:{manifest_hash[:12]}"
            return f"{self.f13_sovereign_signer}:{manifest_hash[:12]}"

        if receipt_class == ReceiptClass.SESSION_CLOSED:
            return f"{self.bound_session_signer}:{manifest_hash[:12]}"

        return f"{self.session_service_signer}:{manifest_hash[:12]}"


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION CLOSURE MANAGER — orchestrates session end
# ═══════════════════════════════════════════════════════════════════════════════


class SessionClosureManager:
    """
    Orchestrates session closure from start to sealed receipt.

    FLOW:
      1. initiate_closure()   → CLOSING
      2. freeze_manifest()     → manifest hash computed
      3. write_supabase()      → operational state persisted
      4. enqueue_outbox()      → VAULT999 outbox entry (PENDING)
      5. finalise()            → CLOSED_PENDING_RECEIPT (if outbox needed)
                                or CLOSED_UNSEALED (if OBSERVED)
    """

    def __init__(
        self,
        outbox: VaultOutbox,
        signer: ServiceSigner | None = None,
        supabase_writer: object | None = None,
        cooling_ledger: object | None = None,
    ):
        self.outbox = outbox
        self.signer = signer or ServiceSigner()
        self.supabase_writer = supabase_writer
        self.cooling_ledger = cooling_ledger
        self._closure: SessionClosure | None = None
        self._manifest: SessionManifest | None = None

    def initiate_closure(
        self,
        session_id: str,
        identity_band: str = "OBSERVER",
        actor_id: str = "anonymous",
        *,
        has_sovereign_seal: bool = False,
        has_governance_action: bool = False,
    ) -> SessionClosure:
        """
        Step 1: Initiate session closure.

        Determines the closure level and sets state to CLOSING.
        This does NOT close the session yet — it begins the process.
        """
        receipt_class, closure_state = determine_closure_level(
            SessionManifest(
                session_id=session_id,
                actor_id=actor_id,
                identity_band=identity_band,
                started_at=datetime.now(UTC).isoformat(),
            ),
            has_sovereign_seal=has_sovereign_seal,
            has_governance_action=has_governance_action,
        )

        self._closure = SessionClosure(
            session_id=session_id,
            closure_state=SessionClosureState.CLOSING,
            receipt_class=receipt_class,
            session_started_at=datetime.now(UTC).isoformat(),
        )

        logger.info(
            f"SessionClosure: initiated for {session_id} "
            f"[{receipt_class.value}]"
        )
        return self._closure

    def freeze_manifest(
        self,
        manifest: SessionManifest,
    ) -> str:
        """
        Step 2: Freeze the session manifest.

        Returns the manifest_hash for downstream use.
        """
        manifest.freeze()
        self._manifest = manifest
        if self._closure:
            self._closure.manifest_hash = manifest.manifest_hash
            self._closure.context_hash = manifest.context_hash
            self._closure.final_artifact_hash = manifest.artifact_hash
            self._closure.rsi_entropy = manifest.rsi_entropy
            self._closure.cooling_analysis = manifest.cooling_analysis

        logger.info(
            f"SessionClosure: manifest frozen "
            f"(hash={manifest.manifest_hash[:16]}...)"
        )
        return manifest.manifest_hash

    def write_supabase(self) -> bool:
        """
        Step 3: Write operational state to Supabase.

        Returns True if successful (or no supabase_writer configured).
        Session closure proceeds regardless of Supabase availability.
        """
        if not self.supabase_writer:
            if self._closure:
                self._closure.written_to_supabase = False
            return True

        try:
            if hasattr(self.supabase_writer, "write_session_closure"):
                self.supabase_writer.write_session_closure(
                    self._closure.to_dict() if self._closure else {},
                    self._manifest.to_dict() if self._manifest else {},
                )
            if self._closure:
                self._closure.written_to_supabase = True
            logger.info("SessionClosure: Supabase write OK")
            return True
        except Exception as e:
            logger.warning(f"SessionClosure: Supabase write failed: {e}")
            if self._closure:
                self._closure.written_to_supabase = False
            return False

    def enqueue_outbox(self) -> VaultOutboxEntry | None:
        """
        Step 4: Enqueue the closure receipt to VAULT999 outbox.

        For SESSION_OBSERVED, this step is skipped (no VAULT needed).
        For SESSION_CLOSED and SESSION_SOVEREIGN_SEALED, an outbox
        entry is created.

        Returns the outbox entry, or None if no outbox needed.
        """
        if not self._closure or not self._manifest:
            logger.error("SessionClosure: cannot enqueue — no closure/manifest")
            return None

        # SESSION_OBSERVED does not need VAULT seal
        if self._closure.receipt_class == ReceiptClass.SESSION_OBSERVED:
            self._closure.closure_state = SessionClosureState.CLOSED_UNSEALED
            self._closure.receipt_signed_by = self.signer.sign(
                ReceiptClass.SESSION_OBSERVED,
                self._manifest.manifest_hash,
            )
            logger.info(
                f"SessionClosure: OBSERVED — no VAULT seal needed. "
                f"Signed by {self._closure.receipt_signed_by}"
            )
            return None

        # Determine required capability
        if self._closure.receipt_class == ReceiptClass.SESSION_SOVEREIGN_SEALED:
            required_capability = "vault.append.sovereign"
        else:
            required_capability = "vault.append.session_closure"

        # Enqueue to outbox
        entry = self.outbox.enqueue(
            session_id=self._manifest.session_id,
            receipt_class=self._closure.receipt_class,
            payload_hash=self._manifest.manifest_hash,
            required_capability=required_capability,
            idempotency_key=f"closure:{self._manifest.session_id}:{self._manifest.manifest_hash[:12]}",
        )

        self._closure.outbox_event_id = entry.event_id
        self._closure.closure_state = SessionClosureState.CLOSED_PENDING_RECEIPT
        self._closure.receipt_signed_by = self.signer.sign(
            self._closure.receipt_class,
            self._manifest.manifest_hash,
        )

        logger.info(
            f"SessionClosure: outbox enqueued {entry.event_id} "
            f"[{self._closure.receipt_class.value}] "
            f"for session {self._manifest.session_id}"
        )
        return entry

    def finalise(self) -> SessionClosure:
        """
        Step 5: Finalise closure.

        After enqueue_outbox, the session is operationally closed.
        Its state reflects whether VAULT seal is pending or not.

        The key invariant:
          Close operational authority IMMEDIATELY.
          Do NOT keep session alive waiting for VAULT.
        """
        if not self._closure:
            raise RuntimeError("Cannot finalise: closure not initiated")

        self._closure.session_closed_at = datetime.now(UTC).isoformat()

        if self._closure.closure_state == SessionClosureState.CLOSING:
            # No outbox was created (SESSION_OBSERVED fallback)
            self._closure.closure_state = SessionClosureState.CLOSED_UNSEALED

        logger.info(
            f"SessionClosure: finalised {self._closure.session_id} "
            f"[{self._closure.closure_state.value}]"
        )
        return self._closure

    def mark_sealed(
        self,
        vault_seal_id: str,
        vault_receipt_hash: str,
        chain_head_hash: str,
    ) -> SessionClosure:
        """
        Called by outbox consumer after successful VAULT append + verification.

        Transitions from CLOSED_PENDING_RECEIPT → CLOSED_SEALED.
        """
        if not self._closure:
            raise RuntimeError("Cannot mark sealed: no closure")

        if self._closure.closure_state != SessionClosureState.CLOSED_PENDING_RECEIPT:
            logger.warning(
                f"SessionClosure: marking sealed but state is "
                f"{self._closure.closure_state.value} (expected CLOSED_PENDING_RECEIPT)"
            )

        self._closure.closure_state = SessionClosureState.CLOSED_SEALED
        self._closure.outbox_appended = True

        if chain_head_hash:
            self._closure.chain_head_verified = True

        # Write to cooling ledger
        if self.cooling_ledger and hasattr(self.cooling_ledger, "write"):
            try:
                self.cooling_ledger.write(
                    {
                        "session_id": self._closure.session_id,
                        "receipt_class": self._closure.receipt_class.value,
                        "closure_state": self._closure.closure_state.value,
                        "vault_seal_id": vault_seal_id,
                        "receipt_hash": vault_receipt_hash,
                        "chain_head_hash": chain_head_hash,
                        "type": "session_closure_sealed",
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                )
                self._closure.cooling_ledger_ref = vault_seal_id
            except Exception as e:
                logger.warning(f"SessionClosure: cooling ledger write failed: {e}")

        logger.info(
            f"SessionClosure: SEALED {self._closure.session_id} "
            f"(vault={vault_seal_id}, chain={chain_head_hash[:16]}...)"
        )
        return self._closure

    @property
    def closure(self) -> SessionClosure | None:
        return self._closure

    @property
    def manifest(self) -> SessionManifest | None:
        return self._manifest
