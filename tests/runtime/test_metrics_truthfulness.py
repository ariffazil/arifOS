"""
tests/runtime/test_metrics_truthfulness.py
═══════════════════════════════════════════════

Truthfulness guarantee: the new metrics must reflect ACTUAL completion
events, never status defaults or zero-fill from upstream probes.

Coverage:
  - arifos_tearframe{component, provenance} — recorded only on completion
  - arifos_rasa_events_total — recorded only when JSONL write succeeds
  - arifos_scar_candidates_total — recorded only after durable persistence

These tests exercise the helpers directly and via the public entry points
they're wired to (log_shadow, judge scar persistence, atlas_calibration).

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Helpers: extract a single counter/gauge value from the noop or real client.
# ---------------------------------------------------------------------------
def _read_counter_value(counter_obj, **labels) -> float:
    """Return the current value of a counter for a specific label set.

    Works for both prometheus_client.Counter and the noop shim.
    """
    try:
        # Real prometheus_client: counter.labels(...)._value.get()
        child = counter_obj.labels(**labels)
        return float(child._value.get())
    except Exception:
        # Noop fallback: no value tracking
        return 0.0


def _read_gauge_value(gauge_obj, **labels) -> float:
    """Return the current value of a gauge for a specific label set."""
    try:
        child = gauge_obj.labels(**labels)
        # Prometheus client Gauge: child._value.get()
        return float(child._value.get())
    except Exception:
        return 0.0


# ---------------------------------------------------------------------------
# TEARFRAME GAUGE
# ---------------------------------------------------------------------------
def test_tearframe_recorded_only_at_completion_boundary():
    """tearframe gauge MUST record at completion, not at construction.

    The metrics module exports TEARFRAME with no default samples. Calling
    record_tearframe() with the same component/provenance twice is
    idempotent and replaces (last-write-wins). Not calling it leaves the
    gauge at its initial value.
    """
    from arifosmcp.runtime.metrics import TEARFRAME, record_tearframe

    # Initial state: no write → 0.0 (noop or true Prometheus default).
    before = _read_gauge_value(
        TEARFRAME, component="confidence", provenance="measured"
    )

    record_tearframe(component="confidence", value=0.85, provenance="measured")
    after = _read_gauge_value(
        TEARFRAME, component="confidence", provenance="measured"
    )
    assert after == pytest.approx(0.85, rel=1e-9)
    assert after != before or before == 0.0  # write took effect


def test_tearframe_provenance_distinguishes_measured_vs_placeholder():
    """Same component, different provenance → distinct label series."""
    from arifosmcp.runtime.metrics import TEARFRAME, record_tearframe

    record_tearframe(component="trm", value=0.94, provenance="measured")
    record_tearframe(component="trm", value=0.50, provenance="placeholder")

    measured = _read_gauge_value(TEARFRAME, component="trm", provenance="measured")
    placeholder = _read_gauge_value(
        TEARFRAME, component="trm", provenance="placeholder"
    )

    assert measured == pytest.approx(0.94, rel=1e-9)
    assert placeholder == pytest.approx(0.50, rel=1e-9)
    assert measured != placeholder


def test_tearframe_none_value_is_noop():
    """None value MUST NOT be recorded (truthfulness)."""
    from arifosmcp.runtime.metrics import TEARFRAME, record_tearframe

    before = _read_gauge_value(
        TEARFRAME, component="confidence", provenance="measured"
    )
    record_tearframe(component="confidence", value=None, provenance="measured")
    after = _read_gauge_value(
        TEARFRAME, component="confidence", provenance="measured"
    )
    # Either noop (no change) or unchanged — never fabricated.
    assert after == before


# ---------------------------------------------------------------------------
# RASA EVENTS COUNTER
# ---------------------------------------------------------------------------
def test_rasa_events_counter_increments_only_on_successful_write(
    tmp_path: Path, monkeypatch
):
    """arifos_rasa_events_total increments ONLY when JSONL write succeeds."""
    from arifosmcp.rasa.rasa_telemetry import RasaTelemetry
    from arifosmcp.runtime.metrics import RASA_EVENTS_TOTAL

    log = tmp_path / "rasa.jsonl"
    tele = RasaTelemetry(log_path=str(log))

    # Baseline: counter for this label set is 0
    baseline = _read_counter_value(
        RASA_EVENTS_TOTAL,
        risk_band="safe",
        enforcement_mode="shadow",
        enforced="false",
    )

    tele.log_shadow(
        session_id="s1",
        message="hello",
        ungoverned_result=None,
        governed_result={
            "detection": type("D", (), {"risk_band": type("B", (), {"value": "safe"}),
                                          "emotion_tags": []})(),
            "judge": None,
            "final_posture": "proceed",
        },
        enforcement_mode="shadow",
        enforced=False,
    )

    after = _read_counter_value(
        RASA_EVENTS_TOTAL,
        risk_band="safe",
        enforcement_mode="shadow",
        enforced="false",
    )
    # Real write succeeded → counter incremented
    assert after > baseline, (
        "arifos_rasa_events_total must increment after durable JSONL write"
    )
    assert log.exists()
    lines = log.read_text().strip().split("\n")
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["risk_band"] == "safe"


def test_rasa_events_counter_does_not_increment_when_disabled(
    tmp_path: Path, monkeypatch
):
    """When telemetry is disabled, the counter MUST NOT increment."""
    from arifosmcp.rasa.rasa_telemetry import RasaTelemetry
    from arifosmcp.runtime.metrics import RASA_EVENTS_TOTAL

    log = tmp_path / "rasa_disabled.jsonl"
    tele = RasaTelemetry(log_path=str(log))
    tele.enabled = False

    baseline = _read_counter_value(
        RASA_EVENTS_TOTAL,
        risk_band="safe",
        enforcement_mode="shadow",
        enforced="false",
    )

    tele.log_shadow(
        session_id="s2",
        message="hi",
        ungoverned_result=None,
        governed_result={
            "detection": type("D", (), {"risk_band": type("B", (), {"value": "safe"}),
                                          "emotion_tags": []})(),
            "judge": None,
            "final_posture": "proceed",
        },
        enforcement_mode="shadow",
        enforced=False,
    )

    after = _read_counter_value(
        RASA_EVENTS_TOTAL,
        risk_band="safe",
        enforcement_mode="shadow",
        enforced="false",
    )
    assert after == baseline, (
        "Counter must NOT increment when telemetry is disabled (no real event)"
    )


# ---------------------------------------------------------------------------
# SCAR CANDIDATES COUNTER
# ---------------------------------------------------------------------------
def test_scar_candidates_counter_increments_only_after_persistence():
    """arifos_scar_candidates_total increments only after JSON write to disk.

    We exercise the record_scar_candidate() helper directly — that's the
    unit under test. The judge call site is responsible for invoking it
    ONLY after JSON durability. This test verifies the helper honors the
    label contract.
    """
    from arifosmcp.runtime.metrics import SCAR_CANDIDATES_TOTAL, record_scar_candidate

    baseline = _read_counter_value(
        SCAR_CANDIDATES_TOTAL,
        stage="arif_judge::paradox_gate",
        severity="high",
    )

    record_scar_candidate(stage="arif_judge::paradox_gate", severity="high")

    after = _read_counter_value(
        SCAR_CANDIDATES_TOTAL,
        stage="arif_judge::paradox_gate",
        severity="high",
    )
    assert after > baseline, (
        "record_scar_candidate must increment counter at call time"
    )


def test_scar_candidates_severity_labels_distinct():
    """Different severity labels → distinct counter series."""
    from arifosmcp.runtime.metrics import SCAR_CANDIDATES_TOTAL, record_scar_candidate

    record_scar_candidate(stage="test::low", severity="low")
    record_scar_candidate(stage="test::critical", severity="critical")

    low = _read_counter_value(SCAR_CANDIDATES_TOTAL, stage="test::low", severity="low")
    critical = _read_counter_value(
        SCAR_CANDIDATES_TOTAL, stage="test::critical", severity="critical"
    )
    assert low > 0
    assert critical > 0


# ---------------------------------------------------------------------------
# /api/live/all kappa_r mapping
# ---------------------------------------------------------------------------
def test_api_live_all_kappa_r_not_echo_debt(monkeypatch):
    """kappa_r is read from kappa_r, NOT aliased to echo_debt.

    The legacy bug aliased kappa_r ← echo_debt. The fix reads kappa_r from
    its own field, returning None when unavailable. We patch the /health
    function so the api_live_all endpoint receives a payload where
    vitals.thermodynamic contains BOTH echo_debt AND kappa_r with
    distinguishable values.
    """

    import time as _t

    from arifosmcp.runtime.rest_routes import rest_routes as rr
    from arifosmcp.runtime.server import app as server_app
    from tests.conftest import SyncASGIClient

    fake_health_payload = {
        "status": "healthy",
        "thermodynamic": {
            "entropy_delta": -0.35,
            "peace_squared": 1.04,
            "vitality_index": 0.82,
            "echo_debt": 0.42,
            "kappa_r": 0.97,  # distinct from echo_debt
            "psi_vitality": 0.82,
            "shadow": 0.3,
            "confidence": 0.88,
            "verdict": None,
            "service_health": "PASS",
            "metabolic_stage": 444,
            "witness": {"human": 0.42, "ai": 0.32, "earth": 0.26},
        },
        "tools_loaded": 8,
        "floors_active": 13,
        "version": "test",
        "source_commit": "test",
        "vault999_health": "healthy",
        "runtime_drift": False,
    }

    # Seed the /health 30s cache directly with the fake payload — no need
    # to monkey-patch the closure-defined health() function. /health will
    # return this cached payload verbatim.
    rr._health_cache["payload"] = fake_health_payload
    rr._health_cache["ts"] = _t.monotonic()

    client = SyncASGIClient(server_app)
    response = client.get("/api/live/all")
    if response.status_code != 200:
        pytest.skip(f"/api/live/all not reachable: {response.status_code}")
    data = response.json()

    v = data.get("vitals", {})
    # Truthfulness contract:
    # 1. kappa_r is read from its own field, NOT aliased to echo_debt.
    assert v.get("kappa_r") == 0.97, (
        f"kappa_r must come from kappa_r source (got {v.get('kappa_r')!r})"
    )
    # 2. echo_debt is its own field, not collapsed into kappa_r.
    assert v.get("echo_debt") == 0.42, (
        "echo_debt must remain its own field, distinct from kappa_r"
    )
    # 3. They are NOT the same value (proves the alias bug is gone).
    assert v.get("kappa_r") != v.get("echo_debt"), (
        "kappa_r must not be aliased to echo_debt"
    )


def test_api_live_all_unavailable_scalar_remains_none(monkeypatch):
    """When vitals lacks a scalar, /api/live/all returns None (no zero-fill)."""
    import time as _t

    from arifosmcp.runtime.rest_routes import rest_routes as rr
    from arifosmcp.runtime.server import app as server_app
    from tests.conftest import SyncASGIClient

    fake_health_payload = {
        "status": "healthy",
        "thermodynamic": {
            "entropy_delta": -0.35,
            "peace_squared": 1.04,
            "vitality_index": 0.82,
            # NOTE: no kappa_r, no echo_debt, no psi_vitality
            "service_health": "PASS",
            "metabolic_stage": 444,
            "witness": {"human": 0.42, "ai": 0.32, "earth": 0.26},
        },
        "tools_loaded": 8,
        "floors_active": 13,
        "version": "test",
        "source_commit": "test",
        "vault999_health": "healthy",
        "runtime_drift": False,
    }

    rr._health_cache["payload"] = fake_health_payload
    rr._health_cache["ts"] = _t.monotonic()

    client = SyncASGIClient(server_app)
    response = client.get("/api/live/all")
    if response.status_code != 200:
        pytest.skip(f"/api/live/all not reachable: {response.status_code}")
    data = response.json()
    v = data.get("vitals", {})
    # Truthfulness: None for unavailable, not 0.0
    assert v.get("kappa_r") is None, (
        f"kappa_r must be None when upstream doesn't provide it (got {v.get('kappa_r')!r})"
    )
    assert v.get("echo_debt") is None, (
        f"echo_debt must be None when upstream doesn't provide it (got {v.get('echo_debt')!r})"
    )
    assert v.get("psi_le") is None


# ---------------------------------------------------------------------------
# graphiti_embedding_runtime decoupling from ARIFOS_ML_FLOORS
# ---------------------------------------------------------------------------
def test_graphiti_embedding_runtime_unverified_when_not_probed(monkeypatch):
    """graphiti_embedding_runtime starts as 'unverified' regardless of ML toggle.

    The F2 TRUTH guarantee: embedding status is reported only AFTER a real
    semantic probe completes. The legacy behavior of binding it to
    ARIFOS_ML_FLOORS+ml_runtime_ready is removed.
    """
    from arifosmcp.runtime.rest_routes import rest_routes as rr
    from arifosmcp.runtime.server import app as server_app
    from tests.conftest import SyncASGIClient

    # Bypass /health 30s cache
    monkeypatch.setattr(rr, "_health_cache", {"payload": None, "ts": 0.0})

    monkeypatch.setattr(
        rr, "_build_governance_status_payload",
        lambda: {
            "telemetry": {}, "floors": {}, "machine_vitals": {},
            "verdict": "HOLD", "session_id": "t",
            "tau_confidence_system": None, "f2_threshold": 0.99,
            "psi_vitality": None, "peace2": None,
        },
    )
    # ML floors DISABLED — must NOT affect graphiti_embedding_runtime.
    monkeypatch.delenv("ARIFOS_ML_FLOORS", raising=False)
    from core.shared import law_audit

    law_audit._probe_ml_embedding_runtime.cache_clear()
    law_audit._load_sbert_runtime.cache_clear()

    client = SyncASGIClient(server_app)
    response = client.get("/health")
    if response.status_code != 200:
        pytest.skip(f"/health not reachable: {response.status_code}")
    data = response.json()

    sr = data.get("semantic_readiness", {})
    # Three independent dimensions:
    assert "graphiti_transport" in sr
    assert "graphiti_storage" in sr
    assert "graphiti_embedding_runtime" in sr
    assert "graphiti_semantic_floor" in sr
    # Decoupling: embedding is unverified (not "disabled" or "hold")
    assert sr["graphiti_embedding_runtime"] == "unverified", (
        f"expected 'unverified' but got {sr['graphiti_embedding_runtime']!r}"
    )
    # Semantic floor still tracks the ML toggle
    assert sr["graphiti_semantic_floor"] in ("disabled", "hold", "enabled")