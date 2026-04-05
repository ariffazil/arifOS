"""
tests/core/test_risk_engine.py — Tests for the Risk Engine action gating
"""

import pytest
from core.risk_engine import RiskEngine
from core.shared.types import ActionClass

def test_classify_action_critical():
    engine = RiskEngine()
    assert engine.classify_action("rm -rf /") == ActionClass.CRITICAL
    assert engine.classify_action("mkfs.ext4 /dev/sdb") == ActionClass.CRITICAL

def test_classify_action_execute():
    engine = RiskEngine()
    assert engine.classify_action("pip install numpy") == ActionClass.EXECUTE
    assert engine.classify_action("docker rm my_container") == ActionClass.EXECUTE

def test_classify_action_write():
    engine = RiskEngine()
    assert engine.classify_action("mkdir logs") == ActionClass.WRITE
    assert engine.classify_action("mv a.txt b.txt") == ActionClass.WRITE

def test_classify_action_read():
    engine = RiskEngine()
    assert engine.classify_action("ls -la") == ActionClass.READ
    assert engine.classify_action("cat README.md") == ActionClass.READ

def test_evaluate_gate_void():
    engine = RiskEngine()
    permitted, reason = engine.evaluate_gate(ActionClass.READ, 1.0, "VOID")
    assert permitted is False
    assert "VOIDed" in reason

def test_evaluate_gate_low_score():
    engine = RiskEngine()
    # Threshold for READ is 0.80
    permitted, reason = engine.evaluate_gate(ActionClass.READ, 0.75, "SEAL")
    assert permitted is False
    assert "Consensus 0.750 < threshold 0.8" in reason

def test_evaluate_gate_critical_no_ratification():
    engine = RiskEngine()
    # Threshold for CRITICAL is 0.98
    permitted, reason = engine.evaluate_gate(ActionClass.CRITICAL, 0.99, "SEAL", human_ratified=False)
    assert permitted is False
    assert "requires explicit human ratification" in reason

def test_evaluate_gate_critical_ratified():
    engine = RiskEngine()
    permitted, reason = engine.evaluate_gate(ActionClass.CRITICAL, 0.99, "SEAL", human_ratified=True)
    assert permitted is True
    assert "Action permitted" in reason

def test_evaluate_gate_success():
    engine = RiskEngine()
    permitted, reason = engine.evaluate_gate(ActionClass.READ, 0.95, "SEAL")
    assert permitted is True
