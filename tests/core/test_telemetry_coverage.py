
from __future__ import annotations
import os
import json
import pytest
from datetime import datetime, timezone, timedelta
from core.telemetry import (
    ConstitutionalTelemetry,
    TelemetryStore,
    log_telemetry,
    check_adaptation_status,
    get_current_hysteresis,
    get_system_vitals,
    get_actual_joules,
    _utcnow
)

@pytest.fixture
def temp_telemetry_store(tmp_path):
    store_path = tmp_path / "telemetry"
    return TelemetryStore(storage_path=str(store_path))

def test_utcnow():
    now = _utcnow()
    assert now.tzinfo == timezone.utc

def test_telemetry_log_and_load(temp_telemetry_store):
    t = ConstitutionalTelemetry(session_id="test_s1", omega_0=0.04)
    temp_telemetry_store.log(t)
    
    assert temp_telemetry_store.first_telemetry_date is not None
    assert temp_telemetry_store.get_telemetry_days() == 0
    
    # Check if file exists
    date_str = _utcnow().strftime("%Y-%m-%d")
    log_file = os.path.join(temp_telemetry_store.storage_path, f"telemetry-{date_str}.jsonl")
    assert os.path.exists(log_file)
    
    with open(log_file) as f:
        data = json.loads(f.read().strip())
        assert data["session_id"] == "test_s1"
        assert data["omega_0"] == 0.04

def test_calculate_weekly_drift(temp_telemetry_store):
    # Log some drift
    t1 = ConstitutionalTelemetry(session_id="s1", predicted_risk=0.5, observed_outcome=0.7, misprediction_delta=0.2)
    temp_telemetry_store.log(t1)
    
    drift = temp_telemetry_store._calculate_weekly_drift()
    assert drift == pytest.approx(0.2)

def test_calculate_hysteresis_penalty(temp_telemetry_store):
    # Log VOID and SABAR
    t_void = ConstitutionalTelemetry(session_id="s_void", void_count=1)
    t_sabar = ConstitutionalTelemetry(session_id="s_sabar", sabar_count=1)
    temp_telemetry_store.log(t_void)
    temp_telemetry_store.log(t_sabar)
    
    h = temp_telemetry_store.calculate_hysteresis_penalty()
    # Formula: total_penalty += (v_count * 0.15 + s_count * 0.03) * decay
    # Today decay is 1.0
    assert h == pytest.approx(0.15 + 0.03)

def test_can_adapt(temp_telemetry_store):
    res = temp_telemetry_store.can_adapt()
    assert res["can_adapt"] is False # Default lock
    assert "Insufficient telemetry" in res["reasons"][0]

def test_generate_weekly_report(temp_telemetry_store):
    report = temp_telemetry_store.generate_weekly_report()
    assert report["q3_compliance"] == "TELEMETRY_FIRST"
    assert "report_date" in report

def test_system_vitals():
    vitals = get_system_vitals()
    assert "cpu_percent" in vitals
    assert "memory_percent" in vitals

def test_get_actual_joules(monkeypatch):
    import psutil
    # Mock CPU load to 35% to match the test calculation: 
    # Watts = 5 + (40 * 0.35) = 19.0
    monkeypatch.setattr(psutil, "cpu_percent", lambda interval=None: 35.0)
    
    j = get_actual_joules(1000.0) # 1 second
    # BASE_TDP = 45.0, IDLE = 5.0, Load = 0.35
    # Watts = 5 + (40 * 0.35) = 5 + 14 = 19.0
    # Joules = 19.0 * 1.0 = 19.0
    assert j == pytest.approx(19.0)

def test_log_telemetry_convenience(monkeypatch, temp_telemetry_store):
    # Patch global store
    import core.telemetry
    monkeypatch.setattr(core.telemetry, "telemetry_store", temp_telemetry_store)
    
    log_telemetry("session_conv", 0.04, 0.1, verdict="SEAL")
    
    h = get_current_hysteresis()
    assert h == 0.0 # SEAL doesn't add to hysteresis
    
    status = check_adaptation_status()
    assert status["days"] == 0
