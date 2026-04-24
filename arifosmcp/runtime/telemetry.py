"""
Telemetry — Prometheus Metrics Stub
════════════════════════════════════

Production-grade metrics for the arifOS canonical surface.
"""
from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

_METRICS_ENABLED = os.getenv("ARIFOS_METRICS_ENABLED", "true").lower() == "true"


class Telemetry:
    """
    Prometheus metrics stub for arifOS.

    Uses prometheus_client if available; otherwise logs metrics.
    """

    def __init__(self) -> None:
        self._registry: Any = None
        self._counters: dict[str, Any] = {}
        self._histograms: dict[str, Any] = {}
        self._gauges: dict[str, Any] = {}
        self._init()

    def _init(self) -> None:
        if not _METRICS_ENABLED:
            logger.info("[Telemetry] Metrics disabled")
            return
        try:
            from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
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

    def record_tool_call(self, tool: str, verdict: str, latency: float | None = None) -> None:
        if _METRICS_ENABLED and "tool_calls" in self._counters:
            self._counters["tool_calls"].labels(tool=tool, verdict=verdict).inc()
        if latency is not None and "tool_latency" in self._histograms:
            self._histograms["tool_latency"].labels(tool=tool).observe(latency)
        logger.debug(f"[Telemetry] tool_call tool={tool} verdict={verdict} latency={latency}")

    def record_floor_breach(self, floor: str, tool: str) -> None:
        if _METRICS_ENABLED and "floor_breaches" in self._counters:
            self._counters["floor_breaches"].labels(floor=floor, tool=tool).inc()
        logger.warning(f"[Telemetry] floor_breach floor={floor} tool={tool}")

    def set_active_sessions(self, count: int) -> None:
        if _METRICS_ENABLED and "active_sessions" in self._gauges:
            self._gauges["active_sessions"].set(count)

    def set_ledger_size(self, count: int) -> None:
        if _METRICS_ENABLED and "ledger_size" in self._gauges:
            self._gauges["ledger_size"].set(count)

    def get_registry(self) -> Any:
        return self._registry
