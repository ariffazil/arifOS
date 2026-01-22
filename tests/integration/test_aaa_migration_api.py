"""
Quick test for AAA-migrated API pipeline routes.
Tests that quantum validation works after migration.
"""

import sys
import asyncio


def test_api_imports():
    """Test that AAA imports work in API routes."""
    try:
        from arifos.core.integration.api.routes.pipeline import router
        from arifos.core.mcp import generate_and_validate_async
        print("[PASS] AAA imports successful")
        return True
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False


def test_api_structure():
    """Test that API endpoints exist with correct signatures."""
    try:
        from arifos.core.integration.api.routes.pipeline import router, run_pipeline, run_pipeline_debug

        # Check endpoints are registered
        routes = [route.path for route in router.routes]
        assert "/pipeline/run" in routes, "Missing /run endpoint"
        assert "/pipeline/run/debug" in routes, "Missing /run/debug endpoint"
        assert "/pipeline/status" in routes, "Missing /status endpoint"

        print(f"[PASS] API structure validated - {len(routes)} endpoints found")
        return True
    except Exception as e:
        print(f"[FAIL] Structure validation error: {e}")
        return False


async def test_api_helpers():
    """Test that AAA helpers can be called (without actual LLM)."""
    try:
        from arifos.core.mcp import validate_text_async

        # Test validation-only (no LLM needed)
        state = await validate_text_async(
            query="Test query",
            draft_response="Test response"
        )

        assert state.collapsed is True, "Quantum state should be collapsed"
        assert state.final_verdict is not None, "Should have verdict"

        print(f"[PASS] AAA helpers work - Verdict: {state.final_verdict}")
        return True
    except Exception as e:
        print(f"[FAIL] Helper test error: {e}")
        return False


async def test_run():
    """Run all tests."""
    print("Testing AAA-migrated API routes...\n")

    results = []

    # Synchronous tests
    results.append(("Imports", test_api_imports()))
    results.append(("Structure", test_api_structure()))

    # Async tests
    results.append(("Helpers", await test_api_helpers()))

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
        print("\n[SUCCESS] All AAA migration tests passed!")
        return True
    else:
        print(f"\n[FAIL] {total - passed} tests failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_run())
    sys.exit(0 if success else 1)
