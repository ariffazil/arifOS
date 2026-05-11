"""
Telemetry — Prometheus Metrics + Langfuse Traces (v4 SDK)
════════════════════════════════════════════════════════

Updated for Langfuse Python SDK v4:
- Uses get_client() singleton
- start_as_current_observation context manager (OTel-native)
- propagate_attributes for session/actor context
- automatic child span propagation
- flush on shutdown for short-lived processes
"""

from __future__ import annotations

import hashlib
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

_METRICS_ENABLED = os.getenv("ARIFOS_METRICS_ENABLED", "true").lower() == "true"

_lf_client: Any = None


def _get_langfuse():
    global _lf_client
    if _lf_client is not None:
        return _lf_client
    try:
        from langfuse import get_client as _gc

        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        host = os.getenv("LANGFUSE_BASE_URL", "https://jp.cloud.langfuse.com")
        if public_key and secret_key:
            _lf_client = _gc()
            logger.info(f"[Telemetry] Langfuse v4 initialized — host={host}")
        else:
            logger.warning(
                "[Telemetry] LANGFUSE_PUBLIC_KEY or LANGFUSE_SECRET_KEY not set"
            )
    except ImportError:
        logger.debug("[Telemetry] langfuse SDK not installed")
    except Exception as e:
        logger.warning(f"[Telemetry] Langfuse init failed: {e}")
    return _lf_client


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
        self._init()
        self._initialized = True

    def _init(self) -> None:
        self._lf = _get_langfuse()

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
                input_hash = _hash_payload(_redact(input_data)) if input_data else None
                output_hash = _hash_payload(output_data) if output_data else None
                span_meta = {
                    "verdict": verdict,
                    "latency_ms": latency,
                    "delta_S": delta_s,
                    "actor_id": actor_id or "unknown",
                    "session_id": session_id or None,
                    "input_hash": input_hash,
                    "output_hash": output_hash,
                    "vault_receipt": vault_receipt,
                    "reasons": reasons or [],
                    "next_safe_action": next_safe_action,
                }
                if metadata:
                    span_meta.update(metadata)
                with self._lf.start_as_current_observation(
                    as_type="span",
                    name=f"arifOS::{tool}",
                    metadata=_redact(span_meta),
                ) as span:
                    span.update(
                        input={"tool": tool, "actor": actor_id},
                        output={"verdict": verdict, "output_hash": output_hash},
                    )
            except Exception as e:
                logger.debug(f"[Telemetry] Langfuse span failed: {e}")

        logger.debug(
            f"[Telemetry] tool_call tool={tool} verdict={verdict} latency={latency}"
        )

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
    next_action = result.get("next_safe_action") or result.get("result", {}).get(
        "next_safe_action"
    )
    vault_receipt = (
        result.get("result", {}).get("entry_id") or result.get("vault_receipt") or None
    )

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
