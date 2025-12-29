import pytest
from arifos_core.contracts.apex_prime_output_v41 import compute_apex_pulse, serialize_public

def test_void_band():
    assert compute_apex_pulse(1.08, "VOID") <= 0.94

def test_sabar_band():
    p = compute_apex_pulse(1.08, "SABAR")
    assert 0.95 <= p <= 0.99

def test_seal_band():
    assert compute_apex_pulse(0.10, "SEAL") >= 1.00

def test_pulse_cap():
    assert compute_apex_pulse(999.0, "SEAL") <= 1.10

def test_missing_psi_gives_null():
    out = serialize_public(verdict="SEAL", psi_internal=None, response="ok")
    assert out["apex_pulse"] is None

def test_seal_output_format():
    out = serialize_public(verdict="SEAL", psi_internal=1.05, response="Hello world")
    assert out["verdict"] == "SEAL"
    assert out["apex_pulse"] >= 1.00
    assert out["response"] == "Hello world"
    assert "reason_code" not in out

def test_sabar_with_reason():
    out = serialize_public(verdict="SABAR", psi_internal=0.98, response="Clarify please", reason_code="F2(DELTA_S)")
    assert out["verdict"] == "SABAR"
    assert 0.95 <= out["apex_pulse"] <= 0.99
    assert out["response"] == "Clarify please"
    assert out["reason_code"] == "F2(DELTA_S)"

def test_void_output_format():
    out = serialize_public(verdict="VOID", psi_internal=0.5, response="Blocked", reason_code="F5(AMANAH)")
    assert out["verdict"] == "VOID"
    assert out["apex_pulse"] <= 0.94
    assert out["response"] == "Blocked"
    assert out["reason_code"] == "F5(AMANAH)"