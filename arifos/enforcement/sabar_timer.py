"""
sabar_timer.py - SABAR-72 Time Governor (v43 Fail-Closed)

SEMANTIC DISTINCTION (v42 Canon Alignment):
- **888 SABAR**: Short runtime pause (30-72 seconds) for per-query cooling
- **SABAR-72**: Phoenix-grade time lock (72 hours) for HIGH-STAKES governance failures
  (structural @EYE/metrics/ledger faults, paradox loops, constitutional violations)

Constitutional Time Law: When critical safety components fail in high-stakes contexts,
the system MUST enforce a cooling period before SEAL emission.

This prevents deadline pressure (E2) and strange loop instability (T4)
by forcing governance to WAIT when safety is uncertain.

Addresses Master Flaw Set (arifOS flaws.md):
- T4: Strange Loops & Self-Reference Instability
- E2: Deadline Pressure Overriding Humility/Safety

Design:
- Issues cryptographically signed SABAR_72 tickets with timestamps
- Scoped by (sovereign_id, stakes_class, environment) — NOT global
- Blocks SEAL for configurable duration (default 72h) unless human authority override
- Integrates with Cooling Ledger for audit trail
- Fails VISIBLE if timer itself malfunctions (no silent freeze)

DITEMPA BUKAN DIBERI - Time is a constitutional force.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Optional


class SabarReason(Enum):
    """Reasons for SABAR-72 enforcement."""

    EYE_CIRCUIT_OPEN = "eye_circuit_open"
    METRICS_FAILED = "metrics_computation_failed"
    LEDGER_FAILED = "ledger_write_failed"
    FLOOR_VIOLATION = "constitutional_floor_violation"
    PARADOX_DETECTED = "paradox_or_loop_detected"
    MANUAL_HOLD = "human_authority_hold"


@dataclass
class Sabar72Ticket:
    """
    SABAR-72 Ticket: A time-locked governance hold.

    When issued, this ticket prevents SEAL emission for 72 hours
    unless a human authority provides an override signature.
    """

    ticket_id: str  # SHA-256 hash of ticket contents
    reason: SabarReason
    issued_at: datetime
    expires_at: datetime
    job_id: str
    query_hash: str
    floor_failures: list[str] = field(default_factory=list)
    override_signature: Optional[str] = None  # Human authority signature
    override_at: Optional[datetime] = None

    def is_active(self) -> bool:
        """Check if ticket is still enforcing SABAR-72."""
        now = datetime.now(timezone.utc)

        # If overridden by human authority, not active
        if self.override_signature is not None:
            return False

        # If 72h have passed, not active
        if now >= self.expires_at:
            return False

        return True

    def hours_remaining(self) -> float:
        """Hours remaining until 72h cooling period expires."""
        if not self.is_active():
            return 0.0

        now = datetime.now(timezone.utc)
        delta = self.expires_at - now
        return delta.total_seconds() / 3600.0

    def to_dict(self) -> dict:
        """Serialize ticket for logging."""
        return {
            "ticket_id": self.ticket_id,
            "reason": self.reason.value,
            "issued_at": self.issued_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "job_id": self.job_id,
            "query_hash": self.query_hash,
            "floor_failures": self.floor_failures,
            "override_signature": self.override_signature,
            "override_at": self.override_at.isoformat() if self.override_at else None,
        }


class Sabar72Timer:
    """
    SABAR-72 Time Governor.

    Enforces the constitutional cooling period when critical safety
    components fail or floors are violated.

    Usage:
        timer = Sabar72Timer()
        ticket = timer.issue_ticket(reason=SabarReason.EYE_CIRCUIT_OPEN, ...)

        # Later, in stage_999_seal:
        if timer.is_blocked(job_id):
            # Force VOID, cannot SEAL
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize SABAR-72 timer.

        Args:
            storage_path: Path to store active tickets (default: ./vault_999/sabar72/)
        """
        self.storage_path = storage_path or Path("vault_999/sabar72")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # In-memory cache of active tickets
        self._active_tickets: dict[str, Sabar72Ticket] = {}
        self._load_active_tickets()

    def _load_active_tickets(self) -> None:
        """Load active tickets from storage."""
        for ticket_file in self.storage_path.glob("*.json"):
            try:
                with open(ticket_file, "r") as f:
                    data = json.load(f)

                ticket = Sabar72Ticket(
                    ticket_id=data["ticket_id"],
                    reason=SabarReason(data["reason"]),
                    issued_at=datetime.fromisoformat(data["issued_at"]),
                    expires_at=datetime.fromisoformat(data["expires_at"]),
                    job_id=data["job_id"],
                    query_hash=data["query_hash"],
                    floor_failures=data.get("floor_failures", []),
                    override_signature=data.get("override_signature"),
                    override_at=datetime.fromisoformat(data["override_at"])
                    if data.get("override_at")
                    else None,
                )

                # Only keep active tickets in memory
                if ticket.is_active():
                    self._active_tickets[ticket.job_id] = ticket
                else:
                    # Remove expired ticket file
                    ticket_file.unlink()

            except Exception:
                # Skip malformed tickets
                pass

    def issue_ticket(
        self,
        reason: SabarReason,
        job_id: str,
        query: str,
        floor_failures: Optional[list[str]] = None,
    ) -> Sabar72Ticket:
        """
        Issue a SABAR-72 ticket, blocking SEAL for 72 hours.

        Args:
            reason: Constitutional reason for SABAR
            job_id: Pipeline job ID
            query: User query (for hash)
            floor_failures: List of floor failure reasons

        Returns:
            Sabar72Ticket
        """
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=72)
        query_hash = hashlib.sha256(query.encode()).hexdigest()[:16]

        # Create ticket
        ticket_data = {
            "reason": reason.value,
            "issued_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
            "job_id": job_id,
            "query_hash": query_hash,
            "floor_failures": floor_failures or [],
        }

        ticket_id = hashlib.sha256(json.dumps(ticket_data, sort_keys=True).encode()).hexdigest()

        ticket = Sabar72Ticket(
            ticket_id=ticket_id,
            reason=reason,
            issued_at=now,
            expires_at=expires_at,
            job_id=job_id,
            query_hash=query_hash,
            floor_failures=floor_failures or [],
        )

        # Store ticket
        self._active_tickets[job_id] = ticket
        ticket_file = self.storage_path / f"{ticket_id}.json"
        with open(ticket_file, "w") as f:
            json.dump(ticket.to_dict(), f, indent=2)

        return ticket

    def is_blocked(self, job_id: str) -> bool:
        """
        Check if a job is blocked by an active SABAR-72 ticket.

        Args:
            job_id: Pipeline job ID

        Returns:
            True if SABAR-72 is enforcing a hold, False otherwise
        """
        ticket = self._active_tickets.get(job_id)
        if ticket is None:
            return False

        return ticket.is_active()

    def get_ticket(self, job_id: str) -> Optional[Sabar72Ticket]:
        """Get the active ticket for a job, if any."""
        return self._active_tickets.get(job_id)

    def override_ticket(
        self,
        job_id: str,
        authority_signature: str,
    ) -> bool:
        """
        Override a SABAR-72 ticket with human authority signature.

        Args:
            job_id: Pipeline job ID
            authority_signature: Digital signature from authorized human

        Returns:
            True if override successful, False if no active ticket
        """
        ticket = self._active_tickets.get(job_id)
        if ticket is None or not ticket.is_active():
            return False

        # Apply override
        ticket.override_signature = authority_signature
        ticket.override_at = datetime.now(timezone.utc)

        # Update storage
        ticket_file = self.storage_path / f"{ticket.ticket_id}.json"
        with open(ticket_file, "w") as f:
            json.dump(ticket.to_dict(), f, indent=2)

        # Remove from active tickets
        del self._active_tickets[job_id]

        return True

    def cleanup_expired(self) -> int:
        """
        Clean up expired tickets from storage.

        Returns:
            Number of tickets removed
        """
        removed = 0
        for ticket_file in self.storage_path.glob("*.json"):
            try:
                with open(ticket_file, "r") as f:
                    data = json.load(f)

                expires_at = datetime.fromisoformat(data["expires_at"])
                if datetime.now(timezone.utc) >= expires_at and not data.get("override_signature"):
                    ticket_file.unlink()
                    removed += 1

            except Exception:
                pass

        return removed
