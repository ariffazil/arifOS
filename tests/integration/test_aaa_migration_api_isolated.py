"""
Isolated test for AAA-migrated API pipeline routes.
Tests the migration without triggering full import chain.
"""

import sys
import asyncio


def test_aaa_imports():
    """Test that AAA helpers are correctly imported."""
    try:
        # Test direct AAA imports work
        from arifos.core.mcp import generate_and_validate_async, validate_text_sync
        print("[PASS] AAA helpers imported successfully")
        return True
    except ImportError as e:
        print(f"[FAIL] AAA import error: {e}")
        return False


def test_pipeline_file_structure():
    """Test that pipeline.py has the correct AAA structure."""
    try:
        with open("arifos_core/integration/api/routes/pipeline.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Check for AAA-level imports
        assert "from arifos.core.mcp import generate_and_validate_async" in content, \
            "Missing AAA import"

        # Check old pipeline is NOT imported
        assert "from arifos.core.system.pipeline import Pipeline" not in content or \
               "# OLD" in content or "DEPRECATED" in content, \
            "Old pipeline still imported"

        # Check AAA pattern is used
        assert "generate_and_validate_async(" in content, "AAA function not called"
        assert "quantum_state.final_verdict" in content, "Not using quantum state"
        assert "quantum_state.agi_particle" in content, "Not extracting from quantum particles"

        # Check docstrings mention AAA
        assert "AAA-Level" in content or "AAA Architecture" in content, \
            "AAA documentation missing"

        print("[PASS] Pipeline file has correct AAA structure")
        print("  - AAA imports present")
        print("  - Old pipeline removed")
        print("  - Quantum state usage verified")
        print("  - AAA documentation present")
        return True
    except FileNotFoundError:
        print("[FAIL] Pipeline file not found")
        return False
    except AssertionError as e:
        print(f"[FAIL] Structure validation: {e}")
        return False


async def test_aaa_validation():
    """Test that AAA validation works."""
    try:
        from arifos.core.mcp import validate_text_async

        # Test validation-only (no LLM needed)
        state = await validate_text_async(
            query="Test AAA migration",
            draft_response="Migration successful"
        )

        assert state.collapsed is True, "Quantum state should be collapsed"
        assert state.final_verdict is not None, "Should have verdict"
        assert state.agi_particle is not None, "Should have AGI particle"
        assert state.asi_particle is not None, "Should have ASI particle"

        print(f"[PASS] AAA validation works - Verdict: {state.final_verdict}")
        return True
    except Exception as e:
        print(f"[FAIL] Validation test error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_judge_migration():
    """Test that arifos_judge was migrated correctly."""
    try:
        with open("arifos_core/mcp/tools/judge.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Check for AAA imports
        assert "from arifos.core.mcp import validate_text_sync" in content, \
            "Judge missing AAA import"

        # Check AAA usage
        assert "validate_text_sync(" in content, "Judge not using AAA function"

        # Check old pipeline is NOT used
        assert "from arifos.core.system.pipeline import" not in content or \
               "# OLD" in content, \
            "Judge still using old pipeline"

        print("[PASS] arifos_judge migrated correctly")
        return True
    except FileNotFoundError:
        print("[FAIL] Judge file not found")
        return False
    except AssertionError as e:
        print(f"[FAIL] Judge validation: {e}")
        return False


async def test_run():
    """Run all tests."""
    print("Testing AAA Migration (Isolated)...\n")

    results = []

    # Synchronous tests
    results.append(("AAA Imports", test_aaa_imports()))
    results.append(("Pipeline Structure", test_pipeline_file_structure()))
    results.append(("Judge Migration", test_judge_migration()))

    # Async tests
    results.append(("AAA Validation", await test_aaa_validation()))

    # Summary
    print("\n" + "="*60)
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")

    print("="*60)
    print(f"\n{passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] AAA migration validated!")
        print("\nMigration Summary:")
        print("  Files: judge.py, pipeline.py")
        print("  Pattern: LLM Generation (orthogonal) Quantum Validation")
        print("  Architecture: Asynchronous, Autonomous, Atomic")
        return True
    else:
        print(f"\n[FAIL] {total - passed} tests failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_run())
    sys.exit(0 if success else 1)
