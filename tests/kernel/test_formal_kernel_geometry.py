"""Formal kernel geometry — three layers, one sovereign.

Python kernel judges. TypeScript A-FORGE executes. Quantum is calculator (contract).
These 6 probes lock the claim surface for arifosmcp.runtime.kernel.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import importlib

from arifosmcp.runtime.kernel.compute import compute_scalars
from arifosmcp.runtime.kernel.judge import judge
from arifosmcp.runtime.kernel.pipeline import (
    ingest_evidence,
    ingest_intent,
    run_pipeline,
    validate_transition,
    PhaseTransitionError,
)
from arifosmcp.runtime.kernel.types import EvidenceItem, GovernanceState, RiskProfile

seal_mod = importlib.import_module("arifosmcp.runtime.kernel.seal")


def _healthy_evidence() -> list[EvidenceItem]:
    return [
        EvidenceItem.create("GEOX", {"phi": 0.18}, "CLAIM"),
        EvidenceItem.create("WEALTH", {"npv": 12.0}, "PLAUSIBLE"),
        EvidenceItem.create("HUMAN", {"ack": True}, "CLAIM"),
    ]


def test_1_seal_path_delta_omega_psi():
    """SEAL path: multi-source evidence + authority → SEAL."""
    st = GovernanceState(
        phase=888,
        evidence=_healthy_evidence(),
        authority_present=True,
        reversible=True,
        risk=RiskProfile(blast_radius="LOW"),
        actor_id="arif",
    )
    st.scalars = compute_scalars(st)
    st = judge(st)
    assert st.verdict == "SEAL"
    assert st.scalars.delta >= 0.0
    assert st.scalars.omega < 0.5
    assert st.scalars.psi >= 0.99


def test_2_void_on_no_authority():
    st = GovernanceState(
        phase=888,
        evidence=_healthy_evidence(),
        authority_present=False,
        reversible=True,
        risk=RiskProfile(blast_radius="LOW"),
    )
    st.scalars = compute_scalars(st)
    st = judge(st)
    assert st.verdict == "VOID"
    assert any(t.id == "AUTHORITY" and t.triggered for t in (st.collapse.tripwires if st.collapse else []))


def test_3_llm_only_blocked():
    """LLM-only evidence trips FLOOR → VOID (not SEAL). Claim text may say HOLD; code is VOID."""
    st = GovernanceState(
        phase=888,
        evidence=[EvidenceItem.create("LLM", {"text": "guess"}, "ESTIMATE")],
        authority_present=True,
        reversible=True,
        risk=RiskProfile(blast_radius="LOW"),
        actor_id="arif",
    )
    st.scalars = compute_scalars(st)
    st = judge(st)
    assert st.verdict in ("HOLD", "VOID", "SABAR")
    assert st.verdict != "SEAL"


def test_4_chain_verify_sha256():
    chain = seal_mod.empty_chain()
    st = GovernanceState(
        phase=888,
        evidence=_healthy_evidence(),
        authority_present=True,
        reversible=True,
        risk=RiskProfile(blast_radius="LOW"),
        actor_id="arif",
        verdict="SEAL",
    )
    st.scalars = compute_scalars(st)
    rec1 = seal_mod.seal(st, chain)
    chain = seal_mod.append_to_chain(chain, rec1)
    rec2 = seal_mod.seal(st, chain)
    chain = seal_mod.append_to_chain(chain, rec2)
    valid, broken, _head = seal_mod.verify_chain(chain)
    assert valid is True
    assert broken == -1
    assert len(chain.records) == 3  # genesis + 2


def test_5_pipeline_transitions_0_errors():
    phases = [0, 111, 333, 555, 777, 888, 900, 999]
    for a, b in zip(phases, phases[1:]):
        validate_transition(a, b)  # must not raise
    try:
        validate_transition(0, 888)
        raise AssertionError("skip 0→888 should be blocked")
    except PhaseTransitionError:
        pass


def test_6_pipeline_run_seal_path_0_errors():
    st = ingest_intent("formal kernel e2e", authority_present=True, reversible=True, actor_id="arif")
    st = ingest_evidence(st, _healthy_evidence())
    pr = run_pipeline(st)
    assert pr.errors == []
    assert pr.state.verdict == "SEAL"
    assert pr.state.phase == 999
    assert 888 in pr.transitions
    assert 999 in pr.transitions


def test_quantum_is_contract_not_kernel_solver():
    """Quantum lives as governance contract under contracts/, never as judge."""
    from pathlib import Path

    root = Path(__file__).resolve().parents[2] / "arifosmcp" / "runtime" / "kernel"
    assert (root / "contracts" / "quantum.py").is_file()
    assert not (root / "organs" / "quantum.py").is_file()
    from arifosmcp.runtime.kernel.contracts.quantum import QuantumComputeReceipt  # noqa: F401
