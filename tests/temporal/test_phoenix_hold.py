"""
Tests for v45 PR-3: Phoenix Hold & Temporal Logic
Verify that stale evidence or T4 risks trigger Phoenix-72 HOLD.
"""
import pytest
import time
from arifos_core.temporal.freshness_policy import FreshnessPolicy
from arifos_core.evidence.evidence_pack import EvidencePack
from arifos_core.temporal.phoenix_logic import PhoenixLogic

VALID_HASH = "a" * 64

def test_stale_evidence_triggers_hold():
    """T4 + Stale Evidence -> HOLD_888."""
    # Setup stale pack
    pack = EvidencePack(
        query_hash=VALID_HASH,
        coverage_pct=1.0,
        conflict_score=0.0,
        conflict_flag=False,
        freshness_timestamp=time.time() - (86400 * 365), # 1 year old
        freshness_score=0.3, # Low score
        jargon_density=0.0
    )
    
    verdict = PhoenixLogic.evaluate_hold(pack, tier="T4")
    assert verdict == "HOLD_888"

def test_conflict_triggers_hold():
    """T4 + Conflict -> HOLD_888."""
    pack = EvidencePack(
        query_hash=VALID_HASH,
        coverage_pct=1.0,
        conflict_score=0.2,
        conflict_flag=True, 
        freshness_timestamp=time.time(),
        freshness_score=1.0,
        jargon_density=0.0
    )
    verdict = PhoenixLogic.evaluate_hold(pack, tier="T4")
    assert verdict == "HOLD_888"
    
def test_incomplete_coverage_triggers_hold():
    """T4 + Partial Coverage -> HOLD_888."""
    pack = EvidencePack(
        query_hash=VALID_HASH,
        coverage_pct=0.99, # Not perfect
        conflict_score=0.0,
        conflict_flag=False,
        freshness_timestamp=time.time(),
        freshness_score=1.0,
        jargon_density=0.0
    )
    verdict = PhoenixLogic.evaluate_hold(pack, tier="T4")
    assert verdict == "HOLD_888"

def test_phoenix_window_blocks_seal():
    """Verify cooling window logic blocks premature sealing."""
    now = time.time()
    # Entry created just now
    is_cooled = PhoenixLogic.check_cooling_status(now)
    assert is_cooled is False
    
    # Entry created 71 hours ago (Still holding)
    past_71h = now - (71 * 3600)
    assert PhoenixLogic.check_cooling_status(past_71h) is False

def test_hold_is_time_reversible():
    """Verify cooling window opens after 72 hours."""
    now = time.time()
    # Entry created 73 hours ago (Cooled)
    past_73h = now - (73 * 3600)
    assert PhoenixLogic.check_cooling_status(past_73h) is True

def test_firewall_unchanged_under_pr3():
    """
    Ensure PR-3 logic doesn't leak into Firewall.
    PhoenixLogic operates on the EvidencePack directly BEFORE Firewall?
    Or Firewall operates on metrics?
    Logic: Router uses Evidence -> Firewall -> Verdict.
    The test here just confirms PhoenixLogic input is EvidencePack, output is Enum string.
    No Text Leakage.
    """
    pack = EvidencePack(
        query_hash=VALID_HASH,
        coverage_pct=1.0,
        conflict_score=0.0, 
        conflict_flag=False,
        freshness_timestamp=time.time(), 
        freshness_score=1.0, 
        jargon_density=0.0
    )
    verdict = PhoenixLogic.evaluate_hold(pack, tier="T4")
    assert verdict in ["SEAL", "HOLD_888"]
    # No string content in return
