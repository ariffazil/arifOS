"""Blocker #7 (civfork gap-map 2026-11-02): flat-default thermodynamic scalar
labels on /health.

A structural baseline rendered without a label reads as a measurement (the
peace2=0.5 pattern). /health's thermodynamic block must carry
``scalar_provenance`` — the same discipline the floors side already applies
via ``floor_provenance`` / ``unmeasured_default`` (SCAR-OBS-GREENWASH).

Acceptance (gap-map G2): the live /health scalar carries the label, and the
label agrees with the leaf's own measurement_contract entry.
"""

from __future__ import annotations

import json
import urllib.request

import pytest

from arifosmcp.runtime.rest_routes.rest_routes import (
    _thermo_scalar_provenance,
    _thermo_scalar_provenance_block,
)


# ── unit: pure classifier ──────────────────────────────────────────────


def test_absent_when_no_value():
    assert (
        _thermo_scalar_provenance("peace_squared", None, event_log_empty=True)
        == "ABSENT"
    )


def test_default_unmeasured_on_flat_baseline_with_empty_log():
    assert (
        _thermo_scalar_provenance("peace_squared", 0.5, event_log_empty=True)
        == "DEFAULT_UNMEASURED"
    )
    assert (
        _thermo_scalar_provenance("entropy_delta", 0.0, event_log_empty=True)
        == "DEFAULT_UNMEASURED"
    )
    assert (
        _thermo_scalar_provenance("shadow", 0.0, event_log_empty=True)
        == "DEFAULT_UNMEASURED"
    )
    assert (
        _thermo_scalar_provenance("echo_debt", 0, event_log_empty=True)
        == "DEFAULT_UNMEASURED"
    )


def test_measured_when_log_has_history():
    assert (
        _thermo_scalar_provenance("peace_squared", 0.5, event_log_empty=False)
        == "MEASURED"
    )


def test_measured_when_value_is_not_baseline():
    # a non-baseline value cannot come from an empty event log, so it is real
    assert (
        _thermo_scalar_provenance("peace_squared", 0.73, event_log_empty=True)
        == "MEASURED"
    )


def test_policy_constant_leaves_match_their_contracts():
    for name in ("kappa_r", "confidence"):
        assert (
            _thermo_scalar_provenance(name, 0.5, event_log_empty=True)
            == "POLICY_CONSTANT"
        )
        # declared constants never fall through to ABSENT even with no value
        assert (
            _thermo_scalar_provenance(name, None, event_log_empty=True)
            == "POLICY_CONSTANT"
        )


def test_unparseable_value_is_absent_not_measured():
    assert (
        _thermo_scalar_provenance("peace_squared", "not-a-number", event_log_empty=True)
        == "ABSENT"
    )


# ── unit: block builder shape ──────────────────────────────────────────


def test_block_labels_cover_the_numeric_contract_leaves():
    telemetry = {
        "dS": 0.5,
        "peace2": 0.5,
        "psi_le": 0.0,
        "kappa_r": 0.5,
        "echoDebt": 0,
        "shadow": 0.0,
        "confidence": 1.0,
    }
    block = _thermo_scalar_provenance_block(telemetry)
    assert set(block["labels"]) == {
        "entropy_delta",
        "peace_squared",
        "vitality_index",
        "kappa_r",
        "echo_debt",
        "shadow",
        "confidence",
    }
    basis = block["basis"]
    assert isinstance(basis["event_log_has_history"], bool)
    assert isinstance(basis["detail"], str) and basis["detail"]
    assert basis["detector"] == "reality_scoring.probe_governance_kernel_events"


def test_block_fails_toward_honesty_when_probe_unavailable(monkeypatch):
    # baseline-equal value + probe failure must NOT label MEASURED
    import builtins

    real_import = builtins.__import__

    def broken_import(name, *args, **kwargs):
        if "reality_scoring" in name:
            raise ImportError("simulated probe outage")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", broken_import)
    block = _thermo_scalar_provenance_block({"peace2": 0.5})
    assert block["basis"]["event_log_has_history"] is False
    assert block["labels"]["peace_squared"] == "DEFAULT_UNMEASURED"


# ── live acceptance (kernel :8088) ─────────────────────────────────────

ARIFOS_HEALTH_URL = "http://127.0.0.1:8088/health"


@pytest.fixture(scope="module")
def health() -> dict:
    try:
        req = urllib.request.Request(
            ARIFOS_HEALTH_URL, headers={"Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            return json.loads(resp.read())
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"arifOS /health unreachable: {exc}")


def test_live_health_thermo_carries_scalar_provenance(health):
    thermo = health.get("thermodynamic") or {}
    sp = thermo.get("scalar_provenance")
    assert isinstance(sp, dict), (
        f"thermodynamic.scalar_provenance missing on live /health; keys={sorted(thermo)}"
    )
    assert "peace_squared" in (sp.get("labels") or {})
    assert (sp.get("basis") or {}).get("event_log_has_history") in (True, False)


def test_live_label_agrees_with_contract_and_value(health):
    """Gap-map G2 acceptance: '/health scalar carries label; contract value
    matches' — the label must agree with the leaf's own contract entry."""
    thermo = health.get("thermodynamic") or {}
    labels = (thermo.get("scalar_provenance") or {}).get("labels") or {}
    contracts = thermo.get("measurement_contract") or {}
    for name in (
        "entropy_delta",
        "peace_squared",
        "vitality_index",
        "kappa_r",
        "echo_debt",
        "shadow",
        "confidence",
    ):
        label = labels.get(name)
        assert label in (
            "MEASURED",
            "DEFAULT_UNMEASURED",
            "POLICY_CONSTANT",
            "ABSENT",
        ), f"{name}: invalid provenance label {label!r}"
        contract = contracts.get(name) or {}
        if contract.get("semantic_class") == "POLICY_CONSTANT":
            assert label == "POLICY_CONSTANT", (
                f"{name}: contract says POLICY_CONSTANT but label says {label!r}"
            )
        if label == "DEFAULT_UNMEASURED":
            # a labelled structural baseline must not simultaneously claim
            # decision eligibility from its contract
            assert contract.get("decision_eligibility") != "FULL", (
                f"{name}: DEFAULT_UNMEASURED contradicts decision_eligibility="
                f"{contract.get('decision_eligibility')!r}"
            )
