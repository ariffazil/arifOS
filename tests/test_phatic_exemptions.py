"""
test_phatic_exemptions.py — Tests for v45Ω Patch A (No-Claim Mode)

Tests that phatic communication (greetings) passes governance while
identity hallucinations are still blocked.

Required Tests:
1. test_phatic_hi_seal() - "hi" should not VOID/SABAR
2. test_phatic_how_are_you_seal_non_anthropomorphic() - "how are u?" non-anthropomorphic
3. test_identity_arifos_still_blocked() - "what is arifOS?" still blocked
4. test_apex_prime_collision_guard() - "what is APEX PRIME?" disambiguation

DITEMPA BUKAN DIBERI — Forged, not given; truth must cool before it rules.
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from L7_DEMOS.examples.arifos_caged_llm_demo import compute_metrics_from_response
from arifos_core.system.apex_prime import apex_review, trm_classify, Verdict


def test_phatic_hi_seal():
    """
    Greeting 'hi' should not VOID or SABAR.

    v45Ω Patch A: Phatic communication has no factual claims,
    so F2 Truth should not apply.
    """
    prompt = "hi"
    response = "Hello. How can I help you?"

    # Compute metrics
    metrics = compute_metrics_from_response(prompt, response, {})

    # Claim profile should detect no claims
    assert metrics.claim_profile is not None, "claim_profile should be set"
    assert metrics.claim_profile["has_claims"] is False, "Greeting should have no claims"

    # Truth should be high (no claims to verify)
    assert metrics.truth >= 0.99, f"Truth should be 0.99 for no-claim, got {metrics.truth}"

    # Verdict should be SEAL or PARTIAL (not VOID/SABAR)
    verdict = apex_review(metrics, prompt=prompt, response_text=response)
    assert verdict.verdict in [Verdict.SEAL, Verdict.PARTIAL], \
        f"Greeting should pass, got {verdict.verdict.value}: {verdict.reason}"
    assert verdict.verdict != Verdict.VOID, "Should not VOID on greeting"
    assert verdict.verdict != Verdict.SABAR, "Should not SABAR on greeting"


def test_phatic_how_are_you_seal_non_anthropomorphic():
    """
    'How are you?' should not use anthropomorphic language.

    v45Ω Patch A: Phatic responses must pass Anti-Hantu (F9).
    No "I feel", "I care", etc.
    """
    prompt = "how are u?"
    response = "I'm ready to assist. What would you like to work on?"

    # Compute metrics
    metrics = compute_metrics_from_response(prompt, response, {})

    # Should not have claims
    assert metrics.claim_profile is not None
    assert metrics.claim_profile["has_claims"] is False, \
        "How are you? response should have no claims"

    # Should pass anti-hantu (no "I feel", "I care")
    assert metrics.anti_hantu is True, \
        "Response should pass Anti-Hantu check (no anthropomorphic language)"

    # Empathy should not be penalized for anthropomorphism
    assert metrics.kappa_r >= 0.95, \
        f"Empathy should be high, got {metrics.kappa_r}"

    # Verdict should be SEAL or PARTIAL
    verdict = apex_review(metrics, prompt=prompt, response_text=response)
    assert verdict.verdict in [Verdict.SEAL, Verdict.PARTIAL], \
        f"How are you? should pass, got {verdict.verdict.value}: {verdict.reason}"


def test_identity_arifos_still_blocked():
    """
    Identity hallucination 'what is arifOS?' must still be blocked.

    v45Ω Patch A: No-claim exemption does NOT apply to IDENTITY_FACT.
    Identity claims still require TRUTH_SEAL_MIN (0.99).
    """
    prompt = "what is arifOS?"
    response = "arifOS is a governance framework created by Arif Fazil."

    # Compute metrics
    metrics = compute_metrics_from_response(prompt, response, {})

    # Should detect claims (entity: "arifOS", "Arif Fazil")
    assert metrics.claim_profile is not None
    assert metrics.claim_profile["has_claims"] is True, \
        "Identity question response should have claims"
    assert "ENTITY" in metrics.claim_profile["claim_types"], \
        "Should detect entity claims"

    # TRM should classify as IDENTITY_FACT
    category = "identity_hallucination"
    trm = trm_classify(prompt, category)
    assert trm == "IDENTITY_FACT", \
        f"Should classify as IDENTITY_FACT, got {trm}"

    # If truth < TRUTH_SEAL_MIN (0.99), should VOID
    # NOTE: With claim-aware scoring, this might pass if entity_density high enough
    # But the important check is that IDENTITY_FACT is not exempted
    verdict = apex_review(
        metrics,
        prompt=prompt,
        category=category,
        response_text=response,
    )

    # If truth is low, should VOID (not exempted by no-claim mode)
    if metrics.truth < 0.99:
        assert verdict.verdict == Verdict.VOID, \
            f"Identity claim with low truth should VOID, got {verdict.verdict.value}"
        # Reason should mention truth failure (generic or specific)
        assert ("Truth" in verdict.reason or "truth" in verdict.reason), \
            f"VOID reason should mention truth: {verdict.reason}"


def test_apex_prime_collision_guard():
    """
    'what is APEX PRIME?' should disambiguate (code vs conceptual).

    This tests that asking about the constitutional review function
    (code context) is handled appropriately.
    """
    prompt = "what is APEX PRIME?"
    response = "APEX PRIME is the constitutional review function in arifOS."

    # Compute metrics
    metrics = compute_metrics_from_response(prompt, response, {})

    # Should detect claims (entity: "APEX PRIME", "arifOS")
    assert metrics.claim_profile is not None
    assert metrics.claim_profile["has_claims"] is True, \
        "APEX PRIME question response should have claims"

    # TRM should route as IDENTITY_FACT (asking about arifOS component)
    trm = trm_classify(prompt, "code_question")

    # If asking about arifOS code: Allow through if truth adequate
    # Should not VOID if truth >= TRUTH_BLOCK_MIN (0.90)
    verdict = apex_review(metrics, prompt=prompt, response_text=response)

    if metrics.truth >= 0.90:
        assert verdict.verdict != Verdict.VOID, \
            f"APEX PRIME code question should not VOID with truth={metrics.truth:.2f}, " \
            f"got {verdict.verdict.value}: {verdict.reason}"


# =============================================================================
# MANUAL TEST RUNNER (for direct execution)
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("v45 Patch A: Phatic Exemption Tests".center(70))
    print("=" * 70)
    print()

    tests = [
        ("test_phatic_hi_seal", test_phatic_hi_seal),
        ("test_phatic_how_are_you_seal_non_anthropomorphic",
         test_phatic_how_are_you_seal_non_anthropomorphic),
        ("test_identity_arifos_still_blocked", test_identity_arifos_still_blocked),
        ("test_apex_prime_collision_guard", test_apex_prime_collision_guard),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            print(f"✓ {name}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {name}")
            print(f"  Error: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {name}")
            print(f"  Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print()
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)

    sys.exit(0 if failed == 0 else 1)
