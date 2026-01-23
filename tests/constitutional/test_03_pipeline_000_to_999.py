"""
test_03_pipeline_000_to_999.py - Metabolic Loop Invariant Validation

AUTHORITY: arifOS Constitutional Law (000_THEORY/000_LAW.md)
ARCHITECT: Arif Fazil (Human Sovereign)
ENGINEER: Claude Sonnet 3.7 / Antigravity (Δ)
VERSION: v49.1.0

PURPOSE:
Validate the 1000-stage metabolic loop defined in ARCHITECTURE.md:
1. Stage 000 (INIT/VOID) - Clean slate initialization.
2. Stage 111-777 (SENSE/THINK/ALIGN/EMPATHY/BRIDGE/EUREKA) - Cognitive processing.
3. Stage 888 (JUDGE) - Constitutional verification.
4. Stage 999 (SEAL) - Final commit and ledger entry.
"""

from typing import Any, Dict

import pytest


def test_metabolic_loop_sequential_progression():
    """
    Ensure the system progresses sequentially through core stages and rejects skips.
    """
    from arifos.core.exceptions import StageSequenceError
    from arifos.core.metabolizer import Metabolizer

    m = Metabolizer()

    # 0. Start at 000
    m.initialize()
    assert m.current_stage == 0

    # 1. Valid progression
    m.transition_to(111)
    assert m.current_stage == 111

    # 2. Invalid skip (e.g., 111 to 999)
    with pytest.raises(StageSequenceError):
        m.transition_to(999)

def test_stage_888_gate():
    """
    Validate that Stage 888 (JUDGE) blocks progression to 999 if floors are failed.
    """
    from arifos.core.exceptions import ConstitutionalViolationError
    from arifos.core.metabolizer import Metabolizer

    m = Metabolizer()
    m.initialize()
    m.transition_to(111)
    m.transition_to(888)

    # Simulate a failed floor verdict during 888
    failed_verdict = {"F2_Truth": 0.50}

    with pytest.raises(ConstitutionalViolationError):
        m.seal(verdict=failed_verdict)

def test_stage_999_seal_ledger_entry():
    """
    Verify that Stage 999 (SEAL) creates a verifiable ledger entry.
    """
    from arifos.core.ledger import LedgerManager
    from arifos.core.metabolizer import Metabolizer

    m = Metabolizer()
    ledger = LedgerManager()

    m.initialize()
    m.transition_to(111)
    m.transition_to(888)

    # Successful seal
    seal_receipt = m.seal(verdict={"F1_Amanah": True, "F2_Truth": 1.0})
    assert seal_receipt["status"] == "SEALED"
    assert "ledger_hash" in seal_receipt

    # Verify ledger inclusion
    entry = ledger.get_entry(seal_receipt["ledger_hash"])
    assert entry["stage"] == 999
    assert entry["verdict"] == "SEAL"
