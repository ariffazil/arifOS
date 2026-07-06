"""
sesat_event.py — The Canonical SESAT Failure Object
====================================================

SESAT is the machine-readable self-failure signal for the arifOS federation.
Not a string. Not a log line. A structured object that travels across nodes,
carries repair routes, and blocks false success.

Grammar: WAJIB → HANTAR → SESAT → JALAN → BAIK → LANTAI → PARUT → TEBUS → SAKSI → LURUS

Forged: 2026-07-06 by FORGE (000Ω)
Source: /root/A-FORGE/forge_work/2026-07-06/SESAT_RESILIENCE_ZEN.md
DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
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


# MALU delta per failure code
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
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
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

    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Auto-compute malu_delta from failure code if not set
        if self.malu_delta == 0.0:
            self.malu_delta = MALU_DELTAS.get(self.failure_code, 0.05)
        # ORANGE+ always requires SAKSI
        if self.severity in (Severity.ORANGE, Severity.RED, Severity.BLACK):
            self.saksi_required = True
        # ORANGE+ is irreversible
        if self.severity in (Severity.RED, Severity.BLACK):
            self.reversible = False

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
) -> SesatEvent:
    """Convenience function to emit a SESAT event.

    WAJIB: call this on every failure. Never silently pass SESAT as LURUS.
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
    )
