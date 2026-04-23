import pytest
from arifosmcp.runtime.well_bridge import get_biological_readiness, inject_biological_context

def test_well_readiness_exists():
    readiness = get_biological_readiness()
    assert "well_score" in readiness
    assert "verdict" in readiness

def test_well_injection():
    initial_state = {
        "verdict": "SEAL",
        "telemetry": {},
        "message": "Initial"
    }
    injected = inject_biological_context(initial_state)
    assert "well_score" in injected["telemetry"]
    assert "well_verdict" in injected["telemetry"]
    
    # Test if it can downgrade SEAL to HOLD if degraded
    # We'll mock the state file check if needed, but let's see if it works with current state.json
