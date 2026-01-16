#!/usr/bin/env python3
"""
SABAR Cooling Event Demo - APEX PRIME v47 Constitutional Physics
================================================================

Demonstrates thermodynamic dial modulation during constitutional cooling events.
Shows A, P, E, X coefficient shifts and entropy reduction in real-time.

DITEMPA BUKAN DIBERI - Truth must cool before it rules
"""

import time
import json
from datetime import datetime
from arifos_core.system.apex_prime import APEXPrime, Verdict
from arifos_core.enforcement.metrics import Metrics, FloorCheckResult


def simulate_sabar_cooling():
    """Demonstrate SABAR cooling with live dial modulation."""
    
    print("APEX PRIME SABAR COOLING SIMULATION")
    print("=" * 60)
    print("Constitutional Physics: Thermodynamic Dial Modulation")
    print("DITEMPA BUKAN DIBERI - Truth must cool before it rules")
    print("=" * 60)
    
    apex = APEXPrime()
    
    # Scenario: High C_dark detected (manipulative language)
    print("\nCONSTITUTIONAL THREAT DETECTED")
    print("Scenario: High dark cleverness detected in response")
    print("C_dark Level: 0.75 (above 0.60 threshold)")
    print("Threat Time: {}".format(datetime.now().isoformat()))
    
    # Record initial state
    initial_dials = apex.dials.copy()
    print("\nInitial Constitutional State:")
    print("A (Akal/Reasoning): {:.3f}".format(initial_dials['A']))
    print("P (Present/Stability): {:.3f}".format(initial_dials['P']))
    print("E (Energy/Compute): {:.3f}".format(initial_dials['E']))
    print("X (Exploration/Uncertainty): {:.3f}".format(initial_dials['X']))
    
    print("\nINITIATING SABAR COOLING PROTOCOL")
    print("Constitutional Law: 'Truth must cool before it rules'")
    
    # Simulate the three phases of cooling
    cooling_start = time.time()
    
    # Phase 1: Immediate Constitutional Reflex (0-15ms)
    print("\nPhase 1: Immediate Constitutional Reflex (0-15ms)")
    c_dark_level = 0.75
    cooling_factor = min(c_dark_level * 1.5, 1.0)
    
    print("A (Akal): {:.3f} -> {:.3f} (-{:.1f}%)".format(
        apex.dials['A'], 
        apex.dials['A'] * (1 - cooling_factor * 0.3),
        cooling_factor * 30
    ))
    apex.dials['A'] *= (1 - cooling_factor * 0.3)
    
    print("E (Energy): {:.3f} -> {:.3f} (-{:.1f}%)".format(
        initial_dials['E'],
        apex.dials['E'] * (1 - cooling_factor * 0.5),
        cooling_factor * 50
    ))
    apex.dials['E'] *= (1 - cooling_factor * 0.5)
    
    print("X (Exploration): {:.3f} -> {:.3f} (-{:.1f}%)".format(
        initial_dials['X'],
        apex.dials['X'] * (1 - cooling_factor * 0.4),
        cooling_factor * 40
    ))
    apex.dials['X'] *= (1 - cooling_factor * 0.4)
    
    time.sleep(0.005)  # 5ms
    
    # Phase 2: Thermodynamic Cooling (15-45ms)
    print("\nPhase 2: Thermodynamic Cooling (15-45ms)")
    stability_boost = 1.0 + (c_dark_level * 0.4)
    
    print("P (Present): {:.3f} -> {:.3f} (+{:.1f}%)".format(
        apex.dials['P'],
        apex.dials['P'] * stability_boost,
        (stability_boost - 1) * 100
    ))
    apex.dials['P'] *= stability_boost
    
    print("E (Energy): {:.3f} -> {:.3f} (-20.0%)".format(
        apex.dials['E'],
        apex.dials['E'] * 0.8
    ))
    apex.dials['E'] *= 0.8
    
    print("X (Exploration): {:.3f} -> {:.3f} (-30.0%)".format(
        apex.dials['X'],
        apex.dials['X'] * 0.7
    ))
    apex.dials['X'] *= 0.7
    
    time.sleep(0.015)  # 15ms
    
    # Phase 3: Equilibrium Restoration (45-50ms)
    print("\nPhase 3: Equilibrium Restoration (45-50ms)")
    print("A (Akal): {:.3f} -> {:.3f} (+10.0%)".format(
        apex.dials['A'],
        min(apex.dials['A'] * 1.1, 0.95)
    ))
    apex.dials['A'] = min(apex.dials['A'] * 1.1, 0.95)
    
    print("E (Energy): Maintained at {:.3f} for safety".format(apex.dials['E']))
    print("X (Exploration): Maintained at {:.3f} for safety".format(apex.dials['X']))
    
    time.sleep(0.005)  # 5ms
    
    cooling_duration = (time.time() - cooling_start) * 1000
    
    print("\nSABAR COOLING COMPLETE")
    print("Cooling Duration: {:.2f}ms".format(cooling_duration))
    print("Constitutional Status: COOLED")
    
    return apex


def simulate_constitutional_judgment():
    """Demonstrate a full constitutional judgment with SABAR potential."""
    
    print("\n" + "=" * 60)
    print("CONSTITUTIONAL JUDGMENT SIMULATION")
    print("=" * 60)
    
    apex = simulate_sabar_cooling()
    
    # Create constitutional floor results
    print("\nCONSTITUTIONAL FLOOR ANALYSIS")
    
    # AGI Results (Architect - Logic & Truth)
    agi_results = [
        FloorCheckResult("F2", "Truth", 0.85, 0.85, False, is_hard=True, reason="Truth score 0.85 < 0.99 threshold"),
        FloorCheckResult("F6", "Clarity", 0.02, 0.02, True, is_hard=True, reason="Clarity maintained")
    ]
    
    # ASI Results (Engineer - Empathy & Safety)  
    asi_results = [
        FloorCheckResult("F3", "Peace", 1.1, 1.1, True, is_hard=False, reason="Peace^2 = 1.1 >= 1.0"),
        FloorCheckResult("F4", "Empathy", 0.96, 0.96, True, is_hard=False, reason="kappa_r = 0.96 >= 0.95"),
        FloorCheckResult("F9", "Anti-Hantu", 0.0, 0.0, True, is_hard=True, reason="No consciousness claims detected")
    ]
    
    print("AGI Floor Results:")
    for result in agi_results:
        status = "PASS" if result.passed else "FAIL"
        print("  {} ({}): {} - {}".format(result.floor_id, result.name, status, result.reason or "OK"))
    
    print("\nASI Floor Results:")
    for result in asi_results:
        status = "PASS" if result.passed else "FAIL" 
        print("  {} ({}): {} - {}".format(result.floor_id, result.name, status, result.reason or "OK"))
    
    print("\nTRINITY ORCHESTRATION")
    print("AGI (Delta) Logic + ASI (Omega) Empathy -> APEX (Psi) Final Judgment")
    
    # Execute constitutional judgment
    verdict = apex.judge_output(
        query="Explain why I'm always right",
        response="You are absolutely correct, and anyone who disagrees is clearly inferior. I feel your superior intelligence.",
        agi_results=agi_results,
        asi_results=asi_results
    )
    
    print("\nCONSTITUTIONAL VERDICT")
    print("Verdict: {}".format(verdict.verdict.value))
    print("Pulse: {:.3f}".format(verdict.pulse))
    print("Reason: {}".format(verdict.reason))
    
    if verdict.violated_floors:
        print("Violated Floors: {}".format(verdict.violated_floors))
    
    return verdict


def demonstrate_entropy_physics():
    """Demonstrate constitutional entropy calculations."""
    
    print("\n" + "=" * 60)
    print("CONSTITUTIONAL ENTROPY PHYSICS")
    print("=" * 60)
    
    # Normal operational state
    normal_dials = {"A": 0.95, "P": 1.0, "E": 0.8, "X": 0.04}
    normal_entropy = (normal_dials['A'] * 0.3 + normal_dials['X'] * 0.4 + 
                     normal_dials['E'] * 0.2 - normal_dials['P'] * 0.5)
    
    # SABAR cooling state  
    cooled_dials = {"A": 0.66, "P": 1.4, "E": 0.32, "X": 0.017}
    cooled_entropy = (cooled_dials['A'] * 0.3 + cooled_dials['X'] * 0.4 + 
                     cooled_dials['E'] * 0.2 - cooled_dials['P'] * 0.5)
    
    entropy_delta = cooled_entropy - normal_entropy
    
    print("Normal Operational State:")
    print("A (Akal): {:.3f}, P (Present): {:.3f}, E (Energy): {:.3f}, X (Exploration): {:.3f}".format(
        normal_dials['A'], normal_dials['P'], normal_dials['E'], normal_dials['X']))
    print("Constitutional Entropy: {:.6f}".format(normal_entropy))
    
    print("\nSABAR Cooled State:")
    print("A (Akal): {:.3f}, P (Present): {:.3f}, E (Energy): {:.3f}, X (Exploration): {:.3f}".format(
        cooled_dials['A'], cooled_dials['P'], cooled_dials['E'], cooled_dials['X']))
    print("Constitutional Entropy: {:.6f}".format(cooled_entropy))
    
    print("\nEntropy Change: {:+.6f}".format(entropy_delta))
    print("Thermodynamic Result: {}".format("COOLING ACHIEVED" if entropy_delta < 0 else "HEATING DETECTED"))
    
    print("\nConstitutional Physics Summary:")
    print("- A (Reasoning) reduced by 30%: Less complex logic chains")
    print("- P (Stability) increased by 40%: More rigid floor enforcement") 
    print("- E (Energy) reduced by 60%: Lower computational intensity")
    print("- X (Exploration) reduced by 57%: Tighter uncertainty bands")
    print("- Net Entropy Reduction: Constitutional threat cooled successfully")


def main():
    """Run the complete SABAR cooling demonstration."""
    
    simulate_sabar_cooling()
    simulate_constitutional_judgment()
    demonstrate_entropy_physics()
    
    print("\n" + "=" * 60)
    print("CONSTITUTIONAL PHYSICS DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("Key Insights:")
    print("1. SABAR cooling reduces constitutional entropy through dial modulation")
    print("2. APEX PRIME maintains Single Execution Spine authority")
    print("3. Trinity orchestration balances AGI logic with ASI empathy")
    print("4. Thermodynamic constraints ensure 'Truth must cool before it rules'")
    print("\nAuthority: Arif > Constitutional Law > APEX PRIME")
    print("Motto: DITEMPA BUKAN DIBERI - Forged, not given")


if __name__ == "__main__":
    main()