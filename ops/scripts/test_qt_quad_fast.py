"""
Fast E2E Test: QT Quad Integration (No Heavy Models)
"""

import asyncio
import sys

sys.path.insert(0, ".")


def test_qt_quad_physics():
    """Test 1: QT Quad calculation functions."""
    print("TEST 1: QT Quad Physics Functions")

    from core.shared.physics import (
        build_qt_quad_proof,
        calculate_w_adversarial,
        calculate_w_ai_quad,
    )

    # Test thought chain
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
            "thought": "Synthesis",
            "stage": "Synthesis",
            "axioms_used": ["F5_PEACE2", "F6_EMPATHY"],
            "assumptions_challenged": [],
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
    qt_proof = build_qt_quad_proof(test_chain)

    print(f"  W₂ (AI Witness): {w_ai:.4f}")
    print(f"  W₄ (Adversarial): {w_adv:.4f}")
    print(f"  W_four: {qt_proof['W_four']:.4f}")
    print(f"  Valid: {qt_proof['quad_witness_valid']}")

    assert w_ai > 0.50, "W₂ should be > 0.50"
    assert w_adv > 0.30, "W₄ should be > 0.30"
    assert qt_proof["quad_witness_valid"], "W_four should be >= 0.75"

    print("  ✅ PASSED\n")


async def test_agi_st_chain():
    """Test 2: AGI builds ST thought chain."""
    print("TEST 2: AGI Sequential Thinking Chain")

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

    print(f"  Chain length: {len(chain)}")
    print(f"  Stages: {stages}")
    print(f"  Revisions: {revisions}")
    print(f"  Cheap truth: {is_cheap}")

    assert len(chain) >= 5, "Should have minimum 5 thoughts"
    assert "Problem Definition" in stages
    assert "Synthesis" in stages
    assert "Conclusion" in stages
    assert revisions >= 1, "Should have adversarial revisions"
    assert not is_cheap, "Should not be cheap truth"

    print("  ✅ PASSED\n")


def test_stakeholder_extraction():
    """Test 3: Stakeholder extraction from tags."""
    print("TEST 3: Stakeholder Extraction")

    from core.shared.physics import extract_stakeholders_from_tags

    chain = [
        {
            "thought": "Synthesis",
            "stage": "Synthesis",
            "tags": [
                "stakeholder:family|impact:critical|psi:0.95|entangled:true",
                "stakeholder:employer|impact:medium|psi:0.85|entangled:false",
            ],
        },
    ]

    stakeholders = extract_stakeholders_from_tags(chain)

    print(f"  Stakeholders: {[s.name for s in stakeholders]}")

    assert len(stakeholders) >= 2, "Should have at least 2 stakeholders"
    assert "family" in [s.name for s in stakeholders]
    assert "employer" in [s.name for s in stakeholders]

    print("  ✅ PASSED\n")


async def main():
    """Run all fast tests."""
    print("=" * 50)
    print("QT Quad Integration Fast Tests")
    print("=" * 50)
    print()

    try:
        test_qt_quad_physics()
        await test_agi_st_chain()
        test_stakeholder_extraction()

        print("=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 50)
        return 0

    except AssertionError as e:
        print(f"❌ FAILED: {e}")
        return 1
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
