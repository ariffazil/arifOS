"""
Unit Tests for Rasa Dunia Engine — arifOS Sensory Substrate
═══════════════════════════════════════════════════════════
"""

from __future__ import annotations

import pytest
from arifosmcp.rasa.rasa_dunia import (
    RasaDuniaEngine,
    RasaDuniaRiskBand,
    RasaDuniaVerdict,
    get_rasa_dunia_snapshot,
)
from arifosmcp.tools.sense import arif_observe


def test_rasa_dunia_engine_baselines():
    """Verify engine evaluates safe baselines correctly."""
    engine = RasaDuniaEngine()
    
    # Standard safe parameters
    live_inputs = {
        "gas:thermal_stress": 1.0,               # Celsius deviation (safe)
        "gas:pipeline_load": 72.0,               # 72 bar (safe)
        "gas:liquefaction_metabolism": 23.9,     # continuous run (safe)
        "gas:chokepoint_friction": 8.0,          # low chokepoint delay (safe)
        
        "gold:systemic_trust_decay": 1.1,        # yield ratio (safe)
        "oil:chokepoint_friction": 6.5,          # Hormuz delay (safe)
        "copper:industrial_metabolism": 48.0,    # LME stock level (safe)
        "fx:systemic_trust_decay": 4.46,         # USD/MYR exchange rate (safe)
    }

    envelope = engine.evaluate(live_inputs)
    assert envelope.verdict == RasaDuniaVerdict.PROCEED
    assert envelope.entropy_index < 0.35
    assert envelope.epistemic_confidence == 0.90
    assert len(envelope.signals) == 8
    
    # Check that individual signals match units and SAFE risk band
    assert envelope.signals["gas:pipeline_load"].risk_band == RasaDuniaRiskBand.SAFE
    assert envelope.signals["gas:pipeline_load"].unit == "bar"
    assert envelope.signals["gas:thermal_stress"].unit == "C"


def test_rasa_dunia_engine_sabar_strain():
    """Verify engine triggers SABAR on elevated physical strain."""
    engine = RasaDuniaEngine()
    
    # Set one vector to elevated strain
    live_inputs = {
        "gas:pipeline_load": 86.5,               # 86.5 bar (elevated pressure strain)
        "gold:systemic_trust_decay": 1.1,
    }

    envelope = engine.evaluate(live_inputs)
    assert envelope.verdict == RasaDuniaVerdict.SABAR
    assert "SABAR triggered" in envelope.notes[0]
    assert envelope.weakest_vector == "gas:pipeline_load"
    assert envelope.signals["gas:pipeline_load"].risk_band == RasaDuniaRiskBand.STRAIN


def test_rasa_dunia_engine_hold_crisis():
    """Verify engine triggers HOLD on physical or trust crisis bands."""
    engine = RasaDuniaEngine()
    
    # Set gold yield ratio to crisis levels
    live_inputs = {
        "gold:systemic_trust_decay": 2.8,        # ratio 2.8 (crisis)
        "gas:pipeline_load": 72.0,
    }

    envelope = engine.evaluate(live_inputs)
    assert envelope.verdict == RasaDuniaVerdict.HOLD
    assert "HOLD triggered" in envelope.notes[0]
    assert envelope.weakest_vector == "gold:systemic_trust_decay"
    assert envelope.signals["gold:systemic_trust_decay"].risk_band == RasaDuniaRiskBand.CRISIS


def test_rasa_dunia_engine_empty_input():
    """Verify engine defaults gracefully when empty input is provided."""
    engine = RasaDuniaEngine()
    envelope = engine.evaluate({})
    
    assert envelope.verdict == RasaDuniaVerdict.PROCEED
    assert envelope.entropy_index == 0.0
    assert envelope.weakest_vector == "none"


def test_get_rasa_dunia_snapshot():
    """Verify snapshot helper method executes without error."""
    snapshot = get_rasa_dunia_snapshot()
    assert isinstance(snapshot, dict)
    assert "verdict" in snapshot
    assert "entropy_index" in snapshot
    assert "signals" in snapshot


def test_arif_observe_rasa_dunia_mode():
    """Verify arif_observe tool integrates rasa_dunia mode and responds with valid packet."""
    resp = arif_observe(
        mode="rasa_dunia",
        actor_id="arif",
        partition_mode="ONLINE"
    )

    assert resp["status"] == "OK"
    # The snapshot is returned directly as the result dict
    result = resp.get("result", resp)
    # verdict may be at result or top-level
    verdict_val = result.get("verdict") or resp.get("verdict")
    entropy_val = result.get("entropy_index") if "entropy_index" in result else resp.get("entropy_index")
    signals_val = result.get("signals") if "signals" in result else resp.get("signals")
    assert verdict_val is not None and isinstance(verdict_val, str) and len(verdict_val) > 0
    assert entropy_val is not None
    assert signals_val is not None
