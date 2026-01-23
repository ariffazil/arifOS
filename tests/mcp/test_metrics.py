"""
Tests for arifOS Metrics Module (v50.5.17)

Validates:
- Counter, Histogram, Gauge metrics
- Prometheus output format
- Thread-safe operations
- Metrics singleton

Constitutional Floor: F8 (Tri-Witness) - metrics provide evidence

DITEMPA BUKAN DIBERI
"""

import pytest
import time
import threading
from arifos.mcp.metrics import (
    get_metrics,
    ArifOSMetrics,
    Counter,
    Histogram,
    Gauge,
)


class TestCounter:
    """Tests for Counter metric."""

    def test_counter_inc(self):
        """Counter increments correctly."""
        counter = Counter(name="test", help="Test counter")
        counter.inc({"label": "a"})
        assert counter.get({"label": "a"}) == 1.0

    def test_counter_inc_with_value(self):
        """Counter increments by specified value."""
        counter = Counter(name="test", help="Test counter")
        counter.inc({"label": "b"}, value=5.0)
        assert counter.get({"label": "b"}) == 5.0

    def test_counter_multiple_labels(self):
        """Counter tracks different label combinations separately."""
        counter = Counter(name="test", help="Test counter")
        counter.inc({"tool": "a", "status": "success"})
        counter.inc({"tool": "a", "status": "error"})
        counter.inc({"tool": "b", "status": "success"})

        assert counter.get({"tool": "a", "status": "success"}) == 1.0
        assert counter.get({"tool": "a", "status": "error"}) == 1.0
        assert counter.get({"tool": "b", "status": "success"}) == 1.0

    def test_counter_reset(self):
        """Counter resets all values."""
        counter = Counter(name="test", help="Test counter")
        counter.inc({"label": "x"})
        counter.reset()
        assert counter.get({"label": "x"}) == 0.0


class TestHistogram:
    """Tests for Histogram metric."""

    def test_histogram_observe(self):
        """Histogram observes values correctly."""
        hist = Histogram(name="test", help="Test histogram")
        hist.observe(0.1, {"tool": "test"})
        hist.observe(0.2, {"tool": "test"})
        hist.observe(0.3, {"tool": "test"})

        # Check that count is 3
        assert hist._counts[(("tool", "test"),)]["count"] == 3

    def test_histogram_sum(self):
        """Histogram tracks sum correctly."""
        hist = Histogram(name="test", help="Test histogram")
        hist.observe(1.0, {"tool": "test"})
        hist.observe(2.0, {"tool": "test"})
        hist.observe(3.0, {"tool": "test"})

        assert hist._counts[(("tool", "test"),)]["sum"] == 6.0

    def test_histogram_buckets(self):
        """Histogram populates buckets correctly."""
        hist = Histogram(
            name="test",
            help="Test histogram",
            buckets=[0.1, 0.5, 1.0]
        )
        hist.observe(0.05, {"tool": "test"})  # <= 0.1
        hist.observe(0.3, {"tool": "test"})   # <= 0.5
        hist.observe(0.8, {"tool": "test"})   # <= 1.0

        data = hist._counts[(("tool", "test"),)]
        assert data["le_0.1"] == 1  # 0.05
        assert data["le_0.5"] == 2  # 0.05 + 0.3
        assert data["le_1.0"] == 3  # 0.05 + 0.3 + 0.8

    def test_histogram_get_percentile(self):
        """Histogram calculates percentiles correctly."""
        hist = Histogram(
            name="test",
            help="Test histogram",
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
        )
        # Add several observations
        for _ in range(10):
            hist.observe(0.05, {"tool": "test"})  # <= 0.1
        for _ in range(30):
            hist.observe(0.3, {"tool": "test"})   # <= 0.5
        for _ in range(40):
            hist.observe(0.8, {"tool": "test"})   # <= 1.0
        for _ in range(20):
            hist.observe(1.5, {"tool": "test"})   # <= 2.0

        # p50 should be around 0.8 (50th percentile)
        p50 = hist.get_percentile(0.50, {"tool": "test"})
        assert 0.1 <= p50 <= 1.0

        # p99 should be near the top
        p99 = hist.get_percentile(0.99, {"tool": "test"})
        assert p99 >= 1.0

    def test_histogram_percentile_empty(self):
        """Histogram returns 0 for empty data."""
        hist = Histogram(name="test", help="Test histogram")
        p50 = hist.get_percentile(0.50, {"tool": "empty"})
        assert p50 == 0.0

    def test_histogram_percentile_exceeds_buckets(self):
        """Histogram handles values at the upper boundary."""
        hist = Histogram(
            name="test",
            help="Test histogram",
            buckets=[0.1, 0.5, 1.0]
        )
        # All values in highest bucket
        for _ in range(100):
            hist.observe(0.9, {"tool": "test"})

        # p99 should return the last bucket
        p99 = hist.get_percentile(0.99, {"tool": "test"})
        assert p99 <= 1.0

    def test_histogram_reset(self):
        """Histogram resets correctly."""
        hist = Histogram(name="test", help="Test histogram")
        hist.observe(0.5, {"tool": "test"})
        hist.reset()
        assert len(hist._counts) == 0


class TestGauge:
    """Tests for Gauge metric."""

    def test_gauge_set(self):
        """Gauge sets value correctly."""
        gauge = Gauge(name="test", help="Test gauge")
        gauge.set(42.0, {"label": "a"})
        assert gauge.get({"label": "a"}) == 42.0

    def test_gauge_inc_dec(self):
        """Gauge increments and decrements correctly."""
        gauge = Gauge(name="test", help="Test gauge")
        gauge.inc({"label": "b"})
        gauge.inc({"label": "b"})
        gauge.dec({"label": "b"})
        assert gauge.get({"label": "b"}) == 1.0


class TestArifOSMetrics:
    """Tests for ArifOSMetrics collector."""

    def setup_method(self):
        """Reset metrics before each test."""
        metrics = get_metrics()
        metrics.reset_all()

    def test_singleton(self):
        """get_metrics returns singleton instance."""
        m1 = get_metrics()
        m2 = get_metrics()
        assert m1 is m2

    def test_track_request(self):
        """track_request context manager records metrics."""
        metrics = get_metrics()

        with metrics.track_request("test_tool"):
            time.sleep(0.01)

        assert metrics.requests_total.get({"tool": "test_tool", "status": "success"}) == 1.0
        # Duration is recorded in request_duration histogram
        assert len(metrics.request_duration._counts) > 0

    def test_track_request_error(self):
        """track_request records errors correctly."""
        metrics = get_metrics()

        with pytest.raises(ValueError):
            with metrics.track_request("test_tool"):
                raise ValueError("Test error")

        assert metrics.requests_total.get({"tool": "test_tool", "status": "error"}) == 1.0

    def test_record_verdict(self):
        """record_verdict tracks verdicts."""
        metrics = get_metrics()
        metrics.record_verdict("agi_genius", "SEAL")
        metrics.record_verdict("agi_genius", "SEAL")
        metrics.record_verdict("agi_genius", "VOID")

        assert metrics.verdicts_total.get({"tool": "agi_genius", "verdict": "SEAL"}) == 2.0
        assert metrics.verdicts_total.get({"tool": "agi_genius", "verdict": "VOID"}) == 1.0

    def test_record_floor_violation(self):
        """record_floor_violation tracks violations."""
        metrics = get_metrics()
        metrics.record_floor_violation("F2_Truth", "agi_genius")
        metrics.record_floor_violation("F2_Truth", "agi_genius")

        assert metrics.floor_violations.get({"floor": "F2_Truth", "tool": "agi_genius"}) == 2.0

    def test_record_rate_limit_hit(self):
        """record_rate_limit_hit tracks rate limit events."""
        metrics = get_metrics()
        metrics.record_rate_limit_hit("000_init", "session")

        assert metrics.rate_limit_hits.get({"tool": "000_init", "limit_type": "session"}) == 1.0

    def test_session_tracking(self):
        """session_started/session_ended tracks active sessions."""
        metrics = get_metrics()
        metrics.session_started()
        metrics.session_started()
        assert metrics.active_sessions.get() == 2.0

        metrics.session_ended()
        assert metrics.active_sessions.get() == 1.0

    def test_prometheus_output(self):
        """get_prometheus_output generates valid format."""
        metrics = get_metrics()
        metrics.record_verdict("test", "SEAL")

        output = metrics.get_prometheus_output()

        assert "# HELP arifos_verdicts_total" in output
        assert "# TYPE arifos_verdicts_total counter" in output
        assert 'arifos_verdicts_total{' in output

    def test_prometheus_output_all_metric_types(self):
        """Prometheus output includes all metric types."""
        metrics = get_metrics()

        # Record various metrics to populate all types
        metrics.requests_total.inc({"tool": "test", "status": "success"})
        metrics.record_verdict("test", "SEAL")
        metrics.record_floor_violation("F2_Truth", "test")
        metrics.record_rate_limit_hit("test", "session")
        metrics.request_duration.observe(0.5, {"tool": "test"})
        metrics.session_started()
        metrics.record_ledger_entry("SEAL")

        output = metrics.get_prometheus_output()

        # Check all metric types are present
        assert "arifos_requests_total" in output
        assert "arifos_verdicts_total" in output
        assert "arifos_floor_violations_total" in output
        assert "arifos_rate_limit_hits_total" in output
        assert "arifos_request_duration_seconds" in output
        assert "arifos_active_sessions" in output
        assert "arifos_ledger_entries_total" in output

        # Check histogram format
        assert "_bucket{" in output
        assert "_sum{" in output
        assert "_count{" in output

    def test_prometheus_output_histogram_buckets(self):
        """Prometheus output includes all histogram buckets."""
        metrics = get_metrics()
        metrics.request_duration.observe(0.1, {"tool": "bucket_test"})

        output = metrics.get_prometheus_output()

        # Should have bucket entries
        assert 'le="0.01"' in output
        assert 'le="0.1"' in output
        assert 'le="+Inf"' in output

    def test_prometheus_output_gauge_without_labels(self):
        """Prometheus output handles gauge without labels."""
        metrics = get_metrics()
        metrics.session_started()

        output = metrics.get_prometheus_output()

        # Gauge should appear without labels
        assert "arifos_active_sessions" in output

    def test_get_stats(self):
        """get_stats returns dictionary summary."""
        metrics = get_metrics()
        metrics.record_verdict("test", "SEAL")

        stats = metrics.get_stats()

        assert "requests" in stats
        assert "verdicts" in stats
        assert "floor_violations" in stats
        assert "active_sessions" in stats
        assert "p99_latency" in stats

    def test_record_ledger_entry(self):
        """record_ledger_entry tracks ledger writes."""
        metrics = get_metrics()
        metrics.record_ledger_entry("SEAL")
        metrics.record_ledger_entry("SEAL")
        metrics.record_ledger_entry("SABAR")

        assert metrics.ledger_entries.get({"verdict": "SEAL"}) == 2.0
        assert metrics.ledger_entries.get({"verdict": "SABAR"}) == 1.0


class TestThreadSafety:
    """Tests for thread-safe metric operations."""

    def test_counter_thread_safe(self):
        """Counter is thread-safe under concurrent access."""
        counter = Counter(name="test", help="Test counter")

        def increment():
            for _ in range(100):
                counter.inc({"label": "concurrent"})

        threads = [threading.Thread(target=increment) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 10 threads * 100 increments = 1000
        assert counter.get({"label": "concurrent"}) == 1000.0

    def test_gauge_thread_safe(self):
        """Gauge is thread-safe under concurrent access."""
        gauge = Gauge(name="test", help="Test gauge")

        def inc_dec():
            for _ in range(100):
                gauge.inc({"label": "concurrent"})
            for _ in range(100):
                gauge.dec({"label": "concurrent"})

        threads = [threading.Thread(target=inc_dec) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All increments and decrements should cancel out
        assert gauge.get({"label": "concurrent"}) == 0.0
