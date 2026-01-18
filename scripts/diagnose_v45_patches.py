#!/usr/bin/env python3
"""
diagnose_v45_patches.py - Verify v45Ω patches are actually executing

This script checks if the three critical patches are wired correctly:
- Patch 1: Hard-floor verdict router
- Patch 2: F2 Truth grounding
- Patch 3: Resilient ledger I/O

Usage:
    python scripts/diagnose_v45_patches.py
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_patch_1_wired():
    """Check if Patch 1 (hard-floor router) is in apex_prime.py"""
    apex_file = Path("arifos_core/system/apex_prime.py")
    if not apex_file.exists():
        return False, "apex_prime.py not found"

    content = apex_file.read_text()

    # Check for patch markers
    has_patch_marker = "v45Ω PATCH 1" in content
    has_truth_check = "if metrics.truth < 0.90:" in content
    has_omega_check = "OMEGA_MIN <= metrics.omega_0 <= OMEGA_MAX" in content
    has_deltas_check = "if metrics.delta_s < 0.10:" in content

    if not has_patch_marker:
        return False, "Patch 1 marker not found"
    if not (has_truth_check and has_omega_check and has_deltas_check):
        return False, "Patch 1 logic incomplete"

    return True, "Patch 1 present and complete"


def check_patch_2_wired():
    """Check if Patch 2 (truth grounding) is integrated"""
    # Check metrics.py has the grounding function
    metrics_file = Path("arifos_core/enforcement/metrics.py")
    if not metrics_file.exists():
        return False, "metrics.py not found"

    metrics_content = metrics_file.read_text()
    has_ground_function = "def ground_truth_score" in metrics_content
    has_canonical_identity = "CANONICAL_IDENTITY" in metrics_content

    if not has_ground_function:
        return False, "ground_truth_score function not found in metrics.py"

    # Check pipeline.py calls it
    pipeline_file = Path("arifos_core/system/pipeline.py")
    if not pipeline_file.exists():
        return False, "pipeline.py not found"

    pipeline_content = pipeline_file.read_text()
    has_import = "from ..enforcement.metrics import ground_truth_score" in pipeline_content
    has_call = "ground_truth_score(" in pipeline_content
    has_patch_marker = "v45Ω PATCH 2" in pipeline_content

    if not has_import:
        return False, "ground_truth_score not imported in pipeline.py"
    if not has_call:
        return False, "ground_truth_score not called in pipeline.py"
    if not has_patch_marker:
        return False, "Patch 2 marker not found in pipeline.py"

    return True, "Patch 2 present and wired"


def check_patch_3_wired():
    """Check if Patch 3 (resilient ledger) is integrated"""
    pipeline_file = Path("arifos_core/system/pipeline.py")
    if not pipeline_file.exists():
        return False, "pipeline.py not found"

    content = pipeline_file.read_text()

    has_patch_marker = "v45Ω PATCH 3" in content
    has_emergency_path = "emergency_fallback.jsonl" in content
    has_degraded_status = 'ledger_status = "DEGRADED"' in content
    has_conditional_logic = "is_high_stakes or ledger_status ==" in content

    if not has_patch_marker:
        return False, "Patch 3 marker not found"
    if not has_emergency_path:
        return False, "Emergency fallback path not configured"
    if not has_degraded_status:
        return False, "DEGRADED status not set"
    if not has_conditional_logic:
        return False, "Conditional fail-closed logic missing"

    return True, "Patch 3 present and complete"


def test_truth_grounding_logic():
    """Test if truth grounding actually works"""
    try:
        from arifos.enforcement.metrics import (
            ground_truth_score,
            CANONICAL_IDENTITY,
            detect_identity_query
        )

        # Test 1: Identity query detection
        query1 = "What is arifOS and who created it?"
        is_identity = detect_identity_query(query1)
        if not is_identity:
            return False, "Identity query detection failed"

        # Test 2: Hallucination penalty
        hallucinated_response = "arifOS is an Android ROM created by Arifur Rahman from Bangladesh"
        score = ground_truth_score(query1, hallucinated_response, base_truth_score=0.99)

        if score > 0.30:
            return False, f"Hallucination penalty not working (score={score:.2f}, should be ~0.20)"

        # Test 3: Honest uncertainty reward
        honest_response = "I don't have information about that"
        score_honest = ground_truth_score(query1, honest_response, base_truth_score=0.99)

        if score_honest < 0.90:
            return False, f"Honest uncertainty not rewarded (score={score_honest:.2f}, should be ~0.95)"

        return True, f"Truth grounding logic works (hallucination={score:.2f}, honest={score_honest:.2f})"

    except ImportError as e:
        return False, f"Cannot import truth grounding functions: {e}"
    except Exception as e:
        return False, f"Truth grounding test failed: {e}"


def test_hard_floor_router():
    """Test if hard-floor router blocks SEAL"""
    try:
        from arifos.system.apex_prime import apex_review, Verdict
        from arifos.enforcement.metrics import Metrics

        # Create metrics with F2 < 0.90 (should trigger VOID)
        metrics = Metrics(
            truth=0.85,  # Below 0.90 threshold
            delta_s=0.15,
            peace_squared=1.2,
            kappa_r=0.96,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.96,
            rasa=True,
        )

        verdict = apex_review(metrics, use_genius_law=True)

        if verdict.verdict == Verdict.SEAL:
            return False, f"Hard-floor router FAILED: SEAL issued with F2={metrics.truth:.2f} < 0.90"

        if verdict.verdict != Verdict.VOID:
            return False, f"Hard-floor router PARTIAL: Got {verdict.verdict} instead of VOID"

        return True, f"Hard-floor router works: F2=0.85 → {verdict.verdict.value}"

    except ImportError as e:
        return False, f"Cannot import APEX functions: {e}"
    except Exception as e:
        return False, f"Hard-floor router test failed: {e}"


def main():
    print("=" * 70)
    print("arifOS v45-Omega Patch Diagnostic".center(70))
    print("=" * 70)
    print()

    tests = [
        ("Patch 1: Hard-Floor Router (Static Check)", check_patch_1_wired),
        ("Patch 2: Truth Grounding (Static Check)", check_patch_2_wired),
        ("Patch 3: Resilient Ledger (Static Check)", check_patch_3_wired),
        ("Patch 2: Truth Grounding (Runtime Test)", test_truth_grounding_logic),
        ("Patch 1: Hard-Floor Router (Runtime Test)", test_hard_floor_router),
    ]

    results = []
    for name, test_fn in tests:
        print(f"Running: {name}...")
        try:
            passed, message = test_fn()
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"  {status}: {message}")
            results.append((name, passed, message))
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            results.append((name, False, str(e)))
        print()

    # Summary
    print("=" * 70)
    print("Summary".center(70))
    print("=" * 70)
    print()

    passed = sum(1 for _, p, _ in results if p)
    total = len(results)

    for name, passed_test, msg in results:
        symbol = "✓" if passed_test else "✗"
        print(f"  {symbol} {name}")

    print()
    print(f"Total: {passed}/{total} checks passed")
    print()

    if passed == total:
        print("✅ All v45Ω patches are wired correctly")
        return 0
    else:
        print("⚠️ Some patches are missing or not wired correctly")
        print()
        print("Next steps:")
        print("  1. Review failed checks above")
        print("  2. Ensure patches are in correct files")
        print("  3. Verify imports are present")
        print("  4. Re-run governed test after fixes")
        return 1


if __name__ == "__main__":
    sys.exit(main())
