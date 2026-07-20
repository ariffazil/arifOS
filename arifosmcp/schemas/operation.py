"""
Session A — OperationEvent + ReceiptEvent Pydantic Schemas
═══════════════════════════════════════════════════════════

Durable event types for the federation's higher spine:
  session → actor → trace → operation → receipt → vault-candidate

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

# ── Operation Status ──────────────────────────────────────────────────────


class OperationStatus:
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"


# ── OperationEvent ────────────────────────────────────────────────────────


class OperationEvent(BaseModel):
    """Emitted for every meaningful action in arifOS."""

    op_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    actor_id: str | None = None
    session_id: str | None = None
    trace_id: str | None = None
    organ: str = "arifos"
    capability: str  # tool name or action class
    params: dict[str, Any] = Field(default_factory=dict)
    timestamp_start: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    timestamp_end: str | None = None
    status: str = OperationStatus.STARTED  # STARTED | SUCCESS | FAIL

    model_config = {"extra": "allow"}


# ── ReceiptEvent ──────────────────────────────────────────────────────────


class ReceiptEvent(BaseModel):
    """Emitted for every sealed or completed operation."""

    receipt_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    op_id: str  # Links to OperationEvent
    session_id: str | None = None
    trace_id: str | None = None
    organ: str = "arifos"
    result_summary: str = ""
    evidence_uri: str | None = None  # snapshot, artifact, etc.
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    signature: str | None = None  # Session E will sign
    vault_candidate: bool = False  # True for lineage-worthy operations

    model_config = {"extra": "allow"}


# ── Bus Replay Result ─────────────────────────────────────────────────────


class BusReplayResult(BaseModel):
    """Result of replaying the durable bus."""

    operations: list[dict[str, Any]] = Field(default_factory=list)
    receipts: list[dict[str, Any]] = Field(default_factory=list)
    total_ops: int = 0
    total_receipts: int = 0
    replay_ok: bool = True
    error: str | None = None
