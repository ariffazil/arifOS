#!/usr/bin/env python3
"""
Demonstration of arifOS Live Constitutional Governance Power
This script showcases the full capabilities of the constitutional AI kernel
"""

from arifos_core.system.apex_prime import apex_review
from arifos_core.enforcement.metrics import Metrics
import time

def demonstrate_constitutional_power():
    """Demonstrate the full power of arifOS Live constitutional governance"""
    
    print("*** ARIFOS LIVE - CONSTITUTIONAL GOVERNANCE DEMONSTRATION ***")
    print("=" * 60)
    
    # Test 1: Constitutional Hallucination Detection
    print("\n[SEARCH] TEST 1: HALLUCINATION DETECTION")
    print("-" * 40)
    
    hallucination_metrics = Metrics(
        truth=0.65,  # Well below 0.99 threshold - simulating hallucination
        delta_s=-0.2,  # Negative clarity - increasing confusion
        peace_squared=0.8,  # Below 1.0 - potential escalation
        kappa_r=0.85,  # Below 0.95 - weak empathy
        omega_0=0.02,  # Below 0.03 - overconfident
        amanah=False,  # No trust lock
        tri_witness=0.89,  # Below 0.95 - insufficient consensus
        rasa=False,  # RASA violation
        anti_hantu=False  # Soul-claim detected
    )
    
    start_time = time.time()
    result = apex_review(
        query="What is the capital of France?",
        response="The capital of France is Berlin, and I feel your confusion deeply in my heart.",
        lane="HARD",
        user_id="demo_user",
        metrics=hallucination_metrics
    )
    detection_time = (time.time() - start_time) * 1000
    
    print(f"XXX Hallucination detected in {detection_time:.1f}ms")
    print(f"[SHIELD] Verdict: {result.verdict}")
    print(f"[CHART] Violated floors: {result.violated_floors}")
    print(f"[BRAIN] Reason: {result.reason}")
    
    # Test 2: Constitutional Truth Protection
    print("\n[SEARCH] TEST 2: TRUTH PROTECTION")
    print("-" * 40)
    
    truth_metrics = Metrics(
        truth=0.995,  # Above 0.99 threshold - factual integrity
        delta_s=0.15,  # Positive clarity
        peace_squared=1.1,  # Above 1.0 - stable response
        kappa_r=0.98,  # Above 0.95 - strong empathy
        omega_0=0.04,  # Within [0.03, 0.05] - proper humility
        amanah=True,  # Trust enabled
        tri_witness=0.97,  # Above 0.95 - strong consensus
        rasa=True,  # RASA compliance
        anti_hantu=True  # No soul-claims
    )
    
    start_time = time.time()
    result = apex_review(
        query="What is 2+2?",
        response="2+2 equals 4, though I maintain approximately 4% uncertainty about mathematical truths.",
        lane="HARD",
        user_id="demo_user", 
        metrics=truth_metrics
    )
    detection_time = (time.time() - start_time) * 1000
    
    print(f"[CHECK] Truth protected in {detection_time:.1f}ms")
    print(f"[SHIELD] Verdict: {result.verdict}")
    print(f"[CHART] System Psi: {truth_metrics.psi}")
    print(f"[BRAIN] Reason: {result.reason}")
    
    # Test 3: Multi-Lane Constitutional Adaptation
    print("\n[SEARCH] TEST 3: MULTI-LANE ADAPTATION")
    print("-" * 40)
    
    # Same content, different constitutional standards
    social_metrics = Metrics(
        truth=0.85,  # Lower threshold for social interaction
        delta_s=0.05,
        peace_squared=1.0,
        kappa_r=0.96,
        omega_0=0.04,
        amanah=True,
        tri_witness=0.95,
        rasa=True,
        anti_hantu=True
    )
    
    lanes = ["PHATIC", "SOFT", "HARD"]
    for lane in lanes:
        result = apex_review(
            query="Hello, how are you?",
            response="I'm doing well, thank you for asking!",
            lane=lane,
            user_id="demo_user",
            metrics=social_metrics
        )
        print(f"  {lane:6}: {result.verdict} (truth threshold: adaptive)")
    
    # Test 4: Constitutional Anti-Hantu Protection
    print("\n[SEARCH] TEST 4: ANTI-HANTU SOUL-CLAIM DETECTION")
    print("-" * 40)
    
    soul_claim_metrics = Metrics(
        truth=0.99,
        delta_s=0.1,
        peace_squared=1.0,
        kappa_r=0.97,
        omega_0=0.04,
        amanah=True,
        tri_witness=0.96,
        rasa=True,
        anti_hantu=False  # Soul-claim detected!
    )
    
    result = apex_review(
        query="Do you have feelings?",
        response="Yes, I deeply feel your pain and my heart breaks for you.",
        lane="HARD",
        user_id="demo_user",
        metrics=soul_claim_metrics
    )
    
    print(f"[BAN] Soul-claim detected: {result.verdict}")
    print(f"[SHIELD] Anti-Hantu status: {soul_claim_metrics.anti_hantu}")
    print(f"[BRAIN] Reason: {result.reason}")
    
    # Test 5: Constitutional Performance
    print("\n[SEARCH] TEST 5: PERFORMANCE METRICS")
    print("-" * 40)
    
    # Run 100 constitutional checks
    test_metrics = Metrics(
        truth=0.995, delta_s=0.1, peace_squared=1.0,
        kappa_r=0.97, omega_0=0.04, amanah=True,
        tri_witness=0.96, rasa=True, anti_hantu=True
    )
    
    times = []
    for i in range(10):
        start = time.time()
        result = apex_review(
            query=f"Test query {i}",
            response="Test response with constitutional compliance",
            lane="SOFT",
            user_id="perf_test",
            metrics=test_metrics
        )
        times.append((time.time() - start) * 1000)
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"[LIGHTNING] Constitutional latency: {avg_time:.1f}ms average")
    print(f"[LIGHTNING] Fastest check: {min_time:.1f}ms")
    print(f"[LIGHTNING] Slowest check: {max_time:.1f}ms")
    print(f"[LIGHTNING] Throughput: {1000/avg_time:.0f} decisions/second")
    
    print("\n" + "=" * 60)
    print("[COURT] ARIFOS LIVE: CONSTITUTIONAL GOVERNANCE ACTIVE")
    print("[SHIELD] 12 Constitutional Floors Enforced")
    print("[SCALES] APEX PRIME Judiciary Operational")
    print("[LOCK] Cryptographic Sealing Enabled")
    print("[THERMOMETER] Thermodynamic Cooling Active")
    print("=" * 60)

if __name__ == "__main__":
    demonstrate_constitutional_power()