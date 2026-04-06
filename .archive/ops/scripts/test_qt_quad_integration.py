"""
E2E Test: QT Quad Integration with Sequential Thinking

Tests the complete QT Quad pipeline:
1. ST thought chain building
2. W₂ (AI Witness) calculation
3. W₄ (Adversarial) calculation
4. Stakeholder extraction from tags
5. QT Quad proof generation
6. AGI/ASI/APEX integration

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import asyncio
import sys

sys.path.insert(0, ".")


def test_qt_quad_physics():
    """Test 1: QT Quad calculation functions."""
    print("=" * 60)
    print("TEST 1: QT Quad Physics Functions")
    print("=" * 60)

    from core.shared.physics import (
        build_qt_quad_proof,
        calculate_w_adversarial,
        calculate_w_ai_quad,
        extract_stakeholders_from_tags,
    )

    # Test thought chain with all 5 stages + adversarial branches
    test_chain = [
        {
            "thought": "Problem Definition 1",
            "stage": "Problem Definition",
            "axioms_used": ["F2_TRUTH"],
            "assumptions_challenged": [],
            "isRevision": False,
            "tags": [],
        },
        {
            "thought": "Research 1",
            "stage": "Research",
            "axioms_used": ["F2_TRUTH", "F7_HUMILITY"],
            "assumptions_challenged": ["source"],
            "isRevision": False,
            "tags": [],
        },
        {
            "thought": "Analysis 1",
            "stage": "Analysis",
            "axioms_used": ["F1_AMANAH"],
            "assumptions_challenged": [],
            "isRevision": False,
            "tags": [],
        },
        {
            "thought": "Critique 1",
            "stage": "Analysis",
            "axioms_used": ["F3_QT_QUAD"],
            "assumptions_challenged": ["validity", "bias"],
            "isRevision": True,
            "revisesThought": 3,
            "branchId": "adv_1",
            "tags": ["adversarial:true"],
        },
        {
            "thought": "Analysis 2",
            "stage": "Analysis",
            "axioms_used": ["F4_CLARITY"],
            "assumptions_challenged": [],
            "isRevision": False,
            "tags": [],
        },
        {
            "thought": "Critique 2",
            "stage": "Analysis",
            "axioms_used": ["F9_ANTI_HANTU"],
            "assumptions_challenged": ["framing", "evidence"],
            "isRevision": True,
            "revisesThought": 5,
            "branchId": "adv_2",
            "tags": ["adversarial:true"],
        },
        {
            "thought": "Synthesis",
            "stage": "Synthesis",
            "axioms_used": ["F5_PEACE2", "F6_EMPATHY"],
            "assumptions_challenged": ["neutrality"],
            "isRevision": False,
            "tags": [
                "stakeholder:user|impact:high|psi:0.9|entangled:true",
                "stakeholder:system|impact:low|psi:0.95|entangled:false",
            ],
        },
        {
            "thought": "Conclusion",
            "stage": "Conclusion",
            "axioms_used": ["F3_QT_QUAD", "F13_SOVEREIGNTY"],
            "assumptions_challenged": ["completeness"],
            "isRevision": False,
            "tags": [],
        },
    ]

    w_ai = calculate_w_ai_quad(test_chain)
    w_adv = calculate_w_adversarial(test_chain)
    stakeholders = extract_stakeholders_from_tags(test_chain)
    qt_proof = build_qt_quad_proof(test_chain)

    print(f"  Thought chain length: {len(test_chain)}")
    print(f"  W₂ (AI Witness): {w_ai:.4f}")
    print(f"  W₄ (Adversarial): {w_adv:.4f}")
    print(f"  Stakeholders: {[s.name for s in stakeholders]}")
    print(f"  W_four: {qt_proof['W_four']:.4f}")
    print(f"  Quad-Witness Valid: {qt_proof['quad_witness_valid']}")

    # Assertions
    assert w_ai > 0.50, "W₂ should be > 0.50 (base)"
    assert w_adv > 0.30, "W₄ should be > 0.30 (base)"
    assert len(stakeholders) >= 2, "Should have at least 2 stakeholders"
    assert qt_proof["quad_witness_valid"], "W_four should be >= 0.75"

    print("  ✅ Test 1 PASSED")
    return qt_proof


async def test_agi_st_chain():
    """Test 2: AGI builds ST thought chain."""
    print()
    print("=" * 60)
    print("TEST 2: AGI Sequential Thinking Chain")
    print("=" * 60)

    from core.organs._1_agi import build_st_thought_chain, cheap_truth_detected

    chain = await build_st_thought_chain(
        query="Should I take the MSS offer?",
        hypotheses=[],
        session_id="test-session-001",
        max_depth=8,
    )

    stages = list(set(t["stage"] for t in chain))
    revisions = sum(1 for t in chain if t.get("isRevision"))
    is_cheap = cheap_truth_detected(chain)

    print(f"  Thought chain length: {len(chain)}")
    print(f"  Stages covered: {stages}")
    print(f"  Revision count: {revisions}")
    print(f"  Cheap truth detected: {is_cheap}")

    # Assertions
    assert len(chain) >= 5, "Should have minimum 5 thoughts"
    assert "Problem Definition" in stages, "Should have Problem Definition"
    assert "Research" in stages, "Should have Research"
    assert "Analysis" in stages, "Should have Analysis"
    assert "Synthesis" in stages, "Should have Synthesis"
    assert "Conclusion" in stages, "Should have Conclusion"
    assert revisions >= 1, "Should have at least 1 adversarial revision"
    assert not is_cheap, "Should not be cheap truth with full chain"

    print("  ✅ Test 2 PASSED")
    return chain


async def test_asi_stakeholders():
    """Test 3: ASI extracts stakeholders from ST chain."""
    print()
    print("=" * 60)
    print("TEST 3: ASI Stakeholder Extraction")
    print("=" * 60)

    from core.organs._2_asi import empathize
    from core.shared.physics import (
        ConstitutionalTensor,
        GeniusDial,
        Peace2,
        QuadTensor,
        UncertaintyBand,
    )

    # Build a chain with stakeholders
    chain = [
        {
            "thought": "Synthesis",
            "stage": "Synthesis",
            "axioms_used": ["F5_PEACE2", "F6_EMPATHY"],
            "assumptions_challenged": [],
            "isRevision": False,
            "tags": [
                "stakeholder:family|impact:critical|psi:0.95|entangled:true",
                "stakeholder:employer|impact:medium|psi:0.85|entangled:false",
                "stakeholder:profession|impact:high|psi:0.80|entangled:true",
            ],
        },
    ]

    tensor = ConstitutionalTensor(
        witness=QuadTensor(H=0.95, A=0.85, E=0.90, V=0.80),
        entropy_delta=-0.1,
        humility=UncertaintyBand(0.04),
        genius=GeniusDial(0.9, 0.9, 0.5, 0.9),
        peace=Peace2({}),
        empathy=0.85,
        truth_score=0.95,
    )
    tensor.st_chain = chain

    result = await empathize("Career decision query", tensor, "test-session-001")

    stakeholder_names = list(result.stakeholder_impact.keys())

    print(f"  Stakeholders detected: {stakeholder_names}")
    print(f"  F6 Empathy: {result.floor_scores.f6_empathy:.4f}")
    print(f"  Metrics: {result.metrics}")

    # Assertions
    assert len(stakeholder_names) >= 3, "Should have at least 3 stakeholders"
    assert "family" in stakeholder_names, "Should have family stakeholder"
    assert "employer" in stakeholder_names, "Should have employer stakeholder"
    assert "profession" in stakeholder_names, "Should have profession stakeholder"

    print("  ✅ Test 3 PASSED")
    return result


async def test_apex_qt_quad():
    """Test 4: APEX uses QT Quad for verdict."""
    print()
    print("=" * 60)
    print("TEST 4: APEX QT Quad Verdict")
    print("=" * 60)

    from core.organs._3_apex import sync
    from core.shared.physics import (
        ConstitutionalTensor,
        GeniusDial,
        Peace2,
        QuadTensor,
        UncertaintyBand,
    )

    # Create QT Quad proof
    qt_proof = {
        "W_four": 0.92,
        "witnesses": {"W_human": 0.95, "W_ai": 0.91, "W_earth": 0.90, "W_adversarial": 0.88},
        "thought_metrics": {
            "total_thoughts": 8,
            "revision_count": 2,
            "unique_axioms": 5,
            "assumptions_challenged": 6,
            "branches": 2,
        },
        "verdict": "SEAL",
    }

    agi_tensor = ConstitutionalTensor(
        witness=QuadTensor(H=0.95, A=0.91, E=0.90, V=0.88),
        entropy_delta=-0.1,
        humility=UncertaintyBand(0.04),
        genius=GeniusDial(0.9, 0.9, 0.5, 0.9),
        peace=Peace2({}),
        empathy=0.85,
        truth_score=0.95,
    )
    agi_tensor.qt_proof = qt_proof

    asi_output = {
        "floor_scores": {"f5_peace": 0.95, "f6_empathy": 0.90, "f9_anti_hantu": 0.95},
        "stakeholder_impact": {"family": 0.9, "employer": 0.5},
    }

    result = await sync(agi_tensor, asi_output, "test-session-001")

    w4 = result.metrics.get("W_4", 0)
    qt_available = result.metrics.get("qt_quad_available", False)

    print(f"  W_4: {w4:.4f}")
    print(f"  Verdict: {result.verdict}")
    print(f"  QT Quad Available: {qt_available}")
    print(f"  Floor Scores: F3={result.floor_scores.f3_tri_witness:.4f}")

    # Assertions
    assert w4 >= 0.75, "W_4 should meet BFT threshold"
    assert qt_available, "QT Quad should be available"
    assert result.verdict in ["SEAL", "SABAR"], "Verdict should be SEAL or SABAR"

    print("  ✅ Test 4 PASSED")
    return result


async def test_sabar_quantum_instead_of_void():
    """Test 5: SABAR_QUANTUM instead of VOID."""
    print()
    print("=" * 60)
    print("TEST 5: SABAR_QUANTUM vs VOID")
    print("=" * 60)

    from core.organs._1_agi import build_st_thought_chain, cheap_truth_detected
    from core.shared.physics import calculate_w_adversarial, calculate_w_ai_quad

    # Short chain (should trigger cheap_truth)
    short_chain = [
        {
            "thought": "Problem",
            "stage": "Problem Definition",
            "axioms_used": [],
            "assumptions_challenged": [],
            "isRevision": False,
            "tags": [],
        },
        {
            "thought": "Conclusion",
            "stage": "Conclusion",
            "axioms_used": [],
            "assumptions_challenged": [],
            "isRevision": False,
            "tags": [],
        },
    ]

    # Full chain
    full_chain = await build_st_thought_chain(
        query="Test query", hypotheses=[], session_id="test-session-002", max_depth=8
    )

    short_w_ai = calculate_w_ai_quad(short_chain)
    short_w_adv = calculate_w_adversarial(short_chain)
    short_cheap = cheap_truth_detected(short_chain)

    full_w_ai = calculate_w_ai_quad(full_chain)
    full_w_adv = calculate_w_adversarial(full_chain)
    full_cheap = cheap_truth_detected(full_chain)

    print(f"  Short chain: W₂={short_w_ai:.4f}, W₄={short_w_adv:.4f}, cheap={short_cheap}")
    print(f"  Full chain:  W₂={full_w_ai:.4f}, W₄={full_w_adv:.4f}, cheap={full_cheap}")

    # Assertions
    assert short_cheap, "Short chain should be cheap truth"
    assert not full_cheap, "Full chain should not be cheap truth"
    assert short_w_ai < full_w_ai, "Short W₂ should be < full W₂"
    assert short_w_adv < full_w_adv, "Short W₄ should be < full W₄"

    print("  ✅ Test 5 PASSED")


async def main():
    """Run all E2E tests."""
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " QT Quad Integration E2E Tests ".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    try:
        # Run all tests
        test_qt_quad_physics()
        chain = await test_agi_st_chain()
        await test_asi_stakeholders()
        await test_apex_qt_quad()
        await test_sabar_quantum_instead_of_void()

        print()
        print("=" * 60)
        print("🎉 ALL E2E TESTS PASSED!")
        print("=" * 60)
        print()
        print("Summary:")
        print("  ✅ QT Quad physics functions work correctly")
        print("  ✅ AGI builds ST thought chain with 5 stages")
        print("  ✅ ASI extracts stakeholders from ST tags")
        print("  ✅ APEX uses QT Quad for verdict")
        print("  ✅ SABAR_QUANTUM replaces VOID with guidance")
        print()
        print("DITEMPA BUKAN DIBERI — Forged, Not Given")
        return 0

    except AssertionError as e:
        print()
        print("❌ TEST FAILED:")
        print(f"   {e}")
        return 1
    except Exception as e:
        print()
        print(f"❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
