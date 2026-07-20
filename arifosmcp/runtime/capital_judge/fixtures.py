"""
PR6 — Deterministic Capital Judge fixture.

A synthetic case with pre-computed expected hashes. The orchestrator
must produce these hashes EXACTLY on every replay. This is the audit's
"Same inputs replayed | Same calculation hashes" requirement.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .state_machine import CapitalCase, _hash


@dataclass
class CapitalJudgeFixture:
    """A reproducible capital case. Same fields → same hashes → same receipts."""

    case_id: str
    capital_case: CapitalCase
    expected_outputs: dict[str, Any]
    expected_input_hash: str
    expected_output_hash: str
    expected_state_chain: list[str]
    expected_receipt_types: list[str]


def _synth_npv(cashflows: list[float], discount_rate: float, terminal: float = 0.0) -> float:
    """Hand-computed NPV with constant discount rate. Reproducible to ±0.01."""
    npv = -1_000_000.0  # initial_capital (sign convention: outflow)
    for t, cf in enumerate(cashflows, start=1):
        npv += cf / ((1 + discount_rate) ** t)
    if terminal:
        npv += terminal / ((1 + discount_rate) ** len(cashflows))
    return round(npv, 2)


def _synth_irr(
    cashflows: list[float],
    initial_capital: float,
    low: float = 0.0,
    high: float = 1.0,
    tol: float = 1e-5,
) -> float:
    """Hand-computed IRR via bisection. Reproducible to ±1e-4."""

    def f(rate: float) -> float:
        v = -initial_capital
        for t, cf in enumerate(cashflows, start=1):
            v += cf / ((1 + rate) ** t)
        return v

    for _ in range(200):
        mid = (low + high) / 2
        if f(mid) > 0:
            low = mid
        else:
            high = mid
        if abs(high - low) < tol:
            return round(mid, 6)
    return round((low + high) / 2, 6)


def _synth_dscr(cashflows: list[float], debt_service: list[float]) -> float:
    """Hand-computed DSCR (cashflow / debt service). Reproducible."""
    total_cf = sum(cashflows)
    total_ds = sum(debt_service)
    if total_ds == 0:
        return float("inf")
    return round(total_cf / total_ds, 2)


# Deterministic fixture parameters
_FCF: list[float] = [200_000.0, 250_000.0, 300_000.0, 350_000.0, 400_000.0]
_DS: list[float] = [0.0, 0.0, 0.0, 0.0, 1_100_000.0]


def cap_2026_001() -> CapitalJudgeFixture:
    """Audit-mandated fixture: deterministic synthetic case."""
    case = CapitalCase(
        case_id="CAP-2026-001",
        actor={
            "session_id": "session-fixture-001",
            "actor_id": "ARIF",
            "subject_did": "did:web:arif-fazil.com:agents:wealth",
        },
        purpose={
            "description": "Synthetic revenue ramp case for CI validation. Deterministic.",
            "decision_requested": "PROCEED_with_advisory",
        },
        valuation={
            "currency": "MYR",
            "valuation_date": "2026-01-01",
            "horizon_years": 5,
            "discount_rate": 0.10,
        },
        inputs={
            "initial_capital": 1_000_000.00,
            "cashflows": _FCF,
            "debt_service": _DS,
            "terminal_assumptions": {"growth": 0, "exit_multiple": 1.0},
        },
        evidence={
            "source_references": ["fixture:synthetic", "version:1.0.0"],
            "observed_values": {"sum_fcf": sum(_FCF), "sum_ds": sum(_DS)},
            "reported_values": {"npv_at_10pct": _synth_npv(_FCF, 0.10)},
            "assumptions": ["discount_rate=0.10", "horizon=5y", "no terminal"],
            "missing_information": [],
        },
        governance={
            "action_class": "ADVISORY_CAPITAL_JUDGMENT",
            "reversibility": "HIGH",
            "blast_radius": "NONE",
            "human_ratification_required": False,
            "minimum_authority": "OPERATOR",
            "public_simulation": False,
        },
        expected_outputs={
            "npv": _synth_npv(_FCF, 0.10),
            "irr": _synth_irr(_FCF, 1_000_000.0),
            "dscr": _synth_dscr(_FCF, _DS),
        },
        issuer="arifOS",
    )
    input_payload = {
        "case_id": case.case_id,
        "inputs": case.inputs,
        "evidence": case.evidence,
    }
    output = {
        "npv": case.expected_outputs["npv"],
        "irr": case.expected_outputs["irr"],
        "dscr": case.expected_outputs["dscr"],
        "case_id": case.case_id,
    }
    return CapitalJudgeFixture(
        case_id=case.case_id,
        capital_case=case,
        expected_outputs=case.expected_outputs,
        expected_input_hash=_hash(input_payload),
        expected_output_hash=_hash(output),
        expected_state_chain=[
            "RECEIVED",
            "AUTHENTICATED",
            "VALIDATED",
            "COMPUTED",
            "JUDGED",
            "SEALED",
            "EXECUTED",
        ],
        expected_receipt_types=["COMPUTATION", "JUDGMENT", "SEAL", "EXECUTION"],
    )


FIXTURE = cap_2026_001()
