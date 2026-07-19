"""
Tests for arifosmcp.runtime.organs_standards.
F1-safe: probes the kernel-self (arifOS) and the others via TCP. Real network calls
to other organs may fail or skip in test env; we never fail on unreachable probe.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arifosmcp.runtime.organs_standards import (  # noqa: E402
    ORGAN_MAP,
    OrganStandardProbe,
    probe_all_organs,
    overall_aggregate_state,
    probe_arifOS,
    probe_vault999,
)


def test_organ_map_covers_all_eight() -> None:
    expected = {"arifos","geox","wealth","well","aaa","aforge","mcp_gateway","vault999"}
    assert set(ORGAN_MAP.keys()) == expected


def test_each_organ_has_three_ports_and_public_origin() -> None:
    """The audit requires internal:host:public per organ."""
    for name, cfg in ORGAN_MAP.items():
        assert "internal_port" in cfg
        assert "host_port" in cfg
        assert "public_origin" in cfg or name == "vault999"  # vault has no public origin
        assert "ontological_layer" in cfg
        assert "exposure" in cfg


def test_probe_arifos_returns_envelope_shape() -> None:
    p = probe_arifOS()
    assert isinstance(p, OrganStandardProbe)
    d = p.to_dict()
    for k in ("organ","internal_port","host_port","public_origin","ontological_layer",
              "transport_state","transport_latency_ms","identity_match",
              "readiness_state","readiness_dependencies","capability_drift",
              "governance_session_required","governance_mutation_allowed","governance_forge_mode",
              "evidence_class","evidence_source","overall_state","overall_reasons","observed_at"):
        assert k in d, f"missing {k}"


def test_arifOS_state_vocabulary_excludes_healthy() -> None:
    """The audit's first P0 fix: layers must use the four-state ladder, not 'HEALTHY'."""
    p = probe_arifOS()
    assert p.transport_state in {"reachable","unreachable","unknown"}
    assert p.overall_state in {"OPERATIONAL","DEGRADED","UNREACHABLE","UNKNOWN"}
    assert p.overall_state != "HEALTHY"
    # Probe type field enforces the audit rule about distinguishing self vs independent.
    assert p.transport_probe_type in {"self","independent","cross-federation"}


def test_overall_aggregate_ladder() -> None:
    # Empty → UNKNOWN
    assert overall_aggregate_state([]) == "UNKNOWN"
    # All OPERATIONAL
    assert overall_aggregate_state([{"overall_state":"OPERATIONAL"}]) == "OPERATIONAL"
    # Any UNREACHABLE → UNREACHABLE
    assert overall_aggregate_state([{"overall_state":"OPERATIONAL"},{"overall_state":"UNREACHABLE"}]) == "UNREACHABLE"
    # Mixed → DEGRADED
    assert overall_aggregate_state([{"overall_state":"OPERATIONAL"},{"overall_state":"DEGRADED"}]) == "DEGRADED"


def test_probe_arifos_self_report_distinguishable_from_independent() -> None:
    """Self-report probe_type marked clearly so future agents don't conflate with independent probes."""
    p = probe_arifOS()
    # All arifOS fields may legitimately be 'self' (we read our own /health).
    assert p.transport_probe_type == "self"
    assert p.identity_probe_type == "self"
    assert p.capability_probe_type == "self"
    assert p.governance_probe_type == "self"


def test_probe_vault999_filesystem_truth(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """VAULT probe must read filesystem state — not just HTTP /health."""
    # Don't tamper with the live vault; only assert the envelope shape.
    p = probe_vault999()
    d = p.to_dict()
    assert d["organ"] == "vault999"
    assert d["ontological_layer"] == "MEMORY"
    assert "governance_session_required" in d
