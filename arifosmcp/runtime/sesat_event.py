"""
sesat_event.py — The Canonical SESAT Failure Object (WS8: Sesat/Malu Ledger Repair)
====================================================================================

SESAT is the machine-readable self-failure signal for the arifOS federation.
Not a string. Not a log line. A structured object that travels across nodes,
carries repair routes, and blocks false success.

WS8 (2026-07-12): Sesat fires on action-scope or substrate-scope failure ONLY.
Session-scope restriction NEVER produces sesat. Instead, emit YELLOW SessionNotice
with malu_delta=0. Historical sesat events marked with correction_status.

Grammar: WAJIB → HANTAR → SESAT → JALAN → BAIK → LANTAI → PARUT → TEBUS → SAKSI → LURUS

Forged: 2026-07-06 by FORGE (000Ω)
WS8 repaired: 2026-07-12 by OpenCode under F13 SOVEREIGN directive
Source: /root/A-FORGE/forge_work/2026-07-06/SESAT_RESILIENCE_ZEN.md
DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class Severity(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    ORANGE = "ORANGE"
    RED = "RED"
    BLACK = "BLACK"


class FailureCode(str, Enum):
    JALAN_PATH = "JALAN_PATH"  # Path/file not reachable
    JALAN_KUASA = "JALAN_KUASA"  # Authority violation
    JALAN_BENAR = "JALAN_BENAR"  # Truth/evidence failure
    JALAN_ALAT = "JALAN_ALAT"  # Tool failure (ghost tool, dispatch)
    JALAN_BENTUK = "JALAN_BENTUK"  # Schema/shape mismatch
    JALAN_KONTEKS = "JALAN_KONTEKS"  # Context loss or corruption
    JALAN_HANTAR = "JALAN_HANTAR"  # Transport/handoff failure
    JALAN_BUKTI = "JALAN_BUKTI"  # Evidence gap
    JALAN_ARAHAN = "JALAN_ARAHAN"  # Instruction ambiguity
    JALAN_SESI = "JALAN_SESI"  # Session limitation (WS8: informational, not failure)


class CorrectionStatus(str, Enum):
    """WS8: Correction status for historical sesat events.

    FALSE_POSITIVE_SESSION_SCOPE: Event was triggered by session-scope
        restriction only — not a real failure. effective_malu_delta should be 0.
    CORRECTED: Event was manually corrected.
    PENDING: Correction pending review.
    """

    FALSE_POSITIVE_SESSION_SCOPE = "FALSE_POSITIVE_SESSION_SCOPE"
    CORRECTED = "CORRECTED"
    PENDING = "PENDING"


# MALU delta per failure code
# WS8: JALAN_SESI has 0.0 — session restriction is NOT a failure
MALU_DELTAS: dict[FailureCode, float] = {
    FailureCode.JALAN_KUASA: 0.20,
    FailureCode.JALAN_BENAR: 0.15,
    FailureCode.JALAN_BUKTI: 0.10,
    FailureCode.JALAN_ALAT: 0.08,
    FailureCode.JALAN_HANTAR: 0.08,
    FailureCode.JALAN_PATH: 0.05,
    FailureCode.JALAN_BENTUK: 0.05,
    FailureCode.JALAN_KONTEKS: 0.05,
    FailureCode.JALAN_ARAHAN: 0.05,
    FailureCode.JALAN_SESI: 0.00,  # WS8: session limitation — ZERO malu
}


@dataclass
class BaikRoute:
    """Named repair route — how to fix this failure."""

    route: str
    owner: str
    max_retries: int = 1
    fallback_routes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "route": self.route,
            "owner": self.owner,
            "max_retries": self.max_retries,
            "fallback_routes": self.fallback_routes,
        }


@dataclass
class SesatEvent:
    """The canonical SESAT failure object. Machine-readable. Travels across nodes.

    WAJIB: every node must emit this on failure. Never silently pass SESAT as LURUS.
    """

    id: str = field(default_factory=lambda: f"sesat-{uuid.uuid4().hex[:12]}")
    source_node: str = ""
    source_surface: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    severity: Severity = Severity.YELLOW

    failure_code: FailureCode = FailureCode.JALAN_ALAT
    failed_claim: str = ""
    observed_reality: str = ""
    reversible: bool = True

    baik: BaikRoute = field(
        default_factory=lambda: BaikRoute(route="inspect_and_retry", owner="unknown")
    )
    lantai: list[str] = field(default_factory=lambda: ["F2", "F4"])

    evidence: dict[str, Any] = field(
        default_factory=lambda: {
            "sha256": None,
            "byte_length": None,
            "mime_type": None,
            "receipt_id": None,
            "witness_refs": [],
        }
    )

    blocked_actions: list[str] = field(default_factory=list)
    next_safe_action: str = "Inspect and classify failure"

    malu_delta: float = 0.0
    saksi_required: bool = False
    tebus_required: bool = True

    # ── WS8: Sesat/Malu Ledger Repair fields ──────────────────────────────
    session_restriction_only: bool = False
    """True when sesat fires for session-scope restriction only (WS8 fix).
    When True, effective_malu_delta should be 0 and this is a FALSE POSITIVE."""
    correction_status: str | None = None
    """Correction status for historical events. Set to
    'FALSE_POSITIVE_SESSION_SCOPE' for events that were session-only.
    None for current/proper events."""
    effective_malu_delta: float = 0.0
    """The malu_delta that SHOULD have been applied. For false positives
    (session_restriction_only=True), this is 0.0. For real failures,
    this equals malu_delta."""

    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Auto-compute malu_delta from failure code if not set
        if self.malu_delta == 0.0 and self.failure_code != FailureCode.JALAN_SESI:
            self.malu_delta = MALU_DELTAS.get(self.failure_code, 0.05)
        # ORANGE+ always requires SAKSI
        if self.severity in (Severity.ORANGE, Severity.RED, Severity.BLACK):
            self.saksi_required = True
        # ORANGE+ is irreversible
        if self.severity in (Severity.RED, Severity.BLACK):
            self.reversible = False
        # WS8: compute effective_malu_delta
        if self.session_restriction_only:
            self.effective_malu_delta = 0.0
            if self.correction_status is None:
                self.correction_status = "FALSE_POSITIVE_SESSION_SCOPE"
        else:
            self.effective_malu_delta = self.malu_delta

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source_node": self.source_node,
            "source_surface": self.source_surface,
            "timestamp": self.timestamp,
            "severity": self.severity.value,
            "failure_code": self.failure_code.value,
            "failed_claim": self.failed_claim,
            "observed_reality": self.observed_reality,
            "reversible": self.reversible,
            "baik": self.baik.to_dict(),
            "lantai": self.lantai,
            "evidence": self.evidence,
            "blocked_actions": self.blocked_actions,
            "next_safe_action": self.next_safe_action,
            "malu_delta": self.malu_delta,
            "saksi_required": self.saksi_required,
            "tebus_required": self.tebus_required,
            # WS8: new fields
            "session_restriction_only": self.session_restriction_only,
            "correction_status": self.correction_status,
            "effective_malu_delta": self.effective_malu_delta,
            "tags": self.tags,
        }

    def to_json(self, indent: int = 2) -> str:
        import json

        return json.dumps(self.to_dict(), indent=indent)


@dataclass
class SessionNotice:
    """WS8: Session Notice — informational event for session-scope restrictions.

    Unlike SesatEvent (which signals real failure), SessionNotice is emitted
    when a call was restricted by session scope (OBSERVE_ONLY, SABAR) but
    the underlying tool call succeeded. This is NOT a failure — it is an
    operational boundary.

    SessionNotice NEVER carries malu_delta. It is GREEN/YELLOW only.
    """

    id: str = field(default_factory=lambda: f"sn-{uuid.uuid4().hex[:12]}")
    source_node: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    severity: Severity = Severity.GREEN

    session_state: str = "OBSERVE_ONLY"
    action_verdict: str = ""
    tool_name: str = ""
    message: str = ""

    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source_node": self.source_node,
            "timestamp": self.timestamp,
            "severity": self.severity.value,
            "session_state": self.session_state,
            "action_verdict": self.action_verdict,
            "tool_name": self.tool_name,
            "message": self.message,
            "tags": self.tags,
        }

    def to_json(self, indent: int = 2) -> str:
        import json

        return json.dumps(self.to_dict(), indent=indent)


def emit_sesat(
    source_node: str,
    failure_code: str | FailureCode,
    failed_claim: str,
    observed_reality: str,
    severity: str | Severity = Severity.YELLOW,
    baik_route: str = "inspect_and_retry",
    baik_owner: str | None = None,
    lantai: list[str] | None = None,
    blocked_actions: list[str] | None = None,
    tags: list[str] | None = None,
    # WS8 parameters
    session_restriction_only: bool = False,
    correction_status: str | None = None,
) -> SesatEvent:
    """Convenience function to emit a SESAT event.

    WAJIB: call this on every failure. Never silently pass SESAT as LURUS.

    WS8 (2026-07-12): session_restriction_only and correction_status parameters
    enable repair of false-positive sesat events. When session_restriction_only=True,
    effective_malu_delta is forced to 0.0.
    """
    fc = failure_code if isinstance(failure_code, FailureCode) else FailureCode(failure_code)
    sev = severity if isinstance(severity, Severity) else Severity(severity)

    return SesatEvent(
        source_node=source_node,
        severity=sev,
        failure_code=fc,
        failed_claim=failed_claim,
        observed_reality=observed_reality,
        baik=BaikRoute(
            route=baik_route,
            owner=baik_owner or source_node,
        ),
        lantai=lantai or ["F2", "F4"],
        blocked_actions=blocked_actions or ["claim_success"],
        tags=tags or [],
        # WS8
        session_restriction_only=session_restriction_only,
        correction_status=correction_status,
    )


def emit_session_notice(
    source_node: str,
    session_state: str,
    tool_name: str = "",
    message: str = "",
    action_verdict: str = "",
    severity: str | Severity = Severity.GREEN,
    tags: list[str] | None = None,
) -> SessionNotice:
    """WS8: Emit a SessionNotice — informational, NOT a failure.

    Call this when a call was restricted by session scope but the
    underlying tool call succeeded. SessionNotice is GREEN/YELLOW only
    and NEVER carries malu_delta.
    """
    sev = severity if isinstance(severity, Severity) else Severity(severity)

    return SessionNotice(
        source_node=source_node,
        severity=sev,
        session_state=session_state,
        tool_name=tool_name,
        message=message,
        action_verdict=action_verdict,
        tags=tags or [],
    )
