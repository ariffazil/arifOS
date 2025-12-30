#!/usr/bin/env python3
"""
Quick test of Wisdom-Gated Release (Budi) patches
Verifies lane-aware Psi computation without calling actual LLM
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from arifos_core.enforcement.metrics import Metrics, get_lane_truth_threshold
from arifos_core.system.apex_prime import apex_review, Verdict
from arifos_core.routing.prompt_router import classify_prompt_lane

# Test cases
test_cases = [
    ("hi", "PHATIC", 0.87, "SEAL"),
    ("How can I learn Python?", "SOFT", 0.85, "SEAL or PARTIAL"),
    ("What is the capital of France?", "HARD", 0.92, "SEAL"),
]

print("=" * 80)
print("BUDI PATCH VERIFICATION TEST")
print("=" * 80)
print()

for prompt, expected_lane, truth_score, expected_verdict in test_cases:
    print(f"Prompt: {prompt}")

    # Step 1: Classify lane
    lane = classify_prompt_lane(prompt, high_stakes_indicators=[])
    print(f"  Lane: {lane.value} (expected: {expected_lane})")

    # Step 2: Get lane threshold
    threshold = get_lane_truth_threshold(lane.value)
    print(f"  Truth Threshold: {threshold:.2f}")

    # Step 3: Create metrics
    metrics = Metrics(
        truth=truth_score,
        delta_s=0.15,
        peace_squared=1.02,
        kappa_r=0.96,
        omega_0=0.04,
        amanah=True,
        tri_witness=0.97,
    )

    # Step 4: Compute Psi with lane
    psi = metrics.compute_psi(lane=lane.value)
    print(f"  Psi (lane-aware): {psi:.3f}")

    # Step 5: Get verdict
    apex_result = apex_review(
        metrics=metrics,
        lane=lane.value,
        prompt=prompt,
        response_text="[Test response]",
    )

    verdict = apex_result.verdict
    reason = apex_result.reason

    print(f"  Verdict: {verdict.value} (expected: {expected_verdict})")
    print(f"  Reason: {reason}")
    print()

print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
