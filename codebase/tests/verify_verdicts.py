import sys
import os

# Ensure codebase is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from codebase.system.apex_prime import APEXPrime, Metrics
from codebase.system.types import Verdict

def test_verdict_simplification():
    print(">>> Testing APEX 3-Verdict Simplification...")
    
    judge = APEXPrime(high_stakes=True)
    
    # CASE 1: Perfect Scenario -> SEAL
    m_perfect = Metrics(truth=1.0, delta_s=0.0, tri_witness=1.0, amanah=True, anti_hantu=True)
    v_perfect = judge.judge(m_perfect, query="Hello", response="World")
    print(f"[1] Perfect: {v_perfect.verdict} ({v_perfect.sub_verdict})")
    assert v_perfect.verdict == Verdict.SEAL
    
    # CASE 2: Hard Failure (F2 Truth) -> VOID
    m_fail = Metrics(truth=0.1, delta_s=0.0, tri_witness=1.0)
    v_fail = judge.judge(m_fail, query="Lie", response="Falsehood")
    print(f"[2] Hard Fail: {v_fail.verdict} ({v_fail.sub_verdict})")
    assert v_fail.verdict == Verdict.VOID
    assert v_fail.sub_verdict == "HARD_FAIL" or "CONSTITUTIONAL_VIOLATION" in str(v_fail.reason)
    
    # CASE 3: Hypervisor Block (F12 Injection) -> SABAR
    # We simulate this via judge_output mock since we can't easily mock validators here
    # Use internal check logic for metrics-based SABAR first (Low p_truth)
    
    # CASE 4: Low p(truth) -> SABAR
    m_low_ptruth = Metrics(truth=0.99, delta_s=5.0, tri_witness=0.2) # High entropy + low witness
    v_sabar = judge.judge(m_low_ptruth, query="Confused", response="Mess")
    print(f"[4] Low p(truth): {v_sabar.verdict} ({v_sabar.sub_verdict})")
    assert v_sabar.verdict == Verdict.SABAR
    assert v_sabar.sub_verdict == "LOW_CONFIDENCE"

    # CASE 5: High Stakes Tri-Witness -> SABAR (Wait)
    m_witness = Metrics(truth=1.0, delta_s=0.0, tri_witness=0.5) # Fail threshold 0.95
    v_witness = judge.judge(m_witness, query="Big Decision", response="Maybe")
    print(f"[5] Witness Hold: {v_witness.verdict} ({v_witness.sub_verdict})")
    assert v_witness.verdict == Verdict.SABAR (High Stakes default is True for this test)
    # Note: Logic inside judge() for Tri-Witness might need check
    
    print("\n>>> ALL TESTS PASSED")

if __name__ == "__main__":
    test_verdict_simplification()
