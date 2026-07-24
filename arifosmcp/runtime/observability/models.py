"""Pydantic models for arifOS observability data contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _new_id() -> UUID:
    return uuid4()


class ObservationRecord(BaseModel):
    """Single tool-call observation — the atomic unit of arifOS telemetry.

    Maps 1:1 to Telemetry.record_tool_call() parameters.
    Stored as one row in observability_observations.
    """

    # Identity
    observation_id: UUID = Field(default_factory=_new_id)
    trace_id: UUID = Field(default_factory=_new_id)
    span_id: UUID = Field(default_factory=_new_id)
    parent_span_id: UUID | None = None

    # Context
    session_id: str | None = None
    actor_id: str = "unknown"
    tool_name: str = ""
    organ_id: str | None = None

    # Timing
    start_time: datetime = Field(default_factory=_now)
    end_time: datetime | None = None
    latency_ms: float | None = None

    # Verdict / governance
    verdict_class: str = "OK"  # SEAL | SABAR | HOLD | VOID | OK
    delta_s: float = 0.0
    reasons: list[str] = Field(default_factory=list)
    next_safe_action: str | None = None
    uncertainty_tag: str | None = None  # CLAIM | ESTIMATE | HYPOTHESIS | UNKNOWN

    # Evidence hashes (never store raw input/output — hashes only)
    input_hash: str | None = None
    output_hash: str | None = None
    vault_receipt: str | None = None

    # Cost attribution
    cost_usd: float | None = None
    model_name: str | None = None

    # Extensible metadata
    metadata: dict[str, Any] | None = None

    # Ingestion metadata
    created_at: datetime = Field(default_factory=_now)

    model_config = {"extra": "ignore", "arbitrary_types_allowed": False}


class ObservationBatch(BaseModel):
    """Batch of observations for the ingestion endpoint."""

    observations: list[ObservationRecord] = Field(default_factory=list)
    source: str = "arifos_kernel"  # arifos_kernel | aforge | honcho
    batch_id: UUID = Field(default_factory=_new_id)
    sent_at: datetime = Field(default_factory=_now)
