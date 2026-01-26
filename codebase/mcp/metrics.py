"""
arifOS Metrics Module (v50.5.17)
Constitutional Metrics for MCP Trinity Tools

Implements Prometheus-compatible metrics for:
- Request counts (per tool, per verdict)
- Latency histograms
- Floor violations
- Rate limit hits
- Session tracking

Constitutional Floor: F8 (Tri-Witness) - metrics provide evidence

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import time
import logging
from dataclasses import dataclass, field
from typing import Dict, Optional, List
from collections import defaultdict
from contextlib import contextmanager
import threading

logger = logging.getLogger(__name__)

# =============================================================================
# METRIC TYPES
# =============================================================================

@dataclass
class Counter:
    """Simple counter metric."""
    name: str
    help: str
    labels: List[str] = field(default_factory=list)
    _values: Dict[tuple, float] = field(default_factory=lambda: defaultdict(float))
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def inc(self, labels: Optional[Dict[str, str]] = None, value: float = 1.0):
        """Increment counter."""
        key = tuple(sorted((labels or {}).items()))
        with self._lock:
            self._values[key] += value

    def get(self, labels: Optional[Dict[str, str]] = None) -> float:
        """Get counter value."""
        key = tuple(sorted((labels or {}).items()))
        with self._lock:
            return self._values[key]

    def reset(self):
        """Reset all values."""
        with self._lock:
            self._values.clear()


@dataclass
class Histogram:
    """Simple histogram metric with predefined buckets."""
    name: str
    help: str
    labels: List[str] = field(default_factory=list)
    buckets: List[float] = field(default_factory=lambda: [0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0])
    _counts: Dict[tuple, Dict[str, float]] = field(default_factory=lambda: defaultdict(lambda: defaultdict(float)))
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def observe(self, value: float, labels: Optional[Dict[str, str]] = None):
        """Record an observation."""
        key = tuple(sorted((labels or {}).items()))
        with self._lock:
            data = self._counts[key]
            data["count"] += 1
            data["sum"] += value
            for bucket in self.buckets:
                if value <= bucket:
                    data[f"le_{bucket}"] += 1
            data["le_+Inf"] += 1

    def get_percentile(self, percentile: float, labels: Optional[Dict[str, str]] = None) -> float:
        """Get approximate percentile value."""
        key = tuple(sorted((labels or {}).items()))
        with self._lock:
            data = self._counts[key]
            total = data.get("count", 0)
            if total == 0:
                return 0.0
            target = total * percentile
            cumulative = 0
            prev_bucket = 0.0
            for bucket in self.buckets:
                bucket_count = data.get(f"le_{bucket}", 0)
                if cumulative + bucket_count >= target:
                    # Linear interpolation
                    fraction = (target - cumulative) / max(bucket_count, 1)
                    return prev_bucket + fraction * (bucket - prev_bucket)
                cumulative = bucket_count
                prev_bucket = bucket
            return self.buckets[-1]

    def reset(self):
        """Reset all values."""
        with self._lock:
            self._counts.clear()


@dataclass
class Gauge:
    """Simple gauge metric."""
    name: str
    help: str
    labels: List[str] = field(default_factory=list)
    _values: Dict[tuple, float] = field(default_factory=lambda: defaultdict(float))
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def set(self, value: float, labels: Optional[Dict[str, str]] = None):
        """Set gauge value."""
        key = tuple(sorted((labels or {}).items()))
        with self._lock:
            self._values[key] = value

    def inc(self, labels: Optional[Dict[str, str]] = None, value: float = 1.0):
        """Increment gauge."""
        key = tuple(sorted((labels or {}).items()))
        with self._lock:
            self._values[key] += value

    def dec(self, labels: Optional[Dict[str, str]] = None, value: float = 1.0):
        """Decrement gauge."""
        key = tuple(sorted((labels or {}).items()))
        with self._lock:
            self._values[key] -= value

    def get(self, labels: Optional[Dict[str, str]] = None) -> float:
        """Get gauge value."""
        key = tuple(sorted((labels or {}).items()))
        with self._lock:
            return self._values[key]

    def reset(self):
        """Reset all values."""
        with self._lock:
            self._values.clear()


# =============================================================================
# ARIFOS METRICS
# =============================================================================

class ArifOSMetrics:
    """
    Constitutional Metrics Collector for arifOS.

    Provides Prometheus-compatible metrics for:
    - Tool invocations (requests_total)
    - Verdict distribution (verdicts_total)
    - Request latency (request_duration_seconds)
    - Floor violations (floor_violations_total)
    - Rate limit events (rate_limit_hits_total)
    - Active sessions (active_sessions)

    Usage:
        metrics = get_metrics()
        with metrics.track_request("agi_genius"):
            result = await mcp_agi_genius(...)
        metrics.record_verdict("agi_genius", result.get("verdict", "UNKNOWN"))
    """

    def __init__(self):
        # Request counter
        self.requests_total = Counter(
            name="arifos_requests_total",
            help="Total number of MCP tool requests",
            labels=["tool", "status"]
        )

        # Verdict counter
        self.verdicts_total = Counter(
            name="arifos_verdicts_total",
            help="Total verdicts by type",
            labels=["tool", "verdict"]
        )

        # Latency histogram
        self.request_duration = Histogram(
            name="arifos_request_duration_seconds",
            help="Request duration in seconds",
            labels=["tool"],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )

        # Floor violation counter
        self.floor_violations = Counter(
            name="arifos_floor_violations_total",
            help="Total floor violations",
            labels=["floor", "tool"]
        )

        # Rate limit hits
        self.rate_limit_hits = Counter(
            name="arifos_rate_limit_hits_total",
            help="Total rate limit hits",
            labels=["tool", "limit_type"]
        )

        # Active sessions gauge
        self.active_sessions = Gauge(
            name="arifos_active_sessions",
            help="Number of active sessions"
        )

        # Ledger entries
        self.ledger_entries = Counter(
            name="arifos_ledger_entries_total",
            help="Total ledger entries created",
            labels=["verdict"]
        )

        logger.info("ArifOSMetrics initialized")

    @contextmanager
    def track_request(self, tool_name: str):
        """
        Context manager to track request duration and count.

        Usage:
            with metrics.track_request("agi_genius"):
                result = await mcp_agi_genius(...)
        """
        start_time = time.time()
        status = "success"
        try:
            yield
        except Exception:
            status = "error"
            raise
        finally:
            duration = time.time() - start_time
            self.requests_total.inc({"tool": tool_name, "status": status})
            self.request_duration.observe(duration, {"tool": tool_name})

    def record_verdict(self, tool_name: str, verdict: str):
        """Record a verdict for a tool."""
        self.verdicts_total.inc({"tool": tool_name, "verdict": verdict})

    def record_floor_violation(self, floor: str, tool_name: str):
        """Record a floor violation."""
        self.floor_violations.inc({"floor": floor, "tool": tool_name})
        logger.warning(f"Floor violation recorded: {floor} in {tool_name}")

    def record_rate_limit_hit(self, tool_name: str, limit_type: str):
        """Record a rate limit hit."""
        self.rate_limit_hits.inc({"tool": tool_name, "limit_type": limit_type})

    def record_ledger_entry(self, verdict: str):
        """Record a ledger entry creation."""
        self.ledger_entries.inc({"verdict": verdict})

    def session_started(self):
        """Increment active session count."""
        self.active_sessions.inc()

    def session_ended(self):
        """Decrement active session count."""
        self.active_sessions.dec()

    def get_prometheus_output(self) -> str:
        """
        Generate Prometheus-compatible metrics output.

        Returns:
            String in Prometheus exposition format
        """
        lines = []

        # requests_total
        lines.append(f"# HELP {self.requests_total.name} {self.requests_total.help}")
        lines.append(f"# TYPE {self.requests_total.name} counter")
        for labels, value in self.requests_total._values.items():
            label_str = ",".join(f'{k}="{v}"' for k, v in labels)
            lines.append(f"{self.requests_total.name}{{{label_str}}} {value}")

        # verdicts_total
        lines.append(f"# HELP {self.verdicts_total.name} {self.verdicts_total.help}")
        lines.append(f"# TYPE {self.verdicts_total.name} counter")
        for labels, value in self.verdicts_total._values.items():
            label_str = ",".join(f'{k}="{v}"' for k, v in labels)
            lines.append(f"{self.verdicts_total.name}{{{label_str}}} {value}")

        # floor_violations_total
        lines.append(f"# HELP {self.floor_violations.name} {self.floor_violations.help}")
        lines.append(f"# TYPE {self.floor_violations.name} counter")
        for labels, value in self.floor_violations._values.items():
            label_str = ",".join(f'{k}="{v}"' for k, v in labels)
            lines.append(f"{self.floor_violations.name}{{{label_str}}} {value}")

        # rate_limit_hits_total
        lines.append(f"# HELP {self.rate_limit_hits.name} {self.rate_limit_hits.help}")
        lines.append(f"# TYPE {self.rate_limit_hits.name} counter")
        for labels, value in self.rate_limit_hits._values.items():
            label_str = ",".join(f'{k}="{v}"' for k, v in labels)
            lines.append(f"{self.rate_limit_hits.name}{{{label_str}}} {value}")

        # request_duration_seconds (histogram)
        lines.append(f"# HELP {self.request_duration.name} {self.request_duration.help}")
        lines.append(f"# TYPE {self.request_duration.name} histogram")
        for labels, data in self.request_duration._counts.items():
            label_str = ",".join(f'{k}="{v}"' for k, v in labels)
            for bucket in self.request_duration.buckets:
                le_key = f"le_{bucket}"
                lines.append(f'{self.request_duration.name}_bucket{{{label_str},le="{bucket}"}} {data.get(le_key, 0)}')
            lines.append(f'{self.request_duration.name}_bucket{{{label_str},le="+Inf"}} {data.get("le_+Inf", 0)}')
            lines.append(f'{self.request_duration.name}_sum{{{label_str}}} {data.get("sum", 0)}')
            lines.append(f'{self.request_duration.name}_count{{{label_str}}} {data.get("count", 0)}')

        # active_sessions (gauge)
        lines.append(f"# HELP {self.active_sessions.name} {self.active_sessions.help}")
        lines.append(f"# TYPE {self.active_sessions.name} gauge")
        for labels, value in self.active_sessions._values.items():
            label_str = ",".join(f'{k}="{v}"' for k, v in labels) if labels else ""
            if label_str:
                lines.append(f"{self.active_sessions.name}{{{label_str}}} {value}")
            else:
                lines.append(f"{self.active_sessions.name} {value}")

        # ledger_entries_total
        lines.append(f"# HELP {self.ledger_entries.name} {self.ledger_entries.help}")
        lines.append(f"# TYPE {self.ledger_entries.name} counter")
        for labels, value in self.ledger_entries._values.items():
            label_str = ",".join(f'{k}="{v}"' for k, v in labels)
            lines.append(f"{self.ledger_entries.name}{{{label_str}}} {value}")

        return "\n".join(lines)

    def get_stats(self) -> Dict:
        """Get metrics summary as dictionary."""
        return {
            "requests": dict(self.requests_total._values),
            "verdicts": dict(self.verdicts_total._values),
            "floor_violations": dict(self.floor_violations._values),
            "rate_limit_hits": dict(self.rate_limit_hits._values),
            "active_sessions": self.active_sessions.get(),
            "p99_latency": {
                tool: self.request_duration.get_percentile(0.99, {"tool": tool})
                for tool in ["init_000", "agi_genius", "asi_act", "apex_judge", "vault_999"]
            }
        }

    def reset_all(self):
        """Reset all metrics (for testing)."""
        self.requests_total.reset()
        self.verdicts_total.reset()
        self.request_duration.reset()
        self.floor_violations.reset()
        self.rate_limit_hits.reset()
        self.active_sessions.reset()
        self.ledger_entries.reset()


# =============================================================================
# SINGLETON
# =============================================================================

_metrics: Optional[ArifOSMetrics] = None


def get_metrics() -> ArifOSMetrics:
    """Get the singleton metrics instance."""
    global _metrics
    if _metrics is None:
        _metrics = ArifOSMetrics()
    return _metrics


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "ArifOSMetrics",
    "get_metrics",
    "Counter",
    "Histogram",
    "Gauge",
]
