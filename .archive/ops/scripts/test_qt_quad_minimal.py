"""
Minimal QT Quad Physics Test (No Imports from organs)
"""

import sys

sys.path.insert(0, ".")


def test_calculate_w_ai_quad():
    """Test W₂ calculation."""
    print("TEST: calculate_w_ai_quad")

    from core.shared.physics import calculate_w_ai_quad

    # Empty chain = base score
    assert calculate_w_ai_quad([]) == 0.50

    # Full chain
    chain = [
        {
            "thought": "T1",
            "stage": "Problem Definition",
            "axioms_used": ["F2"],
            "assumptions_challenged": [],
            "isRevision": False,
            "tags": [],
        },
        {
            "thought": "T2",
            "stage": "Research",
            "axioms_used": ["F2", "F7"],
            "assumptions_challenged": ["a1"],
            "isRevision": False,
            "tags": [],
        },
        {
            "thought": "T3",
            "stage": "Analysis",
            "axioms_used": ["F1"],
            "assumptions_challenged": [],
            "isRevision": False,
            "tags": [],
        },
        {
            "thought": "T4",
            "stage": "Analysis",
            "axioms_used": ["F9"],
            "assumptions_challenged": ["a2", "a3"],
            "isRevision": True,
            "branchId": "b1",
            "tags": [],
        },
        {
            "thought": "T5",
            "stage": "Synthesis",
            "axioms_used": ["F5"],
            "assumptions_challenged": [],
            "isRevision": False,
            "tags": [],
        },
        {
            "thought": "T6",
            "stage": "Conclusion",
            "axioms_used": ["F3", "F13"],
            "assumptions_challenged": ["a4"],
            "isRevision": False,
            "tags": [],
        },
    ]

    w_ai = calculate_w_ai_quad(chain)
    print(f"  W₂ = {w_ai:.4f}")
    assert w_ai > 0.50
    assert w_ai <= 0.99
    print("  ✅ PASSED")


def test_calculate_w_adversarial():
    """Test W₄ calculation."""
    print("\nTEST: calculate_w_adversarial")

    from core.shared.physics import calculate_w_adversarial

    # Empty chain = base score
    assert calculate_w_adversarial([]) == 0.30

    # Chain with revisions
    chain = [
        {"thought": "T1", "isRevision": False, "assumptions_challenged": []},
        {
            "thought": "T2",
            "isRevision": True,
            "assumptions_challenged": ["a1", "a2"],
            "branchId": "b1",
        },
        {"thought": "T3", "isRevision": True, "assumptions_challenged": ["a3"], "branchId": "b2"},
    ]

    w_adv = calculate_w_adversarial(chain)
    print(f"  W₄ = {w_adv:.4f}")
    assert w_adv > 0.30
    assert w_adv <= 0.99
    print("  ✅ PASSED")


def test_extract_stakeholders():
    """Test stakeholder extraction."""
    print("\nTEST: extract_stakeholders_from_tags")

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
    print(f"  Found: {[s.name for s in stakeholders]}")

    assert len(stakeholders) == 2
    assert stakeholders[0].vulnerability_score > 0
    print("  ✅ PASSED")


def test_build_qt_quad_proof():
    """Test complete QT Quad proof."""
    print("\nTEST: build_qt_quad_proof")

    from core.shared.physics import build_qt_quad_proof

    chain = [
        {
            "thought": "T1",
            "stage": "Problem Definition",
            "axioms_used": ["F2"],
            "assumptions_challenged": [],
            "isRevision": False,
            "tags": [],
        },
        {
            "thought": "T2",
            "stage": "Analysis",
            "axioms_used": ["F1"],
            "assumptions_challenged": ["a1"],
            "isRevision": True,
            "branchId": "b1",
            "tags": [],
        },
        {
            "thought": "T3",
            "stage": "Synthesis",
            "axioms_used": ["F5"],
            "assumptions_challenged": [],
            "isRevision": False,
            "tags": ["stakeholder:user|impact:high|psi:0.9|entangled:true"],
        },
        {
            "thought": "T4",
            "stage": "Conclusion",
            "axioms_used": ["F3"],
            "assumptions_challenged": [],
            "isRevision": False,
            "tags": [],
        },
    ]

    proof = build_qt_quad_proof(chain, w_human=0.95, w_earth=0.90)

    print(f"  W_four: {proof['W_four']:.4f}")
    print(f"  Witnesses: {proof['witnesses']}")
    print(f"  Stakeholders: {len(proof['stakeholders'])}")

    assert "W_four" in proof
    assert "witnesses" in proof
    assert proof["W_four"] > 0
    assert len(proof["stakeholders"]) >= 1
    print("  ✅ PASSED")


if __name__ == "__main__":
    print("=" * 50)
    print("QT Quad Minimal Physics Tests")
    print("=" * 50)
    print()

    try:
        test_calculate_w_ai_quad()
        test_calculate_w_adversarial()
        test_extract_stakeholders()
        test_build_qt_quad_proof()

        print()
        print("=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 50)

    except AssertionError as e:
        print(f"\n❌ FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
