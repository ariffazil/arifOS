"""P1 memory-audit-zero-laundering — unmeasured telemetry must be null, not 0.

Live defect (2026-10-27): arif_memory mode=audit returned
diagnostics.metrics.telemetry = {G_star: 0, confidence: 0.85, verdict: "ALIVE",
...} and witness = {human: 0, ai: 0, earth: 0}. Those were Pydantic defaults,
not measurements — zero disguised as a reading.

Fix: G_star and the three witness channels default to None (K2: unknown != 0).
continuity.py treats None as unset, exactly as it treated 0.0.
"""

from __future__ import annotations

from arifosmcp.runtime.model import (
    CanonicalMetrics,
    RuntimeEnvelope,
    TelemetryMetrics,
    TripleWitness,
)


def test_telemetry_defaults_are_unmeasured_not_zero():
    metrics = CanonicalMetrics()
    assert metrics.telemetry.G_star is None
    assert metrics.witness.human is None
    assert metrics.witness.ai is None
    assert metrics.witness.earth is None


def test_measured_values_survive_round_trip():
    metrics = CanonicalMetrics(
        telemetry=TelemetryMetrics(G_star=0.58),
        witness=TripleWitness(human=1.0, ai=0.9, earth=0.8),
    )
    assert metrics.telemetry.G_star == 0.58
    assert metrics.model_dump()["witness"] == {"human": 1.0, "ai": 0.9, "earth": 0.8}


def test_envelope_diagnostics_do_not_claim_a_zero_measurement():
    envelope = RuntimeEnvelope(tool="arif_memory")
    dumped = envelope.model_dump(mode="json")
    assert dumped["metrics"]["telemetry"]["G_star"] is None
    assert dumped["metrics"]["witness"]["human"] is None
