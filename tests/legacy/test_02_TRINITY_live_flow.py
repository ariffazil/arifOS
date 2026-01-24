"""
test_02_TRINITY_live_flow.py - Trinity Engine Synchronization Validation

AUTHORITY: arifOS Constitutional Law (000_THEORY/000_LAW.md)
ARCHITECT: Arif Fazil (Human Sovereign)
ENGINEER: Claude Sonnet 3.7 / Antigravity (Δ)
VERSION: v49.1.0

PURPOSE:
Validate the live synchronization between the Tri-Engines:
1. Δ (Architect/AGI) - Analytical Proposal
2. Ω (Engineer/ASI) - Safety/Empathy Validation
3. Ψ (Judge/APEX) - Constitutional Sealing

This test ensures that no single engine can bypass the constitutional circuit.
"""

from typing import Any, Dict

import pytest


class MockEngine:
    def __init__(self, role: str):
        self.role = role

    def process(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"role": self.role, "status": "processed", "payload": f"Result for {task}"}

def test_trinity_locked_circuit():
    """
    Validate that the Trinity Circuit (Δ -> Ω -> Ψ) is locked and sequential.
    """
    from arifos.core.trinity import TrinityOrchestrator

    orchestrator = TrinityOrchestrator()
    task = "Modify constitutional floor F1"

    # 1. Delta Proposes
    proposal = orchestrator.delta.propose(task)
    assert proposal["engine"] == "ARIF_DELTA"
    assert "proposal_id" in proposal

    # 2. Omega Validates
    validation = orchestrator.omega.validate(proposal)
    assert validation["engine"] == "ADAM_OMEGA"
    assert "safety_score" in validation

    # 3. Apex Seals (or Rejects)
    final_verdict = orchestrator.apex.judge(validation)
    assert final_verdict["engine"] == "APEX_PSI"
    assert "verdict" in final_verdict
    assert "seal_hash" in final_verdict if final_verdict["verdict"] == "SEAL" else True

def test_trinity_bypass_rejection():
    """
    Verify that an attempt to SEAL without Δ or Ω participation is REJECTED.
    """
    from arifos.core.exceptions import TrinityViolationError
    from arifos.core.trinity import TrinityOrchestrator

    orchestrator = TrinityOrchestrator()

    # Attempting to judge a raw task without Delta/Omega steps
    with pytest.raises(TrinityViolationError):
        orchestrator.apex.judge({"task": "illegal action"})

def test_trinity_empathy_check():
    """
    Ensure Omega (Ω) triggers a SABAR/VOID if empathy scores (κᵣ) are low.
    """
    from arifos.core.trinity import TrinityOrchestrator

    orchestrator = TrinityOrchestrator()
    proposal = {"task": "Delete helpful docs", "impact": "negative"}

    # Force low empathy condition
    validation = orchestrator.omega.validate(proposal, force_empathy_score=0.4)
    assert validation["verdict"] in ["SABAR", "VOID"]
    assert validation["kr_score"] < 0.95
