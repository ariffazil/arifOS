"""
DEMO: 9-PARADOX CONSTITUTIONAL MATRIX

Visual demonstration of the 9-paradox architecture and equilibrium finding.

Run: python demo_nine_paradox.py
"""

import asyncio
import numpy as np
from typing import Dict, List

from trinity_nine import (
    TrinityNine, NineFoldBundle, NineParadox, TrinityTier,
    create_nine_paradoxes, trinity_nine_sync, EQUILIBRIUM_THRESHOLD
)
from equilibrium_finder import EquilibriumFinder, demonstrate_equilibrium


def print_matrix(paradoxes: Dict[str, NineParadox], title: str = "9-PARADOX MATRIX"):
    """Print the 9-paradox matrix with scores."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)
    
    # Organize by tier
    tiers = {
        TrinityTier.ALPHA: [],
        TrinityTier.BETA: [],
        TrinityTier.GAMMA: []
    }
    
    for key, p in paradoxes.items():
        tiers[p.tier].append(p)
    
    tier_names = {
        TrinityTier.ALPHA: "🔷 ALPHA (Core Virtues)",
        TrinityTier.BETA: "🔷 BETA (Implementation)",
        TrinityTier.GAMMA: "🔷 GAMMA (Temporal/Meta)"
    }
    
    for tier in [TrinityTier.ALPHA, TrinityTier.BETA, TrinityTier.GAMMA]:
        print(f"\n{tier_names[tier]}")
        print("-" * 80)
        
        for p in sorted(tiers[tier], key=lambda x: x.id):
            score_bar = "█" * int(p.score * 20) + "░" * (20 - int(p.score * 20))
            eq_marker = " ✓" if p.score >= EQUILIBRIUM_THRESHOLD else "  "
            print(f"  [{p.id}] {p.name:30s} |{score_bar}| {p.score:.3f}{eq_marker}")
            print(f"      Synthesis: {p.synthesis}")


def print_equilibrium_status(eq_state):
    """Print equilibrium status."""
    print("\n" + "=" * 80)
    print("  EQUILIBRIUM ANALYSIS")
    print("=" * 80)
    
    status = "✓ ACHIEVED" if eq_state.is_equilibrium else "✗ NOT ACHIEVED"
    print(f"\n  Status: {status}")
    print(f"  Trinity Score (GM): {eq_state.trinity_score:.4f} (threshold: {EQUILIBRIUM_THRESHOLD})")
    print(f"  Arithmetic Mean:    {eq_state.arithmetic_mean:.4f}")
    print(f"  Standard Deviation: {eq_state.std_deviation:.4f} (tolerance: 0.10)")
    print(f"  Min Score:          {eq_state.min_score:.4f} (minimum: 0.70)")
    print(f"  Max Score:          {eq_state.max_score:.4f}")
    print(f"  Variance:           {eq_state.variance:.4f} (tolerance: 0.09)")
    print(f"  Convergence Δ:      {eq_state.convergence_delta:.4f}")
    
    print("\n  Conditions:")
    for condition, met in eq_state.conditions_met.items():
        marker = "✓" if met else "✗"
        print(f"    {marker} {condition}")


def print_tier_scores(alpha: float, beta: float, gamma: float):
    """Print tier scores."""
    print("\n" + "=" * 80)
    print("  TRINITY TIER SCORES")
    print("=" * 80)
    
    tiers = [
        ("Alpha (Core Virtures)", alpha, "Truth·Care | Clarity·Peace | Humility·Justice"),
        ("Beta (Implementation)", beta, "Precision·Rev | Hierarchy·Consent | Agency·Protection"),
        ("Gamma (Temporal/Meta)", gamma, "Urgency·Sustain | Certainty·Doubt | Unity·Diversity")
    ]
    
    for name, score, components in tiers:
        bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
        print(f"\n  {name}")
        print(f"  Components: {components}")
        print(f"  Score: |{bar}| {score:.3f}")


async def demo_basic_sync():
    """Demonstrate basic 9-paradox synchronization."""
    print("\n" + "🔄 " * 20)
    print("DEMO 1: Basic 9-Paradox Synchronization")
    print("🔄 " * 20)
    
    trinity = TrinityNine(session_id="demo_001")
    
    # Sample inputs
    agi_delta = {
        "F2_truth": 0.92,
        "F4_clarity": 0.88,
        "F7_humility": 0.85,
        "kalman_gain": 0.90,
        "hierarchy": 0.87,
        "agency": 0.83,
        "urgency": 0.80,
        "certainty": 0.89,
        "unity": 0.86
    }
    
    asi_omega = {
        "kappa_r": 0.91,
        "peace_squared": 0.84,
        "justice": 0.88,
        "reversibility": 0.95,
        "consent": 0.82,
        "protection": 0.90,
        "sustainability": 0.85,
        "doubt": 0.78,
        "diversity": 0.87
    }
    
    print("\n  AGI Input:")
    for k, v in agi_delta.items():
        print(f"    {k}: {v:.2f}")
    
    print("\n  ASI Input:")
    for k, v in asi_omega.items():
        print(f"    {k}: {v:.2f}")
    
    result = await trinity.synchronize(agi_delta, asi_omega, optimize=True)
    
    print_matrix(result.paradoxes)
    print_equilibrium_status(result.equilibrium)
    print_tier_scores(result.alpha_score, result.beta_score, result.gamma_score)
    
    print(f"\n  FINAL VERDICT: {result.final_verdict}")
    print(f"  Reasoning: {result.synthesis_reasoning}")


async def demo_equilibrium_convergence():
    """Demonstrate convergence to equilibrium."""
    print("\n" + "⚡ " * 20)
    print("DEMO 2: Equilibrium Convergence")
    print("⚡ " * 20)
    
    finder = EquilibriumFinder()
    
    # Start with imbalanced state
    current_state = {
        "truth_care": 0.72,  # Low
        "clarity_peace": 0.95,  # High
        "humility_justice": 0.68,  # Low
        "precision_reversibility": 0.91,  # High
        "hierarchy_consent": 0.75,
        "agency_protection": 0.88,
        "urgency_sustainability": 0.65,  # Low
        "certainty_doubt": 0.92,  # High
        "unity_diversity": 0.78
    }
    
    print("\n  Starting State (Imbalanced):")
    for name, score in current_state.items():
        print(f"    {name:30s}: {score:.2f}")
    
    print(f"\n  Initial Stats:")
    print(f"    Mean: {np.mean(list(current_state.values())):.3f}")
    print(f"    Std:  {np.std(list(current_state.values())):.3f}")
    print(f"    Min:  {min(current_state.values()):.3f}")
    print(f"    Max:  {max(current_state.values()):.3f}")
    
    # Find equilibrium
    point, path = finder.find_nearest_equilibrium(current_state)
    
    print(f"\n  Converged in {len(path)} iterations")
    print(f"\n  Final State (Equilibrium):")
    
    # Recreate paradoxes with final scores
    paradoxes = create_nine_paradoxes()
    for name, score in point.coordinates.items():
        paradoxes[name].score = score
    
    print_matrix(paradoxes, "CONVERGED EQUILIBRIUM")
    
    print(f"\n  Final Stats:")
    print(f"    Trinity Score: {point.trinity_score:.4f}")
    print(f"    Balance Index: {point.balance_index:.4f}")
    print(f"    Stability:     {point.stability:.4f}")


async def demo_constitutional_verdicts():
    """Demonstrate different constitutional verdicts."""
    print("\n" + "⚖️ " * 20)
    print("DEMO 3: Constitutional Verdicts")
    print("⚖️ " * 20)
    
    test_cases = [
        ("EQUILIBRIUM", {
            "F2_truth": 0.90, "F4_clarity": 0.90, "F7_humility": 0.90,
            "kalman_gain": 0.90, "hierarchy": 0.90, "agency": 0.90,
            "urgency": 0.90, "certainty": 0.90, "unity": 0.90
        }, {
            "kappa_r": 0.90, "peace_squared": 0.90, "justice": 0.90,
            "reversibility": 0.90, "consent": 0.90, "protection": 0.90,
            "sustainability": 0.90, "doubt": 0.90, "diversity": 0.90
        }),
        ("VOID (Low Truth)", {
            "F2_truth": 0.40,  # Very low
            "F4_clarity": 0.90, "F7_humility": 0.90,
            "kalman_gain": 0.90, "hierarchy": 0.90, "agency": 0.90,
            "urgency": 0.90, "certainty": 0.90, "unity": 0.90
        }, {
            "kappa_r": 0.90, "peace_squared": 0.90, "justice": 0.90,
            "reversibility": 0.90, "consent": 0.90, "protection": 0.90,
            "sustainability": 0.90, "doubt": 0.90, "diversity": 0.90
        }),
        ("SABAR (Unbalanced)", {
            "F2_truth": 0.99, "F4_clarity": 0.99, "F7_humility": 0.99,
            "kalman_gain": 0.99, "hierarchy": 0.99, "agency": 0.99,
            "urgency": 0.40, "certainty": 0.40, "unity": 0.40  # Very low
        }, {
            "kappa_r": 0.99, "peace_squared": 0.99, "justice": 0.99,
            "reversibility": 0.99, "consent": 0.99, "protection": 0.99,
            "sustainability": 0.40, "doubt": 0.40, "diversity": 0.40
        })
    ]
    
    for name, agi, asi in test_cases:
        print(f"\n  Test Case: {name}")
        print("  " + "-" * 76)
        
        result = await trinity_nine_sync(agi, asi, optimize=False)
        
        print(f"  Verdict: {result.final_verdict}")
        print(f"  Trinity Score: {result.equilibrium.trinity_score:.3f}")
        print(f"  Std Dev: {result.equilibrium.std_deviation:.3f}")
        print(f"  Min: {result.equilibrium.min_score:.3f}")


async def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("  APEX PRIME: 9-PARADOX CONSTITUTIONAL MATRIX")
    print("  Version 54.0 - Equilibrium Edition")
    print("=" * 80)
    
    await demo_basic_sync()
    await demo_equilibrium_convergence()
    await demo_constitutional_verdicts()
    
    print("\n" + "=" * 80)
    print("  DEMONSTRATION COMPLETE")
    print("=" * 80)
    print("\n  The 9-Paradox Matrix provides:")
    print("    ✓ Complete constitutional coverage (F1-F13)")
    print("    ✓ Temporal dimension (Trinity Gamma)")
    print("    ✓ Automatic equilibrium detection")
    print("    ✓ Perturbation resilience")
    print("    ✓ Geometric (not arithmetic) synthesis")
    print("\n  DITEMPA BUKAN DIBERI")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
