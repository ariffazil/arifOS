"""Telemetry — Prometheus Metrics + Selectable Observability Backend.

Backend selection via OBSERVABILITY_BACKEND env var:
    langfuse  → Langfuse v4 Cloud (default, existing path)
    arifos    → Local Postgres (sovereign, no external dependency)
    dual      → Both (migration safety — write to both)

DITEMPA BUKAN DIBERI — observability is a constitutional function, not a SaaS.
"""

from __future__ import annotations

import hashlib
import logging
import os
from datetime import datetime, timezone
from typing import Any

from arifosmcp.runtime.observability import ObservationRecord

logger = logging.getLogger(__name__)

_METRICS_ENABLED = os.getenv("ARIFOS_METRICS_ENABLED", "true").lower() == "true"
_OBSERVABILITY_BACKEND = os.getenv("OBSERVABILITY_BACKEND", "langfuse").lower()

_lf_client: Any = None
_local_backend: Any = None
_nats_conn: Any = None
_nats_ready: bool = False


def _get_langfuse():
    """Return a sync REST emitter function for Langfuse v3 self-hosted.

    Langfuse v4 Python SDK uses OTLP export (/api/public/otel/v1/traces)
    which self-hosted Langfuse v3 does not expose. The REST ingestion
    endpoint (/api/public/ingestion) works on both cloud and self-hosted.
    """
    global _lf_client
    if _lf_client is not None:
        return _lf_client
    if _OBSERVABILITY_BACKEND == "arifos":
        return None
    try:
        import uuid
        from datetime import datetime, timezone

        import httpx

        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        base_url = (os.getenv("LANGFUSE_BASE_URL") or "https://jp.cloud.langfuse.com").rstrip("/")

        if not public_key or not secret_key:
            logger.warning("[Telemetry] LANGFUSE_PUBLIC_KEY or LANGFUSE_SECRET_KEY not set")
            return None

        def _emit(
            name: str,
            session_id: str | None,
            metadata: dict[str, Any] | None,
            tags: list[str] | None,
        ) -> None:
            try:
                ts = datetime.now(timezone.utc).isoformat()
                body: dict[str, Any] = {
                    "id": str(uuid.uuid4()),
                    "name": name,
                    "timestamp": ts,
                }
                if metadata:
                    body["metadata"] = metadata
                if session_id:
                    body["sessionId"] = session_id
                if tags:
                    body["tags"] = tags

                payload = {
                    "batch": [
                        {
                            "id": str(uuid.uuid4()),
                            "type": "trace-create",
                            "body": body,
                            "timestamp": ts,
                        }
                    ]
                }
                with httpx.Client(timeout=5.0) as client:
                    client.post(
                        f"{base_url}/api/public/ingestion",
                        json=payload,
                        auth=(public_key, secret_key),
                    )
            except Exception:
                pass  # never block the tool path

        _lf_client = _emit
        logger.info(f"[Telemetry] Langfuse REST tracer initialized — host={base_url}")
    except ImportError:
        logger.debug("[Telemetry] httpx not available for REST tracer")
    except Exception as e:
        logger.warning(f"[Telemetry] Langfuse init failed: {e}")
    return _lf_client


def _get_local_backend():
    """Get or create the local Postgres observability backend."""
    global _local_backend
    if _local_backend is not None:
        return _local_backend
    if _OBSERVABILITY_BACKEND not in ("arifos", "dual"):
        return None
    try:
        from arifosmcp.runtime.observability import PostgresBackend

        _local_backend = PostgresBackend()
        return _local_backend
    except ImportError as e:
        logger.debug(f"[Telemetry] Local backend not available: {e}")
    except Exception as e:
        logger.warning(f"[Telemetry] Local backend init failed: {e}")
    return None


def _get_nats():
    """Return a sync NATS publish function for Kabarkan streaming.

    Publishes JSON payloads to kabarkan.ingest.<type> via subprocess nats CLI.
    Fire-and-forget — never blocks the kernel tool path.
    nats-py v2 is async-only, so we use the CLI for sync publishing.
    """
    global _nats_conn, _nats_ready
    if _nats_ready:
        return _nats_conn
    try:
        import json as _json
        import subprocess as _sp

        def _publish(subject: str, payload: dict[str, Any]) -> None:
            try:
                _sp.run(
                    ["nats", "publish", subject, _json.dumps(payload, default=str)],
                    capture_output=True,
                    timeout=3,
                )
            except Exception:
                pass  # fire-and-forget

        _nats_conn = _publish
        _nats_ready = True
        logger.info("[Telemetry] NATS producer ready (nats CLI)")
        return _publish
    except Exception as e:
        logger.debug(f"[Telemetry] NATS init deferred: {e}")
    return None


_NATS_CONNECTION: Any = None


def _publish_nats(record: Any) -> None:
    """Fire-and-forget publish an observation to NATS JetStream.

    Falls back silently if NATS is unavailable — never blocks the kernel.
    """
    global _NATS_CONNECTION
    import json
    import threading

    # Lazy-init NATS in a background thread (first call only)
    if _NATS_CONNECTION is None:
        _NATS_CONNECTION = object()  # marker that we tried

        def _init_nats():
            global _NATS_CONNECTION
            try:
                import asyncio
                from nats import NATS as NatsClient

                nc = NatsClient()
                asyncio.run(nc.connect("nats://127.0.0.1:4222"))
                js = nc.jetstream()
                asyncio.run(
                    js.publish(
                        f"kabarkan.ingest.span.{record.trace_id}",
                        json.dumps(record.model_dump(mode="json"), default=str).encode(),
                    )
                )
                asyncio.run(nc.close())
            except Exception:
                pass

        threading.Thread(target=_init_nats, daemon=True).start()
        return

    try:
        import asyncio
        from nats import NATS as NatsClient

        nc = NatsClient()

        async def _pub():
            await nc.connect("nats://127.0.0.1:4222")
            js = nc.jetstream()
            await js.publish(
                f"kabarkan.ingest.span.{record.trace_id}",
                json.dumps(record.model_dump(mode="json"), default=str).encode(),
            )
            await nc.close()

        asyncio.run(_pub())
    except Exception:
        pass


def _hash_payload(data: Any) -> str:
    try:
        import json

        s = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(s.encode()).hexdigest()[:16]
    except Exception:
        return "unavailable"


def _redact(input_data: dict[str, Any]) -> dict[str, Any]:
    """Remove secrets, keys, and sensitive WELL data."""
    if input_data is None:
        return {}
    redact_keys = {
        "password",
        "secret",
        "token",
        "api_key",
        "apikey",
        "authorization",
        "private_key",
        "secret_key",
        "access_token",
        "refresh_token",
        "session_token",
        "bearer",
        "LANGFUSE_SECRET_KEY",
        "LANGFUSE_PUBLIC_KEY",
        "POSTGRES_PASSWORD",
        "DB_PASSWORD",
        "REDIS_PASSWORD",
        "NEXTAUTH_SECRET",
        "ENCRYPTION_KEY",
    }
    result = {}
    for k, v in input_data.items():
        k_lower = k.lower()
        if any(redact in k_lower for redact in redact_keys):
            result[k] = "[REDACTED]"
        elif isinstance(v, dict):
            result[k] = _redact(v)
        elif isinstance(v, list) and len(v) > 100:
            result[k] = f"[list:{len(v)} items]"
        elif isinstance(v, str) and len(v) > 1000:
            result[k] = v[:500] + "...[truncated]"
        else:
            result[k] = v
    return result


class Telemetry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self._registry: Any = None
        self._counters: dict[str, Any] = {}
        self._histograms: dict[str, Any] = {}
        self._gauges: dict[str, Any] = {}
        self._lf = None
        self._local = None
        self._init()
        self._initialized = True

    def _init(self) -> None:
        self._lf = _get_langfuse()
        self._local = _get_local_backend()

        if not _METRICS_ENABLED:
            logger.info("[Telemetry] Metrics disabled")
            return
        try:
            from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

            self._registry = CollectorRegistry()
            self._counters["tool_calls"] = Counter(
                "arifos_tool_calls_total",
                "Total tool calls",
                ["tool", "verdict"],
                registry=self._registry,
            )
            self._counters["floor_breaches"] = Counter(
                "arifos_floor_breaches_total",
                "Total constitutional floor breaches",
                ["floor", "tool"],
                registry=self._registry,
            )
            self._histograms["tool_latency"] = Histogram(
                "arifos_tool_latency_seconds",
                "Tool execution latency",
                ["tool"],
                registry=self._registry,
            )
            self._gauges["active_sessions"] = Gauge(
                "arifos_active_sessions",
                "Number of active sessions",
                registry=self._registry,
            )
            self._gauges["ledger_size"] = Gauge(
                "arifos_ledger_size",
                "Number of sealed vault entries",
                registry=self._registry,
            )
            logger.info("[Telemetry] Prometheus registry initialized")
        except ImportError:
            logger.warning("[Telemetry] prometheus_client not installed; logging only")

    def record_tool_call(
        self,
        tool: str,
        verdict: str,
        latency: float | None = None,
        session_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        delta_s: float = 0.0,
        input_data: dict[str, Any | None] | None = None,
        output_data: dict[str, Any] | None = None,
        actor_id: str | None = None,
        vault_receipt: str | None = None,
        reasons: list[str] | None = None,
        next_safe_action: str | None = None,
    ) -> None:
        if _METRICS_ENABLED and "tool_calls" in self._counters:
            self._counters["tool_calls"].labels(tool=tool, verdict=verdict).inc()
        if latency is not None and "tool_latency" in self._histograms:
            self._histograms["tool_latency"].labels(tool=tool).observe(latency)

        if self._lf:
            try:
                i_hash = _hash_payload(_redact(input_data)) if input_data else None
                o_hash = _hash_payload(output_data) if output_data else None
                trace_meta = {
                    "verdict": verdict,
                    "latency_ms": latency,
                    "delta_S": delta_s,
                    "actor_id": actor_id or "unknown",
                    "session_id": session_id or None,
                    "input_hash": i_hash,
                    "output_hash": o_hash,
                    "vault_receipt": vault_receipt,
                    "reasons": reasons or [],
                    "next_safe_action": next_safe_action,
                }
                if metadata:
                    trace_meta.update(metadata)
                self._lf(
                    name=f"arifOS::{tool}",
                    session_id=session_id,
                    metadata=_redact(trace_meta),
                    tags=[tool, "arifOS"],
                )
            except Exception as e:
                logger.debug(f"[Telemetry] trace emit failed: {e}")

        # ── Kabarkan NATS (fire-and-forget stream) ─────────────────────
        _nats = _get_nats()
        if _nats:
            try:
                i_h = _hash_payload(_redact(input_data)) if input_data else None
                o_h = _hash_payload(output_data) if output_data else None
                payload = {
                    "tool_name": tool,
                    "verdict_class": verdict.upper(),
                    "actor_id": actor_id or "unknown",
                    "session_id": session_id or None,
                    "latency_ms": latency,
                    "delta_s": delta_s,
                    "input_hash": i_h,
                    "output_hash": o_h,
                    "vault_receipt": vault_receipt,
                    "reasons": reasons or [],
                    "next_safe_action": next_safe_action,
                    "organ": "arifOS",
                }
                _nats(f"kabarkan.ingest.span.{tool}", payload)
            except Exception:
                pass

        # ── Local backend (Kabarkan Postgres) ──────────────────────────
        if self._local:
            try:
                input_hash = _hash_payload(_redact(input_data)) if input_data else None
                output_hash = _hash_payload(output_data) if output_data else None
                record = ObservationRecord(
                    session_id=session_id,
                    actor_id=actor_id or "unknown",
                    tool_name=tool,
                    verdict_class=verdict.upper(),
                    delta_s=delta_s,
                    reasons=reasons or [],
                    next_safe_action=next_safe_action,
                    input_hash=input_hash,
                    output_hash=output_hash,
                    vault_receipt=vault_receipt,
                    latency_ms=latency if latency else None,
                    metadata=metadata,
                )
                self._local.store(record)
                # Fire-and-forget NATS publish for downstream consumers
                _publish_nats(record)
            except Exception as e:
                logger.debug(f"[Telemetry] Local backend write failed: {e}")

        logger.debug(f"[Telemetry] tool_call tool={tool} verdict={verdict} latency={latency}")

    def record_floor_breach(self, floor: str, tool: str) -> None:
        if _METRICS_ENABLED and "floor_breaches" in self._counters:
            self._counters["floor_breaches"].labels(floor=floor, tool=tool).inc()
        logger.warning(f"[Telemetry] floor_breach floor={floor} tool={tool}")

    def flush(self) -> None:
        if self._lf:
            try:
                self._lf.flush()
            except Exception as e:
                logger.debug(f"[Telemetry] flush failed: {e}")


_telemetry: Telemetry | None = None


def get_telemetry() -> Telemetry:
    global _telemetry
    if _telemetry is None:
        _telemetry = Telemetry()
    return _telemetry


def trace_tool_call(
    tool_name: str,
    arguments: dict[str, Any],
    result: dict[str, Any],
    session_id: str | None,
    actor_id: str,
    latency_ms: float,
) -> None:
    """
    Primary entry point for Langfuse tracing of arifOS tool calls.

    Wraps a tool invocation with full metadata including:
    - session_id, actor_id, tool name
    - input_hash (redacted arguments)
    - output_hash (result)
    - status derived from result['status'] or result.get('verdict')
    - reasons[], next_safe_action
    - vault_receipt if present
    """
    status = (
        result.get("status")
        or result.get("verdict")
        or result.get("result", {}).get("status", "OK")
        or "OK"
    )
    reasons = result.get("reasons", []) or result.get("result", {}).get("reasons", [])
    next_action = result.get("next_safe_action") or result.get("result", {}).get("next_safe_action")
    vault_receipt = result.get("result", {}).get("entry_id") or result.get("vault_receipt") or None

    get_telemetry().record_tool_call(
        tool=tool_name,
        verdict=status,
        latency=latency_ms / 1000.0,
        session_id=session_id,
        actor_id=actor_id,
        input_data=arguments,
        output_data=result,
        reasons=reasons if isinstance(reasons, list) else [],
        next_safe_action=next_action,
        vault_receipt=vault_receipt,
        delta_s=0.0,
    )
