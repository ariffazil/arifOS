"""
arifosmcp/memory_engine.py
══════════════════════════════════════════

NOTE: MemoryEngine class is DEPRECATED as of 2026-05-11.
All memory functionality has been unified into:
  - arifosmcp/runtime/memory_store.py (canonical backend)
  - arifosmcp/memory/vector_memory_qdrant.py (vector operations)

The Langfuse tracing infrastructure (LangfuseTrace, LangfuseSpan,
get_langfuse_tracer) is NOT deprecated and remains the canonical async
tracer for arifOS tool observability.

DITEMPA BUKAN DIBERI -- Forged, Not Given
"""

from __future__ import annotations

import logging
import os
import uuid
from datetime import UTC, datetime
from typing import Any

import httpx

_tracer_logger = logging.getLogger("arifos.langfuse_tracer")

# ── Langfuse v4 Async Tracer ────────────────────────────────────────────────


class LangfuseSpan:
    """Returned by LangfuseTrace.trace(); supports .end() and .close()."""

    def __init__(
        self,
        tracer: LangfuseTrace,
        trace_id: str,
        observation_id: str | None = None,
    ):
        self.tracer = tracer
        self.trace_id = trace_id
        self.observation_id = observation_id

    async def end(self) -> None:
        """End the root trace observation (maps to Langfuse trace-update)."""
        if not self.tracer.enabled:
            return
        try:
            ts = datetime.now(UTC).isoformat()
            await self.tracer._ingest(
                [
                    {
                        "id": str(uuid.uuid4()),
                        "type": "observation-update",
                        "body": {
                            "id": self.observation_id or self.trace_id,
                            "traceId": self.trace_id,
                            "endTime": ts,
                        },
                        "timestamp": ts,
                    }
                ]
            )
        except Exception as e:
            _tracer_logger.debug("Trace end failed (non-fatal): %s", e)

    async def close(self) -> None:
        """Alias of end() for compatibility."""
        await self.end()

    async def span(
        self,
        name: str,
        input: Any = None,
        output: Any = None,
        metadata: dict[str, Any] | None = None,
    ) -> LangfuseSpan:
        """Create a child span observation."""
        if not self.tracer.enabled:
            return LangfuseSpan(self.tracer, self.trace_id)
        ts = datetime.now(UTC).isoformat()
        span_id = str(uuid.uuid4())
        body: dict[str, Any] = {
            "id": span_id,
            "traceId": self.trace_id,
            "name": name,
            "startTime": ts,
            "type": "span",
            "input": input,
            "metadata": metadata or {},
        }
        if self.observation_id:
            body["parentObservationId"] = self.observation_id
        if output is not None:
            body["output"] = output
        try:
            await self.tracer._ingest(
                [
                    {
                        "id": str(uuid.uuid4()),
                        "type": "span-create",
                        "body": body,
                        "timestamp": ts,
                    }
                ]
            )
        except Exception as e:
            _tracer_logger.debug("Span creation failed (non-fatal): %s", e)
        return LangfuseSpan(self.tracer, self.trace_id, span_id)


class LangfuseTrace:
    """Lightweight async Langfuse v4 REST ingester — fire-and-forget, non-blocking."""

    def __init__(self, base_url: str | None = None):
        self.base_url = (
            base_url or os.getenv("LANGFUSE_BASE_URL") or "https://jp.cloud.langfuse.com"
        ).rstrip("/")
        self.public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        self.secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        self.enabled = bool(self.public_key and self.secret_key)
        self._http = httpx.AsyncClient(timeout=15.0)
        if self.enabled:
            _tracer_logger.info(
                "LangfuseTrace enabled — host=%s key_prefix=%s...",
                self.base_url,
                self.public_key[:12] if self.public_key else "None",
            )
        else:
            _tracer_logger.warning(
                "LangfuseTrace disabled — LANGFUSE_PUBLIC_KEY or LANGFUSE_SECRET_KEY not set"
            )

    async def _ingest(self, batch: list[dict[str, Any]]) -> None:
        if not self.enabled:
            return
        try:
            # self.enabled guarantees public_key and secret_key are non-None
            await self._http.post(
                f"{self.base_url}/api/public/ingestion",
                json={"batch": batch},
                auth=(self.public_key, self.secret_key),  # type: ignore[arg-type]
            )
        except Exception as e:
            _tracer_logger.debug("Langfuse ingestion failed (non-fatal): %s", e)

    async def trace(
        self,
        name: str,
        session_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ) -> LangfuseSpan:
        """
        Emit a root trace observation (Langfuse v4 trace-create).
        Returns a LangfuseSpan with .end() / .close() for explicit termination.
        """
        ts = datetime.now(UTC).isoformat()
        trace_id = str(uuid.uuid4())
        if self.enabled:
            body: dict[str, Any] = {
                "id": trace_id,
                "name": name,
                "metadata": metadata or {},
                "timestamp": ts,
            }
            if session_id:
                body["sessionId"] = session_id
            if tags:
                body["tags"] = tags
            try:
                await self._ingest(
                    [
                        {
                            "id": str(uuid.uuid4()),
                            "type": "trace-create",  # Langfuse v4 discriminator
                            "body": body,
                            "timestamp": ts,
                        }
                    ]
                )
            except Exception as e:
                _tracer_logger.debug("Trace creation failed (non-fatal): %s", e)
        return LangfuseSpan(self, trace_id)

    async def close(self) -> None:
        await self._http.aclose()


_global_langfuse: LangfuseTrace | None = None


def get_langfuse_tracer() -> LangfuseTrace:
    """Factory: returns shared LangfuseTrace instance, reading env vars at call time."""
    global _global_langfuse
    if _global_langfuse is None:
        _global_langfuse = LangfuseTrace()
    return _global_langfuse


# ── Deprecated MemoryEngine — do not use ────────────────────────────────────

_deprecated_logger = logging.getLogger("memory_engine")
_deprecated_logger.warning(
    "MemoryEngine is deprecated. Use arifosmcp.runtime.memory_store instead."
)


class MemoryEngine:
    """Deprecated. Use arifosmcp.runtime.memory_store or vector_memory_qdrant."""

    def __init__(self, *args, **kwargs):
        _deprecated_logger.warning("MemoryEngine is deprecated. Use memory_store.store() instead.")

    async def store(self, *args, **kwargs) -> dict[str, Any]:
        raise RuntimeError("MemoryEngine is deprecated. Use arifosmcp.runtime.memory_store.store()")

    async def recall(self, *args, **kwargs) -> dict[str, Any]:
        raise RuntimeError(
            "MemoryEngine is deprecated. Use arifosmcp.runtime.memory_store.recall()"
        )

    async def search(self, *args, **kwargs) -> dict[str, Any]:
        raise RuntimeError(
            "MemoryEngine is deprecated. Use arifosmcp.runtime.memory_store.search()"
        )

    async def get_embedding(self, *args, **kwargs) -> list[float]:
        raise RuntimeError(
            "MemoryEngine is deprecated. Use vector_memory_qdrant._generate_embedding()"
        )
