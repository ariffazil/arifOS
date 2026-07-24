"""arifOS Observability — sovereign LLM telemetry backend.

Replaces Langfuse v4 SDK with local Postgres + optional MinIO blob store.
Drop-in for the Telemetry class in arifosmcp/runtime/telemetry.py.

Usage:
    OBSERVABILITY_BACKEND=arifos  # writes to local Postgres
    OBSERVABILITY_BACKEND=langfuse  # existing cloud path (default)
    OBSERVABILITY_BACKEND=dual  # both (migration safety)
"""

from __future__ import annotations

from .models import ObservationRecord, ObservationBatch
from .postgres_backend import PostgresBackend

__all__ = ["ObservationRecord", "ObservationBatch", "PostgresBackend"]
